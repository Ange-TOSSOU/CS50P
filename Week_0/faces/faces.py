def main():
    # Get the user input
    user_input = input("What to say ? ")
    print(convert(user_input))


def convert(input):
    # Replace each ":)" by "🙂"
    converted_input = input.replace(":)", "🙂")
    # Replace each ":(" by "🙁"
    converted_input = converted_input.replace(":(", "🙁")

    return converted_input


main()
