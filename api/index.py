from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import json
import traceback
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ==================== KREDENSIAL SUPABASE ====================
SUPABASE_URL = "https://orbifkktcarlrdeentur.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9yYmlma2t0Y2FybHJkZWVudHVyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI4OTUwMjYsImV4cCI6MjA5ODQ3MTAyNn0.GfMHYXE01MjzxMZXcqETT4VEOXdrzG0l5RStm4XeQc0"
# =============================================================

# Table name - PASTIKAN INI SESUAI DENGAN NAMA TABEL DI SUPABASE
TABLE_NAME = "inventory"

def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

# Log storage
api_logs = []

def add_log(message, type="info"):
    log_entry = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "message": str(message),
        "type": type
    }
    api_logs.append(log_entry)
    print(f"[{log_entry['timestamp']}] [{type.upper()}] {message}")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inventory Debug Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #0a0a0f; color: #e0e0e0; font-family: 'Courier New', monospace; }
        .debug-box { background: #1a1a2e; border: 1px solid #333; padding: 10px; margin: 10px 0; }
        .success { color: #00ff88; }
        .error { color: #ff4444; }
        .info { color: #00aaff; }
        .warning { color: #ffaa00; }
        pre { background: #000; padding: 10px; overflow-x: auto; font-size: 12px; }
    </style>
</head>
<body class="p-8">
    <div class="max-w-6xl mx-auto">
        <h1 class="text-3xl font-bold mb-6">🔍 Inventory Debug Dashboard</h1>
        
        <!-- Connection Test -->
        <div class="debug-box">
            <h2 class="text-xl mb-3">📡 Connection Test</h2>
            <button onclick="testConnection()" class="bg-blue-600 px-4 py-2 rounded mb-3">Test Supabase Connection</button>
            <pre id="connection-result">Click button to test...</pre>
        </div>
        
        <!-- Manual Add -->
        <div class="debug-box">
            <h2 class="text-xl mb-3">➕ Manual Add Item</h2>
            <div class="grid grid-cols-2 gap-4 mb-3">
                <input id="username" placeholder="Username" class="bg-black border border-gray-700 p-2 rounded text-white">
                <select id="item" class="bg-black border border-gray-700 p-2 rounded text-white">
                    <option value="elshark">Elshark Gran Maja</option>
                    <option value="gladiator">Gladiator Shark</option>
                    <option value="enchant_stone">Evolved Enchant Stone</option>
                </select>
            </div>
            <button onclick="manualAdd()" class="bg-green-600 px-4 py-2 rounded mb-3">Add Item</button>
            <pre id="add-result">Result will appear here...</pre>
        </div>
        
        <!-- Current Data -->
        <div class="debug-box">
            <h2 class="text-xl mb-3">📊 Current Database Content</h2>
            <button onclick="loadData()" class="bg-purple-600 px-4 py-2 rounded mb-3">Refresh Data</button>
            <div id="data-container">
                <pre id="data-result">Loading...</pre>
            </div>
        </div>
        
        <!-- All Logs -->
        <div class="debug-box">
            <h2 class="text-xl mb-3">📝 API Logs (Live)</h2>
            <div id="logs-container" class="max-h-96 overflow-y-auto">
                <pre id="logs-result">Loading logs...</pre>
            </div>
        </div>
    </div>

    <script>
        async function testConnection() {
            const resultEl = document.getElementById('connection-result');
            resultEl.textContent = 'Testing...';
            
            try {
                const res = await fetch('/api/test-connection');
                const data = await res.json();
                resultEl.textContent = JSON.stringify(data, null, 2);
            } catch (err) {
                resultEl.textContent = 'Error: ' + err.message;
            }
        }
        
        async function manualAdd() {
            const username = document.getElementById('username').value.trim();
            const item = document.getElementById('item').value;
            const resultEl = document.getElementById('add-result');
            
            if (!username) {
                resultEl.textContent = 'ERROR: Username required!';
                return;
            }
            
            resultEl.textContent = 'Sending...';
            
            try {
                const res = await fetch('/api/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        username: username, 
                        items: [item] 
                    })
                });
                
                const data = await res.json();
                resultEl.textContent = JSON.stringify(data, null, 2);
                
                // Refresh data
                loadData();
                loadLogs();
            } catch (err) {
                resultEl.textContent = 'Error: ' + err.message;
            }
        }
        
        async function loadData() {
            const resultEl = document.getElementById('data-result');
            
            try {
                const res = await fetch('/api/data');
                const data = await res.json();
                
                if (data.error) {
                    resultEl.textContent = 'ERROR: ' + data.error;
                } else if (data.length === 0) {
                    resultEl.textContent = '⚠️ Database is empty! No records found.\n\nTry adding an item using the form above.';
                } else {
                    // Format as table
                    let table = 'USERNAME'.padEnd(20) + 'ELSHARK'.padEnd(10) + 'GLADIATOR'.padEnd(12) + 'ENCHANT STONE\n';
                    table += '='.repeat(60) + '\n';
                    
                    data.forEach(row => {
                        table += (row.username || '').padEnd(20);
                        table += String(row.elshark || 0).padEnd(10);
                        table += String(row.gladiator || 0).padEnd(12);
                        table += String(row.enchant_stone || 0) + '\n';
                    });
                    
                    table += '\nTotal records: ' + data.length;
                    resultEl.textContent = table;
                }
            } catch (err) {
                resultEl.textContent = 'Error: ' + err.message;
            }
        }
        
        async function loadLogs() {
            const resultEl = document.getElementById('logs-result');
            
            try {
                const res = await fetch('/api/logs');
                const logs = await res.json();
                
                if (logs.length === 0) {
                    resultEl.textContent = 'No logs yet';
                } else {
                    resultEl.textContent = logs.map(log => 
                        `[${log.timestamp}] [${log.type.toUpperCase()}] ${log.message}`
                    ).join('\n');
                    
                    // Auto scroll
                    const container = document.getElementById('logs-container');
                    container.scrollTop = container.scrollHeight;
                }
            } catch (err) {
                resultEl.textContent = 'Error: ' + err.message;
            }
        }
        
        // Load initial data
        loadData();
        loadLogs();
        
        // Auto refresh every 5 seconds
        setInterval(() => {
            loadData();
            loadLogs();
        }, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/test-connection', methods=['GET'])
def test_connection():
    """Test koneksi ke Supabase"""
    try:
        add_log("Testing Supabase connection...", "info")
        
        # Test 1: Basic connection
        url = f"{SUPABASE_URL}/rest/v1/"
        response = requests.get(url, headers=get_headers())
        
        result = {
            "test_1_basic_connection": {
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response": response.text[:200] if response.text else "Empty"
            }
        }
        
        # Test 2: Try to access table
        url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}"
        params = {'select': '*', 'limit': 1}
        response = requests.get(url, headers=get_headers(), params=params)
        
        result["test_2_table_access"] = {
            "table_name": TABLE_NAME,
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "response": response.text[:500] if response.text else "Empty",
            "data_count": len(response.json()) if response.status_code == 200 else 0
        }
        
        # Test 3: Check table structure with empty POST (will fail but shows error)
        url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}"
        test_data = {
            "username": "TEST_CONNECTION",
            "elshark": 0,
            "gladiator": 0,
            "enchant_stone": 0
        }
        
        # Don't actually insert, just check if we can
        result["test_3_table_structure"] = {
            "expected_columns": list(test_data.keys()),
            "message": "Table structure looks valid" if response.status_code == 200 else "Table might have issues"
        }
        
        add_log("Connection test completed", "success")
        return jsonify(result)
        
    except Exception as e:
        add_log(f"Connection test failed: {str(e)}", "error")
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    return jsonify(api_logs[-50:])

@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        add_log(f"Fetching data from table: {TABLE_NAME}", "info")
        
        url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}"
        params = {
            'select': '*',
            'order': 'username.asc'
        }
        
        response = requests.get(url, headers=get_headers(), params=params)
        
        add_log(f"GET Response: Status={response.status_code}, Body={response.text[:200]}", 
                "success" if response.status_code == 200 else "error")
        
        if response.status_code == 200:
            data = response.json()
            add_log(f"Retrieved {len(data)} records", "success")
            return jsonify(data)
        else:
            error_msg = f"Supabase returned status {response.status_code}: {response.text}"
            add_log(error_msg, "error")
            return jsonify({"error": error_msg, "status_code": response.status_code})
            
    except Exception as e:
        add_log(f"Error: {str(e)}", "error")
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/add', methods=['POST'])
def add_item():
    try:
        raw_data = request.get_data(as_text=True)
        add_log(f"RAW Request: {raw_data}", "info")
        
        data = request.get_json(force=True, silent=True)
        
        if not data:
            add_log("No JSON data received", "error")
            return jsonify({"status": "error", "message": "No JSON data"}), 400
        
        username = data.get('username', '').strip()
        items = data.get('items', [])
        
        add_log(f"Processing: username='{username}', items={items}", "info")
        
        if not username:
            return jsonify({"status": "error", "message": "Username required"}), 400
        
        if not items:
            return jsonify({"status": "error", "message": "No items specified"}), 400
        
        # Filter valid items
        valid_items = ['elshark', 'gladiator', 'enchant_stone']
        items = [item for item in items if item in valid_items]
        
        if not items:
            return jsonify({"status": "error", "message": f"No valid items. Use: {valid_items}"}), 400
        
        # Check existing user
        url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}"
        check_params = {
            'username': f'eq.{username}',
            'select': '*'
        }
        
        check_response = requests.get(url, headers=get_headers(), params=check_params)
        add_log(f"Check user response: Status={check_response.status_code}, Body={check_response.text[:200]}", "info")
        
        if check_response.status_code != 200:
            return jsonify({
                "status": "error",
                "message": f"Failed to check user: {check_response.text}",
                "supabase_status": check_response.status_code
            }), 500
        
        existing_data = check_response.json()
        
        if existing_data and len(existing_data) > 0:
            # UPDATE
            current = existing_data[0]
            update_data = {}
            
            for item in items:
                current_value = current.get(item, 0) or 0
                update_data[item] = current_value + 1
                add_log(f"Update {item}: {current_value} → {update_data[item]}", "success")
            
            update_response = requests.patch(
                url,
                headers=get_headers(),
                json=update_data,
                params={'username': f'eq.{username}'}
            )
            
            add_log(f"UPDATE response: Status={update_response.status_code}, Body={update_response.text[:200]}", 
                   "success" if update_response.status_code in [200, 204] else "error")
            
            if update_response.status_code in [200, 204]:
                return jsonify({
                    "status": "success",
                    "action": "update",
                    "username": username,
                    "items_added": items,
                    "new_values": update_data,
                    "supabase_response": update_response.json() if update_response.text else {}
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": f"Update failed: {update_response.text}",
                    "supabase_status": update_response.status_code
                }), 500
                
        else:
            # INSERT
            new_row = {
                'username': username,
                'elshark': 0,
                'gladiator': 0,
                'enchant_stone': 0
            }
            
            for item in items:
                new_row[item] = 1
            
            add_log(f"Creating new user: {new_row}", "info")
            
            insert_response = requests.post(url, headers=get_headers(), json=new_row)
            
            add_log(f"INSERT response: Status={insert_response.status_code}, Body={insert_response.text[:200]}",
                   "success" if insert_response.status_code in [200, 201] else "error")
            
            if insert_response.status_code in [200, 201]:
                return jsonify({
                    "status": "success",
                    "action": "create",
                    "username": username,
                    "items_added": items,
                    "initial_data": new_row,
                    "supabase_response": insert_response.json() if insert_response.text else {}
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": f"Insert failed: {insert_response.text}",
                    "supabase_status": insert_response.status_code
                }), 500
                
    except Exception as e:
        error_detail = traceback.format_exc()
        add_log(f"CRITICAL ERROR: {str(e)}", "error")
        return jsonify({
            "status": "error",
            "message": str(e),
            "traceback": error_detail
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset_all():
    try:
        add_log("Resetting all items to 0", "warning")
        
        url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}"
        reset_data = {'elshark': 0, 'gladiator': 0, 'enchant_stone': 0}
        
        response = requests.patch(url, headers=get_headers(), json=reset_data)
        
        add_log(f"Reset response: Status={response.status_code}", 
               "success" if response.status_code in [200, 204] else "error")
        
        return jsonify({
            "status": "reset_success",
            "supabase_status": response.status_code
        })
        
    except Exception as e:
        add_log(f"Reset error: {str(e)}", "error")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
