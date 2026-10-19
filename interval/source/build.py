"""Compile and verify the Interval Latin family in TTF and WOFF2 formats."""

from dataclasses import dataclass
import json
from math import ceil
from pathlib import Path
import shutil
import subprocess
import unicodedata

from fontTools.fontBuilder import FontBuilder
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.ttLib import TTFont
from shapely.affinity import translate

from capitals import build_capitals
from extended import ABOVE_MARKS, BELOW_MARKS, COMBINING_MARKS, OGONEK, extend_glyphs, ogonek_anchor
from font_engine import CAP_HEIGHT, X_HEIGHT, Glyph, box, to_truetype, validate_truetype, quantized_geometry
from lowercase import build_lowercase
from punctuation import build_punctuation


ROOT = Path(__file__).resolve().parent.parent
VERSION = "1.103"
LICENSE_TEXT = (Path(__file__).resolve().parents[2] / "LICENSE").read_text(encoding="utf-8")


@dataclass(frozen=True)
class FontStyle:
    name: str
    weight: int
    stroke: int

    @property
    def filename(self) -> str:
        return "interval-" + self.name.lower()


STYLES = (FontStyle("Regular", 400, 72), FontStyle("Medium", 500, 96), FontStyle("Bold", 700, 112))

KERNING = {
    "AV": -42, "AW": -32, "AY": -42, "AT": -22,
    "VA": -42, "WA": -32, "YA": -42, "TA": -28,
    "LT": -32, "LV": -38, "LW": -26, "LY": -44,
    "FA": -28, "PA": -30, "RA": -12,
    "TO": -22, "OT": -22, "VO": -20, "OV": -20,
    "YO": -26, "OY": -26, "YT": -8,
    "Ta": -40, "Te": -40, "To": -40, "Tu": -30, "Ty": -22,
    "Va": -34, "Ve": -28, "Vo": -32, "Vu": -18,
    "Wa": -24, "We": -20, "Wo": -22,
    "Ya": -44, "Ye": -44, "Yo": -44, "Yu": -30,
    "Fa": -16, "Fe": -14, "Fo": -14, "Pa": -16,
    "ry": -8, "rv": -8, "va": -10, "vo": -10,
    "wa": -8, "wo": -8, "ya": -10, "yo": -10,
    "r.": -24, "r,": -24, "T.": -42, "T,": -42,
    "V.": -46, "V,": -46, "W.": -28, "Y.": -46,
    "A’": -26, "L’": -42, "f’": 24,
}


def glyph_name(character: str) -> str:
    return f"uni{ord(character):04X}"


def kerning_adjustments(glyphs: dict[str, Glyph]) -> tuple[dict[tuple[str, str], int], int]:
    groups: dict[str, list[str]] = {}
    for character in glyphs:
        if character not in COMBINING_MARKS:
            base = unicodedata.normalize("NFD", character)[0]
            groups.setdefault(base, []).append(character)
    adjustments = {(left, right): amount for pair, amount in KERNING.items()
                   for left in groups.get(pair[0], []) for right in groups.get(pair[1], [])}

    spacing_glyphs = {character: Glyph(quantized_geometry(glyph.shape), round(glyph.advance))
                      for character, glyph in glyphs.items()}
    characters = [character for character in glyphs if unicodedata.category(character)[0] in "LN"]
    exceptions = 0
    for left in characters:
        first = spacing_glyphs[left]
        for right in characters:
            second = spacing_glyphs[right]
            adjustment = adjustments.get((left, right), 0)
            offset = first.advance+adjustment
            if first.shape.bounds[2] <= offset+second.shape.bounds[0]:
                continue
            placed = translate(second.shape, xoff=offset)
            if first.shape.intersection(placed).area <= 0:
                continue
            maximum = ceil(first.shape.bounds[2]-offset-second.shape.bounds[0]+16)
            for extra in range(1, maximum+1):
                if first.shape.distance(translate(second.shape, xoff=offset+extra)) >= 16-1e-7:
                    adjustments[(left, right)] = adjustment+extra
                    exceptions += 1
                    break
            else:
                raise ValueError(f"Cannot separate colliding pair {left+right!r}")
    for (left, right), adjustment in adjustments.items():
        first, second = spacing_glyphs[left], spacing_glyphs[right]
        if first.shape.intersection(translate(second.shape, xoff=first.advance+adjustment)).area > 0:
            raise ValueError(f"Kerning causes an integer-outline collision: {left+right!r}")
    return adjustments, exceptions


