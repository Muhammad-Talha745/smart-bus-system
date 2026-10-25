from flask import Flask, render_template_string, request

app = Flask(__name__)

# ==========================================
# DATA STRUCTURES & STARTER FLEET
# ==========================================
SUPPORTED_CITIES = ("Karachi", "Hyderabad", "Sukkur", "Mirpur Khas", "Lahore")

routes = [
    {
        "route_id": "LX-101",
        "departure_city": "Karachi",
        "destination_city": "Hyderabad",
        "departure_time": "08:00 AM",
        "ticket_price": 1200,
        "total_seats": 40,
        "available_seats": 40,
        "class": "Royal Executive",
    },
    {
        "route_id": "LX-102",
        "departure_city": "Karachi",
        "destination_city": "Sukkur",
        "departure_time": "09:30 AM",
        "ticket_price": 2000,
        "total_seats": 36,
        "available_seats": 36,
        "class": "First Class Sleeper",
    },
    {
        "route_id": "LX-103",
        "departure_city": "Hyderabad",
        "destination_city": "Mirpur Khas",
        "departure_time": "11:00 AM",
        "ticket_price": 800,
        "total_seats": 32,
        "available_seats": 32,
        "class": "Executive Business",
    },
    {
        "route_id": "LX-104",
        "departure_city": "Karachi",
        "destination_city": "Lahore",
        "departure_time": "07:00 PM",
        "ticket_price": 5000,
        "total_seats": 45,
        "available_seats": 45,
        "class": "Imperial Suite",
    },
    {
        "route_id": "LX-105",
        "departure_city": "Sukkur",
        "destination_city": "Hyderabad",
        "departure_time": "02:00 PM",
        "ticket_price": 1500,
        "total_seats": 30,
        "available_seats": 30,
        "class": "Royal Executive",
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
    <title>SMART BUS | Luxury Executive Fleet</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Cinzel:wght@600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
        .font-luxury { font-family: 'Cinzel', serif; }
        .glass-panel {
            background: rgba(17, 24, 39, 0.7);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .gold-gradient-text {
            background: linear-gradient(135deg, #FDE68A 0%, #D97706 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .gold-border-glow:focus-within {
            border-color: #F59E0B;
            box-shadow: 0 0 15px rgba(245, 158, 11, 0.25);
        }
    </style>
</head>
<body class="bg-[#0A0D14] text-slate-100 min-h-screen selection:bg-amber-500 selection:text-black">

    <!-- Top Luxury Navigation Bar -->
    <header class="border-b border-white/10 glass-panel sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-600 to-amber-300 flex items-center justify-center text-black font-bold text-lg shadow-lg shadow-amber-500/20">
                    ⚜
                </div>
                <div>
                    <h1 class="text-xl font-bold tracking-wider font-luxury gold-gradient-text uppercase">Smart Bus Executive</h1>
                    <p class="text-[10px] tracking-widest text-slate-400 uppercase">First-Class Intercity Mobility</p>
                </div>
            </div>
            
            <div class="flex items-center space-x-4">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-300 border border-amber-500/20">
                    <span class="w-1.5 h-1.5 rounded-full bg-amber-400 mr-2 animate-pulse"></span> Terminal System Active
                </span>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <main class="max-w-7xl mx-auto px-6 py-10 space-y-10">

        <!-- Executive Metrics Row -->
        <section class="grid grid-cols-2 md:grid-cols-4 gap-5">
            <div class="glass-panel p-5 rounded-2xl border-l-4 border-amber-500 shadow-xl">
                <p class="text-xs uppercase tracking-wider text-slate-400 font-medium">Fleet Destinations</p>
                <p class="text-3xl font-extrabold text-white mt-1 font-luxury">05 <span class="text-xs font-normal text-amber-400">Routes</span></p>
            </div>
            <div class="glass-panel p-5 rounded-2xl border-l-4 border-emerald-500 shadow-xl">
                <p class="text-xs uppercase tracking-wider text-slate-400 font-medium">Confirmed Seats</p>
                <p class="text-3xl font-extrabold text-white mt-1 font-luxury">{{ total_reserved }} <span class="text-xs font-normal text-emerald-400">Reserved</span></p>
            </div>
            <div class="glass-panel p-5 rounded-2xl border-l-4 border-blue-500 shadow-xl">
                <p class="text-xs uppercase tracking-wider text-slate-400 font-medium">Executive Bookings</p>
                <p class="text-3xl font-extrabold text-white mt-1 font-luxury">{{ confirmed_count }} <span class="text-xs font-normal text-blue-400">Active</span></p>
            </div>
            <div class="glass-panel p-5 rounded-2xl border-l-4 border-purple-500 shadow-xl">
                <p class="text-xs uppercase tracking-wider text-slate-400 font-medium">Session Revenue</p>
                <p class="text-2xl font-extrabold text-amber-300 mt-1 font-luxury">Rs. {{ "{:,}".format(total_revenue) }}</p>
            </div>
        </section>

        <!-- Notification Banner -->
        {% if alert_message %}
        <div class="p-4 rounded-xl text-sm font-semibold flex items-center justify-between border {{ alert_color }} transition-all">
            <span>{{ alert_message }}</span>
        </div>
        {% endif %}

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            
            <!-- Reservation Concierge (Form) -->
            <section class="lg:col-span-4 glass-panel p-6 rounded-2xl shadow-2xl relative overflow-hidden">
                <div class="absolute -top-12 -right-12 w-32 h-32 bg-amber-500/10 rounded-full blur-2xl"></div>

                <div class="mb-6">
                    <span class="text-xs font-bold text-amber-400 uppercase tracking-widest">Concierge Desk</span>
                    <h2 class="text-xl font-bold font-luxury text-white">Reserve Your Journey</h2>
                    <p class="text-xs text-slate-400 mt-1">Select your preferred route & executive seating.</p>
                </div>

                <form method="POST" action="" class="space-y-4">
                    <input type="hidden" name="action_type" value="book">

                    <div class="gold-border-glow border border-slate-700 rounded-xl p-3 bg-slate-900/50 transition">
                        <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Passenger Name</label>
                        <input type="text" name="name" placeholder="Sir / Madam Full Name" required 
                               class="w-full bg-transparent text-white placeholder-slate-600 text-sm focus:outline-none font-medium">
                    </div>

                    <div class="grid grid-cols-2 gap-3">
                        <div class="gold-border-glow border border-slate-700 rounded-xl p-3 bg-slate-900/50 transition">
                            <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Age</label>
                            <input type="number" name="age" min="1" max="110" placeholder="e.g. 30" required 
                                   class="w-full bg-transparent text-white placeholder-slate-600 text-sm focus:outline-none font-medium">
                        </div>
                        <div class="gold-border-glow border border-slate-700 rounded-xl p-3 bg-slate-900/50 transition">
                            <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Seats Quantity</label>
                            <input type="number" name="seats" min="1" max="10" value="1" required 
                                   class="w-full bg-transparent text-white text-sm focus:outline-none font-medium">
                        </div>
                    </div>

                    <div class="gold-border-glow border border-slate-700 rounded-xl p-3 bg-slate-900/50 transition">
                        <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Select Journey & Class</label>
                        <select name="route_id" class="w-full bg-slate-900 text-white text-sm focus:outline-none cursor-pointer">
                            {% for r in routes %}
                            <option value="{{ r.route_id }}" {% if r.available_seats == 0 %}disabled{% endif %}>
                                {{ r.route_id }} • {{ r.departure_city }} ➔ {{ r.destination_city }} (Rs.{{ r.ticket_price }})
                            </option>
                            {% endfor %}
                        </select>
                    </div>

                    <button type="submit" class="w-full py-3.5 px-6 rounded-xl font-bold text-sm tracking-wider uppercase text-black bg-gradient-to-r from-amber-400 via-amber-300 to-amber-500 hover:opacity-95 transition-all shadow-lg shadow-amber-500/25 active:scale-[0.99]">
                        Confirm Reservation ➔
                    </button>
                </form>
            </section>

            <!-- Fleet Schedule & Real-time Availability -->
            <section class="lg:col-span-8 space-y-8">
                
                <!-- Routes Table -->
                <div class="glass-panel p-6 rounded-2xl shadow-2xl">
                    <div class="flex justify-between items-center mb-6 border-b border-white/10 pb-4">
                        <div>
                            <span class="text-xs font-bold text-amber-400 uppercase tracking-widest">Live Schedule</span>
                            <h2 class="text-lg font-bold font-luxury text-white">Executive Luxury Fleet</h2>
                        </div>
                        <span class="text-xs text-slate-400 font-mono">5 Active Scheduled Charters</span>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-sm">
                            <thead>
                                <tr class="text-xs uppercase tracking-wider text-slate-400 border-b border-white/5">
                                    <th class="pb-3">Route</th>
                                    <th class="pb-3">Destination</th>
                                    <th class="pb-3">Departure</th>
                                    <th class="pb-3">Tier</th>
                                    <th class="pb-3">Fare</th>
                                    <th class="pb-3 text-right">Available Seats</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-white/5">
                                {% for r in routes %}
                                <tr class="hover:bg-white/[0.02] transition">
                                    <td class="py-4 font-mono font-bold text-amber-300">{{ r.route_id }}</td>
                                    <td class="py-4">
                                        <div class="font-semibold text-white">{{ r.departure_city }} <span class="text-amber-400">➔</span> {{ r.destination_city }}</div>
                                    </td>
                                    <td class="py-4 text-slate-300">{{ r.departure_time }}</td>
                                    <td class="py-4">
                                        <span class="px-2 py-0.5 rounded text-[11px] font-semibold bg-white/5 border border-white/10 text-slate-300">
                                            {{ r.class }}
                                        </span>
                                    </td>
                                    <td class="py-4 font-bold text-amber-300">Rs. {{ "{:,}".format(r.ticket_price) }}</td>
                                    <td class="py-4 text-right">
                                        {% if r.available_seats == 0 %}
                                        <span class="px-2.5 py-1 rounded-full text-xs font-bold bg-red-500/10 text-red-400 border border-red-500/20">Full</span>
                                        {% else %}
                                        <span class="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                                            {{ r.available_seats }} / {{ r.total_seats }} Left
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
                <div class="glass-panel p-6 rounded-2xl shadow-2xl">
                    <div class="flex justify-between items-center mb-6 border-b border-white/10 pb-4">
                        <div>
                            <span class="text-xs font-bold text-amber-400 uppercase tracking-widest">Passenger Manifest</span>
                            <h2 class="text-lg font-bold font-luxury text-white">Confirmed Boarding Passes</h2>
                        </div>
                    </div>

                    {% if not bookings %}
                    <div class="text-center py-10 border border-dashed border-white/10 rounded-xl">
                        <p class="text-slate-400 text-sm">No reservations confirmed in this session yet.</p>
                        <p class="text-xs text-slate-600 mt-1">Bookings confirmed through the concierge will appear here immediately.</p>
                    </div>
                    {% else %}
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-sm">
                            <thead>
                                <tr class="text-xs uppercase tracking-wider text-slate-400 border-b border-white/5">
                                    <th class="pb-3">Pass ID</th>
                                    <th class="pb-3">Passenger</th>
                                    <th class="pb-3">Route</th>
                                    <th class="pb-3">Seats</th>
                                    <th class="pb-3">Total Fare</th>
                                    <th class="pb-3">Status</th>
                                    <th class="pb-3 text-right">Action</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-white/5">
                                {% for b in bookings %}
                                <tr class="hover:bg-white/[0.02]">
                                    <td class="py-3 font-mono font-bold text-amber-400">{{ b.booking_id }}</td>
                                    <td class="py-3 font-semibold text-white">{{ b.passenger_name }}</td>
                                    <td class="py-3 font-mono text-slate-300">{{ b.route_id }}</td>
                                    <td class="py-3 text-slate-300">{{ b.seats }}</td>
                                    <td class="py-3 font-bold text-slate-200">Rs. {{ "{:,}".format(b.total_fare) }}</td>
                                    <td class="py-3">
                                        <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold {% if b.status == 'Confirmed' %}bg-emerald-500/10 text-emerald-300 border border-emerald-500/20{% else %}bg-red-500/10 text-red-400 border border-red-500/20{% endif %}">
                                            {{ b.status }}
                                        </span>
                                    </td>
                                    <td class="py-3 text-right">
                                        {% if b.status == 'Confirmed' %}
                                        <form method="POST" action="">
                                            <input type="hidden" name="action_type" value="cancel">
                                            <input type="hidden" name="booking_id" value="{{ b.booking_id }}">
                                            <button type="submit" class="text-xs text-red-400 hover:text-red-300 font-medium px-2 py-1 rounded bg-red-500/5 hover:bg-red-500/10 border border-red-500/20 transition">
                                                Cancel Pass
                                            </button>
                                        </form>
                                        {% else %}
                                        <span class="text-xs text-slate-500 italic">Cancelled</span>
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
        </div>
    </main>

    <!-- Footer -->
    <footer class="border-t border-white/5 py-8 text-center text-xs text-slate-500">
        <p class="font-luxury tracking-widest gold-gradient-text uppercase text-sm">Smart Bus Transportation Company</p>
        <p class="mt-1">Built with Python 3, Serverless Architecture & Tailored Executive Design</p>
    </footer>

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

        # Booking Action
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
                    booking_id = f"LX-{booking_counter}"
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
                    alert_message = f"✓ Executive Boarding Pass {booking_id} Confirmed for {name}. Total: Rs. {total_fare:,}"
                    alert_color = (
                        "bg-emerald-950/80 text-emerald-300 border-emerald-500/40"
                    )
                else:
                    alert_message = "✕ Reservation Request Declined: Please verify seat availability and requirements."
                    alert_color = "bg-red-950/80 text-red-300 border-red-500/40"

        # Cancellation Action
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
                alert_message = f"✓ Boarding Pass {b_id} successfully cancelled. {booking['seats']} seat(s) restored to inventory."
                alert_color = "bg-amber-950/80 text-amber-300 border-amber-500/40"

    # Compute live luxury metrics
    total_reserved = sum(b["seats"] for b in bookings if b["status"] == "Confirmed")
    confirmed_count = sum(1 for b in bookings if b["status"] == "Confirmed")
    total_revenue = sum(b["total_fare"] for b in bookings if b["status"] == "Confirmed")

    return render_template_string(
        HTML_TEMPLATE,
        routes=routes,
        bookings=bookings,
        total_reserved=total_reserved,
        confirmed_count=confirmed_count,
        total_revenue=total_revenue,
        alert_message=alert_message,
        alert_color=alert_color,
    )


if __name__ == "__main__":
    app.run(debug=True)
