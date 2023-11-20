from chancog.diagnostics import start_diagnostics, add_diagnostic_info, end_diagnostics
import tiktoken
import random
from openai import OpenAIError
from retry import retry
import openai

class OpenAIHandler:
    def __init__(self, openai_key, max_retries=3, base_delay=1):
        self.openai_key = openai_key
        self.client = openai.OpenAI(api_key=self.openai_key)
        self.max_retries = max_retries
        self.base_delay = base_delay
        
    def retry_decorator(self, function):
        return retry(OpenAIError, tries=self.max_retries, delay=self.base_delay, backoff=2)(function)

    def call_gpt(self, messages, n=1, model='gpt-3.5-turbo', json_mode=False):
        diagnostics = start_diagnostics('OpenAIHandler.call_gpt')
        add_diagnostic_info(diagnostics, 'model', model)

        @self.retry_decorator
        def make_request():
            if not json_mode:
                response = self.client.chat.completions.create(model=model, messages=messages, n=n)
            else:
                response = self.client.chat.completions.create(model=model, messages=messages, n=n, response_format={"type": "json_object"})
            return response

        try:
            response = make_request()
        except OpenAIError as e:
            add_diagnostic_info(diagnostics, 'OpenAIError', str(e))
            print(f"OpenAIError: {e}")
            return None, diagnostics
        except Exception as e:
            add_diagnostic_info(diagnostics, 'exception', str(e))
            print(f"An unexpected error occurred: {e}")
            return None, diagnostics

        # Extract the model's response and return
        if n == 1:
            assistant_response = response.choices[0].message.content
        else:
            assistant_response = [choice.message.content for choice in response.choices]

        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        add_diagnostic_info(diagnostics, 'prompt_tokens', prompt_tokens)
        add_diagnostic_info(diagnostics, 'completion_tokens', completion_tokens)
        end_diagnostics(diagnostics)
        return assistant_response, diagnostics

    def answer_yes_no_question(self, question, model='gpt-3.5-turbo'):
        diagnostics = start_diagnostics('OAIAzureServiceHandler.answer_yes_no_question')
        add_diagnostic_info(diagnostics, 'model', model)
        full_question = question + '\n' + """Answer with 'yes' or 'no' only."""
        messages = [{'role': 'user', 'content': full_question}]
        assistant_response, call_diagnostics = self.call_gpt(messages, model=model)
        diagnostics['children'].append(call_diagnostics)
    
        if assistant_response.lower().startswith('yes'):
            answer = True
        elif assistant_response.lower().startswith('no'):
            answer = False
        else:
            answer = None

        end_diagnostics(diagnostics)
        return answer, diagnostics

    

    def task_tournament(self,
                        task,
                        num_rounds=1,
                        model='gpt-3.5-turbo',
                        json_mode=False):
        diagnostics = start_diagnostics('OpenAIHandler.task_tournament')
        
        if num_rounds > 4:
            raise ValueError(f'num_rounds = {num_rounds}, but should be 4 or less')
        n = 2**num_rounds
        messages = [{'role':'user', 'content': task}]
        candidate_responses, call_diagnostics = self.call_gpt(messages,
                                                              n=n,
                                                              model=model,
                                                              json_mode=json_mode)
        diagnostics['children'].append(call_diagnostics)
        done = False
    
        directions_start = 'Here is a task:\n'
        directions_start += task + '\n'
        directions_end = 'Is Response 1 better than Response 2?'
     
        while not done:
            # Iterate over bouts, which are sequential candidate responses
            num_bouts = len(candidate_responses) // 2
            new_candidate_responses = []
            for bout in range(num_bouts):
                response1 = candidate_responses[2*bout]
                response2 = candidate_responses[2*bout + 1]
                directions = directions_start
                directions += 'Response 1:\n'
                directions += response1 + '\n'
                directions += 'Response 2:\n'
                directions += response2 + '\n'
                directions += directions_end
                answer, call_diagnostics = self.answer_yes_no_question(directions, model=model)
                diagnostics['children'].append(call_diagnostics)
                if answer is None:
                    # Choosing randomly between response1 and response2
                    chosen_response = random.choice([response1, response2])
                    new_candidate_responses.append(chosen_response)
                elif answer is True:
                    new_candidate_responses.append(response1)
                else:
                    # answer is False
                    new_candidate_responses.append(response2)
    
            candidate_responses = new_candidate_responses
            if len(candidate_responses) == 1:
                done = True
                response = candidate_responses[0]
    
        end_diagnostics(diagnostics)
        return response, diagnostics

def count_tokens(text, model=None):
    # Return the number of tokens in text
    # Optionally, if model is None, also return the cost
    enc = tiktoken.get_encoding("cl100k_base")
    # Tokenize the content
    tokens = len(enc.encode(text))

    if model is None:
        return tokens
            
    if model == 'gpt-4-1106-preview':
        # USD per token
        input_token_cost = .01 / 1000
    else:
         raise ValueError(f'Unrecognized model = {model}')
    
    return tokens, input_token_cost * tokens

# TODO: count tokens by model, returning a dictionary (and similarlly for calc_gpt_cost)
def count_diagnostics_tokens(diagnostics):
    total_prompt_tokens = 0
    total_completion_tokens = 0

    prompt_tokens = diagnostics.get('prompt_tokens', None)
    if prompt_tokens is not None:
        total_prompt_tokens += prompt_tokens

    completion_tokens = diagnostics.get('completion_tokens', None)
    if completion_tokens is not None:
        total_completion_tokens += completion_tokens
    
    if len(diagnostics['children']) == 0:
        return total_prompt_tokens, total_completion_tokens
    
    for sub_diag in diagnostics['children']:
        prompt_tokens, completion_tokens = count_diagnostics_tokens(sub_diag)
        total_prompt_tokens += prompt_tokens
        total_completion_tokens += completion_tokens
    
    return total_prompt_tokens, total_completion_tokens

def calc_gpt_cost(input_tokens, output_tokens, model):
    # USD per token
    if model in ['gpt-4-1106-preview', 'gpt-4']:
        input_cost = .01 / 1000
        output_cost = .03 / 1000
    elif model in ['gpt-3.5-turbo-1106', 'gpt-3.5-turbo']:
        input_cost = 0.001 / 1000
        output_cost = 0.002 / 1000
    elif model in ['gpt-4-32k']:
        input_cost = 0.06 / 1000
        output_cost = 0.12 / 1000
    else:
        raise ValueError(f'Unrecognized model = {model}')
    
    return input_tokens * input_cost + output_tokens * output_cost