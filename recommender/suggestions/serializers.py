from django.conf import settings
from rest_framework import serializers

from .models import (
    Convo, Snippet
)


class SnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snippet
        fields = ('snippet_id', 'text', 'snippet_type',
                  'is_initiate', 'pydantic_text', 'created_date', 'updated_date',)
        read_only_fields = 'snippet_id',


class ConvoSerializer(serializers.ModelSerializer):
    snippets = SnippetSerializer(many=True, required=True, source='snippet_set')

    class Meta:
        model = Convo
        fields = ('convo_id', 'user', 'snippets')
        read_only_fields = 'convo_id',

    # def _create_default_snippet(self):
    #     new_convo = Convo.objects.create(
    #         auth_user=self.context['request'].user
    #     )
    #     data = [
    #         {
    #             "snippet_type": "FRAMING",
    #             "text": settings.TRUNCATED_FRAMING,
    #             "is_initiate": True,
    #             "convo": new_convo
    #         },
    #         {
    #             "snippet_type": "ASSISTANT MESSAGE",
    #             "text": settings.GREETING,
    #             "is_initiate": True,
    #             "convo": new_convo
    #         }
    #     ]
    #     for snippet in data:
    #         Snippet.objects.create(**snippet)
    #     return new_convo
    #
    # def create(self, validated_data):
    #     is_initiate = validated_data["is_initiate"]
    #     if is_initiate:
    #         new_convo = self._create_default_snippet()
    #     return new_convo
