"""Copies the game's Google Play visuals into the site, made light for the web.

    python import_store_images.py

Reads the icon and the store screenshots of the game's repository (GAME_STORE) and writes
assets/snake3d/: icon.png (256 px) and, for each language, the screenshots with their captions in
that language (WebP, 960 px wide). Run it again when the store visuals change, then build.py.
"""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parent
GAME_STORE = Path("C:/Users/arthu/Documents/snake-3d-prototype/Assets/Store")
OUTPUT = ROOT / "assets" / "snake3d"

SCREENSHOTS = ("01_key_art", "02_long_snake", "03_characters", "04_levels", "05_challenges")
# Language of build.py -> its screenshots folder (English: the folder itself, no prefix).
LANGUAGES = ("en", "fr", "es", "pt_BR", "de", "it", "tr", "id", "pl", "vi")
WIDTH = 960
QUALITY = 80


def _source(lang: str, name: str) -> Path:
    if lang == "en":
        return GAME_STORE / "Screenshots" / f"screenshot_{name}.png"
    return GAME_STORE / "Screenshots" / lang / f"{lang}_screenshot_{name}.png"


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    icon = Image.open(GAME_STORE / "store_icon_512.png").convert("RGBA")
    icon.resize((256, 256), Image.LANCZOS).save(OUTPUT / "icon.png", optimize=True)
    for lang in LANGUAGES:
        folder = OUTPUT / lang.lower().replace("_", "-")
        folder.mkdir(exist_ok=True)
        for index, name in enumerate(SCREENSHOTS, 1):
            image = Image.open(_source(lang, name)).convert("RGB")
            height = round(image.height * WIDTH / image.width)
            image.resize((WIDTH, height), Image.LANCZOS).save(
                folder / f"{index}.webp", quality=QUALITY, method=6)
    print("Written to", OUTPUT)


if __name__ == "__main__":
    main()