def build_features(glyphs: dict[str, Glyph], stroke: float) -> tuple[str, dict]:
    lines = ["languagesystem DFLT dflt;", "languagesystem latn dflt;"]
    above_names = " ".join(glyph_name(mark) for mark in ABOVE_MARKS)
    lines.append(f"@ABOVE = [{above_names}];")
    lines.extend([
        "feature ccmp {",
        "lookupflag UseMarkFilteringSet @ABOVE;",
        f"sub {glyph_name('i')}' @ABOVE by {glyph_name('ı')};",
        f"sub {glyph_name('j')}' @ABOVE by {glyph_name('ȷ')};",
        f"sub {glyph_name('į')}' @ABOVE by {glyph_name('ı')} {glyph_name(OGONEK)};",
        "} ccmp;",
    ])

    adjustments, spacing_exceptions = kerning_adjustments(glyphs)
    lines.append("feature kern {")
    lines.append("lookupflag IgnoreMarks;")
    for (left, right), adjustment in adjustments.items():
        lines.append(f"pos {glyph_name(left)} {glyph_name(right)} {adjustment};")
    lines.append("} kern;")

    for mark in ABOVE_MARKS:
        lines.append(f"markClass {glyph_name(mark)} <anchor 0 0> @TOP;")
    for mark in BELOW_MARKS:
        lines.append(f"markClass {glyph_name(mark)} <anchor 0 0> @BOTTOM;")
    lines.append(f"markClass {glyph_name(OGONEK)} <anchor 0 0> @OGONEK;")
    bases = [character for character in glyphs if unicodedata.category(character).startswith("L")]
    lines.append("feature mark {")
    for character in bases:
        left, bottom, right, top = glyphs[character].shape.bounds
        center = round((left+right)/2)
        if character in "jȷ":
            stem = glyphs[character].shape.intersection(box(-1000, X_HEIGHT-70, 2500, X_HEIGHT-10))
            center = round((stem.bounds[0]+stem.bounds[2])/2)
        above = round(max(X_HEIGHT+52, top+52))
        ogonek_x, ogonek_y = ogonek_anchor(glyphs[character], stroke)
        lines.append(f"pos base {glyph_name(character)} <anchor {center} {above}> mark @TOP "
                     f"<anchor {center} {round(min(0, bottom))}> mark @BOTTOM "
                     f"<anchor {round(ogonek_x)} {round(ogonek_y)}> mark @OGONEK;")
    lines.append("} mark;")
    lines.append("feature mkmk {")
    for mark in ABOVE_MARKS:
        top = round(glyphs[mark].shape.bounds[3]+45)
        lines.append(f"pos mark {glyph_name(mark)} <anchor 0 {top}> mark @TOP;")
    for mark in BELOW_MARKS + OGONEK:
        bottom = round(glyphs[mark].shape.bounds[1]-35)
        lines.append(f"pos mark {glyph_name(mark)} <anchor 0 {bottom}> mark @BOTTOM;")
    lines.append("} mkmk;")
    return "\n".join(lines), {"kerningPairs": len(adjustments), "spacingExceptions": spacing_exceptions, "positionedMarks": len(COMBINING_MARKS),
                                "markBases": len(bases)}


