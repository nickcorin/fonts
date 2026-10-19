"""Render README specimens from the distributable fonts with HarfBuzz."""

from dataclasses import dataclass
from functools import lru_cache
from io import BytesIO
from pathlib import Path
import shutil
import subprocess

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
WIDTH, HEIGHT = 1800, 1450
MARGIN = 100
BACKGROUND = "#111312"
FOREGROUND = "f0eee7"
SECONDARY = "#a5aaa4"
RULE = "#383c38"
WEIGHTS = (("regular", 400), ("medium", 500), ("bold", 700))


@dataclass(frozen=True)
class Family:
    name: str

    @property
    def directory(self) -> Path:
        return ROOT / self.name.lower()

    def font(self, weight: str) -> Path:
        path = self.directory / "fonts" / f"{self.name.lower()}-{weight}.ttf"
        if not path.is_file():
            raise FileNotFoundError(path)
        return path


@lru_cache(maxsize=None)
def render_text(font: Path, text: str, size: int) -> Image.Image:
    result = subprocess.run(
        [
            "hb-view",
            str(font),
            f"--text={text}",
            f"--font-size={size}",
            "--shapers=ot",
            "--direction=ltr",
            "--language=en",
            "--background=none",
            f"--foreground={FOREGROUND}",
            "--ink",
            "--margin=4",
            "--output-format=png",
        ],
        check=True,
        capture_output=True,
    )
    with Image.open(BytesIO(result.stdout)) as rendered:
        image = rendered.convert("RGBA")
    bounds = image.getbbox()
    if bounds is None:
        raise ValueError(f"Empty font rendering: {text!r}")
    if min(bounds[:2]) <= 0 or bounds[2] >= image.width or bounds[3] >= image.height:
        raise ValueError(f"Clipped font rendering: {text!r}")
    return image.crop(bounds)


def fit_text(font: Path, text: str, size: int, width: int) -> Image.Image:
    image = render_text(font, text, size)
    while image.width > width:
        size = max(1, min(size - 1, int(size * width / image.width)))
        image = render_text(font, text, size)
    return image


def place_text(canvas: Image.Image, image: Image.Image, x: int, y: int) -> None:
    if x < MARGIN or y < 0 or x + image.width > WIDTH - MARGIN or y + image.height > HEIGHT:
        raise ValueError(f"Text exceeds specimen bounds: {(x, y, image.size)}")
    canvas.paste(image, (x, y), image)


def render_specimen(family: Family) -> Path:
    canvas = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    drawing = ImageDraw.Draw(canvas)
    label_font = ImageFont.load_default(size=26)
    small_font = ImageFont.load_default(size=24)
    available_width = WIDTH - MARGIN * 2

    drawing.text((MARGIN, 65), "DISPLAY TYPE / 03 WEIGHTS", font=label_font, fill=SECONDARY)
    drawing.text((WIDTH - MARGIN, 65), "TTF + WOFF2", font=label_font, fill=SECONDARY, anchor="ra")
    hero = fit_text(family.font("bold"), family.name.upper(), 290, available_width)
    place_text(canvas, hero, MARGIN, 175)
    drawing.line((MARGIN, 430, WIDTH - MARGIN, 430), fill=RULE, width=2)

    sample_x = 440
    for index, (weight, number) in enumerate(WEIGHTS):
        top = 495 + index * 122
        drawing.text((MARGIN, top + 24), f"{weight.upper()} / {number}", font=label_font, fill=SECONDARY)
        sample = fit_text(family.font(weight), "FORM & SPACE", 112, WIDTH - MARGIN - sample_x)
        place_text(canvas, sample, sample_x, top)

    drawing.line((MARGIN, 885, WIDTH - MARGIN, 885), fill=RULE, width=2)
    drawing.text((MARGIN, 930), "CHARACTER SAMPLE / MEDIUM", font=small_font, fill=SECONDARY)
    character_rows = (
        ("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 1010, 65),
        ("abcdefghijklmnopqrstuvwxyz", 1110, 76),
        ("0123456789  & @ # % + − = / ? !", 1220, 68),
    )
    for text, top, size in character_rows:
        sample = fit_text(family.font("medium"), text, size, available_width)
        place_text(canvas, sample, MARGIN, top)

    drawing.line((MARGIN, 1350, WIDTH - MARGIN, 1350), fill=RULE, width=2)
    drawing.text((MARGIN, 1385), family.name.upper(), font=small_font, fill=SECONDARY)
    drawing.text((WIDTH - MARGIN, 1385), "SIL OPEN FONT LICENSE 1.1", font=small_font, fill=SECONDARY, anchor="ra")

    destination = family.directory / "previews" / "specimen.png"
    destination.parent.mkdir(exist_ok=True)
    canvas.save(destination, optimize=True)
    return destination


if __name__ == "__main__":
    if shutil.which("hb-view") is None:
        raise SystemExit("Install the HarfBuzz command-line tools to provide hb-view.")
    for name in ("Aperture", "Interval"):
        destination = render_specimen(Family(name))
        print(f"Rendered {destination.relative_to(ROOT)} ({WIDTH} × {HEIGHT})")
