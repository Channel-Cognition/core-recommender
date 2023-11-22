import json
from chancog.entities import Conversation, Snippet as ChancogSnippet

from django.conf import settings
from chancog.sagenerate.processing import process_new_user_message
from .models import Convo, Snippet


def perform_search(query, convo_id):
    response = {"MESSAGE_STATUS": "SUCCESS",
                 "MESSAGE_DATA": ""}
    conversation = build_dict_convo(convo_id)
    oai_handler_base = settings.OAI_HANDLER_BASE
    oai_handler_azure = settings.OAI_HANDLER
    if conversation is None:
        response["MESSAGE_STATUS"] = "FAILED"
        response["MESSAGE_DATA"] = "Conversation is not found"
        return response
    is_succeed, conversation, llm_message, text, item_infos, new_match_bundle = process_new_user_message(
        conversation=conversation,
        user_message=query,
        oai_handler=oai_handler_azure,
        oai_model=settings.OAI_MODEL,
        cosmos_handler=settings.COSMOS_HANDLER,
        pc_handler=settings.PC_HANDLER,
        tvdb_handler=None,
        ol_handler=None,
    )
    if not is_succeed:
        response["MESSAGE_STATUS"] = "FAILED"
        response["MESSAGE_DATA"] = "Did not get response from Opean AI"
    print(llm_message.to_dict())
    response["MESSAGE_DATA"] = {"llm_response":json.loads(llm_message.to_dict()['text'])['text'],
                                "items":item_infos,
                                "match_bundle":new_match_bundle}
    return response


def build_dict_convo(convo_id):
    conversation = Conversation()
    try:
        obj_convo = Convo.objects.get(convo_id=convo_id)
        snippets = Snippet.objects.filter(convo=obj_convo)
        if snippets.exists():
            for snippet in snippets:
                conversation.append_snippet(ChancogSnippet(snippet.snippet_type, snippet.text))
    except:
        conversation = None
    return conversation


def matching_result(new_match_bundle):
    match_bundle = new_match_bundle
    item_matches = new_match_bundle.item_matches



