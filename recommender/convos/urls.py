from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('', views.ConvoViewSet)

app_name = 'convos'

urlpatterns = [
    path('', include(router.urls))
]