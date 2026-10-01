from datetime import date
import re
import sys

# pip install inflect
import inflect


def main():
    # Get the user birthday.
    birthday = input("Date of Birth: ").strip()

    try:
        age_in_words = get_age_in_words(birthday)
    except ValueError:
        sys.exit("Invalid date")
    print(age_in_words)


def get_age_in_words(birthday, today=None):
    # Check birthday format is : YYYY-MM-DD.
    if not is_valid_format(birthday):
        raise ValueError()

    # Extract year, month and date.
    year, month, day = get_parts_of_date(birthday)
    birth = date(year, month, day)

    # Retrieve the age in minutes.
    if today:
        y, m, d = get_parts_of_date(today)
        today = date(y, m, d)
    else:
        today = date.today()

    days_from_birth_to_today = (today - birth).days
    minutes_from_birth_to_today = days_from_birth_to_today * 24 * 60

    # Convert the age in words.
    age_in_words = inflect.engine().number_to_words(minutes_from_birth_to_today)
    # Format the output.
    age_in_words = age_in_words.replace(" and ", " ").capitalize()
    return f"{age_in_words} minutes"


def get_parts_of_date(date):
    year, month, day = date.split("-")
    year = int(year)
    month = int(month)
    day = int(day)

    return year, month, day


def is_valid_format(date):
    pattern = r"^\d{4}-\d{2}-\d{2}$"

    if re.search(pattern, date):
        return True

    return False


if __name__ == "__main__":
    main()
