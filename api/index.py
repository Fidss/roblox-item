from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import json
import traceback
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ==================== KREDENSIAL SUPABASE ====================
SUPABASE_URL = "https://lgnzuhfangjeqbosquaa.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxnbnp1aGZhbmdqZXFib3NxdWFhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODExODY4MzUsImV4cCI6MjA5Njc2MjgzNX0.-9i4JDnFweYUjGCTRJ0-cuhOAXpl97pIDarO3NvSV-s"
# =============================================================

# Headers untuk Supabase REST API
def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

# Log storage untuk debugging
api_logs = []

def add_log(message, type="info"):
    """Tambahkan log dengan timestamp"""
    log_entry = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "message": str(message),
        "type": type
    }
    api_logs.append(log_entry)
    if len(api_logs) > 100:  # Keep last 100 logs
        api_logs.pop(0)
    print(f"[{log_entry['timestamp']}] [{type.upper()}] {message}")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎮 BloxFruit Item Tracker - Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Rajdhani', sans-serif;
            background: #0a0a0f;
            color: #e0e0e0;
            min-height: 100vh;
        }
        
        .bg-grid {
            background-image: 
                linear-gradient(rgba(0, 255, 200, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 200, 0.03) 1px, transparent 1px);
            background-size: 60px 60px;
        }
        
        .glow-cyan {
            text-shadow: 0 0 20px rgba(0, 255, 200, 0.8),
                         0 0 40px rgba(0, 255, 200, 0.4),
                         0 0 80px rgba(0, 255, 200, 0.2);
            font-family: 'Orbitron', sans-serif;
        }
        
        .card {
            background: linear-gradient(145deg, rgba(20,20,40,0.95), rgba(15,15,30,0.95));
            border: 1px solid rgba(0, 255, 200, 0.15);
            backdrop-filter: blur(20px);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            border-color: rgba(0, 255, 200, 0.3);
            box-shadow: 0 0 30px rgba(0, 255, 200, 0.1);
        }
        
        .stat-number {
            font-family: 'Orbitron', monospace;
            font-weight: 900;
            font-size: 2.5em;
            text-shadow: 0 0 20px currentColor;
        }
        
        .pulse-border {
            animation: pulseBorder 2s infinite;
        }
        
        @keyframes pulseBorder {
            0%, 100% { border-color: rgba(0, 255, 200, 0.2); }
            50% { border-color: rgba(0, 255, 200, 0.5); }
        }
        
        .log-entry {
            font-family: 'Courier New', monospace;
            font-size: 0.8em;
            padding: 4px 8px;
            border-left: 3px solid;
            margin: 2px 0;
            background: rgba(0,0,0,0.3);
        }
        
        .log-success { border-color: #00ff88; color: #00ff88; }
        .log-error { border-color: #ff4444; color: #ff4444; }
        .log-info { border-color: #00aaff; color: #00aaff; }
        .log-warning { border-color: #ffaa00; color: #ffaa00; }
        
        .api-response {
            background: #000;
            color: #00ff00;
            padding: 8px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.75em;
            overflow-x: auto;
            max-height: 200px;
            overflow-y: auto;
        }
        
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #0a0a0f;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #00ffcc33;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #00ffcc66;
        }
        
        .live-dot {
            width: 10px;
            height: 10px;
            background: #00ff00;
            border-radius: 50%;
            animation: livePulse 1.5s infinite;
            display: inline-block;
        }
        
        @keyframes livePulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7); }
            50% { box-shadow: 0 0 0 10px rgba(0, 255, 0, 0); }
        }
        
        .tab-btn {
            transition: all 0.3s ease;
            border-bottom: 2px solid transparent;
        }
        
        .tab-btn.active {
            border-bottom-color: #00ffcc;
            color: #00ffcc;
        }
    </style>
