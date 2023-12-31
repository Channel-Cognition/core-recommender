from rest_framework import serializers
from .models import Movie, Genre, Channel


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ["name"]


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["name"]


class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True)
    channels = ChannelSerializer(many=True)

    class Meta:
        model = Movie
        fields = ('movie_id', 'title', 'year',
                  'thumbnail', 'age_start', 'genres', 'channels')
        read_only_fields = 'movie_id',
