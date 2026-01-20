import unittest
import json
import os
import time
from unittest.mock import patch, MagicMock
from app import app, socketio, MESSAGES_FILE


class TypeCloudTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test-secret"
        app.config["PASSWORD_HASH"] = None  # Reset hash
        # Use a temp file for messages
        self.test_db = "test_messages.json"
        app.config["MESSAGES_FILE"] = (
            self.test_db
        )  # This needs app code change to support config override or we patch open

        self.client = app.test_client()
        self.socket_client = socketio.test_client(app)

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    @patch("app.MESSAGES_FILE", "test_messages.json")
    @patch("app.PASSWORD", "123456")
    def test_full_flow(self):
        # 1. Login
        response = self.client.post(
            "/api/auth/login",
            data=json.dumps({"password": "123456"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        token = data.get("token")
        self.assertTrue(token)

        # 2. Send Message
        headers = {"Authorization": f"Bearer {token}"}
        msg_content = "Hello Type Cloud"

        # Connect socket first to capture emit
        self.assertTrue(self.socket_client.is_connected())

        response = self.client.post(
            "/api/message",
            data=json.dumps({"content": msg_content, "clientId": "test"}),
            headers=headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        # Verify SocketIO Emit
        received = self.socket_client.get_received()
        # Look for 'message' event
        message_events = [x for x in received if x["name"] == "message"]
        self.assertTrue(len(message_events) > 0)
        self.assertEqual(message_events[0]["args"][0], msg_content)

        # Verify File Persistence
        with open("test_messages.json", "r") as f:
            saved_msgs = json.load(f)
            self.assertEqual(len(saved_msgs), 1)
            self.assertEqual(saved_msgs[0]["content"], msg_content)

        # 3. Get History
        response = self.client.get("/api/history", headers=headers)
        self.assertEqual(response.status_code, 200)
        history = json.loads(response.data)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["content"], msg_content)

        print(
            "\nSUCCESS: Login -> Send -> SocketIO -> Persist -> History flow verified."
        )


if __name__ == "__main__":
    unittest.main()
