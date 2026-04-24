from django.utils import timezone

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from vms.models import VirtualMachine
from .models import User
from .serializers import (
    ActivateKeySuccessSerializer,
    ActivationKeySerializer,
    ErrorResponseSerializer,
    RegisterSerializer,
)
from .tasks import send_activation_key_email


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                description="Пользователь успешно зарегистрирован.",
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Ошибка валидации данных.",
            ),
        },
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.create_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        user.generate_activation_key()

        send_activation_key_email.delay(
            user.email,
            user.activation_key,
        )

        return Response(
            {
                "message": "Письмо с ключом отправлено на почту.",
            },
            status=status.HTTP_201_CREATED,
        )


class ActivateKeyView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        request=ActivationKeySerializer,
        responses={
            200: OpenApiResponse(
                response=ActivateKeySuccessSerializer,
                description="Прокси успешно назначен.",
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description=(
                    "Неверный ключ активации или срок его действия истёк."
                ),
            ),
            503: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Все прокси заняты.",
            ),
        },
    )
    def post(self, request):
        serializer = ActivationKeySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        activation_key = serializer.validated_data["activation_key"]

        try:
            user = User.objects.get(activation_key=activation_key)
        except User.DoesNotExist:
            return Response(
                {"detail": "Неверный ключ активации."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            user.activation_key_expires
            and user.activation_key_expires < timezone.now()
        ):
            return Response(
                {"detail": "Срок действия ключа активации истёк."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        vm = VirtualMachine.objects.filter(
            current_user__isnull=True,
            is_active=True,
        ).first()

        if vm is None:
            return Response(
                {"detail": "Все прокси заняты."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        vm.current_user = user
        vm.last_used_at = timezone.now()
        vm.save()

        user.activation_key = None
        user.activation_key_expires = None
        user.save()

        return Response(
            {
                "message": "Подключение выполнено успешно.",
                "proxy": {
                    "host": vm.host,
                    "port": vm.port,
                    "protocol": vm.protocol,
                },
            },
            status=status.HTTP_200_OK,
        )
