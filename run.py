import subprocess
import webbrowser
import time

# Start FastAPI backend
backend = subprocess.Popen(
    ["uvicorn", "app.main:app", "--reload"]
)

# Wait for server
time.sleep(3)

# Open frontend
webbrowser.open("http://localhost:8000")

backend.wait()