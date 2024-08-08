import json
from asgiref.sync import async_to_sync
from django.template.loader import render_to_string
from channels.generic.websocket import WebsocketConsumer
from .forms import CustomUserCreationForm, CustomAuthenticationForm, MarkForm, CommentForm, LocationForm, ZoneForm


# INFO: Channels needs a Redis server. To run it, run:
# sudo docker run --rm -p 6379:6379 redis:7

class FillOutConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name_location = self.scope['url_route']['kwargs']['location_name']

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
        received_json_data = json.loads(text_data)
        requested_action = received_json_data['requested_action']

        if requested_action == 'append_row':
            form_UID = received_json_data['form_UID']
            new_row_html = self.generate_new_row_html(form_UID)

            self.broadcast_data_to_location_group({
                'type': 'send.new.row.to.websocket',
                'new_row_html': new_row_html
            })


    def broadcast_data_to_location_group(self, data):
        async_to_sync(self.channel_layer.group_send)(self.group_name_location, data)


    def generate_new_row_html(self, form_UID):
        form = MarkForm()
        tmp = 'hi'
        tmp = render_to_string('main/_new_row.html', {'form': form, 'form_UID': form_UID})
        return tmp
        

    # Receive message from a location group.
    def send_new_row_to_websocket(self, event):
        new_row_html = event['new_row_html']
        self.send(text_data=json.dumps({'new_row_html': new_row_html}))
