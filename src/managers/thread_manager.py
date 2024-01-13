from exceptions.credential_exception import CredentialException

from openai.types.beta.threads.run import Run
from openai import OpenAI

"""
A class to manage a single assistant's threads from OpenAI.

AUTHOR: Arthur Riechert
VERSION: 1.1.0
"""

class ThreadManager():
    
    def __init__(
        self,
        api_key: str,
        assistant_id: str,
        thread_id: str,
    ):
        
        if not api_key:
            raise CredentialException("No API key provided!")
        elif not assistant_id:
            raise CredentialException("No Assistant Id provided!")
        
        self.client: OpenAI = OpenAI(api_key=api_key)

        self.assistant_id: str = assistant_id
        self.thread_id: str = thread_id

    """
    This function adds a message to the user's thread, runs it, waits for
    a response, and then, will extract the message from the resulting
    data structure.

    Args:
        message (str): The message to be sent to be added to the thread.

    Returns:
        list: All the messages in the current thread after response is ran, in descending order.
    """
    def get_response(self, message: str) -> list:

        # Add the messages to the thread.
        self.client.beta.threads.messages.create(
            self.thread_id,
            role="user",
            content=message
        )

        # Run the thread.
        run: Run = self.client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id
        )

        # Wait for completion.
        while run.status not in ["completed", "failed"]:
            run: Run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread_id,
                run_id=run.id
            )

        if run.status == "completed":

            response: list = self.client.beta.threads.messages.list(thread_id=self.thread_id, order="desc")

            return response
        
    """
    Returns all messages in a single thread.

    Returns:
        list: All the messages in the current thread in ascending order.
    """
    def get_all_messages(self) -> list:
        return self.client.beta.threads.messages.list(thread_id=self.thread_id, order="asc")

