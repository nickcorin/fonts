"""Create separate font archives from the distributable family files."""

import hashlib
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parent.parent
FAMILIES = {"aperture": 6, "interval": 6}


def family_files(family: str) -> list[Path]:
    directory = ROOT / family
    files = [directory / "README.md", directory / f"{family}.css", directory / "manifest.json",
             directory / "previews/specimen.png"]
    files.extend(directory.glob("fonts/*.ttf"))
    files.extend(directory.glob("fonts/*.woff2"))
    files.extend(directory.glob("source/*.py"))
    files.append(directory / "source/requirements.txt")
    return sorted(set(files))


def package_family(family: str, expected_fonts: int) -> Path:
    files = family_files(family)
    missing = [str(path.relative_to(ROOT)) for path in files if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing package files: {missing}")
    font_count = sum(path.suffix in {".ttf", ".woff2"} for path in files)
    if font_count != expected_fonts:
        raise ValueError(f"{family}: expected {expected_fonts} fonts, found {font_count}")

    contents = {path.relative_to(ROOT).as_posix(): path.read_bytes() for path in files}
    contents["LICENSE"] = (ROOT / "LICENSE").read_bytes()
    destination = ROOT / "dist" / f"{family}.zip"
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(contents.items()):
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            archive.writestr(entry, data)

    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise ValueError(f"Archive integrity failed: {destination.name}")
        if set(archive.namelist()) != set(contents):
            raise ValueError(f"Archive inventory differs: {destination.name}")
        for name, data in contents.items():
            if archive.read(name) != data:
                raise ValueError(f"Archived bytes differ: {name}")
    return destination


if __name__ == "__main__":
    (ROOT / "dist").mkdir(exist_ok=True)
    packages = [package_family(family, count) for family, count in FAMILIES.items()]
    checksums = [f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}" for path in packages]
    (ROOT / "dist/SHA256SUMS").write_text("\n".join(checksums) + "\n")
    for package in packages:
        print(f"Packaged {package.relative_to(ROOT)}")
