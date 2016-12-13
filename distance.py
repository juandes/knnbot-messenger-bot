import math

def distance(data1, data2):
    points = zip(data1, data2)
    squared_difference = [pow(a - b, 2) for (a, b) in points]
    return math.sqrt(sum(squared_difference))