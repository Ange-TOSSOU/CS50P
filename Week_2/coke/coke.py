def main():
    coke_price = 50
    accepted_coins = [25, 10, 5]

    # Prompt the user for coins until we got at least 50 cents.
    while coke_price > 0:
        print(f"Amount due: {coke_price}")
        coin_inserted = int(input("Insert Coin: "))

        # Ignore non-accepted coins.
        if coin_inserted in accepted_coins:
            coke_price -= coin_inserted

    print(f"Change Owed: {abs(coke_price)}")


main()
