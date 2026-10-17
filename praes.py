import random
import re

# Three letter words from nltk's English stopword list (the only length we check),
# inlined so the serverless function doesn't need to download nltk data.
STOPWORDS = {
    "ain", "all", "and", "any", "are", "but", "can", "did", "don", "few",
    "for", "had", "has", "her", "him", "his", "how", "i'd", "i'm", "isn",
    "its", "nor", "not", "now", "off", "our", "out", "own", "she", "the",
    "too", "was", "who", "why", "won", "you",
}


def match_case(original, new):
    if original.islower():
        return new.lower()
    elif original.isupper():
        return new.upper()
    elif original.istitle():
        return new.title()

    # If mixed case, match character by character
    matched = ''.join(
        n.upper() if o.isupper() else n.lower()
        for o,n in zip(original, new)
    )

    return matched + new[len(original):]


def is_valid_word(word):
    return word.lower() in STOPWORDS


def tentucky_fried_jicken(word):
    return f"{word[0].upper()}entucky {word[1].upper()}ried {word[2].upper()}icken"


def praesify_word(word):
    modified_word = re.sub(r"^\w{1,3}", "praes", word)  # Replace first few letters
    modified_word = match_case(word, modified_word)
    return modified_word


def praesify_text(text):
    words = text.split()
    modified_words = []

    is_praesify = random.random() < 0.2

    for word in words:
        modified_word = word
        if len(word) == 3 and not is_valid_word(word):
            # Three letter words get Tentucky Fried Jickened
            modified_word = tentucky_fried_jicken(word)
        elif len(word) > 4 and random.random() < 0.2 and is_praesify:
            # 5+ letter words have a 20% chance to be praesified, in 20% of messages
            modified_word = praesify_word(word)

        modified_words.append(modified_word)


    return " ".join(modified_words)
