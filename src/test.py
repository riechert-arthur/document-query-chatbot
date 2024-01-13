import unittest
import streamlit

from database_manager import DatabaseManager
from credential_exception import CredentialException
from login import register_user
from password import hash_password

"""
A script to perform unit testing.

AUTHOR: Arthur Riechert
VERSION: 1.0.0
"""

class DatabaseTest(unittest.TestCase):

    def test_secrets(self):

        credentials: dict = streamlit.secrets["authentication"]

        self.assertTrue("uri" in credentials)

    def test_credentials(self):
        with self.assertRaises(CredentialException):
            DatabaseManager("")

    def test_startup(self):
        self.assertIsNotNone(
            DatabaseManager(streamlit.secrets["authentication"]["uri"])
                .db
        )

    def test_db_insert(self):
        self.assertIsNotNone(
            DatabaseManager(streamlit.secrets["authentication"]["uri"])
                .insert({
                    "user": "test",
                    "password": "123",
                    "usage": "2000",
                    "limit": "3000",
                    "threads": ["1234", "2133"]
                })
        )

    def test_db_query(self):
        self.assertIsNotNone(
            DatabaseManager(streamlit.secrets["authentication"]["uri"])
                .retrieve({"user": "test"})
        )

    def test_user_exists(self):
        self.assertFalse(
            register_user(
                user="test",
                hash=hash_password("1234"),
                db=DatabaseManager(streamlit.secrets["authentication"]["uri"])
            )
        )

if __name__ == "__main__":
    unittest.main()