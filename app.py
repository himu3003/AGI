from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
import json, os

app = Flask(__name__)
CORS(app)

# Path to session JSON files
SESSION_PATH = os.path.join(os.getcwd(), 'demo', 'json')
os.makedirs(SESSION_PATH, exist_ok=True)

# Sample data if none found
SAMPLE_SESSION = {
    "id": "sample_session_1",
    "transcript": "User said 'open Excel' and then 'save report'.",
    "ocr_text": "Excel window showing report data",
    "events": [
        {"time": "00:01", "action": "Opened Excel"},
        {"time": "00:05", "action": "Typed values in cells"},
        {"time": "00:10", "action": "Saved report"}
    ],
    "workflow": ["open_excel", "fill_cells", "save_report"]
}

def load_sessions():
    sessions = []
    for file in os.listdir(SESSION_PATH):
        if file.endswith('.json'):
            with open(os.path.join(SESSION_PATH, file), 'r') as f:
                sessions.append(json.load(f))
    if not sessions:
        sessions.append(SAMPLE_SESSION)
    return sessions

@app.route('/')
def dashboard():
    sessions = load_sessions()
    template = '''
    <!doctype html>
    <html>
    <head>
        <title>AGI Assistant Dashboard</title>
        <style>
            body { background-color: #111; color: #eee; font-family: Arial, sans-serif; margin: 0; padding: 0; }
            .container { width: 90%; margin: auto; padding: 20px; }
            .grid { display: grid; grid-template-columns: 1fr 2fr; gap: 20px; }
            .card { background: #222; padding: 20px; border-radius: 12px; box-shadow: 0 0 10px rgba(0,0,0,0.3); }
            button { background: #4f46e5; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; }
            button:hover { background: #4338ca; }
            ul { list-style: none; padding: 0; }
            li { margin: 6px 0; }
            .green { background: #16a34a; }
            .green:hover { background: #15803d; }
        </style>
        <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    </head>
    <body>
        <div class="container">
            <h1 style="font-size:28px; font-weight:bold; margin-bottom:20px;">AGI Assistant Dashboard</h1>
            <div class="grid">
                <div class="card">
                    <h2>Sessions</h2>
                    <ul>
                        {% for s in sessions %}
                        <li>
                            <button onclick="loadSession('{{ s['id'] }}')" style="width:100%; text-align:left;">{{ s['id'] }}</button>
                        </li>
                        {% endfor %}
                    </ul>
                </div>
                <div class="card">
                    <h2>Session Details</h2>
                    <div id="sessionContent">Select a session to view details.</div>
                </div>
            </div>
        </div>

        <script>
            async function loadSession(id) {
                const res = await axios.get(`/session/${id}`);
                const data = res.data;
                const details = `
                    <p><strong>Transcript:</strong> ${data.transcript}</p>
                    <p><strong>OCR:</strong> ${data.ocr_text}</p>
                    <h3>Events</h3>
                    <ul>${data.events.map(e => `<li>${e.time} - ${e.action}</li>`).join('')}</ul>
                    <h3>Workflow Steps</h3>
                    <ul>${data.workflow.map(step => `<li>${step}</li>`).join('')}</ul>
                    <button class='green' onclick='runAutomation("${data.id}")'>Run Automation</button>
                `;
                document.getElementById('sessionContent').innerHTML = details;
            }

            async function runAutomation(id) {
                if (!confirm('Run automation for ' + id + '?')) return;
                const res = await axios.post(`/run/${id}`);
                alert(res.data.message);
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(template, sessions=sessions)

@app.route('/session/<sid>')
def get_session(sid):
    for s in load_sessions():
        if s['id'] == sid:
            return jsonify(s)
    return jsonify(SAMPLE_SESSION)

@app.route('/run/<sid>', methods=['POST'])
def run_automation(sid):
    return jsonify({"message": f"Automation triggered for session {sid}."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
