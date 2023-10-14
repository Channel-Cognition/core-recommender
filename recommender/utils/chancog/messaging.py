import tiktoken

def snippets_to_messages(snippets, role_mapping):
    """
    Convert a list of snippets into messages format.

    Parameters:
    ----------
    snippets : list
        List of snippets, where each snippet is a dict with 'snippet_type' and 'text' keys.
    role_mapping : dict
        Mapping of snippet type to role.

    Returns:
    -------
    list
        List of messages where each message is a dict with 'role' and 'content' keys.
    """

    messages = []
    for snippet in snippets:
        role = role_mapping[snippet['snippet_type']]
        content = snippet['text']
        messages.append({"role": role, "content": content})
    return messages

def truncate_messages(messages, num_tokens_list, token_limit, required_snippets=None, role_mapping=None):
    """
    Truncate a list of messages to fit within a specified token limit. This should
    only be called if it is alread known the truncation is needed. Hence, num_tokens_list
    is input so we do not repeat computation.

    Parameters:
    ----------
    messages : list
        List of current messages where each message is a dict with 'role' and 'content' keys.
    num_tokens_list : list
        List of integers representing token counts corresponding to each message in the messages list.
    token_limit : int
        Maximum number of tokens allowed for the combined list of messages.
    required_snippets : list, optional
        Snippets that must be included in the result. Each snippet is a dict.
        Defaults to None.
    role_mapping : dict, optional
        Mapping of snippet type to role. Required if required_snippets is provided.
        Defaults to None.

    Returns:
    -------
    list
        Truncated messages, possibly pre-pended with required snippets.
    """

    # Convert required snippets to messages
    if required_snippets is not None and role_mapping:
        required_messages = snippets_to_messages(required_snippets, role_mapping)
        num_required_tokens = count_gpt_message_tokens(required_messages)
    else:
        num_required_tokens = 0

    new_limit = token_limit - num_required_tokens
    
    # Start by reversing the lists to process the latest messages first
    reversed_messages = list(reversed(messages))
    reversed_tokens_list = list(reversed(num_tokens_list))
    
    truncated_messages = []
    truncated_tokens_sum = 0
    
    for msg, token_count in zip(reversed_messages, reversed_tokens_list):
        if truncated_tokens_sum + token_count <= new_limit:
            truncated_messages.append(msg)
            truncated_tokens_sum += token_count
        else:
            break  # stop when we hit the limit
    
    # Now reverse the truncated list back to the original order
    truncated_messages = list(reversed(truncated_messages))
    
    # If there are required messages, prepend them to the truncated message list
    if required_snippets is not None:
        truncated_messages = required_messages + truncated_messages

    return truncated_messages


def count_gpt_message_tokens(messages, return_list=False):
    """
    Count the total number of tokens in a messages object

    """

    # Get a tokenizer for the specified encoding
    num_tokens_list = []
    num_tokens = 0
    for msg in messages:
        num_new_tokens = count_gpt_tokens(msg['content'])
        num_tokens_list.append(num_new_tokens)
        num_tokens += num_new_tokens
    
    if return_list:
        return num_tokens, num_tokens_list
    else:
        return num_tokens

def count_gpt_tokens(s):
    """
    Count the total number of tokens in the input string

    :param s: The string to tokenize and count

    :return: The number of tokens, an integer
    """

    # Get a tokenizer for the specified encoding
    enc = tiktoken.get_encoding("cl100k_base")

    # Tokenize the input text
    tokens = enc.encode(s)

    # Return the number of tokens, len(tokens)
    return len(tokens)
