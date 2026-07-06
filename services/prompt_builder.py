# build prompt for conversational rag


def build_prompt(
    messages,
    context,
    question
):

    prompt = """
You are Lumina AI.

Answer ONLY using the retrieved context.

If the answer is not found,
reply that you couldn't find it in the knowledge base.

"""

    if messages:

        prompt += "\nConversation History\n\n"

        for message in messages:

            role = message["role"].capitalize()

            prompt += (
                f"{role}: {message['content']}\n"
            )

    prompt += "\nRetrieved Context\n\n"

    prompt += context

    prompt += "\n\nCurrent Question\n\n"

    prompt += question

    return prompt