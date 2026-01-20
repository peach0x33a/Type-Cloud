import os
import json
import time
import datetime
from functools import wraps
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import jwt
import bcrypt

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("JWT_SECRET", "default-secret")
app.config["PASSWORD_HASH"] = None  # Lazy load

# Configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MESSAGES_FILE = os.path.join(DATA_DIR, "messages.json")
PASSWORD = os.getenv("PASSWORD", "123456")

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")
CORS(app)

# Ensure data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- Helpers ---


def get_db_messages():
    if not os.path.exists(MESSAGES_FILE):
        return []
    try:
        with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_db_messages(messages):
    with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)


def hash_password_if_needed():
    if app.config["PASSWORD_HASH"] is None:
        # Use bcrypt to hash the env password
        app.config["PASSWORD_HASH"] = bcrypt.hashpw(
            PASSWORD.encode("utf-8"), bcrypt.gensalt()
        )


def check_password(input_password):
    hash_password_if_needed()
    return bcrypt.checkpw(input_password.encode("utf-8"), app.config["PASSWORD_HASH"])


# --- Middleware ---


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"message": "Access token required"}), 401

        try:
            jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        except Exception as e:
            return jsonify({"message": "Invalid token", "error": str(e)}), 403

        return f(*args, **kwargs)

    return decorated


# --- Routes ---


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "password" not in data:
        return jsonify({"statusMessage": "Password required"}), 400

    if check_password(data["password"]):
        token = jwt.encode(
            {
                "authenticated": True,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
            },
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )

        # In Python 3, jwt.encode returns a string (PyJWT 2.x+) or bytes (PyJWT 1.x)
        # Assuming PyJWT 2.x+, it returns string. If bytes, decode.
        if isinstance(token, bytes):
            token = token.decode("utf-8")

        return jsonify({"token": token})

    return jsonify({"statusMessage": "Invalid password"}), 401


@app.route("/api/message", methods=["POST"])
@token_required
def send_message():
    data = request.get_json()
    content = data.get("content")
    client_id = data.get("clientId", "unknown")

    if not content:
        return jsonify({"statusMessage": "Content required"}), 400

    messages = get_db_messages()
    new_message = {
        "id": int(time.time() * 1000),
        "content": content,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "clientId": client_id,
    }
    messages.append(new_message)
    # Keep only last 100 messages (optional optimization)
    if len(messages) > 100:
        messages = messages[-100:]

    save_db_messages(messages)

    # Broadcast to SocketIO clients
    # Note: The original Node app sent a JSON string. We'll send the raw string content to match
    # the PC client expectation: `const text = data.toString()`
    # But wait, the original `ws-server.js` broadcasted the raw message string?
    # Original ws-server.js: `const message = data.toString() ... client.send(message)`
    # Original API: sent `JSON.stringify({ message: content })` to /broadcast
    # And /broadcast did: `const { message } = JSON.parse(body); ... client.send(message)`
    # So the PC client receives just the CONTENT string.

    socketio.emit("message", content)

    return jsonify({"id": new_message["id"]})


@app.route("/api/command", methods=["POST"])
@token_required
def send_command():
    data = request.get_json()
    action = data.get("action")
    if not action:
        return jsonify({"statusMessage": "Action required"}), 400

    print(f"Broadcasting command: {action}")
    socketio.emit("command", action)
    return jsonify({"success": True})


@app.route("/api/history", methods=["GET"])
@token_required
def get_history():
    return jsonify(get_db_messages())


@app.route("/api/clients", methods=["GET"])
@token_required
def get_clients():
    # In a real app we might track detailed client info
    # For now, return a placeholder or track via SocketIO connect/disconnect
    # The original tracked them in memory? Let's check logic.
    # Original ws-server.js tracked connection count implicitly?
    # The `api/clients.get.ts` wasn't read, but `pages/index.vue` calls it.
    # We'll implement a simple in-memory tracker.

    # Convert connected_clients dict to list
    client_list = [
        {"id": k, "lastSeen": v["connected_at"], "type": v.get("type", "unknown")}
        for k, v in connected_clients.items()
        if v.get("type") == "pc"  # Filter: only show PC clients
    ]
    return jsonify(client_list)


# --- SocketIO Events ---

connected_clients = {}


@socketio.on("connect")
def handle_connect():
    # Determine client ID (maybe from query params or random)
    client_id = request.sid
    client_type = request.args.get("type", "unknown")
    connected_clients[client_id] = {
        "connected_at": datetime.datetime.utcnow().isoformat() + "Z",
        "type": client_type,
    }
    print(f"Client connected: {client_id} ({client_type})")


@socketio.on("disconnect")
def handle_disconnect():
    client_id = request.sid
    if client_id in connected_clients:
        del connected_clients[client_id]
    print(f"Client disconnected: {client_id}")


@socketio.on("message")
def handle_websocket_message(data):
    # Handle messages sent directly via WebSocket (if any)
    print(f"Received WebSocket message: {data}")
    # Broadcast to others?
    # Original ws-server.js: broadcasts to all OTHER clients
    emit("message", data, broadcast=True, include_self=False)


@socketio.on("command")
def handle_command(action):
    print(f"Received command: {action}")
    emit("command", action, broadcast=True, include_self=False)


if __name__ == "__main__":
    # Use port 3000 to match the original Nuxt app port for convenience,
    # or 5000 (Flask default). Let's stick to 3000 to be a drop-in replacement if desired,
    # but the instructions say "rewrite", so standard Flask 5000 is fine.
    # However, to avoid conflict if Node is running, I'll use 5000.
    # Wait, the PC client expects ws://localhost:8080 by default.
    # I should run this on 8080 OR update the PC client default.
    # The start.sh ran WS on 8080 and Nuxt on 3000.
    # I will combine them on port 3000 (like Nuxt) or 8080?
    # Let's run on 3000 and update PC client to connect to 3000.
    socketio.run(app, host="0.0.0.0", port=3000, debug=True)
