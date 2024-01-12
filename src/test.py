import unittest
import streamlit

import database_manager
import credential_exception

"""
A script to perform unit testing.

AUTHOR: Arthur Riechert
VERSION: 1.0.0
"""

class DatabaseTest(unittest.TestCase):

    def test_credentials(self):
        with self.assertRaises(
            credential_exception.CredentialException
        ):
            database_manager.DatabaseManager()

    @streamlit.cache_resource
    def test_connection(self):
        self.assertTrue(
           database_manager.DatabaseManager(**streamlit.secrets(["authentication"])).test_client()
        )

if __name__ == "__main__":
    unittest.main()