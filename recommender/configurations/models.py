from django.db import models

# Create your models here.


class LLMModels(models.Model):
    model_name = models.CharField(max_length=255)
    maximum_output_token = models.IntegerField(default=1024)
    is_json_response = models.BooleanField(default=False)
    api_key = models.CharField(max_length=255)
    api_endpoint = models.CharField(max_length=255)
    created_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    updated_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.model_name


class Framing(models.Model):
    content = models.TextField()
    created_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    updated_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.model_name