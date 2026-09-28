import re


def main():
    print(validate(input("IPv4 Address: ")))


def validate(ip):
    pattern = r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$"

    if matches := re.search(pattern, ip):
        for n in matches.groups():
            # Check there is no leading zero.
            if len(n) > 1 and n.startswith("0"):
                return False

            # Check n is in between 0 and 255 (inclusive).
            if not 0 <= int(n) <= 255:
                return False

        return True

    return False


if __name__ == "__main__":
    main()
