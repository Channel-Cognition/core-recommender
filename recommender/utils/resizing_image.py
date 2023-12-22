import base64

import requests

from PIL import Image
from io import BytesIO

from django.core.cache import cache


def save_image_from_url_with_resizing(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Open the image using Pillow
            img = Image.open(BytesIO(response.content))

            # Resize the image
            img_small = img.resize((100, 150), Image.LANCZOS)
            img_medium = img.resize((200, 300), Image.LANCZOS)
            img_large = img.resize((400, 600), Image.LANCZOS)

            # Convert the resized image data to base64
            buffered = BytesIO()
            img_small.save(buffered, format="JPEG")
            image_data_base64_small = base64.b64encode(buffered.getvalue()).decode('utf-8')

            buffered = BytesIO()
            img_medium.save(buffered, format="JPEG")
            image_data_base64_medium = base64.b64encode(buffered.getvalue()).decode('utf-8')

            buffered = BytesIO()
            img_large.save(buffered, format="JPEG")
            image_data_base64_large = base64.b64encode(buffered.getvalue()).decode('utf-8')

            return image_data_base64_small, image_data_base64_medium, image_data_base64_large
        else:
            print("Failed to fetch image from URL.")
    except Exception as e:
        print("Error:", str(e))


def get_or_create_image_cache(thumbnail_url):
    image_dict = {"image_b64_small": None,
                  "image_b64_medium": None,
                  "image_b64_large": None}
    if thumbnail_url:
        cache_key = f'image_cache_{thumbnail_url}'
        cached_image_data = cache.get(cache_key)
        if cached_image_data:
            image_dict = cached_image_data
            print("THE CACHE IS EXISTS", flush=True)
        else:
            print("NEW CACHE", flush=True)
            image_b64_small, image_b64_medium, image_b64_large = save_image_from_url_with_resizing(
                url=thumbnail_url)
            image_dict = {"image_b64_small":image_b64_small,
                          "image_b64_medium":image_b64_medium,
                          "image_b64_large":image_b64_large}
            cache.set(cache_key, image_dict, None)
    return image_dict