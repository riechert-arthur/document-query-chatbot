"""
Manages a backing list of dictionary messages.

AUTHOR: Arthur Riechert
VERSION: 1.0.0
"""

class MessageManager():

    def __init__(self):
        self.conversation: list[dict] = []

    def add_message(self, message: dict):
        self.conversation.append(message)
    
    def remove_message(self, index: int):
        self.conversation.remove(index)