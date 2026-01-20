# AGENTS.md - Type Cloud Development Guidelines

PLEASE USE CHINESE TO REPLY

## Project Overview
Type Cloud is a real-time text input relay system enabling mobile-to-PC text transmission.
It has been rewritten from Nuxt.js to a **Python Flask** architecture.

## Technology Stack
- **Backend**: Python Flask + Flask-SocketIO (Eventlet)
- **Frontend**: HTML5 + Alpine.js + Tailwind CSS (CDN)
- **Real-time**: Socket.IO (Eventlet async mode)
- **PC Client**: Python + `python-socketio` + `ydotool`/`wl-copy`
- **Persistence**: File-based JSON (`server/data/messages.json`)
- **Authentication**: JWT (HS256) + bcrypt

## File Structure
```
type-cloud/
├── server/
│   ├── app.py            # Main application (API + WS)
│   ├── templates/        # Jinja2 templates (index.html)
│   ├── static/           # Static assets
│   ├── data/             # JSON storage
│   ├── requirements.txt  # Backend dependencies
│   └── verify_parity.py  # Test script
├── client/
│   └── index.py          # PC Client logic
├── start.sh              # One-click startup script
├── README.md             # User documentation
└── AGENTS.md             # This developer guide
```

## Development Commands

### Environment Setup
The project uses a virtual environment created by `start.sh` or manually.
```bash
# Manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r server/requirements.txt
# Optional: Install dev tools
pip install flake8 black
```

### Running Components
```bash
# Start Server (Backend + Frontend)
# Runs on http://0.0.0.0:3000
python server/app.py

# Start PC Client (Manual)
export SERVER_URL="http://localhost:3000"
export PASTE_METHOD="ctrl+v" # or "ctrl+shift+v"
python client/index.py
```

### Testing
There is a verification script to test the full flow (Login -> Send -> Broadcast).
```bash
# Run parity verification
source venv/bin/activate
python server/verify_parity.py
```

### Linting & Formatting
```bash
# Format code
black .

# Check for linting errors
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

## Code Style Guidelines

### Python (Backend/Client)
- **Formatting**: Follow PEP 8 guidelines. Use `black` for auto-formatting.
- **Imports**: Group standard library, third-party, and local imports.
  ```python
  import os
  import json
  
  from flask import Flask
  from flask_socketio import SocketIO
  ```
- **Type Hinting**: Encouraged for complex functions but not strictly enforced.
- **Error Handling**: Use `try/except` blocks for external operations (subprocess, network). Print errors to stdout/stderr with context.
  ```python
  try:
      subprocess.run([...], check=True)
  except Exception as e:
      print(f"Error: {e}")
  ```

### Frontend (HTML/JS)
- **Framework**: Alpine.js for reactivity (no compile step). Use `x-data`, `x-bind`, `x-on`.
- **Styling**: Tailwind CSS utility classes. Avoid custom CSS unless necessary.
- **SocketIO**: Use the global `io` object from CDN.
- **Auth**: Store JWT in `localStorage`. Send in `Authorization: Bearer <token>` header.
- **Async/Await**: Use `async/await` for API calls (`fetch`) to ensure cleaner code.

### Naming Conventions
- **Files**: `snake_case.py` (e.g., `verify_parity.py`, `app.py`).
- **Variables**: `snake_case` in Python, `camelCase` in JS.
- **API Routes**: `/api/resource/action` (e.g., `/api/auth/login`, `/api/message`).
- **Constants**: `UPPER_CASE` for environment variables and configuration (e.g., `SERVER_URL`, `JWT_SECRET`).

### Protocol
- **REST**: Use JSON bodies for POST requests. Return JSON responses.
  - Success: `200 OK`, `{ ...data }`
  - Error: `4xx/5xx`, `{ "statusMessage": "Error details" }`
- **WebSocket**:
  - `connect`: Client identifies type via query `?type=web|pc`.
  - `message` event: Broadcast content string to PC clients.
  - `disconnect`: Log disconnection.

## Configuration
- Use environment variables for configuration.
- **Defaults**:
  - `PASSWORD`: `123456`
  - `JWT_SECRET`: `default-secret`
  - `SERVER_URL`: `http://localhost:3000`
  - `PASTE_METHOD`: `ctrl+v` (can be `ctrl+shift+v` for terminal)

This document serves as the definitive guide for the Python Flask version of Type Cloud.
