"""Validation helpers for campus access requests.

Each function returns normally if the input is valid,
or raises ValueError with a clear message if it is not.
None of them change any data.
"""

# ---------- Constants ----------
VALID_CARD_TYPES = ("student", "visitor", "staff")
ID_PREFIX = "A"
ID_DIGIT_COUNT = 3
ASCII_DIGITS = "0123456789"


# ---------- Fellow ID ----------
def validate_fellow_id(fellow_id):
    if not isinstance(fellow_id, str):
        raise ValueError("Fellow ID must be a string")

    if fellow_id.strip() == "":
        raise ValueError("Fellow ID must not be blank")
# ---------- Card type ----------
def validate_card_type(card_type):
    if not isinstance(card_type, str):
        raise ValueError("Card type must be a string")
    if card_type not in VALID_CARD_TYPES:
        raise ValueError("Card type is not valid")
# ---------- Request ID ----------
def validate_request_id(request_id):
    if not isinstance(request_id, str):
        raise ValueError("Request ID must be a string") # Step 1: TODO check the type (must be a string)
    if not request_id.startswith(ID_PREFIX):
        raise ValueError("Request ID must start with the correct prefix") # Step 2: TODO check it starts with ID_PREFIX
    digits = request_id[len(ID_PREFIX):]
    if digits == "":
        raise ValueError("Request ID must have digits after the prefix")
    if not all(c in ASCII_DIGITS for c in digits):
        raise ValueError("Request ID must contain only digits 0-9 after the prefix")
# ---------- Approver ----------
def validate_approver(approved_by):
    if not isinstance(approved_by, str):
        raise ValueError("Approver must be a string")
    if approved_by.strip() == "":
        raise ValueError("Approver must not be blank")
print(validate_card_type("student"))