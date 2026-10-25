"""
Smart Bus Ticket Booking & Reservation System
Fully debugged, verified, and compliant with all PRD specifications and business rules.
"""

# ==========================================
# 1. DATA INITIALIZATION & DATA STRUCTURES
# ==========================================

# Tuple: Supported cities (immutable reference)
SUPPORTED_CITIES = ("Karachi", "Hyderabad", "Sukkur", "Mirpur Khas", "Lahore")

# List of Dictionaries: Starter routes
routes = [
    {
        "route_id": "R101",
        "departure_city": "Karachi",
        "destination_city": "Hyderabad",
        "departure_time": "08:00 AM",
        "ticket_price": 1200,
        "total_seats": 40,
        "available_seats": 40,
    },
    {
        "route_id": "R102",
        "departure_city": "Karachi",
        "destination_city": "Sukkur",
        "departure_time": "09:30 AM",
        "ticket_price": 2000,
        "total_seats": 36,
        "available_seats": 36,
    },
    {
        "route_id": "R103",
        "departure_city": "Hyderabad",
        "destination_city": "Mirpur Khas",
        "departure_time": "11:00 AM",
        "ticket_price": 800,
        "total_seats": 32,
        "available_seats": 32,
    },
    {
        "route_id": "R104",
        "departure_city": "Karachi",
        "destination_city": "Lahore",
        "departure_time": "07:00 PM",
        "ticket_price": 5000,
        "total_seats": 45,
        "available_seats": 45,
    },
    {
        "route_id": "R105",
        "departure_city": "Sukkur",
        "destination_city": "Hyderabad",
        "departure_time": "02:00 PM",
        "ticket_price": 1500,
        "total_seats": 30,
        "available_seats": 30,
    },
]

# List of Dictionaries: Booking history records
bookings = []

# Set: Tracks issued unique booking IDs
issued_booking_ids = set()

# Counter for sequential IDs
booking_counter = 1001


# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================


def display_main_menu():
    """Displays the standard 8-option console menu."""
    print("\n" + "=" * 32)
    print("  SMART BUS RESERVATION SYSTEM  ")
    print("=" * 32)
    print("1. View Available Routes")
    print("2. Search for a Route")
    print("3. Book a Ticket")
    print("4. View My Bookings")
    print("5. Cancel a Booking")
    print("6. View Seat Availability")
    print("7. Generate Booking Report")
    print("8. Exit")
    print("=" * 32)


def generate_unique_booking_id():
    """Generates a guaranteed unique booking ID and stores it in the set."""
    global booking_counter
    while True:
        candidate_id = f"B{booking_counter}"
        booking_counter += 1
        if candidate_id not in issued_booking_ids:
            issued_booking_ids.add(candidate_id)
            return candidate_id


# ==========================================
# 3. FEATURE IMPLEMENTATIONS
# ==========================================


def view_available_routes():
    """
    Feature 3: View Available Routes
    Uses enumerate() and for loop. Demonstrates 'continue' to filter.
    """
    print("\n--- VIEW ROUTES ---")
    filter_choice = input(
        "Filter options: (1) View All Routes, (2) Only Routes with Seats Available: "
    ).strip()

    print("\nAVAILABLE BUS ROUTES")
    print(
        f"{'No.':<4} {'Route':<7} {'Journey':<26} {'Depart':<10} {'Fare':<10} {'Seats':<14}"
    )
    print("-" * 73)

    displayed_count = 0
    for idx, r in enumerate(routes, start=1):
        # 'continue' skips fully booked routes when filter option 2 is chosen
        if filter_choice == "2" and r["available_seats"] == 0:
            continue

        displayed_count += 1
        journey = f"{r['departure_city']} -> {r['destination_city']}"
        fare_str = f"Rs.{r['ticket_price']}"
        seat_str = f"{r['available_seats']}/{r['total_seats']}"
        if r["available_seats"] == 0:
            seat_str = "Fully Booked"

        print(
            f"{idx:<4} {r['route_id']:<7} {journey:<26} {r['departure_time']:<10} {fare_str:<10} {seat_str:<14}"
        )

    if displayed_count == 0:
        print("No routes match your selection.")


