from django.conf import settings
from chancog.sagenerate.cosmos import CosmosHandler
from chancog.sagenerate.endpoints import process_new_user_message
from chancog.llm import OAIAzureServiceHandler
from chancog.sagenerate.tvdb import TVDBHandler
from chancog.sagenerate.openlibrary import OpenLibraryHandler
from chancog.llm import PineconeManager
from decouple import config
from pprint import pprint

def run_sandbox():
    fast_dev = False

    # Cosmos configuration and instantiation
    CosmosURL = settings.CosmosURL
    CosmosKey = settings.CosmosKey
    DATABASE_NAME = 'ConversationsDB'
    cosmos_handler = CosmosHandler(CosmosKey, CosmosURL, DATABASE_NAME)

    model_deployments = {
        'gpt-3.5-turbo': 'gpt-35-turbo-caeast',  # Azure sometimes uses gpt-35-turbo
        'gpt-4': 'gpt-4-default-caeast',
        'text-embedding-ada-002': 'text-embedding-ada-002-caeast'
    }

    oai_handler = OAIAzureServiceHandler(
        AzureOpenAIKey=settings.AzureOpenAIKey,
        AzureOpenAIEndpoint=settings.AzureOpenAIEndpoint,
        model_deployments=model_deployments
    )

    # Pinecone Configuration
    pc_handler = PineconeManager(
        'sa-items2',
        settings.PineconeAPIKey,
        settings.PineconeEnv
    )

    # TVDB Handler Initialization
    tvdb_handler = TVDBHandler(config("TVDBKey"))

    # Open Library Handler
    ol_handler = OpenLibraryHandler()

    framing = "You are an assistant helping the user find new things, which could "
    framing += "be anything from a new movie or TV show to watch to a pair of shoes to buy. "
    framing += "With every response, please (1) provide an updated numbered list of suggestions and "
    framing += "(2) include the item type (e.g., book) with each item in the list. "
    framing += "Be as succinct as is reasonable while still uniquely identifying items. "
    framing += "Do not include items the user is no longer interested in."

    greeting = "Hello, what are you looking for today?"
    user_message1 = 'I am looking for a new sci movie or book, preferably hard sci fi.'

    if fast_dev:
        num_tries = 10
    else:
        num_tries = 10
    for _ in range(num_tries):
        print('-------------------')
        outcome1 = process_new_user_message(None,
                                            user_message1,
                                            cosmos_handler,
                                            oai_handler,
                                            pc_handler,
                                            tvdb_handler,
                                            ol_handler,
                                            framing=framing,
                                            greeting=greeting,
                                            fast_dev=fast_dev)
        print(outcome1['user_message'])
        print(outcome1['llm_response'])
        items1 = [item_info['title'] if item_info else None for item_info in outcome1['items']]
        print(items1)

        convo_id = outcome1['convo_id']
        user_message2 = 'Let\'s focus on just books for now.'
        outcome2 = process_new_user_message(convo_id,
                                            user_message2,
                                            cosmos_handler,
                                            oai_handler,
                                            pc_handler,
                                            tvdb_handler,
                                            ol_handler,
                                            fast_dev=fast_dev)
        print(outcome2['user_message'])
        print(outcome2['llm_response'])
        items2 = [item_info['title'] if item_info else None for item_info in outcome2['items']]
        print(items2)

        if fast_dev:
            for item in items1:
                if item in items2:
                    raise Exception(f'{item} is in items2')
    return True