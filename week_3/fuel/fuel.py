def main():
    while True:
        # Get a fraction formatted as X/Y from the user.
        fraction = input("Fraction: ")

        # Extract parts of the fraction.
        try:
            x, y = fraction.split('/')
        except ValueError:
            continue

        # Convert x and y into integers.
        try:
            x = int(x)
        except ValueError:
            continue

        try:
            y = int(y)
        except ValueError:
            continue

        # Check x is a non-negative integer.
        if x < 0:
            continue

        # Check y is a positive integer.
        if y <= 0:
            continue

        # Check x is not greater than y.
        if x > y:
            continue

        break

    gauge_level = x / y
    gauge_level *= 100

    if gauge_level <= 1:
        print('E')
    elif gauge_level >= 99:
        print('F')
    else:
        print(f"{gauge_level:.0f}%")


main()
