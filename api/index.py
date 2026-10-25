import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, render_template_string, request, session, redirect

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "smartbus_ultra_luxury_secret_key_987654")

# Vercel serverless functions have write access to /tmp
DB_FILE = "/tmp/smartbus.db" if os.environ.get("VERCEL") else "smartbus.db"

# ==========================================
# 1. DATABASE SETUP & INITIALIZATION
# ==========================================
from werkzeug.security import generate_password_hash, check_password_hash


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'passenger',
        created_at TEXT NOT NULL
    )
    """)

    # Routes Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS routes (
        route_id TEXT PRIMARY KEY,
        departure_city TEXT NOT NULL,
        destination_city TEXT NOT NULL,
        departure_time TEXT NOT NULL,
        arrival_time TEXT NOT NULL,
        ticket_price INTEGER NOT NULL,
        total_seats INTEGER NOT NULL,
        available_seats INTEGER NOT NULL,
        bus_model TEXT NOT NULL,
        bus_class TEXT NOT NULL,
        occupied_seats TEXT NOT NULL
    )
    """)

    # Bookings Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        booking_id TEXT PRIMARY KEY,
        user_id INTEGER,
        passenger_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        cnic TEXT NOT NULL,
        passenger_age INTEGER NOT NULL,
        route_id TEXT NOT NULL,
        seats TEXT NOT NULL,
        subtotal INTEGER NOT NULL,
        discount INTEGER NOT NULL,
        total_fare INTEGER NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    # Seed Default Users if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
            (
                "Executive Controller",
                "admin@smartbus.com",
                generate_password_hash("admin123"),
                "admin",
                now,
            ),
        )
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
            (
                "Tariq Mansoor",
                "passenger@smartbus.com",
                generate_password_hash("pass123"),
                "passenger",
                now,
            ),
        )

    # Seed Default Routes if empty
    cursor.execute("SELECT COUNT(*) FROM routes")
    if cursor.fetchone()[0] == 0:
        default_routes = [
            (
                "LX-101",
                "Karachi",
                "Hyderabad",
                "08:00 AM",
                "10:30 AM",
                1800,
                28,
                26,
                "Mercedes-Benz Travego VIP",
                "Royal First Class",
                json.dumps(["1A", "1B"]),
            ),
            (
                "LX-102",
                "Karachi",
                "Sukkur",
                "09:30 AM",
                "03:30 PM",
                3200,
                28,
                27,
                "Volvo 9900 Executive Sleeper",
                "Imperial Suite",
                json.dumps(["3C"]),
            ),
            (
                "LX-103",
                "Hyderabad",
                "Mirpur Khas",
                "11:00 AM",
                "12:45 PM",
                1200,
                28,
                28,
                "Scania Touring HD",
                "Executive Business",
                json.dumps([]),
            ),
            (
                "LX-104",
                "Karachi",
                "Lahore",
                "07:00 PM",
                "09:00 AM",
                6500,
                28,
                24,
                "Setra S 531 DT Double-Decker",
                "Presidential Stateroom",
                json.dumps(["1A", "1B", "2A", "2B"]),
            ),
            (
                "LX-105",
                "Sukkur",
                "Hyderabad",
                "02:00 PM",
                "06:30 PM",
                2200,
                28,
                28,
                "Mercedes-Benz Travego VIP",
                "Royal First Class",
                json.dumps([]),
            ),
        ]
        cursor.executemany(
            "INSERT INTO routes VALUES (?,?,?,?,?,?,?,?,?,?,?)", default_routes
        )

        # Seed 1 initial booking
        cursor.execute(
            """
        INSERT INTO bookings VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
            (
                "LX-1001",
                2,
                "Tariq Mansoor",
                "+92 300 1234567",
                "42101-9876543-1",
                34,
                "LX-101",
                json.dumps(["1A", "1B"]),
                3600,
                0,
                3600,
                "Confirmed",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )

    conn.commit()
    conn.close()


init_db()

# ==========================================
# 2. HTML / UI TEMPLATE (HAUTE MONOCHROME)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SMART BUS | Haute Luxury Transit</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Cinzel:wght@600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #030303; }
        .font-luxury { font-family: 'Cinzel', serif; }
        .border-luxury { border-color: rgba(255, 255, 255, 0.12); }
        .bg-luxury-card { background-color: #0B0B0B; }
        .bg-luxury-input { background-color: #141414; }

        .nav-btn.active {
            color: #FFFFFF !important;
            border-bottom: 2px solid #FFFFFF !important;
        }
        .seat { transition: all 0.15s ease; }
        .seat.available:hover {
            border-color: #FFFFFF !important;
            background-color: #222222 !important;
            transform: translateY(-2px);
        }
        .seat.selected {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border-color: #FFFFFF !important;
            font-weight: 800 !important;
            box-shadow: 0 0 14px rgba(255, 255, 255, 0.4);
        }
        .seat.occupied {
            background-color: #171717 !important;
            border-color: #262626 !important;
            color: #4b4b4b !important;
            cursor: not-allowed;
            text-decoration: line-through;
        }
    </style>
</head>
<body class="text-white min-h-screen selection:bg-white selection:text-black">

    <!-- Top Luxury Navigation -->
    <header class="border-b border-luxury sticky top-0 bg-[#030303]/95 backdrop-blur-xl z-40">
        <div class="max-w-7xl mx-auto px-6 py-4 flex flex-col md:flex-row justify-between items-center gap-4">
            
            <!-- Logo -->
            <div class="flex items-center space-x-3 cursor-pointer" onclick="switchTab('bookingTab')">
                <div class="w-9 h-9 border border-white flex items-center justify-center font-luxury font-bold text-base tracking-tighter">
                    SB
                </div>
                <div>
                    <h1 class="text-lg font-bold tracking-widest font-luxury uppercase">Smart Bus</h1>
                    <p class="text-[9px] tracking-[0.3em] text-neutral-400 uppercase">Executive Travel Fleet</p>
                </div>
            </div>

            <!-- Page Navigation -->
            <nav class="flex items-center space-x-6 text-xs uppercase tracking-wider font-medium">
                <button onclick="switchTab('bookingTab')" id="nav-bookingTab" class="nav-btn py-2 text-neutral-400 hover:text-white transition active">
                    Book Journey
                </button>
                <button onclick="switchTab('fleetTab')" id="nav-fleetTab" class="nav-btn py-2 text-neutral-400 hover:text-white transition">
                    Fleet & Routes
                </button>
                <button onclick="switchTab('myBookingsTab')" id="nav-myBookingsTab" class="nav-btn py-2 text-neutral-400 hover:text-white transition">
                    My Bookings
                </button>

                {% if current_user and current_user.role == 'admin' %}
                <button onclick="switchTab('adminTab')" id="nav-adminTab" class="nav-btn py-1.5 px-3 border border-white rounded hover:bg-white hover:text-black transition">
                    👑 Admin Portal
                </button>
                {% endif %}
            </nav>

            <!-- Authentication User Badge -->
            <div class="flex items-center space-x-3 text-xs font-mono">
                {% if current_user %}
                <div class="flex items-center space-x-3 border border-white/20 px-3 py-1.5 rounded">
                    <span class="text-neutral-400 uppercase text-[10px]">{{ current_user.role }}:</span>
                    <span class="font-bold text-white">{{ current_user.name }}</span>
                    <form method="POST" action="" class="inline">
                        <input type="hidden" name="action_type" value="logout">
                        <button type="submit" class="text-neutral-400 hover:text-red-400 ml-2 text-[10px] uppercase underline">Sign Out</button>
                    </form>
                </div>
                {% else %}
                <button onclick="openAuthModal('login')" class="px-3 py-1.5 text-neutral-300 hover:text-white uppercase">
                    Sign In
                </button>
                <button onclick="openAuthModal('register')" class="px-3 py-1.5 bg-white text-black font-bold uppercase hover:bg-neutral-200 transition">
                    Register
                </button>
                {% endif %}
            </div>

        </div>
    </header>

    <!-- Global Flash Notification -->
    {% if alert_message %}
    <div class="max-w-7xl mx-auto px-6 mt-6">
        <div class="p-4 rounded border text-xs uppercase tracking-widest font-mono flex items-center justify-between {{ alert_color }}">
            <span>{{ alert_message }}</span>
        </div>
    </div>
    {% endif %}

    <!-- ============================================================== -->
    <!-- TAB 1: PASSENGER BOOKING CONSOLE                               -->
    <!-- ============================================================== -->
    <div id="bookingTab" class="page-content max-w-7xl mx-auto px-6 py-10 space-y-10">
        
        <div class="border-b border-luxury pb-6 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
            <div>
                <span class="text-[10px] font-mono uppercase tracking-[0.3em] text-neutral-400">Database-Integrated Fleet System</span>
                <h2 class="text-3xl md:text-4xl font-luxury font-bold mt-1 tracking-tight">Reserve First-Class Seating</h2>
            </div>
            <div class="text-right font-mono text-xs text-neutral-400">
                <span>Active Network:</span>
                <p class="text-lg font-bold text-white">{{ routes|length }} Scheduled Coaches</p>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            
            <!-- Reservation Form with Live Seat Map -->
            <section class="lg:col-span-5 bg-luxury-card border border-luxury p-7 space-y-6">
                <div class="border-b border-luxury pb-3">
                    <span class="text-[10px] font-mono uppercase tracking-widest text-neutral-400">Traveler Details</span>
                    <h3 class="text-xl font-luxury font-bold uppercase mt-1">Passenger Manifest</h3>
                </div>

                <form method="POST" action="" id="bookingForm" class="space-y-4">
                    <input type="hidden" name="action_type" value="book">
                    <input type="hidden" name="selected_seats" id="selectedSeatsInput" value="">

                    <div>
                        <label class="block text-[10px] font-mono uppercase tracking-wider text-neutral-400 mb-1">Full Passenger Name</label>
                        <input type="text" name="name" value="{{ current_user.name if current_user else '' }}" placeholder="Passenger Full Name" required
                               class="w-full bg-luxury-input text-white border border-luxury px-3.5 py-2.5 text-sm focus:outline-none focus:border-white">
                    </div>

                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block text-[10px] font-mono uppercase tracking-wider text-neutral-400 mb-1">Mobile Contact</label>
                            <input type="tel" name="phone" placeholder="0300-1234567" required
                                   class="w-full bg-luxury-input text-white border border-luxury px-3.5 py-2.5 text-sm focus:outline-none focus:border-white">
                        </div>
                        <div>
                            <label class="block text-[10px] font-mono uppercase tracking-wider text-neutral-400 mb-1">CNIC / ID</label>
                            <input type="text" name="cnic" placeholder="42101-XXXXXXX-X" required
                                   class="w-full bg-luxury-input text-white border border-luxury px-3.5 py-2.5 text-sm focus:outline-none focus:border-white">
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block text-[10px] font-mono uppercase tracking-wider text-neutral-400 mb-1">Age</label>
                            <input type="number" name="age" min="1" max="110" placeholder="e.g. 28" required
                                   class="w-full bg-luxury-input text-white border border-luxury px-3.5 py-2.5 text-sm focus:outline-none focus:border-white">
                        </div>
                        <div>
                            <label class="block text-[10px] font-mono uppercase tracking-wider text-neutral-400 mb-1">Luggage Class</label>
                            <select class="w-full bg-luxury-input text-white border border-luxury px-3.5 py-2.5 text-sm focus:outline-none">
                                <option>30kg Included</option>
                                <option>45kg VIP Suite</option>
                            </select>
                        </div>
                    </div>

                    <div>
                        <label class="block text-[10px] font-mono uppercase tracking-wider text-neutral-400 mb-1">Select Coach Service</label>
                        <select name="route_id" id="routeSelect" onchange="renderBusSeats()" 
                                class="w-full bg-luxury-input text-white border border-luxury px-3.5 py-2.5 text-sm focus:outline-none cursor-pointer">
                            {% for r in routes %}
                            <option value="{{ r.route_id }}" data-price="{{ r.ticket_price }}" data-occupied='{{ r.occupied_seats }}'>
                                {{ r.route_id }} • {{ r.departure_city }} ➔ {{ r.destination_city }} (Rs. {{ "{:,}".format(r.ticket_price) }})
                            </option>
                            {% endfor %}
                        </select>
                    </div>

                    <!-- Visual Bus Cabin -->
                    <div class="border border-luxury p-4 bg-black/80 space-y-3">
                        <div class="flex justify-between items-center text-[10px] font-mono uppercase text-neutral-400 border-b border-luxury pb-2">
                            <span>Pilot Cockpit ❖ Front</span>
                            <div class="flex items-center space-x-3">
                                <span class="flex items-center"><span class="w-2 h-2 border border-neutral-600 bg-neutral-900 mr-1"></span> Free</span>
                                <span class="flex items-center"><span class="w-2 h-2 bg-white mr-1"></span> Chosen</span>
                                <span class="flex items-center"><span class="w-2 h-2 bg-neutral-800 mr-1"></span> Sold</span>
                            </div>
                        </div>
                        <div id="seatGrid" class="space-y-2 py-2"></div>
                    </div>

                    <!-- Live Breakdown & Discount -->
                    <div class="p-4 bg-luxury-input border border-luxury text-xs font-mono space-y-1.5">
                        <div class="flex justify-between text-neutral-400">
                            <span>Selected Seats:</span>
                            <span id="selectedSeatsLabel" class="text-white font-bold">None</span>
                        </div>
                        <div class="flex justify-between text-neutral-400">
                            <span>Seat Count:</span>
                            <span id="seatCountLabel" class="text-white">0</span>
                        </div>
                        <div class="flex justify-between text-emerald-400" id="discountRow" style="display: none;">
                            <span>Corporate VIP Discount (10% off):</span>
                            <span id="discountLabel">- Rs. 0</span>
                        </div>
                        <div class="flex justify-between text-sm pt-2 border-t border-luxury font-bold text-white">
                            <span>Total Payable:</span>
                            <span id="totalFareLabel" class="text-base font-luxury">Rs. 0</span>
                        </div>
                    </div>

                    <button type="submit" id="bookSubmitBtn" disabled
                            class="w-full py-3.5 bg-white text-black hover:bg-neutral-200 transition font-bold text-xs uppercase tracking-widest disabled:opacity-20 disabled:cursor-not-allowed">
                        Confirm & Store Reservation ➔
                    </button>
                </form>
            </section>

            <!-- Real-Time Departures Schedule -->
            <section class="lg:col-span-7 space-y-6">
                <div class="bg-luxury-card border border-luxury p-6">
                    <div class="flex justify-between items-center border-b border-luxury pb-4 mb-4">
                        <div>
                            <span class="text-[10px] font-mono uppercase tracking-widest text-neutral-400">Live Database Feed</span>
                            <h3 class="text-lg font-luxury font-bold uppercase">Scheduled Fleet Journeys</h3>
                        </div>
                        <span class="text-xs font-mono text-neutral-400">Real-Time Inventory</span>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead>
                                <tr class="text-[10px] font-mono uppercase text-neutral-400 border-b border-luxury pb-2">
                                    <th class="pb-3">Route</th>
                                    <th class="pb-3">Journey</th>
                                    <th class="pb-3">Departure / Arrival</th>
                                    <th class="pb-3">Fare</th>
                                    <th class="pb-3 text-right">Available</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-luxury">
                                {% for r in routes %}
                                <tr class="hover:bg-white/[0.02]">
                                    <td class="py-3.5 font-mono font-bold text-white">{{ r.route_id }}</td>
                                    <td class="py-3.5">
                                        <div class="font-bold text-white">{{ r.departure_city }} ➔ {{ r.destination_city }}</div>
                                        <div class="text-[10px] text-neutral-400 font-mono">{{ r.bus_model }}</div>
                                    </td>
                                    <td class="py-3.5 font-mono text-neutral-300">{{ r.departure_time }} → {{ r.arrival_time }}</td>
                                    <td class="py-3.5 font-bold font-mono">Rs. {{ "{:,}".format(r.ticket_price) }}</td>
                                    <td class="py-3.5 text-right font-mono font-bold">
                                        {% if r.available_seats == 0 %}
                                        <span class="text-neutral-500">SOLD OUT</span>
                                        {% else %}
                                        <span class="text-white">{{ r.available_seats }} / {{ r.total_seats }}</span>
                                        {% endif %}
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Account / Booking Quick Notice -->
                <div class="bg-luxury-card border border-luxury p-6 flex justify-between items-center">
                    <div>
                        <h4 class="font-luxury font-bold text-sm uppercase">Need Your Official E-Ticket?</h4>
                        <p class="text-xs text-neutral-400 mt-1">Track and print your electronic boarding pass in the My Bookings section.</p>
                    </div>
                    <button onclick="switchTab('myBookingsTab')" class="px-4 py-2 border border-white text-xs uppercase font-mono hover:bg-white hover:text-black transition">
                        View Passes ➔
                    </button>
                </div>
            </section>
        </div>
    </div>

    <!-- ============================================================== -->
    <!-- TAB 2: FLEET & ROUTES SHOWCASE                                 -->
    <!-- ============================================================== -->
    <div id="fleetTab" class="page-content max-w-7xl mx-auto px-6 py-10 space-y-10 hidden">
        <div class="border-b border-luxury pb-4">
            <span class="text-[10px] font-mono uppercase tracking-widest text-neutral-400">Intercity Portfolio</span>
            <h2 class="text-3xl font-luxury font-bold uppercase mt-1">The Master Fleet</h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            {% for r in routes %}
            <div class="bg-luxury-card border border-luxury p-6 flex flex-col justify-between space-y-4">
                <div>
                    <div class="flex justify-between items-center text-xs font-mono text-neutral-400 mb-2">
                        <span>{{ r.route_id }}</span>
                        <span class="border border-white/20 px-2 py-0.5 uppercase text-[9px]">{{ r.bus_class }}</span>
                    </div>
                    <h3 class="text-xl font-luxury font-bold">{{ r.departure_city }} ➔ {{ r.destination_city }}</h3>
                    <p class="text-xs text-neutral-400 font-mono mt-1">{{ r.bus_model }}</p>
                </div>

                <div class="border-t border-b border-luxury py-3 text-xs font-mono space-y-1 text-neutral-300">
                    <div class="flex justify-between">
                        <span>Departure Time:</span>
                        <span class="text-white font-bold">{{ r.departure_time }}</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Standard Fare:</span>
                        <span class="text-white font-bold">Rs. {{ "{:,}".format(r.ticket_price) }}</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Total Capacity:</span>
                        <span class="text-white font-bold">{{ r.total_seats }} VIP Seats</span>
                    </div>
                </div>

                <button onclick="selectRouteAndGo('{{ r.route_id }}')" class="w-full py-2.5 border border-white text-white hover:bg-white hover:text-black font-bold text-xs uppercase tracking-widest transition">
                    Book On This Service ➔
                </button>
            </div>
            {% endfor %}
        </div>
    </div>

    <!-- ============================================================== -->
    <!-- TAB 3: USER SPECIFIC BOOKINGS                                  -->
    <!-- ============================================================== -->
    <div id="myBookingsTab" class="page-content max-w-7xl mx-auto px-6 py-10 space-y-10 hidden">
        <div class="border-b border-luxury pb-4 flex justify-between items-end">
            <div>
                <span class="text-[10px] font-mono uppercase tracking-widest text-neutral-400">Database Travel History</span>
                <h2 class="text-3xl font-luxury font-bold uppercase mt-1">My Electronic Boarding Passes</h2>
            </div>
            {% if not current_user %}
            <p class="text-xs font-mono text-neutral-400">Tip: Sign in to bind bookings permanently to your account.</p>
            {% endif %}
        </div>

        <div class="bg-luxury-card border border-luxury p-6">
            {% if not bookings %}
            <p class="text-neutral-500 text-xs py-8 text-center font-mono uppercase">No records found. Reserve a seat to generate your boarding pass.</p>
            {% else %}
            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs font-mono">
                    <thead>
                        <tr class="text-[10px] uppercase tracking-wider text-neutral-400 border-b border-luxury">
                            <th class="pb-3">Pass ID</th>
                            <th class="pb-3">Passenger</th>
                            <th class="pb-3">Contact</th>
                            <th class="pb-3">Route</th>
                            <th class="pb-3">Seats</th>
                            <th class="pb-3">Fare Paid</th>
                            <th class="pb-3">Status</th>
                            <th class="pb-3 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-luxury">
                        {% for b in bookings %}
                        <tr>
                            <td class="py-3.5 font-bold text-white">{{ b.booking_id }}</td>
                            <td class="py-3.5 font-sans font-medium text-white">{{ b.passenger_name }}</td>
                            <td class="py-3.5 text-neutral-400">{{ b.phone }}</td>
                            <td class="py-3.5 text-neutral-200">{{ b.route_id }}</td>
                            <td class="py-3.5">
                                {% for s in b.seats %}
                                <span class="border border-white/20 px-1 py-0.5 text-[9px] mr-1">{{ s }}</span>
                                {% endfor %}
                            </td>
                            <td class="py-3.5 font-bold">Rs. {{ "{:,}".format(b.total_fare) }}</td>
                            <td class="py-3.5">
                                <span class="px-2 py-0.5 text-[9px] uppercase font-bold {% if b.status == 'Confirmed' %}bg-white text-black{% else %}border border-red-500 text-red-400{% endif %}">
                                    {{ b.status }}
                                </span>
                            </td>
                            <td class="py-3.5 text-right space-x-2">
                                <button onclick='openTicketModal({{ b | tojson }})' 
                                        class="px-2.5 py-1 border border-white text-white hover:bg-white hover:text-black text-[10px] uppercase transition">
                                    Ticket 🖨
                                </button>

                                {% if b.status == 'Confirmed' %}
                                <form method="POST" action="" class="inline">
                                    <input type="hidden" name="action_type" value="cancel">
                                    <input type="hidden" name="booking_id" value="{{ b.booking_id }}">
                                    <button type="submit" class="px-2 py-0.5 border border-red-500 text-red-400 hover:bg-red-500 hover:text-white transition text-[10px] uppercase">
                                        Cancel
                                    </button>
                                </form>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% endif %}
        </div>
    </div>

    <!-- ============================================================== -->
    <!-- TAB 4: 👑 ADMIN COMMAND PORTAL                                 -->
    <!-- ============================================================== -->
    {% if current_user and current_user.role == 'admin' %}
    <div id="adminTab" class="page-content max-w-7xl mx-auto px-6 py-10 space-y-10 hidden">
        <div class="border-b border-luxury pb-4 flex justify-between items-end">
            <div>
                <span class="text-[10px] font-mono uppercase tracking-widest text-neutral-400">Authenticated Operational Database</span>
                <h2 class="text-3xl font-luxury font-bold uppercase mt-1">Admin Command Center</h2>
            </div>
            <span class="px-3 py-1 border border-white text-xs font-mono uppercase">Master Fleet Controller</span>
        </div>

        <!-- KPIs -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="bg-luxury-card border border-luxury p-5">
                <p class="text-[10px] font-mono uppercase text-neutral-400">Gross Ticket Sales</p>
                <p class="text-2xl font-bold font-mono text-white mt-1">Rs. {{ "{:,}".format(total_revenue) }}</p>
            </div>
            <div class="bg-luxury-card border border-luxury p-5">
                <p class="text-[10px] font-mono uppercase text-neutral-400">Total Seats Reserved</p>
                <p class="text-2xl font-bold font-mono text-white mt-1">{{ total_reserved }} Seats</p>
            </div>
            <div class="bg-luxury-card border border-luxury p-5">
                <p class="text-[10px] font-mono uppercase text-neutral-400">Confirmed Bookings</p>
                <p class="text-2xl font-bold font-mono text-white mt-1">{{ confirmed_count }} Active</p>
            </div>
            <div class="bg-luxury-card border border-luxury p-5">
                <p class="text-[10px] font-mono uppercase text-neutral-400">Cancelled Bookings</p>
                <p class="text-2xl font-bold font-mono text-neutral-400 mt-1">{{ cancelled_count }} Void</p>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            
            <!-- Deploy New Route into SQLite DB -->
            <div class="lg:col-span-5 bg-luxury-card border border-luxury p-6 space-y-4">
                <div class="border-b border-luxury pb-3">
                    <span class="text-[10px] font-mono uppercase tracking-widest text-neutral-400">Fleet Operations</span>
                    <h3 class="text-lg font-luxury font-bold uppercase mt-1">Add Route to Database</h3>
                </div>

                <form method="POST" action="" class="space-y-3 text-xs">
                    <input type="hidden" name="action_type" value="add_route">

                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block text-[10px] font-mono uppercase text-neutral-400 mb-1">Route ID</label>
                            <input type="text" name="new_route_id" placeholder="LX-106" required class="w-full bg-luxury-input border border-luxury px-3 py-2 text-white">
                        </div>
                        <div>
                            <label class="block text-[10px] font-mono uppercase text-neutral-400 mb-1">Price (Rs.)</label>
                            <input type="number" name="new_price" placeholder="2500" required class="w-full bg-luxury-input border border-luxury px-3 py-2 text-white">
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block text-[10px] font-mono uppercase text-neutral-400 mb-1">Departure City</label>
                            <input type="text" name="new_dep_city" placeholder="Karachi" required class="w-full bg-luxury-input border border-luxury px-3 py-2 text-white">
                        </div>
                        <div>
                            <label class="block text-[10px] font-mono uppercase text-neutral-400 mb-1">Destination City</label>
                            <input type="text" name="new_dest_city" placeholder="Peshawar" required class="w-full bg-luxury-input border border-luxury px-3 py-2 text-white">
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block text-[10px] font-mono uppercase text-neutral-400 mb-1">Departure Time</label>
                            <input type="text" name="new_dep_time" placeholder="05:00 PM" required class="w-full bg-luxury-input border border-luxury px-3 py-2 text-white">
                        </div>
                        <div>
                            <label class="block text-[10px] font-mono uppercase text-neutral-400 mb-1">Arrival Time</label>
                            <input type="text" name="new_arr_time" placeholder="08:00 AM" required class="w-full bg-luxury-input border border-luxury px-3 py-2 text-white">
                        </div>
                    </div>

                    <div>
                        <label class="block text-[10px] font-mono uppercase text-neutral-400 mb-1">Coach Model</label>
                        <input type="text" name="new_model" placeholder="Mercedes-Benz Travego VIP" required class="w-full bg-luxury-input border border-luxury px-3 py-2 text-white">
                    </div>

                    <button type="submit" class="w-full py-3 bg-white text-black font-bold uppercase tracking-wider text-xs hover:bg-neutral-200 transition mt-2">
                        + Save Route in Database
                    </button>
                </form>
            </div>

            <!-- Global Passenger Manifest -->
            <div class="lg:col-span-7 bg-luxury-card border border-luxury p-6 space-y-4">
                <div class="border-b border-luxury pb-3">
                    <span class="text-[10px] font-mono uppercase tracking-widest text-neutral-400">System Records</span>
                    <h3 class="text-lg font-luxury font-bold uppercase mt-1">Master Manifest & Void Desk</h3>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs font-mono">
                        <thead>
                            <tr class="text-[10px] uppercase text-neutral-400 border-b border-luxury">
                                <th class="pb-2">Pass ID</th>
                                <th class="pb-2">Passenger</th>
                                <th class="pb-2">Seats</th>
                                <th class="pb-2">Status</th>
                                <th class="pb-2 text-right">Void Action</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-luxury">
                            {% for b in all_bookings %}
                            <tr>
                                <td class="py-3 font-bold text-white">{{ b.booking_id }}</td>
                                <td class="py-3 font-sans text-neutral-200">{{ b.passenger_name }}</td>
                                <td class="py-3">{{ b.seats | join(', ') }}</td>
                                <td class="py-3">
                                    <span class="px-2 py-0.5 text-[9px] uppercase font-bold {% if b.status == 'Confirmed' %}bg-white text-black{% else %}text-red-400 border border-red-500/30{% endif %}">
                                        {{ b.status }}
                                    </span>
                                </td>
                                <td class="py-3 text-right">
                                    {% if b.status == 'Confirmed' %}
                                    <form method="POST" action="" class="inline">
                                        <input type="hidden" name="action_type" value="cancel">
                                        <input type="hidden" name="booking_id" value="{{ b.booking_id }}">
                                        <button type="submit" class="px-2 py-0.5 border border-red-500 text-red-400 hover:bg-red-500 hover:text-white transition text-[10px] uppercase">
                                            Cancel & Release
                                        </button>
                                    </form>
                                    {% else %}
                                    <span class="text-neutral-600 text-[10px]">Voided</span>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

        </div>
    </div>
    {% endif %}

    <!-- ============================================================== -->
    <!-- AUTHENTICATION MODAL (SIGN IN / REGISTER)                      -->
    <!-- ============================================================== -->
    <div id="authModal" class="fixed inset-0 bg-black/90 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
        <div class="bg-black border border-white/20 p-8 max-w-sm w-full shadow-2xl relative text-white space-y-5 font-mono">
            
            <div class="flex justify-between items-start border-b border-white/10 pb-3">
                <div>
                    <h3 id="authModalTitle" class="font-luxury font-bold text-lg uppercase tracking-wider">Sign In</h3>
                    <p class="text-[9px] text-neutral-400 uppercase tracking-widest">Executive Credentials</p>
                </div>
                <button onclick="closeAuthModal()" class="text-neutral-400 hover:text-white text-xl font-bold">&times;</button>
            </div>

            <!-- Login Form -->
            <form method="POST" action="" id="loginForm" class="space-y-4 text-xs">
                <input type="hidden" name="action_type" value="login">
                <div>
                    <label class="block text-[10px] uppercase text-neutral-400 mb-1">Email Address</label>
                    <input type="email" name="email" placeholder="admin@smartbus.com" required 
                           class="w-full bg-luxury-input border border-luxury px-3 py-2 text-white focus:outline-none focus:border-white">
                </div>
                <div>
                    <label class="block text-[10px] uppercase text-neutral-400 mb-1">Password</label>
                    <input type="password" name="password" placeholder="••••••••" required 
                           class="w-full bg-luxury-input border border-luxury px-3 py-2 text-white focus:outline-none focus:border-white">
                </div>
                <button type="submit" class="w-full py-2.5 bg-white text-black font-bold uppercase tracking-widest hover:bg-neutral-200 transition">
                    Authenticate Account ➔
                </button>
                <div class="text-[10px] text-neutral-500 text-center pt-2">
                    Default Admin: <b class="text-neutral-300">admin@smartbus.com</b> / <b class="text-neutral-300">admin123</b>
                </div>
            </form>

            <!-- Register Form -->
            <form method="POST" action="" id="registerForm" class="space-y-4 text-xs hidden">
                <input type="hidden" name="action_type" value="register">
                <div>
                    <label class="block text-[10px] uppercase text-neutral-400 mb-1">Your Full Name</label>
                    <input type="text" name="name" placeholder="John Doe" required 
                           class="w-full bg-luxury-input border border-luxury px-3 py-2 text-white focus:outline-none focus:border-white">
                </div>
                <div>
                    <label class="block text-[10px] uppercase text-neutral-400 mb-1">Email Address</label>
                    <input type="email" name="email" placeholder="name@domain.com" required 
                           class="w-full bg-luxury-input border border-luxury px-3 py-2 text-white focus:outline-none focus:border-white">
                </div>
                <div>
                    <label class="block text-[10px] uppercase text-neutral-400 mb-1">Password</label>
                    <input type="password" name="password" minlength="6" placeholder="At least 6 characters" required 
                           class="w-full bg-luxury-input border border-luxury px-3 py-2 text-white focus:outline-none focus:border-white">
                </div>
                <button type="submit" class="w-full py-2.5 bg-white text-black font-bold uppercase tracking-widest hover:bg-neutral-200 transition">
                    Create Passenger Account ➔
                </button>
            </form>

            <div class="border-t border-white/10 pt-3 text-center">
                <button id="toggleAuthBtn" onclick="toggleAuthMode()" class="text-[10px] uppercase underline text-neutral-400 hover:text-white">
                    Need an account? Click here to register
                </button>
            </div>
        </div>
    </div>

    <!-- Printable E-Ticket Modal -->
    <div id="ticketModal" class="fixed inset-0 bg-black/90 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
        <div class="bg-black border border-white/30 p-8 max-w-md w-full shadow-2xl relative text-white space-y-6 font-mono" id="printArea">
            <div class="flex justify-between items-start border-b border-white/20 pb-4">
                <div>
                    <h3 class="font-luxury font-bold text-xl tracking-wider">SMART BUS</h3>
                    <p class="text-[9px] text-neutral-400 uppercase tracking-[0.25em]">First-Class Electronic Boarding Pass</p>
                </div>
                <button onclick="closeTicketModal()" class="text-neutral-400 hover:text-white text-xl font-bold">&times;</button>
            </div>

            <div class="space-y-3 text-xs">
                <div class="flex justify-between">
                    <span class="text-neutral-400 uppercase">Boarding Pass #</span>
                    <span id="mTicketId" class="font-bold text-white"></span>
                </div>
                <div class="flex justify-between font-sans">
                    <span class="text-neutral-400 font-mono uppercase">Passenger:</span>
                    <span id="mPassenger" class="font-bold text-white"></span>
                </div>
                <div class="flex justify-between">
                    <span class="text-neutral-400 uppercase">Contact / CNIC:</span>
                    <span id="mPhone" class="text-neutral-200"></span>
                </div>
                <div class="flex justify-between border-t border-white/10 pt-2 font-sans font-bold">
                    <span class="text-neutral-400 font-mono uppercase">Service Route:</span>
                    <span id="mRoute" class="text-white"></span>
                </div>
                <div class="flex justify-between">
                    <span class="text-neutral-400 uppercase">Allocated Seats:</span>
                    <span id="mSeats" class="font-bold text-white tracking-widest"></span>
                </div>
                <div class="flex justify-between border-t border-white/10 pt-2 font-bold text-sm">
                    <span class="uppercase">Total Fare Paid:</span>
                    <span id="mFare" class="font-luxury"></span>
                </div>
            </div>

            <div class="pt-4 border-t border-dashed border-white/20 text-center">
                <div class="h-10 bg-[repeating-linear-gradient(90deg,#fff,#fff_2px,#000_2px,#000_6px)] opacity-80"></div>
                <p class="text-[8px] text-neutral-500 tracking-[0.3em] mt-2 uppercase">Verified Database Security Hash</p>
            </div>

            <div class="flex space-x-3 pt-2">
                <button onclick="window.print()" class="flex-1 bg-white text-black font-bold py-2.5 text-xs uppercase tracking-widest hover:bg-neutral-200 transition">
                    Print / Save PDF 🖨
                </button>
                <button onclick="closeTicketModal()" class="px-5 py-2.5 border border-white/20 text-white text-xs uppercase hover:bg-white/10">
                    Close
                </button>
            </div>
        </div>
    </div>

    <!-- Frontend Interactive Script -->
    <script>
        const seatRows = 7;
        let selectedSeats = [];

        function switchTab(tabId) {
            document.querySelectorAll('.page-content').forEach(p => p.classList.add('hidden'));
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

            const target = document.getElementById(tabId);
            if (target) target.classList.remove('hidden');
            const nav = document.getElementById('nav-' + tabId);
            if (nav) nav.classList.add('active');
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        function selectRouteAndGo(routeId) {
            switchTab('bookingTab');
            const select = document.getElementById('routeSelect');
            select.value = routeId;
            renderBusSeats();
        }

        function renderBusSeats() {
            const select = document.getElementById('routeSelect');
            if (!select || select.options.length === 0) return;
            const opt = select.options[select.selectedIndex];
            const occupied = JSON.parse(opt.getAttribute('data-occupied') || '[]');
            
            selectedSeats = [];
            updateFareCalculations();

            const grid = document.getElementById('seatGrid');
            grid.innerHTML = '';

            for (let r = 1; r <= seatRows; r++) {
                const rowDiv = document.createElement('div');
                rowDiv.className = 'flex justify-between items-center gap-1';

                const leftDiv = document.createElement('div');
                leftDiv.className = 'flex gap-1.5';
                ['A', 'B'].forEach(col => {
                    const sId = r + col;
                    leftDiv.appendChild(createSeatBtn(sId, occupied.includes(sId)));
                });

                const aisle = document.createElement('div');
                aisle.className = 'text-[9px] font-mono text-neutral-600 px-1 select-none';
                aisle.innerText = '0' + r;

                const rightDiv = document.createElement('div');
                rightDiv.className = 'flex gap-1.5';
                ['C', 'D'].forEach(col => {
                    const sId = r + col;
                    rightDiv.appendChild(createSeatBtn(sId, occupied.includes(sId)));
                });

                rowDiv.appendChild(leftDiv);
                rowDiv.appendChild(aisle);
                rowDiv.appendChild(rightDiv);
                grid.appendChild(rowDiv);
            }
        }

        function createSeatBtn(seatId, isOccupied) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.id = 'seat-' + seatId;
            btn.className = `seat w-9 h-8 border text-[11px] font-mono font-medium flex items-center justify-center ${
                isOccupied ? 'occupied' : 'available bg-[#0e0e0e] border-luxury text-neutral-300'
            }`;
            btn.innerText = seatId;
            if (isOccupied) {
                btn.disabled = true;
            } else {
                btn.onclick = () => toggleSeat(seatId);
            }
            return btn;
        }

        function toggleSeat(seatId) {
            const btn = document.getElementById('seat-' + seatId);
            if (selectedSeats.includes(seatId)) {
                selectedSeats = selectedSeats.filter(s => s !== seatId);
                btn.classList.remove('selected');
            } else {
                selectedSeats.push(seatId);
                btn.classList.add('selected');
            }
            updateFareCalculations();
        }

        function updateFareCalculations() {
            const select = document.getElementById('routeSelect');
            if (!select || select.options.length === 0) return;
            const price = parseInt(select.options[select.selectedIndex].getAttribute('data-price') || 0);
            const count = selectedSeats.length;

            document.getElementById('selectedSeatsInput').value = selectedSeats.join(',');
            document.getElementById('selectedSeatsLabel').innerText = count > 0 ? selectedSeats.join(', ') : 'None';
            document.getElementById('seatCountLabel').innerText = count;

            let subtotal = count * price;
            let discount = 0;

            if (count >= 4) {
                discount = Math.round(subtotal * 0.10);
                document.getElementById('discountRow').style.display = 'flex';
                document.getElementById('discountLabel').innerText = '- Rs. ' + discount.toLocaleString();
            } else {
                document.getElementById('discountRow').style.display = 'none';
            }

            const total = subtotal - discount;
            document.getElementById('totalFareLabel').innerText = 'Rs. ' + total.toLocaleString();
            document.getElementById('bookSubmitBtn').disabled = (count === 0);
        }

        function openAuthModal(mode) {
            document.getElementById('authModal').classList.remove('hidden');
            if (mode === 'register') {
                showRegister();
            } else {
                showLogin();
            }
        }

        function closeAuthModal() {
            document.getElementById('authModal').classList.add('hidden');
        }

        function showLogin() {
            document.getElementById('authModalTitle').innerText = 'Sign In';
            document.getElementById('loginForm').classList.remove('hidden');
            document.getElementById('registerForm').classList.add('hidden');
            document.getElementById('toggleAuthBtn').innerText = 'Need an account? Click here to register';
            document.getElementById('toggleAuthBtn').onclick = showRegister;
        }

        function showRegister() {
            document.getElementById('authModalTitle').innerText = 'Register';
            document.getElementById('loginForm').classList.add('hidden');
            document.getElementById('registerForm').classList.remove('hidden');
            document.getElementById('toggleAuthBtn').innerText = 'Already have an account? Click here to sign in';
            document.getElementById('toggleAuthBtn').onclick = showLogin;
        }

        function toggleAuthMode() {
            const isLogin = !document.getElementById('loginForm').classList.contains('hidden');
            if (isLogin) showRegister(); else showLogin();
        }

        function openTicketModal(b) {
            document.getElementById('mTicketId').innerText = b.booking_id;
            document.getElementById('mPassenger').innerText = b.passenger_name;
            document.getElementById('mPhone').innerText = b.phone + ' | ' + b.cnic;
            document.getElementById('mRoute').innerText = b.route_id;
            document.getElementById('mTime').innerText = b.created_at;
            document.getElementById('mSeats').innerText = b.seats.join(', ');
            document.getElementById('mFare').innerText = 'Rs. ' + b.total_fare.toLocaleString();
            document.getElementById('ticketModal').classList.remove('hidden');
        }

        function closeTicketModal() {
            document.getElementById('ticketModal').classList.add('hidden');
        }

        window.onload = renderBusSeats;
    </script>
</body>
</html>
"""


# ==========================================
# 3. ROUTE CONTROLLERS & SERVER LOGIC
# ==========================================
@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def index(path):
    init_db()
    conn = get_db()
    cursor = conn.cursor()

    alert_message = None
    alert_color = ""

    # Current session user
    current_user = None
    if "user_id" in session:
        cursor.execute(
            "SELECT id, name, email, role FROM users WHERE id = ?",
            (session["user_id"],),
        )
        row = cursor.fetchone()
        if row:
            current_user = dict(row)

    if request.method == "POST":
        action = request.form.get("action_type")

        # -----------------------------
        # 1. USER REGISTRATION
        # -----------------------------
        if action == "register":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "").strip()

            if name and email and len(password) >= 6:
                try:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    pwd_hash = generate_password_hash(password)
                    cursor.execute(
                        "INSERT INTO users (name, email, password_hash, role, created_at) VALUES (?, ?, ?, 'passenger', ?)",
                        (name, email, pwd_hash, now),
                    )
                    conn.commit()

                    # Auto login after signup
                    new_id = cursor.lastrowid
                    session["user_id"] = new_id
                    session["user_role"] = "passenger"
                    session["user_name"] = name
                    alert_message = (
                        f"✓ Welcome, {name}! Your account has been registered."
                    )
                    alert_color = "bg-neutral-900 text-white border-white"
                    current_user = {
                        "id": new_id,
                        "name": name,
                        "email": email,
                        "role": "passenger",
                    }
                except sqlite3.IntegrityError:
                    alert_message = "✕ Registration Failed: An account with this email already exists."
                    alert_color = "bg-neutral-900 text-red-400 border-red-500"
            else:
                alert_message = "✕ Password must be at least 6 characters."
                alert_color = "bg-neutral-900 text-amber-300 border-amber-500"

        # -----------------------------
        # 2. USER LOGIN
        # -----------------------------
        elif action == "login":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "").strip()

            cursor.execute(
                "SELECT id, name, email, password_hash, role FROM users WHERE email = ?",
                (email,),
            )
            user_row = cursor.fetchone()

            if user_row and check_password_hash(user_row["password_hash"], password):
                session["user_id"] = user_row["id"]
                session["user_role"] = user_row["role"]
                session["user_name"] = user_row["name"]
                current_user = dict(user_row)
                alert_message = (
                    f"✓ Welcome back, {user_row['name']}! Authenticated successfully."
                )
                alert_color = "bg-neutral-900 text-white border-white"
            else:
                alert_message = (
                    "✕ Authentication Failed: Invalid email or password credentials."
                )
                alert_color = "bg-neutral-900 text-red-400 border-red-500"

        # -----------------------------
        # 3. USER LOGOUT
        # -----------------------------
        elif action == "logout":
            session.clear()
            current_user = None
            alert_message = "✓ You have been signed out."
            alert_color = "bg-neutral-900 text-neutral-300 border-neutral-600"

        # -----------------------------
        # 4. BOOK TICKET
        # -----------------------------
        elif action == "book":
            name = request.form.get("name", "").strip()
            phone = request.form.get("phone", "").strip()
            cnic = request.form.get("cnic", "").strip()
            age = int(request.form.get("age", 0))
            route_id = request.form.get("route_id", "")
            seats_str = request.form.get("selected_seats", "").strip()
            chosen_seats = [s.strip() for s in seats_str.split(",") if s.strip()]

            cursor.execute("SELECT * FROM routes WHERE route_id = ?", (route_id,))
            r_row = cursor.fetchone()

            if r_row and chosen_seats and name and phone and age > 0:
                occupied_list = json.loads(r_row["occupied_seats"])

                # Check for duplicate seat assignment
                conflict = any(s in occupied_list for s in chosen_seats)
                if conflict:
                    alert_message = "✕ Seat Conflict: One of the selected seats was just taken. Please re-select."
                    alert_color = "bg-neutral-900 text-red-400 border-red-500"
                else:
                    seat_count = len(chosen_seats)
                    subtotal = r_row["ticket_price"] * seat_count
                    discount = round(subtotal * 0.10) if seat_count >= 4 else 0
                    final_fare = subtotal - discount

                    # Generate new sequential booking ID from DB
                    cursor.execute("SELECT COUNT(*) FROM bookings")
                    next_id_num = 1001 + cursor.fetchone()[0]
                    booking_id = f"LX-{next_id_num}"

                    # Update Route in SQLite
                    occupied_list.extend(chosen_seats)
                    new_avail = r_row["available_seats"] - seat_count
                    cursor.execute(
                        "UPDATE routes SET occupied_seats = ?, available_seats = ? WHERE route_id = ?",
                        (json.dumps(occupied_list), new_avail, route_id),
                    )

                    # Insert Booking in SQLite
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    user_id_val = current_user["id"] if current_user else None
                    cursor.execute(
                        """
                    INSERT INTO bookings VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                        (
                            booking_id,
                            user_id_val,
                            name,
                            phone,
                            cnic,
                            age,
                            route_id,
                            json.dumps(chosen_seats),
                            subtotal,
                            discount,
                            final_fare,
                            "Confirmed",
                            now,
                        ),
                    )
                    conn.commit()

                    alert_message = f"✓ Pass {booking_id} Confirmed! Seat(s): {', '.join(chosen_seats)}. Saved in Database."
                    alert_color = "bg-neutral-900 text-white border-white"

        # -----------------------------
        # 5. CANCEL BOOKING
        # -----------------------------
        elif action == "cancel":
            b_id = request.form.get("booking_id")
            cursor.execute(
                "SELECT * FROM bookings WHERE booking_id = ? AND status = 'Confirmed'",
                (b_id,),
            )
            b_row = cursor.fetchone()

            if b_row:
                b_seats = json.loads(b_row["seats"])
                r_id = b_row["route_id"]

                # Restore seats in Route
                cursor.execute("SELECT * FROM routes WHERE route_id = ?", (r_id,))
                r_row = cursor.fetchone()
                if r_row:
                    occ = json.loads(r_row["occupied_seats"])
                    new_occ = [s for s in occ if s not in b_seats]
                    new_avail = min(
                        r_row["total_seats"], r_row["available_seats"] + len(b_seats)
                    )
                    cursor.execute(
                        "UPDATE routes SET occupied_seats = ?, available_seats = ? WHERE route_id = ?",
                        (json.dumps(new_occ), new_avail, r_id),
                    )

                # Mark Cancelled in Database
                cursor.execute(
                    "UPDATE bookings SET status = 'Cancelled' WHERE booking_id = ?",
                    (b_id,),
                )
                conn.commit()

                alert_message = f"✓ Pass {b_id} Voided. {len(b_seats)} seat(s) restored to route availability."
                alert_color = "bg-neutral-900 text-neutral-300 border-neutral-500"

        # -----------------------------
        # 6. ADMIN: ADD ROUTE
        # -----------------------------
        elif action == "add_route" and current_user and current_user["role"] == "admin":
            r_id = request.form.get("new_route_id", "").strip().upper()
            price = int(request.form.get("new_price", 1000))
            dep = request.form.get("new_dep_city", "").strip()
            dest = request.form.get("new_dest_city", "").strip()
            dep_time = request.form.get("new_dep_time", "").strip()
            arr_time = request.form.get("new_arr_time", "Scheduled").strip()
            model = request.form.get("new_model", "Mercedes-Benz Travego VIP").strip()

            if r_id and dep and dest:
                cursor.execute(
                    "INSERT OR REPLACE INTO routes VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        r_id,
                        dep,
                        dest,
                        dep_time,
                        arr_time,
                        price,
                        28,
                        28,
                        model,
                        "Royal First Class",
                        json.dumps([]),
                    ),
                )
                conn.commit()
                alert_message = (
                    f"✓ Route {r_id} successfully added to database inventory."
                )
                alert_color = "bg-neutral-900 text-white border-white"

    # Fetch All Data from Database for Rendering
    cursor.execute("SELECT * FROM routes")
    routes_rows = cursor.fetchall()
    routes_list = [dict(r) for r in routes_rows]

    # Fetch Bookings
    cursor.execute("SELECT * FROM bookings ORDER BY created_at DESC")
    all_bookings_rows = cursor.fetchall()
    all_bookings = []
    for b in all_bookings_rows:
        b_dict = dict(b)
        b_dict["seats"] = json.loads(b_dict["seats"])
        all_bookings.append(b_dict)

    # Filter bookings for the current user (if logged in as passenger)
    if current_user and current_user["role"] != "admin":
        user_bookings = [b for b in all_bookings if b["user_id"] == current_user["id"]]
    else:
        user_bookings = all_bookings

    # Financial / Operational KPIs
    total_reserved = sum(
        len(b["seats"]) for b in all_bookings if b["status"] == "Confirmed"
    )
    confirmed_count = sum(1 for b in all_bookings if b["status"] == "Confirmed")
    cancelled_count = sum(1 for b in all_bookings if b["status"] == "Cancelled")
    total_revenue = sum(
        b["total_fare"] for b in all_bookings if b["status"] == "Confirmed"
    )

    conn.close()

    return render_template_string(
        HTML_TEMPLATE,
        current_user=current_user,
        routes=routes_list,
        bookings=user_bookings,
        all_bookings=all_bookings,
        total_reserved=total_reserved,
        confirmed_count=confirmed_count,
        cancelled_count=cancelled_count,
        total_revenue=total_revenue,
        alert_message=alert_message,
        alert_color=alert_color,
    )


if __name__ == "__main__":
    app.run(debug=True)
