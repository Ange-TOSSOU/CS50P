def main():
    pace = get_pace(miles=26.2, minutes=0)
    print(f"You need to run each mile in {round(pace, 2)} minutes.")


def get_pace(miles, minutes):
    if not minutes > 0:
        raise ValueError("Minutes must be greater than 0.")
    
    return minutes / miles


main()
