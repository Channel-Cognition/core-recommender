import traceback
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from celery import chord
from celery import shared_task
from chancog.sagenerate.azfunc import rag_matcher
from chancog.sagenerate.processing import process_new_user_message
from chancog.parsing import parse_json_string
from django.conf import settings

from movies.models import Movie, Genre
from suggestions.models import Snippet, Convo
from suggestions.pydantics import LLMResponseSchema
from utils.processings import convert_to_list_json, parse_movie_list, process_suggestion
from utils.resizing_image import get_or_create_image_cache
import json

@shared_task
def task_rag_matcher(item):
    result = {
        "item_info": None,
        "cosmos_item_info": None,
        "call_diagnostics": None,
    }
    oai_handler = settings.OAI_HANDLER
    oai_model = settings.OAI_MODEL
    pc_handler = settings.PC_HANDLER
    cosmos_handler = settings.COSMOS_HANDLER
    # get or create movie, if not created, call rag_matcher
    movie, created = Movie.objects.get_or_create(
        title=item["title"],
        year=item["year"]
    )
    if created:
        item_info, cosmos_item_info, call_diagnostics = rag_matcher(item,
                                                                    oai_handler,
                                                                    oai_model,
                                                                    pc_handler,
                                                                    cosmos_handler.containers['items'],
                                                                    num_matches=10)
        movie.item_info = item_info
        movie.cosmos_item_info = cosmos_item_info
        movie.call_diagnostics = call_diagnostics
        movie.save()
    result["item_info"] = movie.item_info
    result["cosmos_item_info"] = movie.cosmos_item_info
    result["call_diagnostics"] = movie.call_diagnostics
    return result


@shared_task
def task_rag_matcher_v2(item):
    print("---------ITEM------------")
    print(item)
    result = {
        "item_info": None,
        "cosmos_item_info": None,
        "call_diagnostics": None,
    }
    oai_handler = settings.OAI_HANDLER
    oai_model = settings.OAI_MODEL
    pc_handler = settings.PC_HANDLER
    cosmos_handler = settings.COSMOS_HANDLER
#    movie, created = Movie.objects.get_or_create(
#        title=item["name"],
#        year=item["year"]
#    )
#    if created:
#        item_info, call_diagnostics = process_suggestion(item,
#                                                         oai_handler,
#                                                         oai_model,
#                                                         pc_handler,
#                                                         cosmos_handler)
#        movie.item_info = item_info
#        movie.call_diagnostics = call_diagnostics
#        movie.save()
 
    item_info, call_diagnostics = process_suggestion(item,
                                                     oai_handler,
                                                     oai_model,
                                                     pc_handler,
                                                     cosmos_handler)
    result["item_info"] = item_info
    return result

@shared_task
def list_result_rag_matcher(results, convo_id, text):
    print("----------RESULT----------------")
    print(results)
    item_infos = []
    obj_convo = Convo.objects.get(convo_id=convo_id)

    list_result = [result for result in results]
    for result in list_result:
        item_info = result.get("item_info", None)
        if item_info:
            item_infos.append(item_info)
    for item in item_infos:
        if item is not None:
            image = get_or_create_image_cache(item["thumbnail_url"])
            item.update({"image": {"image_b64_medium": image["image_b64_medium"]}})
    snippet_data = {"snippet_type": "LLM MESSAGE", "text": text, "convo": obj_convo, "pydantic_text": item_infos}
    Snippet.objects.create(**snippet_data)
    # Send Snippet_Data to FE from WebSocket
    # channel_layer = get_channel_layer()
    # async_to_sync(channel_layer.group_send)(
    #     f"convo_group_{convo_id}",  # Use a unique group name for each conversation
    #     {
    #         'type': 'send_data',
    #         'data': snippet_data,
    #     }
    # )
    return item_infos

