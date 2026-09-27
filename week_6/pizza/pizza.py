import csv
import sys

# pip install tabulate
from tabulate import tabulate


def main():
    # Check the number of command line argument.
    arguments = sys.argv
    nb_cmd_args = len(arguments)
    if nb_cmd_args == 1:
        sys.exit("Too few command-line arguments")
    elif nb_cmd_args > 2:
        sys.exit("Too many command-line arguments")

    # Check the argument provided is a CSV file.
    argument = arguments[1]
    if not argument.endswith(".csv"):
        sys.exit("Not a CSV file")

    # Check the file exists.
    try:
        file = open(argument)
    except FileNotFoundError:
        sys.exit("File does not exist")

    # Get the content of the file as a table.
    reader = csv.DictReader(file)
    table = [line for line in reader]

    # Close the file.
    file.close()

    # Output the table in ASCII Art.
    print(tabulate(table, headers="keys", tablefmt="grid"))


if __name__ == "__main__":
    main()
