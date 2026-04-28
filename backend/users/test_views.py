from http import HTTPStatus

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from users.models import User
from vms.models import VirtualMachine


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    user = User.objects.create_user(
        email="user@example.com",
        password="password123",
    )
    user.generate_activation_key()
    return user


@pytest.fixture
def active_vm():
    return VirtualMachine.objects.create(
        name="proxy-1",
        host="192.168.1.10",
        port=1080,
        protocol="socks5",
        is_active=True,
    )


def test_register_creates_user_and_activation_key(api_client, mocker):
    mock_task = mocker.patch(
        "users.views.send_activation_key_email.delay",
    )

    response = api_client.post(
        "/api/register/",
        {
            "email": "new@example.com",
            "password": "password123",
            "password_confirm": "password123",
        },
        format="json",
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.data["message"] == "Письмо с ключом отправлено на почту."

    user = User.objects.get(email="new@example.com")
    assert user.activation_key is not None
    assert user.is_active is True

    mock_task.assert_called_once_with(
        user.email,
        user.activation_key,
    )


def test_login_success(api_client, user):
    response = api_client.post(
        "/api/login/",
        {
            "email": user.email,
            "password": "password123",
        },
        format="json",
    )

    assert response.status_code == HTTPStatus.OK
    assert response.data["message"] == "Вход выполнен успешно."


def test_profile_requires_authentication(api_client):
    response = api_client.get("/api/profile/")

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_profile_returns_current_user_data(api_client, user):
    api_client.force_authenticate(user=user)

    response = api_client.get("/api/profile/")

    assert response.status_code == HTTPStatus.OK
    assert response.data["email"] == user.email
    assert response.data["activation_key"] == user.activation_key


def test_refresh_key_generates_new_key(api_client, user, mocker):
    mock_task = mocker.patch(
        "users.views.send_activation_key_email.delay",
    )
    old_key = user.activation_key

    api_client.force_authenticate(user=user)

    response = api_client.post("/api/refresh-key/")

    user.refresh_from_db()

    assert response.status_code == HTTPStatus.OK
    assert response.data["message"] == "Новый ключ отправлен на почту."
    assert user.activation_key != old_key
    assert user.activation_key is not None

    mock_task.assert_called_once_with(
        user.email,
        user.activation_key,
    )


def test_activate_key_assigns_free_vm(api_client, user, active_vm, mocker):
    mocker.patch("users.views.send_connection_status")

    response = api_client.post(
        "/api/activate-key/",
        {
            "activation_key": user.activation_key,
        },
        format="json",
    )

    user.refresh_from_db()
    active_vm.refresh_from_db()

    assert response.status_code == HTTPStatus.OK
    assert response.data["message"] == "Подключение выполнено успешно."
    assert response.data["proxy"]["host"] == active_vm.host
    assert response.data["proxy"]["port"] == active_vm.port
    assert response.data["proxy"]["protocol"] == active_vm.protocol

    assert active_vm.current_user == user
    assert active_vm.last_used_at is not None

    assert user.activation_key is None
    assert user.activation_key_expires is None


def test_activate_key_returns_error_when_key_is_invalid(api_client):
    response = api_client.post(
        "/api/activate-key/",
        {
            "activation_key": "invalid-key",
        },
        format="json",
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.data["detail"] == "Неверный ключ активации."


def test_activate_key_returns_error_when_key_is_expired(api_client, user):
    user.activation_key_expires = timezone.now() - timezone.timedelta(hours=1)
    user.save()

    response = api_client.post(
        "/api/activate-key/",
        {
            "activation_key": user.activation_key,
        },
        format="json",
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.data["detail"] == "Срок действия ключа активации истёк."


def test_activate_key_returns_error_when_all_vms_are_busy(
    api_client,
    user,
    mocker,
):
    mocker.patch("users.views.send_connection_status")

    VirtualMachine.objects.create(
        name="proxy-1",
        host="192.168.1.10",
        port=1080,
        protocol="socks5",
        is_active=True,
        current_user=User.objects.create_user(
            email="busy@example.com",
            password="password123",
        ),
    )

    response = api_client.post(
        "/api/activate-key/",
        {
            "activation_key": user.activation_key,
        },
        format="json",
    )

    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert response.data["detail"] == "Все прокси заняты."


def test_change_password_success(api_client, user):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/change-password/",
        {
            "old_password": "password123",
            "new_password": "newpassword123",
            "new_password_confirm": "newpassword123",
        },
        format="json",
    )

    user.refresh_from_db()

    assert response.status_code == HTTPStatus.OK
    assert response.data["message"] == "Пароль успешно изменён."
    assert user.check_password("newpassword123") is True
