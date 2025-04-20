def add(x, y):
  return x + y

def subtract(x, y):
  return x - y

def multiply(x, y):
  return x * y

def divide(x, y):
  if y == 0:
    return "Division by zero!"
  return x / y

# Example usage
print(add(5, 3))
print(subtract(10, 4))
print(multiply(7, 2))
print(divide(15, 3))
print(divide(10, 0))