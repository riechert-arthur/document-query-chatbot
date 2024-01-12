import unittest
import streamlit

from database_manager import DatabaseManager
from credential_exception import CredentialException

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
                .client
        )

if __name__ == "__main__":
    unittest.main()