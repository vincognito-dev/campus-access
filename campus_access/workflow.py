"""Workflow rules for access-card requests (Engineer B).

Rule for every function: check everything first, change the record last.
B never edits storage._requests directly; changes go through
storage.update_request.
"""

from campus_access import storage
from campus_access.validation import validate_approver

# ---------- Constants ----------
# Each status maps to the ONE status that may follow it.
# "returned" is the end of the line, so it maps to None. No real
# new_status ever equals None, so any move after "returned" fails.
ALLOWED_TRANSITIONS = {
    "requested": "approved",
    "approved": "issued",
    "issued": "returned",
    "returned": None,
}


# ---------- Shared helper ----------
def _check_transition(record, new_status):
    current = record["status"]
    allowed = ALLOWED_TRANSITIONS.get(current)
    if new_status != allowed:
        raise ValueError(
            f"Cannot move request from '{current}' to '{new_status}'"
            + (f"; next allowed status is '{allowed}'." if allowed
               else "; no further changes are allowed.")
        )


# ---------- Approve ----------
def approve_request(request_id, approved_by):
    record = storage.get_request(request_id)
    validate_approver(approved_by)
    _check_transition(record, "approved")
    return storage.update_request(
        request_id, status="approved", approved_by=approved_by
    )


# ---------- Issue ----------
def issue_card(request_id):
    record = storage.get_request(request_id)
    _check_transition(record, "issued")
    approver = record.get("approved_by")
    if not approver or not str(approver).strip():
        raise ValueError("Cannot issue a card without an approver on record.")
    return storage.update_request(request_id, status="issued")


# ---------- Return ----------
def return_card(request_id):
    record = storage.get_request(request_id)
    _check_transition(record, "returned")
    return storage.update_request(request_id, status="returned")