"""Build separately installable Interval variants from the shared outlines."""

from collections.abc import Callable, Sequence
from pathlib import Path

from fontTools.ttLib import TTFont

import build as builder
from font_engine import Glyph


def name_variant(source: Path, destination: Path, family: str, style: str) -> None:
    postscript_family = family.replace(" ", "")
    with TTFont(source, recalcTimestamp=False) as face:
        names = {
            1: f"{family} Medium" if style == "Medium" else family,
            2: "Regular" if style == "Medium" else style,
            3: f"{postscript_family}-{builder.VERSION}-{style}",
            4: f"{family} {style}",
            6: f"{postscript_family}-{style}",
            16: family,
            17: style,
        }
        for record in face["name"].names:
            if record.nameID in names:
                record.string = names[record.nameID].encode(record.getEncoding())
        face.save(destination.with_suffix(".ttf"))
        face.flavor = "woff2"
        face.save(destination.with_suffix(".woff2"))


def build_variant(
    destination: Path,
    family: str,
    capitals: Callable[[float], dict[str, Glyph]],
    styles: Sequence[builder.FontStyle],
) -> None:
    builder.ROOT = destination
    builder.build_capitals = capitals
    manifest = [builder.compile_style(style) for style in styles]
    builder.verify(manifest)
    for entry in manifest:
        source = destination / entry["ttf"]
        filename = family.lower().replace(" ", "-") + "-" + entry["style"].lower()
        name_variant(source, destination / "fonts" / filename, family, entry["style"])
        source.unlink()
        (destination / entry["woff2"]).unlink()
    print(f"Built and verified {family} in {len(styles)} weight(s).")
