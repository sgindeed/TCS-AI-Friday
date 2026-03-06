def calculate_deviation(expected, actual):

    if expected == 0:
        return 0

    return abs(expected - actual) / expected