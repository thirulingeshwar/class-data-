from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)

MONGO_URI = "mongodb+srv://thirulingeshwart_db_user:NYzO4OoXyz23gSiI@cluster0.vgmryb8.mongodb.net/?appName=Cluster0"
client = MongoClient(
    MONGO_URI,
    tls=True,
    serverSelectionTimeoutMS=5000
)

client.admin.command("ping")
print("MongoDB Connected 🚀")