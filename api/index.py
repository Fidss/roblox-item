from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)  # Enable CORS untuk semua routes

# ==================== KREDENSIAL SUPABASE ====================
SUPABASE_URL = "https://lgnzuhfangjeqbosquaa.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxnbnp1aGZhbmdqZXFib3NxdWFhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODExODY4MzUsImV4cCI6MjA5Njc2MjgzNX0.-9i4JDnFweYUjGCTRJ0-cuhOAXpl97pIDarO3NvSV-s"
# =============================================================

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Inventory - BloxFruit</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;500;700&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            font-family: 'Rajdhani', sans-serif;
            min-height: 100vh;
            background-attachment: fixed;
        }
        
        .cyber-grid {
            background-image: 
                linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
            background-size: 50px 50px;
        }
        
        .glow-text {
            text-shadow: 0 0 10px rgba(0, 255, 255, 0.5),
                         0 0 20px rgba(0, 255, 255, 0.3),
                         0 0 40px rgba(0, 255, 255, 0.2);
            font-family: 'Orbitron', sans-serif;
        }
        
        .card-gradient {
            background: linear-gradient(145deg, rgba(20,20,40,0.9), rgba(30,30,60,0.8));
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 255, 255, 0.2);
        }
        
        .stat-card {
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(0, 255, 255, 0.3);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0, 255, 255, 0.1), transparent);
            transition: left 0.5s;
        }
        
        .stat-card:hover::before {
            left: 100%;
        }
        
        .stat-card:hover {
            transform: translateY(-2px);
            border-color: rgba(0, 255, 255, 0.6);
            box-shadow: 0 0 30px rgba(0, 255, 255, 0.2);
        }
        
        .item-icon {
            font-size: 2.5em;
            filter: drop-shadow(0 0 10px rgba(0, 255, 255, 0.5));
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(0, 255, 255, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(0, 255, 255, 0); }
            100% { box-shadow: 0 0 0 0 rgba(0, 255, 255, 0); }
        }
        
        .scan-line {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 2px;
            background: rgba(0, 255, 255, 0.1);
            animation: scan 3s linear infinite;
            pointer-events: none;
        }
        
        @keyframes scan {
            0% { top: -2px; }
            100% { top: 100%; }
        }
        
        .reset-btn {
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            border: 1px solid rgba(255, 107, 107, 0.5);
            transition: all 0.3s ease;
        }
        
        .reset-btn:hover {
            background: linear-gradient(135deg, #ee5a24, #ff6b6b);
            box-shadow: 0 0 20px rgba(255, 107, 107, 0.5);
            transform: scale(1.05);
        }
        
        .refresh-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #00ff00;
            border-radius: 50%;
            animation: blink 1s infinite;
        }
        
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        
        table {
            border-collapse: separate;
            border-spacing: 0 8px;
        }
        
        tbody tr {
            transition: all 0.3s ease;
            background: rgba(20, 20, 40, 0.6);
        }
        
        tbody tr:hover {
            background: rgba(0, 255, 255, 0.1);
            transform: scale(1.01);
        }
        
        .item-count {
            font-family: 'Orbitron', monospace;
            font-weight: 900;
            font-size: 1.3em;
            text-shadow: 0 0 10px currentColor;
        }
    </style>
