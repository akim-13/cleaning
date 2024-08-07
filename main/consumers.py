import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

# INFO: Channels needs a Redis server. To run it, run:
# sudo docker run --rm -p 6379:6379 redis:7

class FillOutConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name_location = self.scope["url_route"]["kwargs"]["location_name"]

        # Join a group (a fill-out table for this location).
        async_to_sync(self.channel_layer.group_add)(
            self.group_name_location, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave the group.
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name_location, self.channel_name
        )

    # Receive message from WebSocket.
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to group.
        async_to_sync(self.channel_layer.group_send)(
            self.group_name_location,
            {
                "type": "test.message",
                "message": message,
            },
        )

    # Receive message from group.
    def test_message(self, event):
        message = event["message"]
        self.send(text_data=json.dumps({"message": message}))
