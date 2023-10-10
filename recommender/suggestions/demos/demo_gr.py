# Working example using guardrails based on code here:
# https://docs.guardrailsai.com/guardrails_ai/getting_started/

from pydantic import BaseModel, Field
from typing import List, Optional
from guardrails.validators import ValidRange, ValidChoices
from rich import print
import guardrails as gd
import openai
#import os
from decouple import config

# doctors_notes = """Chest pain that may feel like pressure, tightness, pain, squeezing or aching.
#     &amp;Pain or discomfort that spreads to the shoulder, arm, back, neck, jaw, teeth or sometimes the upper belly.
#     &amp;Cold sweat.
#     &amp;Fatigue.
#     &amp;Heartburn or indigestion.
#     &amp;Lightheadedness or sudden dizziness.
#     &amp;Nausea.
#     &amp;Shortness of breath.
# """

doctors_notes = """49 y/o Male with chronic macular rash to face &amp; hair, worse in beard, eyebrows &amp; nares.
Itchy, flaky, slightly scaly. Moderate response to OTC steroid cream"""

prompt = """
Given the following doctor's notes about a patient, please extract a dictionary that contains the patient's information.

${doctors_notes}

${gr.complete_json_suffix_v2}
"""

class Symptom(BaseModel):
    symptom: str = Field(description="Symptom that a patient is experiencing")
    affected_area: str = Field(description="What part of the body the symptom is affecting", validators=[ValidChoices(choices=['head', 'neck', 'chest'], on_fail="reask")])

class Medication(BaseModel):
    medication: str = Field(description="Name of the medication the patient is taking")
    response: str = Field(description="How the patient is responding to the medication")


class PatientInfo(BaseModel):
    gender: str = Field(description="Patient's gender")
    age: int = Field(validators=[ValidRange(min=0, max=100, on_fail="fix")])
    symptoms: List[Symptom] = Field(description="Symptoms that the patient is currently experiencing. Each symptom should be classified into a separate item in the list.")
    current_meds: List[Medication] = Field(description="Medications the patient is currently taking and their response")


# From pydantic:
guard = gd.Guard.from_pydantic(output_class=PatientInfo, prompt=prompt)
OAI_KEY = config('OPEN_AI_API_KEY')
# Wrap the OpenAI API call with the `guard` object
openai.api_key = OAI_KEY
raw_llm_output, validated_output = guard(
    openai.Completion.create,
    prompt_params={"doctors_notes": doctors_notes},
    engine="text-davinci-003",
    max_tokens=1024,
    temperature=0.3,
)

# Print the validated output from the LLM
print(validated_output)
print(raw_llm_output)

# print(guard.state.most_recent_call.history[0].rich_group)
# print(guard.state.most_recent_call.history[1].rich_group)
# print(guard.state.most_recent_call.tree)