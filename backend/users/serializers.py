from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class ActivationKeySerializer(serializers.Serializer):
    """Сериализатор для передачи ключа активации."""

    activation_key = serializers.CharField()


class ProxyDataSerializer(serializers.Serializer):
    """Сериализатор данных назначенного прокси."""

    host = serializers.CharField()
    port = serializers.IntegerField()
    protocol = serializers.CharField()


class ActivateKeySuccessSerializer(serializers.Serializer):
    """Сериализатор успешного ответа при активации ключа."""

    message = serializers.CharField()
    proxy = ProxyDataSerializer()


class ErrorResponseSerializer(serializers.Serializer):
    """Сериализатор ответа с ошибкой."""

    detail = serializers.CharField()


class MessageResponseSerializer(serializers.Serializer):
    """Сериализатор стандартного сообщения."""

    message = serializers.CharField()


class RegisterSerializer(serializers.Serializer):
    """Сериализатор регистрации пользователя."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        Проверяет совпадение паролей
        и уникальность email.
        """
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Пароли не совпадают."}
            )

        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError(
                {
                    "email": (
                        "Пользователь с таким email уже существует."
                    )
                }
            )

        return attrs


class LoginSerializer(serializers.Serializer):
    """Сериализатор входа пользователя."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ProfileSerializer(serializers.Serializer):
    """Сериализатор данных личного кабинета."""

    email = serializers.EmailField()
    is_active = serializers.BooleanField()
    activation_key = serializers.CharField(allow_null=True)


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор смены пароля."""

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Проверяет совпадение новых паролей."""
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {
                    "new_password_confirm": (
                        "Новые пароли не совпадают."
                    )
                }
            )

        return attrs