def compile_style(style: FontStyle) -> dict:
    glyphs = build_capitals(style.stroke)
    glyphs.update(build_lowercase(style.stroke))
    glyphs.update(build_punctuation(style.stroke))
    glyphs = extend_glyphs(glyphs, style.stroke)
    assert glyphs["į"].shape.bounds[3] > X_HEIGHT+100, "Ogonek-only i must retain its dot"
    cmap = {ord(character): glyph_name(character) for character in sorted(glyphs)}
    order = [".notdef", *cmap.values()]
    notdef = box(60, 0, 660, CAP_HEIGHT).difference(box(130, 70, 590, CAP_HEIGHT-70))
    outlines = {".notdef": to_truetype(notdef)}
    metrics = {".notdef": (720, 60)}
    bounds = []
    for character, glyph in glyphs.items():
        if not glyph.shape.is_valid:
            raise ValueError(f"Invalid {style.name} outline: {character!r}")
        if glyph.advance < 0 or (glyph.advance == 0 and character not in COMBINING_MARKS):
            raise ValueError(f"Invalid {style.name} advance: {character!r}")
        name = glyph_name(character)
        outlines[name] = to_truetype(glyph.shape)
        coordinates, _, _ = outlines[name].getCoordinates({})
        left = min(point[0] for point in coordinates) if len(coordinates) else 0
        metrics[name] = (round(glyph.advance), left)
        if not glyph.shape.is_empty:
            bounds.append(glyph.shape.bounds)

    builder = FontBuilder(1000, isTTF=True)
    builder.setupGlyphOrder(order)
    builder.setupCharacterMap(cmap)
    builder.setupGlyf(outlines)
    builder.setupHorizontalMetrics(metrics)
    builder.setupHorizontalHeader(ascent=880, descent=-240, lineGap=0)
    legacy_family = "Interval Medium" if style.name == "Medium" else "Interval"
    legacy_style = "Regular" if style.name == "Medium" else style.name
    builder.setupNameTable({
        "copyright": LICENSE_TEXT.splitlines()[0],
        "licenseDescription": LICENSE_TEXT,
        "licenseInfoURL": "https://openfontlicense.org",
        "familyName": legacy_family,
        "styleName": legacy_style,
        "typographicFamily": "Interval",
        "typographicSubfamily": style.name,
        "uniqueFontIdentifier": f"Interval-{VERSION}-{style.name}",
        "fullName": f"Interval {style.name}",
        "psName": f"Interval-{style.name}",
        "version": f"Version {VERSION}",
        "description": "Original extended Latin typeface with tabular figures, pair kerning, and combining accent positioning.",
    })
    builder.setupOS2(version=4, sTypoAscender=880, sTypoDescender=-240, sTypoLineGap=0,
                     usWinAscent=max(880, round(max(bound[3] for bound in bounds))+2),
                     usWinDescent=max(240, round(-min(bound[1] for bound in bounds))+2),
                     sCapHeight=CAP_HEIGHT, sxHeight=X_HEIGHT, usWeightClass=style.weight,
                     usWidthClass=5, fsType=0,
                     fsSelection=128 | (32 if style.weight == 700 else 64 if style.weight == 400 else 0))
    builder.setupPost()
    builder.setupMaxp()
    builder.font["head"].macStyle = 1 if style.weight == 700 else 0
    builder.font["head"].fontRevision = float(VERSION)
    features, feature_counts = build_features(glyphs, style.stroke)
    addOpenTypeFeaturesFromString(builder.font, features)
    (ROOT / "fonts").mkdir(exist_ok=True)
    destination = ROOT / "fonts" / style.filename
    builder.save(destination.with_suffix(".ttf"))
    builder.font.flavor = "woff2"
    builder.save(destination.with_suffix(".woff2"))
    return {
        "family": "Interval", "style": style.name, "weight": style.weight, "stroke": style.stroke,
        "glyphs": len(order), "codepoints": len(cmap), **feature_counts,
        "ttf": "fonts/"+destination.with_suffix(".ttf").name,
        "woff2": "fonts/"+destination.with_suffix(".woff2").name,
        "characters": "".join(sorted(glyphs)),
        "outlineBounds": [round(min(bound[0] for bound in bounds)), round(min(bound[1] for bound in bounds)),
                          round(max(bound[2] for bound in bounds)), round(max(bound[3] for bound in bounds))],
    }


