# Get the user's answer.
answer = input(
    "What is the Answer to the Great Question of Life, the Universe, and Everything? "
)

# Format the answer.
ans = answer.strip().lower()

# Check the answer.
match ans:
    case "42" | "forty-two" | "forty two":
        print("Yes")
    case _:
        print("No")
