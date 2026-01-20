#!/bin/bash
export JWT_SECRET="default-secret"
export PASSWORD="123456"

echo "Starting Type Cloud (Flask)..."

# Setup Virtual Environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install Dependencies
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null
else
    echo "Error: requirements.txt not found!"
    exit 1
fi

# Start Flask Server
echo "Starting Server on http://localhost:3000..."
python app.py > server.log 2>&1 &
SERVER_PID=$!
echo "Server started (PID: $SERVER_PID)"

echo "Web Interface: http://localhost:3000"
echo "Press Ctrl+C to stop"

trap "echo 'Stopping...'; kill $SERVER_PID 2>/dev/null; exit" INT

# Wait loop
wait $SERVER_PID
