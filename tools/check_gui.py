"""Find elements that stick out of their window in the mod's .gui files: python tools/check_gui.py

The game clips a child to its containerWindowType, so anything past the window's right or bottom edge is cut off.
Sizes come from size, maxWidth/maxHeight, or the sprite's .dds header. Percent sizes and orientations other than
the top left are skipped: they depend on the screen.
"""
import re
import struct
from pathlib import Path

MOD = Path(__file__).resolve().parent.parent / "mod"
VANILLA = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV")


def parse(text):
    tokens = re.findall(r'"[^"]*"|[{}=]|[^\s{}="]+', re.sub(r"#.*", "", text))
    pos = 0

    def block():
        nonlocal pos
        items = []
        while pos < len(tokens):
            tok = tokens[pos]
            if tok == "}":
                pos += 1
                return items
            if pos + 1 < len(tokens) and tokens[pos + 1] == "=":
                pos += 2
                if tokens[pos] == "{":
                    pos += 1
                    items.append((tok, block()))
                else:
                    items.append((tok, tokens[pos].strip('"')))
                    pos += 1
            else:
                pos += 1
        return items
    return block()


def get(items, key):
    for k, v in items:
        if k == key:
            return v
    return None


def sprites():
    sizes = {}
    for base in [VANILLA / "interface", MOD / "interface"] + sorted(VANILLA.glob("dlc/*/interface")):
        for path in base.rglob("*.gfx"):
            text = path.read_text(encoding="utf-8-sig", errors="ignore")
            for m in re.finditer(r'name\s*=\s*"?(GFX_\w+)"?(.{0,400}?)texturefile\s*=\s*"([^"]+)"(.{0,200})', text, re.S | re.I):
                frames = re.search(r"noOfFrames\s*=\s*(\d+)", m.group(2) + m.group(4))
                for root in (MOD, VANILLA):
                    dds = root / m.group(3)
                    if dds.exists():
                        with dds.open("rb") as f:  # only the header: reading whole pictures took minutes
                            head = f.read(20)
                        if head[:4] == b"DDS ":
                            h, w = struct.unpack("<II", head[12:20])
                            sizes[m.group(1)] = (w // (int(frames.group(1)) if frames else 1), h)
                        break
    return sizes


SPRITES = sprites()


def number(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def extent(kind, items):
    size = get(items, "size")
    if isinstance(size, list):
        w, h = number(get(size, "width") or get(size, "x")), number(get(size, "height") or get(size, "y"))
        if w is not None and h is not None:
            return w, h
    if kind in ("instantTextBoxType", "textboxType"):
        return number(get(items, "maxWidth")), number(get(items, "maxHeight"))
    sprite = get(items, "spriteType") or get(items, "quadTextureSprite")
    if sprite and sprite.strip('"') in SPRITES:
        return SPRITES[sprite.strip('"')]
    return None, None


def walk(name, items, width, height, path, problems):
    for kind, child in items:
        if not isinstance(child, list) or kind in ("position", "size", "margin", "background", "scrollbartype"):
            continue
        orient = (get(child, "orientation") or "upper_left").lower()
        pos = get(child, "position")
        x = number(get(pos, "x")) if isinstance(pos, list) else 0
        y = number(get(pos, "y")) if isinstance(pos, list) else 0
        w, h = extent(kind, child)
        label = f"{path}/{get(child, 'name') or kind}"
        if orient == "upper_left" and None not in (x, y) and width and height:
            if w and x + w > width + 2:
                problems.append(f"{label}: right edge {x + w} > window width {width}")
            if h and y + h > height + 2:
                problems.append(f"{label}: bottom edge {y + h} > window height {height}")
            if x < -2 or y < -2:
                problems.append(f"{label}: starts outside at ({x}, {y})")
        if kind in ("containerWindowType", "windowType"):
            walk(name, child, w, h, label, problems)


# Overhangs the game handles itself: the event window's tileable midsection grows with its text.
ALLOWED = {"eventwindow.gui:EventWindow/midsection/Description"}


def check(path):
    problems = []
    tree = parse(path.read_text(encoding="utf-8-sig", errors="ignore"))
    for _, types in tree:
        if not isinstance(types, list):
            continue
        for kind, window in types:
            if kind in ("containerWindowType", "windowType"):
                w, h = extent(kind, window)
                walk(path.name, window, w, h, f"{path.name}:{get(window, 'name')}", problems)
    return problems


def main():
    problems = []
    for path in sorted((MOD / "interface").glob("*.gui")):
        found = check(path)
        # A file copied from the game keeps the game's own overhangs, which render fine; report only what the mod added.
        original = VANILLA / "interface" / path.name
        if original.exists():
            known = set(check(original))
            found = [p for p in found if p not in known]
        problems += [p for p in found if p.split(":", 1)[0] + ":" + p.split(":", 1)[1].split(":")[0] not in ALLOWED]
    print("\n".join(problems) if problems else "OK: nothing sticks out of its window")


if __name__ == "__main__":
    main()
