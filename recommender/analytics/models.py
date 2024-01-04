from django.db import models

# Create your models here.
# 'call_diagnostics': {'name': 'OpenAIHandler.call_gpt', 'children': [{...}], 'model': 'gpt-4', 'is_azure': True, 'deployment_name': 'gpt-4-default-caeast', 'prompt_tokens': 366, 'completion_tokens': 50, 'latency_ms': 18317.461000000003}}


class RunningResult(models.Model):
    run_id = models.CharField(max_length=255)
    model_name = models.CharField(max_length=255)
    deployment_name = models.CharField(max_length=255)
    promp_tokens = models.IntegerField()
    completion_tokens = models.IntegerField()
    cost = models.IntegerField()
    request = models.CharField(max_length=255)
    response = models.CharField(max_length=255)
    created_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    updated_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.run_id
