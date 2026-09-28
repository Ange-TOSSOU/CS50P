import re


def main():
    print(count(input("Text: ")))


def count(s):
    # Start: ^um[^\w]
    # Middle: [^\w]um[^\w]
    # End: [^\w]um$
    # Alone ("um"): ^um$
    pattern = r"^um[^\w]|[^\w]um[^\w]|[^\w]um$|^um$"

    if matches := re.findall(pattern, s, flags=re.IGNORECASE):
        return len(matches)

    return 0


if __name__ == "__main__":
    main()
