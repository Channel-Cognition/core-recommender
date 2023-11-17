import uuid

from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from chancog.entities import Snippet as SnippetCosmosDB

from queries.convo import Convo as ConvoCosmosDB

# Create your models here.


class Convo(models.Model):
    convo_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    created_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    updated_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.convo_id


class Snippet(models.Model):
    FRAMING = "FRAMING"
    ASSISTANT_MESSAGE = "ASSISTANT MESSAGE"
    USER_MESSAGE = "USER MESSAGE"
    LLM_MESSAGE = "LLM MESSAGE"

    SNIPPET_TYPE_CHOICES = (
        (FRAMING, 'FRAMING'),
        (ASSISTANT_MESSAGE, 'ASSISTANT MESSAGE'),
        (USER_MESSAGE, 'USER MESSAGE'),
        (LLM_MESSAGE, 'LLM MESSAGE')
    )

    snippet_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    convo = models.ForeignKey(
        Convo,
        on_delete=models.CASCADE
    )
    text = models.TextField()
    pydantic_text = models.JSONField(blank=True, null=True)
    snippet_type = models.CharField(max_length=200, choices=SNIPPET_TYPE_CHOICES)
    is_initiate = models.BooleanField(default=False)
    created_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    updated_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.snippet_id

