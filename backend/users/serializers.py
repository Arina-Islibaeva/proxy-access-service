from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class ActivationKeySerializer(serializers.Serializer):
    activation_key = serializers.CharField()


class ProxyDataSerializer(serializers.Serializer):
    host = serializers.CharField()
    port = serializers.IntegerField()
    protocol = serializers.CharField()


class ActivateKeySuccessSerializer(serializers.Serializer):
    message = serializers.CharField()
    proxy = ProxyDataSerializer()


class ErrorResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Пароли не совпадают."}
            )

        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError(
                {"email": "Пользователь с таким email уже существует."}
            )

        return attrs
