# pip install pyfiglet
from pyfiglet import Figlet
import sys


def main():
    # Check the command-line validity.
    if not is_valid():
        sys.exit("Invalid usage")

    # Get the user input.
    text = input("Input: ")

    # Setup the figlet formatter.
    f = Figlet()
    if len(sys.argv) == 3:
        f = Figlet(font=sys.argv[2])

    # Output the formatted text.
    print(f.renderText(text))


def is_valid():
    arguments = sys.argv

    # Check the user provide exactly two arguments or none.
    number_of_arguments = len(arguments)
    if not (number_of_arguments == 1 or number_of_arguments == 3):
        return False

    if number_of_arguments == 1:
        return True

    # number_of_arguments == 3
    # Check the first argument provided.
    option = arguments[1]
    if not (option == "-f" or option == "--font"):
        return False

    # Check the second argument provided. Is it a known font ?
    font = arguments[2]
    if not font in Figlet().getFonts():
        return False

    return True


main()
