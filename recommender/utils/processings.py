import re
import json
import datetime
from chancog.diagnostics import start_diagnostics, end_diagnostics

from chancog.sagenerate.items import build_display_item_info, build_item_summary_dict
from chancog.sagenerate.items import make_item_from_cosmos_info
from chancog.sagenerate.items import Item


def convert_to_list_json(response):
    pattern = re.compile(r'(?P<position>\d+)\. (?P<title>.+?) \((?P<year>\d{4})\)')

    # Find all matches in the response
    matches = pattern.finditer(response)
    result = [{"name": match.group('title').strip(), "year": match.group('year'), "item_type":"movie"} for match in matches]
    return result


def parse_movie_list(input_string):
    movies = []

    # Define the pattern to extract information
    pattern = re.compile(r'(?P<name>[\w\s]+) \((?P<year>\d{4})\) \(movie\)')

    # Iterate over matches in the input string
    for match in pattern.finditer(input_string):
        movie_info = {
            "item_type": "movie",
            "name": match.group('name').strip(),
            "year": match.group('year')
        }
        movies.append(movie_info)

    return movies


def process_suggestion(suggestion,
                       oai_handler,
                       oai_model,
                       pc_handler,
                       cosmos_handler):
    """
    Process an LLM item suggestion asynchronously


    Args:
        suggestion (dict): The suggestion, a dictionary that should contain item_type
        oai_handler (OpenAIHandler): An object of class OpenAIHandler. The oai_handler and oai_model in tandem must support JSON mode
        oai_model (str): The Open AI model to use
        pc_handler (PineconeManager): Handler for Pinecone vector database interactions
        cosmos_handler (CosmosHandler): Handler for CosmosDB interactions

    Returns:
        tuple:
            - dict or None: A dictionary containing information about the matched item, or None if no suitable match was found.
            - dict: Diagnostic information related to the function execution.
    """

    # cosmos_item_info, display_item_info, metric, diagnostics = data_tuple
    data_tuple = make_prelim_match(suggestion,
                                         oai_handler,
                                         pc_handler,
                                         cosmos_handler.containers['items'])

    cosmos_item_info, display_item_info, metric, diagnostics = data_tuple
    # display_item_info, diagnostics = data_tuple2
    data_tuple2 = make_final_match(suggestion,
                                         oai_handler,
                                         oai_model,
                                         pc_handler,
                                         cosmos_handler.containers['items'])

    # TODO: should we always send this?
    display_item_info, diagnostics = data_tuple2
    return display_item_info, diagnostics


def make_prelim_match(llm_suggestion,
                            oai_handler,
                            pc_handler,
                            cosmos_container):
    """
    Make a fast, preliminary match of the input llm_suggestion in our Pinecone vector database

    This function takes an input suggestion from a language model, embeds it using the Azure Open AI API, and then finds
    a preliminary match in the vector database using Pinecone. It also retrieves additional item information from a CosmosDB
    NoSQL database, and prepares this information for display in the frontend application.

    Args:
        llm_suggestion (dict): The suggestion, a dictionary that should contain item_type
        oai_handler (object): The Open AI API handler
        pc_handler (object): Handler for Pinecone API interactions, used for finding matches in the vector database.
        cosmos_container (CosmosContainer): A CosmosDB container object, used to retrieve item information.

    Returns:
        A tuple consisting of (cosmos_item_info, display_item_info, metric, diagnostics), where:
        - cosmos_item_info (dict): The raw item information from CosmosDB.
        - display_item_info (dict): The processed item information formatted for frontend display.
        - metric (float): The metric score of the vector match (likely cosine similiarity)
        - diagnostics (dict): A dictionary containing diagnostic information about the function's execution.

    """

    # Implement logic to create a preliminary match
    diagnostics = start_diagnostics('make_prelim_match')

    suggested_item = Item.create_item_from_dict(llm_suggestion)

    # Embed the input text
    item_embedding, call_diagnostics = oai_handler.call_ada2(str(llm_suggestion))
    diagnostics['children'].append(call_diagnostics)

    # Match the text
    matches, call_diagnostics = pc_handler.find_matches(item_embedding,
                                                        num_matches=10)
    diagnostics['children'].append(call_diagnostics)

    if len(matches) == 0:
        # This should only happen if the vector database is empty
        diagnostics['outcome'] = 'No matches in vector database'
        end_diagnostics(diagnostics)
        return None, None, None, diagnostics

    # Iterate over the matches
    best_metric = None
    best_cosmos_item_info = None
    best_display_item_info = None
    for item_id, metric in matches:
        # Get the item info from the Cosmos NoSQL database, then build
        # the item info needed for display in the frontend
        t0 = datetime.datetime.now()
        cosmos_item_info = cosmos_container.read_item(item_id, partition_key=item_id)
        t1 = datetime.datetime.now()
        time_diff = t1 - t0
        dt = time_diff.total_seconds() * 1000
        diagnostics['container_time_ms'] = dt
        item = make_item_from_cosmos_info(cosmos_item_info)
        display_item_info = build_display_item_info(cosmos_item_info)
        if best_metric is None or item == suggested_item:
            best_cosmos_item_info = cosmos_item_info
            best_display_item_info = display_item_info
            best_metric = metric
        if item == suggested_item:
            break

    diagnostics['outcome'] = 'Success'
    end_diagnostics(diagnostics)
    return best_cosmos_item_info, best_display_item_info, best_metric, diagnostics


