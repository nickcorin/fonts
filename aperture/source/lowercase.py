"""Native lowercase outlines for Aperture's extended geometric construction."""

from shapely.affinity import scale
from shapely.geometry import box

from font_engine import Glyph, bowl, combine, cubic, poly, roundrect, stroke


def _modulated_stroke(points, weight):
    """Keep horizontal material lighter than the vertical stems."""
    normalized = [(x, y / .84) for x, y in points]
    return scale(stroke(normalized, weight), xfact=1, yfact=.84, origin=(0, 0))


def _stem_join(left, right, weight, side='left', edge='top'):
    """Ease the six-unit bowl overshoot into a flat-ended stem."""
    points = [(0, 390), (0, 460), (weight*.6, 460)]
    points += cubic((weight*.6, 460), (weight*.9, 460), (115, 466), (135, 466))
    points += [(135, 390)]
    points = [(right-x if side == 'right' else left+x,
               460-y if edge == 'bottom' else y) for x, y in points]
    return poly(points)


def _shoulder(left, right, weight, join_right=False):
    outer = roundrect(left, -150, right, 466, 135, 135)
    outer = combine(outer, _stem_join(left, right, weight))
    if join_right:
        outer = combine(outer, _stem_join(left, right, weight, side='right'))
    inner = roundrect(left + weight, -175, right - weight, 466 - weight*.84,
                      max(32, 135 - weight*.75), max(32, 135 - weight*.72))
    arch = outer.difference(inner).intersection(box(left, 0, right, 466))
    return combine(arch, box(left, 0, left + weight, 460))


