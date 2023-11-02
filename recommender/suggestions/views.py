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
    OpenApiTypes
)
from .client import perform_search
from .models import Convo, Snippet
from .serializers import ConvoSerializer

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
        query = request.GET.get('q')
        is_initiate = request.GET.get('is_initiate', False)
        convo_id = request.GET.get('convo_id', None)
        if convo_id is None:
            new_convo = self._create_default_snippet()
            serializer = ConvoSerializer(new_convo)
            return Response(serializer.data, status=200)
        convo_existing = Convo.objects.filter(user=user, convo_id=convo_id).latest("created_date")
        snippets = [{
            "snippet_type": "USER MESSAGE",
            "text": query,
            "convo": convo_existing
        }]
        import time
        start = time.time()
        results = perform_search(query, str(convo_existing.convo_id))
        end = time.time()
        print("perform_search", end-start)
        llm_response = results.get("llm_response", None)
        items = results.get("items", None)
        if items:
            for item in items:
                image = get_or_create_image_cache(item["thumbnail_url"])
                item.update({"image": image})
        snippets.append({
                "snippet_type": "LLM MESSAGE",
                "text": llm_response,
                "convo": convo_existing,
                "pydantic_text": results.get("items", None)
            })
        for snippet in snippets:
            Snippet.objects.create(**snippet)
        serializer = ConvoSerializer(convo_existing)
        return Response(serializer.data, status=200)

#TODO will be deprecated if everything is fine!

# class SearchListView(APIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)
#
#     def _create_default_snippet(self):
#         new_convo = Convo.objects.create(
#             user=self.request.user
#         )
#         data = [
#             {
#                 "snippet_type": "FRAMING",
#                 "text": settings.TRUNCATED_FRAMING,
#                 "is_initiate": True,
#                 "convo": new_convo
#             },
#             {
#                 "snippet_type": "ASSISTANT MESSAGE",
#                 "text": settings.GREETING,
#                 "is_initiate": True,
#                 "convo": new_convo
#             }
#         ]
#         for snippet in data:
#             Snippet.objects.create(**snippet)
#         return new_convo
#
#     def get(self, request, *args, **kwargs):
#         user = self.request.user
#         query = request.GET.get('q')
#         is_initiate = request.GET.get('is_initiate', False)
#         convo_id = request.GET.get('convo_id', "")
#         if not query:
#             if is_initiate == "true":
#                 new_convo = self._create_default_snippet()
#                 serializer = ConvoSerializer(new_convo)
#                 return Response(serializer.data, status=200)
#         if convo_id:
#             convo_existing = Convo.objects.filter(user=user, convo_id=convo_id).latest("created_date")
#             convo = perform_search(query, convo_existing)
#             serializer = ConvoSerializer(convo)
#             return Response(serializer.data)
#         convo_existing = Convo.objects.filter(user=user).latest("created_date")
#         convo = perform_search(query, convo_existing)
#         serializer = ConvoSerializer(convo)
#         return Response(serializer.data)
#
# # Integrated With Cosmos DB
# class SearchListV2View(APIView):
#     # authentication_classes = (TokenAuthentication,)
#     # permission_classes = (IsAuthenticated,)
#
#     def _create_default_snippet(self):
#         data = [
#         ]
#         convo_id = str(uuid.uuid4())
#         is_created = ConvoCosmosDB(convo_id=convo_id).create()
#         if is_created:
#             data = [
#                 Snippet("FRAMING", settings.TRUNCATED_FRAMING, datetime.now()),
#                 Snippet("ASSISTANT MESSAGE", settings.GREETING, datetime.now() )
#             ]
#         is_created = ConvoCosmosDB(convo_id=convo_id).create_snippets(data)
#         return convo_id
#
#     def get(self, request, *args, **kwargs):
#         user = self.request.user
#         query = request.GET.get('q')
#         is_initiate = request.GET.get('is_initiate', False)
#         convo_id = request.GET.get('convo_id', None)
#         if convo_id is None:
#             new_convo_id = self._create_default_snippet()
#             get_convo = ConvoCosmosDB(convo_id=new_convo_id).get()
#             convo_dict = get_convo.to_dict()
#             convo_dict["convo_id"] = new_convo_id
#             return Response(convo_dict, status=200)
#         is_snippet_created = ConvoCosmosDB(convo_id=convo_id).create_snippets([Snippet(
#             snippet_type="USER MESSAGE",
#             text=query, timestamp= datetime.now())])
#         if is_snippet_created:
#             results = perform_search_v2(query, convo_id)
#             ConvoCosmosDB(convo_id=convo_id).create_snippets([Snippet("LLM MESSAGE", results)])
#             get_convo = ConvoCosmosDB(convo_id=convo_id).get()
#             return Response(get_convo.to_dict(), status=200)