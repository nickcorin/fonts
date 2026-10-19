"""Round punctuation and compact symbols for Interval."""

from math import cos, pi, sin
from shapely.geometry import GeometryCollection
from font_engine import Glyph, arc, box, combine, cubic, ellipse, modulated_stroke, oval, poly, stroke


def build_punctuation(weight: float) -> dict[str, Glyph]:
    horizontal = weight*.92
    dot_radius = horizontal*.56
    dot = ellipse(85, dot_radius, dot_radius, dot_radius)
    dot_advance = 170
    marks = {
        " ": Glyph(GeometryCollection(), 280),
        ".": Glyph(dot, dot_advance),
        ",": Glyph(combine(dot, stroke([(95, 30), (85, -28), (50, -85)], horizontal*.64)), dot_advance),
        ":": Glyph(combine(ellipse(85, 135, dot_radius, dot_radius), ellipse(85, 400, dot_radius, dot_radius)), dot_advance),
        ";": Glyph(combine(ellipse(85, 400, dot_radius, dot_radius), dot,
                           stroke([(95, 30), (85, -28), (50, -85)], horizontal*.64)), dot_advance),
        "!": Glyph(combine(dot, box(85-weight/2, 175, 85+weight/2, 700)), dot_advance),
        "-": Glyph(box(55, 270, 365, 270+horizontal), 420),
        "_": Glyph(box(50, -110, 550, -110+horizontal), 600),
        "=": Glyph(combine(box(55, 205, 555, 205+horizontal), box(55, 425, 555, 425+horizontal)), 610),
        "+": Glyph(combine(box(55, 315, 555, 315+horizontal), box(305-horizontal/2, 90, 305+horizontal/2, 600)), 610),
        "/": Glyph(stroke([(75, -40), (435, 740)], horizontal), 510),
        "\\": Glyph(stroke([(75, 740), (435, -40)], horizontal), 510),
        "|": Glyph(box(70, -150, 70+horizontal, 750), 140+horizontal),
        "'": Glyph(box(65, 515, 65+horizontal, 710), 130+horizontal),
        '"': Glyph(combine(box(65, 515, 65+horizontal, 710), box(140+horizontal, 515, 140+2*horizontal, 710)), 205+2*horizontal),
        "[": Glyph(combine(box(65, -130, 65+horizontal, 750), box(65, 750-horizontal, 290, 750), box(65, -130, 290, -130+horizontal)), 355),
        "]": Glyph(combine(box(290-horizontal, -130, 290, 750), box(65, 750-horizontal, 290, 750), box(65, -130, 290, -130+horizontal)), 355),
        "(": Glyph(stroke(arc(450, 310, 320, 455, 115, 245), horizontal), 370),
        ")": Glyph(stroke(arc(-80, 310, 320, 455, -65, 65), horizontal), 370),
        "<": Glyph(stroke([(540, 590), (85, 340), (540, 90)], horizontal, join="mitre"), 625),
        ">": Glyph(stroke([(85, 590), (540, 340), (85, 90)], horizontal, join="mitre"), 625),
        "^": Glyph(stroke([(70, 465), (290, 680), (510, 465)], horizontal, join="mitre"), 580),
        "`": Glyph(stroke([(85, 750), (210, 625)], horizontal*.72), 295),
    }
    wave = [(65+index*480/48, 335+43*sin(index*2*pi/48)) for index in range(49)]
    marks["~"] = Glyph(stroke(wave, horizontal*.82), 610)

    brace = [(290, 750), (235, 750)]
    brace += cubic(brace[-1], (155, 750), (150, 690), (150, 580))[1:]
    brace += cubic(brace[-1], (150, 450), (150, 365), (65, 310))[1:]
    brace += cubic(brace[-1], (150, 255), (150, 170), (150, 40))[1:]
    brace += cubic(brace[-1], (150, -70), (155, -130), (235, -130))[1:]
    brace += [(290, -130)]
    marks["{"] = Glyph(stroke(brace, horizontal*.85), 365)
    marks["}"] = Glyph(stroke([(365-x, y) for x, y in brace], horizontal*.85), 365)

    question = cubic((95, 540), (95, 645), (185, 700-horizontal/2), (290, 700-horizontal/2))
    question += cubic(question[-1], (405, 700-horizontal/2), (495, 630), (495, 530))[1:]
    question += cubic(question[-1], (495, 435), (435, 390), (350, 340))[1:]
    question += cubic(question[-1], (295, 305), (290, 250), (290, 175))[1:]
    marks["?"] = Glyph(combine(modulated_stroke(question, weight), ellipse(290, dot_radius, dot_radius, dot_radius)), 590)
    marks["#"] = Glyph(combine(stroke([(185, 0), (275, 700)], horizontal*.88), stroke([(405, 0), (495, 700)], horizontal*.88),
                                box(65, 210, 605, 210+horizontal), box(85, 465, 625, 465+horizontal)), 690)
    marks["*"] = Glyph(combine(*[stroke([(260, 500), (260+180*cos(angle), 500+180*sin(angle))], horizontal*.7)
                                  for angle in [pi/2+index*2*pi/5 for index in range(5)]]), 520)
    marks["%"] = Glyph(combine(oval(60, 420, 300, 708, weight*.62), oval(410, -8, 650, 280, weight*.62),
                                stroke([(140, 0), (565, 700)], horizontal*.75)), 710)

    ampersand = cubic((280, 375), (95, 500), (135, 700-horizontal/2), (300, 700-horizontal/2))
    ampersand += cubic(ampersand[-1], (475, 700-horizontal/2), (495, 520), (285, 385))[1:]
    ampersand += cubic(ampersand[-1], (60, 255), (70, horizontal/2), (300, horizontal/2))[1:]
    ampersand += cubic(ampersand[-1], (470, horizontal/2), (560, 175), (585, 340))[1:]
    marks["&"] = Glyph(combine(modulated_stroke(ampersand, weight), stroke([(205, 455), (620, 0)], horizontal)), 700)

    outer = oval(50, -55, 780, 735, weight*.72).difference(box(420, -100, 850, 120))
    marks["@"] = Glyph(combine(outer, oval(245, 120, 600, 550, weight*.72),
                                box(600-weight*.72, 150, 600, 550),
                                modulated_stroke(cubic((600-weight*.36, 200), (600, 80), (730, 120), (745, 230)), weight*.72)), 835)
    return marks
