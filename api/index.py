from flask import Flask, request, jsonify, render_template_string
import requests
import json

app = Flask(__name__)

# ==================== KREDENSIAL SUPABASE ====================
SUPABASE_URL = "https://lgnzuhfangjeqbosquaa.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxnbnp1aGZhbmdqZXFib3NxdWFhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODExODY4MzUsImV4cCI6MjA5Njc2MjgzNX0.-9i4JDnFweYUjGCTRJ0-cuhOAXpl97pIDarO3NvSV-s"
# =============================================================

# Headers untuk request ke Supabase REST API
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
    <title>Dashboard Inventory Item</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white min-h-screen p-8">
    <div class="max-w-4xl mx-auto">
        <div class="flex justify-between items-center mb-8">
            <h1 class="text-3xl font-bold text-blue-400">Inventory Tracker</h1>
            <button onclick="resetItems()" class="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded shadow-lg transition">
                Reset Count
            </button>
        </div>
        
        <div class="bg-gray-800 rounded-lg shadow-xl overflow-hidden">
            <table class="w-full text-left">
                <thead class="bg-gray-700">
                    <tr>
                        <th class="p-4">Username Roblox</th>
                        <th class="p-4 text-center">Elshark Gran Maja</th>
                        <th class="p-4 text-center">Gladiator Shark</th>
                        <th class="p-4 text-center">Evolved Enchant Stone</th>
                    </tr>
                </thead>
                <tbody id="table-body">
                    </tbody>
            </table>
        </div>
    </div>

    <script>
        async function loadData() {
            try {
                const res = await fetch('/api/data');
                const data = await res.json();
                const tbody = document.getElementById('table-body');
                tbody.innerHTML = '';
                
                if(data.error) return;

                data.forEach(row => {
                    tbody.innerHTML += `
                        <tr class="border-b border-gray-700 hover:bg-gray-800 transition">
                            <td class="p-4 font-semibold text-blue-300">\${row.username}</td>
                            <td class="p-4 text-center text-green-400 font-bold">\${row.elshark}</td>
                            <td class="p-4 text-center text-yellow-400 font-bold">\${row.gladiator}</td>
                            <td class="p-4 text-center text-purple-400 font-bold">\${row.enchant_stone}</td>
                        </tr>
                    `;
                });
            } catch (err) {
                console.error("Gagal memuat data:", err);
            }
        }

        async function resetItems() {
            if(confirm("Yakin ingin mereset semua count item menjadi 0?")) {
                await fetch('/api/reset', { method: 'POST' });
                loadData();
            }
        }

        loadData();
        setInterval(loadData, 5000); // Auto refresh setiap 5 detik
    </script>
</body>
</html>
"""

def supabase_get(table, query_params=None):
    """Helper function untuk GET request ke Supabase"""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = query_params or {}
    
    # Tambahkan select jika tidak ada
    if 'select' not in params:
        params['select'] = '*'
    
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json() if response.status_code == 200 else []

def supabase_post(table, data):
    """Helper function untuk POST request ke Supabase"""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    response = requests.post(url, headers=HEADERS, json=data)
    return response

def supabase_patch(table, data, condition):
    """Helper function untuk PATCH (update) request ke Supabase"""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = condition
    headers = HEADERS.copy()
    headers['Prefer'] = 'return=representation'
    
    response = requests.patch(url, headers=headers, json=data, params=params)
    return response

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        # Gunakan query parameter untuk ordering
        data = supabase_get('inventory', {'order': 'username.asc'})
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/add', methods=['POST'])
def add_item():
    try:
        data = request.json
        username = data.get('username')
        items = data.get('items', [])
        
        # Cek apakah username sudah ada
        existing = supabase_get('inventory', {'username': f'eq.{username}'})
        
        if len(existing) > 0:
            current_data = existing[0]
            update_data = {}
            
            # Tambahkan +1 untuk setiap item
            for item in items:
                if item in ['elshark', 'gladiator', 'enchant_stone']:
                    update_data[item] = current_data.get(item, 0) + 1
            
            if update_data:
                # Update existing user
                supabase_patch('inventory', update_data, {'username': f'eq.{username}'})
        else:
            # Insert new user
            new_row = {
                'username': username, 
                'elshark': 0, 
                'gladiator': 0, 
                'enchant_stone': 0
            }
            for item in items:
                if item in new_row:
                    new_row[item] = 1
            
            supabase_post('inventory', new_row)
            
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_all():
    try:
        # Reset semua item menjadi 0
        url = f"{SUPABASE_URL}/rest/v1/inventory"
        headers = HEADERS.copy()
        headers['Prefer'] = 'return=representation'
        
        # Gunakan filter untuk memastikan tidak mereset dummy user
        params = {'username': 'neq.dummy_system_user'}
        
        # Pertama, ambil semua data
        response = requests.patch(
            url,
            headers=headers,
            json={'elshark': 0, 'gladiator': 0, 'enchant_stone': 0},
            params=params
        )
        
        return jsonify({"status": "reset_success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Untuk Vercel, tidak perlu app.run()
# if __name__ == '__main__':
#     app.run(debug=True)
