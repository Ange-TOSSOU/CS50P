def main():
    # Get the user input.
    text_to_tweet = input("Input: ")

    # Ignore all vowels.
    text_formatted = shorten(text_to_tweet)

    # Output the text to tweet with no vowel.
    print(f"Output: {text_formatted}")


def shorten(word):
    characters = []
    for c in word:
        if not is_vowel(c):
            characters.append(c)

    return "".join(characters)


def is_vowel(character):
    vowels = ["a", "e", "i", "o", "u"]

    character = str(character).lower()

    return character in vowels


if __name__ == "__main__":
    main()
