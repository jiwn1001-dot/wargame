"""Draw France's focus tree: python tools/render_tree.py [out.png]

Reads the generated tree and Korean names, and reports any focuses closer than a name's width.
Hidden Napoleon routes are drawn too, in a muted colour.
"""
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT = Path(__file__).resolve().parent.parent
ARGS = [a for a in sys.argv[1:] if not a.startswith("--route=")]
# --route=LR_route_a,LR_route_b draws only the shared focuses and those routes: what a player on that route sees.
ROUTES = next((a.split("=", 1)[1].split(",") for a in sys.argv[1:] if a.startswith("--route=")), None)
OUT = Path(ARGS[0]) if ARGS else PROJECT / "docs" / "map" / "france_tree.png"
CELL_W, CELL_H = 52, 60

text = (PROJECT / "mod" / "common" / "national_focus" / "france.txt").read_text(encoding="utf-8")
loc = (PROJECT / "mod" / "localisation" / "korean" / "lr_france_focus_l_korean.yml").read_text(encoding="utf-8-sig")
names = dict(re.findall(r'^ (\w+):0 "([^"]*)"', loc, re.M))

focuses = {}
for block in re.split(r"\n\tfocus = \{", text)[1:]:
    fid = re.search(r"id = (\w+)", block).group(1)
    focuses[fid] = {
        "x": int(re.search(r"\bx = (\d+)", block).group(1)),
        "y": int(re.search(r"\by = (\d+)", block).group(1)),
        "pre": re.findall(r"focus = (\w+)", " ".join(re.findall(r"prerequisite = \{([^}]*)\}", block))),
        "hidden": (re.search(r"allow_branch = \{ has_country_flag = (\w+)", block) or [None, None])[1],
    }

if ROUTES:
    focuses = {f: v for f, v in focuses.items() if v["hidden"] is None or v["hidden"] in ROUTES}
    for v in focuses.values():
        v["pre"] = [p for p in v["pre"] if p in focuses]

clashes = []
items = list(focuses.items())
for i, (a, fa) in enumerate(items):
    for b, fb in items[i + 1:]:
        if fa["y"] == fb["y"] and abs(fa["x"] - fb["x"]) < 2 and fa["hidden"] == fb["hidden"]:
            clashes.append((a, b))

width = (max(f["x"] for f in focuses.values()) + 3) * CELL_W
height = (max(f["y"] for f in focuses.values()) + 2) * CELL_H
image = Image.new("RGB", (width, height), (22, 22, 24))
draw = ImageDraw.Draw(image)
font = ImageFont.truetype(r"C:\Windows\Fonts\NotoSansKR-VF.ttf", 12)


def point(focus):
    return (focus["x"] + 1) * CELL_W, (focus["y"] + 1) * CELL_H - 20


crossed = []
for fid, focus in focuses.items():
    for name in focus["pre"]:
        parent = focuses[name]
        px, py = point(parent)
        x, y = point(focus)
        bend = py + CELL_H // 2
        draw.line([(px, py), (px, bend), (x, bend), (x, y)], fill=(70, 90, 120), width=1)
        # Whatever stands in the way of the long drop to the child.
        for other_id, other in focuses.items():
            if other_id not in (fid, name) and other["hidden"] == focus["hidden"] and abs(other["x"] - focus["x"]) < 2 and parent["y"] < other["y"] < focus["y"]:
                crossed.append((name, fid, other_id))
for fid, focus in focuses.items():
    x, y = point(focus)
    fill = (45, 45, 60) if focus["hidden"] else (70, 60, 40)
    draw.rectangle((x - 48, y - 12, x + 48, y + 12), fill=fill, outline=(180, 170, 140))
    draw.text((x, y), names.get(fid, fid)[:9], font=font, fill=(235, 235, 235), anchor="mm")

OUT.parent.mkdir(parents=True, exist_ok=True)
image.save(OUT)
print(f"{len(focuses)} focuses, {width}x{height}px, too close: {clashes[:10]}, lines through focuses: {crossed[:12]} ({len(crossed)})")
