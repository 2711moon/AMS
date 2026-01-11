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
    source: str,
    force_apply: bool,
    allowed_fields: list[str]
):
    """
    Rules:
    - CREATE (old_asset empty):
        - accept full schema (AMS or Excel)
        - NO immutable enforcement
        - NO user-editable restriction
        - preserve incoming remarks
    - UPDATE (old_asset exists):
        - enforce immutables
        - restrict to USER_EDITABLE_FIELDS
        - append remarks
    """

    warnings = []
    is_create = not bool(old_asset)

    # -------------------------------------------------
    # BASE PAYLOAD
    # -------------------------------------------------
    if is_create:
        # First insert: take everything as-is
        payload = copy.deepcopy(incoming_data)
    else:
        # Update: start from existing asset
        payload = copy.deepcopy(old_asset)

    # -------------------------------------------------
    # IMMUTABLE ENFORCEMENT (UPDATES ONLY)
    # -------------------------------------------------
    if not is_create:
        for field in IMMUTABLE_FIELDS:
            if field in incoming_data and field in old_asset:
                old_val = old_asset.get(field)
                new_val = incoming_data.get(field)

                if old_val is None:
                    continue

                if str(old_val).strip().lower() != str(new_val).strip().lower():
                    raise ValueError(f"Immutable field modified: {field}")

    # -------------------------------------------------
    # APPLY DATA
    # -------------------------------------------------
    if is_create:
        # already applied above
        pass
    else:
        # update only allowed user-editable fields
        for key, value in incoming_data.items():
            if key in USER_EDITABLE_FIELDS:
                payload[key] = value

    # -------------------------------------------------
    # DATE VALIDATION (NON-BLOCKING)
    # -------------------------------------------------
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

    # -------------------------------------------------
    # MONEY + GST VALIDATION
    # IMPORTANT:
    # - amount = 0, gst = 0, total > 0 IS VALID (Excel invoices)
    # -------------------------------------------------
    amount = normalize_money(payload.get("amount"))
    gst_total = (
        normalize_money(payload.get("gst_18")) +
        normalize_money(payload.get("gst_22")) +
        normalize_money(payload.get("gst_28"))
    )
    total = normalize_money(payload.get("total"))

    if amount > 0 and gst_total > 0:
        if abs((amount + gst_total) - total) > 0.5:
            warnings.append("Amount / GST / Total mismatch")

    # -------------------------------------------------
    # REMARKS HANDLING
    # -------------------------------------------------
    if not is_create:
        changed = []
        for field in REMARKS_TRIGGER_FIELDS:
            if old_asset.get(field) != payload.get(field):
                changed.append(str(payload.get(field, "")))

        if changed:
            stamp = datetime.now().strftime("%d-%m-%Y")
            line = f"[{stamp}] " + " | ".join(changed)
            existing_remarks = payload.get("remarks") or old_asset.get("remarks") or ""
            payload["remarks"] = (existing_remarks + "\n" + line).strip()

    # -------------------------------------------------
    # SYSTEM FIELDS
    # -------------------------------------------------
    payload["updated_at"] = datetime.utcnow()

    # -------------------------------------------------
    # FINAL FIELD PRUNE
    # (keeps schema consistent, no ghost fields)
    # -------------------------------------------------
    payload = {
        k: v for k, v in payload.items()
        if k in allowed_fields
           or k in IMMUTABLE_FIELDS
           or k in SYSTEM_CONTROLLED_FIELDS
    }

    # -------------------------------------------------
    # WARNINGS HANDLING
    # -------------------------------------------------
    if source == "excel" and warnings and not force_apply:
        return {}, warnings

    return payload, warnings
