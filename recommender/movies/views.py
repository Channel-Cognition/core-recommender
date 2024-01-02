from rest_framework.generics import ListAPIView, DestroyAPIView
from .models import Movie
from .serializers import MovieSerializer


class MovieListView(ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class DeleteAllMoviesView(DestroyAPIView):
    queryset = Movie.objects.all()

    def delete(self, request, *args, **kwargs):
        # Delete all movies
        self.queryset.delete()
        return self.destroy(request, *args, **kwargs)