import bcrypt
from app.db import get_database
db = get_database()
users_collection = db["Password_info"]
def verify_user(username, password):
    user = users_collection.find_one({"name": username})
    if not user:
        return False
    stored_password = user["password"]
    return bcrypt.checkpw(password.encode('utf-8'), stored_password)

def update_password(username,new_password):
    new_hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
    users_collection.update_one(
        {"name": username},
        {"$set": {"password": new_hashed}}
    )
    