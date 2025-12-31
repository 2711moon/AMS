#asset_valid.py
from datetime import datetime, date

# ---------- DATE HELPERS ----------

def parse_ddmmyyyy(val):
    """
    Accepts:
    - dd-mm-yyyy
    - yyyy-mm-dd
    Returns date or None
    """
    if not val:
        return None

    val = str(val).strip()

    for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(val, fmt).date()
        except ValueError:
            pass

    return None


# ---------- MONEY HELPERS ----------

def normalize_money(val):
    """
    Converts:
    - None, "" → 0.0
    - "₹1,200" → 1200.0
    - "118" → 118.0
    """
    if val in (None, "", "—"):
        return 0.0

    try:
        return float(
            str(val)
            .replace(",", "")
            .replace("₹", "")
            .replace("INR", "")
            .strip()
        )
    except ValueError:
        return 0.0
