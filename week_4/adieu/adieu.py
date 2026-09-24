def main():
    names = []
    while True:
        # Get a name from the user.
        try:
            name = input("Name: ")
        except EOFError:
            print()
            break

        names.append(name)

    nb_names = len(names)
    if nb_names > 0:
        output = "Adieu, adieu, to "

        # Append the first name.
        output += names[0]

        # Append the next names except the last one.
        if nb_names > 2:
            tmp = [output]
            tmp.extend(names[1 : nb_names - 1])
            output = ", ".join(tmp) + ","

        # Append the last name.
        if nb_names > 1:
            output += " and " + names[nb_names - 1]

        print(output)


main()
