import random

# From: http://stackoverflow.com/questions/27337784/how-do-i-shuffle-a-multidimensional-list-in-python


def shuffle2d(arr2d, rand=random):
    """Shuffes entries of 2-d array arr2d, preserving shape."""
    reshape = []
    data = []
    iend = 0
    for row in arr2d:
        data.extend(row)
        istart, iend = iend, iend+len(row)
        reshape.append((istart, iend))
    rand.shuffle(data)
    return [data[istart:iend] for (istart, iend) in reshape]
