# Create your views here.
from dateutil.parser import parse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes)
from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from suggestions.models import Convo, Snippet
from suggestions.serializers import ConvoSerializer


@extend_schema_view(
    refresh=extend_schema(
        parameters=[
            OpenApiParameter(
                'last_created',
                OpenApiTypes.STR,
                description='LastCreatedSnippet'
            ),
        ]
    )
)
class ConvoViewSet(mixins.DestroyModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = ConvoSerializer
    queryset = Convo.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    lookup_field = "convo_id"

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        return queryset.filter(
            user=user
        ).order_by('-created_date').distinct()

    @action(['DELETE'], detail=False, url_name='delete-all')
    def delete_all_convo(self, request):
        user = request.user
        list_convo = Convo.objects.filter(user=user)
        list_convo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        instance = get_object_or_404(Convo, convo_id=kwargs.get("convo_id"))
        instance.user = request.user
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['get'],
            lookup_field="convo_id")
    def refresh(self, request, convo_id=None):
        obj_convo = self.get_object()
        snippet = Snippet.objects.filter(convo=obj_convo).latest('created_date')
        serializer = self.get_serializer(obj_convo)
        last_updated_str = request.GET.get('last_created', '')
        last_updated = parse(last_updated_str) if last_updated_str else None

        if last_updated and snippet.created_date > last_updated:
            # New data is available
            serializer = self.get_serializer(obj_convo)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # No new data
            return Response(serializer.data, status=status.HTTP_304_NOT_MODIFIED)