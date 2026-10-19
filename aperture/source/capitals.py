"""Native extended capitals and tabular figures for Aperture."""

from math import asin, atan2, hypot, tan

from shapely.affinity import scale, translate

from font_engine import Glyph, CAP_HEIGHT, bowl, box, combine, cubic, poly, roundrect, stroke


def _clip(shape, bottom=0, top=CAP_HEIGHT):
    return shape.intersection(box(-100, bottom, 1300, top))


def _horizontal_stroke(points, weight):
    raised = [(x, y/.84) for x,y in points]
    return scale(stroke(raised, weight), yfact=.84, origin=(0, 0))


def _s_shape(left, right, height, weight):
    half = weight*.84/2
    turn = 124
    top = height-half
    middle = height/2
    bottom = half
    path = [(right-12, top), (left+turn, top)]
    path += cubic(path[-1], (left+weight/2, top),
                  (left+weight/2, top-55), (left+weight/2, middle+100))[1:]
    path += cubic(path[-1], (left+weight/2, middle+40),
                  (left+weight/2+38, middle), (left+turn, middle))[1:]
    path += [(right-turn, middle)]
    path += cubic(path[-1], (right-weight/2, middle),
                  (right-weight/2, middle-55), (right-weight/2, bottom+100))[1:]
    path += cubic(path[-1], (right-weight/2, bottom+35),
                  (right-weight/2-38, bottom), (right-turn, bottom))[1:]
    path += [(left+12, bottom)]
    return _horizontal_stroke(path, weight)


def build_capitals(stroke_width: float) -> dict[str, Glyph]:
    w = stroke_width
    h = w*.84
    H = CAP_HEIGHT
    left, right = 55, 855
    glyphs = {}

    # The barless A shares its broad stance with the diagonal capitals.
    a = poly([(50,0),(438,620),(482,620),(870,0),
              (870-w*1.16,0),(460,620-w*1.52),(50+w*1.16,0)])
    glyphs['A'] = Glyph(a, 920)

    b_upper = roundrect(left, 285, 805, H, 142, 126)
    b_lower = roundrect(left, 0, 840, 335, 150, 130)
    b_shape = combine(b_upper, b_lower, box(left,0,left+200,H))
    b_shape = b_shape.difference(roundrect(left+w, 310+h/2, 805-w, H-h, 58, 56))
    b_shape = b_shape.difference(roundrect(left+w, h, 840-w, 310-h/2, 64, 58))
    glyphs['B'] = Glyph(b_shape, 900)

    o = bowl(left, -6, right, H+6, w, 168, 172)
    c = o.difference(box(right-190, 126, right+10, H-126))
    glyphs['C'] = Glyph(c, 910)

    d_outer = roundrect(left,0,860,H,220,220)
    d_outer = combine(d_outer, box(left,0,left+225,H))
    d_inner = roundrect(left+w,h,860-w,H-h,145,160)
    d_inner = combine(d_inner, box(left+w,h,left+230,H-h))
    glyphs['D'] = Glyph(d_outer.difference(d_inner), 920)

    # The upper bar floats above a joined lower construction.
    e = combine(box(left,H-h,815,H), box(left,0,815,h),
                box(left,0,left+w,310+h/2), box(left,310-h/2,735,310+h/2))
    glyphs['E'] = Glyph(e, 875)
    f = combine(box(left,0,left+w,H),box(left,H-h,810,H),
                box(left,310-h/2,710,310+h/2))
    glyphs['F'] = Glyph(f, 865)

    g = o.difference(box(right-190, 275, right+10, H-126))
    g = combine(g, box(505,275,855,275+h), box(855-w,0,855,275+h))
    glyphs['G'] = Glyph(g, 920)
    glyphs['H'] = Glyph(combine(box(left,0,left+w,H),box(825-w,0,825,H),
                               box(left,310-h/2,825,310+h/2)), 885)
    glyphs['I'] = Glyph(combine(box(145-w/2,0,145+w/2,H),
                               box(55,0,235,h),box(55,H-h,235,H)), 290)

    j = bowl(50,-6,785,H,w,160,170).difference(box(-100,205,785-w,H+10))
    j = combine(j,box(785-w,170,785,H))
    glyphs['J'] = Glyph(j, 845)

    rise_start = (left+w/2, 265-w/2*(H-265)/(830-left-w))
    k_rise = stroke([rise_start,(830,H)],w*.93)
    k_fall = stroke([(390,384),(835,0)],w*.88)
    glyphs['K'] = Glyph(combine(box(left,0,left+w,H),_clip(combine(k_rise,k_fall))), 915)
    glyphs['L'] = Glyph(combine(box(left,0,left+w,H),box(left,0,790,h)), 850)

    # Offset the diagonal centerline so its outer edge meets the stem corner.
    m_corner = (55+w, H)
    m_angle = atan2(m_corner[1]-210, m_corner[0]-545)
    m_angle += asin(w*.47/hypot(m_corner[0]-545, m_corner[1]-210))
    m_shoulder = 210+(55+w/2-545)*tan(m_angle)
    m = combine(box(55,0,55+w,H),box(1035-w,0,1035,H),
                stroke([(55+w/2,m_shoulder),(545,210),(1035-w/2,m_shoulder)],w*.94,join='mitre'))
    glyphs['M'] = Glyph(_clip(m),1095)
    # The parallel edges meet opposite stem corners at the cap line and baseline.
    n_span = 860-w-(55+w)
    n_angle = atan2(-H, n_span)+asin(w*.92/hypot(n_span, H))
    n_drop = n_span*tan(n_angle)
    n = combine(box(55,0,55+w,H),box(860-w,0,860,H),
                poly([(55+w,H),(860-w,H+n_drop),(860-w,0),(55+w,-n_drop)]))
    glyphs['N'] = Glyph(_clip(n),920)
    glyphs['O'] = Glyph(o,910)

    p_outer = combine(roundrect(left,258,830,H,146,135),
                      box(left,258,left+146,H),box(left,0,left+w,H))
    p_inner = roundrect(left+w,258+h,830-w,H-h,60,63)
    glyphs['P'] = Glyph(p_outer.difference(p_inner),890)

    q_tail = stroke([(580,190),(875,-70)],w*.85)
    glyphs['Q'] = Glyph(combine(o,q_tail),940)
    # Keep the entire diagonal cap inside the bowl's horizontal band.
    leg_start_y = 258+h/2
    leg_start_x = 458+(290-leg_start_y)*(855-458)/290
    r_leg = _clip(stroke([(leg_start_x,leg_start_y),(855,0)],w*.96))
    glyphs['R'] = Glyph(combine(p_outer.difference(p_inner),r_leg),920)
    glyphs['S'] = Glyph(_s_shape(55,845,H,w),905)
    glyphs['T'] = Glyph(combine(box(35,H-h,865,H),box(450-w/2,0,450+w/2,H)),900)

    u = bowl(55,-6,855,H,w,168,172).difference(box(55+w,H/2,855-w,H+10))
    u = combine(u,box(55,180,55+w,H),box(855-w,180,855,H))
    glyphs['U'] = Glyph(u,910)
    v = poly([(40,H),(40+w*1.18,H),(455,w*1.45),(870-w*1.18,H),(870,H),(477,0),(433,0)])
    glyphs['V'] = Glyph(v,910)
    wa = combine(stroke([(45+w*.5,H),(290,w*.65),(550,405),(810,w*.65),(1055-w*.5,H)],w*.94,join='mitre'))
    glyphs['W'] = Glyph(_clip(wa),1100)

    rise = stroke([(55,0),(865,H)],w*1.03)
    fall = stroke([(55,H),(865,0)],w*.75)
    glyphs['X'] = Glyph(_clip(combine(rise,fall)),920)
    y = combine(stroke([(45,H),(455,275),(865,H)],w*.94,join='mitre'),box(455-w/2,0,455+w/2,290))
    glyphs['Y'] = Glyph(_clip(y),910)
    z = combine(box(55,0,850,h),box(55,H-h,850,H),stroke([(805,H-h/2),(100,h/2)],w*.9))
    glyphs['Z'] = Glyph(_clip(z),910)

    glyphs.update(_figures(w))
    return glyphs


