import os
import redis as redis_py
from pymongo import MongoClient
from dotenv import load_dotenv

try:
    print("Loading environment vars")
    load_dotenv()
    print("Loaded environment vars\n")
except Exception as e:
    print(f"Error loading environment vars: {e}")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:password@localhost:27017")

# REDIS_HOST = os.getenv("REDIS_HOST", "redis-master.redis.svc.cluster.local")
# REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
# REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "password")

try:
    client = MongoClient(MONGO_URI)
    db = client["main"]
    db_users = db["users"]
    
    print("Connected to MongoDB: ", client)

    # Connect to Redis (use environment variable or secrets for password)
    # redis = redis_py.Redis(
    #     host=REDIS_HOST,
    #     port=REDIS_PORT,
    #     password=REDIS_PASSWORD,
    #     decode_responses=True  # Automatically decode UTF-8
    # )
    # print("Connected to Redis: ", redis)

except Exception as e:
    print(f"An error occurred: {e}")