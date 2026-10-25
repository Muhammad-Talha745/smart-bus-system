from flask import Flask, render_template_string, request

app = Flask(__name__)

# ==========================================
# 1. LUXURY DATA & FLEET STATE
# ==========================================
routes = [
    {
        "route_id": "LX-101",
        "departure_city": "Karachi",
        "destination_city": "Hyderabad",
        "departure_time": "08:00 AM",
        "arrival_time": "10:30 AM",
        "ticket_price": 1800,
        "total_seats": 28,
        "available_seats": 26,
        "bus_model": "Mercedes-Benz Travego VIP",
        "class": "Royal First Class",
        "occupied_seats": ["1A", "1B"],
    },
    {
        "route_id": "LX-102",
        "departure_city": "Karachi",
        "destination_city": "Sukkur",
        "departure_time": "09:30 AM",
        "arrival_time": "03:30 PM",
        "ticket_price": 3200,
        "total_seats": 28,
        "available_seats": 27,
        "bus_model": "Volvo 9900 Executive Sleeper",
        "class": "Imperial Suite",
        "occupied_seats": ["3C"],
    },
    {
        "route_id": "LX-103",
        "departure_city": "Hyderabad",
        "destination_city": "Mirpur Khas",
        "departure_time": "11:00 AM",
        "arrival_time": "12:45 PM",
        "ticket_price": 1200,
        "total_seats": 28,
        "available_seats": 28,
        "bus_model": "Scania Touring HD",
        "class": "Executive Business",
        "occupied_seats": [],
    },
    {
        "route_id": "LX-104",
        "departure_city": "Karachi",
        "destination_city": "Lahore",
        "departure_time": "07:00 PM",
        "arrival_time": "09:00 AM",
        "ticket_price": 6500,
        "total_seats": 28,
        "available_seats": 24,
        "bus_model": "Setra S 531 DT Double-Decker",
        "class": "Presidential Stateroom",
        "occupied_seats": ["1A", "1B", "2A", "2B"],
    },
    {
        "route_id": "LX-105",
        "departure_city": "Sukkur",
        "destination_city": "Hyderabad",
        "departure_time": "02:00 PM",
        "arrival_time": "06:30 PM",
        "ticket_price": 2200,
        "total_seats": 28,
        "available_seats": 28,
        "bus_model": "Mercedes-Benz Travego VIP",
        "class": "Royal First Class",
        "occupied_seats": [],
    },
]

bookings = [
    {
        "booking_id": "LX-1001",
        "passenger_name": "Tariq Mansoor",
        "phone": "+92 300 1234567",
        "cnic": "42101-9876543-1",
        "passenger_age": 34,
        "route_id": "LX-101",
        "seats": ["1A", "1B"],
        "subtotal": 3600,
        "discount": 0,
        "total_fare": 3600,
        "status": "Confirmed",
        "departure": "Karachi ➔ Hyderabad",
        "departure_time": "08:00 AM",
        "class": "Royal First Class",
    }
]

