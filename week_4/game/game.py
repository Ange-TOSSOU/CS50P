import random


def main():
    # Ask the user for the game level.
    level = get_positive_integer("Level: ")

    # Generate a random integer.
    number = random.randint(1, level)

    # Ask the user for a guess until the guess is right.
    while True:
        guess = get_positive_integer("Guess: ")

        # Does the user guess it right ?
        if guess < number:
            print("Too small!")
        elif guess > number:
            print("Too large!")
        else:
            print("Just right!")
            break


def get_positive_integer(text):
    while True:
        try:
            n = int(input(text))
        except ValueError:
            continue

        if n > 0:
            return n


main()
