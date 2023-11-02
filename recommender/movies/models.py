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