</head>
<body class="bg-grid">
    <div class="min-h-screen">
        <!-- Header -->
        <div class="bg-black bg-opacity-50 border-b border-gray-800">
            <div class="max-w-7xl mx-auto px-4 py-4">
                <div class="flex flex-col md:flex-row justify-between items-center">
                    <div class="flex items-center space-x-3 mb-3 md:mb-0">
                        <i class="fas fa-dragon text-4xl text-cyan-400"></i>
                        <div>
                            <h1 class="text-3xl font-bold glow-cyan text-cyan-300">BLOXFRUIT TRACKER</h1>
                            <p class="text-cyan-600 text-xs tracking-widest">REAL-TIME INVENTORY MONITORING</p>
                        </div>
                    </div>
                    <div class="flex items-center space-x-4">
                        <div class="flex items-center space-x-2 px-3 py-1 bg-black bg-opacity-50 rounded border border-cyan-900">
                            <span class="live-dot"></span>
                            <span class="text-green-400 text-sm font-mono">SYSTEM ONLINE</span>
                        </div>
                        <button onclick="resetItems()" class="px-6 py-2 bg-red-900 bg-opacity-50 hover:bg-red-800 border border-red-700 text-red-300 rounded-lg font-bold transition text-sm">
                            <i class="fas fa-skull mr-2"></i>RESET
                        </button>
                        <button onclick="testAddItem()" class="px-6 py-2 bg-blue-900 bg-opacity-50 hover:bg-blue-800 border border-blue-700 text-blue-300 rounded-lg font-bold transition text-sm">
                            <i class="fas fa-flask mr-2"></i>TEST API
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div class="max-w-7xl mx-auto px-4 py-6">
            <!-- Stats Cards -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div class="card rounded-xl p-6 pulse-border">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-gray-400 text-sm">🦈 ELSHARK GRAN MAJA</span>
                        <span class="text-xs text-cyan-700">SHARK</span>
                    </div>
                    <div id="total-elshark" class="stat-number text-green-400">0</div>
                    <div class="text-xs text-gray-500 mt-2">Total collected by all players</div>
                </div>
                
                <div class="card rounded-xl p-6 pulse-border">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-gray-400 text-sm">⚔️ GLADIATOR SHARK</span>
                        <span class="text-xs text-cyan-700">WARRIOR</span>
                    </div>
                    <div id="total-gladiator" class="stat-number text-yellow-400">0</div>
                    <div class="text-xs text-gray-500 mt-2">Total collected by all players</div>
                </div>
                
                <div class="card rounded-xl p-6 pulse-border">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-gray-400 text-sm">💎 ENCHANT STONE</span>
                        <span class="text-xs text-cyan-700">EVOLVED</span>
                    </div>
                    <div id="total-enchant" class="stat-number text-purple-400">0</div>
                    <div class="text-xs text-gray-500 mt-2">Total collected by all players</div>
                </div>
            </div>

            <!-- Tabs -->
            <div class="flex space-x-4 mb-4 border-b border-gray-800">
                <button class="tab-btn active px-4 py-2 text-sm font-bold" onclick="switchTab('players')">
                    <i class="fas fa-users mr-2"></i>PLAYERS
                </button>
                <button class="tab-btn px-4 py-2 text-sm font-bold" onclick="switchTab('logs')">
                    <i class="fas fa-terminal mr-2"></i>API LOGS
                </button>
            </div>

            <!-- Players Table -->
            <div id="tab-players" class="card rounded-xl overflow-hidden">
                <div class="overflow-x-auto">
                    <table class="w-full">
                        <thead class="bg-black bg-opacity-50">
                            <tr class="text-cyan-400 text-xs uppercase tracking-wider">
                                <th class="p-4 text-left">#</th>
                                <th class="p-4 text-left">Username</th>
                                <th class="p-4 text-center">🦈 Elshark</th>
                                <th class="p-4 text-center">⚔️ Gladiator</th>
                                <th class="p-4 text-center">💎 Enchant Stone</th>
                                <th class="p-4 text-center">Total Items</th>
                            </tr>
                        </thead>
                        <tbody id="table-body">
                            <tr>
                                <td colspan="6" class="p-12 text-center text-gray-600">
                                    <i class="fas fa-spinner fa-spin text-4xl mb-3 block"></i>
                                    Loading data...
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- API Logs -->
            <div id="tab-logs" class="card rounded-xl p-4 hidden" style="max-height: 500px; overflow-y: auto;">
                <div id="logs-container" class="space-y-1">
                    <div class="log-entry log-info">Waiting for API activity...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentTab = 'players';
        
        function switchTab(tab) {
            currentTab = tab;
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            document.getElementById('tab-players').classList.toggle('hidden', tab !== 'players');
            document.getElementById('tab-logs').classList.toggle('hidden', tab !== 'logs');
        }
        
        async function loadData() {
            try {
                const res = await fetch('/api/data');
                const data = await res.json();
                
                if (data.error) {
                    console.error('Error:', data.error);
                    return;
                }
                
                const tbody = document.getElementById('table-body');
                let totalElshark = 0, totalGladiator = 0, totalEnchant = 0;
                
                if (!data || data.length === 0) {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="6" class="p-12 text-center text-gray-600">
                                <i class="fas fa-inbox text-4xl mb-3 block"></i>
                                <p class="text-lg">NO PLAYERS YET</p>
                                <p class="text-sm mt-1">Waiting for Roblox script to detect items...</p>
                            </td>
                        </tr>
                    `;
                } else {
                    tbody.innerHTML = data.map((row, index) => {
                        const elshark = row.elshark || 0;
                        const gladiator = row.gladiator || 0;
                        const enchant = row.enchant_stone || 0;
                        const total = elshark + gladiator + enchant;
                        
                        totalElshark += elshark;
                        totalGladiator += gladiator;
                        totalEnchant += enchant;
                        
                        return `
                            <tr class="border-b border-gray-800 hover:bg-white hover:bg-opacity-5 transition">
                                <td class="p-4 text-gray-500">${index + 1}</td>
                                <td class="p-4">
                                    <div class="flex items-center space-x-3">
                                        <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-white text-sm font-bold">
                                            ${row.username.charAt(0).toUpperCase()}
                                        </div>
                                        <span class="font-semibold">${row.username}</span>
                                    </div>
                                </td>
                                <td class="p-4 text-center">
                                    <span class="text-green-400 font-bold text-lg">${elshark}</span>
                                </td>
                                <td class="p-4 text-center">
                                    <span class="text-yellow-400 font-bold text-lg">${gladiator}</span>
                                </td>
                                <td class="p-4 text-center">
                                    <span class="text-purple-400 font-bold text-lg">${enchant}</span>
                                </td>
                                <td class="p-4 text-center">
                                    <span class="text-cyan-400 font-bold">${total}</span>
                                </td>
                            </tr>
                        `;
                    }).join('');
                }
                
                document.getElementById('total-elshark').textContent = totalElshark;
                document.getElementById('total-gladiator').textContent = totalGladiator;
                document.getElementById('total-enchant').textContent = totalEnchant;
                
            } catch (err) {
                console.error("Failed to load data:", err);
                document.getElementById('table-body').innerHTML = `
                    <tr>
                        <td colspan="6" class="p-8 text-center text-red-400">
                            <i class="fas fa-exclamation-triangle text-4xl mb-3 block"></i>
                            Failed to load data
                            <p class="text-sm mt-1">${err.message}</p>
                        </td>
                    </tr>
                `;
            }
        }
        
        async function loadLogs() {
            try {
                const res = await fetch('/api/logs');
                const logs = await res.json();
                const container = document.getElementById('logs-container');
                
                if (!logs || logs.length === 0) {
                    container.innerHTML = '<div class="log-entry log-info">No API activity yet...</div>';
                } else {
                    container.innerHTML = logs.map(log => `
                        <div class="log-entry log-${log.type}">
                            <span class="text-gray-600">[${log.timestamp}]</span> ${log.message}
                        </div>
                    `).join('');
                    
                    // Auto scroll to bottom
                    container.parentElement.scrollTop = container.parentElement.scrollHeight;
                }
            } catch (err) {
                console.error("Failed to load logs:", err);
            }
        }
        
        async function resetItems() {
            if (!confirm('⚠️ ARE YOU SURE?\n\nThis will reset ALL item counts to 0 for ALL players!\n\nThis action cannot be undone.')) return;
            
            try {
                const res = await fetch('/api/reset', { method: 'POST' });
                const result = await res.json();
                
                if (result.status === 'reset_success') {
                    document.body.style.backgroundColor = '#ff000033';
                    setTimeout(() => document.body.style.backgroundColor = '', 300);
                }
                
                loadData();
                loadLogs();
            } catch (err) {
                alert('Failed to reset: ' + err.message);
            }
        }
        
        async function testAddItem() {
            const username = prompt('Enter test username:', 'TestPlayer');
            if (!username) return;
            
            const items = ['elshark', 'gladiator', 'enchant_stone'];
            const selectedItem = prompt('Select item:\n1. elshark\n2. gladiator\n3. enchant_stone', '1');
            
            let item;
            if (selectedItem === '1') item = 'elshark';
            else if (selectedItem === '2') item = 'gladiator';
            else if (selectedItem === '3') item = 'enchant_stone';
            else return;
            
            try {
                const res = await fetch('/api/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, items: [item] })
                });
                
                const result = await res.json();
                alert('API Response:\n' + JSON.stringify(result, null, 2));
                
                loadData();
                loadLogs();
            } catch (err) {
                alert('Test failed: ' + err.message);
            }
        }
        
        // Initial load
        loadData();
        loadLogs();
        
        // Auto refresh
        setInterval(() => {
            loadData();
            if (currentTab === 'logs') loadLogs();
        }, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Endpoint untuk melihat log API"""
    return jsonify(api_logs[-50:])  # Return last 50 logs

@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        add_log("Fetching all inventory data", "info")
        
        # Gunakan URL yang benar untuk Supabase REST API
        url = f"{SUPABASE_URL}/rest/v1/inventory"
        params = {
            'select': '*',
            'order': 'username.asc'
        }
        
        response = requests.get(url, headers=get_headers(), params=params)
        
        add_log(f"Supabase GET Response: Status={response.status_code}", 
                "success" if response.status_code == 200 else "error")
        
        if response.status_code == 200:
            data = response.json()
            add_log(f"Retrieved {len(data)} players", "success")
            return jsonify(data)
        else:
            add_log(f"Supabase Error: {response.text}", "error")
            return jsonify([])
            
    except Exception as e:
        add_log(f"Error fetching data: {str(e)}", "error")
        return jsonify({"error": str(e)}), 500

@app.route('/api/add', methods=['POST'])
def add_item():
    try:
        # Parse request
        raw_data = request.get_data(as_text=True)
        add_log(f"RAW Request Body: {raw_data}", "info")
        
        data = request.get_json(force=True, silent=True)
        
        if not data:
            add_log("ERROR: No JSON data in request", "error")
            return jsonify({
                "status": "error", 
                "message": "No JSON data received",
                "received": raw_data
            }), 400
        
        username = data.get('username', '').strip()
        items = data.get('items', [])
        
        add_log(f"Processing: username={username}, items={items}", "info")
        
        if not username:
            add_log("ERROR: Empty username", "error")
            return jsonify({
                "status": "error",
                "message": "Username is required"
            }), 400
        
        if not items:
            add_log("ERROR: No items provided", "error")
            return jsonify({
                "status": "error",
                "message": "No items specified"
            }), 400
        
        # Filter valid items
        valid_items = ['elshark', 'gladiator', 'enchant_stone']
        items = [item for item in items if item in valid_items]
        
        if not items:
            add_log("ERROR: No valid items after filtering", "error")
            return jsonify({
                "status": "error",
                "message": f"No valid items. Must be one of: {valid_items}"
            }), 400
        
        # Cek existing user
        url = f"{SUPABASE_URL}/rest/v1/inventory"
        params = {'username': f'eq.{username}', 'select': '*'}
        
        response = requests.get(url, headers=get_headers(), params=params)
        add_log(f"Check user '{username}': Status={response.status_code}", "info")
        
        if response.status_code == 200:
            existing_data = response.json()
            
            if existing_data and len(existing_data) > 0:
                # UPDATE existing user
                current = existing_data[0]
                update_data = {}
                
                for item in items:
                    current_value = current.get(item, 0) or 0
                    new_value = current_value + 1
                    update_data[item] = new_value
                    add_log(f"Updating {item}: {current_value} → {new_value}", "success")
                
                # PATCH request
                patch_response = requests.patch(
                    url,
                    headers=get_headers(),
                    json=update_data,
                    params={'username': f'eq.{username}'}
                )
                
                add_log(f"PATCH Response: Status={patch_response.status_code}", 
                       "success" if patch_response.status_code in [200, 204] else "error")
                
                if patch_response.status_code in [200, 204]:
                    result_data = patch_response.json() if patch_response.text else update_data
                    return jsonify({
                        "status": "success",
                        "action": "update",
                        "username": username,
                        "items_added": items,
                        "new_values": update_data,
                        "supabase_response": result_data
                    })
                else:
                    add_log(f"PATCH Error: {patch_response.text}", "error")
                    return jsonify({
                        "status": "error",
                        "message": f"Supabase update failed: {patch_response.text}"
                    }), 500
                    
            else:
                # INSERT new user
                new_row = {
                    'username': username,
                    'elshark': 0,
                    'gladiator': 0,
                    'enchant_stone': 0
                }
                
                for item in items:
                    new_row[item] = 1
                
                add_log(f"Creating new user with: {new_row}", "info")
                
                post_response = requests.post(
                    url,
                    headers=get_headers(),
                    json=new_row
                )
                
                add_log(f"POST Response: Status={post_response.status_code}",
                       "success" if post_response.status_code in [200, 201] else "error")
                
                if post_response.status_code in [200, 201]:
                    return jsonify({
                        "status": "success",
                        "action": "create",
                        "username": username,
                        "items_added": items,
                        "initial_data": new_row,
                        "supabase_response": post_response.json() if post_response.text else {}
                    })
                else:
                    add_log(f"POST Error: {post_response.text}", "error")
                    return jsonify({
                        "status": "error",
                        "message": f"Supabase insert failed: {post_response.text}"
                    }), 500
        else:
            add_log(f"GET Error: {response.text}", "error")
            return jsonify({
                "status": "error",
                "message": f"Failed to check user: {response.text}"
            }), 500
            
    except Exception as e:
        error_detail = traceback.format_exc()
        add_log(f"CRITICAL ERROR: {str(e)}\n{error_detail}", "error")
        return jsonify({
            "status": "error",
            "message": str(e),
            "traceback": error_detail
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset_all():
    try:
        add_log("RESETTING ALL ITEMS TO 0", "warning")
        
        url = f"{SUPABASE_URL}/rest/v1/inventory"
        reset_data = {'elshark': 0, 'gladiator': 0, 'enchant_stone': 0}
        
        response = requests.patch(
            url,
            headers=get_headers(),
            json=reset_data
        )
        
        add_log(f"Reset Response: Status={response.status_code}", 
               "success" if response.status_code in [200, 204] else "error")
        
        return jsonify({
            "status": "reset_success",
            "supabase_status": response.status_code
        })
        
    except Exception as e:
        add_log(f"Reset Error: {str(e)}", "error")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