def _figures(w):
    H = CAP_HEIGHT
    h = w*.84
    left, right = 75, 765
    advance = 840
    result = {}
    zero = bowl(left,-6,right,H+6,w,162,168)
    result['0'] = Glyph(zero,advance)
    one = combine(box(450-w/2,0,450+w/2,H),box(245,0,650,h),
                  stroke([(245,H-118),(450-w/2,H-h/2)],w*.86))
    result['1'] = Glyph(_clip(one),advance)

    half = h/2
    path = [(left+w/2,H-125),(left+w/2,H-105)]
    path += cubic(path[-1],(left+w/2,H-half),(left+160,H-half),(420,H-half))[1:]
    path += cubic(path[-1],(650,H-half),(right-w/2,H-half),(right-w/2,H-150))[1:]
    path += cubic(path[-1],(right-w/2,H-250),(620,H-280),(490,270))[1:]
    path += [(left+w/2,h/2),(right,h/2)]
    result['2'] = Glyph(_horizontal_stroke(path,w),advance)

    upper = bowl(left,270,right,H+6,w,145,128)
    lower = bowl(left,-6,right,350,w,145,128)
    three = combine(upper,lower).difference(box(-10,100,285,H-100))
    three = combine(three,box(330,310-h/2,right-110,310+h/2))
    result['3'] = Glyph(three,advance)

    four_diagonal = stroke([(590,H),(left,195)],w*.93).intersection(box(left,0,right,H))
    four = combine(four_diagonal,box(left,195-h/2,right,195+h/2),box(590-w/2,0,590+w/2,H))
    result['4'] = Glyph(_clip(four),advance)

    five_lower = bowl(left,-6,right,350,w,145,128).difference(box(left-10,110,285,360))
    five = combine(five_lower,box(left,350-h,left+w,H),box(left,H-h,right,H),box(left,350-h,560,350))
    result['5'] = Glyph(five,advance)

    six = bowl(left,-6,right,350,w,145,128)
    six_rise = bowl(left,-6,right,H+6,w,162,168).difference(box(330,-10,right+10,H-105))
    result['6'] = Glyph(combine(six,six_rise),advance)
    seven = combine(box(left,H-h,right,H),stroke([(right-w/2,H-h/2),(280,0)],w*.96))
    result['7'] = Glyph(_clip(seven),advance)
    eight = combine(bowl(left,270,right,H+6,w,145,128),bowl(left,-6,right,350,w,145,128))
    result['8'] = Glyph(eight,advance)
    nine = scale(combine(six,six_rise),xfact=-1,yfact=-1,origin=(420,310))
    result['9'] = Glyph(nine,advance)
    return result