def search_route():
    """
    Feature 4: Search for a Route
    Case-insensitive search by route ID, departure city, or destination city.
    Demonstrates 'break' and 'for-else' construct.
    """
    print("\n--- SEARCH FOR A ROUTE ---")
    term = input("Search by route ID or city: ").strip()

    if not term:
        print("Search term cannot be empty.")
        return

    normalized_term = term.lower()
    matches = []

    # Loop with break and for-else logic
    for r in routes:
        if r["route_id"].lower() == normalized_term:
            matches.append(r)
            break  # Stop search immediately once unique route ID is found
        elif (
            normalized_term in r["departure_city"].lower()
            or normalized_term in r["destination_city"].lower()
        ):
            matches.append(r)
    else:
        # Executes if the loop completed WITHOUT break
        if not matches:
            print(f"No routes found matching '{term}'.")
            return

    # Display results
    print(f"\nFound {len(matches)} matching route(s):")
    for r in matches:
        journey = f"{r['departure_city']} -> {r['destination_city']}"
        seats_text = (
            f"{r['available_seats']} seats available"
            if r["available_seats"] > 0
            else "Fully Booked"
        )
        print(f"{r['route_id']} | {journey} | Rs. {r['ticket_price']} | {seats_text}")


def book_ticket():
    """
    Feature 5: Book a Ticket
    Validates passenger name, age, route ID, and seat availability.
    Deducts seats and saves booking atomically upon passing all checks.
    """
    print("\n--- BOOK A TICKET ---")

    # BR-01: Name validation
    name = input("Enter passenger name: ").strip()
    if not name:
        print("Validation Error: Passenger name cannot be blank.")
        return

    # BR-02: Age validation
    age_input = input("Enter passenger age: ").strip()
    if not age_input.isdigit() or int(age_input) <= 0:
        print("Validation Error: Age must be a positive whole number.")
        return
    age = int(age_input)

    # BR-03: Route validation
    route_code = input("Enter route ID (e.g., R101): ").strip().upper()
    selected_route = None
    for r in routes:
        if r["route_id"] == route_code:
            selected_route = r
            break

    if selected_route is None:
        print(f"Validation Error: Route ID '{route_code}' does not exist.")
        return

    # BR-04 & BR-05: Seat validation & availability check
    seats_input = input("Enter number of seats to book: ").strip()
    if not seats_input.isdigit() or int(seats_input) <= 0:
        print(
            "Validation Error: Seat quantity must be a positive integer greater than zero."
        )
        return
    requested_seats = int(seats_input)

    if requested_seats > selected_route["available_seats"]:
        print(
            f"Validation Error: Cannot book {requested_seats} seats. Only {selected_route['available_seats']} seats available."
        )
        return

    # BR-06, BR-07, BR-08: Confirm booking and update availability
    booking_id = generate_unique_booking_id()
    total_fare = selected_route["ticket_price"] * requested_seats

    booking_record = {
        "booking_id": booking_id,
        "passenger_name": name,
        "passenger_age": age,
        "route_id": selected_route["route_id"],
        "seats": requested_seats,
        "total_fare": total_fare,
        "status": "Confirmed",
    }

    selected_route["available_seats"] -= requested_seats
    bookings.append(booking_record)

    # Output formatted confirmation
    print("\nBooking confirmed!")
    print(f"Booking ID: {booking_record['booking_id']}")
    print(f"Passenger: {booking_record['passenger_name']}")
    print(
        f"Route: {selected_route['route_id']} ({selected_route['departure_city']} -> {selected_route['destination_city']})"
    )
    print(f"Seats booked: {booking_record['seats']}")
    print(f"Fare per seat: Rs. {selected_route['ticket_price']}")
    print(f"Total fare: Rs. {booking_record['total_fare']}")
    print(f"Status: {booking_record['status']}")


def view_my_bookings():
    """
    Feature 6: View My Bookings
    Enumerates all booking records, including cancelled ones.
    """
    print("\n--- BOOKING HISTORY ---")
    if not bookings:
        print("No bookings found.")
        return

    print(
        f"{'No.':<4} {'Booking ID':<12} {'Passenger':<16} {'Route':<8} {'Seats':<7} {'Fare':<12} {'Status':<10}"
    )
    print("-" * 72)
    for idx, b in enumerate(bookings, start=1):
        fare_str = f"Rs. {b['total_fare']}"
        print(
            f"{idx:<4} {b['booking_id']:<12} {b['passenger_name']:<16} {b['route_id']:<8} {b['seats']:<7} {fare_str:<12} {b['status']:<10}"
        )


def cancel_booking():
    """
    Feature 7: Cancel a Booking
    Validates booking status, restores seats once, and sets status to Cancelled.
    Demonstrates for-else search logic.
    """
    print("\n--- CANCEL A BOOKING ---")
    target_id = input("Enter booking ID to cancel: ").strip().upper()

    target_booking = None
    for b in bookings:
        if b["booking_id"] == target_id:
            target_booking = b
            break
    else:
        # Executes only if loop completes without encountering break
        print(f"Cancellation Error: Booking ID '{target_id}' not found.")
        return

    # Check status
    if target_booking["status"] == "Cancelled":
        print(
            f"Cancellation Error: Booking {target_id} is already cancelled. No seats restored."
        )
        return

    # Restore seats to route safely
    for r in routes:
        if r["route_id"] == target_booking["route_id"]:
            # BR-13: Keep 0 <= available_seats <= total_seats
            r["available_seats"] = min(
                r["total_seats"], r["available_seats"] + target_booking["seats"]
            )
            target_booking["status"] = "Cancelled"

            print(f"\nBooking {target_id} has been cancelled.")
            print(f"Seats restored: {target_booking['seats']}")
            print(f"Route {r['route_id']} available seats: {r['available_seats']}")
            return

    print("Error: Associated route for this booking could not be located.")


