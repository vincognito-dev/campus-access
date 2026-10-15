# Design Decisions

Agreed by: Engineer A (name) and Engineer B (name)
Date: 2026-10-15

## 1. What does one request dictionary look like?
Five fields, exactly these keys:

    {"id": "A001", "fellow_id": "F001", "card_type": "visitor",
     "status": "requested", "approved_by": None}

- `status` is one of: requested, approved, issued, returned.
- `approved_by` is `None` until approval, and a nonempty string afterwards.
- All requests live in one dictionary, `_requests`, keyed by request ID.
  Reason: lookup by ID is direct, and a key can only exist once.

## 2. What does create_request return?
A **copy** of the new record (`dict(record)`), not the stored one.
Reason: the caller can print it, but cannot change the store by editing it.
`get_request` and `update_request` also return copies.

## 3. How do functions report invalid input?
Every failure raises `ValueError` with a message saying what is wrong.
No function returns True/False or None to signal an error.
The CLI (Engineer B) catches `ValueError` and shows the message.
A missing data file also raises `ValueError`, so the CLI starts with an
empty store instead of crashing.

## 4. Where is the next ID generated?
In `storage._next_id()`. It reads the IDs already in `_requests`, takes the
highest number, and adds 1 (empty store gives A001). It does not use
`len()`, because gaps would cause a duplicate ID. IDs are never reused.
After a reload the store is refilled from the file, so the next ID continues
correctly (A002, not A001). No counter is saved.
Format: prefix `A` plus zero-padded digits (`ID_DIGIT_COUNT = 3`).
Validation accepts any number of ASCII digits, so A1000 is valid.

## 5. How does Engineer B call Engineer A's storage functions?
- Read a record: `storage.get_request(request_id)` (returns a copy).
- Change a record: `storage.update_request(request_id, status=..., approved_by=...)`.
  Only `status` and `approved_by` may change.
- B never edits `storage._requests` directly.
- Transition rules (requested -> approved -> issued -> returned) are B's job
  in `workflow.py`. B checks the rule first, then calls `update_request` last.
  `update_request` does not check transitions.
- Shared lists: `VALID_STATUSES` is defined once in `storage.py`.

## 6. What happens if a saved JSON file is invalid?
`load_requests` raises `ValueError` and leaves the in-memory data unchanged.
It rejects: missing file, empty file, corrupt JSON, a top-level value that
is not a dictionary, duplicate IDs, missing or extra keys, an id that does
not match its key, invalid fellow ID or card type, invalid status, and a
status that disagrees with `approved_by` (requested must have no approver;
every other status must have one).
Records are validated into a separate dictionary, which replaces the store
only after every record passes.
`save_requests` writes to a temporary file and replaces the real file only
on success, so a failed save never damages a valid file.

## 7. Which data must never change on a rejected operation?
Everything in `_requests`: every field of every record, and the set of IDs.
Each function validates and checks first and changes the store as its last
step. A rejected action leaves the record exactly as it was.

## Validation rules
- Fellow ID: must be a string; blank or spaces-only is rejected.
- Card type: visitor, student or staff. Case-sensitive: "Visitor" is
  rejected (validation, not sanitization).
- Request ID: "A" followed by one or more ASCII digits 0-9. Full-width and
  other Unicode digits are rejected. `.isdigit()` is not used for this reason.
- Approver: must be a string; blank or spaces-only is rejected.
## Resolved decisions

- **Fellow ID with spaces:** " F001 " is rejected (validation, not sanitization), so the stored value is exactly what the user typed.
- **Approver format:** any nonempty, non-blank string is accepted (e.g. "M01"). Only `validate_approver` changes if a format is required later.
- **Workflow return value:** `approve_request`, `issue_card` and `return_card` return a copy of the updated record, matching `create_request` and `get_request`.


## Project layout
Package `campus_access/` with validation.py, storage.py (A), workflow.py,
cli.py (B). `main.py` only starts the CLI. Tests live in `tests/` and use
temporary files.