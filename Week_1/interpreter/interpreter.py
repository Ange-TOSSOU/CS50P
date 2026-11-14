# Get the expression to evaluate.
expression = input("Expression: ")

# Format the input.
expression = expression.strip()

# Extract the operands and the operator from the expression.
x, op, y = expression.split(" ")

# Convert operands to int.
x = int(x)
y = int(y)

# Output the result of the expression.
if op == "+":
    print(f"{x + y:.1f}")
elif op == "-":
    print(f"{x - y:.1f}")
elif op == "*":
    print(f"{x * y:.1f}")
elif op == "/":
    print(f"{x / y:.1f}")
