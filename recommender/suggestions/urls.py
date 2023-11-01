from django.urls import path

from . import views
app_name = "suggestions"
urlpatterns = [
    path('', views.SearchListV2View.as_view(), name='search')
]