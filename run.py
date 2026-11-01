"""
Start Erodha with ONE command:   python run.py

Starts the Django backend (port 8000) and the Streamlit dashboard (port 8501),
opens the browser, and stops both when you press Ctrl+C.
"""
import importlib.util
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = sys.executable
HEALTH = "http://127.0.0.1:8000/api/health/"
UI_URL = "http://localhost:8501"

REQUIRED = {"django": "django", "rest_framework": "djangorestframework", "whitenoise": "whitenoise",
            "streamlit": "streamlit", "yfinance": "yfinance", "scipy": "scipy",
            "plotly": "plotly", "pandas": "pandas", "numpy": "numpy"}


def check_packages():
    missing = [pip for mod, pip in REQUIRED.items() if importlib.util.find_spec(mod) is None]
    if missing:
        sys.exit("Missing packages: " + ", ".join(missing) +
                 "\nFix with:  pip install -r requirements.txt\n"
                 "(make sure your venv is active, or use run.bat)")


def wait_for_backend(timeout=120):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(HEALTH, timeout=3) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(1.5)
    return False


def main():
    check_packages()
    print("Starting Erodha backend on http://127.0.0.1:8000 ...")
    backend = subprocess.Popen([PY, "backend/manage.py", "runserver", "127.0.0.1:8000", "--noreload"], cwd=ROOT)
    ui = None
    try:
        if not wait_for_backend():
            sys.exit("Backend did not start within 2 minutes. Scroll up for the error message.")
        print("Backend is healthy. Starting dashboard ...")
        ui = subprocess.Popen([PY, "-m", "streamlit", "run", "frontend/app.py",
                               "--server.port", "8501", "--server.headless", "true"], cwd=ROOT)
        time.sleep(6)
        webbrowser.open(UI_URL)
        print(f"\nErodha is running:  {UI_URL}\nPress Ctrl+C here to stop everything.\n")
        while backend.poll() is None and ui.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping ...")
    finally:
        for p in (ui, backend):
            if p and p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    p.kill()


if __name__ == "__main__":
    main()
