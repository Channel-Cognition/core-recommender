from chancog.llm import OAIAzureServiceHandler
from decouple import config
from local_llm import calc_gpt_cost, count_diagnostics_tokens
from local_llm import OpenAIHandler
from chancog.entities import Conversation, Snippet
import lorem

model_deployments = {
    'gpt-3.5-turbo': 'gpt-35-turbo-caeast', # Azure sometimes uses gpt-35-turbo
    'gpt-4': 'gpt-4-default-caeast',
    'gpt-4-32k': 'gpt-4-32k-default-caeast',
    'text-embedding-ada-002': 'text-embedding-ada-002-caeast'
}
        
dumb_model_azure = 'gpt-3.5-turbo'
smart_model_azure = 'gpt-4'
oai_handler_azure = OAIAzureServiceHandler(
    azure_openai_key=config("AZURE_OPENAI_KEY"),
    azure_openai_endpoint=config("AZURE_OPENAI_ENDPOINT"),
    model_deployments=model_deployments
)

# These
dumb_model_base = 'gpt-3.5-turbo-1106'
smart_model_azure = 'gpt-4-1106-preview'

oai_handler_base = OpenAIHandler(config("OPENAI_API_KEY"))

framing = "You are an assistant helping the user find new things, which could "
framing += "be anything from a new movie or TV show to watch to a pair of shoes to buy. "
framing += "With every response, please (1) provide an updated numbered list of suggestions and "
framing += "(2) include the item type (e.g., book) with each item in the list. "
framing += "Be as succinct as is reasonable while still uniquely identifying items. "
framing += "Do not include items the user is no longer interested in."
framing += "Return a JSON with two base fields: text, which, will be shown to the user, and new_items, "
framing += "which is a list of newly suggested items. Each item in new_items must contain an item_type field "
framing += "(e.g., book) and should contain additional fields to uniquely specify the item "
framing += "(e.g., title and author for a book)."


greeting = "Hello, what can I suggest for you today?"

# TODO: support entering and loading a conversation from a json file using a command line input
conversation = Conversation()
snippets = []
conversation.add_snippet(Snippet('framing', framing))
conversation.add_snippet(Snippet('greeting', greeting))

# We use snippet_index to remember which snippets we've shown in the terminal frontend
# In particular, it is the index in conversation.snippets of the next snippet we
# need to show.
#snippet_index = 0

def main():
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
        conversation.add_snippet(Snippet('user_message', user_message))
        #snippet_index += 1

        llm_message = lorem.sentence()
        print('Assistant: ' + llm_message + '\n')
        conversation.add_snippet(Snippet('llm_message', llm_message))
        #snippet_index += 1

if __name__ == "__main__":
    main()