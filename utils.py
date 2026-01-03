#UTILS.PY
from models import asset_types_collection
from bson import ObjectId
from datetime import datetime

#def serialize_asset(asset):
#    def safe(val):
#        if isinstance(val, ObjectId):
#            return str(val)
#        elif isinstance(val, datetime):
#            return val.strftime("%Y-%m-%d")
#        return val
#
#    return {k: safe(v) for k, v in asset.items()}
def normalize_cell(val):
    if isinstance(val, datetime):
        return val.strftime("%Y-%m-%d")
    return str(val).strip() if val is not None else ""

def get_date_fields(schema=None):
    if schema is None:
        schema = get_master_fields()
    return [f["name"] for f in schema if f["type"] == "date"]

def is_valid_date(val):
    try:
        datetime.strptime(val, "%Y-%m-%d")
        return True
    except:
        return False

def is_future_date(val):
    try:
        return datetime.strptime(val, "%Y-%m-%d") > datetime.now()
    except:
        return False

def is_valid_year(val):
    return val.isdigit() and len(val) == 4 and 1900 <= int(val) <= datetime.now().year

def get_field_type(name, schema=None):
    if schema is None:
        schema = get_master_fields()
    for f in schema:
        if f["name"] == name:
            return f["type"]
    return None

def matches_search(asset, search_term):
    if not search_term:
        return True

    search_term = search_term.lower()
    for field in get_master_fields():
        name = field["name"]
        value = asset.get(name)
        if isinstance(value, (str, int, float)) and search_term in str(value).lower():
            return True
    return False

def normalize_asset_data(data):
    return {
        'name': data.get('name', '').strip().title(),
        'category': data.get('category', '').strip().lower(),
        'owner': data.get('owner', '').strip(),
        'status':    data.get('status', 'available').strip(),
    }

def normalize_imported_asset(asset):
    """
    Maps imported asset keys/labels to DB field names using master fields.
    Ensures all master fields exist in the returned dict.
    """
    # Build a mapping from label → name from master fields
    label_to_name = {f["label"]: f["name"] for f in get_master_fields()}

    normalized = {}
    for field in get_master_fields():
        name = field["name"]
        # Check if asset has the key directly, else try matching by label
        normalized[name] = asset.get(name) or asset.get(next((lbl for lbl, n in label_to_name.items() if n == name), ""), "")
    
    return normalized

def get_all_existing_types():
    return sorted(
        [doc["type_name"] for doc in asset_types_collection.find({}, {"type_name": 1})]
    )

def get_fields_for_type(asset_type):
    doc = asset_types_collection.find_one({"type_name": asset_type})
    return doc["fields"] if doc and "fields" in doc else None

def get_asset_statuses():
    return ["Available(p)", "Available(g)", "Assigned(p)", "Assigned(g)", "Repair/Faulty", "Discard"]

