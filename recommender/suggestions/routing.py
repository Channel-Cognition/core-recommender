# your_app/routing.py

from django.urls import path
from . import consumers

ws_url_patterns = [
    path('result/', consumers.ResultConsumer.as_asgi())
]
