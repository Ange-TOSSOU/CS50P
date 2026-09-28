import re


def main():
    print(convert(input("Hours: ")))


def convert(s):
    pattern = r"^(?P<start_time>\d{1,2}(?:\:\d{1,2})?) (?P<start_period>AM|PM) to (?P<end_time>\d{1,2}(?:\:\d{1,2})?) (?P<end_period>AM|PM)$"

    match = re.search(pattern, s)
    if not match:
        raise ValueError("Not valid 12-hour format.")

    start_time = check_and_get_24_format(
        match.group("start_time"), match.group("start_period")
    )
    end_time = check_and_get_24_format(
        match.group("end_time"), match.group("end_period")
    )

    return f"{start_time} to {end_time}"


def check_and_get_24_format(time, period):
    # Extract parts of the time.
    try:
        time_h, time_m = time.split(":")
    except:
        time_h = time
        time_m = 0

    # Check the values of the hour and the minute.
    time_h = int(time_h)
    time_m = int(time_m)

    if (not 0 <= time_h <= 12) or (not 0 <= time_m <= 59):
        raise ValueError("Not valid 12-hour format.")

    # Convert the hour to the 24-format.
    if period == "PM":
        time_h = 12 + time_h % 12
    else:
        time_h %= 12

    return f"{time_h:02d}:{time_m:02d}"


if __name__ == "__main__":
    main()
