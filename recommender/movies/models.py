import uuid
from django.db import models

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


class Movie(models.Model):
    movie_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    title = models.CharField(max_length=150)
    year = models.IntegerField()
    thumbnail = models.URLField(max_length=200)
    age_start = models.IntegerField(blank=True, null=True)
    genres = models.ManyToManyField(
        'Genre',
        blank=True,
        null=True
    )

    class Meta:
        unique_together = (('title', 'year'),)
