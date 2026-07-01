from flask import Flask, request, jsonify, render_template_string
from supabase import create_client, Client

app = Flask(__name__)

# ==================== KREDENSIAL SUPABASE ====================
SUPABASE_URL = "https://lgnzuhfangjeqbosquaa.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxnbnp1aGZhbmdqZXFib3NxdWFhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODExODY4MzUsImV4cCI6MjA5Njc2MjgzNX0.-9i4JDnFweYUjGCTRJ0-cuhOAXpl97pIDarO3NvSV-s"
# =============================================================

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        res = supabase.table('inventory').select('*').order('username').execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/add', methods=['POST'])
def add_item():
    try:
        data = request.json
        username = data.get('username')
        items = data.get('items', []) # Menerima list item berupa array

        # Cek apakah username sudah terdaftar
        res = supabase.table('inventory').select('*').eq('username', username).execute()
        
        if len(res.data) > 0:
            current_data = res.data[0]
            update_data = {}
            
            # Tambahkan +1 untuk setiap item yang dikirim di dalam array
            for item in items:
                if item in ['elshark', 'gladiator', 'enchant_stone']:
                    update_data[item] = current_data.get(item, 0) + 1
            
            if update_data:
                supabase.table('inventory').update(update_data).eq('username', username).execute()
        else:
            # Jika user baru, set default 0 dan berikan nilai 1 pada item yang didapat
            new_row = {'username': username, 'elshark': 0, 'gladiator': 0, 'enchant_stone': 0}
            for item in items:
                if item in new_row:
                    new_row[item] = 1
                    
            supabase.table('inventory').insert(new_row).execute()
            
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_all():
    try:
        # Mengubah semua data item menjadi 0
        supabase.table('inventory').update({'elshark': 0, 'gladiator': 0, 'enchant_stone': 0}).neq('username', 'dummy_system_user').execute()
        return jsonify({"status": "reset_success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
