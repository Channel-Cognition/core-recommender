import json
from chancog.entities import Conversation, Snippet as ChancogSnippet

from django.conf import settings
from utils.processings import process_new_user_message

from .models import Convo, Snippet
from .tasks import process_new_user_message, error_handler


def perform_search(convo_id):
    response = {"MESSAGE_STATUS": "SUCCESS",
                 "MESSAGE_DATA": ""}
    result = process_new_user_message.apply_async(args=[convo_id], link_error=[error_handler.s(),])
    print(is_succeed)
    if not is_succeed:
        response["MESSAGE_STATUS"] = "FAILED"
        response["MESSAGE_DATA"] = "Did not get response from Opean AI"
    print(item_infos)
    response["MESSAGE_DATA"] = {"llm_response":text,
                                "items":item_infos,}
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



