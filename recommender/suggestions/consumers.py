# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ResultConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        convo_id = self.scope['url_route']['kwargs']['convo_id']
        await self.channel_layer.group_add(
            f"convo_group_{convo_id}",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        convo_id = self.scope['url_route']['kwargs']['convo_id']
        await self.channel_layer.group_discard(
            f"convo_group_{convo_id}",
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def send_data(self, event):
        data = event['data']
        await self.send(text_data=json.dumps(data))
