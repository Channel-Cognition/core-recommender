import tiktoken
import json

def count_tokens_and_lines_in_jsonl(filename, text_field, max_tokens=None):
    """
    Count the total number of tokens and lines in a JSONL file.

    :param filename: The path to the input JSONL file.
    :param text_field: The field of the JSON objects to tokenize.
    :param max_tokens: The maximum number of tokens per line. If a line contains more tokens,
                       this number will be added to the total token count instead of the actual
                       number of tokens. If None, all tokens are counted. Default is None.

    :return: A tuple containing the total number of tokens and lines.
    """

    # Initialize counters for tokens and lines
    token_count = 0
    line_count = 0

    # Get a tokenizer for the specified encoding
    enc = tiktoken.get_encoding("cl100k_base")

    # Open the specified file in read mode
    with open(filename, 'r') as file:
        # Iterate over each line in the file
        for line in file:
            # Parse the line as a JSON object
            data = json.loads(line)

            # Tokenize the text in the specified field of the JSON object
            tokens = enc.encode(data[text_field])

            # Increment the line counter
            line_count += 1

            # Increment the token counter
            # If max_tokens is provided and len(tokens) exceeds it, add max_tokens to the count
            # Otherwise, add the actual number of tokens
            token_count += min(len(tokens), max_tokens) if max_tokens else len(tokens)

    # Return the total number of tokens and lines
    return token_count, line_count




# https://hmarr.com/blog/counting-openai-tokens/
#    https://community.openai.com/t/how-to-calculate-the-tokens-when-using-function-call/266573/10
#    def num_tokens_from_functions(functions, model="gpt-3.5-turbo-0613"):
#        """Return the number of tokens used by a list of functions."""
#        try:
#            encoding = tiktoken.encoding_for_model(model)
#        except KeyError:
#            print("Warning: model not found. Using cl100k_base encoding.")
#            encoding = tiktoken.get_encoding("cl100k_base")
#        
#        num_tokens = 0
#        for function in functions:
#            function_tokens = len(encoding.encode(function['name']))
#            function_tokens += len(encoding.encode(function['description']))
#            
#            if 'parameters' in function:
#                parameters = function['parameters']
#                if 'properties' in parameters:
#                    for propertiesKey in parameters['properties']:
#                        function_tokens += len(encoding.encode(propertiesKey))
#                        v = parameters['properties'][propertiesKey]
#                        for field in v:
#                            if field == 'type':
#                                function_tokens += 2
#                                function_tokens += len(encoding.encode(v['type']))
#                            elif field == 'description':
#                                function_tokens += 2
#                                function_tokens += len(encoding.encode(v['description']))
#                            elif field == 'enum':
#                                function_tokens -= 3
#                                for o in v['enum']:
#                                    function_tokens += 3
#                                    function_tokens += len(encoding.encode(o))
#                            else:
#                                print(f"Warning: not supported field {field}")
#                    function_tokens += 11
#
#            num_tokens += function_tokens
#
#        num_tokens += 12 
#        return num_tokens
#