def verify(manifest: list[dict]) -> dict:
    required = set(range(32, 127)) | set(range(160, 384)) | {ord(mark) for mark in COMBINING_MARKS}
    for entry in manifest:
        for extension in ("ttf", "woff2"):
            with TTFont(ROOT / entry[extension]) as font:
                cmap = font.getBestCmap()
                missing = required-cmap.keys()
                assert not missing, (entry["style"], missing)
                assert font["OS/2"].usWeightClass == entry["weight"]
                assert font["OS/2"].sCapHeight == CAP_HEIGHT
                assert font["OS/2"].sxHeight == X_HEIGHT
                assert abs(font["head"].fontRevision-float(VERSION)) <= 1/65536
                assert font["name"].getDebugName(5) == f"Version {VERSION}"
                assert font["name"].getDebugName(16) == "Interval"
                assert len({font["hmtx"][cmap[ord(digit)]][0] for digit in "0123456789"}) == 1
                assert all(font["hmtx"][cmap[ord(mark)]][0] == 0 for mark in COMBINING_MARKS)
                assert all(cmap[ord(letter)] != cmap[ord(letter.upper())] for letter in "abcdefghijklmnopqrstuvwxyz")
                lookups = {lookup.LookupType for lookup in font["GPOS"].table.LookupList.Lookup}
                assert {2, 4, 6} <= lookups, lookups
                assert "GSUB" in font and "GDEF" in font
                assert font["maxp"].numGlyphs == entry["glyphs"]
                for name in font.getGlyphOrder():
                    validate_truetype(font["glyf"][name], font["glyf"])
                    coordinates, _, _ = font["glyf"][name].getCoordinates(font["glyf"])
                    if len(coordinates):
                        assert font["hmtx"][name][1] == min(point[0] for point in coordinates), name
                        ys = [point[1] for point in coordinates]
                        assert max(ys) <= font["OS/2"].usWinAscent, name
                        assert min(ys) >= -font["OS/2"].usWinDescent, name
    result = {"fontsVerified": len(manifest)*2, "checks": [
        "TTF and WOFF2 parsing, all outline decoding, and valid integer contours",
        "Printable ASCII and complete U+00A0–U+017F coverage",
        "Distinct lowercase and tabular numeral advances",
        "One typographic family with 400, 500, and 700 weight metadata",
        "Zero-advance combining marks and GPOS base/mark attachment",
        "GPOS mark-to-mark attachment and GSUB dotless i/j handling",
        "Connected ogonek contours and retained dot on ogonek-only i",
        "Kerning collision checks across accented pairs and all supported letter/numeral pairs",
        "Vertical bounds and matching 700/510 cap and x-height metadata",
    ]}
    harfbuzz = shutil.which("hb-shape")
    if not harfbuzz:
        raise RuntimeError("Install HarfBuzz hb-shape to verify exported font shaping.")
    verify_shaping(manifest, harfbuzz)
    result["checks"].append("HarfBuzz positions: normalization, intervening lower marks, dotless i/j, stacked accents, and kerning")
    return result


def verify_shaping(manifest: list[dict], harfbuzz: str) -> None:
    def shape(path: Path, text: str, *options: str) -> list[dict]:
        output = subprocess.check_output([harfbuzz, str(path), text, "--output-format=json", *options], text=True)
        return json.loads(output)

    def positions(glyphs: list[dict]) -> list[dict]:
        return [{key: value for key, value in glyph.items() if key != "cl"} for glyph in glyphs]

    for entry in manifest:
        path = ROOT / entry["ttf"]
        accented = "ÄéîñöůçŞŽ"
        assert positions(shape(path, accented)) == positions(shape(path, unicodedata.normalize("NFD", accented)))
        j_acute = shape(path, "j\u0301")
        assert [glyph["g"] for glyph in j_acute] == [glyph_name("ȷ"), glyph_name("\u0301")]
        assert j_acute[1]["ax"] == 0 and j_acute[1]["dy"] >= X_HEIGHT+50
        j_two_marks = shape(path, "j\u0326\u0301")
        assert j_two_marks[0]["g"] == glyph_name("ȷ")
        assert j_two_marks[2]["ax"] == 0 and j_two_marks[2]["dy"] == j_acute[1]["dy"]
        i_ogonek_acute = shape(path, "į\u0301")
        assert [glyph["g"] for glyph in i_ogonek_acute] == [glyph_name("ı"), glyph_name(OGONEK), glyph_name("\u0301")]
        assert i_ogonek_acute[-1]["dy"] >= X_HEIGHT+50
        stacked = shape(path, "x\u0301\u0302")
        assert len(stacked) == 3 and stacked[2]["dy"] > stacked[1]["dy"]+120
        kerned = sum(glyph["ax"] for glyph in shape(path, "AV"))
        unkerned = sum(glyph["ax"] for glyph in shape(path, "AV", "--features=-kern"))
        assert kerned < unkerned
        accent_pair = sum(glyph["ax"] for glyph in shape(path, "īī"))
        accent_pair_without_kern = sum(glyph["ax"] for glyph in shape(path, "īī", "--features=-kern"))
        assert accent_pair > accent_pair_without_kern


if __name__ == "__main__":
    manifest = [compile_style(style) for style in STYLES]
    result = {"version": VERSION, "unitsPerEm": 1000, "capHeight": CAP_HEIGHT, "xHeight": X_HEIGHT,
              "fonts": manifest, "verification": verify(manifest)}
    (ROOT / "manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps(result["verification"], indent=2))
