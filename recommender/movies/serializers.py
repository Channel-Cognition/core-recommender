from rest_framework import serializers
from .models import Movie, Genre, Channel, MovieImage


class MovieImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieImage
        fields = ["image_b64_small", "image_b64_medium", "image_b64_large"]


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
    movie_image = MovieImageSerializer()

    class Meta:
        model = Movie
        fields = ('movie_id', 'title', 'year',
                  'thumbnail', 'age_start', 'genres', 'channels', 'movie_image')
        read_only_fields = 'movie_id',





# from rest_framework import serializers
# from django.core.cache import cache
#
# class ImageSerializer(serializers.Serializer):
#     image_url = serializers.CharField(max_length=255)
#     image_data = serializers.SerializerMethodField()
#
#     class Meta:
#         model = MyModel
#
#     def get_image_data(self, obj):
#         image_url = obj['image_url']
#         cached_data = cache.get(image_url)
#
#         if cached_data is None:
#             # Image data is not in cache, fetch it and cache it
#             # Replace this part with your image retrieval logic
#             import requests
#             response = requests.get(image_url)
#
#             if response.status_code == 200:
#                 image_data = response.content
#                 cache.set(image_url, image_data, 60 * 15)  # Cache for 15 minutes
#             else:
#                 return None
#         else:
#             image_data = cached_data
#
#         return image_data
#
#
# from django.http import HttpResponse
# from django.core.cache import cache
# from PIL import Image
#
# def cached_image(request, image_url):
#     # Define the cache key based on the image URL
#     cache_key = f'image_cache_{image_url}'
#
#     # Attempt to fetch the image from the cache
#     cached_image_data = cache.get(cache_key)
#
#     if cached_image_data:
#         # If the image is cached, serve it
#         return HttpResponse(cached_image_data, content_type='image/jpeg')
#     else:
#         # If the image is not in the cache, fetch it
#         import requests
#
#         response = requests.get(image_url)
#         if response.status_code == 200:
#             image_data = response.content
#
#             # Resize the image or perform any other image processing as needed
#             image = Image.open(io.BytesIO(image_data))
#             image = image.resize((200, 200))  # Resize to your desired dimensions
#
#             # Convert the image back to bytes
#             resized_image_data = io.BytesIO()
#             image.save(resized_image_data, format="JPEG")
#             resized_image_data = resized_image_data.getvalue()
#
#             # Cache the resized image for 15 minutes (adjust as needed)
#             cache.set(cache_key, resized_image_data, 60 * 15)
#
#             # Serve the resized image
#             return HttpResponse(resized_image_data, content_type='image/jpeg')
#         else:
#             return HttpResponse("Image not found", status=404)

