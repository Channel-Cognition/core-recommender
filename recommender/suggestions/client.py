from django.conf import settings
from django.core.cache import cache
from django.db import transaction

import guardrails as gd
import openai

from movies.models import Movie, Genre, Channel
from .models import Snippet
from .pydantics import MovieInfo
from .suggestion import Suggestion


def perform_search(query, convo):
    data = []
    # messages [{"role": role, "content": content}, {"role": role, "content": content}]
    data.append({
                "snippet_type": "USER MESSAGE",
                "text": query,
                "convo": convo
            })
    snippets = Snippet.objects.filter(convo=convo, snippet_type="FRAMING")
    messages = [{"role": get_role(snippet.snippet_type), "content":snippet.text}for snippet in snippets]
    messages.append({"role":"user", "content":query})
    llm_response = Suggestion(query).process_llm_response()
    movie_items = llm_response["items"]
    movies_dicts = get_or_create_movies(movie_items)
    data.append({
                "snippet_type": "LLM MESSAGE",
                "text": "Sure, Here are recommendations movies for you!",
                "convo": convo,
                "pydantic_text": movies_dicts
            })
    for snippet in data:
        Snippet.objects.create(**snippet)
    return convo


def get_or_create_genres(genres, movie):
    for genre in genres:
        instance_genre, created = Genre.objects.get_or_create(name__iexact=genre,
                                                              defaults={"name":genre})
        movie.genres.add(instance_genre)


def get_or_create_channels(channels, movie):
    for channel in channels:
        instance_genre, created = Channel.objects.get_or_create(name__iexact=channel,
                                                                defaults={"name":channel})
        movie.channels.add(instance_genre)


@transaction.atomic
def get_or_create_movies(movie_items):
    list_movies = []
    for movie in movie_items:
        movie_dict = {}
        movie_title = movie["title"]
        movie_year = movie["year"]
        movie_ages = movie.get("ages", "")
        short_description = movie["short_description"]
        long_description = movie["long_description"]
        thumbnail_url = movie["thumbnail_url"]
        genres = movie.get("genres", [])
        channels = movie.get("streaming_on", [])
        instance_movie, created = Movie.objects.get_or_create(
            title=movie_title,
            year=movie_year,
            defaults={"short_description":short_description,
                      "long_description":long_description,
                      "age_start": movie_ages,
                      "thumbnail": thumbnail_url})
        if genres:
            get_or_create_genres(genres, instance_movie)
        if channels:
            get_or_create_channels(channels, instance_movie)

        movie_dict["title"] = instance_movie.title
        movie_dict["year"] = instance_movie.year
        movie_dict["genres"] = [genre.name for genre in instance_movie.genres.all()]
        movie_dict["channels"] = [channel.name for channel in instance_movie.channels.all()]
        movie_dict["summary"] = instance_movie.short_description
        movie_dict["long_description"] = instance_movie.long_description
        movie_dict["thumbnail"] = instance_movie.thumbnail
        movie_dict["image"] = get_or_create_image_cache(instance_movie)
        list_movies.append(movie_dict)
    return list_movies


def get_or_create_image_cache(instance):
    if instance.thumbnail:
        cache_key = f'image_cache_{instance.thumbnail}'
        cached_image_data = cache.get(cache_key)
        if cached_image_data:
            image_dict = cached_image_data
        else:
            image_b64_small, image_b64_medium, image_b64_large = instance.save_image_from_url_with_resizing(
                url=instance.thumbnail)
            image_dict = {"image_b64_small":image_b64_small,
                          "image_b64_medium":image_b64_medium,
                          "image_b64_large":image_b64_large}
            cache.set(cache_key, image_dict, None)
    return image_dict


def get_first_sentence(message):
    first_sentence = message.split(':', 1)[0]
    return first_sentence


def extract_response(llm_response):
    llm_response = llm_response
    prompt = """

    ${llm_response}

    ${gr.complete_json_suffix_v2}
    """
    # From pydantic:
    guard = gd.Guard.from_pydantic(output_class=MovieInfo, prompt=prompt)
    OPEN_AI_API_KEY = settings.OPEN_AI_KEY
    OAI_KEY = OPEN_AI_API_KEY

    # Wrap the OpenAI API call with the `guard` object
    openai.api_key = OAI_KEY
    raw_llm_output, validated_output = guard(
        openai.Completion.create,
        prompt_params={"llm_response": llm_response},
        engine="text-davinci-003",
        max_tokens=2048,
        temperature=0.3,
    )
    print(validated_output)
    print(raw_llm_output)
    return validated_output


def get_role(snippet_type):
    dict_role = {'FRAMING': 'system',
                 'ASSISTANT MESSAGE': 'assistant',
                 'USER MESSAGE': 'user',
                 'LLM MESSAGE': 'assistant'}
    return dict_role[snippet_type]