from django.conf import settings
from .messaging import truncate_messages, count_gpt_message_tokens
import openai
from decouple import config
import json

def build_llm_call(new_snippets,
                   role_mapping,
                   convo_table=None,
                   convo_id=None,
                   required_snippets=None):
    # Build a llm call, adapting which model we use based on the number of
    # tokens. We also truncate if necessary. We call one of two GPT 3.5
    # turbo models, depending on the context length:
    #
    # 
    # (1) gpt-3.5-turbo        4097 tokens
    # (2) gpt-3.5-turbo-16k -- 16385 tokens
    #
    # When we get access to the Anthropic API, we can also use their 100k
    # context models
    #
    # We need a "fudge factor" on when we truncate for two reasones. First, the
    # what Open AI actually does for the chat completion endpoint is not public
    # information, so our estimates of the number of input tokens using tiktoken
    # are only rough estimates. Second, the sum of the input and output tokens must
    # be less than the context window. So, if we call 3.5 turbo with 4090 input tokens
    # the ouput tokens can be only 7 in length, which means we will almost certainly
    # not reach the stop token. For both these reasons, we should be aggressively
    # conservative in applying a "fudge factor" when we step up models and truncate.

    # First, up the full messsages object using both the new input snippets and, if
    # necessary, the conversation history.
    if convo_id is not None:
        # Then convo_table should not be None
        use_history = True
    else:
        use_history = False
    
    messages = []
    is_new = []
    if use_history:
        # Fetch the conversation history based on the convo_id.
        convo_history = convo_table.get_conversation_history(convo_id)
        for entry in convo_history:
            role = role_mapping[entry.snippet_type]
            content = entry.text
            messages.append({"role": role, "content": content})
            is_new.append(True)
       
    # Next, loop over each new snippet
    for snippet in new_snippets:
        role = role_mapping[snippet['snippet_type']]
        content = snippet['text']
        messages.append({"role": role, "content": content})
        is_new.append(False)
    
    # TODO: should we check whether the tokens in new_snippets already exceed the length
    #       we can use with gpt-3.5-turbo-16?
        
    num_tokens, num_tokens_list = count_gpt_message_tokens(messages, return_list=True)
    first_limit = 3000
    second_limit = 4000 # 14000
    if num_tokens < first_limit:
        # If the context length, including with the new snippets, is less than
        # 3000 then we use gpt-3.5-turbo with no truncation
        model = 'gpt-3.5-turbo'
        truncated = False
    elif num_tokens < second_limit:
        # Otherwise, if the context length, including with the new snippets, is less than
        # 14000 then we use gpt-3.5-turbo with no truncation
        model = 'gpt-3.5-turbo-16k'
        truncated = False
    else:
        # If the context length is 14000 or larger we truncate the oldest entries in
        # messages to keep it under 14000. If we are truncating, we must always include
        # the requried snippets at the front, so first we count those.
        model = 'gpt-3.5-turbo-16k'
        if required_snippets is not None:
            num_required_tokens = count_gpt_message_tokens(required_snippets)
        else:
            num_required_tokens = 0
        
        new_limit = second_limit - num_required_tokens
        if num_tokens > new_limit:
            messages = truncate_messages(messages,
                                         num_tokens_list,
                                         second_limit,
                                         required_snippets,
                                         role_mapping=None)
            truncated = True
        else:
            truncated = False
    print("BUILD LLLM CALL!!!!!", messages, truncated)
    return messages, model, truncated

def embed_text(text, api_key=None):
    """
    Get a vector embedding for the input text using Open AI's model.

    Args:
        text (str): The text to embed.
        api_key (str, optional): The OpenAI API key. If not provided, it will be loaded 
                                 from the environment using python-decouple. Defaults to None.

    Returns:
        tuple:
            list: The embedding as a Python list.
            str: The name of the model used to get the embedding.
            int: The number of tokens used in the prompt.
            
    Note:
        Currently, only OpenAI's text-embedding-ada-002 model is supported.
    """
    
    model = 'text-embedding-ada-002'
    if api_key is None:
        api_key = config('OPEN_AI_API_KEY')
    # Make the API call

    response = openai.Embedding.create(input=text,
                                       model=model,
                                       api_key=api_key)

    return response['data'][0]['embedding'], model, response['usage']['prompt_tokens']