# TODO: should we first check whether the match is good with an LLM call?
#       there's some repeat code with make_prelim_match, bit it's this current approach is simple
def make_final_match(llm_suggestion,
                           oai_handler_azure,
                           oai_model,
                           pc_handler,
                           cosmos_container,
                           num_matches=10):
    """
    For the input llm_suggesiton, retrieve matches from the database then ask an LLM which is the best match


    Args:
        llm_suggestion (dict): The suggestion made by the llm
        oai_handler_azure (object): An object of class OAIAzureServiceHandler for making calls to the Azure Open AI Service.
        pc_handler (object): An object of class PineconeManager for making calls to the Pinecone vector database
        container (object): An object for interacting with the Cosmos DB container
        num_matches (int, optional): The number of candidate matches to use. Defaults to 5.

    Returns:
        tuple:
            - dict or None: A dictionary containing information about the matched item, or None if no suitable match was found.
            - dict: Diagnostic information related to the function execution.
    """
    diagnostics = start_diagnostics('rag_matcher')

    # Embed the input text
    item_embedding, call_diagnostics = oai_handler_azure.call_ada2(str(llm_suggestion))
    diagnostics['children'].append(call_diagnostics)

    # Match the text
    matches, call_diagnostics = pc_handler.find_matches(item_embedding,
                                                        num_matches=num_matches)
    diagnostics['children'].append(call_diagnostics)

    if len(matches) == 0:
        # This should only happen if the vector database is empty
        diagnostics['outcome'] = 'No matches in vector database'
        end_diagnostics(diagnostics)
        return None, diagnostics

    # TODO: should we use a minimum metric threshold to avoid making unneeded calls to the LLM?

    # Store item_info from the database in a list
    cosmos_item_infos = []
    cosmos_item_summaries = []
    # Itere
    for item_id, metric in matches:
        t0 = datetime.datetime.now()
        item_info = cosmos_container.read_item(item_id, partition_key=item_id)
        t1 = datetime.datetime.now()
        time_diff = t1 - t0
        dt = time_diff.total_seconds() * 1000
        diagnostics['container_time_ms'] = dt
        cosmos_item_infos.append(item_info)
        item_summary = build_item_summary_dict(item_info)
        cosmos_item_summaries.append(item_summary)

    # Turn the summaries into a json string
    summaries_string = json.dumps(cosmos_item_summaries)
    suggestion_string = json.dumps(llm_suggestion)

    task = 'Here is an item:\n'
    task += suggestion_string + '\n'
    task += 'Here are some potential matches from our database:\n'
    task += summaries_string
    task += 'Return a json with the field item_id that contains the matching item ID, or null if the item is not in the candidate matches.\n'

    messages = [{'role': 'user',
                 'content': task}]
    match, call_diagnostics = oai_handler_azure.call_gpt(messages,
                                                         model=oai_model,
                                                         json_mode=True)

    diagnostics['children'].append(call_diagnostics)

    try:
        parsed_match = json.loads(match)
        item_id = parsed_match.get('item_id', None)
    except json.JSONDecodeError as e:
        diagnostics['outcome'] = 'Failed to parse the LLM match string'
        end_diagnostics(diagnostics)
        return None, diagnostics
    except Exception as e:
        diagnostics['outcome'] = 'An unexpected error occured parsing the LLM match string'
        end_diagnostics(diagnostics)
        return None, diagnostics

    if item_id is None:
        diagnostics['outcome'] = 'The LLM could not identify a match or did not return the correct field'
        end_diagnostics(diagnostics)
        return None, diagnostics

    cosmos_item_info = [x for x in cosmos_item_infos if str(item_id) == str(x['id'])]
    if len(cosmos_item_info) == 0:
        diagnostics['outcome'] = 'The matched item is not in cosmos_item_infos'
        end_diagnostics(diagnostics)
        return None, diagnostics

    # diagnostics['outcome'] = 'No match was found'
    cosmos_item_info = cosmos_item_info[0]
    display_item_info = build_display_item_info(cosmos_item_info)
    end_diagnostics(diagnostics)
    return display_item_info, diagnostics
