from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes
)

from movies.serializers import MovieSerializer


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                'q',
                OpenApiTypes.STR,
                description='Query Suggestion'
            ),
        ]
    )
)



class SearchListView(APIView):
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = None
        # if request.user.is_authenticated:
        #     user = request.user.username
        query = request.GET.get('q')
        if not query:
            return Response('', status=400)
        # TODO Integrate This Code With AI
        # results = client.perform_search(query)
        results = [
            {
                "id": 1,
                "title": "Beetlejuice",
                "year": "1988",
                "thumbnail": "https://images-na.ssl-images-amazon.com/images/M/MV5BMTUwODE3MDE0MV5BMl5BanBnXkFtZTgwNTk1MjI4MzE@._V1_SX300.jpg"
            },
            {
                "id": 2,
                "title": "The Cotton Club",
                "year": "1984",
                "thumbnail": "https://images-na.ssl-images-amazon.com/images/M/MV5BMTU5ODAyNzA4OV5BMl5BanBnXkFtZTcwNzYwNTIzNA@@._V1_SX300.jpg"
            },
            {
                "id": 3,
                "title": "The Shawshank Redemption",
                "year": "1994",
                "thumbnail": "https://images-na.ssl-images-amazon.com/images/M/MV5BODU4MjU4NjIwNl5BMl5BanBnXkFtZTgwMDU2MjEyMDE@._V1_SX300.jpg"
            },
            {
                "id": 4,
                "title": "Crocodile Dundee",
                "year": "1986",
                "thumbnail": "https://images-na.ssl-images-amazon.com/images/M/MV5BMTg0MTU1MTg4NF5BMl5BanBnXkFtZTgwMDgzNzYxMTE@._V1_SX300.jpg"
            },
            {
                "id": 5,
                "title": "Valkyrie",
                "year": "2008",
                "thumbnail": "http://ia.media-imdb.com/images/M/MV5BMTg3Njc2ODEyN15BMl5BanBnXkFtZTcwNTAwMzc3NA@@._V1_SX300.jpg"
            },
            {
                "id": 6,
                "title": "Ratatouille",
                "year": "2007",
                "thumbnail": "https://images-na.ssl-images-amazon.com/images/M/MV5BMTMzODU0NTkxMF5BMl5BanBnXkFtZTcwMjQ4MzMzMw@@._V1_SX300.jpg"
            },
            {
                "id": 7,
                "title": "City of God",
                "year": "2002",
                "thumbnail": "https://images-na.ssl-images-amazon.com/images/M/MV5BMjA4ODQ3ODkzNV5BMl5BanBnXkFtZTYwOTc4NDI3._V1_SX300.jpg"
            },
            {
                "id": 8,
                "title": "Memento",
                "year": "2000",
                "thumbnail": "https://images-na.ssl-images-amazon.com/images/M/MV5BNThiYjM3MzktMDg3Yy00ZWQ3LTk3YWEtN2M0YmNmNWEwYTE3XkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1_SX300.jpg"
            },
            ]
        serializer = MovieSerializer(results, many=True)
        return Response(serializer.data)