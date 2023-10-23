import uuid
import base64

import requests
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from io import BytesIO


# Create your models here.
# class Ratings(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     moodboard_id = db.Column(db.Integer, db.ForeignKey('moodboards.id'), nullable=False)
#     title = db.Column(db.String(120))
#     year = db.Column(db.Integer)
#     rating = db.Column(db.Float)

class Genre(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Channel(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Movie(models.Model):
    movie_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True)
    title = models.CharField(
        max_length=150,
        db_index=True)
    year = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        db_index=True)
    thumbnail = models.URLField(
        max_length=200,
        blank=True,
        null=True)
    age_start = models.CharField(
        max_length=10,
        blank=True,
        null=True)
    genres = models.ManyToManyField(
        'Genre',
        blank=True,
        null=True
    )
    channels = models.ManyToManyField(
        'Channel',
        blank=True,
        null=True
    )
    short_description = models.CharField(
        max_length=150,
        blank=True,
        null=True)
    long_description = models.TextField(
        blank=True,
        null=True)

    class Meta:
        unique_together = (('title', 'year'),)

    def save_image_from_url_with_resizing(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # Open the image using Pillow
                img = Image.open(BytesIO(response.content))

                # Resize the image
                img_small = img.resize((100, 150), Image.LANCZOS)
                img_medium = img.resize((400, 600), Image.LANCZOS)
                img_large = img.resize((800, 1000), Image.LANCZOS)

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