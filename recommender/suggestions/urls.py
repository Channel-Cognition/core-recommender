from django.urls import path

from . import views
app_name = "suggestions"
urlpatterns = [
    path('', views.SearchListView.as_view(), name='search'),
    path('dummy', views.DummyListView.as_view(), name='demo'),
    path('free', views.FreeSearchListView.as_view(), name='free-search')

]