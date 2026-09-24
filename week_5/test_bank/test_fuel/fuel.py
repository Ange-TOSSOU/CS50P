def main():
    while True:
        # Get a fraction formatted as X/Y from the user.
        fraction = input("Fraction: ")

        try:
            result = convert(fraction)
        except:
            continue

        print(gauge(result))
        break


def convert(fraction):
    # Extract parts of the fraction.
    x, y = fraction.split("/")

    # Convert x and y into integers.
    x = int(x)
    y = int(y)

    # Check x is a non-negative integer.
    if x < 0:
        raise ValueError()

    # Check y is a positive integer.
    if y < 0:
        raise ValueError()

    if y == 0:
        raise ZeroDivisionError()

    # Check x is not greater than y.
    if x > y:
        raise ValueError()

    gauge_level = (x / y) * 100
    return int(f"{gauge_level:.0f}")


def gauge(percentage):
    if percentage <= 1:
        return "E"
    elif percentage >= 99:
        return "F"
    else:
        return f"{percentage}%"


if __name__ == "__main__":
    main()
