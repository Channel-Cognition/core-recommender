# asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from suggestions.routing import ws_url_patterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recommender.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
                ws_url_patterns
        )
    ),
})
