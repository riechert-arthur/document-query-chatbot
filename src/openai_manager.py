import openai

"""
Functions to work with OpenAI's API.

AUTHOR: Arthur Riechert
VERSION: 1.0.0
"""

def create_assistant(api_key: str):
    return openai.OpenAI(api_key=api_key).beta.assistants.create(
        instructions="You are a friendly assistant.",
        tools=[{"type": "retrieval"}],
        model="gpt-4",
    ).id

def create_thread(api_key: str):
    return openai.OpenAI(api_key=api_key).beta.threads.create().id

def get_threads(api_key: str, thread_ids: list[str]):

    threads = []

    client = openai.OpenAI(api_key=api_key)

    for id in thread_ids:
        threads.append(
            client.beta.threads.retrieve(id)
        )

    return threads

def get_first_messages(api_key: str, thread_ids: list[str]):

    first_messages = {}

    client = openai.OpenAI(api_key=api_key)

    for id in thread_ids:
        messages = client.beta.threads.messages.list(id).data
        first_messages[messages[0]["created_at"]] = messages[0]["content"]["text"]["value"]

    return first_messages