def view_seat_availability():
    """
    Feature 8: View Seat Availability
    Shows seat ratios, classifies status, and offers an availability filter.
    """
    print("\n--- SEAT AVAILABILITY ---")
    filter_choice = input(
        "Filter options: (1) View All Routes, (2) Only Routes with Seats Available: "
    ).strip()

    print(f"\n{'Route ID':<10} {'Journey':<26} {'Available/Total':<18} {'Status':<16}")
    print("-" * 70)

    for r in routes:
        if filter_choice == "2" and r["available_seats"] == 0:
            continue

        if r["available_seats"] == r["total_seats"]:
            status_text = "Available"
        elif r["available_seats"] == 0:
            status_text = "Fully Booked"
        else:
            status_text = "Partially Booked"

        journey = f"{r['departure_city']} -> {r['destination_city']}"
        seat_ratio = f"{r['available_seats']} / {r['total_seats']}"
        print(f"{r['route_id']:<10} {journey:<26} {seat_ratio:<18} {status_text:<16}")


def generate_booking_report():
    """
    Feature 9 & 10: Generate Booking Report and Route Schedule
    Uses nested loops to aggregate route bookings and builds departure schedule.
    """
    print("\n====================================")
    print("           BOOKING REPORT           ")
    print("====================================")

    total_created = len(bookings)
    confirmed_count = 0
    cancelled_count = 0
    seats_reserved = 0
    confirmed_revenue = 0

    # Calculate report fields
    for b in bookings:
        if b["status"] == "Confirmed":
            confirmed_count += 1
            seats_reserved += b["seats"]
            confirmed_revenue += b["total_fare"]
        elif b["status"] == "Cancelled":
            cancelled_count += 1

    fully_booked_routes = 0
    for r in routes:
        if r["available_seats"] == 0:
            fully_booked_routes += 1

    print(f"Total bookings created: {total_created}")
    print(f"Confirmed bookings:     {confirmed_count}")
    print(f"Cancelled bookings:     {cancelled_count}")
    print(f"Seats currently reserved: {seats_reserved}")
    print(f"Confirmed revenue:      Rs. {confirmed_revenue:,}")
    print(f"Fully booked routes:    {fully_booked_routes}")

    # Nested Loop: Confirmed bookings grouped by route
    print("\n--- CONFIRMED BOOKINGS BREAKDOWN BY ROUTE ---")
    for r in routes:
        print(
            f"\nRoute {r['route_id']} ({r['departure_city']} -> {r['destination_city']}):"
        )
        route_confirmed_found = False
        for b in bookings:
            if b["route_id"] == r["route_id"] and b["status"] == "Confirmed":
                print(
                    f"  - Booking {b['booking_id']}: {b['passenger_name']}, {b['seats']} seat(s), Fare: Rs. {b['total_fare']}"
                )
                route_confirmed_found = True
        if not route_confirmed_found:
            print("  - No active confirmed bookings.")

    # Feature 10: Route Schedule by Departure City
    print("\n====================================")
    print("   ROUTE SCHEDULE BY DEPARTURE CITY ")
    print("====================================")
    for city in SUPPORTED_CITIES:
        print(f"\n{city}")
        has_departures = False
        for r in routes:
            if r["departure_city"] == city:
                print(
                    f"  {r['route_id']} -> {r['destination_city']} | {r['departure_time']}"
                )
                has_departures = True
        if not has_departures:
            print("  No scheduled departures.")


# ==========================================
# 4. MAIN MENU DRIVER LOOP
# ==========================================


def main():
    """Main application loop."""
    while True:
        display_main_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            view_available_routes()
        elif choice == "2":
            search_route()
        elif choice == "3":
            book_ticket()
        elif choice == "4":
            view_my_bookings()
        elif choice == "5":
            cancel_booking()
        elif choice == "6":
            view_seat_availability()
        elif choice == "7":
            generate_booking_report()
        elif choice == "8":
            print("\nThank you for using Smart Bus Reservation System. Goodbye!\n")
            break
        else:
            print("\n[!] Invalid selection. Please enter a number between 1 and 8.")
            continue


if __name__ == "__main__":
    main()
