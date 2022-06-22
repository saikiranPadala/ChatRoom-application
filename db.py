from pymongo import MongoClient
from werkzeug.security import generate_password_hash

client = MongoClient("mongodb+srv://test:test@cluster0.niit6.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
chat_db = client.get_database("ChatDB")
users_collection = chat_db.get_collection("users")
db = client.database


def save_user(username, email, password):
    users_collection.insert_one({'_id': username, 'email': email, 'password': password})


save_user("sai", "sai@123", "sam")
