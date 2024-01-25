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


class MatchBundle(models.Model):
    snippet = models.ForeignKey(Snippet, related_name='match_bundles', on_delete=models.CASCADE)

    created_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    updated_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.snippet_id


class ItemMatch(models.Model):
    match_bundle = models.ForeignKey(MatchBundle, related_name='item_matches', on_delete=models.CASCADE)
    external_id = models.CharField(max_length=200, null=True, blank=True)
    quality = models.CharField(max_length=100, null=True, blank=True)
    details = models.TextField(null=True, blank=True)

    created_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    updated_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.snippet_id

class LLMStream(models.Model):
    """
    A streaming call to the OpenAI large language model (LLM) API

    Attributes:
        llm_stream_id (UUIDField): A unique identifier for the LLM stream.
        convo (ForeignKey): A reference to the associated conversation.
        status (CharField): The current status of the LLM stream, which can be
                            'FAILURE', 'SUCCESS', or 'PENDING'.
    """

    # Unique identifier for the LLM stream. It's auto-generated and non-editable.
    llm_stream_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)

    # Foreign key linking to the Convo model. On deletion of the referenced Convo, this record will also be deleted.
    convo = models.ForeignKey(
        Convo,
        on_delete=models.CASCADE
    )

    # Define the set of valid choices for the status of the LLM stream.
    STATUS_CHOICES = [
        ('FAILURE', 'Failure'),  # Represents a failed state of the LLM stream.
        ('SUCCESS', 'Success'),  # Represents a successful state of the LLM stream.
        ('PENDING', 'Pending'),  # Represents a pending state of the LLM stream.
    ]

    # The status field stores the current state of the LLM stream and can only take values defined in STATUS_CHOICES.
    status = models.CharField(
        max_length=200,
        choices=STATUS_CHOICES,
    )

class LLMStreamChunk(models.Model):
    """
    Chunk of text from a streaming call to the OpenAI Large Language Model (LLM) API.

    Each chunk is a part of a larger LLMStream and contains a portion of the text from that stream.

    Attributes:
        id (UUIDField): A unique identifier for this chunk.
        llm_stream (ForeignKey): A reference to the associated LLMStream.
        text (TextField): The text content of this chunk.
        timestamp (DateTimeField): The timestamp when this chunk was created.
    """

    # Unique identifier for the chunk. It's auto-generated and non-editable.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Foreign key linking to the LLMStream model. On deletion of the referenced LLMStream, this record will also be deleted.
    llm_stream = models.ForeignKey(
        LLMStream,
        on_delete=models.CASCADE
    )

    # A text field to store the content of the chunk.
    text = models.TextField()

    # Timestamp for when the chunk is created.
    timestamp = models.DateTimeField(auto_now_add=True)