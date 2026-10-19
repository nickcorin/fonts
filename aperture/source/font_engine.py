"""Outline primitives for the Aperture extended Latin family."""

from dataclasses import dataclass
from math import cos, sin, pi

from fontTools.pens.ttGlyphPen import TTGlyphPen
from shapely import set_precision
from shapely.geometry import Polygon, LineString, GeometryCollection, box
from shapely.geometry.base import BaseGeometry
from shapely.geometry.polygon import orient
from shapely.ops import unary_union


CAP_HEIGHT = 620
X_HEIGHT = 460
DESCENDER = -180


@dataclass(frozen=True)
class Glyph:
    shape: BaseGeometry
    advance: float


def poly(points):
    return Polygon(points)


def combine(*shapes):
    return unary_union(shapes)


def stroke(points, width, cap='flat', join='round'):
    return LineString(points).buffer(width / 2, cap_style=cap, join_style=join, quad_segs=20)


def cubic(start, first, second, end, steps=24):
    points = []
    for index in range(steps + 1):
        t = index / steps
        u = 1 - t
        points.append(tuple(u**3 * start[axis] + 3*u*u*t*first[axis]
                            + 3*u*t*t*second[axis] + t**3*end[axis]
                            for axis in (0, 1)))
    return points


def roundrect(left, bottom, right, top, radius_x, radius_y=None):
    """A straight-sided bowl with independently controlled corner radii."""
    rx = min(radius_x, (right-left)/2)
    ry = min(radius_y if radius_y is not None else radius_x, (top-bottom)/2)
    k = .5522847498
    corners = [
        ((right-rx, top), (right-rx+k*rx, top), (right, top-ry+k*ry), (right, top-ry)),
        ((right, bottom+ry), (right, bottom+ry-k*ry), (right-rx+k*rx, bottom), (right-rx, bottom)),
        ((left+rx, bottom), (left+rx-k*rx, bottom), (left, bottom+ry-k*ry), (left, bottom+ry)),
        ((left, top-ry), (left, top-ry+k*ry), (left+rx-k*rx, top), (left+rx, top)),
    ]
    return poly([point for corner in corners for point in cubic(*corner)])


def bowl(left, bottom, right, top, weight, radius_x=150, radius_y=165, horizontal_ratio=.84):
    outer = roundrect(left, bottom, right, top, radius_x, radius_y)
    inner = roundrect(left+weight, bottom+weight*horizontal_ratio,
                      right-weight, top-weight*horizontal_ratio,
                      max(24, radius_x-weight*.8), max(24, radius_y-weight*.8))
    return outer.difference(inner)


def ellipse(cx, cy, rx, ry):
    return poly([(cx+rx*cos(t*pi/96),cy+ry*sin(t*pi/96)) for t in range(192)])


def ring(cx, cy, rx, ry, thickness):
    return ellipse(cx, cy, rx, ry).difference(ellipse(cx, cy, rx-thickness, ry-thickness))


def arc(cx, cy, rx, ry, start, end, steps=64):
    return [(cx+rx*cos((start+(end-start)*i/steps)*pi/180),
             cy+ry*sin((start+(end-start)*i/steps)*pi/180)) for i in range(steps+1)]


def quantized_geometry(shape):
    simplified = shape.buffer(0).simplify(.25, preserve_topology=True)
    quantized = set_precision(simplified, grid_size=1, mode="valid_output")
    return set_precision(quantized, grid_size=0)


def to_truetype(shape):
    pen = TTGlyphPen(None)
    geometry = quantized_geometry(shape)
    polygons = [geometry] if geometry.geom_type == 'Polygon' else list(getattr(geometry,'geoms',[]))
    for polygon in polygons:
        if polygon.geom_type != 'Polygon' or polygon.is_empty:
            continue
        polygon = orient(polygon, sign=-1)
        for contour in [polygon.exterior, *polygon.interiors]:
            points = [(round(x), round(y)) for x,y in list(contour.coords)[:-1]]
            if len(points) < 3:
                continue
            pen.moveTo(points[0])
            for point in points[1:]:
                pen.lineTo(point)
            pen.closePath()
    glyph = pen.glyph()
    validate_truetype(glyph)
    return glyph


def validate_truetype(glyph, glyph_set=None):
    """Reject invalid contours after integer quantization or font decoding."""
    coordinates, endpoints, flags = glyph.getCoordinates(glyph_set or {})
    start = 0
    for endpoint in endpoints:
        points = list(coordinates[start:endpoint+1])
        if any(not (flag & 1) for flag in flags[start:endpoint+1]):
            raise ValueError("The linear-outline compiler emitted an off-curve point")
        contour = Polygon(points)
        if len(set(points)) < 3 or contour.area == 0 or not contour.is_valid:
            raise ValueError("Invalid integer outline contour")
        start = endpoint+1
