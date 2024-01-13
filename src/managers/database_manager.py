from exceptions.credential_exception import CredentialException
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

        self.uri: str = uri
        self.db = self.start_connection()

    """
    Initializes the MongoDB database instance.

    Returns:
        Database: An instnace of the MongoDB database.
    """
    def start_connection(self) -> any:

        try:
            client: MongoClient = MongoClient(self.uri, server_api=ServerApi('1'))

            client.admin.command('ping')

            return client["demo"]["users"]
        
        except ConnectionFailure as e:

            raise ConnectionError(f"Connection failed: {e}")
        
    """
    Inserts a single document into the database.

    Args:
        item (dict): A dict containing document information.

    Returns:
        string: The id created for the new entry.
    """
    def insert(self, item: dict) -> str:
        return self.db.insert_one(item).inserted_id
    
    """
    Retrieves a single document from the database.

    Args:
        query (dict): A dict containing query.

    Returns:
        dict: The result of the query.
    """
    def retrieve(self, query: dict) -> dict:
        return self.db.find_one(query)
    
    """
    Finds a single user in the database.

    Args:
        username (str): The username that you want to locate.

    Returns:
        dict: The user's information.
    """
    def get_user(self, username: str) -> dict:
        
        user = self.retrieve({"user": username})

        return user
    
    """
    Retrieves a users by id.

    Args:
        id (str): The id of the user to retrieve.

    Returns:
        dict: The user's information.
    """
    def get_user_by_id(self, id: str) -> dict:

        user = self.retrieve({"_id": id})

        return user

    """
    Inputs the ids for threads related to an individual.

    Args:
        username (str): The username of the user.
        item (str): The thread's id.
    """     
    def add_thread(self, username: str, thread_id: str) -> None:

        user_id = self.get_user(username)["_id"]

        self.db.update_one(
            {"_id": user_id},
            {"$push": { "threads": thread_id}}
        )

    """
    Replaces the current chat history with a new one.

    Args:
        username (str): The username of the person.
        chat_history (list[dict]): The new chat history.
    """
    def update_chat_history(self, username: str, chat_history: list[dict]) -> None:

        user_id = self.get_user(username)["_id"]

        self.db.update_one(
            {"_id": user_id},
            {"$set": {"chat_history": chat_history}}
        )

    """
    Removes the user based on id.

    Args:
        user_id (str): The id of the user to be deleted.
    """
    def delete_user(self, user_id: str) -> None:
        self.db.delete_one({"_id": user_id})

    """
    Adds an extra amount of the current usage of the user.

    Args:
        id (str): The id of the user.
        extra (int): The amount to add.
    """
    def update_count(self, id: str, extra: int) -> None:

        user: dict = self.db.find_one({"_id": id})

        current_count: int = user["usage"] + extra
        
        self.db.update_one(
            {"_id": id},
            {"$set": {"usage": current_count}}
        )