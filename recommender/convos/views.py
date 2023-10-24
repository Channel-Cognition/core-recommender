# Create your views here.
from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from suggestions.models import Convo
from suggestions.serializers import ConvoSerializer


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

    @action(['DELETE'], detail=False, url_name='delete-all')
    def delete_all_convo(self, request):
        user = request.user
        list_convo = Convo.objects.filter(user=user)
        list_convo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)