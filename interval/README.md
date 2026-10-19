# Interval

Interval is a geometric Latin typeface with round bowls, tabular numerals, a barless capital A, and an open upper stem on R. The family includes Regular, Medium, and Bold in TTF and WOFF2 formats.

![Interval in Regular, Medium, and Bold, with uppercase and lowercase letters, numerals, and punctuation](previews/specimen.png)

The fonts support 366 characters, including printable ASCII, Latin-1 Supplement, Latin Extended-A, punctuation, and combining accents. OpenType tables provide kerning, accent attachment, stacked marks, and dotless forms for accented i and j. Version 1.103.

## Install

Install the TTF files in [fonts](fonts) through your operating system's font manager. To use the web fonts, copy the `fonts` directory with [interval.css](interval.css) and load that stylesheet.

```css
h1 {
	font-family: "Interval", sans-serif;
	font-weight: 500;
	font-synthesis: none;
}
```

## Upgrade from separate variants

Version 1.103 makes the barless A and open R standard across all three weights, including their accented forms. Uninstall Interval Barless and Interval Open, then install the latest Interval fonts. Replace those family names with `Interval` in your documents and stylesheets. Existing Interval users also receive these new capital forms when upgrading.

## Build

Use Python 3.10 or later. Install [HarfBuzz](https://github.com/harfbuzz/harfbuzz) with its `hb-shape` command available on your path, then run these commands from this directory:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r source/requirements.txt
.venv/bin/python source/build.py
```

The builder writes TTF and WOFF2 files to the `fonts` directory and checks character coverage, outline validity, metrics, and accent shaping. It also writes `manifest.json` with font metrics and character coverage.

## License

This font software is licensed under the [SIL Open Font License 1.1](../LICENSE). No Reserved Font Names are declared. Keep `LICENSE` beside the `interval` directory when extracting the download.
