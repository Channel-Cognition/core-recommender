# Generated by Django 4.2.6 on 2023-10-13 00:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("suggestions", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="snippet",
            name="is_initiate",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="convo",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
