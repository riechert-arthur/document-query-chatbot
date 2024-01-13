import unittest
import streamlit

from managers.database_manager import DatabaseManager
from exceptions.credential_exception import CredentialException
from utils.authentication_utils import register_user, login_user, check_for_user
from utils.password_utils import hash_password

"""
A script to perform unit testing.

AUTHOR: Arthur Riechert
VERSION: 1.1.0
"""

class DatabaseTest(unittest.TestCase):

    """
    A basic test to make sure the secrets.toml file is
    in the right place and has the right fields.
    """
    def test_secrets(self):

        credentials: dict = streamlit.secrets["authentication"]

        self.assertTrue("uri" in credentials)

    """
    Ensures that the correct exception is raised when
    DatabaseManager is supplied with an empty uri.
    """
    def test_credentials(self):
        with self.assertRaises(CredentialException):
            DatabaseManager("")

    """
    Ensures that the database is connected up by checking
    that the client is not None.
    """
    def test_startup(self):

        uri: str = streamlit.secrets["authentication"]["uri"]

        db: DatabaseManager = DatabaseManager(uri)

        self.assertIsNotNone(db.db)

    """
    Adds a document to the MongoDB database. The insert method
    will return a String id of the inserted item; thus, it should not
    evaluate to None.
    """
    def test_db_insert(self):

        uri: str = streamlit.secrets["authentication"]["uri"]

        db: DatabaseManager = DatabaseManager(uri)

        hash: bytes = hash_password("1234")

        self.assertIsNotNone(
            db.insert({
                "user": "test",
                "password": hash,
                "usage": 2000,
                "limit": 3000,
                "threads": ["1234", "2133"]
            })
        )

    """
    This test ensures that the database is able to query and return
    an option.
    """
    def test_db_query(self):

        uri: str = streamlit.secrets["authentication"]["uri"]

        db: DatabaseManager = DatabaseManager(uri)

        self.assertIsNotNone(db.retrieve({"user": "test"}))

    """
    Tests that the register_user function does not create a duplicate user.
    """
    def test_register_user_exists(self):

        uri: str = streamlit.secrets["authentication"]["uri"]

        db: DatabaseManager = DatabaseManager(uri)

        self.assertFalse(
            register_user(
                user="test",
                hash=hash_password("1234"),
                db=db
            )
        )

    """
    This test ensures that check for user returns true.
    """
    def test_check_for_user(self):

        uri: str = streamlit.secrets["authentication"]["uri"]

        db: DatabaseManager = DatabaseManager(uri)

        self.assertTrue(
            check_for_user(
                user="test",
                db=db,
            )
        )

    """
    Tests that the login function correctly verifies a test account.
    """
    def test_user_verification(self):
        
        uri: str = streamlit.secrets["authentication"]["uri"]

        db: DatabaseManager = DatabaseManager(uri)

        self.assertTrue(
            login_user(
                user="test",
                password="1234",
                db=db
            )
        )

    """
    Tests that usage metrics are being updated in MongoDB
    """
    def test_updated_count(self):
        
        uri: str = streamlit.secrets["authentication"]["uri"]

        db: DatabaseManager = DatabaseManager(uri)

        test_user: dict = db.get_user("test")
        test_user_id: str = test_user["_id"]
        current_count: int = test_user["usage"]
        extra: int = 20

        new_count: int = current_count + extra

        db.update_count(test_user_id, extra)

        updated_test_user: dict = db.get_user_by_id(test_user_id)
        current_count: int = updated_test_user["usage"]

        self.assertEqual(new_count, current_count)

if __name__ == "__main__":
    unittest.main()