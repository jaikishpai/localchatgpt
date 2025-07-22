import os
from pymongo import MongoClient
from datetime import datetime
from passlib.context import CryptContext

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = "localchatgpt"
COLLECTION_NAME = "chat_cache"
USERS_COLLECTION = "users"

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
users_collection = db[USERS_COLLECTION]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_cached_response(user: str, message: str):
    doc = collection.find_one({"user": user, "message": message})
    if doc:
        return doc.get("response"), doc.get("context")
    return None, None

def cache_response(user: str, message: str, response: str, context: str):
    collection.insert_one({
        "user": user,
        "message": message,
        "response": response,
        "context": context,
        "timestamp": datetime.utcnow()
    })

def create_user(username: str, password: str):
    if users_collection.find_one({"username": username}):
        return False  # User already exists
    hashed_pw = pwd_context.hash(password)
    users_collection.insert_one({"username": username, "password": hashed_pw})
    return True

def verify_user(username: str, password: str):
    user = users_collection.find_one({"username": username})
    if not user:
        return False
    return pwd_context.verify(password, user["password"])

def get_user(username: str):
    return users_collection.find_one({"username": username}) 