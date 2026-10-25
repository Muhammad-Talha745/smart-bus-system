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
<body class="bg-slate-100 text-slate-900 font-sans min-h-screen">
    <!-- Header -->
    <header class="bg-blue-900 text-white py-5 shadow-lg">
        <div class="max-w-6xl mx-auto px-4 flex justify-between items-center">
            <div class="flex items-center space-x-3">
                <span class="text-3xl">🚌</span>
                <div>
                    <h1 class="text-2xl font-bold tracking-wide">Smart Bus Reservation System</h1>
                    <p class="text-xs text-blue-200">Official Ticket Booking Portal</p>
                </div>
            </div>
            <span class="bg-emerald-500 text-white text-xs px-3 py-1.5 rounded-full font-bold shadow-sm">
                ● Live & Active
            </span>
        </div>
    </header>

    <main class="max-w-6xl mx-auto px-4 py-8 grid grid-cols-1 md:grid-cols-3 gap-8">
        
        <!-- Left Column: Booking Form -->
        <section class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 h-fit">
            <h2 class="text-xl font-bold mb-4 text-blue-900 border-b pb-2 flex items-center">
                <span>🎫 Book a Ticket</span>
            </h2>

            {% if alert_message %}
            <div class="mb-4 p-3 rounded-lg text-sm font-semibold {{ alert_color }}">
                {{ alert_message }}
            </div>
            {% endif %}

            <form method="POST" action="" class="space-y-4">
                <input type="hidden" name="action_type" value="book">
                
                <div>
                    <label class="block text-sm font-semibold text-slate-700 mb-1">Passenger Name</label>
                    <input type="text" name="name" placeholder="e.g. Ahmed Ali" required 
                           class="w-full bg-white text-slate-900 border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm">
                </div>

                <div>
                    <label class="block text-sm font-semibold text-slate-700 mb-1">Passenger Age</label>
                    <input type="number" name="age" min="1" max="120" placeholder="e.g. 25" required 
                           class="w-full bg-white text-slate-900 border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm">
                </div>

                <div>
                    <label class="block text-sm font-semibold text-slate-700 mb-1">Select Route</label>
                    <select name="route_id" class="w-full bg-white text-slate-900 border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm">
                        {% for r in routes %}
                        <option value="{{ r.route_id }}" {% if r.available_seats == 0 %}disabled{% endif %}>
                            {{ r.route_id }} ({{ r.departure_city }} ➔ {{ r.destination_city }}) - Rs.{{ r.ticket_price }} [{{ r.available_seats }} seats]
                        </option>
                        {% endfor %}
                    </select>
                </div>

                <div>
                    <label class="block text-sm font-semibold text-slate-700 mb-1">Seats Quantity</label>
                    <input type="number" name="seats" min="1" max="10" value="1" required 
                           class="w-full bg-white text-slate-900 border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm">
                </div>

                <button type="submit" class="w-full bg-blue-700 hover:bg-blue-800 text-white font-bold py-2.5 px-4 rounded-xl transition duration-150 shadow-md">
                    Confirm Reservation
                </button>
            </form>
        </section>

        <!-- Right Column: Routes & Bookings -->
        <section class="md:col-span-2 space-y-8">
            <!-- Available Routes -->
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h2 class="text-xl font-bold mb-4 text-blue-900 border-b pb-2">📍 Available Routes</h2>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-sm">
                        <thead>
                            <tr class="border-b bg-slate-50 text-slate-600 font-semibold">
                                <th class="p-3">Route</th>
                                <th class="p-3">Journey</th>
                                <th class="p-3">Time</th>
                                <th class="p-3">Fare</th>
                                <th class="p-3">Availability</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100">
                            {% for r in routes %}
                            <tr class="hover:bg-slate-50 transition">
                                <td class="p-3 font-mono font-bold text-blue-700">{{ r.route_id }}</td>
                                <td class="p-3 font-medium">{{ r.departure_city }} ➔ {{ r.destination_city }}</td>
                                <td class="p-3 text-slate-600">{{ r.departure_time }}</td>
                                <td class="p-3 font-semibold text-slate-800">Rs. {{ r.ticket_price }}</td>
                                <td class="p-3">
                                    {% if r.available_seats == 0 %}
                                    <span class="bg-red-100 text-red-700 text-xs font-bold px-2.5 py-1 rounded-full">Fully Booked</span>
                                    {% else %}
                                    <span class="bg-emerald-100 text-emerald-800 text-xs font-bold px-2.5 py-1 rounded-full">
                                        {{ r.available_seats }} / {{ r.total_seats }}
                                    </span>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Booking History -->
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h2 class="text-xl font-bold mb-4 text-blue-900 border-b pb-2">📋 Booking History</h2>
                {% if not bookings %}
                <p class="text-sm text-slate-500 py-3">No bookings placed yet. Select a route and book a seat!</p>
                {% else %}
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-sm">
                        <thead>
                            <tr class="border-b bg-slate-50 text-slate-600 font-semibold">
                                <th class="p-3">ID</th>
                                <th class="p-3">Passenger</th>
                                <th class="p-3">Route</th>
                                <th class="p-3">Seats</th>
                                <th class="p-3">Fare</th>
                                <th class="p-3">Status</th>
                                <th class="p-3">Action</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100">
                            {% for b in bookings %}
                            <tr class="hover:bg-slate-50">
                                <td class="p-3 font-mono font-bold text-blue-800">{{ b.booking_id }}</td>
                                <td class="p-3 font-medium">{{ b.passenger_name }}</td>
                                <td class="p-3 text-slate-600">{{ b.route_id }}</td>
                                <td class="p-3">{{ b.seats }}</td>
                                <td class="p-3 font-semibold">Rs. {{ b.total_fare }}</td>
                                <td class="p-3">
                                    <span class="px-2.5 py-0.5 rounded-full text-xs font-bold {% if b.status == 'Confirmed' %}bg-green-100 text-green-800{% else %}bg-red-100 text-red-800{% endif %}">
                                        {{ b.status }}
                                    </span>
                                </td>
                                <td class="p-3">
                                    {% if b.status == 'Confirmed' %}
                                    <form method="POST" action="">
                                        <input type="hidden" name="action_type" value="cancel">
                                        <input type="hidden" name="booking_id" value="{{ b.booking_id }}">
                                        <button type="submit" class="text-xs bg-red-50 text-red-600 hover:bg-red-100 px-2.5 py-1 rounded font-semibold transition">
                                            Cancel
                                        </button>
                                    </form>
                                    {% else %}
                                    <span class="text-xs text-slate-400 italic">Cancelled</span>
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


@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def index(path):
    global booking_counter
    alert_message = None
    alert_color = ""

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
                    total_fare = route["ticket_price"] * seats
                    route["available_seats"] -= seats
                    bookings.insert(
                        0,
                        {
                            "booking_id": booking_id,
                            "passenger_name": name,
                            "passenger_age": age,
                            "route_id": route_id,
                            "seats": seats,
                            "total_fare": total_fare,
                            "status": "Confirmed",
                        },
                    )
                    alert_message = (
                        f"✓ Booking {booking_id} Confirmed! Total: Rs. {total_fare}"
                    )
                    alert_color = "bg-green-100 text-green-800 border border-green-200"
                else:
                    alert_message = "✕ Unable to book: check seat availability."
                    alert_color = "bg-red-100 text-red-800 border border-red-200"

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
                alert_message = f"✓ Booking {b_id} cancelled. Seats restored."
                alert_color = "bg-amber-100 text-amber-800 border border-amber-200"

    return render_template_string(
        HTML_TEMPLATE,
        routes=routes,
        bookings=bookings,
        alert_message=alert_message,
        alert_color=alert_color,
    )


if __name__ == "__main__":
    app.run(debug=True)
