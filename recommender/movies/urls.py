from django.urls import path
from .views import MovieListView, DeleteAllMoviesView
app_name = "movies"
urlpatterns = [
    path('', MovieListView.as_view(), name='movie-list'),
    path('delete-all/', DeleteAllMoviesView.as_view(), name='delete-all-movies'),

]