def build_lowercase(stroke_width: float) -> dict[str, Glyph]:
    """Return a–z with fixed outer proportions and weight-dependent counters."""
    weight = stroke_width
    horizontal = weight * .84
    half = weight / 2
    half_horizontal = horizontal / 2
    left, right = 50, 650
    lower_bowl = bowl(left, -6, right, 466, weight, 135, 135)
    counter = roundrect(left+weight, -6+horizontal, right-weight, 466-horizontal,
                        max(24, 135-weight*.8), max(24, 135-weight*.8))
    upper_left = _stem_join(left, right, weight).difference(counter)
    upper_right = _stem_join(left, right, weight, side='right').difference(counter)
    lower_left = _stem_join(left, right, weight, edge='bottom').difference(counter)
    lower_right = _stem_join(left, right, weight, side='right', edge='bottom').difference(counter)
    glyphs: dict[str, Glyph] = {}

    glyphs['o'] = Glyph(lower_bowl, 700)
    glyphs['a'] = Glyph(combine(lower_bowl, upper_right, lower_right,
                                box(right-weight, 0, right, 460)), 700)
    glyphs['b'] = Glyph(combine(lower_bowl, lower_left, box(left, 0, left+weight, 620)), 700)
    glyphs['d'] = Glyph(combine(lower_bowl, lower_right, box(right-weight, 0, right, 620)), 700)
    glyphs['p'] = Glyph(combine(lower_bowl, upper_left, box(left, -180, left+weight, 460)), 700)
    glyphs['q'] = Glyph(combine(lower_bowl, upper_right, box(right-weight, -180, right, 460)), 700)

    open_bowl = lower_bowl.difference(box(475, 116, 710, 344))
    glyphs['c'] = Glyph(open_bowl, 690)
    eye = lower_bowl.difference(box(470, 106, 710, 230))
    eye = combine(eye, box(left+weight/2, 230-half_horizontal, right, 230+half_horizontal))
    glyphs['e'] = Glyph(eye, 700)

    descender = [(right-half, 460), (right-half, -48)]
    descender += cubic((right-half, -48), (right-half, -130),
                       (right-92, -180+half_horizontal), (right-180, -180+half_horizontal))
    descender += [(220, -180+half_horizontal)]
    descender += cubic((220, -180+half_horizontal), (155, -180+half_horizontal),
                       (110, -150+half_horizontal), (100, -103))
    glyphs['g'] = Glyph(combine(lower_bowl, upper_right,
                                _modulated_stroke(descender, weight)), 700)

    shoulder = _shoulder(50, 640, weight)
    glyphs['n'] = Glyph(shoulder, 690)
    glyphs['h'] = Glyph(combine(shoulder, box(50, 0, 50+weight, 620)), 690)
    glyphs['m'] = Glyph(combine(_shoulder(50, 500, weight, join_right=True),
                                _shoulder(500-weight, 950, weight)), 1000)

    cup_outer = roundrect(50, -6, 640, 650, 135, 135)
    cup_inner = roundrect(50+weight, -6+horizontal, 640-weight, 675,
                          max(32, 135-weight*.75), max(32, 135-weight*.72))
    cup_outer = combine(cup_outer, _stem_join(50, 640, weight, side='right', edge='bottom'))
    cup = cup_outer.difference(cup_inner).intersection(box(50, -6, 640, 460))
    glyphs['u'] = Glyph(combine(cup, box(640-weight, 0, 640, 460)), 690)

    arm = _shoulder(50, 480, weight).difference(box(50+weight, -1, 510, 327))
    glyphs['r'] = Glyph(arm, 510)

    stem_center = 125
    dot = roundrect(stem_center-half, 620-weight, stem_center+half, 620, 9, 9)
    glyphs['i'] = Glyph(combine(box(stem_center-half, 0, stem_center+half, 460), dot), 250)

    hook_center = 270-half
    hook = [(hook_center, 460), (hook_center, -50)]
    hook += cubic((hook_center, -50), (hook_center, -130),
                  (210, -180+half_horizontal), (135, -180+half_horizontal))
    hook += [(50, -180+half_horizontal)]
    hook_dot = roundrect(270-weight, 620-weight, 270, 620, 9, 9)
    glyphs['j'] = Glyph(combine(_modulated_stroke(hook, weight), hook_dot), 330)

    foot = [(65+half, 620), (65+half, 125)]
    foot += cubic((65+half, 125), (65+half, 55),
                  (145, half_horizontal), (215, half_horizontal))
    foot += [(295, half_horizontal)]
    glyphs['l'] = Glyph(_modulated_stroke(foot, weight), 345)

    ascender = [(145+half, 0), (145+half, 478)]
    ascender += cubic((145+half, 478), (145+half, 570),
                      (250, 620-half_horizontal), (330, 620-half_horizontal))
    ascender += [(440, 620-half_horizontal)]
    glyphs['f'] = Glyph(combine(_modulated_stroke(ascender, weight),
                                box(50, 425-half_horizontal, 420, 425+half_horizontal)), 475)

    upright = [(155+half, 585), (155+half, 125)]
    upright += cubic((155+half, 125), (155+half, 50),
                      (245, half_horizontal), (315, half_horizontal))
    upright += [(445, half_horizontal)]
    glyphs['t'] = Glyph(combine(_modulated_stroke(upright, weight),
                                box(50, 425-half_horizontal, 430, 425+half_horizontal)), 485)

    top = 466-half_horizontal
    bottom = -6+half_horizontal
    left_center, right_center = 50+half, 650-half
    serpentine = [(right_center, 365)]
    serpentine += cubic((right_center, 365), (right_center, top-30),
                        (565, top), (485, top))
    serpentine += [(205, top)]
    serpentine += cubic((205, top), (110, top),
                        (left_center, 405), (left_center, 345))
    serpentine += cubic((left_center, 345), (left_center, 267),
                        (125, 230), (220, 230))
    serpentine += [(470, 230)]
    serpentine += cubic((470, 230), (570, 230),
                        (right_center, 193), (right_center, 121))
    serpentine += cubic((right_center, 121), (right_center, 46),
                        (570, bottom), (485, bottom))
    serpentine += [(205, bottom)]
    serpentine += cubic((205, bottom), (115, bottom),
                        (left_center, 37), (left_center, 100))
    glyphs['s'] = Glyph(_modulated_stroke(serpentine, weight), 700)

    glyphs['v'] = Glyph(poly([(50, 460), (50+weight, 460), (350, 91),
                             (650-weight, 460), (650, 460),
                             (350+weight*.55, 0), (350-weight*.55, 0)]), 700)
    glyphs['w'] = Glyph(poly([(50, 460), (50+weight, 460), (265, 98),
                             (480-weight*.5, 460), (480+weight*.5, 460),
                             (695, 98), (910-weight, 460), (910, 460),
                             (695+weight*.55, 0), (695-weight*.55, 0),
                             (480, 350), (265+weight*.55, 0),
                             (265-weight*.55, 0)]), 960)

    cross_bounds = box(50, 0, 650, 460)
    cross = combine(stroke([(50, 0), (650, 460)], weight*1.03),
                    stroke([(50, 460), (650, 0)], weight*.75))
    glyphs['x'] = Glyph(cross.intersection(cross_bounds), 700)

    upper_start = 50+weight*.65
    upper_slope = 285/(620-upper_start)
    lower_slope = -260/340
    join_x = (175-upper_slope*upper_start-260+lower_slope*310)/(lower_slope-upper_slope)
    join_y = 260+(join_x-310)*lower_slope
    upper_arm = stroke([(upper_start, 175), (620, 460)], weight*.92)
    lower_arm = stroke([(join_x, join_y), (650, 0)], weight*.92)
    diagonal_arms = combine(upper_arm, lower_arm).intersection(box(50, 0, 650, 460))
    glyphs['k'] = Glyph(combine(box(50, 0, 50+weight, 620), diagonal_arms), 700)

    glyphs['y'] = Glyph(poly([(50, 460), (50+weight, 460), (350, 140),
                             (650-weight, 460), (650, 460),
                             (170+weight*.6, -180), (170-weight*.6, -180),
                             (300, 80)]), 700)

    zigzag = stroke([(650, 460-half_horizontal), (50, half_horizontal)], weight*.92)
    zigzag = zigzag.intersection(box(50, 0, 650, 460))
    glyphs['z'] = Glyph(combine(box(50, 460-horizontal, 650, 460),
                                box(50, 0, 650, horizontal), zigzag), 700)

    return glyphs
