"""Latin extensions, typographic symbols, and combining accents for Aperture."""

from math import pi, sin
import unicodedata

from shapely.affinity import rotate, scale, translate
from shapely.geometry import LineString
from shapely.geometry.base import BaseGeometry

from font_engine import Glyph, arc, bowl, box, combine, cubic, ellipse, ring, roundrect, stroke


ABOVE_MARKS = "\u0300\u0301\u0302\u0303\u0304\u0306\u0307\u0308\u030a\u030b\u030c"
BELOW_MARKS = "\u0326\u0327"
OGONEK = "\u0328"
COMBINING_MARKS = ABOVE_MARKS + BELOW_MARKS + OGONEK


def fit(shape: BaseGeometry, advance: float) -> Glyph:
    if shape.is_empty:
        return Glyph(shape, advance)
    shift = max(0, 40-shape.bounds[0])
    shape = translate(shape, xoff=shift)
    return Glyph(shape, max(advance+shift, shape.bounds[2]+50))


def centered(glyph: Glyph, factor: float, center_x: float, center_y: float) -> BaseGeometry:
    shape = scale(glyph.shape, xfact=factor, yfact=factor, origin=(0, 0))
    left, bottom, right, top = shape.bounds
    return translate(shape, xoff=center_x-(left+right)/2, yoff=center_y-(bottom+top)/2)


def ogonek_anchor(glyph: Glyph, weight: float) -> tuple[float, float]:
    """Place the join on the lower-right contour, including rounded bases."""
    left, bottom, right, top = glyph.shape.bounds
    lower_stroke = glyph.shape.intersection(box(left-1, bottom-1, right+1, bottom+weight*.65))
    anchor_x = lower_stroke.bounds[2]-weight*.35
    vertical_slice = glyph.shape.intersection(LineString([(anchor_x, bottom-10), (anchor_x, top+1)]))
    return anchor_x, vertical_slice.bounds[1]


def above_mark(mark: str, center: float, bottom: float, weight: float) -> BaseGeometry:
    thickness = weight*.64
    if mark == "\u0300":
        return stroke([(center-75, bottom+105), (center+60, bottom+10)], thickness)
    if mark == "\u0301":
        return stroke([(center-60, bottom+10), (center+75, bottom+105)], thickness)
    if mark == "\u0302":
        return stroke([(center-110, bottom+10), (center, bottom+105),
                       (center+110, bottom+10)], thickness, join="mitre")
    if mark == "\u0303":
        points = [(center-130+index*260/40, bottom+55+30*sin(index*2*pi/40)) for index in range(41)]
        return stroke(points, thickness)
    if mark == "\u0304":
        return box(center-130, bottom+35, center+130, bottom+35+thickness)
    if mark == "\u0306":
        return stroke(arc(center, bottom+115, 125, 105, 200, 340), thickness)
    if mark == "\u0307":
        return box(center-thickness/2, bottom+30, center+thickness/2, bottom+30+thickness)
    if mark == "\u0308":
        return combine(box(center-115, bottom+30, center-115+thickness, bottom+30+thickness),
                       box(center+115-thickness, bottom+30, center+115, bottom+30+thickness))
    if mark == "\u030a":
        return ring(center, bottom+58, 62, 58, min(weight*.46, 37))
    if mark == "\u030b":
        return combine(stroke([(center-135, bottom+10), (center-40, bottom+110)], thickness),
                       stroke([(center+35, bottom+10), (center+130, bottom+110)], thickness))
    if mark == "\u030c":
        return stroke([(center-110, bottom+105), (center, bottom+10),
                       (center+110, bottom+105)], thickness, join="mitre")
    raise ValueError(f"Unsupported above mark U+{ord(mark):04X}")


def below_mark(mark: str, center: float, weight: float) -> BaseGeometry:
    if mark == "\u0327":
        points = [(center, 7), (center-30, -35), (center+30, -55),
                  (center+40, -95), (center, -125), (center-60, -112)]
    elif mark == "\u0326":
        points = [(center+20, -45), (center+20, -85), (center-20, -135)]
    elif mark == "\u0328":
        points = cubic((center, 10), (center-115, -45), (center-115, -130), (center-30, -130))
        points += cubic((center-30, -130), (center, -130), (center+25, -115), (center+45, -100))[1:]
    else:
        raise ValueError(f"Unsupported below mark U+{ord(mark):04X}")
    return stroke(points, weight*.58)


