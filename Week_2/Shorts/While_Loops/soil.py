import random

moisture = random.randint(25, 40)


def sample():
    global moisture
    moisture = moisture - random.randint(1, 5)
    return moisture
