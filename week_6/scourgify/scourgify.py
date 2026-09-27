import csv
import sys


def main():
    # Check the number of command line argument.
    arguments = sys.argv
    nb_cmd_args = len(arguments)
    if nb_cmd_args < 3:
        sys.exit("Too few command-line arguments")
    elif nb_cmd_args > 3:
        sys.exit("Too many command-line arguments")

    # Check the argument provided is a CSV file.
    file_to_read = arguments[1]
    file_to_create = arguments[2]

    # Check the file to read exists.
    try:
        before = open(file_to_read)
    except:
        sys.exit(f"Could not read {file_to_read}")

    # Create and fill the new csv file.
    with open(file_to_create, "w", newline="") as after, before:
        reader = csv.DictReader(before)
        writer = csv.DictWriter(after, fieldnames=["first", "last", "house"])
        writer.writeheader()

        for line in reader:
            names = line["name"].split(",")
            writer.writerow(
                {
                    "first": names[1].strip(),
                    "last": names[0].strip(),
                    "house": line["house"],
                }
            )


if __name__ == "__main__":
    main()
