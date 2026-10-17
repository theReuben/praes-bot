import json
import os
import time
import urllib.parse
import urllib.request

CLIENT_ID = os.environ.get("TWITCH_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("TWITCH_CLIENT_SECRET", "")

# Cached app access token, reused while the function instance stays warm
_token = {"value": None, "expires_at": 0}


def get_app_token():
    if _token["value"] and time.time() < _token["expires_at"] - 60:
        return _token["value"]

    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
    }).encode()
    with urllib.request.urlopen("https://id.twitch.tv/oauth2/token", data=data, timeout=10) as resp:
        body = json.load(resp)

    _token["value"] = body["access_token"]
    _token["expires_at"] = time.time() + body["expires_in"]
    return _token["value"]


def helix(method, path, params=None, body=None):
    url = f"https://api.twitch.tv/helix/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)

    request = urllib.request.Request(url, method=method, headers={
        "Authorization": f"Bearer {get_app_token()}",
        "Client-Id": CLIENT_ID,
        "Content-Type": "application/json",
    })
    data = json.dumps(body).encode() if body is not None else None

    with urllib.request.urlopen(request, data=data, timeout=10) as resp:
        raw = resp.read()
    return json.loads(raw) if raw else None


def send_chat_message(broadcaster_id, sender_id, message):
    return helix("POST", "chat/messages", body={
        "broadcaster_id": broadcaster_id,
        "sender_id": sender_id,
        "message": message[:500],  # Twitch's chat message limit
    })
