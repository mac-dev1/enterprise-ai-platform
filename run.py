import subprocess
import webbrowser
import time

# Start FastAPI backend
backend = subprocess.Popen(
    ["uvicorn", "app.main:app", "--reload"]
)

backend.wait()