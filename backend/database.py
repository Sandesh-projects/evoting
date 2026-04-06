from pymongo import MongoClient, ASCENDING

# 🔌 Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["evoting_db"]
users_collection = db["users"]

# 🔒 Security Enhancement: Create Unique Indexes
# This ensures that no two users can have the same Aadhaar or Email at the database level.
users_collection.create_index([("aadhaar_hash", ASCENDING)], unique=True)
users_collection.create_index([("email", ASCENDING)], unique=True)

print("✅ MongoDB Connected and Indexes Verified")