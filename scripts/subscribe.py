"""Manage PraesBot's EventSub subscription.

Needs TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET and TWITCH_EVENTSUB_SECRET set (same values as Vercel).

    python scripts/subscribe.py create https://<your-app>.vercel.app/api/webhook
    python scripts/subscribe.py list
    python scripts/subscribe.py delete
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from twitch_api import helix

BOT_LOGIN = "PraesBot"
CHANNEL_LOGIN = "barbosaOnline"


def get_user_id(login):
    users = helix("GET", "users", {"login": login})["data"]
    if not users:
        sys.exit(f"No Twitch user called {login}")
    return users[0]["id"]


def list_subscriptions():
    return helix("GET", "eventsub/subscriptions")["data"]


def create(callback_url):
    response = helix("POST", "eventsub/subscriptions", body={
        "type": "channel.chat.message",
        "version": "1",
        "condition": {
            "broadcaster_user_id": get_user_id(CHANNEL_LOGIN),
            "user_id": get_user_id(BOT_LOGIN),
        },
        "transport": {
            "method": "webhook",
            "callback": callback_url,
            "secret": os.environ["TWITCH_EVENTSUB_SECRET"],
        },
    })
    print(response["data"][0]["status"])


def delete():
    for subscription in list_subscriptions():
        helix("DELETE", "eventsub/subscriptions", {"id": subscription["id"]})
        print(f"Deleted {subscription['type']} -> {subscription['transport'].get('callback')}")


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "list"
    if command == "create":
        create(sys.argv[2])
    elif command == "delete":
        delete()
    else:
        for subscription in list_subscriptions():
            print(subscription["status"], subscription["type"], subscription["transport"].get("callback"))


if __name__ == "__main__":
    main()
