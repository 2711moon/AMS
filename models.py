#models.py
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

client = MongoClient('mongodb://localhost:27017/')
db = client['ams']

users_collection = db['users']
assets_collection = db['assets']
asset_types_collection = db['asset_types']
import_previews_collection = db['import_previews']

# --- TTL Index for auto-expiring import previews ---
# Will auto-delete after 2 hours (7200 seconds)
import_previews_collection.create_index(
    "created_at",
    expireAfterSeconds=7200
)
