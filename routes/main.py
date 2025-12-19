#routes/main.py
from flask import Blueprint, request, render_template, session, redirect, url_for, flash, jsonify, send_from_directory
from bson.objectid import ObjectId
from datetime import datetime, date
from models import assets_collection, asset_types_collection
from forms import AssetForm
from extensions import csrf, format_inr
import re
from utils import normalize_asset_data, get_master_fields, get_indian_states, get_all_existing_types, normalize_imported_asset


main_bp = Blueprint('main', __name__)

def parse_ddmmyyyy_to_date(val):
    try:
        return datetime.strptime(val.strip(), "%d-%m-%Y") if val else None
    except Exception:
        return None
    
def safe_to_float(v, default=0.0):
    """Robustly convert values like '₹1,23,456.78', '1,23,456.78', 'None', None -> float."""
    if v is None:
        return default
    s = str(v).strip()
    if s.lower() == "none" or s == "":
        return default
    s = s.replace("₹", "").replace(",", "")
    try:
        return float(s)
    except Exception:
        return default

def format_inr_no_symbol(value):
    """Indian-format number string without the rupee symbol (for edit inputs)."""
    try:
        value = safe_to_float(value, 0.0)
        integer, dot, fraction = f"{value:.2f}".partition(".")
        last3 = integer[-3:]
        rest = integer[:-3]
        if rest:
            rest = ",".join([rest[max(i-2, 0):i] for i in range(len(rest), 0, -2)][::-1])
            formatted = rest + "," + last3
        else:
            formatted = last3
        return f"{formatted}.{fraction}"
    except Exception:
        return str(value)
    
@main_bp.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('public/assets', filename)

@main_bp.route('/')
def landing():
    return render_template('landing.html')

@main_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    raw_assets = list(assets_collection.find())
    asset_types = list(asset_types_collection.find())

    assets = []
    for asset in raw_assets:
        asset_copy = asset.copy()
        category = asset.get("category", "")
        type_match = next((t for t in asset_types if t.get("type_name", "").lower() == category.lower()), None)
        asset_copy["type_name"] = type_match["type_name"] if type_match else category
        asset_copy["_id"] = str(asset_copy["_id"])

        # Optionally normalize imported fields
        # For example, if imported asset has "Given Date", map it to "given_date"
        for field in get_master_fields():
            key = field["name"]
            label = field["label"]
            if key not in asset_copy and label in asset_copy:
                asset_copy[key] = asset_copy[label]

        assets.append(asset_copy)

    return render_template('dashboard.html', assets=assets)

@main_bp.route("/create_type", methods=["POST"])
def create_type():
    try:
        data = request.get_json(force=True)
        print("📥 Raw payload received:", data)

        if not isinstance(data, dict):
            print("❌ Payload is not a dictionary")
            return jsonify(success=False, message="Invalid payload format."), 400

        type_name = data.get("type")
        fields = data.get("fields")

        print("📥 type_name:", type_name)
        print("📥 fields:", fields)

        if not type_name or not isinstance(fields, list) or len(fields) == 0:
            print("❌ Missing or invalid type/fields")
            return jsonify(success=False, message="Type name and fields are required."), 400

        for field in fields:
            if not isinstance(field, dict):
                print("❌ Field is not a dictionary:", field)
                return jsonify(success=False, message="Each field must be an object."), 400
            if "name" not in field or "label" not in field or "type" not in field:
                print("❌ Field missing required keys:", field)
                return jsonify(success=False, message="Each field must have 'name', 'label', and 'type'."), 400

        if asset_types_collection.find_one({"type_name": type_name}):
            print("⚠️ Type already exists:", type_name)
            return jsonify(success=False, message="Type already exists."), 409

        asset_types_collection.insert_one({
            "type_name": type_name,
            "fields": fields
        })

        print("✅ Type saved successfully:", type_name)
        return jsonify(success=True, message="Type created successfully.")

    except Exception as e:
        print("🔥 Exception occurred:", str(e))
        return jsonify(success=False, message="Server error."), 500

@main_bp.route('/get_asset_types')
def get_asset_types():
    types = asset_types_collection.find({}, {"_id": 0, "type_name": 1})
    return jsonify([doc["type_name"] for doc in types])

