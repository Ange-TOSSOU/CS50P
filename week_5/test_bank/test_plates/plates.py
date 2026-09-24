def main():
    plate = input("Plate: ")
    if is_valid(plate):
        print("Valid")
    else:
        print("Invalid")


def is_valid(s):
    # s must start with at least two letters.
    if not starts_with_two_letters(s):
        return False

    # s must contain a maximum of 6 caharacters (letters or numbers).
    # Note : if s starts with at least two letters, it already contains a minimum of 2 characters.
    if number_of_alphanum_characters(s) > 6:
        return False

    # s must not contain spaces or punctuation marks.
    if contains_white_spaces(s) or contains_punctuation_marks(s):
        return False

    # Numbers cannot be used in the middle of a plate; they must come at the end.
    # The first number used cannot be a zero.
    return no_number_in_the_middle(s)


def starts_with_two_letters(s):
    if len(s) < 2:
        return False

    first_two_characters = s[:2]

    return first_two_characters.isalpha()


def number_of_alphanum_characters(s):
    num = 0
    for c in s:
        if str(c).isalpha() or str(c).isdecimal():
            num += 1

    return num


def contains_punctuation_marks(s):
    punctuation_marks = [
        ".",
        "?",
        "!",
        ",",
        ":",
        ";",
        "'",
        '"',
        "(",
        ")",
        "-",
        "[",
        "]",
        "/",
        "{",
        "}",
    ]

    for pm in punctuation_marks:
        if pm in s:
            return True

    return False


def contains_white_spaces(s):
    for c in s:
        if str(c).isspace():
            return True

    return False


def no_number_in_the_middle(s):
    if contains_no_decimal(s):
        return True

    # Find the index of the first number.
    index = 0
    for c in s:
        if str(c).isdecimal():
            break

        index += 1

    # Check the decimal found is not zero.
    if int(s[index]) == 0:
        return False

    # Check every character after is decimal.
    return s[index:].isdecimal()


def contains_no_decimal(s):
    for c in s:
        if str(c).isdecimal():
            return False

    return True


if __name__ == "__main__":
    main()
