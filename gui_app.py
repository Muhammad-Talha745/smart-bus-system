"""
Smart Bus Ticket Booking & Reservation System - Graphical User Interface (GUI)
Built using Python's built-in Tkinter library (No external dependencies needed).
"""

import tkinter as tk
from tkinter import ttk, messagebox

# ==========================================
# 1. CORE DATA STRUCTURES
# ==========================================

SUPPORTED_CITIES = ("Karachi", "Hyderabad", "Sukkur", "Mirpur Khas", "Lahore")

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

bookings = []
issued_booking_ids = set()
booking_counter = 1001


def generate_unique_booking_id():
    global booking_counter
    while True:
        candidate_id = f"B{booking_counter}"
        booking_counter += 1
        if candidate_id not in issued_booking_ids:
            issued_booking_ids.add(candidate_id)
            return candidate_id


# ==========================================
# 2. GUI APPLICATION CLASS
# ==========================================


class SmartBusApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Bus Ticket Booking & Reservation System")
        self.geometry("900x620")
        self.minsize(800, 550)

        # Style configuration
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Header Banner
        header = tk.Frame(self, bg="#1e3a8a", height=60)
        header.pack(fill="x", side="top")
        title_label = tk.Label(
            header,
            text="🚌 SMART BUS RESERVATION SYSTEM",
            font=("Helvetica", 16, "bold"),
            fg="white",
            bg="#1e3a8a",
        )
        title_label.pack(pady=15)

        # Tab Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create 4 tabs
        self.tab_routes = ttk.Frame(self.notebook)
        self.tab_book = ttk.Frame(self.notebook)
        self.tab_bookings = ttk.Frame(self.notebook)
        self.tab_reports = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_routes, text="  Bus Routes  ")
        self.notebook.add(self.tab_book, text="  Book Ticket  ")
        self.notebook.add(self.tab_bookings, text="  Bookings & Cancel  ")
        self.notebook.add(self.tab_reports, text="  Reports & Schedule  ")

        # Build each tab view
        self.build_routes_tab()
        self.build_booking_tab()
        self.build_my_bookings_tab()
        self.build_reports_tab()

    # ----------------------------------------------------
    # TAB 1: VIEW & SEARCH ROUTES
    # ----------------------------------------------------
    def build_routes_tab(self):
        # Search Bar
        search_frame = ttk.LabelFrame(
            self.tab_routes, text=" Search Routes ", padding=10
        )
        search_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(search_frame, text="Search (City or Route ID):").pack(
            side="left", padx=5
        )
        self.search_entry = ttk.Entry(search_frame, width=25)
        self.search_entry.pack(side="left", padx=5)

        ttk.Button(search_frame, text="Search", command=self.apply_route_search).pack(
            side="left", padx=5
        )
        ttk.Button(
            search_frame, text="Reset / View All", command=self.refresh_routes_table
        ).pack(side="left", padx=5)

        # Routes Table
        table_frame = ttk.Frame(self.tab_routes)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("id", "journey", "time", "fare", "seats", "status")
        self.routes_tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=10
        )

        self.routes_tree.heading("id", text="Route ID")
        self.routes_tree.heading("journey", text="Journey")
        self.routes_tree.heading("time", text="Departure Time")
        self.routes_tree.heading("fare", text="Fare")
        self.routes_tree.heading("seats", text="Seats Available")
        self.routes_tree.heading("status", text="Status")

        self.routes_tree.column("id", width=80, anchor="center")
        self.routes_tree.column("journey", width=220)
        self.routes_tree.column("time", width=120, anchor="center")
        self.routes_tree.column("fare", width=100, anchor="center")
        self.routes_tree.column("seats", width=130, anchor="center")
        self.routes_tree.column("status", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.routes_tree.yview
        )
        self.routes_tree.configure(yscrollcommand=scrollbar.set)
        self.routes_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.refresh_routes_table()

    def refresh_routes_table(self, filtered_list=None):
        for item in self.routes_tree.get_children():
            self.routes_tree.delete(item)

        target_routes = filtered_list if filtered_list is not None else routes
        for r in target_routes:
            status = (
                "Fully Booked"
                if r["available_seats"] == 0
                else (
                    "Available"
                    if r["available_seats"] == r["total_seats"]
                    else "Partially Booked"
                )
            )
            seats_str = f"{r['available_seats']} / {r['total_seats']}"
            journey = f"{r['departure_city']} ➔ {r['destination_city']}"
            self.routes_tree.insert(
                "",
                "end",
                values=(
                    r["route_id"],
                    journey,
                    r["departure_time"],
                    f"Rs. {r['ticket_price']}",
                    seats_str,
                    status,
                ),
            )

    def apply_route_search(self):
        query = self.search_entry.get().strip().lower()
        if not query:
            self.refresh_routes_table()
            return

        matches = []
        for r in routes:
            if (
                query == r["route_id"].lower()
                or query in r["departure_city"].lower()
                or query in r["destination_city"].lower()
            ):
                matches.append(r)
        self.refresh_routes_table(matches)

    # ----------------------------------------------------
    # TAB 2: BOOK A TICKET
    # ----------------------------------------------------
    def build_booking_tab(self):
        card = ttk.LabelFrame(
            self.tab_book, text=" Passenger & Journey Details ", padding=20
        )
        card.pack(fill="x", padx=40, pady=20)

        # Passenger Name
        ttk.Label(card, text="Passenger Full Name:").grid(
            row=0, column=0, sticky="w", pady=8
        )
        self.name_entry = ttk.Entry(card, width=35)
        self.name_entry.grid(row=0, column=1, sticky="w", pady=8)

        # Passenger Age
        ttk.Label(card, text="Passenger Age:").grid(row=1, column=0, sticky="w", pady=8)
        self.age_entry = ttk.Entry(card, width=15)
        self.age_entry.grid(row=1, column=1, sticky="w", pady=8)

        # Select Route
        ttk.Label(card, text="Select Route:").grid(row=2, column=0, sticky="w", pady=8)
        self.route_var = tk.StringVar()
        self.route_dropdown = ttk.Combobox(
            card, textvariable=self.route_var, width=32, state="readonly"
        )
        self.update_route_dropdown()
        self.route_dropdown.grid(row=2, column=1, sticky="w", pady=8)

        # Number of Seats
        ttk.Label(card, text="Number of Seats:").grid(
            row=3, column=0, sticky="w", pady=8
        )
        self.seats_spinbox = ttk.Spinbox(card, from_=1, to=50, width=10)
        self.seats_spinbox.set(1)
        self.seats_spinbox.grid(row=3, column=1, sticky="w", pady=8)

        # Book Button
        book_btn = tk.Button(
            card,
            text="Confirm & Book Ticket",
            bg="#15803d",
            fg="white",
            font=("Helvetica", 10, "bold"),
            padx=15,
            pady=8,
            command=self.handle_booking,
        )
        book_btn.grid(row=4, column=0, columnspan=2, pady=15)

    def update_route_dropdown(self):
        options = [
            f"{r['route_id']} - {r['departure_city']} to {r['destination_city']} (Rs.{r['ticket_price']})"
            for r in routes
        ]
        self.route_dropdown["values"] = options
        if options:
            self.route_dropdown.current(0)

    def handle_booking(self):
        name = self.name_entry.get().strip()
        age_str = self.age_entry.get().strip()
        selected_route_text = self.route_var.get()
        seats_str = self.seats_spinbox.get().strip()

        # Validation
        if not name:
            messagebox.showerror("Validation Error", "Passenger name cannot be blank.")
            return

        if not age_str.isdigit() or int(age_str) <= 0:
            messagebox.showerror("Validation Error", "Age must be a positive integer.")
            return

        if not seats_str.isdigit() or int(seats_str) <= 0:
            messagebox.showerror(
                "Validation Error", "Seat quantity must be a positive number."
            )
            return

        route_id = selected_route_text.split(" - ")[0]
        selected_route = next((r for r in routes if r["route_id"] == route_id), None)
        requested_seats = int(seats_str)

        if requested_seats > selected_route["available_seats"]:
            messagebox.showwarning(
                "Unavailable",
                f"Only {selected_route['available_seats']} seat(s) remain on {route_id}.",
            )
            return

        # Commit Booking
        b_id = generate_unique_booking_id()
        total_fare = selected_route["ticket_price"] * requested_seats

        record = {
            "booking_id": b_id,
            "passenger_name": name,
            "passenger_age": int(age_str),
            "route_id": route_id,
            "seats": requested_seats,
            "total_fare": total_fare,
            "status": "Confirmed",
        }
        selected_route["available_seats"] -= requested_seats
        bookings.append(record)

        # Reset form & notify
        self.name_entry.delete(0, "end")
        self.age_entry.delete(0, "end")
        self.seats_spinbox.set(1)

        self.refresh_routes_table()
        self.refresh_bookings_table()
        self.refresh_reports()

        messagebox.showinfo(
            "Booking Successful!",
            f"Booking ID: {b_id}\nPassenger: {name}\nSeats: {requested_seats}\nTotal Fare: Rs. {total_fare}",
        )

    # ----------------------------------------------------
    # TAB 3: BOOKING HISTORY & CANCELLATION
    # ----------------------------------------------------
    def build_my_bookings_tab(self):
        top_bar = ttk.Frame(self.tab_bookings, padding=10)
        top_bar.pack(fill="x")

        cancel_btn = tk.Button(
            top_bar,
            text="Cancel Selected Booking",
            bg="#b91c1c",
            fg="white",
            font=("Helvetica", 9, "bold"),
            padx=10,
            pady=5,
            command=self.handle_cancellation,
        )
        cancel_btn.pack(side="left")

        # Bookings Table
        columns = ("id", "passenger", "route", "seats", "fare", "status")
        self.bookings_tree = ttk.Treeview(
            self.tab_bookings, columns=columns, show="headings", height=12
        )

        self.bookings_tree.heading("id", text="Booking ID")
        self.bookings_tree.heading("passenger", text="Passenger Name")
        self.bookings_tree.heading("route", text="Route ID")
        self.bookings_tree.heading("seats", text="Seats")
        self.bookings_tree.heading("fare", text="Total Fare")
        self.bookings_tree.heading("status", text="Status")

        self.bookings_tree.column("id", width=100, anchor="center")
        self.bookings_tree.column("passenger", width=180)
        self.bookings_tree.column("route", width=90, anchor="center")
        self.bookings_tree.column("seats", width=80, anchor="center")
        self.bookings_tree.column("fare", width=110, anchor="center")
        self.bookings_tree.column("status", width=120, anchor="center")

        self.bookings_tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.refresh_bookings_table()

    def refresh_bookings_table(self):
        for item in self.bookings_tree.get_children():
            self.bookings_tree.delete(item)

        for b in bookings:
            self.bookings_tree.insert(
                "",
                "end",
                values=(
                    b["booking_id"],
                    b["passenger_name"],
                    b["route_id"],
                    b["seats"],
                    f"Rs. {b['total_fare']}",
                    b["status"],
                ),
            )

    def handle_cancellation(self):
        selected_item = self.bookings_tree.selection()
        if not selected_item:
            messagebox.showwarning(
                "Select Booking",
                "Please select a booking record from the table to cancel.",
            )
            return

        b_values = self.bookings_tree.item(selected_item)["values"]
        b_id = b_values[0]

        target_booking = next((b for b in bookings if b["booking_id"] == b_id), None)
        if not target_booking:
            return

        if target_booking["status"] == "Cancelled":
            messagebox.showinfo("Notice", f"Booking {b_id} is already cancelled.")
            return

        # Restore seats
        route_obj = next(
            (r for r in routes if r["route_id"] == target_booking["route_id"]), None
        )
        if route_obj:
            route_obj["available_seats"] = min(
                route_obj["total_seats"],
                route_obj["available_seats"] + target_booking["seats"],
            )

        target_booking["status"] = "Cancelled"

        self.refresh_routes_table()
        self.refresh_bookings_table()
        self.refresh_reports()

        messagebox.showinfo(
            "Cancelled",
            f"Booking {b_id} cancelled successfully.\n{target_booking['seats']} seats restored to {route_obj['route_id']}.",
        )

    # ----------------------------------------------------
    # TAB 4: REPORTS & SCHEDULE
    # ----------------------------------------------------
    def build_reports_tab(self):
        self.report_box = tk.Text(
            self.tab_reports, font=("Courier", 10), padx=15, pady=15
        )
        self.report_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh_reports()

    def refresh_reports(self):
        self.report_box.delete("1.0", "end")

        total_created = len(bookings)
        confirmed_count = sum(1 for b in bookings if b["status"] == "Confirmed")
        cancelled_count = sum(1 for b in bookings if b["status"] == "Cancelled")
        seats_reserved = sum(b["seats"] for b in bookings if b["status"] == "Confirmed")
        confirmed_revenue = sum(
            b["total_fare"] for b in bookings if b["status"] == "Confirmed"
        )
        fully_booked = sum(1 for r in routes if r["available_seats"] == 0)

        report_txt = "=" * 50 + "\n"
        report_txt += "             SMART BUS BOOKING REPORT             \n"
        report_txt += "=" * 50 + "\n\n"
        report_txt += f"Total Bookings Created:   {total_created}\n"
        report_txt += f"Confirmed Bookings:       {confirmed_count}\n"
        report_txt += f"Cancelled Bookings:       {cancelled_count}\n"
        report_txt += f"Seats Currently Reserved: {seats_reserved}\n"
        report_txt += f"Confirmed Total Revenue:  Rs. {confirmed_revenue:,}\n"
        report_txt += f"Fully Booked Routes:      {fully_booked}\n\n"

        report_txt += "=" * 50 + "\n"
        report_txt += "          ROUTE SCHEDULE BY DEPARTURE CITY        \n"
        report_txt += "=" * 50 + "\n"

        for city in SUPPORTED_CITIES:
            report_txt += f"\n📍 {city.upper()}\n"
            departures = [r for r in routes if r["departure_city"] == city]
            if departures:
                for d in departures:
                    report_txt += f"   • {d['route_id']} -> {d['destination_city']} | Time: {d['departure_time']} | Fare: Rs. {d['ticket_price']}\n"
            else:
                report_txt += "   • No scheduled departures.\n"

        self.report_box.insert("1.0", report_txt)


# ==========================================
# 3. ENTRY POINT
# ==========================================
if __name__ == "__main__":
    app = SmartBusApp()
    app.mainloop()
