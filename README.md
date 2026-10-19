# Fonts

Aperture and Interval: original Latin display fonts, desktop and webfont files, and editable outline sources.

| Family | Weights | Download |
| --- | --- | --- |
| [Aperture](aperture/) | Regular, Medium, Bold | [Aperture ZIP](dist/aperture.zip) |
| [Interval](interval/) | Regular, Medium, Bold | [Interval ZIP, including variants](dist/interval.zip) |
| [Interval Barless](interval/variants/barless/) | Medium | Included in the Interval ZIP |
| [Interval Open](interval/variants/open/) | Regular, Medium, Bold | Included in the Interval ZIP |

Interval Barless removes the A crossbar. Interval Open combines that A with an open R. The variants have separate family names and can be installed alongside standard Interval.

## Install

Download a family archive, extract it, and install its `.ttf` files with your operating system's font manager. For websites, use the `.woff2` files and the stylesheet supplied with each family or variant.

Each font supports 366 characters, including Latin extensions, tabular numerals, punctuation, and combining accents. These are upright, unhinted display fonts. They have no italic styles or variable axes.

## Build

Each family's README contains its rebuild commands and prerequisites. The sources require Python 3.10 or later and HarfBuzz's `hb-shape` command.

To package the current font files into separate archives, run:

```sh
python3 tools/package.py
```

The command writes `dist/aperture.zip`, `dist/interval.zip`, and `dist/SHA256SUMS`. The archives contain fonts, stylesheets, build sources, and usage instructions.

## License

The fonts, outline sources, build scripts, stylesheets, and accompanying documentation are licensed under the [SIL Open Font License 1.1](LICENSE). No Reserved Font Names are declared.
