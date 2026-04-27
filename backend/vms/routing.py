from django.urls import path

from .consumers import ConnectionStatusConsumer


websocket_urlpatterns = [
    path("ws/status/", ConnectionStatusConsumer.as_asgi()),
]
