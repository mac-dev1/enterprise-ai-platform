import json
import os

SESSION_FILE = "data/sessions.json"

# cargar sesiones existentes
def load_sessions():
    if not os.path.exists(SESSION_FILE):
        return {}
    with open(SESSION_FILE, "r") as f:
        return json.load(f)

# guardar sesiones
def save_sessions(sessions):
    os.makedirs("data", exist_ok=True)
    with open(SESSION_FILE, "w") as f:
        json.dump(sessions, f)

sessions = load_sessions()

def get_summary(session_id):
    return sessions.get(session_id, "")

def update_summary(session_id, summary):
    sessions[session_id] = summary
    save_sessions(sessions)