booking_counter = 1002

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SMART BUS | Haute Luxury Intercity Transit</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Cinzel:wght@500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #030303; }
        .font-luxury { font-family: 'Cinzel', serif; }
        .border-luxury { border-color: rgba(255, 255, 255, 0.12); }
        .bg-luxury-card { background-color: #0C0C0C; }
        .bg-luxury-input { background-color: #141414; }
        
        .nav-btn.active {
            color: #FFFFFF !important;
            border-bottom: 2px solid #FFFFFF !important;
        }

        .seat {
            transition: all 0.15s ease;
        }
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
            border-color: #282828 !important;
            color: #555555 !important;
            cursor: not-allowed;
            text-decoration: line-through;
        }
    </style>
</head>
<body class="text-white min-h-screen selection:bg-white selection:text-black">

    <!-- Top Luxury Bar -->
    <header class="border-b border-luxury sticky top-0 bg-[#030303]/90 backdrop-blur-xl z-50">
        <div class="max-w-7xl mx-auto px-6 py-4 flex flex-col md:flex-row justify-between items-center gap-4">
            
            <div class="flex items-center space-x-3 cursor-pointer" onclick="switchTab('bookingTab')">
                <div class="w-9 h-9 border border-white flex items-center justify-center font-luxury font-bold text-base tracking-tighter">
                    SB
                </div>
                <div>
                    <h1 class="text-lg font-bold tracking-widest font-luxury uppercase">Smart Bus</h1>
                    <p class="text-[9px] tracking-[0.3em] text-neutral-400 uppercase">Executive Travel Fleet</p>
                </div>
            </div>

            <!-- Multi-Page Navigation Links -->
            <nav class="flex items-center space-x-6 text-xs uppercase tracking-wider font-medium">
                <button onclick="switchTab('bookingTab')" id="nav-bookingTab" class="nav-btn py-2 text-neutral-400 hover:text-white transition active">
                    Book Journey
                </button>
                <button onclick="switchTab('fleetTab')" id="nav-fleetTab" class="nav-btn py-2 text-neutral-400 hover:text-white transition">
                    Fleet & Routes
                </button>
                <button onclick="switchTab('pnrTab')" id="nav-pnrTab" class="nav-btn py-2 text-neutral-400 hover:text-white transition">
                    Boarding Pass
                </button>
                <button onclick="switchTab('aboutTab')" id="nav-aboutTab" class="nav-btn py-2 text-neutral-400 hover:text-white transition">
                    Standards
                </button>
                <button onclick="switchTab('adminTab')" id="nav-adminTab" class="nav-btn py-1.5 px-3 border border-white/30 rounded hover:border-white hover:bg-white hover:text-black text-neutral-300 transition">
                    🔒 Admin Portal
                </button>
            </nav>
        </div>
    </header>

    <!-- Global Notifications -->
    {% if alert_message %}
    <div class="max-w-7xl mx-auto px-6 mt-6">
        <div class="p-4 rounded border text-xs uppercase tracking-widest font-mono flex items-center justify-between {{ alert_color }}">
            <span>{{ alert_message }}</span>
        </div>
    </div>
    {% endif %}

    <!-- ============================================================== -->
    <!-- PAGE 1: PASSENGER BOOKING CONSOLE (DEFAULT)                     -->
    <!-- ============================================================== -->
    <div id="bookingTab" class="page-content max-w-7xl mx-auto px-6 py-10 space-y-10">
        
        <!-- Hero Tagline -->
        <div class="border-b border-luxury pb-6 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
            <div>
                <span class="text-[10px] font-mono uppercase tracking-[0.3em] text-neutral-400">Reserve Private Charter Seating</span>
                <h2 class="text-3xl md:text-4xl font-luxury font-bold mt-1 tracking-tight">First-Class Intercity Travel</h2>
            </div>
            <div class="text-right">
                <span class="text-xs font-mono text-neutral-400">Total Fleet Journeys Today</span>
                <p class="text-xl font-bold font-mono">05 Active Routes</p>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            
            <!-- Reservation Form with Real Seat Selection -->
            <section class="lg:col-span-5 bg-luxury-card border border-luxury p-7 rounded-none space-y-6">
                <div class="border-b border-luxury pb-4">
                    <span class="text-[10px] font-mono uppercase tracking-widest text-neutral-400">Step 01 / Reservation Desk</span>
                    <h3 class="text-xl font-luxury font-bold uppercase mt-1">Passenger Manifesto</h3>
                </div>

                <form method="POST" action="" id="bookingForm" class="space-y-4">
                    <input type="hidden" name="action_type" value="book">
                    <input type="hidden" name="selected_seats" id="selectedSeatsInput" value="">

                    <div>
                        <label class="block text-[10px] font-mono uppercase tracking-wider text-neutral-400 mb-1">Full Passenger Name</label>
                        <input type="text" name="name" placeholder="Lord / Lady / Full Name" required
                               class="w-full bg-luxury-input text-white border border-luxury px-3.5 py-2.5 text-sm focus:outline-none focus:border-white transition">
                    </div>

                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block text-[10px] font-mono uppercase tracking-wider text-neutral-400 mb-1">Mobile Contact</label>
                            <input type="tel" name="phone" placeholder="0300-1234567" required
                                   class="w-full bg-luxury-input text-white border border-luxury px-3.5 py-2.5 text-sm focus:outline-none focus:border-white transition">
                        </div>
                        <div>
                            <label class="block text-[10px] font-mono uppercase tracking-wider text-neutral-400 mb-1">National ID / CNIC</label>
                            <input type="text" name="cnic" placeholder="42101-XXXXXXX-X" required
                                   class="w-full bg-luxury-input text-white border border-luxury px-3.5 py-2.5 text-sm focus:outline-none focus:border-white transition">
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block text-[10px] font-mono uppercase tracking-wider text-neutral-400 mb-1">Age</label>
                            <input type="number" name="age" min="1" max="110" placeholder="e.g. 30" required
                                   class="w-full bg-luxury-input text-white border border-luxury px-3.5 py-2.5 text-sm focus:outline-none focus:border-white transition">
                        </div>
                        <div>
                            <label class="block text-[10px] font-mono uppercase tracking-wider text-neutral-400 mb-1">Luggage Preference</label>
                            <select class="w-full bg-luxury-input text-white border border-luxury px-3.5 py-2.5 text-sm focus:outline-none">
                                <option>Executive 30kg + Cabin</option>
                                <option>VIP Stateroom 45kg</option>
                            </select>
                        </div>
                    </div>

                    <div>
                        <label class="block text-[10px] font-mono uppercase tracking-wider text-neutral-400 mb-1">Select Scheduled Service</label>
                        <select name="route_id" id="routeSelect" onchange="renderBusSeats()" 
                                class="w-full bg-luxury-input text-white border border-luxury px-3.5 py-2.5 text-sm focus:outline-none cursor-pointer">
                            {% for r in routes %}
                            <option value="{{ r.route_id }}" data-price="{{ r.ticket_price }}" data-occupied='{{ r.occupied_seats | tojson }}'>
                                {{ r.route_id }} • {{ r.departure_city }} ➔ {{ r.destination_city }} (Rs. {{ "{:,}".format(r.ticket_price) }})
                            </option>
                            {% endfor %}
                        </select>
                    </div>

                    <!-- Visual Bus Cabin -->
                    <div class="border border-luxury p-4 bg-black/60 space-y-3">
                        <div class="flex justify-between items-center text-[10px] font-mono uppercase text-neutral-400 border-b border-luxury pb-2">
                            <span>Pilot Cabin ❖ Front</span>
                            <div class="flex items-center space-x-3">
                                <span class="flex items-center"><span class="w-2 h-2 border border-neutral-600 bg-neutral-900 mr-1"></span> Free</span>
                                <span class="flex items-center"><span class="w-2 h-2 bg-white mr-1"></span> Selected</span>
                                <span class="flex items-center"><span class="w-2 h-2 bg-neutral-800 mr-1"></span> Sold</span>
                            </div>
                        </div>

                        <!-- 28 Seat Blueprint -->
                        <div id="seatGrid" class="space-y-2 py-2"></div>
                    </div>

                    <!-- Summary & VIP Group Discount Calculation -->
                    <div class="p-4 bg-luxury-input border border-luxury text-xs font-mono space-y-1.5">
                        <div class="flex justify-between text-neutral-400">
                            <span>Chosen Seats:</span>
                            <span id="selectedSeatsLabel" class="text-white font-bold">None</span>
                        </div>
                        <div class="flex justify-between text-neutral-400">
                            <span>Total Count:</span>
                            <span id="seatCountLabel" class="text-white">0</span>
                        </div>
                        <div class="flex justify-between text-emerald-400" id="discountRow" style="display: none;">
                            <span>VIP Corporate Discount (-10%):</span>
                            <span id="discountLabel">- Rs. 0</span>
                        </div>
                        <div class="flex justify-between text-sm pt-2 border-t border-luxury font-bold text-white">
                            <span>Payable Amount:</span>
                            <span id="totalFareLabel" class="text-base font-luxury">Rs. 0</span>
                        </div>
                    </div>

                    <button type="submit" id="bookSubmitBtn" disabled
                            class="w-full py-3.5 bg-white text-black hover:bg-neutral-200 transition font-bold text-xs uppercase tracking-widest disabled:opacity-20 disabled:cursor-not-allowed">
                        Confirm Reservation & Issue Pass ➔
                    </button>
                </form>
            </section>

            <!-- Active Fleet Departures Table -->
            <section class="lg:col-span-7 space-y-6">
                
                <div class="bg-luxury-card border border-luxury p-6">
                    <div class="flex justify-between items-center border-b border-luxury pb-4 mb-4">
                        <div>
                            <span class="text-[10px] font-mono uppercase tracking-widest text-neutral-400">Live Manifest</span>
                            <h3 class="text-lg font-luxury font-bold uppercase">Scheduled Departures</h3>
                        </div>
                        <span class="text-xs font-mono text-neutral-400">Synchronized Real-Time</span>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-sm">
                            <thead>
                                <tr class="text-[10px] font-mono uppercase tracking-wider text-neutral-400 border-b border-luxury pb-2">
                                    <th class="pb-3">Route</th>
                                    <th class="pb-3">Origin ➔ Destination</th>
                                    <th class="pb-3">Departure</th>
                                    <th class="pb-3">Class</th>
                                    <th class="pb-3">Fare</th>
                                    <th class="pb-3 text-right">Available</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-luxury text-xs">
                                {% for r in routes %}
                                <tr class="hover:bg-white/[0.02] transition">
                                    <td class="py-3.5 font-mono font-bold text-white">{{ r.route_id }}</td>
                                    <td class="py-3.5">
                                        <div class="font-bold text-white">{{ r.departure_city }} ➔ {{ r.destination_city }}</div>
                                        <div class="text-[10px] text-neutral-400">{{ r.bus_model }}</div>
                                    </td>
                                    <td class="py-3.5 font-mono text-neutral-300">{{ r.departure_time }}</td>
                                    <td class="py-3.5">
                                        <span class="px-2 py-0.5 border border-white/20 text-[10px] uppercase font-mono tracking-wider">
                                            {{ r.class }}
                                        </span>
                                    </td>
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

                <!-- Recent Passenger Boarding Passes -->
                <div class="bg-luxury-card border border-luxury p-6">
                    <div class="flex justify-between items-center border-b border-luxury pb-4 mb-4">
                        <div>
                            <span class="text-[10px] font-mono uppercase tracking-widest text-neutral-400">Boarding Passes</span>
                            <h3 class="text-lg font-luxury font-bold uppercase">Issued Passenger Manifest</h3>
                        </div>
                    </div>

                    {% if not bookings %}
                    <p class="text-neutral-500 text-xs py-4 text-center font-mono uppercase">No records issued in current session.</p>
                    {% else %}
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs font-mono">
                            <thead>
                                <tr class="text-[10px] uppercase tracking-wider text-neutral-400 border-b border-luxury">
                                    <th class="pb-2">Pass #</th>
                                    <th class="pb-2">Passenger</th>
                                    <th class="pb-2">Seats</th>
                                    <th class="pb-2">Total Paid</th>
                                    <th class="pb-2">Status</th>
                                    <th class="pb-2 text-right">Document</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-luxury">
                                {% for b in bookings %}
                                <tr>
                                    <td class="py-3 font-bold text-white">{{ b.booking_id }}</td>
                                    <td class="py-3 font-sans font-medium text-white">{{ b.passenger_name }}</td>
                                    <td class="py-3">
                                        {% for s in b.seats %}
                                        <span class="border border-white/20 px-1 py-0.5 text-[9px] mr-1">{{ s }}</span>
                                        {% endfor %}
                                    </td>
                                    <td class="py-3 font-bold">Rs. {{ "{:,}".format(b.total_fare) }}</td>
                                    <td class="py-3">
                                        <span class="px-2 py-0.5 text-[10px] uppercase font-bold {% if b.status == 'Confirmed' %}bg-white text-black{% else %}border border-red-500 text-red-400{% endif %}">
                                            {{ b.status }}
                                        </span>
                                    </td>
                                    <td class="py-3 text-right">
                                        <button onclick='openTicketModal({{ b | tojson }})' 
                                                class="px-2.5 py-1 border border-white text-white hover:bg-white hover:text-black text-[10px] uppercase transition font-mono">
                                            Print E-Ticket 🖨
                                        </button>
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
    </div>

    <!-- ============================================================== -->
    <!-- PAGE 2: FLEET & ROUTES SHOWCASE                                -->
    <!-- ============================================================== -->
    <div id="fleetTab" class="page-content max-w-7xl mx-auto px-6 py-10 space-y-10 hidden">
        <div class="border-b border-luxury pb-4">
            <span class="text-[10px] font-mono uppercase tracking-widest text-neutral-400">The Master Fleet</span>
            <h2 class="text-3xl font-luxury font-bold uppercase mt-1">Intercity Fleet Portfolio</h2>
            <p class="text-xs text-neutral-400 mt-1 max-w-2xl">Every coach in our fleet is custom-commissioned with ergonomic sleeper cabins, high-speed Starlink connectivity, and individual passenger climate controls.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            {% for r in routes %}
            <div class="bg-luxury-card border border-luxury p-6 flex flex-col justify-between space-y-4">
                <div>
                    <div class="flex justify-between items-center text-xs font-mono text-neutral-400 mb-2">
                        <span>{{ r.route_id }}</span>
                        <span class="border border-white/20 px-2 py-0.5 uppercase text-[9px]">{{ r.class }}</span>
                    </div>
                    <h3 class="text-xl font-luxury font-bold">{{ r.departure_city }} ➔ {{ r.destination_city }}</h3>
                    <p class="text-xs text-neutral-400 font-mono mt-1">{{ r.bus_model }}</p>
                </div>

                <div class="border-t border-b border-luxury py-3 my-2 text-xs font-mono space-y-1 text-neutral-300">
                    <div class="flex justify-between">
                        <span>Departure Time:</span>
                        <span class="text-white font-bold">{{ r.departure_time }}</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Estimated Arrival:</span>
                        <span class="text-white font-bold">{{ r.arrival_time }}</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Standard Fare:</span>
                        <span class="text-white font-bold">Rs. {{ "{:,}".format(r.ticket_price) }}</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Seating Configuration:</span>
                        <span class="text-white">2x2 Luxury Recliner</span>
                    </div>
                </div>

                <button onclick="selectRouteAndGo('{{ r.route_id }}')" class="w-full py-2.5 border border-white text-white hover:bg-white hover:text-black font-bold text-xs uppercase tracking-widest transition">
                    Reserve On This Coach ➔
                </button>
            </div>
            {% endfor %}
        </div>
    </div>

    <!-- ============================================================== -->
    <!-- PAGE 3: PNR & BOARDING PASS LOOKUP                             -->
    <!-- ============================================================== -->
    <div id="pnrTab" class="page-content max-w-7xl mx-auto px-6 py-10 space-y-10 hidden">
        <div class="border-b border-luxury pb-4">
            <span class="text-[10px] font-mono uppercase tracking-widest text-neutral-400">Electronic Verification</span>
            <h2 class="text-3xl font-luxury font-bold uppercase mt-1">Boarding Pass Terminal</h2>
        </div>

        <div class="max-w-xl mx-auto bg-luxury-card border border-luxury p-8 space-y-6">
            <h3 class="text-lg font-luxury font-bold uppercase text-center">Retrieve Digital Boarding Pass</h3>
            <p class="text-xs text-neutral-400 text-center">Enter your issued Pass ID (e.g. LX-1001) to verify reservation status and print travel passes.</p>
            
            <div class="space-y-4">
                <div>
                    <label class="block text-[10px] font-mono uppercase text-neutral-400 mb-1">Pass / Ticket ID</label>
                    <input type="text" id="lookupIdInput" placeholder="LX-1001" class="w-full bg-luxury-input border border-luxury px-3.5 py-2.5 text-sm font-mono focus:outline-none focus:border-white">
                </div>
                <button onclick="searchPass()" class="w-full py-3 bg-white text-black font-bold text-xs uppercase tracking-widest hover:bg-neutral-200 transition">
                    Locate Boarding Pass
                </button>
            </div>

            <div id="lookupResult" class="hidden border-t border-luxury pt-4 text-xs font-mono space-y-2"></div>
        </div>
    </div>

    <!-- ============================================================== -->
    <!-- PAGE 4: EXECUTIVE STANDARDS (ABOUT)                            -->
    <!-- ============================================================== -->
    <div id="aboutTab" class="page-content max-w-7xl mx-auto px-6 py-10 space-y-10 hidden">
        <div class="border-b border-luxury pb-4">
            <span class="text-[10px] font-mono uppercase tracking-widest text-neutral-400">Haute Mobility</span>
            <h2 class="text-3xl font-luxury font-bold uppercase mt-1">The Smart Bus Standards</h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div class="bg-luxury-card border border-luxury p-6 space-y-3">
                <span class="text-2xl font-luxury">01</span>
                <h3 class="text-lg font-luxury font-bold">First-Class Sleepers</h3>
                <p class="text-xs text-neutral-400 leading-relaxed">Individually partitioned lie-flat seats upholstered in Italian full-grain leather, equipped with pneumatic lumbar support and noise-cancellation acoustics.</p>
            </div>
            <div class="bg-luxury-card border border-luxury p-6 space-y-3">
                <span class="text-2xl font-luxury">02</span>
                <h3 class="text-lg font-luxury font-bold">Dedicated Flight Crew</h3>
                <p class="text-xs text-neutral-400 leading-relaxed">Every journey features certified cabin stewards serving gourmet hot beverages, refreshments, warm towels, and bespoke travel kits.</p>
            </div>
            <div class="bg-luxury-card border border-luxury p-6 space-y-3">
                <span class="text-2xl font-luxury">03</span>
                <h3 class="text-lg font-luxury font-bold">Terminal Priority</h3>
                <p class="text-xs text-neutral-400 leading-relaxed">Skip the crowd. Access private Smart Bus executive arrival lounges with private parking, high-speed fiber internet, and complimentary luggage handlers.</p>
            </div>
        </div>
    </div>

    <!-- ============================================================== -->
    <!-- PAGE 5: 🔒 MASTER ADMIN PORTAL                                 -->
    <!-- ============================================================== -->
    <div id="adminTab" class="page-content max-w-7xl mx-auto px-6 py-10 space-y-10 hidden">
        <div class="border-b border-luxury pb-4 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
            <div>
                <span class="text-[10px] font-mono uppercase tracking-widest text-neutral-400">Executive Fleet Control</span>
                <h2 class="text-3xl font-luxury font-bold uppercase mt-1">Command & Analytics Portal</h2>
            </div>
            <div class="text-right">
                <span class="px-3 py-1 border border-white text-xs font-mono uppercase">Role: Fleet Operations Controller</span>
            </div>
        </div>

        <!-- Financial & Fleet KPIs -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="bg-luxury-card border border-luxury p-5">
                <p class="text-[10px] font-mono uppercase text-neutral-400">Gross Ticket Sales</p>
                <p class="text-2xl font-bold font-mono text-white mt-1">Rs. {{ "{:,}".format(total_revenue) }}</p>
            </div>
            <div class="bg-luxury-card border border-luxury p-5">
                <p class="text-[10px] font-mono uppercase text-neutral-400">Total Travelers Transported</p>
                <p class="text-2xl font-bold font-mono text-white mt-1">{{ total_reserved }} Seats</p>
            </div>
            <div class="bg-luxury-card border border-luxury p-5">
                <p class="text-[10px] font-mono uppercase text-neutral-400">Confirmed Manifests</p>
                <p class="text-2xl font-bold font-mono text-white mt-1">{{ confirmed_count }} Active</p>
            </div>
            <div class="bg-luxury-card border border-luxury p-5">
                <p class="text-[10px] font-mono uppercase text-neutral-400">Cancelled Bookings</p>
                <p class="text-2xl font-bold font-mono text-neutral-400 mt-1">{{ cancelled_count }} Void</p>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            
            <!-- Add New Route Form -->
            <div class="lg:col-span-5 bg-luxury-card border border-luxury p-6 space-y-4">
                <div class="border-b border-luxury pb-3">
                    <span class="text-[10px] font-mono uppercase tracking-widest text-neutral-400">Fleet Dispatch</span>
                    <h3 class="text-lg font-luxury font-bold uppercase mt-1">Add Route to Inventory</h3>
                </div>

                <form method="POST" action="" class="space-y-3 text-xs">
                    <input type="hidden" name="action_type" value="add_route">

                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block text-[10px] font-mono uppercase text-neutral-400 mb-1">Route ID</label>
                            <input type="text" name="new_route_id" placeholder="LX-106" required class="w-full bg-luxury-input border border-luxury px-3 py-2 text-white">
                        </div>
                        <div>
                            <label class="block text-[10px] font-mono uppercase text-neutral-400 mb-1">Base Fare (Rs.)</label>
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
                            <label class="block text-[10px] font-mono uppercase text-neutral-400 mb-1">Executive Coach Model</label>
                            <input type="text" name="new_model" placeholder="Mercedes-Benz Travego" required class="w-full bg-luxury-input border border-luxury px-3 py-2 text-white">
                        </div>
                    </div>

                    <button type="submit" class="w-full py-3 bg-white text-black font-bold uppercase tracking-wider text-xs hover:bg-neutral-200 transition mt-2">
                        + Deploy Route to Live System
                    </button>
                </form>
            </div>

            <!-- Master Manifest & Cancellation Desk -->
            <div class="lg:col-span-7 bg-luxury-card border border-luxury p-6 space-y-4">
                <div class="border-b border-luxury pb-3">
                    <span class="text-[10px] font-mono uppercase tracking-widest text-neutral-400">Master Console</span>
                    <h3 class="text-lg font-luxury font-bold uppercase mt-1">Passenger Manifest & Seat Restoral</h3>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs font-mono">
                        <thead>
                            <tr class="text-[10px] uppercase text-neutral-400 border-b border-luxury">
                                <th class="pb-2">Pass ID</th>
                                <th class="pb-2">Passenger</th>
                                <th class="pb-2">Contact</th>
                                <th class="pb-2">Seats</th>
                                <th class="pb-2">Status</th>
                                <th class="pb-2 text-right">Void Action</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-luxury">
                            {% for b in bookings %}
                            <tr>
                                <td class="py-3 font-bold text-white">{{ b.booking_id }}</td>
                                <td class="py-3 font-sans text-neutral-200">{{ b.passenger_name }}</td>
                                <td class="py-3 text-neutral-400">{{ b.phone }}</td>
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
                                    <span class="text-neutral-600 text-[10px]">Restored</span>
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

    <!-- Official Printable Digital Boarding Pass Modal -->
    <div id="ticketModal" class="fixed inset-0 bg-black/90 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
        <div class="bg-black border border-white/30 p-8 max-w-md w-full shadow-2xl relative text-white space-y-6 font-mono" id="printArea">
            
            <div class="flex justify-between items-start border-b border-white/20 pb-4">
                <div>
                    <h3 class="font-luxury font-bold text-xl tracking-wider">SMART BUS</h3>
                    <p class="text-[9px] text-neutral-400 uppercase tracking-[0.25em]">First-Class Electronic Boarding Document</p>
                </div>
                <button onclick="closeTicketModal()" class="text-neutral-400 hover:text-white text-xl font-bold">&times;</button>
            </div>

            <div class="space-y-3 text-xs">
                <div class="flex justify-between">
                    <span class="text-neutral-400 uppercase">Boarding Pass ID:</span>
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
                    <span class="text-neutral-400 font-mono uppercase">Itinerary:</span>
                    <span id="mRoute" class="text-white"></span>
                </div>
                <div class="flex justify-between">
                    <span class="text-neutral-400 uppercase">Departure Time:</span>
                    <span id="mTime" class="text-white"></span>
                </div>
                <div class="flex justify-between">
                    <span class="text-neutral-400 uppercase">Allocated Cabin Seats:</span>
                    <span id="mSeats" class="font-bold text-white tracking-widest"></span>
                </div>
                <div class="flex justify-between border-t border-white/10 pt-2 font-bold text-sm">
                    <span class="uppercase">Total Fare Paid:</span>
                    <span id="mFare" class="font-luxury"></span>
                </div>
            </div>

            <!-- Barcode Graphic Simulation -->
            <div class="pt-4 border-t border-dashed border-white/20 text-center">
                <div class="h-10 bg-[repeating-linear-gradient(90deg,#fff,#fff_2px,#000_2px,#000_6px)] opacity-80"></div>
                <p class="text-[8px] text-neutral-500 tracking-[0.3em] mt-2 uppercase">Verified Cryptographic Boarding Pass</p>
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

    <!-- Footer -->
    <footer class="border-t border-luxury py-10 text-center text-xs text-neutral-500 font-mono space-y-2 mt-20">
        <p class="font-luxury uppercase text-white tracking-widest text-sm">Smart Bus Transportation Corporation</p>
        <p>Commercial Intercity Transit System • Production Environment Vercel Deployment</p>
    </footer>

    <!-- Frontend Interactive Script -->
    <script>
        const allBookings = {{ bookings | tojson }};
        const seatRows = 7;
        let selectedSeats = [];

        function switchTab(tabId) {
            document.querySelectorAll('.page-content').forEach(p => p.classList.add('hidden'));
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

            document.getElementById(tabId).classList.remove('hidden');
            const navBtn = document.getElementById('nav-' + tabId);
            if (navBtn) navBtn.classList.add('active');
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

        function searchPass() {
            const query = document.getElementById('lookupIdInput').value.trim().toUpperCase();
            const res = document.getElementById('lookupResult');
            const match = allBookings.find(b => b.booking_id === query);

            res.classList.remove('hidden');
            if (match) {
                res.innerHTML = `
                    <div class="p-4 border border-white/20 bg-black space-y-2">
                        <div class="text-white font-bold text-sm">Pass Found: ${match.booking_id}</div>
                        <div>Passenger: <b>${match.passenger_name}</b></div>
                        <div>Itinerary: ${match.departure} (${match.departure_time})</div>
                        <div>Seats: <b>${match.seats.join(', ')}</b></div>
                        <div>Status: <span class="font-bold uppercase ${match.status === 'Confirmed' ? 'text-white' : 'text-red-400'}">${match.status}</span></div>
                        <button onclick='openTicketModal(${JSON.stringify(match)})' class="w-full mt-3 py-2 bg-white text-black font-bold uppercase text-xs">Print Pass 🖨</button>
                    </div>
                `;
            } else {
                res.innerHTML = `<p class="text-red-400 py-2">No boarding pass located matching "${query}".</p>`;
            }
        }

        function openTicketModal(b) {
            document.getElementById('mTicketId').innerText = b.booking_id;
            document.getElementById('mPassenger').innerText = b.passenger_name;
            document.getElementById('mPhone').innerText = (b.phone || 'N/A') + ' | ' + (b.cnic || '');
            document.getElementById('mRoute').innerText = b.departure;
            document.getElementById('mTime').innerText = b.departure_time;
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


@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def index(path):
    global booking_counter
    alert_message = None
    alert_color = ""

    if request.method == "POST":
        action = request.form.get("action_type")

        # 1. Booking Flow
        if action == "book":
            name = request.form.get("name", "").strip()
            phone = request.form.get("phone", "").strip()
            cnic = request.form.get("cnic", "").strip()
            age_raw = request.form.get("age", "0")
            route_id = request.form.get("route_id", "")
            seats_str = request.form.get("selected_seats", "").strip()
            selected_seats_list = [s.strip() for s in seats_str.split(",") if s.strip()]

            route = next((r for r in routes if r["route_id"] == route_id), None)

            if route and selected_seats_list and name and phone and age_raw.isdigit():
                conflict = any(
                    s in route["occupied_seats"] for s in selected_seats_list
                )
                if conflict:
                    alert_message = "✕ Seat Conflict Detected: One or more selected seats were just claimed."
                    alert_color = "bg-neutral-900 text-red-400 border-red-500/40"
                else:
                    seat_count = len(selected_seats_list)
                    subtotal = route["ticket_price"] * seat_count
                    discount = round(subtotal * 0.10) if seat_count >= 4 else 0
                    final_fare = subtotal - discount

                    booking_id = f"LX-{booking_counter}"
                    booking_counter += 1

                    route["occupied_seats"].extend(selected_seats_list)
                    route["available_seats"] -= seat_count

                    bookings.insert(
                        0,
                        {
                            "booking_id": booking_id,
                            "passenger_name": name,
                            "phone": phone,
                            "cnic": cnic,
                            "passenger_age": int(age_raw),
                            "route_id": route_id,
                            "seats": selected_seats_list,
                            "subtotal": subtotal,
                            "discount": discount,
                            "total_fare": final_fare,
                            "status": "Confirmed",
                            "departure": f"{route['departure_city']} ➔ {route['destination_city']}",
                            "departure_time": route["departure_time"],
                            "class": route["class"],
                        },
                    )
                    alert_message = f"✓ Pass {booking_id} Issued for {name} ({seat_count} seats: {', '.join(selected_seats_list)})"
                    alert_color = "bg-neutral-900 text-white border-white/40"

        # 2. Cancellation Flow
        elif action == "cancel":
            b_id = request.form.get("booking_id")
            booking = next((b for b in bookings if b["booking_id"] == b_id), None)
            if booking and booking["status"] == "Confirmed":
                route = next(
                    (r for r in routes if r["route_id"] == booking["route_id"]), None
                )
                if route:
                    route["occupied_seats"] = [
                        s for s in route["occupied_seats"] if s not in booking["seats"]
                    ]
                    route["available_seats"] = min(
                        route["total_seats"],
                        route["available_seats"] + len(booking["seats"]),
                    )
                booking["status"] = "Cancelled"
                alert_message = f"✓ Pass {b_id} Voided. Seats {', '.join(booking['seats'])} restored to inventory."
                alert_color = "bg-neutral-900 text-neutral-300 border-neutral-500"

        # 3. Admin: Add New Route
        elif action == "add_route":
            r_id = request.form.get("new_route_id", "").strip().upper()
            price = int(request.form.get("new_price", 1000))
            dep = request.form.get("new_dep_city", "").strip()
            dest = request.form.get("new_dest_city", "").strip()
            time = request.form.get("new_dep_time", "").strip()
            model = request.form.get("new_model", "Luxury Coach").strip()

            if r_id and dep and dest:
                routes.append(
                    {
                        "route_id": r_id,
                        "departure_city": dep,
                        "destination_city": dest,
                        "departure_time": time,
                        "arrival_time": "Scheduled",
                        "ticket_price": price,
                        "total_seats": 28,
                        "available_seats": 28,
                        "bus_model": model,
                        "class": "Royal First Class",
                        "occupied_seats": [],
                    }
                )
                alert_message = f"✓ Route {r_id} ({dep} ➔ {dest}) added to live fleet."
                alert_color = "bg-neutral-900 text-white border-white"

    total_reserved = sum(
        len(b["seats"]) for b in bookings if b["status"] == "Confirmed"
    )
    confirmed_count = sum(1 for b in bookings if b["status"] == "Confirmed")
    cancelled_count = sum(1 for b in bookings if b["status"] == "Cancelled")
    total_revenue = sum(b["total_fare"] for b in bookings if b["status"] == "Confirmed")

    return render_template_string(
        HTML_TEMPLATE,
        routes=routes,
        bookings=bookings,
        total_reserved=total_reserved,
        confirmed_count=confirmed_count,
        cancelled_count=cancelled_count,
        total_revenue=total_revenue,
        alert_message=alert_message,
        alert_color=alert_color,
    )


if __name__ == "__main__":
    app.run(debug=True)
