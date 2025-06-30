# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Ensures .env variables are loaded into os.environ

class Config:
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
    INDEX_NAME = os.getenv("INDEX_NAME")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    CONNECTION_STRING = os.getenv("CONNECTION_STRING")
    Google_Recaptcha = os.getenv("Google_Recaptcha")