import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TaskProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        self.group_name = f'task_progress_{self.task_id}'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        print(f"Task ID: {self.task_id}")
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def task_progress_update(self, event):
        await self.send(text_data=json.dumps({
            'progress': event['progress'],
            'percent': event['percent'],
            'composition_id': event.get('composition_id'),
        }))