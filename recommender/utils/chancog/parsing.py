import re

def contains_numbered_list_dumb(text):
    """
    Determines whether a given text contains a numbered list.
    
    Parameters:
    text (str): The text to be checked for a numbered list.
    
    Returns:
    bool: True if a numbered list is found, False otherwise.
    """
    # Strip leading and trailing whitespace
    text = text.strip()

    # Regular expression to match lines that optionally start with whitespace,
    # followed by a number and either a period or a parenthesis.
    pattern = re.compile(r'^\s*\d+[.)]', re.MULTILINE)
    
    # Search for the pattern in the text
    match = pattern.search(text)
    
    # Return True if a match is found, otherwise False
    return bool(match)

def extract_numbered_list_content_dumb(text):
    """
    Extracts the content of numbered list items from a given text.
    
    Parameters:
    text (str): The text containing a numbered list.
    
    Returns:
    list: A list of strings, each string representing the content of a list item.
          Returns an empty list if no numbered list items are found.
    """
    # Regular expression to match numbered list items.
    # This pattern looks for a number followed by either a period or a parenthesis,
    # and captures the rest of the text on the line.
    pattern = re.compile(r'^\s*\d+[.)]\s*(.*?)(?=\s*\d+[.)]|$)', re.MULTILINE | re.DOTALL)
    
    # Find all matches of the pattern in the text
    matches = pattern.findall(text)
    
    # If matches were found, return a list of the matched content;
    # otherwise, return an empty list.
    return matches if matches else []