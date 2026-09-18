def main():
    # Get the user input.
    text_to_tweet = input("Input: ")

    # Ignore all vowels.
    characters = []
    for c in text_to_tweet:
        if not is_vowel(c):
            characters.append(c)

    text_formatted = "".join(characters)

    # Output the text to tweet with no vowel.
    print(f"Output: {text_formatted}")


def is_vowel(character):
    vowels = ['a', 'e', 'i', 'o', 'u']

    character = str(character).lower()

    return character in vowels


main()