</head>
<body class="cyber-grid">
    <div class="scan-line"></div>
    
    <div class="max-w-7xl mx-auto px-4 py-8">
        <!-- Header -->
        <div class="flex flex-col md:flex-row justify-between items-center mb-10">
            <div class="flex items-center space-x-4 mb-4 md:mb-0">
                <i class="fas fa-dragon text-5xl text-cyan-400"></i>
                <div>
                    <h1 class="text-5xl font-bold glow-text text-cyan-300">INVENTORY</h1>
                    <p class="text-cyan-400 text-sm tracking-widest font-mono">TRACKER SYSTEM v2.0</p>
                </div>
            </div>
            
            <div class="flex items-center space-x-4">
                <div class="flex items-center space-x-2 bg-black bg-opacity-50 px-4 py-2 rounded-lg border border-cyan-800">
                    <span class="refresh-indicator"></span>
                    <span class="text-cyan-400 text-sm">LIVE</span>
                </div>
                <button onclick="resetItems()" class="reset-btn text-white font-bold py-3 px-6 rounded-lg shadow-lg flex items-center space-x-2">
                    <i class="fas fa-skull"></i>
                    <span>RESET ALL</span>
                </button>
            </div>
        </div>
        
        <!-- Stats Overview -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
            <div class="stat-card p-6 rounded-lg text-center">
                <div class="item-icon mb-3">🦈</div>
                <h3 class="text-cyan-400 text-sm font-bold mb-2">ELSHARK GRAN MAJA</h3>
                <p id="total-elshark" class="text-4xl text-green-400 item-count">0</p>
            </div>
            <div class="stat-card p-6 rounded-lg text-center">
                <div class="item-icon mb-3">⚔️</div>
                <h3 class="text-cyan-400 text-sm font-bold mb-2">GLADIATOR SHARK</h3>
                <p id="total-gladiator" class="text-4xl text-yellow-400 item-count">0</p>
            </div>
            <div class="stat-card p-6 rounded-lg text-center">
                <div class="item-icon mb-3">💎</div>
                <h3 class="text-cyan-400 text-sm font-bold mb-2">EVOLVED ENCHANT STONE</h3>
                <p id="total-enchant" class="text-4xl text-purple-400 item-count">0</p>
            </div>
        </div>
        
        <!-- Player Table -->
        <div class="card-gradient rounded-xl shadow-2xl overflow-hidden">
            <div class="px-6 py-4 border-b border-cyan-900 flex justify-between items-center">
                <h2 class="text-xl font-bold text-cyan-300">
                    <i class="fas fa-users mr-2"></i>PLAYER INVENTORY
                </h2>
                <span id="player-count" class="text-cyan-500 text-sm">0 Players</span>
            </div>
            
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead>
                        <tr class="text-cyan-400 text-sm uppercase tracking-wider">
                            <th class="p-4 text-left">
                                <i class="fas fa-user mr-2"></i>Username
                            </th>
                            <th class="p-4 text-center">
                                <i class="fas fa-fish mr-2"></i>Elshark
                            </th>
                            <th class="p-4 text-center">
                                <i class="fas fa-shield-halved mr-2"></i>Gladiator
                            </th>
                            <th class="p-4 text-center">
                                <i class="fas fa-gem mr-2"></i>Enchant Stone
                            </th>
                        </tr>
                    </thead>
                    <tbody id="table-body">
                        <!-- Data akan dimuat di sini -->
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="text-center mt-8 text-cyan-800 text-xs">
            <p>🔒 SECURE CONNECTION TO SUPABASE DATABASE</p>
            <p class="mt-1">Auto-refresh every 5 seconds | Real-time tracking</p>
        </div>
    </div>

    <script>
        async function loadData() {
            try {
                const res = await fetch('/api/data');
                const data = await res.json();
                const tbody = document.getElementById('table-body');
                
                if (data.error) {
                    console.error('Error:', data.error);
                    return;
                }
                
                // Hitung total
                let totalElshark = 0;
                let totalGladiator = 0;
                let totalEnchant = 0;
                
                tbody.innerHTML = '';
                
                if (data.length === 0) {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="4" class="p-8 text-center text-cyan-600">
                                <i class="fas fa-inbox text-4xl mb-3 block"></i>
                                <p class="text-lg">No data available</p>
                                <p class="text-sm mt-1">Waiting for players to collect items...</p>
                            </td>
                        </tr>
                    `;
                } else {
                    data.forEach(row => {
                        const elshark = row.elshark || 0;
                        const gladiator = row.gladiator || 0;
                        const enchant = row.enchant_stone || 0;
                        
                        totalElshark += elshark;
                        totalGladiator += gladiator;
                        totalEnchant += enchant;
                        
                        tbody.innerHTML += `
                            <tr class="border-b border-cyan-900">
                                <td class="p-4">
                                    <div class="flex items-center space-x-3">
                                        <div class="w-8 h-8 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 flex items-center justify-center text-white text-sm font-bold">
                                            ${row.username.charAt(0).toUpperCase()}
                                        </div>
                                        <span class="font-semibold text-cyan-200">${row.username}</span>
                                    </div>
                                </td>
                                <td class="p-4 text-center">
                                    <span class="text-green-400 item-count">${elshark}</span>
                                </td>
                                <td class="p-4 text-center">
                                    <span class="text-yellow-400 item-count">${gladiator}</span>
                                </td>
                                <td class="p-4 text-center">
                                    <span class="text-purple-400 item-count">${enchant}</span>
                                </td>
                            </tr>
                        `;
                    });
                }
                
                // Update totals
                document.getElementById('total-elshark').textContent = totalElshark;
                document.getElementById('total-gladiator').textContent = totalGladiator;
                document.getElementById('total-enchant').textContent = totalEnchant;
                document.getElementById('player-count').textContent = `${data.length} Players`;
                
            } catch (err) {
                console.error("Failed to load data:", err);
            }
        }

        async function resetItems() {
            if (confirm("⚠️ ARE YOU SURE?\nThis will reset ALL item counts to 0!")) {
                try {
                    const res = await fetch('/api/reset', { method: 'POST' });
                    const result = await res.json();
                    
                    if (result.status === 'reset_success') {
                        // Tampilkan efek flash
                        document.body.style.transition = 'all 0.3s';
                        document.body.style.backgroundColor = '#ff000020';
                        setTimeout(() => {
                            document.body.style.backgroundColor = '';
                        }, 300);
                    }
                    
                    loadData();
                } catch (err) {
                    console.error("Reset failed:", err);
                    alert("Failed to reset items!");
                }
            }
        }

        // Load data immediately and then every 5 seconds
        loadData();
        setInterval(loadData, 5000);
    </script>
</body>
</html>
"""

def supabase_request(method, endpoint, data=None, params=None):
    """Helper function untuk request ke Supabase REST API"""
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=HEADERS, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=HEADERS, json=data)
        elif method == 'PATCH':
            response = requests.patch(url, headers=HEADERS, json=data, params=params)
        else:
            return None
        
        # Debug print
        print(f"Supabase {method} Response Status: {response.status_code}")
        print(f"Response Body: {response.text[:200]}")
        
        if response.status_code in [200, 201, 204]:
            return response.json() if response.text else {"status": "success"}
        else:
            print(f"Error from Supabase: {response.text}")
            return None
            
    except Exception as e:
        print(f"Exception in supabase_request: {str(e)}")
        return None

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        data = supabase_request('GET', 'inventory', params={'order': 'username.asc'})
        if data is None:
            return jsonify([])
        return jsonify(data)
    except Exception as e:
        print(f"Error in get_data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/add', methods=['POST'])
def add_item():
    try:
        # Debug: print request data
        print("=== RECEIVED ADD REQUEST ===")
        print(f"Headers: {dict(request.headers)}")
        print(f"Raw Data: {request.get_data()}")
        
        data = request.get_json(force=True, silent=True)
        if not data:
            print("ERROR: No JSON data received")
            return jsonify({"status": "error", "message": "No JSON data"}), 400
        
        username = data.get('username', '').strip()
        items = data.get('items', [])
        
        print(f"Username: {username}")
        print(f"Items: {items}")
        
        if not username:
            print("ERROR: Username is empty")
            return jsonify({"status": "error", "message": "Username required"}), 400
        
        if not items:
            print("ERROR: No items provided")
            return jsonify({"status": "error", "message": "No items provided"}), 400
        
        # Cek existing user
        existing = supabase_request('GET', 'inventory', params={'username': f'eq.{username}'})
        print(f"Existing user data: {existing}")
        
        if existing and len(existing) > 0:
            # User exists, update
            current_data = existing[0]
            update_data = {}
            
            for item in items:
                if item in ['elshark', 'gladiator', 'enchant_stone']:
                    current_value = current_data.get(item, 0) or 0
                    update_data[item] = current_value + 1
                    print(f"Updating {item}: {current_value} -> {update_data[item]}")
            
            if update_data:
                result = supabase_request('PATCH', 'inventory', 
                                        data=update_data, 
                                        params={'username': f'eq.{username}'})
                print(f"Update result: {result}")
                
        else:
            # New user
            new_row = {
                'username': username,
                'elshark': 0,
                'gladiator': 0,
                'enchant_stone': 0
            }
            
            for item in items:
                if item in new_row:
                    new_row[item] = 1
                    print(f"Setting initial {item} = 1 for new user")
            
            result = supabase_request('POST', 'inventory', data=new_row)
            print(f"Insert result: {result}")
        
        return jsonify({"status": "success", "message": f"Added {items} for {username}"})
        
    except Exception as e:
        print(f"CRITICAL ERROR in add_item: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_all():
    try:
        print("=== RESET ALL ITEMS ===")
        result = supabase_request('PATCH', 'inventory',
                                data={'elshark': 0, 'gladiator': 0, 'enchant_stone': 0},
                                params={'username': 'neq.dummy_system_user'})
        
        print(f"Reset result: {result}")
        return jsonify({"status": "reset_success"})
    except Exception as e:
        print(f"Error in reset: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Untuk Vercel deployment
if __name__ == '__main__':
    app.run(debug=True, port=5000)
