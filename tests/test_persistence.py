import json
import os
import tempfile
import unittest

from campus_access import storage


def good_record(request_id="A001"):
    return {
        "id": request_id,
        "fellow_id": "F001",
        "card_type": "visitor",
        "status": "requested",
        "approved_by": None,
    }


class TestPersistence(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp_dir.name, "requests.json")
        storage._requests.clear()

    def tearDown(self):
        storage._requests.clear()
        self.temp_dir.cleanup()

    def write_file(self, text):
        with open(self.path, "w") as f:
            f.write(text)

    def write_records(self, records):
        self.write_file(json.dumps(records))

    # ---------- save and reload ----------
    def test_save_then_load_restores_records(self):
        storage.create_request("F001", "visitor")
        storage.save_requests(self.path)
        storage._requests.clear()
        storage.load_requests(self.path)
        self.assertEqual(storage.get_request("A001")["fellow_id"], "F001")

    def test_next_id_after_reload_is_a002(self):          # CASE 6
        storage.create_request("F001", "visitor")
        storage.save_requests(self.path)
        storage._requests.clear()
        storage.load_requests(self.path)
        new_record = storage.create_request("F002", "staff")
        self.assertEqual(new_record["id"], "A002")

    # ---------- failed save ----------
    def test_failed_save_keeps_old_file(self):
        storage.create_request("F001", "visitor")
        storage.save_requests(self.path)
        with open(self.path) as f:
            before = f.read()

        storage._requests["A001"]["fellow_id"] = {1, 2}    # a set: json can't write it
        with self.assertRaises(Exception):
            storage.save_requests(self.path)

        with open(self.path) as f:
            after = f.read()
        self.assertEqual(before, after)
        self.assertFalse(os.path.exists(self.path + ".tmp"))

    # ---------- bad files: each must raise ValueError ----------
    def test_missing_file_rejected(self):
        with self.assertRaises(ValueError):
            storage.load_requests(self.path)

    def test_empty_file_rejected(self):
        self.write_file("")
        with self.assertRaises(ValueError):
            storage.load_requests(self.path)

    def test_corrupted_json_rejected(self):
        self.write_file("{not json")
        with self.assertRaises(ValueError):
            storage.load_requests(self.path)

    def test_duplicate_ids_rejected(self):
        record = json.dumps(good_record())
        self.write_file('{"A001": %s, "A001": %s}' % (record, record))
        with self.assertRaises(ValueError):
            storage.load_requests(self.path)

    def test_missing_key_rejected(self):
        record = good_record()
        del record["status"]
        self.write_records({"A001": record})
        with self.assertRaises(ValueError):
            storage.load_requests(self.path)

    def test_wrong_top_level_type_rejected(self):
        self.write_file("[]")
        with self.assertRaises(ValueError):
            storage.load_requests(self.path)

    def test_invalid_status_rejected(self):
        record = good_record()
        record["status"] = "pending"
        self.write_records({"A001": record})
        with self.assertRaises(ValueError):
            storage.load_requests(self.path)

    def test_invalid_card_type_rejected(self):
        record = good_record()
        record["card_type"] = "mentor"
        self.write_records({"A001": record})
        with self.assertRaises(ValueError):
            storage.load_requests(self.path)

    def test_id_not_matching_key_rejected(self):
        record = good_record("A002")                       # id A002 filed under key A001
        self.write_records({"A001": record})
        with self.assertRaises(ValueError):
            storage.load_requests(self.path)

    def test_issued_without_approver_rejected(self):
        record = good_record()
        record["status"] = "issued"                        # approved_by stays None
        self.write_records({"A001": record})
        with self.assertRaises(ValueError):
            storage.load_requests(self.path)

    # ---------- a failed load never wipes existing data ----------
    def test_failed_load_keeps_existing_records(self):    # CASE 7
        storage.create_request("F001", "visitor")
        self.write_file("{not json")
        with self.assertRaises(ValueError):
            storage.load_requests(self.path)
        self.assertIn("A001", storage._requests)


if __name__ == "__main__":
    unittest.main()