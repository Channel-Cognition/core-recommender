from chancog.entities import Conversation, Snippet as ChancogSnippet
from chancog.sagenerate.processing import process_new_user_message

from django.conf import settings

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
    is_succeed, conversation, item_infos, llm_message = process_new_user_message(
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
    response["MESSAGE_DATA"] = {"llm_response":llm_message,
                                "items":item_infos}
    # print(is_succeed)
    # print(conversation)
    # print(item_infos)
    # print(llm_message)
    print(response)
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