def call_gpt3_5_turbo(messages,
                      model='gpt-3.5-turbo',
                      api_key=None):
    """
    Process a conversation with gpt-3.5-turbo.

    Args:
        messages (list): List of message dictionaries for the conversation.
        model (str, optional): The LLM model to use, default is 'gpt-3.5-turbo'.
        api_key (str, optional): The OpenAI API key. If not provided, it will be loaded 
                                  from the environment using python-decouple. Defaults to None.

    Returns:
        tuple: 
            - str: LLM's response.
            - str: Used LLM model.
            - int: Number of tokens used in the prompt.
            - int: Number of tokens used in the completion.
    """
    if api_key is None:
        # api_key = config('OPEN_AI_API_KEY')
        api_key = settings.OPEN_AI_KEY

    # Make the API call

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        api_key=api_key
    )
    """
    {
        "id": "chatcmpl-88ekEMzr4a8oUWg2fP5oIIN0eDE8v",
        "object": "chat.completion",
        "created": 1697073938,
        "model": "gpt-3.5-turbo-0613",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Of course, I'd be happy to suggest some family-friendly movies for your movie night! Here are a few options:\n\n1. \"Toy Story\" (1995)\n2. \"Finding Nemo\" (2003)\n3. \"The Incredibles\" (2004)\n4. \"Zootopia\" (2016)\n5. \"Moana\" (2016)\n6. \"Coco\" (2017)\n7. \"Spider-Man: Into the Spider-Verse\" (2018)\n8. \"Paddington 2\" (2017)\n9. \"The Lego Movie\" (2014)\n10. \"Frozen\" (2013)\n\nI hope you find these suggestions enjoyable for your family movie night! Let me know if you'd like more options or if there's anything else I can assist you with."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 98,
            "completion_tokens": 170,
            "total_tokens": 268
        }
    }
    """

    # Extract the model's response and return
    assistant_response = response['choices'][0]['message']['content']
    prompt_tokens = response['usage']['prompt_tokens']
    completion_tokens = response['usage']['completion_tokens']
    return assistant_response, model, prompt_tokens, completion_tokens

# TODO: explore using functions for text operations
#       https://platform.openai.com/docs/guides/gpt/function-calling
def have_list(text,
              model='gpt-3.5-turbo',
              report_tokens=False,
              api_key=None):
    """
    Determines whether the input text contains a list.

    Args:
        text (str): The string of text to assess.
        model (str, optional): The LLM model to use, defaulted to 'gpt-3.5-turbo'.
        report_tokens (bool, optional): A flag indicating whether to report the token usage,
                                         defaulted to False.
        api_key (str, optional): The OpenAI API key. If not provided, it will be loaded from
                                  the environment using python-decouple, defaulted to None.

    Returns:
        bool or tuple: 
            - If report_tokens is False, returns True if a list is found, False if not, 
              and None if the response is unrecognized.
            - If report_tokens is True, returns a tuple containing the aforementioned boolean 
              value, the number of prompt tokens, and the number of completion tokens.
    """
    
    # If the input is an empty list just return False
    if text=="":
        return False

    if api_key is None:
        api_key = config('OPEN_AI_API_KEY')

    messages = [{'role': 'system',
                 'content': 'Does the provided text contain a list of things? Answer either yes or no.'},
                {'role': 'user',
                 'content': text}]

    assistant_response, model, prompt_tokens, completion_tokens =\
        call_gpt3_5_turbo(messages, model=model, api_key=api_key)

    if assistant_response.lower().startswith('yes'):
        answer = True
    elif assistant_response.lower().startswith('no'):
        answer = False
    else:
        answer = None
    
    if not report_tokens:
        return answer
    else:
        return answer, prompt_tokens, completion_tokens


def extract_list(text,
                 model='gpt-3.5-turbo',
                 report_tokens=False,
                 api_key=None):
    """
    Extract the list in the input text as a JSON line string object

    Args:
        text (str): The string of text with a list.
        model (str, optional): The LLM model to use, defaulted to 'gpt-3.5-turbo'.
        report_tokens (bool, optional): A flag indicating whether to report the token usage,
                                         defaulted to False.
        api_key (str, optional): The OpenAI API key. If not provided, it will be loaded from
                                  the environment using python-decouple, defaulted to None.

    Returns:
        bool or tuple: 
            - If report_tokens is False, returns a list of JSON objects
            - If report_tokens is True, returns a list of JSON objects,
              the number of prompt tokens, and the number of completion tokens
    """
    
    if api_key is None:
        api_key = config('OPEN_AI_API_KEY')

    directions =  'Produce a JSON line file from the following text. '
    directions += 'Do not return anything but the JSON line objects. '
    directions += 'Add a type field indicating what you think each object is, out the following: '
    directions += 'movie, TV show, other'
    messages = [{'role': 'system',
                 'content': directions},
                {'role': 'user',
                 'content': text}]

    assistant_response, model, prompt_tokens, completion_tokens =\
        call_gpt3_5_turbo(messages, model=model, api_key=api_key)
    
    json_objects = [json.loads(line) for line in assistant_response.splitlines()]

    if not report_tokens:
        return json_objects 
    else:
        return json_objects, prompt_tokens, completion_tokens