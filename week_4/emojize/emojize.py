# pip install emojize
import emoji


def main():
    # Get the user input containing (or not) emoji name(s).
    user_input = input("Input: ")

    # Convert all emoji names in their emoji unicode.
    converted_input = emoji.emojize(user_input, language="alias")

    print("Output:", converted_input)


main()
