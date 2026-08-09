import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

db = client["blast_radius"]

assets = db["assets"]
edges = db["edges"]
scenarios = db["scenarios"]
incidents = db["incidents"]
mitre = db["mitre"]
reports = db["reports"]


def check_connection():
    """Ask MongoDB to respond. Raises an error if it is not reachable."""
    client.admin.command("ping")
    return True