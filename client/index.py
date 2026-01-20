import os
import time
import subprocess
import socketio

# Configuration
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:3000")
PASTE_METHOD = os.getenv("PASTE_METHOD", "auto")

sio = socketio.Client()


def check_tools():
    """Verify required tools are installed"""
    tools = ["wl-copy", "ydotool", "xdotool", "kdotool"]
    missing = []
    for tool in tools:
        if subprocess.call(["which", tool], stdout=subprocess.DEVNULL) != 0:
            missing.append(tool)

    if missing:
        print(f"Warning: Missing tools: {', '.join(missing)}")
        if "xdotool" in missing and "kdotool" in missing:
            print("  - xdotool/kdotool: Required for automatic window detection")
        if "wl-copy" in missing or "ydotool" in missing:
            print("  - wl-copy/ydotool: Required for clipboard and pasting")
            if "wl-copy" in missing or "ydotool" in missing:
                exit(1)


def get_active_window_class():
    """Get the active window class name using xdotool or kdotool"""
    try:
        # Try kdotool first (KDE Wayland support)
        if subprocess.call(["which", "kdotool"], stdout=subprocess.DEVNULL) == 0:
            win_id = subprocess.check_output(
                ["kdotool", "getactivewindow"], stderr=subprocess.DEVNULL
            ).strip()
            cls = (
                subprocess.check_output(
                    ["kdotool", "getwindowclassname", win_id], stderr=subprocess.DEVNULL
                )
                .strip()
                .decode("utf-8")
            )
            return cls.lower()

        # Fallback to xdotool
        win_id = subprocess.check_output(
            ["xdotool", "getactivewindow"], stderr=subprocess.DEVNULL
        ).strip()
        cls = (
            subprocess.check_output(
                ["xdotool", "getwindowclassname", win_id], stderr=subprocess.DEVNULL
            )
            .strip()
            .decode("utf-8")
        )
        return cls.lower()
    except Exception:
        return "unknown"


def write_clipboard(text):
    """Write text to clipboard using wl-copy"""
    try:
        p = subprocess.Popen(["wl-copy"], stdin=subprocess.PIPE)
        p.communicate(input=text.encode("utf-8"))
        if p.returncode != 0:
            print("Error writing to clipboard")
    except Exception as e:
        print(f"Clipboard error: {e}")


def is_terminal_active():
    """Check if the active window is a terminal"""
    if PASTE_METHOD == "auto":
        win_class = get_active_window_class()
        print(f"Detected window: {win_class}")
        if any(
            term in win_class
            for term in [
                "konsole",
                "terminal",
                "xterm",
                "kitty",
                "alacritty",
                "gnome-terminal",
            ]
        ):
            return True
    elif PASTE_METHOD == "ctrl+shift+v":
        return True
    return False


def simulate_paste():
    """Simulate Paste using ydotool"""
    try:
        use_terminal_paste = is_terminal_active()

        if use_terminal_paste:
            # Terminal Paste: Ctrl(29) + Shift(42) + V(47)
            # Keys down: 29:1 42:1 47:1
            # Keys up: 47:0 42:0 29:0
            keys = ["29:1", "42:1", "47:1", "47:0", "42:0", "29:0"]
            print("Sending Paste (Ctrl+Shift+V)...")
        else:
            # Standard Paste: Ctrl(29) + V(47)
            keys = ["29:1", "47:1", "47:0", "29:0"]
            print("Sending Paste (Ctrl+V)...")

        result = subprocess.run(
            ["ydotool", "key"] + keys,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"ydotool failed: {result.stderr}")
        else:
            print("Paste command sent successfully")
    except Exception as e:
        print(f"Paste simulation error: {e}")


@sio.event
def connect():
    print(f"Connected to Type Cloud server at {SERVER_URL}")


@sio.event
def disconnect():
    print("Disconnected from server")


@sio.event
def message(data):
    print(f"Received message: {data}")
    write_clipboard(data)
    # Short delay to ensure clipboard is updated
    time.sleep(0.1)
    simulate_paste()
    print("Text injected successfully")


@sio.on("command")
def handle_command(action):
    print(f"Received command: {action}")
    try:
        keys = []
        is_term = is_terminal_active()

        if action == "backspace":
            keys = ["14:1", "14:0"]
        elif action == "enter":
            keys = ["28:1", "28:0"]
        elif action == "left":
            keys = ["105:1", "105:0"]
        elif action == "right":
            keys = ["106:1", "106:0"]
        elif action == "clear":
            if is_term:
                # Terminal Clear Line: Ctrl+E (End), Ctrl+U (Clear Start)
                # Ctrl(29) + E(18), Ctrl(29) + U(22)
                # Note: ydotool key 29:1 18:1 18:0 29:0 ...
                # Sequence: Ctrl down, E click, Ctrl up. Ctrl down, U click, Ctrl up.
                keys = [
                    "29:1",
                    "18:1",
                    "18:0",
                    "29:0",  # Ctrl+E
                    "29:1",
                    "22:1",
                    "22:0",
                    "29:0",  # Ctrl+U
                ]
                print("Sending Clear Line (Ctrl+E, Ctrl+U)...")
            else:
                # GUI Clear: Ctrl+A then Backspace
                keys = ["29:1", "30:1", "30:0", "29:0", "14:1", "14:0"]
                print("Sending Clear All (Ctrl+A, Backspace)...")

        if keys:
            subprocess.run(["ydotool", "key"] + keys, check=True)
            print(f"Command '{action}' executed")
    except Exception as e:
        print(f"Command execution error: {e}")


def main():
    print("Type Cloud PC Client (Python)")
    print("Checking tools...")
    check_tools()

    while True:
        try:
            sio.connect(SERVER_URL + "?type=pc")
            sio.wait()
        except socketio.exceptions.ConnectionError:
            print("Connection failed. Retrying in 3 seconds...")
            time.sleep(3)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(3)


if __name__ == "__main__":
    main()
