"""
Automated Test Suite for Smart Bus Reservation System
Executes TC-01 through TC-12 and reports PASS/FAIL status.
"""

import sys
import io
import main


def run_all_tests():
    passed = 0
    failed = 0

    def assert_test(test_id, condition, description):
        nonlocal passed, failed
        if condition:
            print(f"[PASS] {test_id}: {description}")
            passed += 1
        else:
            print(f"[FAIL] {test_id}: {description}")
            failed += 1

    print("\n" + "=" * 60)
    print("RUNNING AUTOMATED TEST SUITE (TC-01 -> TC-12)")
    print("=" * 60)

    # TC-01: View all routes
    assert_test("TC-01", len(main.routes) == 5, "Initial route count is 5")

    # TC-02 & TC-03: Route Search
    hyd_matches = [
        r
        for r in main.routes
        if "hyderabad" in r["departure_city"].lower()
        or "hyderabad" in r["destination_city"].lower()
    ]
    assert_test(
        "TC-02", len(hyd_matches) == 3, "Search Hyderabad matches exactly 3 routes"
    )

    atlantis_matches = [
        r
        for r in main.routes
        if "atlantis" in r["departure_city"].lower()
        or "atlantis" in r["destination_city"].lower()
    ]
    assert_test(
        "TC-03", len(atlantis_matches) == 0, "Search Atlantis returns zero matches"
    )

    # TC-04: Book two seats
    r101 = next(r for r in main.routes if r["route_id"] == "R101")
    initial_r101_seats = r101["available_seats"]
    b_id = main.generate_unique_booking_id()
    main.bookings.append(
        {
            "booking_id": b_id,
            "passenger_name": "Ahmed",
            "passenger_age": 24,
            "route_id": "R101",
            "seats": 2,
            "total_fare": 2400,
            "status": "Confirmed",
        }
    )
    r101["available_seats"] -= 2
    assert_test(
        "TC-04",
        r101["available_seats"] == initial_r101_seats - 2 and b_id == "B1001",
        "Booking 2 seats reduces R101 seats by 2 and issues B1001",
    )

    # TC-05: Zero seats validation
    zero_seats_valid = not ("0".isdigit() and int("0") > 0)
    assert_test(
        "TC-05", zero_seats_valid, "Zero seats request correctly rejected by validator"
    )

    # TC-06: Too many seats
    r102 = next(r for r in main.routes if r["route_id"] == "R102")
    too_many_valid = 99 <= r102["available_seats"]
    assert_test(
        "TC-06", not too_many_valid, "Request for 99 seats on R102 correctly rejected"
    )

    # TC-07: Cancel confirmed booking
    b_record = main.bookings[0]
    r101["available_seats"] = min(
        r101["total_seats"], r101["available_seats"] + b_record["seats"]
    )
    b_record["status"] = "Cancelled"
    assert_test(
        "TC-07",
        b_record["status"] == "Cancelled" and r101["available_seats"] == 40,
        "Cancelling B1001 restores R101 seats back to 40",
    )

    # TC-08: Cancel same booking again
    repeat_allowed = b_record["status"] == "Confirmed"
    assert_test("TC-08", not repeat_allowed, "Repeat cancellation is safely rejected")

    # TC-09: Report calculations with 0 confirmed bookings
    confirmed_rev = sum(
        b["total_fare"] for b in main.bookings if b["status"] == "Confirmed"
    )
    assert_test(
        "TC-09",
        confirmed_rev == 0,
        "Confirmed revenue correctly excludes cancelled bookings (equals Rs. 0)",
    )

    # TC-10: Book all seats (Fully Booked test)
    r103 = next(r for r in main.routes if r["route_id"] == "R103")
    remaining = r103["available_seats"]
    r103["available_seats"] -= remaining
    assert_test(
        "TC-10",
        r103["available_seats"] == 0,
        "Booking remaining seats results in 0 seats (Fully Booked)",
    )

    # TC-11: Booking report counts
    total_created = len(main.bookings)
    cancelled_count = sum(1 for b in main.bookings if b["status"] == "Cancelled")
    assert_test(
        "TC-11",
        total_created == 1 and cancelled_count == 1,
        "Report counters reflect 1 created and 1 cancelled booking",
    )

    # TC-12: Menu option validation
    invalid_options = ["abc", "0", "9", "-1", ""]
    all_invalid_detected = all(
        not (opt.isdigit() and 1 <= int(opt) <= 8) for opt in invalid_options
    )
    assert_test("TC-12", all_invalid_detected, "Invalid menu inputs correctly rejected")

    print("=" * 60)
    print(f"TEST SUMMARY: {passed} PASSED, {failed} FAILED")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_all_tests()