def extend_glyphs(glyphs: dict[str, Glyph], weight: float) -> dict[str, Glyph]:
    result = dict(glyphs)
    horizontal = weight*.84

    def add(character: str, shape: BaseGeometry, advance: float) -> None:
        result[character] = fit(shape, advance)

    def joined(left: str, right: str, overlap: float) -> Glyph:
        first, second = result[left], result[right]
        offset = first.shape.bounds[2]-second.shape.bounds[0]-overlap
        shape = combine(first.shape, translate(second.shape, xoff=offset))
        return fit(shape, shape.bounds[2]+55)

    def pair(left: str, right: str, spacing: float = -25) -> Glyph:
        first, second = result[left], result[right]
        return fit(combine(first.shape, translate(second.shape, xoff=first.advance+spacing)),
                   first.advance+second.advance+spacing)

    for character, dotless in (("i", "ı"), ("j", "ȷ")):
        result[dotless] = Glyph(result[character].shape.intersection(box(-1000, -1000, 2500, 480)),
                               result[character].advance)

    ae_outline = combine(
        stroke([(70, 0), (420, 620)], weight).intersection(box(0, 0, 2000, 620)),
        box(420-weight/2, 0, 420+weight/2, 620),
        box(420, 620-horizontal, 1090, 620),
        box(420, 310-horizontal/2, 995, 310+horizontal/2),
        box(420, 0, 1090, horizontal),
        box(220, 220, 420, 220+horizontal),
    )
    add("Æ", ae_outline, 1140)
    result["æ"] = joined("a", "e", weight*.5)
    result["Œ"] = joined("O", "E", weight*1.45)
    result["œ"] = joined("o", "e", weight*.5)
    result["Ĳ"] = pair("I", "J")
    result["ĳ"] = pair("i", "j", -10)

    for character, base in (("Ø", "O"), ("ø", "o")):
        glyph = result[base]
        left, bottom, right, top = glyph.shape.bounds
        add(character, combine(glyph.shape, stroke([(left+30, bottom+15),
                                                    (right-30, top-15)], weight*.64)), glyph.advance)

    for character, base, height in (("Ð", "D", 310), ("Đ", "D", 310), ("đ", "d", 525)):
        glyph = result[base]
        left, _, right, _ = glyph.shape.bounds
        start, end = (right-250, right+45) if base == "d" else (left-25, left+340)
        add(character, combine(glyph.shape, box(start, height-horizontal/2,
                                               end, height+horizontal/2)), glyph.advance)

    o = result["o"]
    left, _, right, _ = o.shape.bounds
    center = (left+right)/2
    eth_back = cubic((right-weight/2, 230), (right-weight/2, 465),
                     (center+20, 575), (center-140, 620))
    add("ð", combine(o.shape, stroke(eth_back, weight),
                     stroke([(center-150, 505), (center+135, 575)], horizontal)), o.advance)

    upper_p = result["P"]
    upper_left = upper_p.shape.bounds[0]
    lower_left = result["p"].shape.bounds[0]
    thorn_bowl = translate(upper_p.shape, yoff=-90).intersection(box(-1000, 145, 2500, 575))
    add("Þ", combine(thorn_bowl, box(upper_left, 0, upper_left+weight, 620)), upper_p.advance)
    add("þ", combine(result["p"].shape, box(lower_left, -180, lower_left+weight, 620)), result["p"].advance)

    sharp_s = [(70+weight/2, 0), (70+weight/2, 450)]
    sharp_s += cubic(sharp_s[-1], (70+weight/2, 570), (220, 620-horizontal/2), (375, 620-horizontal/2))[1:]
    sharp_s += cubic(sharp_s[-1], (585, 620-horizontal/2), (645, 470), (410, 325))[1:]
    sharp_s += cubic(sharp_s[-1], (625, 305), (710, 230), (710, 140))[1:]
    sharp_s += cubic(sharp_s[-1], (710, 35), (545, horizontal/2), (350, 30))[1:]
    add("ß", stroke(sharp_s, horizontal), 805)
    cap_sharp_s = [(70+weight/2, 0), (70+weight/2, 620-horizontal/2), (420, 620-horizontal/2)]
    cap_sharp_s += cubic(cap_sharp_s[-1], (655, 620-horizontal/2), (730, 560), (730, 475))[1:]
    cap_sharp_s += cubic(cap_sharp_s[-1], (730, 415), (650, 365), (490, 330))[1:]
    cap_sharp_s += cubic(cap_sharp_s[-1], (735, 295), (795, 230), (795, 140))[1:]
    cap_sharp_s += cubic(cap_sharp_s[-1], (795, 40), (655, horizontal/2), (400, horizontal/2))[1:]
    add("ẞ", stroke(cap_sharp_s, horizontal), 890)

    for character, base in (("Ħ", "H"), ("ħ", "h")):
        glyph = result[base]
        left, _, right, _ = glyph.shape.bounds
        end = left+250 if base == "h" else right+20
        add(character, combine(glyph.shape, box(left-20, 505, end, 505+horizontal*.8)), glyph.advance)
    for character, base in (("Ł", "L"), ("ł", "l")):
        glyph = result[base]
        left = glyph.shape.bounds[0]
        add(character, combine(glyph.shape, stroke([(left-15, 240), (left+265, 390)], horizontal)), glyph.advance)
    for character, base, height in (("Ŧ", "T", 265), ("ŧ", "t", 205)):
        glyph = result[base]
        center = (glyph.shape.bounds[0]+glyph.shape.bounds[2])/2
        add(character, combine(glyph.shape, box(center-190, height, center+190, height+horizontal*.8)), glyph.advance)
    for character, base in (("Ŋ", "N"), ("ŋ", "n")):
        glyph = result[base]
        right = glyph.shape.bounds[2]-weight/2
        floor = -180+horizontal/2
        tail = [(right, 130), (right, -60)]
        tail += cubic(tail[-1], (right, floor), (right-110, floor), (right-220, floor+20))[1:]
        add(character, combine(glyph.shape, stroke(tail, weight)), glyph.advance)

    add("ĸ", result["k"].shape.intersection(box(-1000, -1000, 2500, 460)), result["k"].advance)
    long_s = [(110, 0), (110, 480)]
    long_s += cubic(long_s[-1], (110, 590), (230, 620-horizontal/2), (400, 620-horizontal/2))[1:]
    add("ſ", stroke(long_s, weight), 465)
    for character, base in (("Ŀ", "L"), ("ŀ", "l")):
        glyph = result[base]
        center = max(glyph.shape.bounds[0]+265, glyph.advance-170)
        add(character, combine(glyph.shape, box(center-horizontal/2, 280,
                                               center+horizontal/2, 280+horizontal)),
            max(glyph.advance, center+horizontal/2+55))
    leading_quote = stroke([(75, 620), (75, 555), (40, 505)], horizontal*.8)
    add("ŉ", combine(leading_quote, translate(result["n"].shape, xoff=145)), result["n"].advance+145)

    for codepoint in (*range(0xC0, 0x180), 0x0218, 0x0219, 0x021A, 0x021B):
        character = chr(codepoint)
        decomposition = unicodedata.normalize("NFD", character)
        if decomposition == character:
            continue
        base, *marks = decomposition
        has_upper_accent = any(mark in ABOVE_MARKS for mark in marks)
        accent_base = {"i": "ı", "j": "ȷ"}.get(base, base) if has_upper_accent else base
        glyph = result[accent_base]
        shape = glyph.shape
        left, _, right, top = shape.bounds
        center = (left+right)/2
        if base == "j":
            stem = shape.intersection(box(-1000, 400, 2500, 480))
            center = (stem.bounds[0]+stem.bounds[2])/2
        advance = glyph.advance
        for mark in marks:
            if mark == "\u0327" and base == "g":
                accent = rotate(below_mark("\u0326", 0, weight), 180, origin=(0, 0))
                accent = translate(accent, xoff=center,
                                   yoff=max(515, top+52)-accent.bounds[1])
            elif mark == "\u0327" and base in "GKkLlNnRr":
                accent = below_mark("\u0326", center, weight)
            elif mark in BELOW_MARKS + OGONEK:
                if mark == OGONEK:
                    anchor_x, anchor_y = ogonek_anchor(glyph, weight)
                    accent = translate(below_mark(mark, anchor_x, weight), yoff=anchor_y)
                    if shape.distance(accent) > .5:
                        raise ValueError(f"Detached ogonek in {character}")
                else:
                    accent = below_mark(mark, center, weight)
            elif mark == "\u030c" and base in "dlt":
                ascender = shape.intersection(box(-1000, 500, 2500, 1000))
                anchor_x = ascender.bounds[2]+70
                accent = stroke([(anchor_x, 620), (anchor_x, 560), (anchor_x-35, 505)], weight*.54)
                advance = max(advance, accent.bounds[2]+40)
            else:
                accent = above_mark(mark, center, max(515, top+52), weight)
            shape = combine(shape, accent)
        result[character] = Glyph(shape, advance)

    for mark in ABOVE_MARKS:
        result[mark] = Glyph(above_mark(mark, 0, 0, weight), 0)
    for mark in BELOW_MARKS + OGONEK:
        result[mark] = Glyph(below_mark(mark, 0, weight), 0)

    def quote(opening: bool, bottom: float = 475) -> BaseGeometry:
        points = [(145, bottom+150), (75, bottom+85), (75, bottom)] if opening else [
            (75, bottom+150), (75, bottom+65), (145, bottom)]
        return stroke(points, horizontal*.88)

    for character, opening, bottom in (("‘", True, 475), ("’", False, 475), ("‚", False, -20)):
        add(character, quote(opening, bottom), 235)
    for character, opening, bottom in (("“", True, 475), ("”", False, 475), ("„", False, -20)):
        first = quote(opening, bottom)
        add(character, combine(first, translate(first, xoff=180)), 415)
    for character, direction, count in (("«", -1, 2), ("»", 1, 2), ("‹", -1, 1), ("›", 1, 1)):
        points = [(290, 410), (85, 250), (290, 90)] if direction < 0 else [(85, 410), (290, 250), (85, 90)]
        shape = stroke(points, horizontal, join="mitre")
        if count == 2:
            shape = combine(shape, translate(shape, xoff=250))
        add(character, shape, 390+(count-1)*250)

    add("–", box(50, 265, 850, 265+horizontal), 900)
    add("—", box(50, 265, 1120, 265+horizontal), 1170)
    add("…", combine(*(box(x, 0, x+horizontal, horizontal) for x in (60, 275, 490))), 625)
    add("·", box(85, 245, 85+horizontal, 245+horizontal), 170+horizontal)
    add("•", ellipse(185, 280, 80, 80), 370)
    for character, base, bottom, top in (("$", "S", -70, 690), ("¢", "c", -70, 540)):
        glyph = result[base]
        center = (glyph.shape.bounds[0]+glyph.shape.bounds[2])/2
        add(character, combine(glyph.shape, box(center-weight*.24, bottom,
                                               center+weight*.24, top)), glyph.advance)
    add("€", combine(result["C"].shape, box(40, 230, 500, 230+horizontal*.75),
                     box(40, 365, 500, 365+horizontal*.75)), result["C"].advance)
    pound = [(210, 25), (210, 450)]
    pound += cubic(pound[-1], (210, 575), (345, 620-horizontal/2), (515, 620-horizontal/2))[1:]
    pound += cubic(pound[-1], (620, 620-horizontal/2), (680, 570), (700, 530))[1:]
    add("£", combine(stroke(pound, weight), box(80, 250, 530, 250+horizontal), box(80, 0, 715, horizontal)), 790)
    y = result["Y"]
    center = (y.shape.bounds[0]+y.shape.bounds[2])/2
    add("¥", combine(y.shape, box(center-250, 190, center+250, 190+horizontal*.75),
                     box(center-250, 300, center+250, 300+horizontal*.75)), y.advance)
    add("¤", combine(bowl(175, 130, 645, 540, horizontal, 100, 100),
                     *[stroke(points, horizontal) for points in ([(75, 40), (240, 190)],
                         [(580, 480), (745, 630)], [(75, 630), (240, 480)], [(580, 190), (745, 40)])]), 820)

    minus = box(60, 270, 720, 270+horizontal)
    add("−", minus, 780)
    add("±", combine(box(60, 80, 720, 80+horizontal), box(60, 375, 720, 375+horizontal),
                     box(390-horizontal/2, 220, 390+horizontal/2, 595)), 780)
    add("×", combine(stroke([(120, 90), (660, 530)], horizontal),
                     stroke([(120, 530), (660, 90)], horizontal)), 780)
    add("÷", combine(minus, box(390-horizontal/2, 85, 390+horizontal/2, 85+horizontal),
                     box(390-horizontal/2, 460, 390+horizontal/2, 460+horizontal)), 780)
    for character, points in (("≤", [(680, 600), (95, 380), (680, 165)]),
                              ("≥", [(95, 600), (680, 380), (95, 165)])):
        add(character, combine(stroke(points, horizontal, join="mitre"), box(80, 0, 700, horizontal)), 780)
    add("≠", combine(result["="].shape, stroke([(200, 55), (575, 575)], horizontal*.85)), 780)
    wave = [(65+index*650/48, 205+40*sin(index*2*pi/48)) for index in range(49)]
    add("≈", combine(stroke(wave, horizontal*.8), translate(stroke(wave, horizontal*.8), yoff=195)), 780)
    add("¬", combine(box(60, 310, 720, 310+horizontal), box(720-horizontal, 125, 720, 310)), 780)

    arrow = combine(stroke([(75, 310), (795, 310)], horizontal*.85),
                    stroke([(540, 490), (795, 310), (540, 130)], horizontal*.85, join="mitre"))
    for character, angle in (("→", 0), ("←", 180), ("↑", 90), ("↓", -90)):
        add(character, rotate(arrow, angle, origin=(435, 310)), 870)
    for character, base in (("©", "C"), ("®", "R")):
        add(character, combine(ring(420, 310, 350, 305, horizontal*.65),
                               centered(result[base], .50, 420, 310)), 840)
    add("™", combine(centered(result["T"], .42, 235, 490),
                     centered(result["M"], .42, 680, 490)), 930)

    result["\u00a0"] = result[" "]
    result["\u00ad"] = result["-"]
    add("¡", rotate(result["!"].shape, 180, origin=(result["!"].advance/2, 310)), result["!"].advance)
    add("¿", rotate(result["?"].shape, 180, origin=(result["?"].advance/2, 310)), result["?"].advance)
    add("¦", combine(box(65, -120, 65+horizontal, 195), box(65, 325, 65+horizontal, 670)), 130+horizontal)
    section = cubic((455, 680), (350, 750), (180, 690), (180, 595))
    section += cubic(section[-1], (180, 500), (500, 400), (500, 300))[1:]
    section += cubic(section[-1], (500, 210), (400, 214), (340, 252))[1:]
    section_shape = stroke(section, horizontal*.85)
    section_shape = combine(section_shape, rotate(section_shape, 180, origin=(340, 350)))
    add("§", scale(section_shape, xfact=1.25, yfact=620/700, origin=(0, 0)), 825)
    add("¶", combine(roundrect(50, 290, 550, 620, 130, 120), box(290, 290, 550, 620),
                     box(550-weight, 0, 550, 620), box(655, 0, 655+weight, 620)), 825)
    u = result["u"]
    add("µ", combine(u.shape, box(u.shape.bounds[0], -180, u.shape.bounds[0]+weight, 220)), u.advance)
    add("°", ring(205, 520, 115, 100, horizontal*.65), 410)
    for character, mark in (("¨", "\u0308"), ("¯", "\u0304"), ("´", "\u0301")):
        add(character, above_mark(mark, 200, 515, weight), 400)
    add("¸", below_mark("\u0327", 165, weight), 330)
    for character, base in (("ª", "a"), ("º", "o")):
        add(character, combine(centered(result[base], .60, 275, 490),
                               box(65, 270, 485, 270+horizontal*.65)), 550)
    for character, base in (("¹", "1"), ("²", "2"), ("³", "3")):
        add(character, centered(result[base], .54, 260, 450), 520)
    fraction_slash = stroke([(325, 0), (675, 620)], horizontal*.7)
    for character, numerator, denominator in (("¼", "1", "4"), ("½", "1", "2"), ("¾", "3", "4")):
        add(character, combine(centered(result[numerator], .40, 225, 490), fraction_slash,
                               centered(result[denominator], .40, 785, 130)), 1010)
    add("⁄", fraction_slash, 730)
    for character, advance in (("\u2009", 160), ("\u202f", 160), ("\u2007", result["0"].advance)):
        result[character] = Glyph(result[" "].shape, advance)

    missing = [f"U+{codepoint:04X}" for codepoint in range(0xA0, 0x180) if chr(codepoint) not in result]
    if missing:
        raise ValueError("Incomplete Latin coverage: "+", ".join(missing))
    return result
