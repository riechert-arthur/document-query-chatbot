from database_manager import DatabaseManager
from credential_exception import CredentialException
from password import check_password
from openai_manager import create_assistant
import streamlit

"""
Provides all the processes for authenticating a user or creating a new user.

AUTHOR: Arthur Riechert
VERSION: 1.0.0
"""

def check_for_user(user: str, db: DatabaseManager) -> bool:
    
    if not user:
        raise CredentialException("Invalid user.")
    
    for result in db.retrieve({"user": user}):
        if result["user"] == user:
            return True
        
    return False

def register_user(user: str, hash: str, db: DatabaseManager) -> bool:

    if check_for_user(user, db):
        return False
    
    db.insert({
        "user": user,
        "password": hash,
        "usage": 0,
        "limit": 3000,
        "assistant_id": create_assistant(streamlit.secrets["openai"]["api_key"]),
        "threads": [],
        "chat_history": [],
    })

    return True

def login_user(user: str, password: str, db: DatabaseManager) -> bool:

    if check_for_user(user, db):
        for result in db.retrieve({"user": user}):
            if result["user"] == user and check_password(password, result["password"]):
                return True
            
    return False