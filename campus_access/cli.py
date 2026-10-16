import os

from campus_access import storage
from campus_access.workflow import approve_request, issue_card, return_card

def _format_request(request: dict) -> str:
    approver = request["approved_by"] if request["approved_by"] else "none"
    return (
        f"ID: {request['id']}\n"
        f"Fellow ID: {request['fellow_id']}\n"
        f"Card type: {request['card_type']}\n"
        f"Status: {request['status']}\n"
        f"Approved by: {approver}"
    )
def _save_before_quit(storage_path: str) -> bool:
    """Offer to save. Return True if it is safe to quit."""
    answer = input("Save before quitting? (y/n): ").strip().lower()
    if answer != "y":
        return True
    try:
        storage.save_requests(storage_path)
        print(f"Saved requests to {storage_path}")
        return True
    except OSError as exc:
        print(f"Save failed: {exc}")
        return False

def run_menu() -> None:
    """Run a simple interactive campus access-card request manager."""
    storage_path = os.path.join(os.getcwd(), "campus_requests.json")

    # Reload earlier data on startup so IDs continue (A002, not A001 again).
    if os.path.exists(storage_path):
        try:
            storage.load_requests(storage_path)
            print(f"Loaded requests from {storage_path}")
        except (ValueError, OSError) as exc:
            print(f"Could not load {storage_path}: {exc}")
# ---------- List (read-only) ----------

    while True:
        print("__________________________________")
        print("Campus Access Card Manager\n")
        print("1. Create request")
        print("2. View request")
        print("3. Approve request")
        print("4. Issue card")
        print("5. Return card")
        print("6. List requests")
        print("7. Save to JSON")
        print("8. Reload from JSON")
        print("9. Quit")
        print("__________________________________\n")
        choice = input("Select an option: ").strip()
        wants_quit = choice == "9" or choice.lower() in {"q", "quit", "exit"}
        
        if wants_quit:
            if _save_before_quit(storage_path):
                print("Goodbye.")
                return
            continue

        try:
            if choice == "1":
                fellow_id = input("Fellow ID: ").strip()
                card_type = input("Card type (visitor/student/staff): ").strip().lower()
                request = storage.create_request(fellow_id, card_type)
                print(f"Request {request['id']} created for {request['fellow_id']} ({request['card_type']})")

            elif choice == "2":
                request_id = input("Request ID: ").strip()
                print(_format_request(storage.get_request(request_id)))

            elif choice == "3":
                request_id = input("Request ID: ").strip()
                approved_by = input("Approver ID: ").strip()
                request = approve_request(request_id, approved_by)
                print(f"Request {request['id']} approved by {request['approved_by']}.")

            elif choice == "4":
                request_id = input("Request ID: ").strip()
                request = issue_card(request_id)
                print(f"Card issued for request {request['id']}.")

            elif choice == "5":
                request_id = input("Request ID: ").strip()
                request = return_card(request_id)
                print(f"Card returned for request {request['id']}.")

            elif choice == "6":
                requests = storage.list_requests()
                if not requests:
                    print("No requests yet.")
                for request in requests:
                    print(_format_request(request))
                    print("-" * 20)

            elif choice == "7":
                storage.save_requests(storage_path)
                print(f"Saved requests to {storage_path}")

            elif choice == "8":
                storage.load_requests(storage_path)
                print(f"Reloaded requests from {storage_path}")

            else:
                print("Invalid option. Please choose a menu number from 1 to 9.")

        except ValueError as exc:
            print(f"Error: {exc}")
        except OSError as exc:
            print(f"File error: {exc}")