def get_master_fields():
    return[
        {"label": "Previous Employee", "name": "prev_emp", "type": "text"},
        {"label": "Username", "name": "username", "type": "text"},
        {"label": "Previous Employee Code", "name": "prev_emp_code", "type": "text"},
        {"label": "User Code", "name": "user_code", "type": "text"},
        {"label": "Area of Collection", "name": "area_of_collection", "type": "text"},
        {"label": "Area", "name": "area", "type": "text"},
        {"label": "State", "name": "state", "type": "select", "options": get_indian_states()},  
        {"label": "Amount", "name": "amount", "type": "number"},
        {"label": "GST (18%)", "name": "gst_18", "type": "number"},
        {"label": "GST (22%)", "name": "gst_22", "type": "number"},
        {"label": "GST (28%)", "name": "gst_28", "type": "number"}, 
        {"label": "Total", "name": "total", "type": "number"},
        {"label": "Date of Purchase", "name": "purchase_date", "type": "date"},
        {"label": "Previous Given Date", "name": "prev_given_date", "type": "date"},
        {"label": "Given Date", "name": "given_date", "type": "date"},
        {"label": "Collected Date", "name": "collected_date", "type": "date"},
        {"label": "Year", "name": "year", "type": "text"},
        {"label": "Status", "name": "status", "type": "select", "options": get_asset_statuses()},
        {"label": "Remarks", "name": "remarks", "type": "text"},
        {"label": "Invoice No.", "name": "invoice_no", "type": "text"},
        {"label": "Vendor", "name": "vendor", "type": "datalist", "options": []},
        {"label": "License", "name": "license", "type": "text"},
        {"label": "Asset Tag", "name": "asset_tag", "type": "text"},
        {"label": "Serial No.", "name": "serial_no", "type": "text"},
        {"label": "OS", "name": "os", "type": "datalist", "options": []},
        {"label": "Model", "name": "model", "type": "datalist", "options": []},
        {"label": "System Manufacturer", "name": "system_manufacturer", "type": "datalist", "options": []},        
        {"label": "Domain", "name": "domain", "type": "text"},
        {"label": "IP Address", "name": "ip_address", "type": "text"},
        {"label": "Processor", "name": "processor", "type": "text"},
        {"label": "RAM", "name": "ram", "type": "text"},
        {"label": "Courier by", "name": "courier_by", "type": "text"},
        {"label": "HDD Size", "name": "hdd", "type": "text"},
        {"label": "Endpoint Name", "name": "endpoint_name", "type": "text"},
        {"label": "Received on Approval", "name": "received_on_approval", "type": "text"},
        {"label": "Storage", "name": "storage", "type": "text"},
        {"label": "IMEI-1", "name": "imei1", "type": "text"},
        {"label": "IMEI-2", "name": "imei2", "type": "text"},
        {"label": "IT Tag", "name": "it_tag", "type": "text"}, #ADD
        {"label": "Accounts Tag", "name": "accounts_tag", "type": "text"}, #ADD
        {"label": "Employee code", "name": "employee_code", "type": "text"}, #ADD
        {"label": "Employee name", "name": "employee_name", "type": "text"}, #ADD
        {"label": "Sent by", "name": "send_by", "type": "text"},  
        {"label": "System Model", "name": "system_model", "type": "datalist", "options": []},
        {"label": "Received", "name": "received", "type": "text"},
        {"label": "Asset Tag (CPU)", "name": "cpu_asset_tag", "type": "text"},
        {"label": "IT Tag (CPU)", "name": "IT_tagC", "type": "text"}, #ADD
        {"label": "Accounts Tag (CPU)", "name": "accounts_tagC", "type": "text"}, #ADD      
        {"label": "Main circuit board", "name": "main_circuit_board", "type": "text"},
        {"label": "MTR Asset Tag", "name": "mtr_asset_tag", "type": "text"}, #REMOVE
        {"label": "Asset Tag (Monitor)", "name": "monitor_asset_tag", "type": "text"}, #REMOVE
        {"label": "IT Tag (MTR)", "name": "IT_tagM", "type": "text"}, #ADD
        {"label": "Accounts Tag (MTR)", "name": "accounts_tagM", "type": "text"}, #ADD
        {"label": "Monitor Make", "name": "monitor_make", "type": "text"},
        {"label": "Total Hard Disk Size", "name": "hdd", "type": "text"},
        {"label": "HDD Type", "name": "hdd_type", "type": "datalist", "options": []},
        {"label": "Battery Type", "name": "battery_type", "type": "datalist", "options": []}  
    ]

def get_indian_states():
    return [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
        "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
        "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
        "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
        "Uttar Pradesh", "Uttarakhand", "West Bengal",
        "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
        "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
    ]

def filter_form_fields(form_data, allowed_fields):
    """
    Returns only fields that are explicitly allowed.
    Skips unrelated/null/default fields.
    """
    return {k: v for k, v in form_data.items() if k in allowed_fields}

def fill_missing_asset_fields(data):
    enriched = data.copy()
    enriched.setdefault('remarks', '')
    enriched.setdefault('status', 'available')
    return enriched