@shared_task()
def handle_failed_task(convo_id, task_id, traceback_str):
    print(f"Task failed: task_id={task_id}, convo_id={convo_id}, exception={traceback_str}")
    print(traceback_str)
    obj_convo = Convo.objects.get(convo_id=convo_id)
    snippet_data = {"snippet_type": "LLM MESSAGE",
                    "text": "Something went wrong, please try again",
                    "convo": obj_convo,
                    "pydantic_text": ""}
    Snippet.objects.create(**snippet_data)
    # Send Snippet_Data to FE from WebSocket
    # channel_layer = get_channel_layer()
    # async_to_sync(channel_layer.group_send)(
    #     f"convo_group_{convo_id}",  # Use a unique group name for each conversation
    #     {
    #         'type': 'send_data',
    #         'data': snippet_data,
    #     }
    # )
    return "Handle Failed Success"


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
    try:
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
        import time
        start = time.time()
        llm_message, call_diagnostics = oai_handler.call_gpt(messages,
                                                             model=oai_model)
        end = time.time()
        print("-------RESULT TIME----------")
        print(end-start)
        print("---------------LLM_MESSAGE---------------")
        print(llm_message)
        llm_message_parse = parse_movie_list(llm_message)
        print("-----------LLM_MESSAGE_PARSE----------")
        print(llm_message_parse)
        if len(llm_message_parse) == 0:
            task_id = process_new_user_message.request.id
            traceback_str = llm_message
            handle_failed_task.apply_async(args=(conversation_id, task_id, traceback_str))
            return llm_message
        text = "Here is movie recommendation for you"
        print("-----------TEXT_-----------")
        print(text)
        new_items = llm_message_parse
        print(new_items)
        if new_items:
            callback = list_result_rag_matcher.s(convo_id=str(conversation_id), text=text)
            header = [task_rag_matcher.s(item) for item in new_items if item]
            result_rag_mathcer = chord(header)(callback)
        return llm_message
    except Exception as e:
        traceback_str = traceback.format_exc()
        task_id = process_new_user_message.request.id
        handle_failed_task.apply_async(args=(conversation_id, task_id, traceback_str))
        raise


@shared_task
def process_new_user_message_v2(conversation_id):
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
    try:
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
        #oai_handler = settings.OAI_HANDLER
        oai_model = settings.OAI_MODEL
        import time
        start = time.time()
        #llm_message, call_diagnostics = oai_handler.call_gpt(messages,
        #                                                     model=oai_model,
        #                                                     json_mode=True)
        azure_client = settings.AZURE_CLIENT
        response = azure_client.chat.completions.create(
            model='gpt-4-default-caeast',
            messages=messages,
            stream=True
        )
        print('****************')
        print(response)
        print('****************')

        chunk_texts = []
        # iterate through the stream of events
        for n, chunk in enumerate(response):
            print('-----')
            print(n)
            print('--')
            choice_delta = chunk.choices[0].delta
            print(choice_delta)
            chunk_text = choice_delta.content
            print('--')
            print(chunk_text)
            chunk_texts.append(chunk_text)  # save the message
        
        # Build llm_message, accounting for the fact that the content
        # of the last, stop chunk is None
        llm_message = ''.join([c for c in chunk_texts if c])

        # TODO: load chunks from database

        end = time.time()
        print("-------RESULT TIME----------")
        print(end-start)
        print("---------------LLM_MESSAGE---------------")
        print(llm_message)

        llm_dict = json.loads(llm_message)
        callback = list_result_rag_matcher.s(convo_id=str(conversation_id), text=llm_dict['text'])
        #header = []
        # TODO: use the new algorithm for matching here
        header = [task_rag_matcher_v2.s(item) for item in llm_dict['new_items'] if item]
        result_rag_matcher = chord(header)(callback)
        return llm_message
#        llm_message_parse = convert_to_list_json(llm_message)
#        print("-----------LLM_MESSAGE_PARSE----------")
#        print(llm_message_parse)
#        if len(llm_message_parse) == 0:
#            task_id = process_new_user_message_v2.request.id
#            traceback_str = llm_message
#            handle_failed_task.apply_async(args=(conversation_id, task_id, traceback_str))
#            return llm_message
#        text = "Here is movie recommendation for you"
#        print("-----------TEXT_-----------")
#        print(text)
#        new_items = llm_message_parse
#        print(new_items)
#        print("----------NEW_ITEMS-------------------")
#        print(new_items)
#        if new_items:
#            callback = list_result_rag_matcher.s(convo_id=str(conversation_id), text=text)
#            header = [task_rag_matcher_v2.s(item) for item in new_items if item]
#            result_rag_mathcer = chord(header)(callback)
#        return llm_message
    except Exception as e:
        traceback_str = traceback.format_exc()
        task_id = process_new_user_message_v2.request.id
        handle_failed_task.apply_async(args=(conversation_id, task_id, traceback_str))
        raise