@main_bp.route('/get_fields/<asset_type>')
def get_fields(asset_type):
    config = asset_types_collection.find_one({'type_name': asset_type})
    if config and 'fields' in config:
        fields = config["fields"]

        status_options = ["Available(p)", "Available(g)", "Assigned(p)", "Assigned(g)", "Repair/Faulty", "Discard"]    

        for field in fields:
            if field.get("name", "").lower() == "state" and field.get("type") == "select":
                if not field.get("options"):
                    field["options"] = get_indian_states()

            if field.get("name", "").lower() == "status" and field.get("type") == "select":
                if not field.get("options"):
                    field["options"] = status_options

        return jsonify({"fields": fields})

    # ✅ Always return fields key to avoid frontend error
    return jsonify({"fields": []})


@main_bp.route("/get_master_fields")
def get_master_fields_api():
    return jsonify({"fields": get_master_fields()})

@csrf.exempt
@main_bp.route("/filter_assets", methods=["POST"])
def filter_assets():
    search = request.form.get("search", "").strip().lower()
    sort = request.form.get("sort", "").strip()

    def normalize(val):
        """Convert values to lowercase strings for searching."""
        if val is None:
            return ""
        if isinstance(val, (datetime, date)):
            return val.strftime("%d-%m-%Y").lower()
        return str(val).replace(",", "").replace("₹", "").replace("INR", "").replace("USD", "").strip().lower()

    def format_display(val):
        """Convert values for display in JSON output."""
        if val in [None, ""]:
            return "—"
        if isinstance(val, (datetime, date)):
            return val.strftime("%d-%m-%Y")
        return str(val)

    field_configs = get_master_fields()
    assets = list(assets_collection.find())
    asset_types = list(asset_types_collection.find())

    # ---------- SEARCH ----------
    if search:
        matched_assets = []
        for asset in assets:
            matched = False
            category = asset.get("category", "")
            type_match = next((t for t in asset_types if t.get("type_name", "").lower() == category.lower()), None)

            # Match against master fields
            for field in field_configs:
                key = field.get("name")
                if normalize(search) in normalize(asset.get(key)):
                    matched = True
                    break

            # Match against all fields except _id
            if not matched:
                for key, value in asset.items():
                    if key == "_id":
                        continue
                    if normalize(search) in normalize(value):
                        matched = True
                        break

            # Match against category
            if not matched and normalize(search) in normalize(category):
                matched = True

            # Match against type_name
            if not matched and type_match and normalize(search) in normalize(type_match.get("type_name", "")):
                matched = True

            # Match against labels in type fields
            if not matched and type_match:
                for field in type_match.get("fields", []):
                    if normalize(search) in normalize(field.get("label", "")):
                        matched = True
                        break

            if matched:
                matched_assets.append(asset)
    else:
        matched_assets = assets

    # ---------- FORMAT FOR CLIENT ----------
    results = []
    for asset in matched_assets:
        result = {"_id": str(asset["_id"])}
        for key, value in asset.items():
            result[key] = format_display(value)

        category = asset.get("category", "")
        type_match = next((t for t in asset_types if t.get("type_name", "").lower() == category.lower()), None)
        if type_match:
            result["type_name"] = type_match.get("type_name", category)

        results.append(result)

    # ---------- SORT ----------
    if sort:
        key, direction = sort.rsplit("_", 1)
        reverse = direction == "desc"

        def parse_date(val):
            if not val or val == "—":
                return datetime.min
            for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
                try:
                    return datetime.strptime(str(val), fmt)
                except Exception:
                    pass
            return datetime.min

        def parse_currency(val):
            if not val or val == "—":
                return 0
            try:
                return float(str(val).replace(",", "").replace("₹", "").replace("INR", "").replace("USD", "").strip())
            except Exception:
                return 0

        def sort_key(asset):
            val = asset.get(key, "")
            if "date" in key:
                return parse_date(val)
            if any(x in key for x in ("price", "cost", "amount", "value", "total", "gst")):
                return parse_currency(val)
            return str(val).lower()

        results.sort(key=sort_key, reverse=reverse)

    return jsonify(results)

