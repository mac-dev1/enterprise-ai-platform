import json
import os

SESSION_FILE = "data/sessions.json"

# asegurar carpeta
os.makedirs("data", exist_ok=True)


def load_sessions():
    if not os.path.exists(SESSION_FILE):
        return {}
    with open(SESSION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_sessions(sessions):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=2)


# memoria en RAM
sessions = load_sessions()


# 🔹 obtener sesión completa
def get_session(session_id):
    return sessions.get(session_id, {
        "summary": "",
        "history": []
    })


# 🔹 actualizar sesión
def update_session(session_id, summary, question, answer):
    if session_id not in sessions:
        sessions[session_id] = {
            "summary": "",
            "history": []
        }

    sessions[session_id]["summary"] = summary

    # 🔹 solo agregar si hay contenido
    if question is not None and answer is not None:
        sessions[session_id]["history"].append({
            "q": question,
            "a": answer
        })

    save_sessions(sessions)