from campus_access.storage import RequestRegistry
from campus_access.storage import RequestRegistry
from campus_access.workflow import WorkflowManager


class WorkflowManager:
    def __init__(self, registry: RequestRegistry):
        self.registry = registry

    def approve_request(self, request_id: str, approved_by: str):
        if not approved_by or not isinstance(approved_by, str) or not approved_by.strip():
            raise ValueError("Approver identity cannot be blank.")
        
        req = self.registry.get_request(request_id)
        if req["status"] != "requested":
            raise ValueError(f"Cannot approve request in '{req['status']}' status.")

        # Update core state through registry cache reference modification safely
        record = self.registry._requests[request_id]
        record["status"] = "approved"
        record["approved_by"] = approved_by.strip()

    def issue_card(self, request_id: str):
        req = self.registry.get_request(request_id)
        if req["status"] != "approved":
            raise ValueError(f"Cannot issue card from status '{req['status']}'. Must be 'approved'.")
        if not req["approved_by"]:
            raise ValueError("Cannot issue a card without an authorized staff signature.")

        record = self.registry._requests[request_id]
        record["status"] = "issued"

    def return_card(self, request_id: str):
        req = self.registry.get_request(request_id)
        if req["status"] != "issued":
            raise ValueError(f"Cannot return card from status '{req['status']}'. Must be 'issued'.")

        record = self.registry._requests[request_id]
        record["status"] = "returned"
