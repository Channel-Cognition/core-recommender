from celery import chord
from chancog.diagnostics import start_diagnostics, add_diagnostic_info, end_diagnostics
from chancog.parsing import parse_json_string
from chancog.sagenerate import processing

from django.conf import settings

from suggestions.models import Convo, Snippet
from suggestions.tasks import run_task


# def process_new_user_message(conversation_id):
#     """
#     Processes a new user message for a Suggest Anything conversation
#
#     Args:
#         conversation (MatchConversation): An object of class chancog.entities.MatchConversation
#         user_message (str): The new user message
#         cosmos_handler (object): Handler for CosmosDB interactions
#         oai_handler (object): Handler for the Open AI API
#         oai_model (str): The chat completion model to use. Must support JSON mode.
#         pc_handler (object): Handler for Pinecone API interactions
#         tvdb_handler (object): Handler for TVDB API interactions
#         ol_handler (object): Handler for Open Library API interactions
#
#     Returns:
#         A tuple consisting of (success, conversation), where success indicates whether the processing
#         was successful and conversation is the (likely) updated conversation
#     """
#     snippet_type_to_role = {Snippet.FRAMING: 'assistant',
#                             Snippet.ASSISTANT_MESSAGE: 'assistant',
#                             Snippet.USER_MESSAGE: 'user',
#                             Snippet.LLM_MESSAGE: 'assistant'}
#
#     diagnostics = start_diagnostics('process_new_user_message')
#     obj_conversion = Convo.objects.get(convo_id=conversation_id)
#     snippets = Snippet.objects.filter(convo=obj_conversion)
#     messages = []
#     for snippet in snippets:
#         messages.append({
#            'role': snippet_type_to_role.get(snippet.snippet_type),
#             'content': snippet.text
#         })
#     result = call_gpt.apply_async(args=[messages])
#     task_result = result.get()
#     print("---------------TASK RESULT-------------------")
#     print(task_result)
#     llm_message = task_result.get("llm_message")
#     call_diagnostics = task_result.get("call_diagnostics")
#     # llm_message, call_diagnostics = oai_handler.call_gpt(messages,
#     #                                                      model=oai_model,
#     #                                                      json_mode=True)
#     print("---------------LLM_MESSAGE---------------")
#     print(llm_message)
#     diagnostics['children'].append(call_diagnostics)
#
#     # Gracefully parse llm_message, which should be a json string (error_on_failure is the
#     # default, but set it explicitly for maximum clarity)
#     llm_message_dict = parse_json_string(llm_message,
#                                          error_on_failure=False)
#     text = llm_message_dict.get('text')  # can be None
#     print("-----------TEXT_-----------")
#     print(text)
#     print("----------new_items-----------------")
#     new_items = []
#     if isinstance(llm_message, list):
#         new_items = llm_message
#     new_items = llm_message_dict.get('new_items', None)  # can be None
#     if new_items is None:
#         new_items = llm_message_dict.get('suggestions', None)
#         if new_items:
#             if isinstance(new_items, dict):
#                 new_items.append(new_items)
#         new_items = llm_message_dict.get("movie_suggestions")
#
#
#     print(new_items)
#     # Loop over new item suggestions to match them
#     item_infos = []  # a list to start display item info
#     cosmos_item_infos = []
#     callback = list_result_rag_matcher.s()
#     header = [task_rag_matcher.s(item) for item in new_items]
#     result_rag_mathcer = chord(header)(callback)
#     task_result_rag_matcher = result_rag_mathcer.get()
#
#     print("-------------TASK RESULT RAG MATCHER---------------")
#     print(task_result_rag_matcher)
#     for result in task_result_rag_matcher:
#         item_info = result.get("item_info", None)
#         cosmos_item_info = result.get('cosmos_item_info', None)
#         if item_info and cosmos_item_info:
#             item_infos.append(item_info)
#             cosmos_item_infos.append(cosmos_item_info)
#
#         print("-------------ITEM INFO--------")
#         print(item_info)
#         print("-----------COSMOS_ITEM_INFO------------------")
#         print(cosmos_item_info)
#         diagnostics['children'].append(call_diagnostics)
#     end_diagnostics(diagnostics)
#     return True, text, item_infos, cosmos_item_infos


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

    diagnostics = start_diagnostics('process_new_user_message')
    obj_conversion = Convo.objects.get(convo_id=conversation_id)
    snippets = Snippet.objects.filter(convo=obj_conversion)
    messages = []
    for snippet in snippets:
        messages.append({
           'role': snippet_type_to_role.get(snippet.snippet_type),
            'content': snippet.text
        })
    is_succeed, text, item_infos, cosmos_item_infos = run_task.apply_async(args=[messages])
    return True, is_succeed, item_infos, cosmos_item_infos
