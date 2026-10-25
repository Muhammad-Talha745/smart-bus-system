from flask import Flask, render_template_string, request

app = Flask(__name__)

# ==========================================
# DATA STRUCTURES
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
booking_counter = 1001

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Bus Ticket Reservation</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-800 font-sans">
    <header class="bg-blue-900 text-white py-6 shadow-md">
        <div class="max-w-6xl mx-auto px-4 flex justify-between items-center">
            <h1 class="text-2xl font-bold tracking-wide">🚌 Smart Bus Reservation System</h1>
            <span class="bg-emerald-600 text-xs px-3 py-1 rounded-full font-semibold">Live & Active</span>
        </div>
    </header>

    <main class="max-w-6xl mx-auto px-4 py-8 grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- Booking Form -->
        <section class="bg-white p-6 rounded-xl shadow-sm border border-slate-200 h-fit">
            <h2 class="text-xl font-bold mb-4 text-blue-900 border-b pb-2">Book a Ticket</h2>
            <form method="POST" action="" class="space-y-4">
                <input type="hidden" name="action_type" value="book">
                <div>
                    <label class="block text-sm font-semibold mb-1">Passenger Name</label>
                    <input type="text" name="name" required class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-blue-500">
                </div>
                <div>
                    <label class="block text-sm font-semibold mb-1">Age</label>
                    <input type="number" name="age" min="1" required class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-blue-500">
                </div>
                <div>
                    <label class="block text-sm font-semibold mb-1">Select Route</label>
                    <select name="route_id" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-blue-500">
                        {% for r in routes %}
                        <option value="{{ r.route_id }}" {% if r.available_seats == 0 %}disabled{% endif %}>
                            {{ r.route_id }} ({{ r.departure_city }} ➔ {{ r.destination_city }}) - Rs.{{ r.ticket_price }} [{{ r.available_seats }} left]
                        </option>
                        {% endfor %}
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-semibold mb-1">Seats Quantity</label>
                    <input type="number" name="seats" min="1" max="10" value="1" required class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-blue-500">
                </div>
                <button type="submit" class="w-full bg-blue-700 hover:bg-blue-800 text-white font-bold py-2.5 px-4 rounded-lg transition duration-200 shadow">
                    Confirm Reservation
                </button>
            </form>
        </section>

        <!-- Right Panels: Routes & Bookings -->
        <section class="md:col-span-2 space-y-8">
            <!-- Available Routes -->
            <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                <h2 class="text-xl font-bold mb-4 text-blue-900 border-b pb-2">Available Routes</h2>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-sm">
                        <thead>
                            <tr class="border-b bg-slate-50 text-slate-600">
                                <th class="p-2">Route</th>
                                <th class="p-2">Journey</th>
                                <th class="p-2">Time</th>
                                <th class="p-2">Fare</th>
                                <th class="p-2">Available Seats</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for r in routes %}
                            <tr class="border-b hover:bg-slate-50">
                                <td class="p-2 font-mono font-bold text-blue-700">{{ r.route_id }}</td>
                                <td class="p-2">{{ r.departure_city }} ➔ {{ r.destination_city }}</td>
                                <td class="p-2">{{ r.departure_time }}</td>
                                <td class="p-2">Rs. {{ r.ticket_price }}</td>
                                <td class="p-2">
                                    {% if r.available_seats == 0 %}
                                    <span class="text-red-600 font-bold">Fully Booked</span>
                                    {% else %}
                                    <span class="text-emerald-700 font-semibold">{{ r.available_seats }} / {{ r.total_seats }}</span>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Booking History -->
            <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                <h2 class="text-xl font-bold mb-4 text-blue-900 border-b pb-2">Booking History</h2>
                {% if not bookings %}
                <p class="text-sm text-slate-500 py-2">No bookings placed yet. Book a seat using the form!</p>
                {% else %}
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-sm">
                        <thead>
                            <tr class="border-b bg-slate-50 text-slate-600">
                                <th class="p-2">ID</th>
                                <th class="p-2">Passenger</th>
                                <th class="p-2">Route</th>
                                <th class="p-2">Seats</th>
                                <th class="p-2">Total Fare</th>
                                <th class="p-2">Status</th>
                                <th class="p-2">Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for b in bookings %}
                            <tr class="border-b">
                                <td class="p-2 font-mono font-bold">{{ b.booking_id }}</td>
                                <td class="p-2">{{ b.passenger_name }}</td>
                                <td class="p-2">{{ b.route_id }}</td>
                                <td class="p-2">{{ b.seats }}</td>
                                <td class="p-2">Rs. {{ b.total_fare }}</td>
                                <td class="p-2">
                                    <span class="px-2 py-0.5 rounded text-xs font-bold {% if b.status == 'Confirmed' %}bg-green-100 text-green-800{% else %}bg-red-100 text-red-800{% endif %}">
                                        {{ b.status }}
                                    </span>
                                </td>
                                <td class="p-2">
                                    {% if b.status == 'Confirmed' %}
                                    <form method="POST" action="">
                                        <input type="hidden" name="action_type" value="cancel">
                                        <input type="hidden" name="booking_id" value="{{ b.booking_id }}">
                                        <button type="submit" class="text-xs text-red-600 hover:underline font-semibold">Cancel</button>
                                    </form>
                                    {% else %}
                                    <span class="text-xs text-slate-400">Cancelled</span>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% endif %}
            </div>
        </section>
    </main>
</body>
</html>
"""


# Catch-all route prevents 404 regardless of how Vercel rewrites internal paths
@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def index(path):
    global booking_counter
    if request.method == "POST":
        action = request.form.get("action_type")

        # Handle Booking
        if action == "book":
            name = request.form.get("name", "").strip()
            age_raw = request.form.get("age", "0")
            route_id = request.form.get("route_id", "")
            seats_raw = request.form.get("seats", "0")

            if age_raw.isdigit() and seats_raw.isdigit():
                age = int(age_raw)
                seats = int(seats_raw)
                route = next((r for r in routes if r["route_id"] == route_id), None)
                if route and 0 < seats <= route["available_seats"] and name and age > 0:
                    booking_id = f"B{booking_counter}"
                    booking_counter += 1
                    route["available_seats"] -= seats
                    bookings.insert(
                        0,
                        {
                            "booking_id": booking_id,
                            "passenger_name": name,
                            "passenger_age": age,
                            "route_id": route_id,
                            "seats": seats,
                            "total_fare": route["ticket_price"] * seats,
                            "status": "Confirmed",
                        },
                    )

        # Handle Cancellation
        elif action == "cancel":
            b_id = request.form.get("booking_id")
            booking = next((b for b in bookings if b["booking_id"] == b_id), None)
            if booking and booking["status"] == "Confirmed":
                route = next(
                    (r for r in routes if r["route_id"] == booking["route_id"]), None
                )
                if route:
                    route["available_seats"] = min(
                        route["total_seats"],
                        route["available_seats"] + booking["seats"],
                    )
                booking["status"] = "Cancelled"

    return render_template_string(HTML_TEMPLATE, routes=routes, bookings=bookings)


if __name__ == "__main__":
    app.run(debug=True)
