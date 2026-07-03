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


#analyze video

def analyze_video(transcript):

    prompt = f"""
You are an expert AI Video Analyst.

Analyze the following YouTube transcript.

Return ONLY valid JSON in this format:

{{
    "summary": "...",
    "takeaways": [
        "...",
        "...",
        "...",
        "...",
        "..."
    ],
    "topics": [
        "...",
        "...",
        "...",
        "..."
    ]
}}

Instructions:

1. Write a DETAILED AI Summary.
- Explain the video thoroughly.
- Cover all major concepts.
- The summary should be detailed study notes.
- Write multiple well-structured paragraphs.
- Do NOT make it short.
- Include important explanations and examples from the video.

2. Generate 5-8 key takeaways.

3. Generate 4-8 main topics.

Return ONLY valid JSON.

Do NOT use markdown.

Do NOT wrap the JSON inside ```json.
    
Transcript:

{transcript}
"""

    response = client.chat.completions.create(
        model="qwen/qwen3-32b",
        temperature=0.2,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response.choices[0].message.content.strip()

    #remove markdown if model returns it

    if content.startswith("```"):

        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

    try:

        return json.loads(content)

    except json.JSONDecodeError:

        return {
            "summary": content,
            "takeaways": [],
            "topics": []
        }


#summary

def summarize(text):

    result = analyze_video(text)

    return result["summary"]


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
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content