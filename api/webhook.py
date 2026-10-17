import hashlib
import hmac
import json
import os
import sys
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from praes import praesify_text
from twitch_api import send_chat_message

EVENTSUB_SECRET = os.environ.get("TWITCH_EVENTSUB_SECRET", "").encode()

# Twitch retries deliveries, so remember recent message ids (best effort per warm instance)
_seen_ids = {}


def is_valid_signature(headers, body):
    message = (
        headers.get("Twitch-Eventsub-Message-Id", "")
        + headers.get("Twitch-Eventsub-Message-Timestamp", "")
    ).encode() + body
    expected = "sha256=" + hmac.new(EVENTSUB_SECRET, message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, headers.get("Twitch-Eventsub-Message-Signature", ""))


def is_fresh(headers):
    # e.g. 2023-07-19T14:56:51.634234626Z, nanoseconds are more precision than we need
    timestamp = headers.get("Twitch-Eventsub-Message-Timestamp", "")
    try:
        sent = datetime.strptime(timestamp[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return False
    return abs(time.time() - sent.timestamp()) < 600


def is_duplicate(message_id):
    now = time.time()
    for seen_id, seen_at in list(_seen_ids.items()):
        if now - seen_at > 600:
            del _seen_ids[seen_id]
    if message_id in _seen_ids:
        return True
    _seen_ids[message_id] = now
    return False


def handle_chat_message(payload):
    event = payload["event"]
    bot_id = payload["subscription"]["condition"]["user_id"]

    # Prevent infinite loops
    if event["chatter_user_id"] == bot_id:
        return

    text = event["message"]["text"]
    if text.strip() == "!ping":
        reply = "Pong!"
    else:
        reply = praesify_text(text)
        if reply == text:
            return

    send_chat_message(event["broadcaster_user_id"], bot_id, reply)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))

        if not is_valid_signature(self.headers, body) or not is_fresh(self.headers):
            return self.respond(403)

        payload = json.loads(body)
        message_type = self.headers.get("Twitch-Eventsub-Message-Type")

        if message_type == "webhook_callback_verification":
            return self.respond(200, payload["challenge"])

        if message_type == "revocation":
            print(f"Subscription revoked: {payload['subscription']['status']}")
            return self.respond(204)

        if message_type == "notification" and not is_duplicate(self.headers.get("Twitch-Eventsub-Message-Id")):
            try:
                handle_chat_message(payload)
            except Exception as e:
                # Still ack, otherwise Twitch retries and eventually revokes the subscription
                print(f"Error handling chat message: {e}")

        self.respond(204)

    def respond(self, status, text=None):
        self.send_response(status)
        if text is not None:
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(text.encode())
        else:
            self.end_headers()
