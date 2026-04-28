from django.urls import path

from .consumers import ConnectionStatusConsumer


# Маршруты WebSocket-подключений
websocket_urlpatterns = [
    path("ws/status/", ConnectionStatusConsumer.as_asgi()),
]
