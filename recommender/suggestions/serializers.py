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
        read_only_fields = 'convo_id',\


    def to_representation(self, instance):
        # Order snippets by created_date in descending order
        snippets_data = instance.snippet_set.order_by('created_date')

        # Serialize ordered snippets
        snippets_serializer = SnippetSerializer(snippets_data, many=True)

        # Add the ordered snippets to the representation
        representation = super(ConvoSerializer, self).to_representation(instance)
        representation['snippets'] = snippets_serializer.data

        return representation
