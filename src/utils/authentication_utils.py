import streamlit as st

from managers.database_manager import DatabaseManager
from exceptions.credential_exception import CredentialException
from utils.password_utils import check_password
from utils.openai_utils import create_assistant

"""
Provides all the processes for authenticating a user or creating a new user.

AUTHOR: Arthur Riechert
VERSION: 1.1.0
"""

"""
Checks to see if a user is in the database already.

Args:
    user (str): The user to check for.
    db (DatabaseManager): The DatabaseManager currently employed.

Returns:
    bool: Whether or not the user exists.
"""
def check_for_user(user: str, db: DatabaseManager) -> bool:
    
    if not user:
        raise CredentialException("Invalid user.")
    
    result: dict = db.retrieve({"user": user})
    
    if result and result["user"] == user:
        return True
    
    return False

"""
Inserts a new, default user into MongoDB.

Args:
    user (str): The user to insert.
    hash (str): The encrypted password.
    db (DatabaseManager): The DatabaseManager currently employed.

Returns:
    bool: Whether or not the operation is successful.
"""
def register_user(user: str, hash: bytes, db: DatabaseManager) -> bool:

    # Ensure no duplicates are created.
    user_exists: bool = check_for_user(user, db)
    if user_exists: return False

    # Only create the assistant after we verify the user doesn't exist already.
    api_key: str = st.secrets["openai"]["api_key"]
    assistant_id: str = create_assistant(api_key)
    
    db.insert({
        "user": user,
        "password": hash,
        "usage": 0,
        "limit": 3000,
        "assistant_id": assistant_id,
        "threads": [],
        "chat_history": [],
    })

    return True

"""
Checks to ensure the inputted login credentials match an existing record.

Args:
    user (str): The user to search find and validate.
    password (str): The unencrypted passcode the user entered.
    db (DatabaseManager): The currently employed DatabaseManager.

Returns:
    bool: Whether or not the operation was a success.
"""
def login_user(user: str, password: str, db: DatabaseManager) -> bool:

    verified: bool = False
    user_exists: bool = check_for_user(user, db)

    if user_exists:
        
        result: dict = db.retrieve({"user": user})
        username: str = result["user"]
        hash: bytes = result["password"]

        verified: bool = username == user and check_password(password, hash)
            
    return verified