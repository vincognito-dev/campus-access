import os

from campus_access.workflow import (
    approve_request,
    create_request,
    get_request,
    issue_card,
    list_requests,
    load_requests,
    return_card,
    save_requests,
)


def run_menu() -> None:
    """Run a simple interactive campus access-card request manager."""
    storage_path = os.path.join(os.getcwd(), "campus_requests.json")

    while True:
        print("\nCampus Access Card Manager")
        print("1. Create request")
        print("2. View request")
        print("3. Approve request")
        print("4. Issue card")
        print("5. Return card")
        print("6. List requests")
        print("7. Save to JSON")
        print("8. Reload from JSON")
        print("9. Quit")

        choice = input("Select an option: ").strip()
        if choice.lower() in {"q", "quit", "exit"}:
            print("Goodbye.")
            return

        try:
            option = int(choice)
        except ValueError:
            print("Invalid option. Please choose a menu number or 'quit'.")
            continue

        if option == 1:
            fellow_id = input("Fellow ID: ").strip()
            card_type = input("Card type (visitor/student/staff): ").strip().lower()
            try:
                request = create_request(fellow_id, card_type)
                print(f"Request {request['id']} created for {request['fellow_id']} ({request['card_type']})")
            except ValueError as exc:
                print(f"Error: {exc}")

        elif option == 2:
            request_id = input("Request ID: ").strip()
            try:
                request = get_request(request_id)
                print(request)
            except ValueError as exc:
                print(f"Error: {exc}")

        elif option == 3:
            request_id = input("Request ID: ").strip()
            approved_by = input("Approver ID: ").strip()
            try:
                request = approve_request(request_id, approved_by)
                print(f"Request {request['id']} approved by {request['approved_by']}.")
            except ValueError as exc:
                print(f"Error: {exc}")

        elif option == 4:
            request_id = input("Request ID: ").strip()
            try:
                request = issue_card(request_id)
                print(f"Card issued for request {request['id']}.")
            except ValueError as exc:
                print(f"Error: {exc}")

        elif option == 5:
            request_id = input("Request ID: ").strip()
            try:
                request = return_card(request_id)
                print(f"Card returned for request {request['id']}.")
            except ValueError as exc:
                print(f"Error: {exc}")

        elif option == 6:
            print(list_requests())

        elif option == 7:
            try:
                save_requests(storage_path)
                print(f"Saved requests to {storage_path}")
            except OSError as exc:
                print(f"Save failed: {exc}")

        elif option == 8:
            try:
                load_requests(storage_path)
                print(f"Reloaded requests from {storage_path}")
            except (FileNotFoundError, ValueError, OSError) as exc:
                print(f"Reload failed: {exc}")

        elif option == 9:
            print("Goodbye.")
            return

        else:
            print("Invalid option. Please choose a valid menu number.")
