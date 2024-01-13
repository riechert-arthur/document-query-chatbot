from credential_exception import CredentialException
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure

"""
A class to manage the database connection with MongoDB.

AUTHOR: Arthur Riechert
VERSION: 1.0.0
"""

class DatabaseManager:

    def __init__(self, uri: str):

        if not uri:
            raise CredentialException("No URI provided!")

        self.uri = uri
        self.db = self.start_connection()

    def start_connection(self):

        try:
            client = MongoClient(self.uri, server_api=ServerApi('1'))

            client.admin.command('ping')

            return client["demo"]["users"]
        
        except ConnectionFailure as e:
            raise ConnectionError(f"Connection failed: {e}")
        
    def insert(self, item: dict) -> str:
        return self.db.insert_one(item).inserted_id
    
    def retrieve(self, query: dict) -> dict:
        return self.db.find(query)
    
    def get_user(self, username: str) -> dict:
        
        users = self.retrieve({"user": username})

        for user in users:
            if user["user"] == username:
                return user
            
    def add_thread(self, user: str, item: str) -> dict:

        user_id = self.get_user(user)["_id"]

        self.db.update_one(
            {"_id": user_id},
            {"$push": { "threads": item}}
        )

    def update_chat_history(self, user: str, chat_history: list[dict]):

        user_id = self.get_user(user)["_id"]

        self.db.update_one(
            {"_id": user_id},
            {"$set": {"chat_history": chat_history}}
        )