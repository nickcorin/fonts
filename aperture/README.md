# Aperture

Aperture is a wide geometric display typeface with a barless A, an open E, and distinct lowercase forms. Version 2.001 includes Regular 400, Medium 500, and Bold 700 in desktop TTF and web WOFF2 formats.

![Aperture in three weights with uppercase, lowercase, numerals, and punctuation](previews/specimen.png)

## Install and use

Install the TTF files in [fonts](fonts) through your operating system's font manager. Applications list the three weights under Aperture. Older applications may list Medium separately as Aperture Medium.

For web use, keep [aperture.css](aperture.css) beside the `fonts` directory and load the stylesheet:

```html
<link rel="stylesheet" href="aperture/aperture.css">
```

```css
.heading {
	font-family: "Aperture", sans-serif;
	font-weight: 500;
	font-kerning: normal;
	font-synthesis: none;
}
```

Use Aperture for headings, identity work, and short text. Start at 18 to 20 px for Regular text and allow comfortable line spacing, especially with stacked accents. Preserve the native letter widths and use the supplied weights instead of synthetic bolding.

## Character support

Each weight maps 366 Unicode characters, with 367 glyphs including `.notdef`. Coverage includes printable ASCII, Latin-1 Supplement, Latin Extended-A, Romanian comma-below letters, capital sharp S, typographic punctuation, currency and mathematical symbols, arrows, fractions, and tabular lining numerals. [manifest.json](manifest.json) records the complete character inventory and font metrics.

Fourteen combining accents have zero advance and OpenType positioning. Mark-to-mark attachment supports stacked accents, and upper accents trigger dotless i and j forms. Pair kerning includes accented letters and spacing adjustments for overlapping letter and numeral pairs.

The family has upright styles only. It has no variable axes, italic styles, non-Latin alphabets, or TrueType hinting instructions. Character support does not include all Unicode Latin characters or all combining marks.

## Build the fonts

Use Python 3.10 or newer. Install HarfBuzz with `hb-shape` available on your `PATH`. From the repository root, run:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r aperture/source/requirements.txt
.venv/bin/python aperture/source/build.py
```

The build writes all six font files and `aperture/manifest.json`. Verification checks exported contours, character coverage, font metadata, numeral advances, mark positioning, kerning, and HarfBuzz shaping. A missing `hb-shape` command stops verification.

The editable outline construction is in [source](source). `capitals.py`, `lowercase.py`, `punctuation.py`, and `extended.py` define the glyphs. `font_engine.py` supplies geometry and TrueType conversion, and `build.py` compiles and verifies the family.

## License

This font software is licensed under the [SIL Open Font License 1.1](../LICENSE). No Reserved Font Names are declared. Keep `LICENSE` beside the `aperture` directory when extracting the download.
