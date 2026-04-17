import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

#st.set_page_config(page_title="Enterprise AI Assistant")
# --- Initialize history ---
if "history" not in st.session_state:
    st.session_state.history = []

if "summary" not in st.session_state:
    st.session_state.summary = ""
st.title("🤖 Enterprise AI Assistant")

# --- Upload section ---
st.header("Upload document")

uploaded_file = st.file_uploader(
    "Choose a file (.txt or .pdf)",
    type=["txt", "pdf"]
)

if uploaded_file is not None:
    if st.button("Upload document"):
        files = {
            "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
        }

        response = requests.post(
            f"{API_URL}/upload",
            files=files
        )

        if response.status_code == 200:
            st.success("File uploaded successfully!")
        else:
            st.error("Upload failed.")

# --- INPUT PRIMERO ---
with st.form(key="chat_form", clear_on_submit=True):
    question = st.text_input("Type your message")
    submit = st.form_submit_button("Send")

if submit and question:
    response = requests.post(
        f"{API_URL}/ask",
        json={
            "question": question,
            "summary": st.session_state.summary
        }
    )

    if response.status_code == 200:
        data = response.json()["response"]
        answer = data["answer"]
        st.session_state.summary = data["summary"]

        st.session_state.history.append((question, answer))
    else:
        st.error("Error while querying API")

# --- DESPUÉS MOSTRAR HISTORIAL ---
st.header("Conversation")

for q, a in reversed(st.session_state.history):
    st.markdown(f"**You:** {q}")
    st.markdown(f"**AI:** {a}")
