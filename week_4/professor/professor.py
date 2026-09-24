import random


def main():
    MAX_TRY = 3
    N_QUESTIONS = 10
    score = 0

    # Get the level from the user.
    level = get_level()

    for _ in range(N_QUESTIONS):
        # Generate two non-negative integers.
        x = generate_integer(level)
        y = generate_integer(level)

        # Ask for the answer.
        answer = x + y
        for i in range(MAX_TRY):
            # Get the user answer.
            try:
                user_answer = int(input(f"{x} + {y} = "))
            except ValueError:
                continue

            # Check the user answer.
            if user_answer == answer:
                score += 1
                break
            else:
                print("EEE")

            # Get the answer after 3 failed attempt.
            if i == MAX_TRY - 1:
                print(f"{x} + {y} = {answer}")

    print(f"Score: {score}")


def get_level():
    while True:
        try:
            n = int(input("Level: "))
        except ValueError:
            continue

        if 1 <= n <= 3:
            return n


def generate_integer(level):
    ranges_list = [range(10), range(10, 100), range(100, 1000)]
    return random.choice(ranges_list[level - 1])


if __name__ == "__main__":
    main()