@main_bp.route("/create_asset", methods=["GET", "POST"])
def create_asset():
    form = AssetForm()

    if request.method == "POST":
        raw_data = request.form.copy()
        raw_data.pop("csrf_token", None)
        raw_data.pop("submit", None)

        selected_type = raw_data.get("category", "")
        new_type = raw_data.get("new_type", "").strip()
        is_new_type = selected_type == "add_new_type" and new_type

        if is_new_type:
            selected_type = new_type
            raw_data["category"] = new_type

            # Parse selected features
            predefined_fields_raw = request.form.get("selected_features", "")
            predefined_fields = [f.strip() for f in predefined_fields_raw.split(",") if f.strip()]

            # Combine field list
            master_fields = get_master_fields()
            full_predefined = [f for f in master_fields if f["name"] in predefined_fields]

            # Save the new type to DB
            asset_types_collection.update_one(
                {"type_name": new_type},
                {"$set": {"fields": full_predefined}},
                upsert=True
            )

        # ✅ Fetch config AFTER type is saved
        if is_new_type:
            fields_to_render = full_predefined
        else:
            selected_config = asset_types_collection.find_one({"type_name": selected_type})
            fields_to_render = selected_config["fields"] if selected_config else []

        allowed_fields = [f["name"] for f in fields_to_render]

        for field in ["given_date", "purchase_date", "collected_date", "prev_given_date"]:
            date_str = raw_data.get(field, "")
            parsed_date = parse_ddmmyyyy_to_date(date_str.strip()) if date_str.strip() else None
            if parsed_date:
                raw_data[field] = parsed_date.strftime("%d-%m-%Y")
            else:
                raw_data[field] = date_str

        for money_field in ["amount", "total"]:
            if raw_data.get(money_field):
                raw_data[money_field] = raw_data[money_field].replace("₹", "").replace(",", "")

        normalized = normalize_asset_data(raw_data)
        raw_data.update(normalized)

        payload = {}
        for field_name in allowed_fields:
            value = raw_data.get(field_name, "")
            if isinstance(value, datetime):
                value = value.strftime("%d-%m-%Y")
            payload[field_name] = value

        # Ensure all allowed fields are present, even if empty
        for field_name in allowed_fields:
            payload.setdefault(field_name, "")

        payload["category"] = selected_type

        assets_collection.insert_one(payload)

        flash("Asset added successfully.", "success")
        return redirect(url_for("main.dashboard"))

    # GET route: Populate dropdown and form
    types = asset_types_collection.find({}, {"type_name": 1})
    form.category.choices = [(t["type_name"], t["type_name"]) for t in types]
    form.category.choices.append(("add_new_type", "add_new_type"))

    selected_type = request.args.get("type")
    fields_to_render = []

    if selected_type == "add_new_type":
        fields_to_render = get_master_fields()
        for field in fields_to_render:
            if field.get("name", "").lower() == "state" and field.get("type") == "select":
                if not field.get("options"):
                    field["options"] = get_indian_states()
    elif selected_type:
        config = asset_types_collection.find_one({"type_name": selected_type})
        if config and "fields" in config:
            fields_to_render = config["fields"]

    return render_template(
        "create_new_asset.html",
        form=form,
        editing=False,
        master_fields=get_master_fields(),
        asset_data={},
        fields_to_render=fields_to_render
    )


def normalize_gst_keys(asset: dict) -> dict:
    """
    Ensure GST keys follow format: gst_22 (instead of gst_(22%) or gst22)
    """
    normalized = {}
    for key, value in asset.items():
        key_str = str(key)
        if key_str.lower().startswith("gst"):
            # Extract digits from key
            match = re.search(r"(\d+)", key_str)
            if match:
                new_key = f"gst_{match.group(1)}"
                normalized[new_key] = value
            else:
                normalized[key] = value
        else:
            normalized[key] = value
    return normalized

