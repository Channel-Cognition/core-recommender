from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView
)
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from suggestions.routing import ws_url_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(),
         name='api-schema',
         ),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='api-schema'),
         name='api-docs'
         ),
    path('api/user/', include('user.urls', namespace='user')),
    path('api/suggestions/', include('suggestions.urls', namespace='suggestions')),
    path('api/convos/', include('convos.urls', namespace='convos')),
    path('api/movies/', include('movies.urls', namespace='movies')),
    # Include WebSocket URL patterns
    path('ws/', include(ws_url_patterns)),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
