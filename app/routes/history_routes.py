from flask import Blueprint, jsonify,request
import requests
from app.db import get_database
from bson import ObjectId
from app.services.User_login import verify_user
from app.config import Config
history_bp = Blueprint("history_bp", __name__)
db = get_database()
collection = db["Previous_chats"]

def serialize_doc(doc):
    doc['_id'] = str(doc['_id'])
    return doc

from datetime import datetime
from datetime import timezone
import pytz

def human_readable_duration(delta):
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return f"{seconds} seconds ago"
    elif seconds < 3600:
        return f"{seconds // 60} minutes ago"
    elif seconds < 86400:
        return f"{seconds // 3600} hours ago"
    else:
        return f"{seconds // 86400} days ago"

@history_bp.route("/", methods=["GET","POST"])
def get_all_chat_histories():
    # Get database and collection
    db = get_database()
    collection = db["Previous_chats"]

    # Fetch all documents from MongoDB
    all_chats = collection.find()

    # Format each document
    results = []
    for doc in all_chats:
        doc['_id'] = str(doc['_id'])  # Convert ObjectId to string for JSON
        created_at = doc.get("created_at")
        last_chatted_at = doc.get("last_chatted_at")
        now = datetime.now(pytz.timezone("Asia/Kolkata"))
         # Make last_chatted_at timezone-aware if it's naive
        if last_chatted_at and last_chatted_at.tzinfo is None:
            last_chatted_at = last_chatted_at.replace(tzinfo=timezone.utc).astimezone(pytz.timezone("Asia/Kolkata"))
        results.append({
            "Phone_no": doc.get("Phone_no"),
            "name": doc.get("name"),
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else None,
            "last_chatted_at": last_chatted_at.strftime("%Y-%m-%d %H:%M:%S") if last_chatted_at else None,
            "time_since_last_chat": human_readable_duration(now - last_chatted_at) if last_chatted_at else None,
            "chat_history": doc.get("chat_history", [])
        })

    return jsonify(results)
