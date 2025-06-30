from app.db import get_database
from langchain.schema import HumanMessage
dbname = get_database()
collection = dbname["Previous_chats"]
from pymongo import ASCENDING
from datetime import datetime, timedelta
import pytz

IST = pytz.timezone('Asia/Kolkata')

def store_chat(phone_no: str, name: str, user_question: str, ai_response: str):
    chat_pair = [
        {"role": "user", "content": user_question},
        {"role": "ai", "content": ai_response}
    ]

    now = datetime.now(IST)

    # Clean up if more than 1000 users
    if collection.count_documents({}) > 1000:
        oldest = collection.find({}).sort("last_chatted_at", ASCENDING).limit(100)
        ids_to_delete = [doc["_id"] for doc in oldest]
        collection.delete_many({"_id": {"$in": ids_to_delete}})

    # Check if user exists
    if collection.find_one({"Phone_no": phone_no}):
        collection.update_one(
            {"Phone_no": phone_no},
            {
                "$push": {
                    "chat_history": {
                        "$each": chat_pair,
                        "$slice": -60
                    }
                },
                "$set": {
                    "last_chatted_at": now
                }
            }
        )
    else:
        new_user = {
            "Phone_no": phone_no,
            "name": name,
            "chat_history": chat_pair,
            "created_at": now,
            "last_chatted_at": now
        }
        collection.insert_one(new_user)

def retrieve_chat_history(phone_no: str):
    """
    Retrieves chat history in format:
    [HumanMessage(...), 'response', HumanMessage(...), 'response', ...]
    """
    doc = collection.find_one({"Phone_no": phone_no})
    if not doc:
        return []

    formatted_history = []
    for item in doc["chat_history"]:
        if item["role"] == "user":
            formatted_history.append(HumanMessage(content=item["content"]))
        elif item["role"] == "ai":
            formatted_history.append(item["content"])
    
    return formatted_history


