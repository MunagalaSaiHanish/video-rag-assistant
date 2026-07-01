import os

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


def summarize(text):

    prompt = f"""
Summarize the following transcript into concise bullet points.

Transcript:

{text}
"""

    response = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


def ask_question(question, context):

    prompt = f"""
Answer ONLY using the context below.

Context:
{context}

Question:
{question}

If the answer is not present in the context,
reply with:
"I couldn't find that information in the video."
"""

    response = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content