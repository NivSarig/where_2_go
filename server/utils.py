import random
import string


def generate_random_string():
    # Generate a random string of fixed length
    letters = string.ascii_uppercase
    result_str = "".join(random.choice(letters) for i in range(4))
    return result_str
