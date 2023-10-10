# Generated by Django 4.2.6 on 2023-10-08 22:25

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Movie",
            fields=[
                (
                    "movie_id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("title", models.CharField(max_length=150)),
                ("year", models.IntegerField()),
                ("thubmnail", models.URLField()),
            ],
            options={"unique_together": {("title", "year")},},
        ),
    ]