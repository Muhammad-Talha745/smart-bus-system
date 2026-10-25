from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# ==========================================
# 1. CORE DATA WITH SEAT OCCUPANCY
# ==========================================
SUPPORTED_CITIES = ("All", "Karachi", "Hyderabad", "Sukkur", "Mirpur Khas", "Lahore")

routes = [
    {
        "route_id": "LX-101",
        "departure_city": "Karachi",
        "destination_city": "Hyderabad",
        "departure_time": "08:00 AM",
        "arrival_time": "10:30 AM",
        "ticket_price": 1200,
        "total_seats": 28,
        "available_seats": 26,
        "class": "Royal Executive",
        "occupied_seats": ["1A", "1B"],  # Pre-occupied realistic starter seats
    },
    {
        "route_id": "LX-102",
        "departure_city": "Karachi",
        "destination_city": "Sukkur",
        "departure_time": "09:30 AM",
        "arrival_time": "03:30 PM",
        "ticket_price": 2000,
        "total_seats": 28,
        "available_seats": 27,
        "class": "First Class Sleeper",
        "occupied_seats": ["3C"],
    },
    {
        "route_id": "LX-103",
        "departure_city": "Hyderabad",
        "destination_city": "Mirpur Khas",
        "departure_time": "11:00 AM",
        "arrival_time": "12:45 PM",
        "ticket_price": 800,
        "total_seats": 28,
        "available_seats": 28,
        "class": "Executive Business",
        "occupied_seats": [],
    },
    {
        "route_id": "LX-104",
        "departure_city": "Karachi",
        "destination_city": "Lahore",
        "departure_time": "07:00 PM",
        "arrival_time": "09:00 AM (Next Day)",
        "ticket_price": 5000,
        "total_seats": 28,
        "available_seats": 24,
        "class": "Imperial Suite",
        "occupied_seats": ["1A", "1B", "2A", "2B"],
    },
    {
        "route_id": "LX-105",
        "departure_city": "Sukkur",
        "destination_city": "Hyderabad",
        "departure_time": "02:00 PM",
        "arrival_time": "06:30 PM",
        "ticket_price": 1500,
        "total_seats": 28,
        "available_seats": 28,
        "class": "Royal Executive",
        "occupied_seats": [],
    },
]

bookings = [
    {
        "booking_id": "LX-1001",
        "passenger_name": "Tariq Mansoor",
        "phone": "+92 300 1234567",
        "passenger_age": 34,
        "route_id": "LX-101",
        "seats": ["1A", "1B"],
        "subtotal": 2400,
        "discount": 0,
        "total_fare": 2400,
        "status": "Confirmed",
        "departure": "Karachi ➔ Hyderabad",
        "departure_time": "08:00 AM",
    }
]

