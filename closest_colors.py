import math

RGB_CODE_DICTIONARY = {
    (255, 69, 0): 2,  # bright red
    (255, 168, 0): 3,  # orange
    (255, 214, 53): 4,  # yellow
    (0, 163, 96): 6,  # darker green
    (126, 237, 86): 8,  # lighter green
    (36, 80, 164): 12,  # darkest blue
    (54, 144, 234): 13,  # medium normal blue
    (81, 233, 244): 14,  # cyan
    (129, 30, 159): 18,  # darkest purple
    (180, 74, 192): 19,  # normal purple
    (255, 153, 170): 23,  # pink
    (156, 105, 38): 25,  # brown
    (0, 0, 0): 27,  # black
    (137, 141, 144): 29,  # grey
    (212, 215, 217): 30,  # light grey
    (255, 255, 255): 31,  # white
}


def find_palette(point):
    def distance(c1, c2):
        (r1, g1, b1) = c1
        (r2, g2, b2) = c2
        return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)

    colors = list(RGB_CODE_DICTIONARY.keys())
    closest_colors = sorted(colors, key=lambda color: distance(color, point))
    closest_color = closest_colors[0]
    code = RGB_CODE_DICTIONARY[closest_color]
    return code
