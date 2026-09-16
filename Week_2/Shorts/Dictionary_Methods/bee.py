WORDS = {"PAIR": 4, "HAIR": 4, "CHAIR": 5, "GRAPHIC": 7}


def main():
    print("Welcome to Spelling Bee!")
    for word, points in WORDS.items():
        print(f"{word} was worth {points} points.")


main()
