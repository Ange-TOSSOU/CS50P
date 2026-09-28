import re

locations = {"+1": "United States and Canada", "+62": "Indonesia", "+505": "Nicaragua"}


def main():
    pattern = r"(?P<country_code>\+\d{1,3}) \d{3}-\d{3}-\d{4}"
    number = input("Number: ")

    if match := re.search(pattern, number):
        country_code = match.group("country_code")
        print(locations[country_code])
    else:
        print("Invalid")


main()
