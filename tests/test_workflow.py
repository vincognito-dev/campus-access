"""Tests for campus_access/workflow.py (Engineer B).

Run with:  python -m unittest tests.test_workflow -v
       or: python -m unittest discover -v
No third-party packages needed. Uses a fake storage so the tests don't
depend on storage.py internals.
Assumes update_request(request_id, **fields) returns the updated record.
"""

import unittest
from unittest import mock

from campus_access import workflow


# ---------- Fakes ----------
class FakeStorage:
    def __init__(self, records):
        self.records = records
        self.update_calls = []

    def get_request(self, request_id):
        if request_id not in self.records:
            raise KeyError(request_id)
        return dict(self.records[request_id])  # copy, like a real read

    def update_request(self, request_id, **fields):
        self.update_calls.append((request_id, fields))
        self.records[request_id].update(fields)
        return dict(self.records[request_id])


def fake_validate_approver(approved_by):
    if not approved_by or not str(approved_by).strip():
        raise ValueError("Invalid approver")


def make(status, approved_by=None, request_id=1):
    return {request_id: {"id": request_id, "status": status, "approved_by": approved_by}}


class WorkflowTestCase(unittest.TestCase):
    def install(self, records):
        """Swap in a FakeStorage and fake validator for this test."""
        fake = FakeStorage(records)
        p1 = mock.patch.object(workflow, "storage", fake)
        p2 = mock.patch.object(workflow, "validate_approver", fake_validate_approver)
        p1.start()
        p2.start()
        self.addCleanup(p1.stop)
        self.addCleanup(p2.stop)
        return fake


# ---------- ALLOWED_TRANSITIONS ----------
class TestTransitionTable(unittest.TestCase):
    def test_transition_table(self):
        self.assertEqual(workflow.ALLOWED_TRANSITIONS["requested"], "approved")
        self.assertEqual(workflow.ALLOWED_TRANSITIONS["approved"], "issued")
        self.assertEqual(workflow.ALLOWED_TRANSITIONS["issued"], "returned")
        self.assertIsNone(workflow.ALLOWED_TRANSITIONS["returned"])


# ---------- _check_transition ----------
class TestCheckTransition(unittest.TestCase):
    def test_allows_next_step(self):
        workflow._check_transition({"status": "requested"}, "approved")  # no raise

    def test_rejects_bad_moves(self):
        bad_moves = [
            ("requested", "issued"),    # skip
            ("requested", "returned"),  # skip
            ("approved", "approved"),   # repeat
            ("approved", "returned"),   # skip
            ("issued", "approved"),     # backwards
            ("returned", "approved"),   # nothing follows returned
            ("returned", "returned"),
        ]
        for current, attempted in bad_moves:
            with self.subTest(current=current, attempted=attempted):
                with self.assertRaises(ValueError):
                    workflow._check_transition({"status": current}, attempted)

    def test_message_names_both_statuses(self):
        with self.assertRaises(ValueError) as ctx:
            workflow._check_transition({"status": "requested"}, "issued")
        self.assertIn("requested", str(ctx.exception))
        self.assertIn("issued", str(ctx.exception))


# ---------- approve_request ----------
class TestApproveRequest(WorkflowTestCase):
    def test_happy_path(self):
        fake = self.install(make("requested"))
        result = workflow.approve_request(1, "Dr. Smith")
        self.assertEqual(result["status"], "approved")
        self.assertEqual(result["approved_by"], "Dr. Smith")
        self.assertEqual(len(fake.update_calls), 1)

    def test_invalid_approver_leaves_record_untouched(self):
        for bad in [None, "", "   "]:
            with self.subTest(approver=bad):
                fake = self.install(make("requested"))
                with self.assertRaises(ValueError):
                    workflow.approve_request(1, bad)
                self.assertEqual(fake.update_calls, [])
                self.assertEqual(fake.records[1]["status"], "requested")

    def test_wrong_state_leaves_record_untouched(self):
        for status in ["approved", "issued", "returned"]:
            with self.subTest(status=status):
                fake = self.install(make(status, approved_by="Dr. Smith"))
                with self.assertRaises(ValueError):
                    workflow.approve_request(1, "Someone Else")
                self.assertEqual(fake.update_calls, [])
                self.assertEqual(fake.records[1]["approved_by"], "Dr. Smith")


# ---------- issue_card ----------
class TestIssueCard(WorkflowTestCase):
    def test_happy_path(self):
        fake = self.install(make("approved", approved_by="Dr. Smith"))
        result = workflow.issue_card(1)
        self.assertEqual(result["status"], "issued")
        self.assertEqual(len(fake.update_calls), 1)

    def test_wrong_state_leaves_record_untouched(self):
        for status in ["requested", "issued", "returned"]:
            with self.subTest(status=status):
                fake = self.install(make(status, approved_by="Dr. Smith"))
                with self.assertRaises(ValueError):
                    workflow.issue_card(1)
                self.assertEqual(fake.update_calls, [])

    def test_without_approver_is_rejected(self):
        for approver in [None, "", "   "]:
            with self.subTest(approver=approver):
                fake = self.install(make("approved", approved_by=approver))
                with self.assertRaises(ValueError):
                    workflow.issue_card(1)
                self.assertEqual(fake.update_calls, [])
                self.assertEqual(fake.records[1]["status"], "approved")

    def test_missing_approver_key_is_rejected(self):
        fake = self.install({1: {"id": 1, "status": "approved"}})  # no approved_by key
        with self.assertRaises(ValueError):
            workflow.issue_card(1)
        self.assertEqual(fake.update_calls, [])


# ---------- return_card ----------
class TestReturnCard(WorkflowTestCase):
    def test_happy_path(self):
        fake = self.install(make("issued", approved_by="Dr. Smith"))
        result = workflow.return_card(1)
        self.assertEqual(result["status"], "returned")
        self.assertEqual(len(fake.update_calls), 1)

    def test_wrong_state_leaves_record_untouched(self):
        for status in ["requested", "approved", "returned"]:
            with self.subTest(status=status):
                fake = self.install(make(status, approved_by="Dr. Smith"))
                with self.assertRaises(ValueError):
                    workflow.return_card(1)
                self.assertEqual(fake.update_calls, [])


# ---------- Full lifecycle ----------
class TestLifecycle(WorkflowTestCase):
    def test_full_lifecycle_then_locked(self):
        fake = self.install(make("requested"))
        workflow.approve_request(1, "Dr. Smith")
        workflow.issue_card(1)
        workflow.return_card(1)
        self.assertEqual(fake.records[1]["status"], "returned")

        # nothing may follow "returned"
        with self.assertRaises(ValueError):
            workflow.approve_request(1, "Dr. Smith")
        with self.assertRaises(ValueError):
            workflow.issue_card(1)
        with self.assertRaises(ValueError):
            workflow.return_card(1)
        self.assertEqual(len(fake.update_calls), 3)  # only the three valid moves wrote


# ---------- Missing record ----------
class TestMissingRecord(WorkflowTestCase):
    def test_unknown_request_id_raises_before_any_write(self):
        fake = self.install(make("requested"))
        with self.assertRaises(Exception):
            workflow.approve_request(999, "Dr. Smith")
        self.assertEqual(fake.update_calls, [])


if __name__ == "__main__":
    unittest.main()

