"""Storage for campus access requests.

Owns the request store, ID generation, lookup, save and load.
Rule for every function: check everything first, change the store last.
"""

import json
import os

from campus_access.validation import (
    validate_fellow_id,
    validate_card_type,
    validate_request_id,
    validate_approver,
    ID_PREFIX,
    ID_DIGIT_COUNT,
)

# ---------- Constants ----------
VALID_STATUSES = ("requested", "approved", "issued", "returned")
REQUIRED_KEYS = ("id", "fellow_id", "card_type", "status", "approved_by")
# ---------- The store ----------
_requests = {}

# ---------- ID generation ----------
def next_id():
    highest = 0
    for request_id in _requests:
        number = int(request_id[len(ID_PREFIX):])
        if number > highest:
            highest = number
    return f"{ID_PREFIX}{highest + 1:0{ID_DIGIT_COUNT}d}"
print(next_id())
# ---------- Create ----------
def create_request(fellow_id, card_type):
    validate_fellow_id(fellow_id)
    validate_card_type(card_type)
    request_id = next_id()
    requested = {
        "id": request_id,
        "fellow_id": fellow_id,
        "card_type": card_type,
        "status": "requested",
        "approved_by": None
    }
    _requests[request_id] = requested
    return dict(requested)

# ---------- Lookup (read-only) ----------
def get_request(request_id):
    validate_request_id(request_id)

    if request_id not in _requests:
        raise ValueError(f"Request {request_id} not found")

    return dict(_requests[request_id])
# ---------- Update contract for Engineer B ----------
def update_request(request_id, **changes):
    validate_request_id(request_id)

    if request_id not in _requests:
        raise ValueError(f"Request {request_id} not found")

    allowed = ("status", "approved_by")
    for field in changes:
        if field not in allowed:
            raise ValueError(f"Field '{field}' cannot be changed")

    _requests[request_id].update(changes)
    return dict(_requests[request_id])


# ---------- Save ----------
def save_requests(path):
    data = {request_id: dict(record) for request_id, record in _requests.items()}
    temp_path = path + ".tmp"

    try:
        with open(temp_path, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(temp_path, path)
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise

# ---------- Load ----------
def _validate_record(key, record):
    if not isinstance(record, dict):
        raise ValueError(f"Record {key} must be a dictionary")

    if set(record.keys()) != set(REQUIRED_KEYS):
        raise ValueError(f"Record {key} must have exactly these keys: {REQUIRED_KEYS}")

    validate_request_id(record["id"])
    if record["id"] != key:
        raise ValueError(f"Record id {record['id']} does not match its key {key}")

    validate_fellow_id(record["fellow_id"])
    validate_card_type(record["card_type"])

    if record["status"] not in VALID_STATUSES:
        raise ValueError(f"Record {key} has invalid status: {record['status']}")

    if record["status"] == "requested":
        if record["approved_by"] is not None:
            raise ValueError(f"Record {key} is requested but has an approver")
    else:
        validate_approver(record["approved_by"])


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate id in file: {key}")
        result[key] = value
    return result


def load_requests(path):
    try:
        with open(path, "r") as f:
            text = f.read()
    except FileNotFoundError:
        raise ValueError(f"File not found: {path}") from None

    if text.strip() == "":
        raise ValueError("File is empty")

    try:
        data = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except json.JSONDecodeError as error:
        raise ValueError(f"File is not valid JSON: {error}") from None

    if not isinstance(data, dict):
        raise ValueError("File must contain a dictionary of requests")

    loaded = {}
    for key, record in data.items():
        _validate_record(key, record)
        loaded[key] = dict(record)

    _requests.clear()
    _requests.update(loaded)