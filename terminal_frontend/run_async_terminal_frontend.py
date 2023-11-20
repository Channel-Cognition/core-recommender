import asyncio
from chancog.sagenerate.items import build_display_item_info
from chancog.llm import OpenAIHandler
from chancog.cosmos import CosmosHandler
from chancog.sagenerate.azfunc import smart_match_and_add
from chancog.sagenerate.tvdb import TVDBHandler
from chancog.sagenerate.openlibrary import OpenLibraryHandler
from chancog.llm import PineconeManager
from decouple import config
from local_llm import calc_gpt_cost, count_diagnostics_tokens
from chancog.entities import Conversation, Snippet
import json
from pprint import pprint
from chancog.sagenerate.processing import process_new_user_message_async

model_deployments = {
    'gpt-3.5-turbo': 'gpt-35-turbo-caeast', # Azure sometimes uses gpt-35-turbo
    'gpt-4': 'gpt-4-default-caeast',
    'gpt-4-32k': 'gpt-4-32k-default-caeast',
    'text-embedding-ada-002': 'text-embedding-ada-002-caeast'
}
        
dumb_model_azure = 'gpt-3.5-turbo'
smart_model_azure = 'gpt-4'
oai_handler_azure = OpenAIHandler(
    config("AZURE_OPENAI_KEY"),
    azure_endpoint=config("AZURE_OPENAI_ENDPOINT"),
    model_deployments=model_deployments
)

# These
dumb_model_base = 'gpt-3.5-turbo-1106'
smart_model_base = 'gpt-4-1106-preview'

oai_handler_base = OpenAIHandler(config("OPENAI_API_KEY"))

# Pinecone Configuration
pc_handler = PineconeManager(
    config('PINECONE_ITEMS_INDEX_NAME'),
    config('PINECONE_API_KEY'),
    config('PINECONE_API_ENV')
)

cosmos_handler = CosmosHandler(config('COSMOS_KEY'),
                               config('COSMOS_URL'),
                               config('COSMOS_DB_NAME'),
                               container_names=['items'])


# TVDB Handler Initialization
tvdb_handler = TVDBHandler(config("TVDB_KEY"))

# Open Library Handler
ol_handler = OpenLibraryHandler()

framing = "You are an assistant helping the user find new things, which could "
framing += "be anything from a new movie or TV show to watch to a pair of shoes to buy. "
framing += "With every response, please (1) provide an updated list of suggestions and "
framing += "(2) include the item type (e.g., book) with each item in the list. "
framing += "Be as succinct as is reasonable while still uniquely identifying items. "
framing += "Do not include items the user is no longer interested in."
framing += "Return a JSON with two base fields: text, which, will be shown to the user, and new_items, "
framing += "which is a list of newly suggested items. Each item in new_items must contain an item_type field "
framing += "(e.g., book) and should contain additional fields to uniquely specify the item "
framing += "(e.g., title and author for a book)."


greeting = "Hello, what can I suggest for you today?"

# Example callback function
async def process_callback(action, data_tuple):
    print('****callback action: ' + action + '****')
    if action == 'add_llm_text':
        text = data_tuple
        print('Assistant: ' + text + '\n')
    elif action == 'add_prelim_suggestion':
        cosmos_item_info, display_item_info, metric, diagnostics = data_tuple
        pprint(display_item_info)
    elif action == 'add_final_suggestion':
        display_item_info, diagnostics = data_tuple
        pprint(display_item_info)
    else:
        raise ValueError(f'Unrecognized action = {action}')
    print('********')

async def main():
    conversation = Conversation()
    conversation.append_snippet(Snippet('framing', framing))
    conversation.append_snippet(Snippet('greeting', greeting))

    # We don't show the framing snippet, but do show the greeting snippet
    print('Assistant: ' + greeting + '\n')
    #snippet_index = 2
    while True:
        user_message = input("You: ")
        # The new use snippet is already shown, so increment snippet_index
        #snippet_index += 1
        if user_message.lower() == "exit":
            print("Exiting the chat bot...")
            break

        print('Calling process_new_user_message_async')
        success, conversation, text, diagnostics = await process_new_user_message_async(conversation,
                                                                                        user_message,
                                                                                        process_callback,
                                                                                        cosmos_handler,
                                                                                        oai_handler_azure,
                                                                                        smart_model_azure,
                                                                                        pc_handler,
                                                                                        tvdb_handler,
                                                                                        ol_handler)

if __name__ == "__main__":
    asyncio.run(main())