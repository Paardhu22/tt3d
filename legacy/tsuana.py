import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"


def call_tsuana(mode, user_input, profile_dict):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": json.dumps({
                        "mode": mode,
                        "profile": profile_dict,
                        "user_input": user_input
                    })
                }
            ],
            max_tokens=800,
            temperature=0.4
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return json.dumps({
            "type": "error",
            "message": str(e)
        })
