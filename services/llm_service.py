import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from services.prompt_builder import build_prompt

# ---------------------------------------------------------
# Environment
# ---------------------------------------------------------

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

MODEL = "qwen/qwen3-32b"

SYSTEM_PROMPT = """
You are Lumina AI.

You are an intelligent Knowledge Assistant.

Rules:

- Answer only using the provided context.
- If the answer is not present, clearly say that you couldn't find it.
- Never hallucinate facts.
- Be concise and professional.
- When possible, organize answers using bullet points.
"""

# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

def summarize(text):

    prompt = f"""
Generate a professional summary.

Requirements

- Clear
- Concise
- Preserve important ideas
- Easy to understand

Content

{text}
"""

    try:

        response = client.chat.completions.create(

            model=MODEL,

            temperature=0.3,

            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

        )

        return response.choices[0].message.content

    except Exception:

        return "Unable to generate summary."


# ---------------------------------------------------------
# Insights
# ---------------------------------------------------------

def generate_insights(summary):

    prompt = f"""
Return ONLY valid JSON.

Schema

{{
    "takeaways":[
        "...",
        "...",
        "...",
        "...",
        "..."
    ],
    "topics":[
        "...",
        "...",
        "...",
        "...",
        "..."
    ]
}}

Do not include markdown.

Summary

{summary}
"""

    try:

        response = client.chat.completions.create(

            model=MODEL,

            temperature=0.2,

            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

        )

        content = response.choices[0].message.content.strip()

        if content.startswith("```"):

            content = (
                content
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

        return json.loads(content)

    except Exception:

        return {

            "takeaways": [],

            "topics": []

        }


# ---------------------------------------------------------
# Chat
# ---------------------------------------------------------

def ask_question(

    question,

    context,

    messages=None

):

    if messages is None:

        messages = []

    prompt = build_prompt(

        messages=messages,

        context=context,

        question=question

    )

    try:

        response = client.chat.completions.create(

            model=MODEL,

            temperature=0.2,

            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

        )

        return response.choices[0].message.content

    except Exception:

        return (
            "Sorry, I couldn't generate a response. "
            "Please try again."
        )