booking_counter = 1002

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SMART BUS | Real-Life Luxury Transportation</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Cinzel:wght@600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
        .font-luxury { font-family: 'Cinzel', serif; }
        .glass-panel {
            background: rgba(15, 23, 42, 0.75);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .seat {
            transition: all 0.2s ease;
        }
        .seat.available:hover {
            transform: scale(1.08);
            border-color: #F59E0B;
            background-color: rgba(245, 158, 11, 0.2);
        }
        .seat.selected {
            background-color: #F59E0B !important;
            color: #000 !important;
            font-weight: bold;
            border-color: #F59E0B !important;
            box-shadow: 0 0 10px rgba(245, 158, 11, 0.5);
        }
        .seat.occupied {
            background-color: rgba(239, 68, 68, 0.15) !important;
            border-color: rgba(239, 68, 68, 0.3) !important;
            color: #EF4444 !important;
            cursor: not-allowed;
            opacity: 0.6;
        }
    </style>
</head>
<body class="bg-[#080B11] text-slate-100 min-h-screen selection:bg-amber-500 selection:text-black">

    <!-- Navbar -->
    <header class="border-b border-white/10 glass-panel sticky top-0 z-40">
        <div class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-600 to-amber-300 flex items-center justify-center text-black font-bold text-lg shadow-lg shadow-amber-500/20">
                    ⚜
                </div>
                <div>
                    <h1 class="text-xl font-bold tracking-wider font-luxury text-amber-300 uppercase">Smart Bus Executive</h1>
                    <p class="text-[10px] tracking-widest text-slate-400 uppercase">Live Intercity Travel Network</p>
                </div>
            </div>
            
            <div class="flex items-center space-x-3">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                    ● Seat Reservation Engine Active
                </span>
            </div>
        </div>
    </header>

    <!-- Main Body -->
    <main class="max-w-7xl mx-auto px-6 py-8 space-y-8">

        <!-- Executive Metrics -->
        <section class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="glass-panel p-4 rounded-xl border-l-4 border-amber-500">
                <p class="text-xs text-slate-400 uppercase font-medium">Fleet Network</p>
                <p class="text-2xl font-bold text-white mt-1">5 Intercity Routes</p>
            </div>
            <div class="glass-panel p-4 rounded-xl border-l-4 border-emerald-500">
                <p class="text-xs text-slate-400 uppercase font-medium">Seats Occupied</p>
                <p class="text-2xl font-bold text-emerald-400 mt-1">{{ total_reserved }} Seats</p>
            </div>
            <div class="glass-panel p-4 rounded-xl border-l-4 border-blue-500">
                <p class="text-xs text-slate-400 uppercase font-medium">Active Bookings</p>
                <p class="text-2xl font-bold text-blue-400 mt-1">{{ confirmed_count }} Confirmed</p>
            </div>
            <div class="glass-panel p-4 rounded-xl border-l-4 border-amber-400">
                <p class="text-xs text-slate-400 uppercase font-medium">Total Revenue</p>
                <p class="text-2xl font-bold text-amber-300 mt-1">Rs. {{ "{:,}".format(total_revenue) }}</p>
            </div>
        </section>

        {% if alert_message %}
        <div class="p-4 rounded-xl text-sm font-semibold border {{ alert_color }}">
            {{ alert_message }}
        </div>
        {% endif %}

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

            <!-- Real-World Booking Console with Interactive Seat Map -->
            <section class="lg:col-span-5 glass-panel p-6 rounded-2xl shadow-xl space-y-6">
                <div>
                    <span class="text-xs font-bold text-amber-400 uppercase tracking-widest">Real-Time Booking</span>
                    <h2 class="text-xl font-bold font-luxury text-white">Passenger & Seat Console</h2>
                    <p class="text-xs text-slate-400 mt-1">Pick specific seats directly on the bus blueprint below.</p>
                </div>

                <form method="POST" action="" id="bookingForm" class="space-y-4">
                    <input type="hidden" name="action_type" value="book">
                    <input type="hidden" name="selected_seats" id="selectedSeatsInput" value="">

                    <!-- Passenger Details -->
                    <div class="space-y-3">
                        <div class="border border-slate-700 rounded-xl p-2.5 bg-slate-900/60">
                            <label class="block text-[11px] font-semibold text-slate-400 uppercase">Passenger Full Name</label>
                            <input type="text" name="name" placeholder="e.g. Daniyal Khan" required
                                   class="w-full bg-transparent text-white text-sm focus:outline-none">
                        </div>

                        <div class="grid grid-cols-2 gap-3">
                            <div class="border border-slate-700 rounded-xl p-2.5 bg-slate-900/60">
                                <label class="block text-[11px] font-semibold text-slate-400 uppercase">Mobile Number</label>
                                <input type="tel" name="phone" placeholder="0300-1234567" required
                                       class="w-full bg-transparent text-white text-sm focus:outline-none">
                            </div>
                            <div class="border border-slate-700 rounded-xl p-2.5 bg-slate-900/60">
                                <label class="block text-[11px] font-semibold text-slate-400 uppercase">Age</label>
                                <input type="number" name="age" min="1" max="110" placeholder="e.g. 28" required
                                       class="w-full bg-transparent text-white text-sm focus:outline-none">
                            </div>
                        </div>

                        <div class="border border-slate-700 rounded-xl p-2.5 bg-slate-900/60">
                            <label class="block text-[11px] font-semibold text-slate-400 uppercase">Select Bus Journey</label>
                            <select name="route_id" id="routeSelect" onchange="renderBusSeats()" class="w-full bg-slate-900 text-white text-sm focus:outline-none cursor-pointer">
                                {% for r in routes %}
                                <option value="{{ r.route_id }}" data-price="{{ r.ticket_price }}" data-occupied='{{ r.occupied_seats | tojson }}'>
                                    {{ r.route_id }} • {{ r.departure_city }} ➔ {{ r.destination_city }} (Rs.{{ r.ticket_price }})
                                </option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>

                    <!-- Bus Seat Map Blueprint -->
                    <div class="border border-white/10 rounded-2xl p-4 bg-slate-950/80">
                        <div class="flex justify-between items-center mb-3 pb-2 border-b border-white/10 text-xs">
                            <span class="font-bold text-slate-300">Front / Driver Cabin 💺</span>
                            <div class="flex items-center space-x-3 text-[11px]">
                                <span class="flex items-center"><span class="w-2.5 h-2.5 rounded bg-slate-700 mr-1 border border-slate-500"></span> Free</span>
                                <span class="flex items-center"><span class="w-2.5 h-2.5 rounded bg-amber-400 mr-1"></span> Chosen</span>
                                <span class="flex items-center"><span class="w-2.5 h-2.5 rounded bg-red-600 mr-1"></span> Booked</span>
                            </div>
                        </div>

                        <!-- 2x2 Seating Grid: 7 rows = 28 seats -->
                        <div id="seatGrid" class="space-y-2 py-2"></div>
                    </div>

                    <!-- Dynamic Fare Summary & Discount Notice -->
                    <div class="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs space-y-1">
                        <div class="flex justify-between text-slate-400">
                            <span>Selected Seats:</span>
                            <span id="selectedSeatsLabel" class="font-bold text-amber-300">None</span>
                        </div>
                        <div class="flex justify-between text-slate-400">
                            <span>Seat Count:</span>
                            <span id="seatCountLabel" class="font-bold text-white">0</span>
                        </div>
                        <div class="flex justify-between text-slate-400" id="discountRow" style="display: none;">
                            <span class="text-emerald-400">VIP Group Discount (10% off):</span>
                            <span id="discountLabel" class="font-bold text-emerald-400">- Rs. 0</span>
                        </div>
                        <div class="flex justify-between text-sm pt-2 border-t border-white/10 font-bold text-white">
                            <span>Final Payable Amount:</span>
                            <span id="totalFareLabel" class="text-amber-400 text-base">Rs. 0</span>
                        </div>
                    </div>

                    <button type="submit" id="bookSubmitBtn" disabled
                            class="w-full py-3.5 px-6 rounded-xl font-bold text-sm tracking-wider uppercase text-black bg-gradient-to-r from-amber-400 via-amber-300 to-amber-500 hover:opacity-95 transition disabled:opacity-30 disabled:cursor-not-allowed shadow-lg shadow-amber-500/20">
                        Confirm & Reserve Seats ➔
                    </button>
                </form>
            </section>

            <!-- Right Column: Routes & Boarding Passes -->
            <section class="lg:col-span-7 space-y-8">
                
                <!-- Routes Schedule with City Filter -->
                <div class="glass-panel p-6 rounded-2xl shadow-xl">
                    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6 border-b border-white/10 pb-4">
                        <div>
                            <span class="text-xs font-bold text-amber-400 uppercase tracking-widest">Intercity Network</span>
                            <h2 class="text-lg font-bold font-luxury text-white">Departures & Availability</h2>
                        </div>

                        <!-- City Filter Pills -->
                        <div class="flex flex-wrap gap-1">
                            {% for c in cities %}
                            <button onclick="filterCity('{{ c }}')" class="city-btn text-[11px] px-2.5 py-1 rounded-full font-medium border border-white/10 hover:border-amber-400 text-slate-300 transition">
                                {{ c }}
                            </button>
                            {% endfor %}
                        </div>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-sm" id="routesTable">
                            <thead>
                                <tr class="text-xs uppercase tracking-wider text-slate-400 border-b border-white/5">
                                    <th class="pb-3">Route</th>
                                    <th class="pb-3">Journey</th>
                                    <th class="pb-3">Departure / Arrival</th>
                                    <th class="pb-3">Fare</th>
                                    <th class="pb-3 text-right">Available</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-white/5">
                                {% for r in routes %}
                                <tr class="route-row hover:bg-white/[0.02] transition" data-dept="{{ r.departure_city }}">
                                    <td class="py-3 font-mono font-bold text-amber-300">{{ r.route_id }}</td>
                                    <td class="py-3 font-medium text-white">
                                        {{ r.departure_city }} ➔ {{ r.destination_city }}
                                        <span class="block text-[10px] text-slate-400">{{ r.class }}</span>
                                    </td>
                                    <td class="py-3 text-xs text-slate-300">
                                        {{ r.departure_time }} <span class="text-slate-500">→</span> {{ r.arrival_time }}
                                    </td>
                                    <td class="py-3 font-bold text-amber-300">Rs. {{ "{:,}".format(r.ticket_price) }}</td>
                                    <td class="py-3 text-right">
                                        <span class="px-2.5 py-0.5 rounded-full text-xs font-bold {% if r.available_seats == 0 %}bg-red-500/10 text-red-400 border border-red-500/20{% else %}bg-emerald-500/10 text-emerald-400 border border-emerald-500/20{% endif %}">
                                            {{ r.available_seats }} / {{ r.total_seats }}
                                        </span>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Confirmed Bookings with Printable E-Ticket Modal -->
                <div class="glass-panel p-6 rounded-2xl shadow-xl">
                    <div class="flex justify-between items-center mb-6 border-b border-white/10 pb-4">
                        <div>
                            <span class="text-xs font-bold text-amber-400 uppercase tracking-widest">Travel Records</span>
                            <h2 class="text-lg font-bold font-luxury text-white">Official Passenger Manifest</h2>
                        </div>
                    </div>

                    {% if not bookings %}
                    <p class="text-slate-400 text-sm py-4 text-center">No passenger reservations placed yet.</p>
                    {% else %}
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-sm">
                            <thead>
                                <tr class="text-xs uppercase tracking-wider text-slate-400 border-b border-white/5">
                                    <th class="pb-3">Ticket ID</th>
                                    <th class="pb-3">Passenger</th>
                                    <th class="pb-3">Seats</th>
                                    <th class="pb-3">Fare</th>
                                    <th class="pb-3">Status</th>
                                    <th class="pb-3 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-white/5">
                                {% for b in bookings %}
                                <tr class="hover:bg-white/[0.02]">
                                    <td class="py-3 font-mono font-bold text-amber-400">{{ b.booking_id }}</td>
                                    <td class="py-3">
                                        <div class="font-medium text-white">{{ b.passenger_name }}</div>
                                        <div class="text-[11px] text-slate-400">{{ b.phone }}</div>
                                    </td>
                                    <td class="py-3">
                                        {% for s in b.seats %}
                                        <span class="inline-block px-1.5 py-0.5 text-[10px] font-bold bg-amber-400/10 text-amber-300 border border-amber-400/20 rounded mr-1 mb-1">{{ s }}</span>
                                        {% endfor %}
                                    </td>
                                    <td class="py-3 font-bold text-slate-200">Rs. {{ "{:,}".format(b.total_fare) }}</td>
                                    <td class="py-3">
                                        <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold {% if b.status == 'Confirmed' %}bg-emerald-500/10 text-emerald-300 border border-emerald-500/20{% else %}bg-red-500/10 text-red-400 border border-red-500/20{% endif %}">
                                            {{ b.status }}
                                        </span>
                                    </td>
                                    <td class="py-3 text-right space-x-2">
                                        <!-- View E-Ticket Button -->
                                        <button onclick='openTicketModal({{ b | tojson }})' class="text-xs text-amber-300 hover:text-amber-200 font-semibold px-2 py-1 rounded bg-amber-500/10 border border-amber-500/20 transition">
                                            Ticket 🖨
                                        </button>

                                        {% if b.status == 'Confirmed' %}
                                        <form method="POST" action="" class="inline">
                                            <input type="hidden" name="action_type" value="cancel">
                                            <input type="hidden" name="booking_id" value="{{ b.booking_id }}">
                                            <button type="submit" class="text-xs text-red-400 hover:text-red-300 px-2 py-1 rounded bg-red-500/5 hover:bg-red-500/15 border border-red-500/20 transition">
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

            </section>
        </div>
    </main>

    <!-- Printable E-Ticket Modal -->
    <div id="ticketModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-slate-900 border border-amber-500/30 rounded-2xl p-6 max-w-md w-full shadow-2xl relative text-slate-100" id="printArea">
            <div class="flex justify-between items-start border-b border-white/10 pb-3 mb-4">
                <div>
                    <h3 class="font-luxury font-bold text-lg text-amber-400">SMART BUS EXECUTIVE</h3>
                    <p class="text-[10px] text-slate-400 uppercase tracking-widest">Official Electronic Boarding Pass</p>
                </div>
                <button onclick="closeTicketModal()" class="text-slate-400 hover:text-white font-bold text-lg leading-none">&times;</button>
            </div>

            <div class="space-y-3 text-sm">
                <div class="flex justify-between">
                    <span class="text-xs text-slate-400 uppercase">Boarding Pass #</span>
                    <span id="mTicketId" class="font-mono font-bold text-amber-300"></span>
                </div>
                <div class="flex justify-between">
                    <span class="text-xs text-slate-400 uppercase">Passenger</span>
                    <span id="mPassenger" class="font-bold text-white"></span>
                </div>
                <div class="flex justify-between">
                    <span class="text-xs text-slate-400 uppercase">Contact Phone</span>
                    <span id="mPhone" class="text-slate-200"></span>
                </div>
                <div class="flex justify-between">
                    <span class="text-xs text-slate-400 uppercase">Journey Route</span>
                    <span id="mRoute" class="font-bold text-amber-200"></span>
                </div>
                <div class="flex justify-between">
                    <span class="text-xs text-slate-400 uppercase">Departure Time</span>
                    <span id="mTime" class="text-slate-200"></span>
                </div>
                <div class="flex justify-between">
                    <span class="text-xs text-slate-400 uppercase">Assigned Seats</span>
                    <span id="mSeats" class="font-bold text-amber-300"></span>
                </div>
                <div class="flex justify-between border-t border-white/10 pt-2 font-bold">
                    <span>Total Fare Paid</span>
                    <span id="mFare" class="text-emerald-400"></span>
                </div>
            </div>

            <!-- Barcode Graphic Simulation -->
            <div class="mt-6 pt-4 border-t border-dashed border-white/15 text-center">
                <div class="h-10 bg-[repeating-linear-gradient(90deg,#fff,#fff_2px,#000_2px,#000_6px)] opacity-60 rounded"></div>
                <p class="text-[10px] text-slate-500 font-mono tracking-widest mt-2 uppercase">Verified Terminal Boarding Pass</p>
            </div>

            <div class="mt-6 flex space-x-3">
                <button onclick="window.print()" class="flex-1 bg-amber-400 hover:bg-amber-300 text-black font-bold py-2 rounded-xl text-xs uppercase tracking-wider transition">
                    Print / Save PDF 🖨
                </button>
                <button onclick="closeTicketModal()" class="px-4 py-2 border border-slate-700 text-slate-300 rounded-xl text-xs hover:bg-white/5">
                    Close
                </button>
            </div>
        </div>
    </div>

    <!-- Frontend Interactive JavaScript -->
    <script>
        const seatRows = 7;
        const seatCols = ['A', 'B', 'C', 'D'];
        let selectedSeats = [];

        function renderBusSeats() {
            const select = document.getElementById('routeSelect');
            const selectedOpt = select.options[select.selectedIndex];
            const occupied = JSON.parse(selectedOpt.getAttribute('data-occupied') || '[]');
            
            selectedSeats = [];
            updateFareCalculations();

            const grid = document.getElementById('seatGrid');
            grid.innerHTML = '';

            for (let r = 1; r <= seatRows; r++) {
                const rowDiv = document.createElement('div');
                rowDiv.className = 'flex justify-between items-center gap-1';

                // Left pair (A, B)
                const leftDiv = document.createElement('div');
                leftDiv.className = 'flex gap-1.5';
                ['A', 'B'].forEach(col => {
                    const seatId = r + col;
                    leftDiv.appendChild(createSeatBtn(seatId, occupied.includes(seatId)));
                });

                // Aisle marker
                const aisle = document.createElement('div');
                aisle.className = 'text-[9px] font-mono text-slate-600 px-1 select-none';
                aisle.innerText = r;

                // Right pair (C, D)
                const rightDiv = document.createElement('div');
                rightDiv.className = 'flex gap-1.5';
                ['C', 'D'].forEach(col => {
                    const seatId = r + col;
                    rightDiv.appendChild(createSeatBtn(seatId, occupied.includes(seatId)));
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
            btn.className = `seat w-9 h-8 rounded-lg border text-xs font-mono font-medium flex items-center justify-center ${
                isOccupied ? 'occupied' : 'available bg-slate-900 border-slate-700 text-slate-300'
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

            // VIP Group Discount (10% if 4 or more seats booked)
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

        function filterCity(city) {
            const rows = document.querySelectorAll('.route-row');
            rows.forEach(r => {
                if (city === 'All' || r.getAttribute('data-dept') === city) {
                    r.style.display = '';
                } else {
                    r.style.display = 'none';
                }
            });
        }

        function openTicketModal(b) {
            document.getElementById('mTicketId').innerText = b.booking_id;
            document.getElementById('mPassenger').innerText = b.passenger_name;
            document.getElementById('mPhone').innerText = b.phone || 'N/A';
            document.getElementById('mRoute').innerText = b.departure;
            document.getElementById('mTime').innerText = b.departure_time;
            document.getElementById('mSeats').innerText = b.seats.join(', ');
            document.getElementById('mFare').innerText = 'Rs. ' + b.total_fare.toLocaleString();
            document.getElementById('ticketModal').classList.remove('hidden');
        }

        function closeTicketModal() {
            document.getElementById('ticketModal').classList.add('hidden');
        }

        // Initialize seat map on load
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

        # Booking Action with Seat Validation
        if action == "book":
            name = request.form.get("name", "").strip()
            phone = request.form.get("phone", "").strip()
            age_raw = request.form.get("age", "0")
            route_id = request.form.get("route_id", "")
            seats_str = request.form.get("selected_seats", "").strip()
            selected_seats_list = [s.strip() for s in seats_str.split(",") if s.strip()]

            route = next((r for r in routes if r["route_id"] == route_id), None)

            if route and selected_seats_list and name and phone and age_raw.isdigit():
                # Verify none of the selected seats are already occupied
                conflict = any(
                    s in route["occupied_seats"] for s in selected_seats_list
                )
                if conflict:
                    alert_message = "✕ Seat Conflict: One or more selected seats were just taken. Please choose other seats."
                    alert_color = "bg-red-950/80 text-red-300 border-red-500/40"
                else:
                    seat_count = len(selected_seats_list)
                    subtotal = route["ticket_price"] * seat_count
                    discount = round(subtotal * 0.10) if seat_count >= 4 else 0
                    final_fare = subtotal - discount

                    booking_id = f"LX-{booking_counter}"
                    booking_counter += 1

                    # Lock seats in route
                    route["occupied_seats"].extend(selected_seats_list)
                    route["available_seats"] -= seat_count

                    bookings.insert(
                        0,
                        {
                            "booking_id": booking_id,
                            "passenger_name": name,
                            "phone": phone,
                            "passenger_age": int(age_raw),
                            "route_id": route_id,
                            "seats": selected_seats_list,
                            "subtotal": subtotal,
                            "discount": discount,
                            "total_fare": final_fare,
                            "status": "Confirmed",
                            "departure": f"{route['departure_city']} ➔ {route['destination_city']}",
                            "departure_time": route["departure_time"],
                        },
                    )
                    alert_message = f"✓ Reservation {booking_id} Confirmed! Seat(s): {', '.join(selected_seats_list)}. Total Fare: Rs. {final_fare:,}"
                    alert_color = (
                        "bg-emerald-950/80 text-emerald-300 border-emerald-500/40"
                    )
            else:
                alert_message = "✕ Incomplete Details: Please select your seats and provide name, phone, and age."
                alert_color = "bg-amber-950/80 text-amber-300 border-amber-500/40"

        # Cancellation Action (Releases specific seats)
        elif action == "cancel":
            b_id = request.form.get("booking_id")
            booking = next((b for b in bookings if b["booking_id"] == b_id), None)
            if booking and booking["status"] == "Confirmed":
                route = next(
                    (r for r in routes if r["route_id"] == booking["route_id"]), None
                )
                if route:
                    # Release seats back to the route map
                    route["occupied_seats"] = [
                        s for s in route["occupied_seats"] if s not in booking["seats"]
                    ]
                    route["available_seats"] = min(
                        route["total_seats"],
                        route["available_seats"] + len(booking["seats"]),
                    )
                booking["status"] = "Cancelled"
                alert_message = f"✓ Pass {b_id} cancelled. Seat(s) {', '.join(booking['seats'])} released back to availability."
                alert_color = "bg-amber-950/80 text-amber-300 border-amber-500/40"

    total_reserved = sum(
        len(b["seats"]) for b in bookings if b["status"] == "Confirmed"
    )
    confirmed_count = sum(1 for b in bookings if b["status"] == "Confirmed")
    total_revenue = sum(b["total_fare"] for b in bookings if b["status"] == "Confirmed")

    return render_template_string(
        HTML_TEMPLATE,
        routes=routes,
        bookings=bookings,
        cities=SUPPORTED_CITIES,
        total_reserved=total_reserved,
        confirmed_count=confirmed_count,
        total_revenue=total_revenue,
        alert_message=alert_message,
        alert_color=alert_color,
    )


if __name__ == "__main__":
    app.run(debug=True)
