from rest_framework import serializers


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
