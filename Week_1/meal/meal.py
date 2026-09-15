def main():
    # Get the time from the user.
    time = input("What time is it? ")

    # Output which time is it.
    time_in_hours = convert(time)
    if convert("7:00") <= time_in_hours <= convert("8:00"):
        print("breakfast time")
    elif convert("12:00") <= time_in_hours <= convert("13:00"):
        print("lunch time")
    elif convert("18:00") <= time_in_hours <= convert("19:00"):
        print("dinner time")


def convert(time):
    # Format the time
    time = time.strip().lower()

    # Check the time format used
    add_hours = False
    if time.endswith("a.m."):
        time = time.removesuffix("a.m.").strip()
    elif time.endswith("p.m."):
        add_hours = True
        time = time.removesuffix("p.m.").strip()
    
    # Extract the hour and the minute.
    hour, minute = time.split(':')

    # Convert hour and time in hours.
    hour_in_hours = float(hour)
    if add_hours and hour_in_hours != 12:
        hour_in_hours = hour_in_hours + 12
    
    minute_in_hours = float(minute) / 60

    # Return the time in seconds.
    return hour_in_hours + minute_in_hours


if __name__ == "__main__":
    main()
