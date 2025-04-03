import random
import re
import boto3
import nltk
import logging
from twitchio.ext import commands
from nltk.corpus import stopwords


# Twitch Bot Credentials
BOT_NICK = "PraesBot"
CHANNEL = ["barbosaOnline"]

# Function to get the TWITCH_OAUTH_TOKEN from AWS SSM
def get_twitch_oauth_token():
    ssm_client = boto3.client('ssm', region_name='eu-west-2')

    # Fetch the parameter from AWS SSM
    try:
        response = ssm_client.get_parameter(Name='TWITCH_OAUTH_TOKEN', WithDecryption=True)
        return response['Parameter']['Value']
    except Exception as e:
        print(f"Error fetching TWITCH_OAUTH_TOKEN from SSM: {e}")
        return None


class PraesBot(commands.Bot):
    def __init__(self, token):
        super().__init__(token=token, prefix="!", nick=BOT_NICK, initial_channels=CHANNEL)

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


def match_case(original, new):
    if original.islower():
        return new.lower()
    elif original.isupper():
        return new.upper()
    elif original.istitle():
        return new.title

    # If mixed case, match character by character
    matched = ''.join(
        n.upper() if o.isupper() else n.lower()
        for o,n in zip(original, new)
    )

    return matched + new[len(original):]


def is_valid_word(word):
    word_list = stopwords.words('english')
    return word.lower() in word_list


def tentucky_fried_jicken(word):
    return f"{word[0].upper()}entucky {word[1].upper()}ried {word[2].upper()}icken"


def praesify_word(word):
    modified_word = re.sub(r"^\w{1,3}", "praes", word)  # Replace first few letters
    modified_word = match_case(word, modified_word)
    return modified_word


def praesify_text(text):
    words = text.split()
    modified_words = []

    is_praesify = random.random() < 0.4

    for word in words:
        modified_word = word
        if len(word) == 3 and not is_valid_word(word):
            # Three letter words get Tentucky Fried Jickened
            modified_word = tentucky_fried_jicken(word)
        elif len(word) > 4 and random.random() < 0.2 and is_praesify:
            # 5+ letter words have a 10% chance to be praesified
            modified_word = praesify_word(word)

        modified_words.append(modified_word)

    logging.info(f"modified words: {modified_words}")
    return " ".join(modified_words)


# Run the bot
def main():
    """Starts the Twitch bot."""
    token = get_twitch_oauth_token()
    if token is None:
        print("Failed to retrieve Twitch OAuth token. Exiting.")
        return

    # Download common words for filtering
    nltk.download('stopwords')

    bot = PraesBot(token)
    bot.run()


if __name__ == "__main__":
    main()
