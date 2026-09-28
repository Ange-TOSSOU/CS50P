import re


def main():
    print(parse(input("HTML: ")))


def parse(s):
    pattern = r"<iframe .*src=\"https?://(?:www\.)?youtube\.com/embed/(?P<video_id>\w+)\".*>.*</iframe>"

    if match := re.search(pattern, s):
        video_id = match.group("video_id")
        return f"https://youtu.be/{video_id}"

    return None


if __name__ == "__main__":
    main()
