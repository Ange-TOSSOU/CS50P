def main():
    items = {}

    while True:
        # Get an item from the user.
        try:
            item = input()
        except EOFError:
            break

        item = item.strip().lower()

        # Add the item to the dictionary and keep the occurrence.
        try:
            items[item] += 1
        except KeyError:
            items[item] = 1

    # Sort items alphabetically.
    items = dict(sorted(items.items()))

    # Print the items with their occurrence.
    for item, occurrence in items.items():
        print(f"{occurrence} {item.upper()}")


main()
