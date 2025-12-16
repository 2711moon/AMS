#migration.py

from models import assets_collection
from routes.main import safe_to_float, normalize_gst_keys

for asset in assets_collection.find({}):
    updated = False
    asset = normalize_gst_keys(asset)
    sanitized_asset = {}

    for key, value in asset.items():
        # MongoDB does not allow . in key names
        new_key = key.replace(".", "_").strip()
        # Convert numeric fields
        if new_key in ["amount", "total"] or new_key.startswith("gst_"):
            value = safe_to_float(value, 0.0)
        sanitized_asset[new_key] = value
        if sanitized_asset.get(new_key) != asset.get(key):
            updated = True

    if updated:
        assets_collection.update_one({"_id": asset["_id"]}, {"$set": sanitized_asset})
