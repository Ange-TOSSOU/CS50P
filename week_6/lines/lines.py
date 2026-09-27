import sys


def main():
    # Check the number of command line argument.
    arguments = sys.argv
    nb_cmd_args = len(arguments)
    if nb_cmd_args == 1:
        sys.exit("Too few command-line arguments")
    elif nb_cmd_args > 2:
        sys.exit("Too many command-line arguments")

    # Check the argument provided is a Python file.
    argument = arguments[1]
    if not argument.endswith(".py"):
        sys.exit("Not a Python file")

    # Check the file exists.
    try:
        file = open(argument)
    except FileNotFoundError:
        sys.exit("File does not exist")

    # Count relevant lines.
    count = 0
    for line in file.readlines():
        if not (line.isspace() or line.strip().startswith("#")):
            count += 1

    # Close the file.
    file.close()

    # Output relevant line.
    print(count)


if __name__ == "__main__":
    main()
