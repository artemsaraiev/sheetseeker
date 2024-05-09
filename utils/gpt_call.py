import requests
import os
import json
from openai import OpenAI

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
print(OPENROUTER_API_KEY)

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key= OPENROUTER_API_KEY,
)


def send_gpt_request(messages, model, request_type):
    prepend_messages = [{"role": "system", "content": "Generate 5 questions that potential might ask about this part of this table."}]

    if request_type == "generate_questions":
        messages = prepend_messages + messages

    completion = client.chat.completions.create(
      model=model,
      messages=messages,
    )
    # print(completion.choices[0].message.content)
    return completion.choices[0].message.content