import json, redis
from uuid import uuid4
from threading import Event, Thread
from collections import defaultdict
from asgiref.sync import async_to_sync
from django.template.loader import render_to_string
from channels.generic.websocket import WebsocketConsumer
from .forms import FillOutForm, CustomUserCreationForm, CustomAuthenticationForm, MarkForm, CommentForm, LocationForm, ZoneForm

# NOTE: Channels needs a Redis server. To run it, run:
# sudo docker run --rm -p 6379:6379 redis:7

redis_client = redis.Redis(host='localhost', port=6379, db=0)

class FillOutConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name_location = self.scope['url_route']['kwargs']['location_name']

        # Join a group (a fill-out table for this location).
        async_to_sync(self.channel_layer.group_add)(
            self.group_name_location, self.channel_name
        )

        self.accept() 

        group_has_active_users = redis_client.scard(f'active_users:{self.group_name_location}') > 0        
        if group_has_active_users:
            active_user = redis_client.srandmember(f'active_users:{self.group_name_location}').decode('utf-8')

            async_to_sync(self.channel_layer.send)(
                active_user, {
                    'type': 'request_current_page_contents',
                    'requester': self.channel_name
                }
            )

            self.update_current_page_contents_event = Event()
            update_current_page_contents_thread = Thread(target=self.update_current_page_contents)
            update_current_page_contents_thread.start()

        redis_client.sadd(f'active_users:{self.group_name_location}', self.channel_name)


    def update_current_page_contents(self):
        if self.update_current_page_contents_event.wait(timeout=5):
            self.send(text_data=json.dumps({
                'requested_action': 'update_current_page_contents',
                'current_page_contents': self.current_page_contents,
                'field_values': self.field_values
            }))
        else:
            # TODO: Implement actual logging.
            print('ERROR TIMEOUT\n'*5)


    def disconnect(self, close_code):
        # Leave the group.
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name_location, self.channel_name
        )

        redis_client.srem(f'active_users:{self.group_name_location}', self.channel_name)

        group_is_empty = redis_client.scard(f'active_users:{self.group_name_location}') == 0
        if group_is_empty:
            redis_client.delete(f'active_users:{self.group_name_location}')


    # Receive message from WebSocket.
    def receive(self, text_data):
        received_json_data = json.loads(text_data)
        requested_action = received_json_data['requested_action']

        match requested_action:
            case 'send_current_page_contents':
                current_page_contents = received_json_data['current_page_contents']
                field_values = received_json_data['field_values']
                requester = received_json_data['requester']
                async_to_sync(self.channel_layer.send)(
                    requester, {
                        'type': 'send_current_page_contents',
                        'current_page_contents': current_page_contents,
                        'field_values': field_values
                    }
                )
            
            case 'update_current_page_contents':
                self.current_page_contents = received_json_data['current_page_contents']
                self.field_values = received_json_data['field_values']

                if hasattr(self, 'update_current_page_contents_event'):
                    # Continue execution inside `update_current_page_contents()`.
                    self.update_current_page_contents_event.set()

            case 'append_row':
                row_UUID = str(uuid4())
                new_row_html = self.generate_new_row_html(row_UUID)

                self.broadcast_data_to_location_group({
                    # `type` calls the specified function.
                    'type': 'send_new_row_to_websocket',
                    'new_row_html': new_row_html,
                    'row_UUID': row_UUID
                })
            
            case 'change_time_period':
                self.broadcast_data_to_location_group({
                    'type': 'send_change_time_period_request_to_websocket'
                })

            case 'field_change':
                row_UUID = received_json_data['row_UUID']
                field_name = received_json_data['field_name']
                field_value = received_json_data['field_value']
                self.broadcast_data_to_location_group({
                    'type': 'send_field_change_to_websocket',
                    'row_UUID': row_UUID,
                    'field_name': field_name,
                    'field_value': field_value
                })


    def broadcast_data_to_location_group(self, data):
        async_to_sync(self.channel_layer.group_send)(self.group_name_location, data)


    def generate_new_row_html(self, row_UUID):
        form = FillOutForm()
        return render_to_string('main/_new_row.html', {'form': form, 'row_UUID': row_UUID})


    def send_new_row_to_websocket(self, event):
        new_row_html = event['new_row_html']
        row_UUID = event['row_UUID']
        self.send(text_data=json.dumps({
            'requested_action': 'append_row',
            'new_row_html': new_row_html,
            'row_UUID': row_UUID
        }))

    
    def send_change_time_period_request_to_websocket(self, event):
        self.send(text_data=json.dumps({'requested_action': 'change_time_period'}))


    def request_current_page_contents(self, event):
        self.send(text_data=json.dumps({
            'requested_action': 'request_current_page_contents',
            'requester': event['requester']
        }))

    def send_current_page_contents(self, event):
        self.send(text_data=json.dumps({
            'requested_action': 'send_current_page_contents',
            'current_page_contents': event['current_page_contents'],
            'field_values': event['field_values']
        }))

    def send_field_change_to_websocket(self, event):
        row_UUID = event['row_UUID']
        field_name = event['field_name']
        field_value = event['field_value']

        self.send(text_data=json.dumps({
            'requested_action': 'field_change',
            'row_UUID': row_UUID,
            'field_name': field_name,
            'field_value': field_value
        }))
