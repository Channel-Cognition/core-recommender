import uuid

from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from chancog.entities import Snippet as SnippetCosmosDB

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


@receiver(post_save, sender=Snippet)
def snippet_post_save(sender, instance, created, *args, **kwargs):
    # snippet will be saved after mirroring to CosmosDB successfully
    import time
    start=time.time()
    if created:
        convo_id = str(instance.convo.convo_id)
        if not ConvoCosmosDB(convo_id=convo_id).is_exist():
            convo_id = None
            is_created = ConvoCosmosDB(convo_id=str(instance.convo.convo_id)).create()
            if is_created:
                convo_id = str(instance.convo.convo_id)
        ConvoCosmosDB(convo_id=convo_id).create_snippets([SnippetCosmosDB(
            snippet_type=instance.snippet_type,
            text=instance.text, timestamp=instance.created_date)])
        end=time.time()
        print("post_save", end-start)
        return convo_id

