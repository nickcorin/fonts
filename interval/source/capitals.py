"""Compact geometric capitals and tabular numerals for Interval."""

from math import sqrt

from shapely.affinity import rotate, translate

from font_engine import Glyph, box, combine, cubic, ellipse, modulated_stroke, oval, poly, stroke


def clip(shape, bottom=0, top=700):
    return shape.intersection(box(-100,bottom,1200,top))


def axis_at_join(corner_x, corner_y, inner_x, inner_y, width):
    """Locate a stroke axis whose right edge meets a horizontal join exactly."""
    low, high = corner_x - width * 2, corner_x
    rise = corner_y - inner_y
    for _ in range(40):
        axis_x = (low + high) / 2
        edge_x = axis_x + width / 2 * sqrt(1 + ((axis_x - inner_x) / rise) ** 2)
        if edge_x < corner_x:
            low = axis_x
        else:
            high = axis_x
    return (low + high) / 2


def zigzag(left, right, height, horizontal, diagonal):
    """Join a diagonal to both horizontal bar corners with uniform stroke depth."""
    span = right - left
    rise = height - 2 * horizontal
    ratio = (diagonal / rise) ** 2
    a, b, c = 1 - ratio, 2 * ratio * span, -diagonal ** 2 - ratio * span ** 2
    band = (-b + sqrt(b * b - 4 * a * c)) / (2 * a)
    return poly([(left,height),(right,height),(right,height-horizontal),
                 (left+band,horizontal),(right,horizontal),(right,0),
                 (left,0),(left,horizontal),(right-band,height-horizontal),
                 (left,height-horizontal)])


def right_form(left,bottom,right,top):
    shoulder = left+(right-left)*.38
    middle = (bottom+top)/2
    path=[(left,bottom),(left,top),(shoulder,top)]
    path+=cubic(path[-1],(right,top),(right,middle+(top-bottom)*.26),(right,middle))[1:]
    path+=cubic(path[-1],(right,middle-(top-bottom)*.26),(right,bottom),(shoulder,bottom))[1:]
    return poly(path)


def right_bowl(left,bottom,right,top,weight):
    return right_form(left,bottom,right,top).difference(
        right_form(left+weight,bottom+weight*.92,right-weight,top-weight*.92))


def serpentine(left,right,height,weight):
    h=weight*.92
    center=(left+right)/2
    points=[(right-25,height-118)]
    points+=cubic(points[-1],(right-78,height-h/2),(center+80,height-h/2),(center-12,height-h/2))[1:]
    points+=cubic(points[-1],(left+92,height-h/2),(left+weight/2,height*.86),(left+weight/2,height*.74))[1:]
    points+=cubic(points[-1],(left+weight/2,height*.59),(center-100,height*.55),(center+4,height*.50))[1:]
    points+=cubic(points[-1],(right-118,height*.45),(right-weight/2,height*.41),(right-weight/2,height*.25))[1:]
    points+=cubic(points[-1],(right-weight/2,height*.08),(right-140,h/2),(center+8,h/2))[1:]
    points+=cubic(points[-1],(center-102,h/2),(left+78,h/2),(left+22,118))[1:]
    return modulated_stroke(points,weight)


