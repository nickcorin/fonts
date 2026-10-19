"""Build Interval Barless Medium with a crossbar-free capital A."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
FAMILY_ROOT = ROOT.parents[1]
sys.path.insert(0, str(FAMILY_ROOT / "source"))

from capitals import build_capitals
from font_engine import Glyph, poly
from variants import build_variant, builder


def barless_capitals(stroke_width: float) -> dict[str, Glyph]:
    glyphs = build_capitals(stroke_width)
    w = stroke_width
    legs = poly([(40, 0), (318, 700), (362, 700), (640, 0),
                 (640 - w * .99, 0), (340, 700 - w * 1.50), (40 + w * .99, 0)])
    glyphs["A"] = Glyph(legs, glyphs["A"].advance)
    return glyphs


if __name__ == "__main__":
    medium = next(style for style in builder.STYLES if style.name == "Medium")
    build_variant(ROOT, "Interval Barless", barless_capitals, [medium])
