# praes-bot

Serverless PraesBot: Twitch EventSub (`channel.chat.message`) -> Vercel function (`api/webhook.py`) -> Helix send chat message.

## Setup

1. Vercel env vars: `TWITCH_CLIENT_ID`, `TWITCH_CLIENT_SECRET`, `TWITCH_EVENTSUB_SECRET` (any random 10-100 char string).
2. Deploy, then with the same env vars locally:
   `python scripts/subscribe.py create https://<app>.vercel.app/api/webhook`
3. `python scripts/subscribe.py list` should show `enabled`.

PraesBot must have authorised the client ID with `user:read:chat`, `user:write:chat`, `user:bot`, and be a mod (or the broadcaster grants `channel:bot`).
