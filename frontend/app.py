import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Enterprise AI Assistant")

st.title("🤖 Enterprise AI Assistant")

# --- Upload section ---
st.header("Upload document")

uploaded_file = st.file_uploader("Choose a .txt file", type="txt")

if uploaded_file is not None:
    files = {"file": uploaded_file.getvalue()}
    response = requests.post(f"{API_URL}/upload", files={"file": uploaded_file})

    if response.status_code == 200:
        st.success("File uploaded successfully!")
    else:
        st.error("Upload failed.")

# --- Chat section ---
st.header("Ask a question")

question = st.text_input("Enter your question")

if "history" not in st.session_state:
    st.session_state.history = []

if st.button("Ask"):
    if question:
        response = requests.post(
            f"{API_URL}/ask",
            json={"question": question}
        )

        if response.status_code == 200:
            answer = response.json()["answer"]
            st.session_state.history.append((question, answer))

# Mostrar historial
for q, a in st.session_state.history:
    st.markdown(f"**You:** {q}")
    st.markdown(f"**AI:** {a}")