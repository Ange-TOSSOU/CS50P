MENU = {
    "Baja Taco": 4.25,
    "Burrito": 7.50,
    "Bowl": 8.50,
    "Nachos": 11.00,
    "Quesadilla": 8.50,
    "Super Burrito": 8.50,
    "Super Quesadilla": 9.50,
    "Taco": 3.00,
    "Tortilla Salad": 8.00
}


def main():
    total = 0
    while True:
        # Get the item the user want to order.
        try:
            item = input("Item: ")
        except EOFError:
            break

        # Get the price of the item.
        try:
            price = MENU[item.title()]
        except KeyError:
            continue

        # Print the total bill.
        total += price
        print(f"Total: ${total:.2f}")


main()
