import bcrypt

"""
Provides methods for hashing passwords.

AUTHOR: Arthur Riechert
VERSION: 1.0.0
"""

def hash_password(password):

    salt = bcrypt.gensalt()

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    return hashed_password


def check_password(entered_password, hashed_password):

    return bcrypt.checkpw(entered_password.encode('utf-8'), hashed_password)