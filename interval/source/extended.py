"""Latin extensions, round symbols, and combining accents for Interval."""

from math import pi, sin
import unicodedata
from shapely.affinity import rotate, scale, translate
from shapely.geometry import LineString
from shapely.geometry.base import BaseGeometry
from font_engine import CAP_HEIGHT, X_HEIGHT, DESCENDER, Glyph, arc, box, combine, cubic, ellipse, modulated_stroke, oval, ring, stroke


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
        return stroke([(center-65, bottom+110), (center+50, bottom+10)], thickness)
    if mark == "\u0301":
        return stroke([(center-50, bottom+10), (center+65, bottom+110)], thickness)
    if mark == "\u0302":
        return stroke([(center-105, bottom+10), (center, bottom+110), (center+105, bottom+10)], thickness, join="mitre")
    if mark == "\u0303":
        points = [(center-115+index*230/40, bottom+55+30*sin(index*2*pi/40)) for index in range(41)]
        return stroke(points, thickness)
    if mark == "\u0304":
        return box(center-115, bottom+35, center+115, bottom+35+thickness)
    if mark == "\u0306":
        return stroke(arc(center, bottom+110, 110, 95, 200, 340), thickness)
    if mark == "\u0307":
        return ellipse(center, bottom+30+thickness/2, thickness*.55, thickness*.55)
    if mark == "\u0308":
        return combine(ellipse(center-85, bottom+30+thickness/2, thickness*.55, thickness*.55),
                       ellipse(center+85, bottom+30+thickness/2, thickness*.55, thickness*.55))
    if mark == "\u030a":
        return ring(center, bottom+62, 62, 62, min(weight*.44, 36))
    if mark == "\u030b":
        return combine(stroke([(center-125, bottom+10), (center-45, bottom+110)], thickness),
                       stroke([(center+25, bottom+10), (center+105, bottom+110)], thickness))
    if mark == "\u030c":
        return stroke([(center-105, bottom+110), (center, bottom+10), (center+105, bottom+110)], thickness, join="mitre")
    raise ValueError(f"Unsupported above mark U+{ord(mark):04X}")


def below_mark(mark: str, center: float, weight: float) -> BaseGeometry:
    if mark == "\u0327":
        points = cubic((center, 5), (center-25, -25), (center-40, -40), (center+5, -50))
        points += cubic(points[-1], (center+65, -65), (center+20, -140), (center-55, -110))[1:]
    elif mark == "\u0326":
        points = [(center+20, -45), (center+15, -90), (center-20, -135)]
    elif mark == "\u0328":
        points = cubic((center, 10), (center-105, -45), (center-105, -130), (center-30, -130))
        points += cubic(points[-1], (center, -130), (center+20, -115), (center+40, -100))[1:]
    else:
        raise ValueError(f"Unsupported below mark U+{ord(mark):04X}")
    return stroke(points, weight*.58)


