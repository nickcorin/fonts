"""Native lowercase outlines for Interval's compact geometric construction."""

from math import sqrt

from shapely.geometry import box

from font_engine import Glyph, combine, cubic, ellipse, modulated_stroke, oval, poly


def _curve(*segments):
    return [point for segment in segments for point in cubic(*segment)]


def _arch(left, right, weight, top=510, stem_top=510):
    """An upright stem and rounded shoulder with an open bottom counter."""
    horizontal = weight * .92
    shoulder = top + 8
    outer = poly(
        [(left, 0), (left, stem_top), (left + weight, stem_top),
         (left + weight, top - 76)]
        + _curve(
            ((left + weight, top - 76), (left + weight + 40, top - 12),
             ((left + right) / 2 - 28, shoulder),
             ((left + right) / 2 + 15, shoulder)),
            (((left + right) / 2 + 15, shoulder), (right - 20, shoulder),
             (right, top - 102), (right, top - 198)),
        )
        + [(right, 0)]
    )
    inner = poly(
        [(left + weight, -1), (left + weight, top - 214)]
        + _curve(
            ((left + weight, top - 214), (left + weight, top - 96),
             ((left + right) / 2 - 40, shoulder - horizontal),
             ((left + right) / 2 + 15, shoulder - horizontal)),
            (((left + right) / 2 + 15, shoulder - horizontal),
             (right - weight - 35, shoulder - horizontal),
             (right - weight, top - 111), (right - weight, top - 209)),
        )
        + [(right - weight, -1)]
    )
    return outer.difference(inner)


