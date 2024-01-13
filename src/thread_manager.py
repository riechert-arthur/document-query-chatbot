from credential_exception import CredentialException

import openai

import time

"""
A class to manage a single assistant's threads from OpenAI.

AUTHOR: Arthur Riechert
VERSION: 1.0.0
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
        
        self.client = openai.OpenAI(api_key=api_key)

        self.assistant_id = assistant_id
        self.thread_id = thread_id

    def get_response(self, message: str):

        self.client.beta.threads.messages.create(
            self.thread_id,
            role="user",
            content=message
        )

        run = self.client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id
        )

        while run.status not in ["completed", "failed"]:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread_id,
                run_id=run.id
            )

        if run.status == "completed":

            response = self.client.beta.threads.messages.list(thread_id=self.thread_id, order="desc")

            return response
        
    def get_all_messages(self):
        return self.client.beta.threads.messages.list(thread_id=self.thread_id, order="asc")

