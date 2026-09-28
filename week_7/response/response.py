# pip install validator-collection
from validator_collection import checkers


def main():
    email = input("What's your email address? ")

    if checkers.is_email(email):
        print("Valid")
    else:
        print("Invalid")


main()
