from rest_framework import serializers
from .models import Movie, Genre


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("name")


class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, required=False)

    class Meta:
        model = Movie
        fields = ('movie_id', 'title', 'year',
                  'thumbnail', "age_start", "genres")
        read_only_fields = 'movie_id',


# class GenreSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Genre
#         fields = ("name")
#
#
# class MovieSerializer(serializers.Serializer):
#     genres = GenreSerializer(many=True, required=False)
#
#     class Meta:
#         model = Movie
#         fields = ('movie_id', 'title', 'year',
#                   'thumbnail', "age_start", "genres")
#         read_only_fields = 'movie_id',