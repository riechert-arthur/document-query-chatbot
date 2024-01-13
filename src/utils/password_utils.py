from bcrypt import gensalt, hashpw, checkpw

"""
Provides methods for hashing passwords.

AUTHOR: Arthur Riechert
VERSION: 1.1.0
"""

"""
Encrypts a string password.

Args:
    password (str): The string to be encrypted.

Returns:
    bytes: The hashed password.
"""
def hash_password(password: str) -> bytes:

    salt: bytes = gensalt()

    hashed_password: bytes = hashpw(password.encode('utf-8'), salt)

    return hashed_password

"""
Checks if an unencrypted password equals an encrypted password.

Args:
    entered_password (str): The unhashed password to check.
    hashed_password (bytes): A string bytes representing a hashed password.

Returns:
    bool: Whether or not the two passwords are equal.
"""
def check_password(entered_password: str, hashed_password: bytes) -> bool:

    return checkpw(entered_password.encode('utf-8'), hashed_password)