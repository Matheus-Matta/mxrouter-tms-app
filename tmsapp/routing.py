from django.urls import re_path
from tmsapp.consumers import TaskProgressConsumer

websocket_urlpatterns = [
    re_path(r'ws/tasks/(?P<task_id>[\w-]+)/$', TaskProgressConsumer.as_asgi()),
]