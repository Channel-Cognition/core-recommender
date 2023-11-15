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
from chancog.sagenerate.azfunc import rag_matcher
from chancog.sagenerate.processing import process_new_user_message

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

# TODO: support entering and loading a conversation from a json file using a command line input
#conversation = Conversation()
#snippets = []
#conversation.append_snippet(Snippet('framing', framing))
#conversation.append_snippet(Snippet('greeting', greeting))

# We use snippet_index to remember which snippets we've shown in the terminal frontend
# In particular, it is the index in conversation.snippets of the next snippet we
# need to show.
#snippet_index = 0

def main():
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

        success, conversation, item_infos, text = process_new_user_message(conversation,
                                                                           user_message,
                                                                           cosmos_handler,
                                                                           oai_handler_azure,
                                                                           smart_model_azure,
                                                                           pc_handler,
                                                                           tvdb_handler,
                                                                           ol_handler)
                  
            

        print('Assistant:' + text + '\n')
        print('----')
        for display_info in item_infos:
            pprint(display_info)

if __name__ == "__main__":
    main()
#        conversation.append_snippet(Snippet('user_message', user_message))
#        #snippet_index += 1
#
#        #llm_message = lorem.sentence()
#        messages = conversation.build_open_ai_messages()
#        llm_message, _ = oai_handler_base.call_gpt(messages,
#                                                   model=dumb_model_base,
#                                                   json_mode=True)
#        try:
#            parsed_json = json.loads(llm_message)
#        except json.JSONDecodeError as e:
#            print("JSON decoding failed:", e)
#        except Exception as e:
#            raise(e)
#        print('Assistant: ' + parsed_json['text'] + '\n')
#        conversation.append_snippet(Snippet('llm_message', llm_message))
#        #snippet_index += 1
#
#        # Loop over entries in new_items to do a Pinecone vector search
#        for suggestion in parsed_json['new_items']:
#            print('******************')
#            'LLM suggestion:'
#            pprint(suggestion)
#            item_info, diagnostics = rag_matcher(suggestion,
#                                                 oai_handler_base,
#                                                 oai_handler_azure,
#                                                 pc_handler,
#                                                 cosmos_handler.containers['items'],
#                                                 num_matches=3)
#            'Our match:'
#            pprint(item_info)
#            print('******************')
#    input_tokens, output_tokens = count_diagnostics_tokens(diagnostics)
#    cost = calc_gpt_cost(input_tokens, output_tokens, dumb_model_base)
#    print('Final cost:')
#    print(cost)

       
