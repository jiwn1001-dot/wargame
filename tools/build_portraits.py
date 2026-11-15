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
    "FRA_napoleon_bonaparte": "portrait_napoleon_bonaparte",
    "LR_FRA_flandin": "portrait_flandin",
}
# Character id -> a portrait sprite the game already has (vanilla or DLC).
VANILLA = {
    "LR_FRA_orleans": "GFX_portrait_fra_jean_duke_of_guise",  # Jean d'Orleans, Duke of Guise (La Resistance)
}
# DLC-only portraits of the mod's French cast, copied into the mod under the same sprite names
# so they show without the DLC. (Paradox's terms forbid publishing DLC art: keep these out of a public upload.)
DLC_SPRITES = [
    "GFX_portrait_fra_jean_duke_of_guise",
    "GFX_portrait_FRA_charles_maurras",
    "GFX_portrait_FRA_marcel_bucard",
    "GFX_portrait_FRA_marcel_deat",
]
CHARACTER_FILES = [MOD / "common" / "characters" / "lr_characters.txt", MOD / "common" / "characters" / "lr_world_characters.txt"]


def fit(picture):
    scale = max(SIZE[0] / picture.width, SIZE[1] / picture.height)
    picture = picture.resize((round(picture.width * scale), round(picture.height * scale)), Image.LANCZOS)
    left, top = (picture.width - SIZE[0]) // 2, 0  # Keep the top: that is where the face is.
    return picture.crop((left, top, left + SIZE[0], top + SIZE[1]))


def dlc_sprites(folder):
    """Copy each DLC sprite's texture into the mod; return the sprite definitions."""
    import shutil
    found = {}
    for root in (world.VANILLA / "dlc").iterdir():
        for gfx in root.glob("interface/**/*.gfx") if root.is_dir() else []:
            text = gfx.read_text(encoding="utf-8-sig", errors="ignore")
            for name, texture in re.findall(r'name\s*=\s*"?(GFX_\w+)"?\s*texture[fF]ile\s*=\s*"([^"]+)"', text):
                if name in DLC_SPRITES:
                    found[name] = root / texture
    out = []
    (folder / "dlc").mkdir(exist_ok=True)
    for name in DLC_SPRITES:
        source = found.get(name)
        if not source or not source.exists():
            print(f"skipped {name}: not found in the game's DLC folders")
            continue
        shutil.copyfile(source, folder / "dlc" / source.name)
        out.append(f'\tspriteType = {{\n\t\tname = "{name}"\n\t\ttexturefile = "gfx/leaders/LR/dlc/{source.name}"\n\t}}\n')
    return out


def main():
    folder = MOD / "gfx" / "leaders" / "LR"
    folder.mkdir(parents=True, exist_ok=True)
    sprites = dlc_sprites(folder)
    sprite_of = dict(VANILLA)
    for character, art in PORTRAITS.items():
        if not (ART / f"{art}.png").exists():
            print(f"skipped {character}: put the picture at docs/art/{art}.png")
            continue
        sprite_of[character] = f"GFX_{art}"
        fit(Image.open(ART / f"{art}.png").convert("RGBA")).save(folder / f"{art}.dds")
        sprites.append(f'\tspriteType = {{\n\t\tname = "GFX_{art}"\n\t\ttexturefile = "gfx/leaders/LR/{art}.dds"\n\t}}\n')
    (MOD / "interface" / "lr_portraits.gfx").write_text("spriteTypes = {\n" + "".join(sprites) + "}\n", encoding="utf-8")

    done = set()
    for path in CHARACTER_FILES:
        text = path.read_text(encoding="utf-8")
        for character, sprite in sprite_of.items():
            block = re.search(rf"\t{character}=\{{.*?\n\t\}}\n", text, re.S)
            if block:
                text = text.replace(block.group(0), block.group(0).replace('"GFX_portrait_unknown"', f'"{sprite}"'))
                done.add(character)
        path.write_text(text, encoding="utf-8")
    missing = set(sprite_of) - done
    if missing:
        raise SystemExit(f"characters not found: {sorted(missing)}")
    print(f"OK: {len(sprite_of)} portraits")


if __name__ == "__main__":
    main()
