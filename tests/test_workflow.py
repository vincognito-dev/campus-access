import unittest
import os
import json
from campus_access.storage import RequestRegistry
from campus_access.workflow import WorkflowManager

class TestCampusAccessSystem(unittest.TestCase):
    def setUp(self):
        self.registry = RequestRegistry()
        self.workflow = WorkflowManager(self.registry)
        self.test_file = "test_data_output.json"

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    # 1. Valid registration check (A1 & Case 1)
    def test_valid_creation(self):
        rid = self.registry.create_request("F001", "visitor")
        self.assertEqual(rid, "A001")
        req = self.registry.get_request(rid)
        self.assertEqual(req["status"], "requested")
        self.assertIsNone(req["approved_by"])

    # 2. Rejection configurations check (A2)
    def test_invalid_card_type(self):
        with self.assertRaises(ValueError):
            self.registry.create_request("F002", "platinum_access")

    def test_blank_fellow_id(self):
        with self.assertRaises(ValueError):
            self.registry.create_request("   ", "student")

    # 3. Illegal shortcut transition check (Case 2)
    def test_illegal_issue_before_approval(self):
        rid = self.registry.create_request("F001", "student")
        with self.assertRaises(ValueError):
            self.workflow.issue_card(rid)
        # Ensure status did not change
        self.assertEqual(self.registry.get_request(rid)["status"], "requested")

    # 4. Empty approver criteria check (Case 3)
    def test_blank_approver(self):
        rid = self.registry.create_request("F001", "staff")
        with self.assertRaises(ValueError):
            self.workflow.approve_request(rid, "   ")
        self.assertEqual(self.registry.get_request(rid)["status"], "requested")

    # 5. Full normal workflow pipeline pass (Case 4)
    def test_correct_full_workflow(self):
        rid = self.registry.create_request("F001", "staff")
        self.workflow.approve_request(rid, "M01")
        self.assertEqual(self.registry.get_request(rid)["status"], "approved")

        self.workflow.issue_card(rid)
        self.assertEqual(self.registry.get_request(rid)["status"], "issued")
        
        self.workflow.return_card(rid)
        self.assertEqual(self.registry.get_request(rid)["status"], "returned")

    # 6. Double usage/return terminal state rejection check (Case 5)
    def test_double_return_rejection(self):
        rid = self.registry.create_request("F001", "visitor")
        self.workflow.approve_request(rid, "M01")
        self.workflow.issue_card(rid)
        self.workflow.return_card(rid)
        
        with self.assertRaises(ValueError):
            self.workflow.return_card(rid)
            
        with self.assertRaises(ValueError):
            self.workflow.issue_card(rid)

    # 7. Uniqueness high water-marks persistent across safe environments (Case 6)
    def test_unique_ids_after_reload(self):
        self.registry.create_request("F001", "student")
        self.registry.save_requests(self.test_file)
        
        new_registry = RequestRegistry()
        new_registry.load_requests(self.test_file)
        next_id = new_registry.create_request("F002", "staff")
        self.assertEqual(next_id, "A002")

    # 8. Malformed components payload file handling execution criteria (Case 7)
    def test_corrupted_json_handling(self):
        with open(self.test_file, "w") as f:
            f.write("{invalid-json-payload-corrupted}")
        
        with self.assertRaises(json.JSONDecodeError):
            self.registry.load_requests(self.test_file)