def build_capitals(stroke_width:float)->dict[str,Glyph]:
    w=stroke_width
    h=w*.92
    H=700
    result={}
    a=poly([(40,0),(318,H),(362,H),(640,0),(640-w*.99,0),
            (340,H-w*1.50),(40+w*.99,0)])
    result['A']=Glyph(a,680)

    b_outer=combine(right_form(65,315,575,H),right_form(65,0,605,370))
    b_inner=combine(right_form(65+w,350+h/2,575-w,H-h),
                    right_form(65+w,h,605-w,350-h/2))
    result['B']=Glyph(b_outer.difference(b_inner),675)

    o=oval(55,-8,715,H+8,w)
    cx,cy=385,350
    opening=poly([(cx,cy),(835,665),(835,35)])
    result['C']=Glyph(o.difference(opening),715)
    result['D']=Glyph(right_bowl(65,0,675,H,w),745)
    result['E']=Glyph(combine(box(65,H-h,535,H),box(65,350-h/2,535,350+h/2),box(65,0,535,h)),600)
    f=combine(box(65,0,65+w,350+h/2),box(65,H-h,535,H),box(65,350-h/2,495,350+h/2))
    result['F']=Glyph(f,600)
    g=o.difference(poly([(cx,cy),(835,cy),(835,665)]))
    result['G']=Glyph(combine(g,box(cx+15,cy-h/2,715,cy+h/2)),775)
    result['H']=Glyph(combine(box(65,0,65+w,H),box(595-w,0,595,H),box(65,350-h/2,595,350+h/2)),660)
    result['I']=Glyph(box(110-w/2,0,110+w/2,H),220)

    j=[(565-w/2,H),(565-w/2,235)]
    j+=cubic(j[-1],(565-w/2,82),(430,h/2),(320,h/2))[1:]
    j+=cubic(j[-1],(200,h/2),(104,80),(70+w/2,165))[1:]
    result['J']=Glyph(modulated_stroke(j,w),630)

    k=combine(box(65,0,65+w,H),stroke([(65+w*.7,310),(575,H)],w*.95),
              stroke([(275,440),(600,0)],w*.95))
    result['K']=Glyph(clip(k),675)
    result['L']=Glyph(combine(box(65,0,65+w,H),box(65,0,535,h)),600)

    m_axis=axis_at_join(65+w,H,425,210,w*.94)
    m_start=m_axis+(m_axis-425)*100/(H-210)
    m_diagonals=stroke([(m_start,H+100),(425,210),(850-m_start,H+100)],w*.94,join='mitre')
    m=combine(box(65,0,65+w,H),box(785-w,0,785,H),m_diagonals)
    m=m.intersection(box(65,0,785,H))
    result['M']=Glyph(clip(m),850)
    n_axis=axis_at_join(65+w,H,365,H/2,w*.94)
    n_start=n_axis+(n_axis-365)*100/(H/2)
    n_diagonal=stroke([(n_start,H+100),(730-n_start,-100)],w*.94)
    n=combine(box(65,0,65+w,H),box(665-w,0,665,H),n_diagonal)
    n=n.intersection(box(65,0,665,H))
    result['N']=Glyph(clip(n),730)
    result['O']=Glyph(o,770)
    p=combine(right_bowl(65,285,575,H,w),box(65,0,65+w,H))
    result['P']=Glyph(p,645)
    result['Q']=Glyph(combine(o,stroke([(485,170),(715,-40)],w*.9)),790)
    # Bury the diagonal's upper cap inside the bowl, below the counter floor.
    diagonal=stroke([(315-295*160/305,465),(610,0)],w*.98)
    r=combine(p,clip(diagonal,top=285+h))
    upper_stem=box(64,285+h,66+w,H-h)
    result['R']=Glyph(r.difference(upper_stem),680)
    result['S']=Glyph(serpentine(55,585,H,w),650)
    result['T']=Glyph(combine(box(30,H-h,610,H),box(320-w/2,0,320+w/2,H)),640)

    u=[(65+w/2,H),(65+w/2,240)]
    u+=cubic(u[-1],(65+w/2,89),(210,h/2),(350,h/2))[1:]
    u+=cubic(u[-1],(490,h/2),(635-w/2,89),(635-w/2,240))[1:]
    u += [(635-w/2,H)]
    result['U']=Glyph(modulated_stroke(u,w),700)
    result['V']=Glyph(poly([(30,H),(30+w*1.04,H),(325,w*1.48),(620-w*1.04,H),(620,H),(347,0),(303,0)]),650)
    ws=stroke([(35+w/2,H),(235,w*.70),(430,570),(625,w*.70),(825-w/2,H)],w*.94,join='mitre')
    result['W']=Glyph(clip(ws),860)
    result['X']=Glyph(clip(combine(stroke([(45,0),(635,H)],w*.94),stroke([(45,H),(635,0)],w*.94))),680)
    y=combine(stroke([(30,H),(325,330),(620,H)],w*.94,join='mitre'),box(325-w/2,0,325+w/2,340))
    result['Y']=Glyph(translate(clip(y),xoff=20),690)
    result['Z']=Glyph(zigzag(55,600,H,h,w*.94),655)
    result.update(build_figures(w))
    return result


