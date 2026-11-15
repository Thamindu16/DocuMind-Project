"""Start the DocuMind API and the chat UI with one command: python start.py"""
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def find_chainlit():
    """Locate the chainlit executable inside the active environment."""
    found = shutil.which("chainlit")
    if found:
        return found
    name = "chainlit.exe" if os.name == "nt" else "chainlit"
    return str(Path(sys.executable).parent / name)


def is_free(port):
    """True if this computer lets us listen on the port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def pick_port(start):
    """Return the first usable port at or after start."""
    for port in range(start, start + 30):
        if is_free(port):
            return port
    raise RuntimeError("No free port found")


def api_ready(port):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2) as response:
        return response.status == 200


def port_open(port):
    with socket.create_connection(("localhost", port), timeout=2):
        return True


def wait_for(check, process, name, timeout=90):
    """Wait until check() succeeds, stopping early if the process dies."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if process.poll() is not None:
            print(f"The {name} stopped unexpectedly. Read the messages above.")
            return False
        try:
            if check():
                return True
        except Exception:
            pass
        time.sleep(1)
    print(f"The {name} did not start within {timeout} seconds.")
    return False


def main():
    if not (ROOT / ".env").exists():
        print("Missing .env file. Copy .env.example to .env and add your Groq API key, then run again.")
        sys.exit(1)

    # Build the search index on the first run
    if not (ROOT / "data" / "vectorstore").exists():
        print("Building the document index (first run only)...")
        subprocess.run([sys.executable, "-m", "src.documind.ingestion.indexer"], cwd=ROOT, check=True)

    api_port = pick_port(8000)
    print(f"Starting the API on port {api_port}...")
    api = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.documind.api.main:app", "--port", str(api_port)], cwd=ROOT
    )
    if not wait_for(lambda: api_ready(api_port), api, "API"):
        api.terminate()
        sys.exit(1)

    ui_port = pick_port(api_port + 1)
    print(f"Starting the chat UI on port {ui_port}...")
    env = os.environ.copy()
    env["DOCUMIND_API_URL"] = f"http://127.0.0.1:{api_port}"
    ui = subprocess.Popen(
        [find_chainlit(), "run", "app/chat.py", "--port", str(ui_port), "--headless"], cwd=ROOT, env=env
    )
    if not wait_for(lambda: port_open(ui_port), ui, "chat UI"):
        api.terminate()
        ui.terminate()
        sys.exit(1)

    webbrowser.open(f"http://localhost:{ui_port}")
    print(f"\nDocuMind is running at http://localhost:{ui_port}")
    print(f"API documentation: http://127.0.0.1:{api_port}/docs")
    print("Press Ctrl+C to stop.")

    try:
        while api.poll() is None and ui.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        for process in (api, ui):
            process.terminate()


if __name__ == "__main__":
    main()