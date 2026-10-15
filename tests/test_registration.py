import unittest
from campus_access.validation import (
    validate_request_id,
    validate_card_type,
    validate_approver,
    validate_fellow_id,
)


class TestValidation(unittest.TestCase):

    def test_valid_request_id_passes(self):
        validate_request_id("A001")

    def test_request_id_with_no_digits_rejected(self):
        with self.assertRaises(ValueError):
            validate_request_id("A")

if __name__ == "__main__":
    unittest.main()