@main_bp.route("/edit_asset/<asset_id>", methods=["GET", "POST"])
def edit_asset(asset_id):
    asset = assets_collection.find_one({"_id": ObjectId(asset_id)})
    if not asset:
        flash("Asset not found.", "danger")
        return redirect(url_for("main.dashboard"))

    # Normalize GST keys so we always have gst_XX
    asset = normalize_gst_keys(asset)

    selected_type = asset.get("category", "")
    config = asset_types_collection.find_one({"type_name": selected_type})
    fields_to_render = config.get("fields", []) if config else []
    allowed_fields = [f["name"] for f in fields_to_render]

    # Pre-populate form data
    populated_data = {}
    amount_numeric = safe_to_float(asset.get("amount"), 0.0)

    for field in fields_to_render:
        field_name = field["name"]
        field_label = field["label"]

        # Prefer DB key, fallback to label
        raw_val = asset.get(field_name, asset.get(field_label, ""))

        if field_name.startswith("gst_"):
            # If empty -> compute from amount; else coerce
            if raw_val in [None, "", "—"]:
                try:
                    gst_percent = int(field_name.split("_")[1])
                except Exception:
                    gst_percent = 0
                val_num = round(amount_numeric * gst_percent / 100, 2)
            else:
                val_num = safe_to_float(raw_val, 0.0)
            # Fill edit input with Indian commas, no ₹
            val = format_inr_no_symbol(val_num)

        elif field_name == "amount":
            # Always show with commas, no ₹
            val = format_inr_no_symbol(amount_numeric)

        elif field_name == "total":
            # Sum all gst_* safely
            total_gst = 0.0
            for k, v in asset.items():
                if isinstance(k, str) and k.startswith("gst_"):
                    total_gst += safe_to_float(v, 0.0)
            val_num = amount_numeric + total_gst
            val = format_inr_no_symbol(val_num)

        else:
            val = "" if raw_val in [None, ""] else raw_val

        populated_data[field_name] = val

    # 🔑 ADD THIS LINE — RIGHT HERE
    populated_data["category"] = selected_type


    form = AssetForm(data=populated_data)

    if request.method == "POST":
        raw_data = request.form.to_dict()
        raw_data.pop("csrf_token", None)
        raw_data.pop("submit", None)

        # Parse dates
        for field in ["given_date", "purchase_date", "collected_date", "prev_given_date"]:
            date_str = raw_data.get(field, "")
            parsed_date = parse_ddmmyyyy_to_date(date_str.strip()) if date_str.strip() else None
            raw_data[field] = parsed_date.strftime("%d-%m-%Y") if parsed_date else date_str

        # Normalize numeric fields -> raw decimals for DB
        for money_field in ["amount", "total"]:
            if money_field in raw_data:
                raw_data[money_field] = safe_to_float(raw_data[money_field], 0.0)

        for key in list(raw_data.keys()):
            if key.startswith("gst_"):
                raw_data[key] = safe_to_float(raw_data.get(key), 0.0)

        # Normalize name/category/status/owner (your existing helper)
        raw_data.update(normalize_asset_data(raw_data))

        # Allowed payload only
        payload = {}
        for key in allowed_fields:
            val = raw_data.get(key, "")
            payload[key] = val

        payload["category"] = selected_type

        assets_collection.update_one({"_id": ObjectId(asset_id)}, {"$set": payload})

        flash("Asset updated successfully.", "success")
        return redirect(url_for("main.dashboard"))

    asset["_id"] = str(asset["_id"])
    return render_template(
        "create_new_asset.html",
        form=form,
        editing=True,
        master_fields=get_master_fields(),
        asset_data=asset,
        asset_id=asset_id,
        fields_to_render=fields_to_render,
        types=get_all_existing_types()
    )

@main_bp.route("/view_asset/<asset_id>")
def view_asset(asset_id):
    asset = assets_collection.find_one({"_id": ObjectId(asset_id)})
    if not asset:
        flash("Asset not found", "danger")
        return redirect(url_for("main.dashboard"))

    # 🔹 Normalize GST keys
    asset = normalize_gst_keys(asset)

    # 🔹 Ensure numeric fields are float for consistent formatting
    for key in asset:
        if key in ["amount", "total"] or key.startswith("gst_"):
            asset[key] = safe_to_float(asset[key], 0.0)

    # 3️⃣ Auto-calculate total if missing
    amount = safe_to_float(asset.get("amount"), 0.0)
    if "total" not in asset or safe_to_float(asset.get("total"), 0.0) == 0.0:
        total_gst = sum(safe_to_float(asset[k], 0.0) for k in asset if k.startswith("gst_"))
        asset["total"] = amount + total_gst

    view_data = []
    for key, value in asset.items():
        if key == "_id":
            continue

        # Determine if this field should be formatted as currency
        is_currency = key in ["amount", "total"] or key.startswith("gst_")

        # Format value
        if isinstance(value, (datetime, date)):
            formatted_value = value.strftime("%d-%m-%Y")
        elif is_currency:
            formatted_value = format_inr(value)  # Flask filter from extensions.py
        else:
            formatted_value = value if value not in [None, ""] else "—"

        # Label
        if key.startswith("gst_"):
            label = f"GST ({key.split('_')[1]}%)"
        else:
            label = key.replace("_", " ").title()

        view_data.append({
            "label": label,
            "value": formatted_value,
            "is_currency": is_currency
        })

    return render_template("view_asset.html", asset=asset, view_data=view_data)
