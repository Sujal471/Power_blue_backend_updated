from pymongo import MongoClient
import certifi
import os
from dotenv import load_dotenv

load_dotenv()

CONNECTION_STRING = os.getenv("CONNECTION_STRING")
client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
db = client['User_info']  # or client["your_db_name"] if default doesn't work

def get_database():
    return db