def build_lowercase(stroke_width: float) -> dict[str, Glyph]:
    """Return a complete lowercase alphabet with 510-unit x-height."""
    weight = stroke_width
    horizontal = weight * .92
    letters: dict[str, Glyph] = {}

    def add(character, shape, advance):
        letters[character] = Glyph(shape, advance)

    round_bowl = oval(50, -8, 530, 518, weight)
    add('o', round_bowl, 580)
    add('b', combine(round_bowl, box(50, 0, 50 + weight, 700)), 580)
    add('d', combine(round_bowl, box(530 - weight, 0, 530, 700)), 580)
    add('p', combine(round_bowl, box(50, -200, 50 + weight, 510)), 580)
    add('q', combine(round_bowl, box(530 - weight, -200, 530, 510)), 580)

    # The aperture crosses the full stroke depth and stays clear in Bold.
    add('c', round_bowl.difference(box(370, 151, 560, 359)), 565)
    e_bowl = oval(50, -8, 525, 518, weight)
    e_open = e_bowl.difference(box(375, 147, 560, 255))
    e_outer = ellipse(287.5, 255, 237.5, 263)
    e_bar = box(65, 255, 510, 255 + horizontal).intersection(e_outer)
    add('e', combine(e_open, e_bar), 575)

    lower_a = oval(50, -8, 490, 330, weight)
    upper_a = modulated_stroke(_curve(
        ((95, 433), (164, 498), (294, 518 - horizontal / 2),
         (334, 518 - horizontal / 2)),
        ((334, 518 - horizontal / 2), (429, 518 - horizontal / 2),
         (490 - weight / 2, 440), (490 - weight / 2, 344)),
    ), weight)
    add('a', combine(lower_a, upper_a, box(490 - weight, 0, 490, 350)), 545)

    g_tail = modulated_stroke(_curve(
        ((530 - weight / 2, 270), (530 - weight / 2, 110),
         (530 - weight / 2, -33), (530 - weight / 2, -62)),
        ((530 - weight / 2, -62), (530 - weight / 2, -123),
         (402, -200 + horizontal / 2), (289, -200 + horizontal / 2)),
        ((289, -200 + horizontal / 2), (212, -200 + horizontal / 2),
         (142, -121), (106, -95)),
    ), weight)
    add('g', combine(round_bowl, box(530 - weight, 255, 530, 510), g_tail), 580)

    add('n', _arch(50, 515, weight), 565)
    add('h', _arch(50, 515, weight, stem_top=700), 565)
    add('m', combine(_arch(50, 430, weight),
                     _arch(430 - weight, 810, weight, stem_top=434)), 860)

    u_shape = poly(
        [(50, 510), (50, 190)]
        + _curve(
            ((50, 190), (50, 68), (110, -8), (235, -8)),
            ((235, -8), (345, -8), (405, 45), (515 - weight, 88)),
        )
        + [(515 - weight, 0), (515, 0), (515, 510),
           (515 - weight, 510), (515 - weight, 212)]
        + _curve(
            ((515 - weight, 212), (515 - weight, horizontal - 2),
             (50 + weight, horizontal - 12), (50 + weight, 206)),
        )
        + [(50 + weight, 510)]
    )
    add('u', u_shape, 565)

    shoulder_r = modulated_stroke(_curve(
        ((50 + weight / 2, 298), (50 + weight / 2, 461),
         (216, 531), (341, 459)),
    ), weight)
    add('r', combine(box(50, 0, 50 + weight, 510), shoulder_r), 385)

    dot = ellipse(100, 650, weight * .54, weight * .54)
    add('i', combine(box(100 - weight / 2, 0, 100 + weight / 2, 510), dot), 210)
    j_stem_x = 133
    j_tail = modulated_stroke(_curve(
        ((j_stem_x, 510), (j_stem_x, 350), (j_stem_x, 100), (j_stem_x, -54)),
        ((j_stem_x, -54), (j_stem_x, -145),
         (104, -200 + horizontal / 2), (62, -200 + horizontal / 2)),
        ((62, -200 + horizontal / 2), (40, -200 + horizontal / 2),
         (22, -183 + horizontal / 2), (8, -162 + horizontal / 2)),
    ), weight)
    j_dot = ellipse(j_stem_x, 650, weight * .54, weight * .54)
    add('j', combine(j_tail, j_dot), 235)

    l_foot = modulated_stroke(_curve(
        ((50 + weight / 2, 700), (50 + weight / 2, 500),
         (50 + weight / 2, 160), (50 + weight / 2, 109)),
        ((50 + weight / 2, 109), (50 + weight / 2, horizontal / 2),
         (128, horizontal / 2), (207, horizontal / 2)),
    ), weight)
    add('l', l_foot, 255)

    f_hook = modulated_stroke(_curve(
        ((130 + weight / 2, 0), (130 + weight / 2, 180),
         (130 + weight / 2, 490), (130 + weight / 2, 552)),
        ((130 + weight / 2, 552), (130 + weight / 2, 681),
         (253, 700 - horizontal / 2), (339, 657)),
    ), weight)
    add('f', combine(f_hook, box(40, 410, 337, 410 + horizontal)), 365)

    t_hook = modulated_stroke(_curve(
        ((125 + weight / 2, 645), (125 + weight / 2, 450),
         (125 + weight / 2, 230), (125 + weight / 2, 142)),
        ((125 + weight / 2, 142), (125 + weight / 2, horizontal / 2),
         (248, horizontal / 2 - 9), (331, 61)),
    ), weight)
    add('t', combine(t_hook, box(35, 410, 335, 410 + horizontal)), 375)

    diagonal = weight * .97
    k_upper = modulated_stroke([(72, 202), (459 - weight / 2, 510)], diagonal)
    k_lower = modulated_stroke([(251, 352), (480 - weight / 2, 0)], diagonal)
    k_body = combine(box(50, 0, 50 + weight, 700), k_upper, k_lower)
    add('k', k_body.intersection(box(50, 0, 490, 700)), 535)

    def descending_pair(left, middle, right, top=510, bottom=0):
        return modulated_stroke([(left + weight / 2, top),
                                 (middle, bottom + horizontal / 2),
                                 (right - weight / 2, top)], diagonal, join='mitre')

    add('v', descending_pair(45, 280, 515).intersection(box(45, 0, 515, 510)), 560)
    w_path = [(45 + weight / 2, 510), (227, horizontal / 2),
              (392, 510 - horizontal / 2), (557, horizontal / 2),
              (740 - weight / 2, 510)]
    add('w', modulated_stroke(w_path, diagonal, join='mitre')
        .intersection(box(45, 0, 740, 510)), 785)
    x_shape = combine(
        modulated_stroke([(50 + weight / 2, 510), (490 - weight / 2, 0)], diagonal),
        modulated_stroke([(490 - weight / 2, 510), (50 + weight / 2, 0)], diagonal),
    ).intersection(box(50, 0, 490, 510))
    add('x', x_shape, 540)

    y_left = modulated_stroke([(45 + weight / 2, 510), (280, 28)], diagonal)
    y_right = modulated_stroke(_curve(
        ((515 - weight / 2, 510), (413, 320), (281, 16), (233, -81)),
        ((233, -81), (192, -166), (151, -196 + horizontal / 2), (67, -166)),
    ), diagonal)
    add('y', combine(y_left, y_right).intersection(box(35, -200, 515, 510)), 560)

    z_rise = 510 - 2 * horizontal
    z_ratio = (diagonal * .92 / z_rise) ** 2
    z_a, z_b, z_c = 1 - z_ratio, 2 * z_ratio * 440, -diagonal ** 2 - z_ratio * 440 ** 2
    z_band = (-z_b + sqrt(z_b * z_b - 4 * z_a * z_c)) / (2 * z_a)
    z_shape = poly([(50,510),(490,510),(490,510-horizontal),
                    (50+z_band,horizontal),(490,horizontal),(490,0),
                    (50,0),(50,horizontal),(490-z_band,510-horizontal),
                    (50,510-horizontal)])
    add('z', z_shape, 540)

    s_curve = _curve(
        ((440 - weight * .18, 431), (399, 481), (334, 518 - horizontal / 2),
         (268, 518 - horizontal / 2)),
        ((268, 518 - horizontal / 2), (169, 518 - horizontal / 2),
         (66 + weight / 2, 447), (66 + weight / 2, 382)),
        ((66 + weight / 2, 382), (66 + weight / 2, 316),
         (146, 287), (270, 254)),
        ((270, 254), (374, 225), (461 - weight / 2, 202),
         (461 - weight / 2, 133)),
        ((461 - weight / 2, 133), (461 - weight / 2, 47),
         (362, -8 + horizontal / 2), (267, -8 + horizontal / 2)),
        ((267, -8 + horizontal / 2), (181, -8 + horizontal / 2),
         (104, 30), (61 + weight * .15, 86)),
    )
    add('s', modulated_stroke(s_curve, weight), 520)
    return letters
