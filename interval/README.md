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

## Variants

[Interval Barless](variants/barless) removes the crossbar from capital A and its accented forms. It is available in Medium.

[Interval Open](variants/open) combines that barless A with an omission in R's upper left stem. It is available in Regular, Medium, and Bold.

Each variant has a separate installable family name and its own CSS file. The lowercase forms remain the same.

## Build

Use Python 3.10 or later. Install [HarfBuzz](https://github.com/harfbuzz/harfbuzz) with its `hb-shape` command available on your path, then run these commands from this directory:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r source/requirements.txt
.venv/bin/python source/build.py
.venv/bin/python variants/barless/source/build.py
.venv/bin/python variants/open/source/build.py
```

The builders write TTF and WOFF2 files to each family's `fonts` directory. They check character coverage, outline validity, metrics, and accent shaping. The main builder also writes `manifest.json` with font metrics and character coverage.

## License

This font software, including Interval Barless and Interval Open, is licensed under the [SIL Open Font License 1.1](../LICENSE). No Reserved Font Names are declared. Keep `LICENSE` beside the `interval` directory when extracting the download.
