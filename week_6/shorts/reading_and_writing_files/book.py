def main():
    with open("alice.txt", encoding="utf-8") as file:
        contents = file.readlines()

    chapter1 = contents[52:261]
    with open("chapter1.txt", "w", encoding="utf-8") as file:
        file.writelines(chapter1)


main()
