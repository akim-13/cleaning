from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"fill-out/(?P<location_name>.+)/$", consumers.FillOutConsumer.as_asgi()),  
]