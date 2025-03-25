import random
import re
from twitchio.ext import commands

# Twitch Bot Credentials
BOT_NICK = "PraesBot"
TOKEN = "1rztlvhouaytk2yuycxu2ytelmj47f"
CHANNEL = ["barbosaOnline"]


class PraesBot(commands.Bot):
    def __init__(self):
        super().__init__(token=TOKEN, prefix="!", nick=BOT_NICK, initial_channels=CHANNEL)

    async def event_ready(self):
        print(f"Logged in as {self.nick}")
        for channel in self.connected_channels:
            print(f"Connected to: {channel.name}")
            await channel.send("I have arrived.")

    async def event_message(self, message):
        if message.author is None:
            return  # Ignore system messages

        modified_message = praesify_text(message.content)

        # Prevent infinite loops
        if modified_message != message.content:
            await message.channel.send(modified_message)


def praesify_text(text):
    words = text.split()
    modified_words = []

    for word in words:
        if len(word) > 4 and random.random() < 0.3:  # 30% chance to modify
            modified_word = re.sub(r"^\w{1,3}", "praes", word)  # Replace first few letters
            modified_words.append(modified_word)
        else:
            modified_words.append(word)

    return " ".join(modified_words)


# Run the bot
def main():
    """Starts the Twitch bot."""
    bot = PraesBot()
    bot.run()


if __name__ == "__main__":
    main()