def build_figures(w):
    h=w*.92
    H=700
    left,right=65,605
    result={}
    zero=oval(left,-8,right,H+8,w)
    result['0']=Glyph(zero,670)
    flag_x,flag_y=360-w/2,H-h/2
    flag_end=(flag_x+2*w,flag_y+2*w*(flag_y-(H-160))/(flag_x-160))
    flag=stroke([(160,H-160),flag_end],w*.9).intersection(box(-100,0,360+w/2,H))
    one=combine(flag,box(360-w/2,0,360+w/2,H),box(190,0,535,h))
    result['1']=Glyph(clip(one),670)

    two=[(left+w/2,520)]
    two+=cubic(two[-1],(left+w/2,620),(175,H-h/2),(330,H-h/2))[1:]
    two+=cubic(two[-1],(465,H-h/2),(right-w/2,635),(right-w/2,525))[1:]
    two+=cubic(two[-1],(right-w/2,440),(490,375),(385,285))[1:]
    two+=[(left+w*.6,h/2),(right,h/2)]
    result['2']=Glyph(modulated_stroke(two,w),670)

    three=[(left+12,H-112)]
    three+=cubic(three[-1],(140,H-h/2),(230,H-h/2),(335,H-h/2))[1:]
    three+=cubic(three[-1],(495,H-h/2),(right-w/2,620),(right-w/2,525))[1:]
    three+=cubic(three[-1],(right-w/2,408),(450,350),(325,350))[1:]
    three+=[(265,350)]
    upper=modulated_stroke(three,w)
    lower=[(265,350),(325,350)]
    lower+=cubic(lower[-1],(490,350),(right-w/2,290),(right-w/2,180))[1:]
    lower+=cubic(lower[-1],(right-w/2,63),(470,h/2),(335,h/2))[1:]
    lower+=cubic(lower[-1],(220,h/2),(140,h/2),(left+10,115))[1:]
    result['3']=Glyph(combine(upper,modulated_stroke(lower,w)),670)
    four_diagonal=stroke([(465,H),(65,225)],w*.94).intersection(box(65,225-h/2,620,H))
    four=combine(four_diagonal,box(65,225-h/2,620,225+h/2),box(465-w/2,0,465+w/2,H))
    result['4']=Glyph(clip(four),670)

    five=[(right-20,H-h/2),(150,H-h/2),(120,370)]
    five+=cubic(five[-1],(220,425),(315,430),(375,430))[1:]
    five+=cubic(five[-1],(510,430),(right-w/2,343),(right-w/2,215))[1:]
    five+=cubic(five[-1],(right-w/2,75),(480,h/2),(335,h/2))[1:]
    five+=cubic(five[-1],(220,h/2),(130,70),(left+12,125))[1:]
    result['5']=Glyph(modulated_stroke(five,w),670)

    lower_oval=oval(left,-8,right,440,w)
    six_back=[(right-35,H-95)]
    six_back+=cubic(six_back[-1],(490,H-h/2),(420,H-h/2),(335,H-h/2))[1:]
    six_back+=cubic(six_back[-1],(150,H-h/2),(left+w/2,520),(left+w/2,230))[1:]
    result['6']=Glyph(combine(lower_oval,modulated_stroke(six_back,w)),670)
    seven_axis=axis_at_join(right,H-h,240,0,w*.94)
    seven_top=240+(seven_axis-240)*(H+100)/(H-h)
    seven_diagonal=stroke([(seven_top,H+100),(240,0)],w*.94).intersection(box(left,0,right,H))
    result['7']=Glyph(combine(box(left,H-h,right,H),seven_diagonal),670)
    result['8']=Glyph(combine(oval(90,318,580,H+8,w),oval(left,-8,right,382,w)),670)
    result['9']=Glyph(rotate(result['6'].shape,180,origin=(335,350)),670)
    return result
