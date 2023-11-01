from django.urls import path

from . import views
app_name = "suggestions"
urlpatterns = [
    path('', views.SearchListViewV3.as_view(), name='search')
]