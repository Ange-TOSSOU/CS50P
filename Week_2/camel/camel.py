def main():
    # Get the camel case sequence.
    camel_case = input("camelCase: ")

    # Convert the camel case sequence into the snake case.
    snake_case = convert_camel_to_snake(camel_case.strip())

    # Output the snake case sequence.
    print(f"snake_case: {snake_case}")


def convert_camel_to_snake(variable_name):
    characters = []
    for c in variable_name:
        c_str = str(c)
        if c_str.isupper():
            characters.append("_" + c_str.lower())
        else:
            characters.append(c_str)

    return "".join(characters)


main()
