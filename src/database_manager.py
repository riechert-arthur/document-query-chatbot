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
        self.client = self.start_connection()

    def start_connection(self):
        try:
            client = MongoClient(self.uri, server_api=ServerApi('1'))

            client.admin.command('ping')
            return client
        except ConnectionFailure as e:
            raise ConnectionError(f"Connection failed: {e}")