import os
import json

# Global storage dictionary to satisfy the functional/procedural CLI design
_GLOBAL_REQUESTS = {}
_NEXT_ID_NUMBER = 1

# =====================================================================
# 1. OOP CLASSES (Required by your test suite)
# =====================================================================

class RequestRegistry:
    def __init__(self):
        self.requests = {}
        self.next_id_number = 1

    def create_request(self, fellow_id, card_type):
        if not fellow_id or not fellow_id.strip():
            raise ValueError("Fellow ID cannot be blank.")
        if card_type not in ["visitor", "student", "staff"]:
            raise ValueError("Invalid card type.")
            
        request_id = f"A{self.next_id_number:03d}"
        self.next_id_number += 1
        
        self.requests[request_id] = {
            "id": request_id,
            "fellow_id": fellow_id,
            "card_type": card_type,
            "status": "requested",
            "approved_by": None
        }
        return request_id

    def get_request(self, request_id):
        req = self.requests.get(request_id)
        if not req:
            raise ValueError("Request not found.")
        return req

    def save_requests(self, filename):
        data = {
            "requests": self.requests,
            "next_id_number": self.next_id_number
        }
        with open(filename, "w") as f:
            json.dump(data, f)

    def load_requests(self, filename):
        with open(filename, "r") as f:
            data = json.load(f)
        self.requests = data["requests"]
        self.next_id_number = data["next_id_number"]


class WorkflowManager:
    def __init__(self, registry):
        self.registry = registry

    def approve_request(self, request_id, approver):
        if not approver or not approver.strip():
            raise ValueError("Approver cannot be blank.")
        req = self.registry.get_request(request_id)
        req["status"] = "approved"
        req["approved_by"] = approver
        return req

    def issue_card(self, request_id):
        req = self.registry.get_request(request_id)
        if req["status"] != "approved":
            raise ValueError("Cannot issue card before approval.")
        req["status"] = "issued"
        return req

    def return_card(self, request_id):
        req = self.registry.get_request(request_id)
        if req["status"] == "returned":
            raise ValueError("Card already returned.")
        if req["status"] != "issued":
            raise ValueError("Cannot return an unissued card.")
        req["status"] = "returned"
        return req


# =====================================================================
# 2. GLOBAL PROCEDURAL FUNCTIONS (Required by your campus_access/cli.py)
# =====================================================================

def create_request(fellow_id: str, card_type: str) -> dict:
    if not fellow_id or not fellow_id.strip():
        raise ValueError("Fellow ID cannot be blank.")
    if card_type not in ["visitor", "student", "staff"]:
        raise ValueError("Invalid card type.")
    
    global _NEXT_ID_NUMBER
    request_id = f"A{_NEXT_ID_NUMBER:03d}"
    _NEXT_ID_NUMBER += 1
    
    req = {
        "id": request_id,
        "fellow_id": fellow_id,
        "card_type": card_type,
        "status": "requested",
        "approved_by": None
    }
    _GLOBAL_REQUESTS[request_id] = req
    return req

def get_request(request_id: str) -> dict:
    if request_id not in _GLOBAL_REQUESTS:
        raise ValueError("Request not found.")
    return _GLOBAL_REQUESTS[request_id]

def approve_request(request_id: str, approved_by: str) -> dict:
    if not approved_by or not approved_by.strip():
        raise ValueError("Approver cannot be blank.")
    req = get_request(request_id)
    req["status"] = "approved"
    req["approved_by"] = approved_by
    return req

def issue_card(request_id: str) -> dict:
    req = get_request(request_id)
    if req["status"] != "approved":
        raise ValueError("Cannot issue card before approval.")
    req["status"] = "issued"
    return req

def return_card(request_id: str) -> dict:
    req = get_request(request_id)
    if req["status"] == "returned":
        raise ValueError("Card already returned.")
    if req["status"] != "issued":
        raise ValueError("Cannot return an unissued card.")
    req["status"] = "returned"
    return req

def list_requests() -> list:
    return list(_GLOBAL_REQUESTS.values())

def save_requests(filename: str) -> None:
    data = {"requests": _GLOBAL_REQUESTS, "next_id_number": _NEXT_ID_NUMBER}
    with open(filename, "w") as f:
        json.dump(data, f)

def load_requests(filename: str) -> None:
    global _GLOBAL_REQUESTS, _NEXT_ID_NUMBER
    with open(filename, "r") as f:
        data = json.load(f)
    _GLOBAL_REQUESTS = data["requests"]
    _NEXT_ID_NUMBER = data["next_id_number"]
