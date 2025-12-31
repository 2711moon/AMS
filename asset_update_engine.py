# asset_update_engine.py
from datetime import datetime, date
import copy

from asset_fields import (
    IMMUTABLE_FIELDS,
    SYSTEM_CONTROLLED_FIELDS,
    USER_EDITABLE_FIELDS,
    REMARKS_TRIGGER_FIELDS,
)
from asset_valid import (
    parse_ddmmyyyy,
    normalize_money,
)


def sanitize_asset_update(
    old_asset: dict,
    incoming_data: dict,
    *,
    source: str,          # "ui" or "excel"
    force_apply: bool
):
    warnings = []
    payload = copy.deepcopy(old_asset)

    # ---------- IMMUTABLE ENFORCEMENT ----------
    for field in IMMUTABLE_FIELDS:
        if field in incoming_data and incoming_data[field] != old_asset.get(field):
            raise ValueError(f"Immutable field modified: {field}")

    # ---------- APPLY USER-EDITABLE ONLY ----------
    for key, value in incoming_data.items():
        if key in USER_EDITABLE_FIELDS:
            payload[key] = value

    # ---------- DATE VALIDATION ----------
    for field in (
        "given_date",
        "purchase_date",
        "collected_date",
        "prev_given_date",
    ):
        val = payload.get(field)
        if not val:
            continue

        parsed = parse_ddmmyyyy(val)
        if not parsed:
            warnings.append(f"Invalid date format for {field}")
        elif parsed > date.today():
            warnings.append(f"{field} is a future date")

    # ---------- MONEY + GST ----------
    amount = normalize_money(payload.get("amount"))
    gst_total = (
        normalize_money(payload.get("gst_18")) +
        normalize_money(payload.get("gst_22")) +
        normalize_money(payload.get("gst_28"))
    )
    total = normalize_money(payload.get("total"))

    if amount > 0 and abs((amount + gst_total) - total) > 0.5:
        warnings.append("Amount / GST / Total mismatch")

    # ---------- REMARKS APPEND ----------
    changed = []
    for field in REMARKS_TRIGGER_FIELDS:
        if old_asset.get(field) != payload.get(field):
            changed.append(str(payload.get(field, "")))

    if changed:
        stamp = datetime.now().strftime("%d-%m-%Y")
        line = f"[{stamp}] " + " | ".join(changed)
        payload["remarks"] = (old_asset.get("remarks", "") + "\n" + line).strip()

    # ---------- SYSTEM FIELDS ----------
    payload["updated_at"] = datetime.utcnow()

    if source == "excel" and warnings and not force_apply:
        return {}, warnings

    return payload, warnings
