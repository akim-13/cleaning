import json, redis, random
from uuid import uuid4
from bs4 import BeautifulSoup
from threading import Event, Thread
from collections import defaultdict
from django.shortcuts import redirect
from asgiref.sync import async_to_sync
from django.template.loader import render_to_string
from channels.generic.websocket import WebsocketConsumer
from .views import encode_location_name
from .forms import FillOutForm, CustomUserCreationForm, CustomAuthenticationForm,LocationForm, ZoneFormSet


# NOTE: Channels needs a Redis server. To run it, run:
# sudo docker run --rm -p 6379:6379 redis:7

redis_client = redis.Redis(host='localhost', port=6379, db=0)

class FillOutConsumer(WebsocketConsumer):
    def connect(self):
        self.location_name = self.scope['url_route']['kwargs']['location_name']
        self.group_name_location = encode_location_name(self.location_name)

        # Join a group (a fill-out table for this location).
        async_to_sync(self.channel_layer.group_add)(
            self.group_name_location, self.channel_name
        )

        self.accept() 

        if redis_client.get(f'submission_successful_in_{self.location_name}') is None:
            redis_client.set(f'submission_successful_in_{self.location_name}', 'unknown')

        submission_successful = redis_client.get(f'submission_successful_in_{self.location_name}').decode('utf-8')
        group_has_active_users = redis_client.scard(f'active_users_in_{self.location_name}') > 0        
        if submission_successful == 'true':
            # NOTE: Form submission causes the page to reload, hence the submitter's
            # websocket has to reconnect. This if prevents them from unnecessarily
            # requesting the page contents from other users.
            pass
        elif group_has_active_users:
            active_user = redis_client.srandmember(f'active_users_in_{self.location_name}').decode('utf-8')

            async_to_sync(self.channel_layer.send)(
                active_user, {
                    'type': 'request_current_page_contents',
                    'requester': self.channel_name
                }
            )

            self.update_current_page_contents_event = Event()
            update_current_page_contents_thread = Thread(target=self.update_current_page_contents)
            update_current_page_contents_thread.start()

        redis_client.sadd(f'active_users_in_{self.location_name}', self.channel_name)


    def update_current_page_contents(self):
        if self.update_current_page_contents_event.wait(timeout=5):
            self.send(text_data=json.dumps({
                'requested_action': 'update_current_page_contents',
                'current_page_contents': self.current_page_contents,
                'field_values': self.field_values,
                'role': self.get_user_role()
            }))
        else:
            # TODO: Implement actual logging.
            print('ERROR TIMEOUT\n'*5)


    def disconnect(self, close_code):
        # Leave the group.
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name_location, self.channel_name
        )

        redis_client.srem(f'active_users_in_{self.location_name}', self.channel_name)

        group_is_empty = redis_client.scard(f'active_users_in_{self.location_name}') == 0
        if group_is_empty:
            redis_client.delete(f'active_users_in_{self.location_name}')


    # Receive message from WebSocket.
    def receive(self, text_data):
        received_json_data = json.loads(text_data)
        requested_action = received_json_data['requested_action']

        match requested_action:
            case 'send_current_page_contents':
                current_page_contents = received_json_data['current_page_contents']
                csrf_token = received_json_data['csrf_token']
                field_values = received_json_data['field_values']
                requester = received_json_data['requester']

                async_to_sync(self.channel_layer.send)(
                    requester, {
                        'type': 'send_current_page_contents',
                        'current_page_contents': current_page_contents.replace(csrf_token, ''),
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

            case 'update_field':
                row_UUID = received_json_data['row_UUID']
                field_name = received_json_data['field_name']
                field_value = received_json_data['field_value']
                self.broadcast_data_to_location_group({
                    'type': 'send_field_update_to_websocket',
                    'row_UUID': row_UUID,
                    'field_name': field_name,
                    'field_value': field_value
                })


    def broadcast_data_to_location_group(self, data):
        async_to_sync(self.channel_layer.group_send)(self.group_name_location, data)


    def generate_new_row_html(self, row_UUID):
        form = FillOutForm(location=self.location_name)
        return render_to_string('main/_new_row.html', {'form': form, 'row_UUID': row_UUID})


    def send_new_row_to_websocket(self, event):
        new_row_html = event['new_row_html']
        row_UUID = event['row_UUID']

        role = self.get_user_role()

        self.send(text_data=json.dumps({
            'requested_action': 'append_row',
            'new_row_html': new_row_html,
            'row_UUID': row_UUID,
            'role': role
        }))


    def get_user_role(self):
        user = self.scope['user']
        roles = list(user.groups.values_list('name', flat=True))

        if 'manager_contractor' in roles:
            role = 'contractor'
        elif 'manager_customer' in roles:
            role = 'customer'
        else:
            raise Exception('User must be assigned to either manager_contractor or manager_customer group')

        return role
            

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


    def send_field_update_to_websocket(self, event):
        row_UUID = event['row_UUID']
        field_name = event['field_name']
        field_value = event['field_value']

        self.send(text_data=json.dumps({
            'requested_action': 'update_field',
            'row_UUID': row_UUID,
            'field_name': field_name,
            'field_value': field_value
        }))


    # NOTE: This is called from the fill_out view.
    def send_page_contents_after_submission(self, event):
        page_contents_after_submission = event['page_contents_after_submission']
        html_body = BeautifulSoup(page_contents_after_submission, 'html.parser').body.decode_contents()

        self.send(text_data=json.dumps({
            'requested_action': 'update_current_page_contents',
            'current_page_contents': html_body,
        }))