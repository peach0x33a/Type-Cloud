#!/bin/bash

# Configuration
# Change this to your server's public IP or domain
SERVER_URL="${SERVER_URL:-http://localhost:3000}"
export SERVER_URL

echo "--- Type Cloud Client Launcher ---"

# 1. Start ydotoold if not running
if ! pgrep -x "ydotoold" > /dev/null; then
    echo "ydotoold is not running. Attempting to start..."
    
    # Try starting ydotoold
    # Note: On some systems, ydotoold needs to be run as root
    # or the user needs to be in the 'input' group.
    sudo ydotoold --background
    
    # Give it a second to initialize the socket
    sleep 1
    
    if pgrep -x "ydotoold" > /dev/null; then
        echo "✅ ydotoold started successfully."
    else
        echo "❌ Failed to start ydotoold. Please start it manually."
        exit 1
    fi
else
    echo "✅ ydotoold is already running."
fi

# 2. Locate and Activate Virtual Environment
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/../venv"

if [ -d "$VENV_DIR" ]; then
    echo "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
else
    echo "⚠️  Warning: Virtual environment not found at $VENV_DIR."
    echo "Make sure you have run the root start.sh or install dependencies manually."
fi

# 3. Run Client
echo "Connecting to $SERVER_URL..."
python "$SCRIPT_DIR/index.py"
