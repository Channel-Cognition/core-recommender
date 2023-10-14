from django.conf import settings
import guardrails as gd
import openai
from .models import Snippet
from .pydantics import MovieInfo
from .suggestion import Suggestion


def extract_response(llm_response):
    llm_response = llm_response
    prompt = """

    ${llm_response}

    ${gr.complete_json_suffix_v2}
    """
    # From pydantic:
    guard = gd.Guard.from_pydantic(output_class=MovieInfo, prompt=prompt)
    OPEN_AI_API_KEY = settings.OPEN_AI_KEY
    OAI_KEY = OPEN_AI_API_KEY

    # Wrap the OpenAI API call with the `guard` object
    openai.api_key = OAI_KEY
    raw_llm_output, validated_output = guard(
        openai.Completion.create,
        prompt_params={"llm_response": llm_response},
        engine="text-davinci-003",
        max_tokens=2048,
        temperature=0.3,
    )
    print(validated_output)
    print(raw_llm_output)
    return validated_output


def get_role(snippet_type):
    dict_role = {'FRAMING': 'system',
                 'ASSISTANT MESSAGE': 'assistant',
                 'USER MESSAGE': 'user',
                 'LLM MESSAGE': 'assistant'}
    return dict_role[snippet_type]


def perform_search(query, convo):
    data = []
    # messages [{"role": role, "content": content}, {"role": role, "content": content}]
    data.append({
                "snippet_type": "USER MESSAGE",
                "text": query,
                "convo": convo
            })
    snippets = Snippet.objects.filter(convo=convo, snippet_type="FRAMING")
    messages = [{"role": get_role(snippet.snippet_type), "content":snippet.text}for snippet in snippets]
    messages.append({"role":"user", "content":query})
    suggestion = Suggestion.build_llm_call(messages)
    llm_response = suggestion.call_gpt()
    pydantic_movie = extract_response(llm_response)
    data.append({
                "snippet_type": "LLM MESSAGE",
                "text": llm_response,
                "convo": convo,
                "pydantic_text": pydantic_movie
            })
    for snippet in data:
        Snippet.objects.create(**snippet)
    return convo
