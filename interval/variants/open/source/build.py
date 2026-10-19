"""Build Interval Open with a crossbar-free A and an open upper stem on R."""

from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parent.parent
BARLESS_SOURCE = ROOT.parent / "barless" / "source" / "build.py"
spec = importlib.util.spec_from_file_location("barless_builder", BARLESS_SOURCE)
barless_builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(barless_builder)

from font_engine import Glyph, box
from variants import build_variant, builder


def open_capitals(stroke_width: float) -> dict[str, Glyph]:
    glyphs = barless_builder.barless_capitals(stroke_width)
    horizontal = stroke_width * .92
    upper_stem = box(64, 285 + horizontal, 66 + stroke_width, 700 - horizontal)
    letter = glyphs["R"]
    glyphs["R"] = Glyph(letter.shape.difference(upper_stem), letter.advance)
    return glyphs


if __name__ == "__main__":
    build_variant(ROOT, "Interval Open", open_capitals, builder.STYLES)
