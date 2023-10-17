# Create your views here.
from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from suggestions.models import Convo
from suggestions.serializers import ConvoSerializer

# Create your views here.


class ConvoViewSet(mixins.DestroyModelMixin,
                mixins.RetrieveModelMixin,
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