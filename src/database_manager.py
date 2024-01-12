import credential_exception
import pymongo

"""
A class to manage the database connection with MongoDB.

AUTHOR: Arthur Riechert
VERSION: 1.0.0
"""

class DatabaseManager():

    def __init__(self, **credentials):

        if (credentials == None):
            raise credential_exception.CredentialException("No login information presented!")

        self.credentials: dict = credentials
        self.client: pymongo.MongoClient = self.start_connection()

    def start_connection(self) -> pymongo.MongoClient:
        return pymongo.MongoClient(self.credentials)
    
    # Will ensure client has working connection.
    # Will try 3 times after failure.
    def test_client(self) -> bool:
        
        count = 0

        while (count < 3):
            try:
                self.client.test_database
            except pymongo.ConnectionFailure as e:
                print (f"Connection failed. Retrying... Attempt:{count} Remaining:{3 - 1 - count}")

                if count == 2:
                    return False
                
                count += 1

        return True