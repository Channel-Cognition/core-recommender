from utils.chancog.messaging import count_gpt_message_tokens, truncate_messages
from utils.chancog.llm import call_gpt3_5_turbo


class Suggestion:
    # Suggest from Convo ID
    # messages [{"role": role, "content": content}, {"role": role, "content": content}]
    # role:snippet_type, content:text
    def __init__(self, messages, llm_model):
        self.messages = messages
        self.llm_model = llm_model

    @classmethod
    def build_llm_call(cls, messages):
        required_snippets = [{"role": "assistant", "content": m["content"]}
                             for m in messages if m["role"] == "system"]
        num_tokens, num_tokens_list = count_gpt_message_tokens(messages, return_list=True)
        first_limit = 3000
        second_limit = 4000  # 14000
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
        return cls(messages, model)

    def call_gpt(self):
        llm_response, model, prompt_tokens, completion_tokens = call_gpt3_5_turbo(self.messages, model=self.llm_model)
        # Todo save the tokens so we can calculate how much the cost for every convo
        return llm_response

