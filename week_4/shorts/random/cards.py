import random

cards = ["jack", "queen", "king"]


def main():
    random.seed(1)
    print(random.choices(cards, k=2))


main()