def extend_glyphs(glyphs: dict[str, Glyph], weight: float) -> dict[str, Glyph]:
    result = dict(glyphs)
    horizontal = weight*.92

    def add(character: str, shape: BaseGeometry, advance: float) -> None:
        result[character] = fit(shape, advance)

    def joined(left: str, right: str, overlap: float) -> Glyph:
        first, second = result[left], result[right]
        offset = first.shape.bounds[2]-second.shape.bounds[0]-overlap
        shape = combine(first.shape, translate(second.shape, xoff=offset))
        return fit(shape, shape.bounds[2]+55)

    def pair(left: str, right: str, spacing: float = -15) -> Glyph:
        first, second = result[left], result[right]
        return fit(combine(first.shape, translate(second.shape, xoff=first.advance+spacing)),
                   first.advance+second.advance+spacing)

    for character, dotless in (("i", "ı"), ("j", "ȷ")):
        result[dotless] = Glyph(result[character].shape.intersection(box(-1000, -1000, 2500, X_HEIGHT+1)),
                               result[character].advance)

    ae = combine(stroke([(70, 0), (390, CAP_HEIGHT)], weight).intersection(box(0, 0, 2000, CAP_HEIGHT)),
                 box(390-weight/2, 0, 390+weight/2, CAP_HEIGHT),
                 box(390, CAP_HEIGHT-horizontal, 885, CAP_HEIGHT), box(390, 350-horizontal/2, 805, 350+horizontal/2),
                 box(390, 0, 885, horizontal), box(205, 255, 390, 255+horizontal))
    add("Æ", ae, 950)
    result["æ"] = joined("a", "e", weight*.6)
    oe = combine(oval(65, -8, 725, 708, weight).intersection(box(0, -20, 650, 720)),
                 box(650-weight, 0, 650, 700), box(395, 700-horizontal, 1060, 700),
                 box(630, 350-horizontal/2, 980, 350+horizontal/2), box(395, 0, 1060, horizontal))
    add("Œ", oe, 1120)
    result["œ"] = joined("o", "e", weight*.55)
    result["Ĳ"] = pair("I", "J")
    result["ĳ"] = pair("i", "j", 0)

    for character, base in (("Ø", "O"), ("ø", "o")):
        glyph = result[base]
        left, bottom, right, top = glyph.shape.bounds
        add(character, combine(glyph.shape, stroke([(left+25, bottom+15), (right-25, top-15)], weight*.62)), glyph.advance)
    for character, base, height in (("Ð", "D", 350), ("Đ", "D", 350), ("đ", "d", 595)):
        glyph = result[base]
        left, _, right, _ = glyph.shape.bounds
        start, end = (right-185, right+45) if base == "d" else (left-25, left+280)
        add(character, combine(glyph.shape, box(start, height-horizontal/2, end, height+horizontal/2)), glyph.advance)

    o = result["o"]
    left, _, right, _ = o.shape.bounds
    center = (left+right)/2
    eth = cubic((right-weight/2, 255), (right-weight/2, 515), (center+50, 640), (center-110, 700))
    add("ð", combine(o.shape, modulated_stroke(eth, weight), stroke([(center-115, 570), (center+110, 640)], horizontal*.82)), o.advance)
    upper_p = result["P"]
    upper_left = upper_p.shape.bounds[0]
    lower_left = result["p"].shape.bounds[0]
    thorn_bowl = translate(upper_p.shape, yoff=-100).intersection(box(-1000, 190, 2500, 620))
    add("Þ", combine(thorn_bowl, box(upper_left, 0, upper_left+weight, CAP_HEIGHT)), upper_p.advance)
    add("þ", combine(result["p"].shape, box(lower_left, DESCENDER, lower_left+weight, CAP_HEIGHT)), result["p"].advance)

    sharp_s = [(65+weight/2, 0), (65+weight/2, 495)]
    sharp_s += cubic(sharp_s[-1], (65+weight/2, 620), (150, 700-horizontal/2), (275, 700-horizontal/2))[1:]
    sharp_s += cubic(sharp_s[-1], (435, 700-horizontal/2), (470, 520), (310, 385))[1:]
    sharp_s += cubic(sharp_s[-1], (470, 355), (535, 260), (535, 155))[1:]
    sharp_s += cubic(sharp_s[-1], (535, 45), (435, horizontal/2), (275, 30))[1:]
    add("ß", modulated_stroke(sharp_s, weight), 630)
    cap_sharp_s = [(65+weight/2, 0), (65+weight/2, 700-horizontal/2), (320, 700-horizontal/2)]
    cap_sharp_s += cubic(cap_sharp_s[-1], (495, 700-horizontal/2), (560, 630), (560, 535))[1:]
    cap_sharp_s += cubic(cap_sharp_s[-1], (560, 460), (505, 415), (375, 365))[1:]
    cap_sharp_s += cubic(cap_sharp_s[-1], (560, 330), (610, 255), (610, 155))[1:]
    cap_sharp_s += cubic(cap_sharp_s[-1], (610, 50), (510, horizontal/2), (325, horizontal/2))[1:]
    add("ẞ", modulated_stroke(cap_sharp_s, weight), 710)

    for character, base in (("Ħ", "H"), ("ħ", "h")):
        glyph = result[base]
        left, _, right, _ = glyph.shape.bounds
        end = left+220 if base == "h" else right+20
        add(character, combine(glyph.shape, box(left-20, 585, end, 585+horizontal*.75)), glyph.advance)
    for character, base in (("Ł", "L"), ("ł", "l")):
        glyph = result[base]
        left = glyph.shape.bounds[0]
        add(character, combine(glyph.shape, stroke([(left-15, 280), (left+225, 425)], horizontal*.8)), glyph.advance)
    for character, base, height in (("Ŧ", "T", 300), ("ŧ", "t", 230)):
        glyph = result[base]
        center = (glyph.shape.bounds[0]+glyph.shape.bounds[2])/2
        add(character, combine(glyph.shape, box(center-150, height, center+150, height+horizontal*.75)), glyph.advance)
    for character, base in (("Ŋ", "N"), ("ŋ", "n")):
        glyph = result[base]
        right = glyph.shape.bounds[2]-weight/2
        floor = DESCENDER+horizontal/2
        tail = [(right, 130), (right, -60)]
        tail += cubic(tail[-1], (right, floor), (right-90, floor), (right-180, floor+20))[1:]
        add(character, combine(glyph.shape, modulated_stroke(tail, weight)), glyph.advance)

    add("ĸ", result["k"].shape.intersection(box(-1000, -1000, 2500, X_HEIGHT)), result["k"].advance)
    long_s = [(100, 0), (100, 535)]
    long_s += cubic(long_s[-1], (100, 650), (195, 700-horizontal/2), (325, 700-horizontal/2))[1:]
    add("ſ", modulated_stroke(long_s, weight), 390)
    for character, base in (("Ŀ", "L"), ("ŀ", "l")):
        glyph = result[base]
        center = max(glyph.shape.bounds[0]+220, glyph.advance-130)
        add(character, combine(glyph.shape, ellipse(center, 340, horizontal*.5, horizontal*.5)), max(glyph.advance, center+horizontal/2+55))
    leading_quote = stroke([(70, 700), (70, 635), (40, 580)], horizontal*.7)
    add("ŉ", combine(leading_quote, translate(result["n"].shape, xoff=125)), result["n"].advance+125)

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
            stem = shape.intersection(box(-1000, X_HEIGHT-70, 2500, X_HEIGHT-10))
            center = (stem.bounds[0]+stem.bounds[2])/2
        advance = glyph.advance
        for mark in marks:
            if mark == "\u0327" and base == "g":
                accent = rotate(below_mark("\u0326", 0, weight), 180, origin=(0, 0))
                accent = translate(accent, xoff=center,
                                   yoff=max(X_HEIGHT+52, top+52)-accent.bounds[1])
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
                ascender = shape.intersection(box(-1000, X_HEIGHT+30, 2500, 1000))
                anchor_x = ascender.bounds[2]+65
                accent = stroke([(anchor_x, 700), (anchor_x, 635), (anchor_x-30, 580)], weight*.54)
                advance = max(advance, accent.bounds[2]+40)
            else:
                accent = above_mark(mark, center, max(X_HEIGHT+52, top+52), weight)
            shape = combine(shape, accent)
        result[character] = Glyph(shape, advance)

    for mark in ABOVE_MARKS:
        result[mark] = Glyph(above_mark(mark, 0, 0, weight), 0)
    for mark in BELOW_MARKS + OGONEK:
        result[mark] = Glyph(below_mark(mark, 0, weight), 0)

    def quote(opening: bool, bottom: float = 535) -> BaseGeometry:
        points = [(125, bottom+165), (75, bottom+100), (75, bottom)] if opening else [(75, bottom+165), (75, bottom+65), (125, bottom)]
        return stroke(points, horizontal*.7)

    for character, opening, bottom in (("‘", True, 535), ("’", False, 535), ("‚", False, -20)):
        add(character, quote(opening, bottom), 205)
    for character, opening, bottom in (("“", True, 535), ("”", False, 535), ("„", False, -20)):
        first = quote(opening, bottom)
        add(character, combine(first, translate(first, xoff=145)), 350)
    for character, direction, count in (("«", -1, 2), ("»", 1, 2), ("‹", -1, 1), ("›", 1, 1)):
        points = [(230, 450), (75, 280), (230, 110)] if direction < 0 else [(75, 450), (230, 280), (75, 110)]
        shape = stroke(points, horizontal*.8, join="mitre")
        if count == 2:
            shape = combine(shape, translate(shape, xoff=190))
        add(character, shape, 310+(count-1)*190)

    add("–", box(50, 300, 550, 300+horizontal), 600)
    add("—", box(50, 300, 950, 300+horizontal), 1000)
    add("…", combine(*(ellipse(x, horizontal*.55, horizontal*.55, horizontal*.55) for x in (85, 255, 425))), 510)
    add("·", ellipse(90, 280, horizontal*.55, horizontal*.55), 180)
    add("•", ellipse(150, 300, 75, 75), 300)
    for character, base, bottom, top in (("$", "S", -75, 775), ("¢", "c", -75, 585)):
        glyph = result[base]
        center = (glyph.shape.bounds[0]+glyph.shape.bounds[2])/2
        add(character, combine(glyph.shape, box(center-weight*.22, bottom, center+weight*.22, top)), glyph.advance)
    add("€", combine(result["C"].shape, box(40, 250, 460, 250+horizontal*.7), box(40, 420, 460, 420+horizontal*.7)), result["C"].advance)
    pound = [(185, 25), (185, 490)]
    pound += cubic(pound[-1], (185, 630), (270, 700-horizontal/2), (385, 700-horizontal/2))[1:]
    pound += cubic(pound[-1], (495, 700-horizontal/2), (550, 625), (560, 575))[1:]
    add("£", combine(modulated_stroke(pound, weight), box(65, 280, 420, 280+horizontal), box(65, 0, 580, horizontal)), 650)
    y = result["Y"]
    center = (y.shape.bounds[0]+y.shape.bounds[2])/2
    add("¥", combine(y.shape, box(center-195, 210, center+195, 210+horizontal*.7), box(center-195, 335, center+195, 335+horizontal*.7)), y.advance)
    add("¤", combine(oval(160, 175, 560, 575, horizontal), *[stroke(points, horizontal*.8) for points in (
        [(75, 90), (215, 230)], [(505, 520), (645, 660)], [(75, 660), (215, 520)], [(505, 230), (645, 90)])]), 720)

    minus = box(55, 315, 555, 315+horizontal)
    add("−", minus, 610)
    add("±", combine(box(55, 70, 555, 70+horizontal), box(55, 400, 555, 400+horizontal), box(305-horizontal/2, 240, 305+horizontal/2, 630)), 610)
    add("×", combine(stroke([(105, 130), (505, 570)], horizontal*.9), stroke([(105, 570), (505, 130)], horizontal*.9)), 610)
    add("÷", combine(minus, ellipse(305, 115, horizontal*.5, horizontal*.5), ellipse(305, 580, horizontal*.5, horizontal*.5)), 610)
    for character, points in (("≤", [(530, 630), (80, 390), (530, 155)]), ("≥", [(80, 630), (530, 390), (80, 155)])):
        add(character, combine(stroke(points, horizontal*.85, join="mitre"), box(65, 0, 545, horizontal)), 610)
    add("≠", combine(result["="].shape, stroke([(175, 70), (435, 635)], horizontal*.75)), 610)
    wave = [(55+index*500/48, 230+35*sin(index*2*pi/48)) for index in range(49)]
    add("≈", combine(stroke(wave, horizontal*.75), translate(stroke(wave, horizontal*.75), yoff=220)), 610)
    add("¬", combine(box(55, 350, 555, 350+horizontal), box(555-horizontal, 140, 555, 350)), 610)

    arrow = combine(stroke([(70, 350), (640, 350)], horizontal*.75), stroke([(440, 545), (640, 350), (440, 155)], horizontal*.75, join="mitre"))
    for character, angle in (("→", 0), ("←", 180), ("↑", 90), ("↓", -90)):
        add(character, rotate(arrow, angle, origin=(355, 350)), 710)
    for character, base in (("©", "C"), ("®", "R")):
        add(character, combine(ring(400, 350, 345, 345, horizontal*.6), centered(result[base], .50, 400, 350)), 800)
    add("™", combine(centered(result["T"], .40, 200, 560), centered(result["M"], .40, 520, 560)), 730)

    result["\u00a0"] = result[" "]
    result["\u00ad"] = result["-"]
    add("¡", rotate(result["!"].shape, 180, origin=(result["!"].advance/2, 350)), result["!"].advance)
    add("¿", rotate(result["?"].shape, 180, origin=(result["?"].advance/2, 350)), result["?"].advance)
    add("¦", combine(box(70, -150, 70+horizontal, 225), box(70, 375, 70+horizontal, 750)), 140+horizontal)
    section = cubic((455, 680), (350, 750), (180, 690), (180, 595))
    section += cubic(section[-1], (180, 500), (500, 400), (500, 300))[1:]
    section += cubic(section[-1], (500, 210), (400, 214), (340, 252))[1:]
    section_shape = stroke(section, horizontal*.75)
    add("§", combine(section_shape, rotate(section_shape, 180, origin=(340, 350))), 675)
    pilcrow = combine(ellipse(260, 515, 205, 185), box(260, 330, 465, 700), box(465-weight, 0, 465, 700), box(555, 0, 555+weight, 700))
    add("¶", pilcrow, 720)
    u = result["u"]
    add("µ", combine(u.shape, box(u.shape.bounds[0], DESCENDER, u.shape.bounds[0]+weight, 245)), u.advance)
    add("°", ring(175, 600, 100, 100, horizontal*.6), 350)
    for character, mark in (("¨", "\u0308"), ("¯", "\u0304"), ("´", "\u0301")):
        add(character, above_mark(mark, 175, X_HEIGHT+52, weight), 350)
    add("¸", below_mark("\u0327", 145, weight), 290)
    for character, base in (("ª", "a"), ("º", "o")):
        add(character, combine(centered(result[base], .60, 220, 550), box(65, 315, 375, 315+horizontal*.6)), 440)
    for character, base in (("¹", "1"), ("²", "2"), ("³", "3")):
        add(character, centered(result[base], .54, 230, 515), 460)
    fraction_slash = stroke([(285, 0), (600, 700)], horizontal*.65)
    for character, numerator, denominator in (("¼", "1", "4"), ("½", "1", "2"), ("¾", "3", "4")):
        add(character, combine(centered(result[numerator], .40, 195, 555), fraction_slash, centered(result[denominator], .40, 700, 145)), 900)
    add("⁄", fraction_slash, 665)
    for character, advance in (("\u2009", 140), ("\u202f", 140), ("\u2007", result["0"].advance)):
        result[character] = Glyph(result[" "].shape, advance)

    missing = [f"U+{codepoint:04X}" for codepoint in range(0xA0, 0x180) if chr(codepoint) not in result]
    if missing:
        raise ValueError("Incomplete Latin coverage: "+", ".join(missing))
    return result
