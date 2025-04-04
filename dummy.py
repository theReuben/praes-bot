import random
import re

import nltk
from nltk.corpus import stopwords

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

    out = matched + new[len(original):]

    if not isinstance(out, str):
        print(f"Non-string value encountered in match_case: {out}")
        out = str(out)

    return out

def is_valid_word(word):
    word_list = stopwords.words('english')
    return word.lower() in word_list


def tentucky_fried_jicken(word):
    modified_word =  f"{word[0].upper()}entucky {word[1].upper()}ried {word[2].upper()}icken"
    if not isinstance(modified_word, str):
        print(f"Non-string value encountered in tfj: {modified_word}")
        modified_word = str(modified_word)
    return modified_word


def praesify_word(word):
    modified_word = re.sub(r"^\w{1,3}", "praes", word)  # Replace first few letters
    modified_word = match_case(word, modified_word)
    if not isinstance(modified_word, str):
        print(f"Non-string value encountered in praesify_word: {modified_word} - {word}")
        modified_word = str(modified_word)
    return modified_word


def praesify_text(text):
    words = text.split()
    modified_words = []

    for word in words:
        modified_word = word
        if len(word) == 3 and not is_valid_word(word):
            # Three letter words get Tentucky Fried Jickened
            modified_word = tentucky_fried_jicken(word)
        elif len(word) > 4 :
            # 5+ letter words have a 10% chance to be praesified
            modified_word = praesify_word(word)

        modified_words.append(modified_word)

    print(modified_words)
    return " ".join(modified_words)

if __name__ == '__main__':
    # Download word list if you haven't already
    # nltk.download('stopwords')

    text_in = "Enjoying Tentucky Hried Eicken stream? Want more Barbosa? Then come join us on Tentucky Hried Eicken discord Fentucky Oried Ricken more Fentucky Uried Nicken Aentucky Nried Dicken shenanigans https://discord.gg/VKbarMJuSu"
    praesify_text(text_in)
