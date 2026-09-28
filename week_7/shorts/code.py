import re


def main():
    code = input("Hexadecimal color code: ").strip()

    pattern = r"^#[a-f\d]{6}$"
    if match := re.search(pattern, code, flags=re.IGNORECASE):
        print(f"Valid. Matched with {match.group()}")
    else:
        print("Invalid.")


main()
