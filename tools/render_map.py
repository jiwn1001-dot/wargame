"""Draw the 1936 ownership the mod produces: python tools/render_map.py [out_dir]

Reads the vanilla province bitmap and state files, applies TRANSFERS from build_world.py,
and writes docs/map/<region>.png with a label for every country and state id.
"""
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_world as world

Image.MAX_IMAGE_PIXELS = None
VANILLA = world.VANILLA
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else world.PROJECT / "docs" / "map"
# Name -> (left, top, right, bottom) in province bitmap pixels.
REGIONS = {
    "europe": (2250, 280, 3350, 1130),
    "north_america": (250, 200, 1650, 1130),
    "south_america": (950, 950, 1850, 1850),
    "africa_middle_east": (2350, 750, 3750, 1800),
    "asia": (3400, 350, 4900, 1300),
}


def state_data():
    """Return state id -> (1936 owner, provinces), honouring dated 1936.1.1 transfers."""
    states = {}
    for path in (VANILLA / "history" / "states").glob("*.txt"):
        text = re.sub(r"#.*", "", path.read_text(encoding="utf-8-sig", errors="ignore"))
        state = re.search(r"\bid\s*=\s*(\d+)", text)
        owner = re.search(r"\bowner\s*=\s*(\w+)", text)
        provinces = re.search(r"provinces\s*=\s*\{([^}]*)\}", text)
        if not (state and owner and provinces):
            continue
        tag = owner.group(1)
        dated = re.search(r"\b1936\.1\.1\s*=\s*\{", text)
        if dated:
            moved = re.search(r"transfer_state_to\s*=\s*(\w+)", text[dated.end():dated.end() + 400])
            if moved:
                tag = moved.group(1)
        states[int(state.group(1))] = (tag, [int(p) for p in provinces.group(1).split()])
    return states


MOD_COLOURS = {}
_colours = world.MOD / "common" / "countries" / "colors.txt"
if _colours.exists():
    for _tag, _r, _g, _b in re.findall(r"(\w{3}) = \{\s*color = rgb \{ (\d+) (\d+) (\d+) \}", _colours.read_text(encoding="utf-8")):
        MOD_COLOURS[_tag] = (int(_r), int(_g), int(_b))


def colour(tag):
    if tag in MOD_COLOURS:
        return MOD_COLOURS[tag]
    seed = sum((i + 1) * ord(c) * 37 for i, c in enumerate(tag))
    return (70 + seed % 170, 70 + (seed * 7) % 170, 70 + (seed * 13) % 170)


def main():
    states = state_data()
    final = {state: owner for state, (owner, _) in states.items()}
    for tag, moved in world.TRANSFERS.items():
        for state in moved:
            final[state] = tag

    province_rgb = {}
    with open(VANILLA / "map" / "definition.csv", encoding="latin-1") as handle:
        for line in handle:
            parts = line.split(";")
            if parts[0].isdigit() and int(parts[0]):
                province_rgb[int(parts[0])] = tuple(int(x) for x in parts[1:4])

    bitmap = np.asarray(Image.open(VANILLA / "map" / "provinces.bmp").convert("RGB")).astype(np.uint32)
    keys = (bitmap[..., 0] << 16) | (bitmap[..., 1] << 8) | bitmap[..., 2]
    state_ids = np.zeros(keys.shape, dtype=np.int32)
    uniques, inverse = np.unique(keys, return_inverse=True)
    lookup = {}
    for state, (_, provinces) in states.items():
        for province in provinces:
            if province in province_rgb:
                r, g, b = province_rgb[province]
                lookup[(r << 16) | (g << 8) | b] = state
    mapped = np.array([lookup.get(int(u), 0) for u in uniques], dtype=np.int32)
    state_ids = mapped[inverse].reshape(keys.shape)

    ids = np.unique(state_ids)
    palette = np.zeros((int(ids.max()) + 1, 3), dtype=np.uint8)
    palette[0] = (24, 34, 52)
    for state in ids:
        if state:
            palette[state] = colour(final[int(state)])
    picture = palette[state_ids]
    edges = (state_ids[1:, 1:] != state_ids[:-1, 1:]) | (state_ids[1:, 1:] != state_ids[1:, :-1])
    picture[1:, 1:][edges] = picture[1:, 1:][edges] * 3 // 4

    OUT.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    height = state_ids.shape[0]
    for name, (left, top, right, bottom) in REGIONS.items():
        # The bitmap is stored bottom-up relative to in-game y, but PIL already gives image order.
        crop = Image.fromarray(picture[top:bottom, left:right]).resize(((right - left) * 2, (bottom - top) * 2), Image.NEAREST)
        draw = ImageDraw.Draw(crop)
        window = state_ids[top:bottom, left:right]
        for state in np.unique(window):
            if not state:
                continue
            ys, xs = np.nonzero(window == state)
            if len(xs) < 25:
                continue
            x, y = int(xs.mean()) * 2, int(ys.mean()) * 2
            label = f"{final[int(state)]}\n{state}"
            draw.multiline_text((x - 10, y - 10), label, fill=(255, 255, 255), font=font, align="center",
                                stroke_width=1, stroke_fill=(0, 0, 0))
        crop.save(OUT / f"{name}.png")
    print(f"wrote {len(REGIONS)} maps to {OUT} (bitmap height {height})")


if __name__ == "__main__":
    main()
