import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Reads the .env file and loads MONGO_URI into the environment
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# serverSelectionTimeoutMS stops it hanging forever if MongoDB is not running
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

db = client["blast_radius"]

# The six collections. Every other file imports these from here.
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