"""Punctuation with the Aperture family's horizontal and corner proportions."""

from math import cos, pi, sin

from shapely.geometry import GeometryCollection

from font_engine import Glyph, arc, bowl, box, combine, cubic, poly, roundrect, stroke


def build_punctuation(weight: float) -> dict[str, Glyph]:
    horizontal = weight * .84
    dot = box(65, 0, 65 + horizontal, horizontal)
    marks = {
        " ": Glyph(GeometryCollection(), 330),
        ".": Glyph(dot, 130 + horizontal),
        ",": Glyph(combine(dot, poly([(65, -95), (65+horizontal, 20),
                                      (65+horizontal, horizontal), (65, 0)])), 130+horizontal),
        ":": Glyph(combine(box(65, 85, 65+horizontal, 85+horizontal),
                           box(65, 365, 65+horizontal, 365+horizontal)), 130+horizontal),
        ";": Glyph(combine(box(65, 365, 65+horizontal, 365+horizontal), dot,
                           poly([(65, -95), (65+horizontal, 20),
                                 (65+horizontal, horizontal), (65, 0)])), 130+horizontal),
        "!": Glyph(combine(dot, box(65, 165, 65+horizontal, 620)), 130+horizontal),
        "-": Glyph(box(55, 260, 460, 260+horizontal), 515),
        "_": Glyph(box(55, -110, 715, -110+horizontal), 770),
        "=": Glyph(combine(box(55, 170, 715, 170+horizontal),
                           box(55, 385, 715, 385+horizontal)), 770),
        "+": Glyph(combine(box(55, 285, 715, 285+horizontal),
                           box(385-horizontal/2, 55, 385+horizontal/2, 570)), 770),
        "/": Glyph(stroke([(75, -30), (635, 650)], horizontal), 710),
        "\\": Glyph(stroke([(75, 650), (635, -30)], horizontal), 710),
        "|": Glyph(box(65, -120, 65+horizontal, 670), 130+horizontal),
        "'": Glyph(box(65, 450, 65+horizontal, 635), 130+horizontal),
        '"': Glyph(combine(box(65, 450, 65+horizontal, 635),
                            box(135+horizontal, 450, 135+2*horizontal, 635)), 200+2*horizontal),
        "[": Glyph(combine(box(60, -105, 60+horizontal, 670),
                           box(60, 670-horizontal, 370, 670),
                           box(60, -105, 370, -105+horizontal)), 430),
        "]": Glyph(combine(box(370-horizontal, -105, 370, 670),
                           box(60, 670-horizontal, 370, 670),
                           box(60, -105, 370, -105+horizontal)), 430),
        "(": Glyph(stroke(arc(440, 282, 310, 390, 112, 248), horizontal), 440),
        ")": Glyph(stroke(arc(0, 282, 310, 390, -68, 68), horizontal), 440),
        "<": Glyph(stroke([(625, 555), (95, 310), (625, 65)], horizontal, join="mitre"), 735),
        ">": Glyph(stroke([(95, 555), (625, 310), (95, 65)], horizontal, join="mitre"), 735),
        "^": Glyph(stroke([(70, 395), (350, 620), (630, 395)], horizontal, join="mitre"), 700),
        "`": Glyph(stroke([(70, 680), (230, 565)], horizontal), 315),
    }
    wave = [(65 + index*610/48, 310 + 45*sin(index*2*pi/48)) for index in range(49)]
    marks["~"] = Glyph(stroke(wave, horizontal), 740)

    brace = [(365, 670), (255, 670)]
    brace += cubic((255, 670), (180, 670), (175, 620), (175, 550))[1:]
    brace += [(175, 405), (80, 282), (175, 160), (175, 10)]
    brace += cubic((175, 10), (175, -60), (180, -105), (255, -105))[1:]
    brace += [(365, -105)]
    marks["{"] = Glyph(stroke(brace, horizontal), 450)
    marks["}"] = Glyph(stroke([(445-x, y) for x, y in brace], horizontal), 450)

    question = [(85, 465)]
    question += cubic((85, 465), (85, 570), (170, 620-horizontal/2), (350, 620-horizontal/2))[1:]
    question += cubic((350, 620-horizontal/2), (535, 620-horizontal/2), (620, 575), (620, 465))[1:]
    question += cubic((620, 465), (620, 370), (535, 340), (420, 305))[1:]
    question += cubic((420, 305), (365, 285), (350, 255), (350, 165))[1:]
    marks["?"] = Glyph(combine(stroke(question, horizontal),
                                box(350-horizontal/2, 0, 350+horizontal/2, horizontal)), 710)
    marks["#"] = Glyph(combine(stroke([(210, 0), (300, 620)], horizontal),
                                stroke([(510, 0), (600, 620)], horizontal),
                                box(65, 175, 740, 175+horizontal),
                                box(85, 395, 760, 395+horizontal)), 825)
    marks["*"] = Glyph(combine(*[stroke([(350, 420),
                                         (350+210*cos(angle), 420+190*sin(angle))], horizontal*.8)
                                   for angle in [pi/2+index*2*pi/5 for index in range(5)]]), 700)
    marks["%"] = Glyph(combine(bowl(65, 360, 330, 626, horizontal*.64, 75, 80),
                                bowl(490, -6, 755, 260, horizontal*.64, 75, 80),
                                stroke([(135, 0), (685, 620)], horizontal*.85)), 820)

    ampersand = cubic((350, 345), (165, 470), (180, 620-horizontal/2), (355, 620-horizontal/2))
    ampersand += cubic((355, 620-horizontal/2), (530, 620-horizontal/2), (570, 470), (330, 330))[1:]
    ampersand += cubic((330, 330), (90, 205), (80, horizontal/2), (340, horizontal/2))[1:]
    ampersand += cubic((340, horizontal/2), (535, horizontal/2), (660, 160), (690, 330))[1:]
    marks["&"] = Glyph(combine(stroke(ampersand, horizontal),
                                stroke([(255, 420), (740, 0)], horizontal)), 835)

    outside = roundrect(45, -35, 855, 655, 220, 210)
    outer_ring = outside.difference(roundrect(45+horizontal*.8, -35+horizontal*.8,
                                             855-horizontal*.8, 655-horizontal*.8, 170, 160))
    outer_ring = outer_ring.difference(box(450, -45, 900, 145))
    marks["@"] = Glyph(combine(outer_ring, bowl(230, 130, 660, 500, horizontal*.8, 100, 110),
                                box(660-horizontal*.8, 135, 660, 500),
                                box(660-horizontal*.8, 135, 820, 135+horizontal*.8)), 910)
    return marks
