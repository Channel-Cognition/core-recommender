from django.contrib import admin

# Register your models here.
from django.contrib import admin
from.models import *


class MovieAdmin(admin.ModelAdmin):
    pass


admin.site.register(Movie, MovieAdmin)