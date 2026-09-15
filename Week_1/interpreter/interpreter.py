# Get the expression to evaluate.
expression = input("Expression: ")

# Format the input.
expression = expression.strip()

# Extract the operands and the operator from the expression.
x, op, y = expression.split(' ')

# Convert operands to float.
x = float(x)
y = float(y)

# Output the result of the expression.
if op == '+':
    print(x + y)
elif op == '-':
    print(x - y)
elif op == '*':
    print(x * y)
elif op == '/':
    print(x / y)
