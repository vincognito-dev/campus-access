import json
import os
import re

class RequestRegistry:
    def __init__(self):
        self._requests = {}
        self._next_id_numeric = 1

    def create_request(self, fellow_id: str, card_type: str) -> str:
        if not isinstance(fellow_id, str) or not isinstance(card_type, str):
            raise ValueError("Inputs must be strings.")
        
        sanitized_fellow = fellow_id.strip()
        if not sanitized_fellow:
            raise ValueError("Fellow ID cannot be blank.")
            
        allowed_types = {"visitor", "student", "staff"}
        if card_type not in allowed_types:
            raise ValueError("Invalid card type.")

        req_id = f"A{self._next_id_numeric:03d}"
        
        self._requests[req_id] = {
            "id": req_id,
            "fellow_id": sanitized_fellow,
            "card_type": card_type,
            "status": "requested",
            "approved_by": None
        }
        self._next_id_numeric += 1
        return req_id

    def get_request(self, request_id: str) -> dict:
        if request_id not in self._requests:
            raise ValueError(f"Request ID '{request_id}' not found.")
        # Return the actual dictionary reference so status updates save dynamically
        return self._requests[request_id]

    def list_all(self) -> list:
        return list(self._requests.values())

    def save_requests(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            # Save both the requests and the next tracking ID
            json.dump({
                "requests": self._requests,
                "next_id_numeric": self._next_id_numeric
            }, f, indent=4)

    def load_requests(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
            
        with open(path, 'r', encoding='utf-8') as f:
            raw_content = f.read().strip()
            if not raw_content:
                raise ValueError("JSON file is empty.")
            data = json.loads(raw_content)

        if "requests" in data and "next_id_numeric" in data:
            requests_dict = data["requests"]
            self._next_id_numeric = int(data["next_id_numeric"])
        else:
            requests_dict = data

        if not isinstance(requests_dict, dict):
            raise ValueError("Invalid format: Root component must be a dictionary object.")

        temp_requests = {}
        highest_id = 0
        id_pattern = re.compile(r"^A([0-9]{3})$")

        for k, v in requests_dict.items():
            match = id_pattern.match(k)
            if not match:
                raise ValueError(f"Malformed request ID structure key: {k}")
            
            numeric_part = int(match.group(1))
            if numeric_part > highest_id:
                highest_id = numeric_part

            for field in ["id", "fellow_id", "card_type", "status", "approved_by"]:
                if field not in v:
                    raise ValueError(f"Missing mandatory field '{field}' in request {k}")

            if v["id"] != k:
                raise ValueError(f"Key mismatch: Key '{k}' does not match record ID '{v['id']}'")

            if v["card_type"] not in {"visitor", "student", "staff"}:
                raise ValueError(f"Invalid card type encountered: {v['card_type']}")

            if v["status"] not in {"requested", "approved", "issued", "returned"}:
                raise ValueError(f"Invalid status layer encountered: {v['status']}")

            if v["status"] != "requested" and not v["approved_by"]:
                raise ValueError(f"Integrity check failed: State '{v['status']}' requires an approver.")

            temp_requests[k] = {
                "id": v["id"],
                "fellow_id": str(v["fellow_id"]).strip(),
                "card_type": v["card_type"],
                "status": v["status"],
                "approved_by": v["approved_by"]
            }

        self._requests = temp_requests
        if "next_id_numeric" not in data:
            self._next_id_numeric = highest_id + 1
