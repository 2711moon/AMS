#init_db.py

from pymongo import MongoClient
from getpass import getpass
from werkzeug.security import generate_password_hash

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["ams"]

# Collections
users_collection = db["users"]
asset_types_collection = db["asset_types"]

# Asset type field definitions
asset_type_fields = {
  "Mobile": [ 
    {"label": "Model", "name": "model", "type": "datalist", "options": ["abc", "def", "ghi", "jkl", "mno"]},
    {"label": "Date of Purchase", "name": "purchase_date", "type": "date"},
    {"label": "Vendor", "name": "vendor", "type": "datalist", "options": []},
    {"label": "RAM", "name": "ram", "type": "text"},
    {"label": "Storage", "name": "storage", "type": "text"},
    {"label": "IMEI-1", "name": "imei1", "type": "text"},
    {"label": "IMEI-2", "name": "imei2", "type": "text"},
    {"label": "Invoice No.", "name": "invoice_no", "type": "text"},
    {"label": "Amount", "name": "amount", "type": "number"},
    {"label": "GST (18%)", "name": "gst_18", "type": "number"},
    {"label": "Total", "name": "total", "type": "number"},
    {"label": "Given Date", "name": "given_date", "type": "date"},
    #{"label": "Username", "name": "username", "type": "text"}, REMOVE
    #{"label": "Employee code", "name": "employee_code", "type": "text"}, ADD
    #{"label": "Employee name", "name": "employee_name", "type": "text"}, ADD
    {"label": "Area", "name": "area", "type": "text"},
    {"label": "State", "name": "state", "type": "select"},
    {"label": "Status", "name": "status", "type": "select"},
    {"label": "Remarks", "name": "remarks", "type": "text"}
  ],

  "Barcode Scanner": [
    {"label": "Model", "name": "model", "type": "datalist", "options": ["abc", "def", "ghi", "jkl", "mno"]},  
    #{"label": "User Code", "name": "user_code", "type": "text"}, REMOVE (ASK IF NEEDED, IF THEY PUT THEIR OR ACCOUNTS TAG, OR JUST SERIAL NO. SUFFICES)
    #{"label": "IT Tag", "name": "IT_tag", "type": "text"}, ADD
    #{"label": "Accounts Tag", "name": "accounts_tag", "type": "text"}, ADD
    {"label": "Serial No.", "name": "serial_no", "type": "text"},
    #{"label": "Username", "name": "username", "type": "text"}, REMOVE
    #{"label": "Employee code", "name": "employee_code", "type": "text"}, ADD
    #{"label": "Employee name", "name": "employee_name", "type": "text"}, ADD
    {"label": "Given Date", "name": "given_date", "type": "date"},
    {"label": "Area", "name": "area", "type": "text"},
    {"label": "State", "name": "state", "type": "select"},
    {"label": "Vendor", "name": "vendor", "type": "datalist", "options": []},
    {"label": "Amount", "name": "amount", "type": "number"},
    {"label": "GST (18%)", "name": "gst_18", "type": "number"},
    {"label": "Total", "name": "total", "type": "number"},
    {"label": "Date of Purchase", "name": "purchase_date", "type": "date"},
    {"label": "Invoice No.", "name": "invoice_no", "type": "text"},
    {"label": "Send By", "name": "send_by", "type": "text"},
    {"label": "Status", "name": "status", "type": "select"},
    {"label": "Remarks", "name": "remarks", "type": "text"}
  ],

  "Face Machine": [
    {"label": "Model", "name": "model", "type": "text"},
    {"label": "Serial No.", "name": "serial_no", "type": "text"},
    {"label": "Date of Purchase", "name": "purchase_date", "type": "date"},
    {"label": "Vendor", "name": "vendor", "type": "datalist", "options": []},
    {"label": "Area", "name": "area", "type": "text"},
    {"label": "Amount", "name": "amount", "type": "number"},
    {"label": "GST (18%)", "name": "gst_18", "type": "number"},
    {"label": "Total", "name": "total", "type": "number"},
    {"label": "Status", "name": "status", "type": "select"},
    {"label": "Remarks", "name": "remarks", "type": "text"}
  ],

  "Franchise TAB": [
    {"label": "Model", "name": "model", "type": "text"},
    #{"label": "User Code", "name": "user_code", "type": "text"}, REMOVE (ASK IF NEEDED, IF THEY PUT THEIR OR ACCOUNTS TAG, OR JUST SERIAL NO. SUFFICES)
    #{"label": "IT Tag", "name": "IT_tag", "type": "text"}, ADD
    #{"label": "Accounts Tag", "name": "accounts_tag", "type": "text"}, ADD
    {"label": "Serial No.", "name": "serial_no", "type": "text"},
    {"label": "Date of Purchase", "name": "purchase_date", "type": "date"},
    {"label": "Vendor", "name": "vendor", "type": "datalist", "options": []},
    #{"label": "Employee code", "name": "employee_code", "type": "text"}, ADD
    #{"label": "Username", "name": "username", "type": "text"}, REMOVE  
    #{"label": "Employee name", "name": "employee_name", "type": "text"}, ADD
    {"label": "Given Date", "name": "given_date", "type": "date"},
    {"label": "Area", "name": "area", "type": "text"},
    {"label": "State", "name": "state", "type": "select"},
    {"label": "Invoice No.", "name": "invoice_no", "type": "text"},
    #{"label": "Send By", "name": "send_by", "type": "text"}, REMOVE
    #{"label": "Sent by", "name": "sent_by", "type": "text"}, ADD
    {"label": "Amount", "name": "amount", "type": "number"},
    {"label": "GST (18%)", "name": "gst_18", "type": "number"},
    {"label": "Total", "name": "total", "type": "number"},
    {"label": "Status", "name": "status", "type": "select"},
    {"label": "Remarks", "name": "remarks", "type": "text"}
  ],

  "Franchise Printer": [
    {"label": "Model", "name": "model", "type": "text"},
    #{"label": "User Code", "name": "user_code", "type": "text"}, REMOVE
    #{"label": "IT Tag", "name": "IT_tag", "type": "text"}, ADD
    #{"label": "Accounts Tag", "name": "accounts_tag", "type": "text"}, ADD
    #{"label": "Endpoint Name", "name": "endpoint_name", "type": "text"},REMOVE
    {"label": "Serial No.", "name": "serial_no", "type": "text"},
    {"label": "Date of Purchase", "name": "purchase_date", "type": "date"},
    {"label": "Vendor", "name": "vendor", "type": "datalist", "options": []},
    #{"label": "Employee code", "name": "employee_code", "type": "text"}, ADD
    #{"label": "Username", "name": "username", "type": "text"}, REMOVE
    #{"label": "Employee name", "name": "employee_name", "type": "text"}, ADD
    {"label": "Given Date", "name": "given_date", "type": "date"},
    {"label": "Area", "name": "area", "type": "text"},
    {"label": "State", "name": "state", "type": "select"},
    {"label": "Amount", "name": "amount", "type": "number"},
    {"label": "GST (18%)", "name": "gst_18", "type": "number"},
    {"label": "Total", "name": "total", "type": "number"},
    {"label": "Invoice No.", "name": "invoice_no", "type": "text"},
    {"label": "Send By", "name": "send_by", "type": "text"},
    {"label": "Status", "name": "status", "type": "select"},
    {"label": "Remarks", "name": "remarks", "type": "text"}
  ],
  
  "Franchise Inv": [
    #{"label": "User Code", "name": "user_code", "type": "text"}, REMOVE
    #{"label": "IT Tag", "name": "IT_tag", "type": "text"}, ADD
    #{"label": "Accounts Tag", "name": "accounts_tag", "type": "text"}, ADD
    {"label": "Endpoint Name", "name": "endpoint_name", "type": "text"},
    #{"label": "Employee code", "name": "employee_code", "type": "text"}, ADD
    #{"label": "Username", "name": "username", "type": "text"}, REMOVE
    #{"label": "Employee name", "name": "employee_name", "type": "text"}, ADD
    {"label": "Given Date", "name": "given_date", "type": "date"},
    {"label": "OS", "name": "os", "type": "datalist", "options": []},
    {"label": "System Model", "name": "system_model", "type": "datalist", "options": []},
    {"label": "System Manufacturer", "name": "system_manufacturer", "type": "datalist", "options": []},
    {"label": "Serial No. ", "name": "serial_no", "type": "text"},
    {"label": "Processor", "name": "processor", "type": "text"},
    {"label": "RAM", "name": "ram", "type": "text"},
    {"label": "HDD Size", "name": "hdd", "type": "text"},
    {"label": "Received", "name": "received", "type": "text"},
    {"label": "Vendor", "name": "vendor", "type": "datalist", "options": []},
    {"label": "Invoice No.", "name": "invoice_no", "type": "text"},
    {"label": "Amount", "name": "amount", "type": "number"},
    {"label": "GST (18%)", "name": "gst_18", "type": "number"},
    {"label": "Total", "name": "total", "type": "number"},
    {"label": "Status", "name": "status", "type": "select"},
    {"label": "Remarks", "name": "remarks", "type": "text"}
  ],

  "Laptop": [
    #{"label": "Current User Code", "name": "user_code", "type": "text"}, REMOVE
    #{"label": "Employee code", "name": "employee_code", "type": "text"}, ADD
    #{"label": "Username", "name": "username", "type": "text"}, REMOVE
    #{"label": "Employee name", "name": "employee_name", "type": "text"}, ADD
    {"label": "Given Date", "name": "given_date", "type": "date"},
    {"label": "Serial No.", "name": "serial_no", "type": "text"},
    #{"label": "Asset Tag", "name": "asset_tag", "type": "text"}, REMOVE
    #{"label": "IT Tag", "name": "IT_tag", "type": "text"}, ADD
    #{"label": "Accounts Tag", "name": "accounts_tag", "type": "text"}, ADD
    #{"label": "Endpoint Name", "name": "endpoint_name", "type": "text"}, REMOVE (ASK ABOUT IT)
    {"label": "Date of Purchase", "name": "purchase_date", "type": "date"},
    {"label": "Vendor", "name": "vendor", "type": "datalist", "options": []},
    {"label": "License", "name": "license", "type": "text"},
    {"label": "OS", "name": "os", "type": "datalist", "options": []},
    {"label": "System Model", "name": "system_model", "type": "datalist", "options": []},
    {"label": "System Manufacturer", "name": "system_manufacturer", "type": "datalist", "options": []},
    {"label": "Processor", "name": "processor", "type": "text"},
    {"label": "RAM", "name": "ram", "type": "text"},
    {"label": "HDD Size", "name": "hdd", "type": "text"},
    {"label": "Free Space", "name": "free_space", "type": "text"},
    {"label": "Invoice No.", "name": "invoice_no", "type": "text"},
    {"label": "Amount", "name": "amount", "type": "number"},
    {"label": "GST (18%)", "name": "gst_18", "type": "number"},
    {"label": "Total", "name": "total", "type": "number"},
    {"label": "Received on Approval", "name": "received_on_approval", "type": "text"},
    {"label": "Status", "name": "status", "type": "select"},
    {"label": "Remarks", "name": "remarks", "type": "text"}
  ],

  "IP Phones": [
    {"label": "Model", "name": "model", "type": "datalist", "options": ["abc", "def", "ghi", "jkl", "mno"]},
    {"label": "Serial No.", "name": "serial_no", "type": "text"},
    {"label": "Date of Purchase", "name": "purchase_date", "type": "date"},
    {"label": "Area", "name": "Area", "type": "text"},
    {"label": "Courier by", "name": "courier_by", "type": "text"},
    {"label": "Amount", "name": "amount", "type": "number"},
    {"label": "GST (18%)", "name": "gst_18", "type": "number"},
    {"label": "Total", "name": "total", "type": "number"},
    {"label": "Status", "name": "status", "type": "select"},
    {"label": "Remarks", "name": "remarks", "type": "text"}
  ],

  "Printer": [
    {"label": "Model", "name": "model", "type": "text"},
    #{"label": "User Code", "name": "user_code", "type": "text"}, REMOVE
    #{"label": "IT Tag", "name": "IT_tag", "type": "text"}, ADD
    #{"label": "Accounts Tag", "name": "accounts_tag", "type": "text"}, ADD
    #{"label": "Asset Tag", "name": "asset_tag", "type": "text"}, REMOVE
    #{"label": "Endpoint name", "name": "endpoint_name", "type": "text"}, REMOVE  (ASK ABOUT IT)
    {"label": "Date of Purchase", "name": "purchase_date", "type": "date"},
    {"label": "Vendor", "name": "vendor", "type": "datalist", "options": []},
    {"label": "Serial No.", "name": "serial_no", "type": "text"},
    #{"label": "Username", "name": "username", "type": "text"}, REMOVE
    #{"label": "Employee code", "name": "employee_code", "type": "text"}, ADD
    #{"label": "Employee name", "name": "employee_name", "type": "text"}, ADD
    {"label": "Given Date", "name": "given_date", "type": "date"},
    {"label": "Domain", "name": "domain", "type": "text"},
    {"label": "IP Address", "name": "ip_address", "type": "text"},
    {"label": "Invoice No.", "name": "invoice_no", "type": "text"},
    {"label": "Amount", "name": "amount", "type": "number"},
    {"label": "GST (18%)", "name": "gst_18", "type": "number"},
    {"label": "Total", "name": "total", "type": "number"},
    {"label": "Status", "name": "status", "type": "select"},
    {"label": "Remarks", "name": "remarks", "type": "text"}
  ],

  "Desktop": [
    #{"label": "Asset Tag (CPU)", "name": "cpu_asset_tag", "type": "text"},
    #{"label": "IT Tag (CPU)", "name": "IT_tagC", "type": "text"}, ADD
    #{"label": "Accounts Tag (CPU)", "name": "accounts_tagC", "type": "text"}, ADD
    #{"label": "Endpoint name", "name": "endpoint_name", "type": "text"},
    #{"label": "Username", "name": "username", "type": "text"}, REMOVE
    #{"label": "Employee code", "name": "employee_code", "type": "text"}, ADD
    #{"label": "Employee name", "name": "employee_name", "type": "text"}, ADD
    {"label": "Domain", "name": "domain", "type": "text"},
    {"label": "OS", "name": "os", "type": "datalist", "options": []},
    {"label": "System Model", "name": "system_model", "type": "datalist", "options": []},
    {"label": "System Manufacturer", "name": "system_manufacturer", "type": "datalist", "options": []},
    {"label": "Main circuit board", "name": "main_circuit_board", "type": "text"},
    {"label": "Processor", "name": "processor", "type": "text"},
    {"label": "RAM", "name": "ram", "type": "text"},
    {"label": "HDD Size", "name": "hdd", "type": "text"},
    #{"label": "MTR Asset Tag", "name": "mtr_asset_tag", "type": "text"}, REMOVE
    #{"label": "Asset Tag (Monitor)", "name": "monitor_asset_tag", "type": "text"}, REMOVE
    #{"label": "IT Tag (MTR)", "name": "IT_tagM", "type": "text"}, ADD
    #{"label": "Accounts Tag (MTR)", "name": "accounts_tagM", "type": "text"}, ADD
    {"label": "Monitor Make", "name": "monitor_make", "type": "text"},
    {"label": "Serial No.", "name": "serial_no", "type": "text"},
    {"label": "Year", "name": "year", "type": "text"},
    {"label": "Vendor", "name": "vendor", "type": "datalist", "options": []},
    {"label": "Date of Purchase", "name": "purchase_date", "type": "date"},
    {"label": "Invoice No.", "name": "invoice_no", "type": "text"},
    {"label": "Amount", "name": "amount", "type": "number"},
    {"label": "GST (18%)", "name": "gst_18", "type": "number"},
    {"label": "Total", "name": "total", "type": "number"},
    {"label": "Given Date", "name": "given_date", "type": "date"},
    {"label": "Status", "name": "status", "type": "select"},
    {"label": "Remarks", "name": "remarks", "type": "text"}
  ],

  "All-in-one": [
  #  {"label": "User Code", "name": "user_code", "type": "text"},
  #{"label": "Employee code", "name": "employee_code", "type": "text"}, ADD

  # {"label": "Asset Tag", "name": "asset_tag", "type": "text"},
  # {"label": "Endpoint name", "name": "endpoint_name", "type": "text"},
    {"label": "Date of Purchase", "name": "purchase_date", "type": "date"},
    {"label": "Vendor", "name": "vendor", "type": "datalist", "options": []},
  # {"label": "Username", "name": "username", "type": "text"},
   {"label": "Given Date", "name": "given_date", "type": "date"},
   {"label": "Domain", "name": "domain", "type": "text"},
   {"label": "IP Address", "name": "ip_address", "type": "text"},
   {"label": "OS", "name": "os", "type": "text"},
   {"label": "System Model", "name": "system_model", "type": "text"},
   {"label": "System Manufacturer", "name": "system_manufacturer", "type": "text"},
   {"label": "Main circuit board", "name": "main_circuit_board", "type": "text"},
   {"label": "Processor", "name": "processor", "type": "text"},
   {"label": "RAM", "name": "ram", "type": "text"},
   {"label": "Total Hard Disk Size", "name": "hdd", "type": "text"},
   {"label": "Invoice No.", "name": "invoice_no", "type": "text"},
   {"label": "Amount", "name": "amount", "type": "number"},
   {"label": "GST (18%)", "name": "gst_18", "type": "number"},
   {"label": "Total", "name": "total", "type": "number"},
   {"label": "Status", "name": "status", "type": "select"},
   {"label": "Remarks", "name": "remarks", "type": "text"}
  ],

  "Mouse": [
    {"label": "Model", "name": "model", "type": "text"},
    {"label": "Date of Purchase", "name": "purchase_date", "type": "date"},
    {"label": "Vendor", "name": "vendor", "type": "datalist", "options": []},
    {"label": "Serial No.", "name": "serial_no", "type": "text"},
    #{"label": "Username", "name": "username", "type": "text"}, REMOVE
    #{"label": "Employee code", "name": "Employee_code", "type": "text"}, ADD
    #{"label": "Employee name", "name": "employee_name", "type": "text"}, ADD
    {"label": "Given Date", "name": "given_date", "type": "date"},
    {"label": "Area", "name": "area", "type": "text"},
    {"label": "State", "name": "state", "type": "select"},
    {"label": "Invoice No.", "name": "invoice_no", "type": "text"},
    {"label": "Amount", "name": "amount", "type": "number"},
    {"label": "GST (18%)", "name": "gst_18", "type": "number"},
    {"label": "Total", "name": "total", "type": "number"},
    {"label": "Status", "name": "status", "type": "select"},
    {"label": "Remarks", "name": "remarks", "type": "text"}
  ],

  "KBD": [
    {"label": "Model", "name": "model", "type": "text"},
    {"label": "Date of Purchase", "name": "purchase_date", "type": "date"},
    {"label": "Vendor", "name": "vendor", "type": "datalist", "options": []},
    {"label": "Serial No.", "name": "serial_no", "type": "text"},
    #{"label": "Username", "name": "username", "type": "text"}, REMOVE
    #{"label": "Employee code", "name": "Employee_code", "type": "text"}, ADD
    #{"label": "Employee name", "name": "employee_name", "type": "text"}, ADD
    {"label": "Given Date", "name": "given_date", "type": "date"},
    {"label": "Area", "name": "area", "type": "text"},
    {"label": "State", "name": "state", "type": "select"},
    {"label": "Invoice No.", "name": "invoice_no", "type": "text"},
    {"label": "Amount", "name": "amount", "type": "number"},
    {"label": "GST (18%)", "name": "gst_18", "type": "number"},
    {"label": "Total", "name": "total", "type": "number"},
    {"label": "Status", "name": "status", "type": "select"},
    {"label": "Remarks", "name": "remarks", "type": "text"}
  ],

  "HDD": [
    {"label": "Model", "name": "model", "type": "text"},
    {"label": "HDD Type", "name": "hdd_type", "type": "datalist", "options": []},
    {"label": "Date of Purchase", "name": "purchase_date", "type": "date"},
    {"label": "Vendor", "name": "vendor", "type": "datalist", "options": []},
    {"label": "Serial No.", "name": "serial_no", "type": "text"},
    #{"label": "Username", "name": "username", "type": "text"}, REMOVE
    #{"label": "Employee code", "name": "Employee_code", "type": "text"}, ADD
    #{"label": "Employee name", "name": "employee_name", "type": "text"}, ADD
    {"label": "Given Date", "name": "given_date", "type": "date"},
    {"label": "Area", "name": "area", "type": "text"},
    {"label": "State", "name": "state", "type": "select"},
    {"label": "Invoice No.", "name": "invoice_no", "type": "text"},
    {"label": "Amount", "name": "amount", "type": "number"},
    {"label": "GST (18%)", "name": "gst_18", "type": "number"},
    {"label": "Total", "name": "total", "type": "number"},
    {"label": "Status", "name": "status", "type": "select"},
    {"label": "Remarks", "name": "remarks", "type": "text"}
  ],

  "Battery": [
    {"label": "Model", "name": "model", "type": "text"},
    {"label": "Battery Type", "name": "battery_type", "type": "datalist", "options": []},
    {"label": "Date of Purchase", "name": "purchase_date", "type": "date"},
    {"label": "Vendor", "name": "vendor", "type": "datalist", "options": []},
    {"label": "Serial No.", "name": "serial_no", "type": "text"},
    #{"label": "Username", "name": "username", "type": "text"}, REMOVE
    #{"label": "Employee code", "name": "Employee_code", "type": "text"}, ADD
    #{"label": "Employee name", "name": "employee_name", "type": "text"}, ADD
    {"label": "Given Date", "name": "given_date", "type": "date"},
    {"label": "Area", "name": "area", "type": "text"},
    {"label": "State", "name": "state", "type": "select"},
    {"label": "Invoice No.", "name": "invoice_no", "type": "text"},
    {"label": "Amount", "name": "amount", "type": "number"},
    {"label": "GST (28%)", "name": "gst_28", "type": "number"},
    {"label": "Total", "name": "total", "type": "number"},
    {"label": "Status", "name": "status", "type": "select"},
    {"label": "Remarks", "name": "remarks", "type": "text"}
  ]
}

# Insert asset types into DB if not already present
for asset_type, fields in asset_type_fields.items():
    if not asset_types_collection.find_one({"type_name": asset_type}):
        asset_types_collection.insert_one({"type_name": asset_type, "fields": fields})

print("\n✅ Asset types initialized successfully.")

# Admin setup (safe interactive)
if users_collection.count_documents({}) == 0:
    print("\n--- Admin Setup ---")
    username = input("Enter admin username: ").strip().lower()
    password = getpass("Enter admin password: ")
    hashed_password = generate_password_hash(password)
    users_collection.insert_one({"username": username, "password": hashed_password})
    print("\n✅ Admin user created successfully.")
else:
    print("\nℹ️ Admin user(s) already exists. Skipping user creation.")
