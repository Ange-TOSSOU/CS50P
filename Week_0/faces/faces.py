# Get the user input
user_input = input("What to say ? ")

# Replace each ":)" by "🙂"
converted_input = user_input.replace(":)", "🙂")
# Replace each ":(" by "🙁"
converted_input = converted_input.replace(":(", "🙁")

print(converted_input)
