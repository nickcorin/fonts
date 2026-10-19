# Interval

Interval is a geometric Latin typeface with round bowls, tabular numerals, and selective stroke omissions. The family includes Regular, Medium, and Bold in TTF and WOFF2 formats.

The fonts support 366 characters, including printable ASCII, Latin-1 Supplement, Latin Extended-A, punctuation, and combining accents. OpenType tables provide kerning, accent attachment, stacked marks, and dotless forms for accented i and j. Version 1.102.

## Install

Install the TTF files in [fonts](fonts) through your operating system's font manager. To use the web fonts, copy the `fonts` directory with [interval.css](interval.css) and load that stylesheet.

```css
h1 {
	font-family: "Interval", sans-serif;
	font-weight: 500;
	font-synthesis: none;
}
```

## Build

Use Python 3.10 or later. Install [HarfBuzz](https://github.com/harfbuzz/harfbuzz) with its `hb-shape` command available on your path, then run these commands from this directory:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r source/requirements.txt
.venv/bin/python source/build.py
```

The builder writes TTF and WOFF2 files to the `fonts` directory. It checks character coverage, outline validity, metrics, and accent shaping. It also writes `manifest.json` with font metrics and character coverage.
