MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]


def main():
    while True:
        # Get a date from the user.
        try:
            date = input("Date: ")
        except EOFError:
            break

        date = date.title()

        # Check which format the user used.
        is_first_format = True
        for m in MONTHS:
            if date.find(m) != -1:
                is_first_format = False
                break

        # Extract parts of the date : day, month and year.
        if is_first_format:
            try:
                month, day, year = date.split('/')
            except ValueError:
                continue

            try:
                month = int(month)
            except ValueError:
                continue
        else:
            if date.count(',') != 1:
                continue
            
            date = date.replace(',', '')
            try:
                month, day, year = date.split(' ')
            except ValueError:
                continue

            try:
                month = MONTHS.index(month.strip().title()) + 1
            except ValueError:
                continue

        # Check the validity of the month.
        if not 1 <= month <= 12:
            continue

        # Check the validity of the day.
        try:
            day = int(day)
        except ValueError:
            continue
        if not 1 <= day <= 31:
            continue

        # Check the validity of the year.
        try:
            year = int(year)
        except ValueError:
            continue
        if not 1 <= year <= 9999:
            continue

        # Output the date using the ISO 8601 format.
        print(f"{year:04d}-{month:02d}-{day:02d}")

        break


main()
