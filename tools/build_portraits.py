"""Leader portraits from docs/art: python tools/build_portraits.py

Run it after tools/build_events.py, which rewrites the world characters with blank portraits.
Each picture is fitted to 156x210, the size of vanilla leader portraits.
"""
import re

from PIL import Image

import build_world as world

MOD = world.MOD
ART = world.PROJECT / "docs" / "art"
SIZE = (156, 210)

# Character id -> picture in docs/art (without .png).
PORTRAITS = {
    "FRA_louis_xx": "portrait_louis_xx",
}
CHARACTER_FILES = [MOD / "common" / "characters" / "lr_characters.txt", MOD / "common" / "characters" / "lr_world_characters.txt"]


def fit(picture):
    scale = max(SIZE[0] / picture.width, SIZE[1] / picture.height)
    picture = picture.resize((round(picture.width * scale), round(picture.height * scale)), Image.LANCZOS)
    left, top = (picture.width - SIZE[0]) // 2, 0  # Keep the top: that is where the face is.
    return picture.crop((left, top, left + SIZE[0], top + SIZE[1]))


def main():
    folder = MOD / "gfx" / "leaders" / "LR"
    folder.mkdir(parents=True, exist_ok=True)
    sprites = []
    for character, art in PORTRAITS.items():
        fit(Image.open(ART / f"{art}.png").convert("RGBA")).save(folder / f"{art}.dds")
        sprites.append(f'\tspriteType = {{\n\t\tname = "GFX_{art}"\n\t\ttexturefile = "gfx/leaders/LR/{art}.dds"\n\t}}\n')
    (MOD / "interface" / "lr_portraits.gfx").write_text("spriteTypes = {\n" + "".join(sprites) + "}\n", encoding="utf-8")

    done = set()
    for path in CHARACTER_FILES:
        text = path.read_text(encoding="utf-8")
        for character, art in PORTRAITS.items():
            block = re.search(rf"\t{character}=\{{.*?\n\t\}}\n", text, re.S)
            if block:
                text = text.replace(block.group(0), block.group(0).replace('"GFX_portrait_unknown"', f'"GFX_{art}"'))
                done.add(character)
        path.write_text(text, encoding="utf-8")
    missing = set(PORTRAITS) - done
    if missing:
        raise SystemExit(f"characters not found: {sorted(missing)}")
    print(f"OK: {len(PORTRAITS)} portraits")


if __name__ == "__main__":
    main()
