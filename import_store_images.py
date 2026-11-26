"""Copies the game's Google Play visuals into the site, made light for the web.

    python import_store_images.py

Reads the icon and the feature graphic of the game's repository (GAME_STORE) and writes
assets/snake3d/: icon.png (256 px) and feature.webp. Run it again when the store visuals change, then build.py.
"""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parent
GAME_STORE = Path("C:/Users/arthu/Documents/snake-3d-prototype/Assets/Store")
OUTPUT = ROOT / "assets" / "snake3d"


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    icon = Image.open(GAME_STORE / "store_icon_512.png").convert("RGBA")
    icon.resize((256, 256), Image.LANCZOS).save(OUTPUT / "icon.png", optimize=True)
    feature = Image.open(GAME_STORE / "feature_graphic_1024x500.png").convert("RGB")
    feature.save(OUTPUT / "feature.webp", quality=85, method=6)
    print("Written to", OUTPUT)


if __name__ == "__main__":
    main()
