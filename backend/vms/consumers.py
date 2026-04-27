import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


class ConnectionStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]

        await self.accept()

        if user.is_anonymous:
            await self.send(
                text_data=json.dumps(
                    {
                        "status": "error",
                        "message": "Пользователь не авторизован.",
                    }
                )
            )
            await self.close()
            return

        self.group_name = f"user_{user.id}_connection_status"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        proxy = await self.get_user_proxy(user.id)

        if proxy:
            await self.send(
                text_data=json.dumps(
                    {
                        "status": "connected",
                        "message": "Пользователь подключён к прокси.",
                        "proxy": proxy,
                    }
                )
            )
        else:
            await self.send(
                text_data=json.dumps(
                    {
                        "status": "disconnected",
                        "message": "Прокси не назначен.",
                    }
                )
            )

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

    async def connection_status(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "status": event["status"],
                    "message": event["message"],
                    "proxy": event.get("proxy"),
                }
            )
        )

    @database_sync_to_async
    def get_user_proxy(self, user_id):
        from .models import VirtualMachine

        vm = VirtualMachine.objects.filter(
            current_user_id=user_id,
            is_active=True,
        ).first()

        if not vm:
            return None

        return {
            "host": vm.host,
            "port": vm.port,
            "protocol": vm.protocol,
        }
