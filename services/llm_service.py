import os
import json

from dotenv import load_dotenv
from openai import OpenAI

#load environment variables

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

#generate detailed summary

def summarize(transcript):

    prompt = f"""
You are an AI assistant. 
Summarize the following transcript into concise bullet points.

Include points and hifhlight the important points

Transcript:

{transcript}
"""

    response = client.chat.completions.create(
        model="qwen/qwen3-32b",
        temperature=0.3,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


#generate key takeaways and topics

def generate_insights(summary):

    prompt = f"""
Read the following summary.

Generate ONLY valid JSON.

Format:

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
        "..."
    ]
}}

Instructions:

1. Generate 5 important key takeaways.

2. Generate 4-7 main topics.

Return ONLY valid JSON.

Summary:

{summary}
"""

    response = client.chat.completions.create(
        model="qwen/qwen3-32b",
        temperature=0.2,
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    content = response.choices[0].message.content.strip()

    if content.startswith("```"):

        content = content.replace("```json","")
        content = content.replace("```","")
        content = content.strip()

    try:

        return json.loads(content)

    except json.JSONDecodeError:

        return {

            "takeaways":[],

            "topics":[]
        }


#ask question

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
        temperature=0.2,
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    return response.choices[0].message.content