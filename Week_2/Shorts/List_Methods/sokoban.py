def main():
    history = []

    while True:
        action = input("Action: ")

        if action == "Undo":
            undone = history.pop()
            print(f"Undone: {undone}")
        elif action == "Restart":
            history.clear()
        else:
            history.append(action)
        
        print(history)


main()
