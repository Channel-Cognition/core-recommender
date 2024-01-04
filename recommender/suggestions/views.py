import time

from chancog.sagenerate.processing import get_dummy_suggestions
from django.conf import settings
# Create your views here.
from rest_framework.views import APIView

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes)

from .models import Convo, Snippet, MatchBundle, ItemMatch
from .serializers import ConvoSerializer
from .tasks import process_new_user_message

from utils.resizing_image import get_or_create_image_cache


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                'q',
                OpenApiTypes.STR,
                description='Query Suggestion'
            ),
            OpenApiParameter(
                'is_initiate',
                OpenApiTypes.BOOL,
                description='Is initiate convo?'
            ),
            OpenApiParameter(
                'convo_id',
                OpenApiTypes.STR,
                description='convo ID'
            )
        ]
    )
)
class SearchListView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _create_default_snippet(self):
        new_convo = Convo.objects.create(
            user=self.request.user
        )
        data = [
            {
                "snippet_type": "FRAMING",
                "text": settings.TRUNCATED_FRAMING,
                "is_initiate": True,
                "convo": new_convo
            },
            {
                "snippet_type": "ASSISTANT MESSAGE",
                "text": settings.GREETING,
                "is_initiate": True,
                "convo": new_convo
            }
        ]
        for snippet in data:
            Snippet.objects.create(**snippet)
        return new_convo

    def get(self, request, *args, **kwargs):
        user = self.request.user
        query = request.GET.get('q', None)
        convo_id = request.GET.get('convo_id', None)
        if convo_id is None:
            new_convo = self._create_default_snippet()
            serializer = ConvoSerializer(new_convo)
            return Response(serializer.data, status=200)
        convo_existing = Convo.objects.filter(user=user, convo_id=convo_id).latest("created_date")
        query_snippet = {"snippet_type": "USER MESSAGE", "text": query, "convo": convo_existing}
        Snippet.objects.create(**query_snippet)
        result = process_new_user_message.apply_async(args=(convo_id, ))
        serializer = ConvoSerializer(convo_existing)
        return Response(serializer.data, status=200)


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                'q',
                OpenApiTypes.STR,
                description='Query Suggestion'
            ),
            OpenApiParameter(
                'is_initiate',
                OpenApiTypes.BOOL,
                description='Is initiate convo?'
            ),
            OpenApiParameter(
                'convo_id',
                OpenApiTypes.STR,
                description='convo ID'
            )
        ]
    )
)
class FreeSearchListView(APIView):

    def _bulk_create_snippets(self, snippets):
        for snippet in snippets:
            Snippet.objects.create(**snippet)
        return None

    def _create_default_snippet(self):
        new_convo = Convo.objects.create(
        )
        data = [
            {
                "snippet_type": "FRAMING",
                "text": settings.TRUNCATED_FRAMING,
                "is_initiate": True,
                "convo": new_convo
            },
            {
                "snippet_type": "ASSISTANT MESSAGE",
                "text": settings.GREETING,
                "is_initiate": True,
                "convo": new_convo
            }
        ]
        for snippet in data:
            Snippet.objects.create(**snippet)
        return new_convo

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', None)
        convo_id = request.GET.get('convo_id', None)
        if convo_id is None:
            new_convo = self._create_default_snippet()
            serializer = ConvoSerializer(new_convo)
            return Response(serializer.data, status=200)
        convo_existing = Convo.objects.filter(convo_id=convo_id).latest("created_date")
        snippets = [{"snippet_type": "USER MESSAGE", "text": query, "convo": convo_existing
        }]
        import time
        start = time.time()
        results = perform_search(query, str(convo_existing.convo_id))
        if results["MESSAGE_STATUS"] == "FAILED":
            print(results["MESSAGE_DATA"])
            snippets.append({"snippet_type": "LLM MESSAGE", "text": "Sorry we cant find you're searching",
                             "convo": convo_existing, "pydantic_text": None})
            self._bulk_create_snippets(snippets)
            serializer = ConvoSerializer(convo_existing)
            return Response(serializer.data, status=200)
        end = time.time()
        print("perform_search", end-start)
        llm_response = results["MESSAGE_DATA"]["llm_response"]
        items = results["MESSAGE_DATA"]["items"]
        if items:
            for item in items:
                image = get_or_create_image_cache(item["thumbnail_url"])
                item.update({"image":{"image_b64_medium": image["image_b64_medium"]}})
        snippets.append({"snippet_type": "LLM MESSAGE", "text": llm_response, "convo": convo_existing,
                         "pydantic_text": items})

        self._bulk_create_snippets(snippets)
        serializer = ConvoSerializer(convo_existing)
        return Response(serializer.data, status=200)


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                'q',
                OpenApiTypes.STR,
                description='Query Suggestion'
            ),
            OpenApiParameter(
                'is_initiate',
                OpenApiTypes.BOOL,
                description='Is initiate convo?'
            ),
            OpenApiParameter(
                'convo_id',
                OpenApiTypes.STR,
                description='convo ID'
            )
        ]
    )
)
class DummyListView(SearchListView):

    def get(self, request, *args, **kwargs):
        user = self.request.user
        query = request.GET.get('q', None)
        convo_id = request.GET.get('convo_id', None)
        if convo_id is None:
            new_convo = self._create_default_snippet()
            serializer = ConvoSerializer(new_convo)
            return Response(serializer.data, status=200)
        convo_existing = Convo.objects.filter(user=user, convo_id=convo_id).latest("created_date")
        snippets = [{"snippet_type": "USER MESSAGE", "text": query, "convo": convo_existing
        }]
        items, llm_response, sampled_item_ids = get_dummy_suggestions()
        if items:
            for item in items:
                if item is not None:
                    image = get_or_create_image_cache(item["thumbnail_url"])
                    item.update({"image":{"image_b64_medium": image["image_b64_medium"]}})
        snippets.append({"snippet_type": "LLM MESSAGE", "text": llm_response, "convo": convo_existing,
                         "pydantic_text": items})

        self._bulk_create_snippets(snippets)
        serializer = ConvoSerializer(convo_existing)
        return Response(serializer.data, status=200)