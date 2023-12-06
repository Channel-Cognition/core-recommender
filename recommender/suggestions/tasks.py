import random
import sys
from celery import chord

from celery import shared_task
from chancog.sagenerate.azfunc import rag_matcher
from chancog.sagenerate.processing import process_new_user_message
from chancog.parsing import parse_json_string

from suggestions.models import Snippet, Convo
from utils.resizing_image import get_or_create_image_cache



from django.conf import settings


@shared_task
def async_process_new_user_message(
        conversation,
        user_message,
        oai_handler,
        oai_model,
        cosmos_handler,
        pc_handler):
    is_succeed, conversation, llm_message, text, item_infos, new_match_bundle = process_new_user_message(
        conversation=conversation,
        user_message=user_message,
        oai_handler=oai_handler,
        oai_model=oai_model,
        cosmos_handler=cosmos_handler,
        pc_handler=pc_handler)
    return is_succeed, conversation, llm_message, text, item_infos, new_match_bundle


@shared_task
def call_gpt(messages):
    oai_handler = settings.OAI_HANDLER
    oai_model = settings.OAI_MODEL
    llm_message, call_diagnostics = oai_handler.call_gpt(messages,
                                                         model=oai_model,
                                                         json_mode=True)
    result = {"llm_message":llm_message,
              "call_diagnostics":call_diagnostics}
    return result


@shared_task
def task_rag_matcher(item):
    oai_handler = settings.OAI_HANDLER
    oai_model = settings.OAI_MODEL
    pc_handler = settings.PC_HANDLER
    cosmos_handler = settings.COSMOS_HANDLER
    item_info, cosmos_item_info, call_diagnostics = rag_matcher(item,
                                                                oai_handler,
                                                                oai_model,
                                                                pc_handler,
                                                                cosmos_handler.containers['items'],
                                                                num_matches=10)
    result = {
        "item_info": item_info,
        "cosmos_item_info": cosmos_item_info,
        "call_diagnostics": call_diagnostics
    }
    return result


@shared_task
def list_result_rag_matcher(results, convo_id, text):
    item_infos = []
    cosmos_item_infos = []
    obj_convo = Convo.objects.get(convo_id=convo_id)

    list_result = [result for result in results]
    for result in list_result:
        item_info = result.get("item_info", None)
        cosmos_item_info = result.get('cosmos_item_info', None)
        if item_info and cosmos_item_info:
            item_infos.append(item_info)
            cosmos_item_infos.append(cosmos_item_info)

        print("-------------ITEM INFO--------")
        print(item_info)
        print("-----------COSMOS_ITEM_INFO------------------")
        print(cosmos_item_info)
    print("-------------ITEM INFOS------------------")
    print(item_infos)
    print("-------------COSMOS ITEM INFOS------------------")
    print(cosmos_item_infos)
    for item in item_infos:
        if item is not None:
            image = get_or_create_image_cache(item["thumbnail_url"])
            item.update({"image": {"image_b64_medium": image["image_b64_medium"]}})
    snippet_data = {"snippet_type": "LLM MESSAGE", "text": text, "convo": obj_convo,
                    "pydantic_text": item_infos}
    Snippet.objects.create(**snippet_data)
    return item_infos


@shared_task
def error_handler(task_id, exc, traceback):
    sys.stdout.write(">>>>")
    sys.stdout.write(str(exc))
    sys.stdout.write(">>>>")
    sys.stdout.flush()


@shared_task
def call_gpt_result(task_result):
    llm_message = task_result.get("llm_message")

    print("---------------LLM_MESSAGE---------------")
    print(llm_message)

    # Gracefully parse llm_message, which should be a json string (error_on_failure is the
    # default, but set it explicitly for maximum clarity)
    llm_message_dict = parse_json_string(llm_message,
                                         error_on_failure=False)
    text = llm_message_dict.get('text')  # can be None
    print("-----------TEXT_-----------")
    print(text)
    print("----------new_items-----------------")
    new_items = []
    if isinstance(llm_message, list):
        new_items = llm_message
    new_items = llm_message_dict.get('new_items', None)  # can be None
    if new_items is None:
        new_items = llm_message_dict.get('suggestions', None)
        if new_items:
            if isinstance(new_items, dict):
                new_items.append(new_items)
        new_items = llm_message_dict.get("movie_suggestions")

    print(new_items)
    callback = list_result_rag_matcher.s()
    header = [task_rag_matcher.s(item) for item in new_items]
    result_rag_mathcer = chord(header)(callback)
    return True, text, llm_message


@shared_task()
def run_task(messages):
    call_gpt.apply_async(args=[messages], link=[call_gpt_result.s(),], link_error=[error_handler.s(),])


@shared_task
def process_new_user_message(conversation_id):
    """
    Processes a new user message for a Suggest Anything conversation

    Args:
        conversation (MatchConversation): An object of class chancog.entities.MatchConversation
        user_message (str): The new user message
        cosmos_handler (object): Handler for CosmosDB interactions
        oai_handler (object): Handler for the Open AI API
        oai_model (str): The chat completion model to use. Must support JSON mode.
        pc_handler (object): Handler for Pinecone API interactions
        tvdb_handler (object): Handler for TVDB API interactions
        ol_handler (object): Handler for Open Library API interactions

    Returns:
        A tuple consisting of (success, conversation), where success indicates whether the processing
        was successful and conversation is the (likely) updated conversation
    """
    snippet_type_to_role = {Snippet.FRAMING: 'assistant',
                            Snippet.ASSISTANT_MESSAGE: 'assistant',
                            Snippet.USER_MESSAGE: 'user',
                            Snippet.LLM_MESSAGE: 'assistant'}

    obj_conversion = Convo.objects.get(convo_id=conversation_id)
    snippets = Snippet.objects.filter(convo=obj_conversion)
    messages = []
    for snippet in snippets:
        messages.append({
           'role': snippet_type_to_role.get(snippet.snippet_type),
            'content': snippet.text
        })
    oai_handler = settings.OAI_HANDLER
    oai_model = settings.OAI_MODEL
    llm_message, call_diagnostics = oai_handler.call_gpt(messages,
                                                         model=oai_model,
                                                         json_mode=True)
    # is_succeed, text, item_infos, cosmos_item_infos = run_task.apply_async(args=[messages])
    # llm_message = task_result.get("llm_message")

    print("---------------LLM_MESSAGE---------------")
    print(llm_message)

    # Gracefully parse llm_message, which should be a json string (error_on_failure is the
    # default, but set it explicitly for maximum clarity)
    llm_message_dict = parse_json_string(llm_message,
                                         error_on_failure=False)
    text = llm_message_dict.get('text', "Here are the movie recommendations for you.")  # can be None
    print("-----------TEXT_-----------")
    print(text)
    print("----------new_items-----------------")
    new_items = []
    if isinstance(llm_message, list):
        new_items = llm_message
    new_items = llm_message_dict.get('new_items', None)  # can be None
    if new_items is None:
        new_items = llm_message_dict.get('suggestions', None)
        if new_items:
            if isinstance(new_items, dict):
                new_items.append(new_items)
        new_items = llm_message_dict.get("movie_suggestions")

    print(new_items)
    callback = list_result_rag_matcher.s(convo_id=str(conversation_id), text=text)
    header = [task_rag_matcher.s(item) for item in new_items if item]
    result_rag_mathcer = chord(header)(callback)
    return llm_message
