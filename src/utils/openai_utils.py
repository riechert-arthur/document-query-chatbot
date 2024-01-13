from openai import OpenAI

"""
Functions to work with OpenAI's API.

AUTHOR: Arthur Riechert
VERSION: 1.1.0
"""

"""
Creates a default assistant in OpenAI.

Args:
    api_key (str): The key to your OpenAI account.

Returns:
    str: The id of the assistant created.
"""
def create_assistant(api_key: str) -> str:
    return OpenAI(api_key=api_key).beta.assistants.create(
        instructions="You are a friendly assistant.",
        tools=[{"type": "retrieval"}],
        model="gpt-4-1106-preview",
    ).id

"""
Deletes an existing assistant.

Args:
    api_key (str): The key to your OpenAI account.
"""
def delete_assistant(api_key: str, assistant_id: str) -> None:
    OpenAI(api_key=api_key).beta.assistants.delete(assistant_id)

"""
Creates a new thread.

Args:
    api_key (str): The key to your OpenAI account.

Returns:
    str: The thread's id.
"""
def create_thread(api_key: str) -> str:
    return OpenAI(api_key=api_key).beta.threads.create().id