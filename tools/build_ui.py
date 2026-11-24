"""Empire skin for the game UI (imperial navy, gilt and parchment, the Napoleonic style), and a serif title font.

Textures: the vanilla frames, backgrounds, buttons and bars of the main screens are recoloured into black, bronze
and gold with a gradient map. Shapes and sizes stay the same, so every vanilla layout still fits. Icons, flags,
portraits, pictures and counters are left alone. Saturated pixels (status colours) keep part of their colour.

Font: the Korean title fonts (hoi_24header, hoi_30header, hoi_36header, vic_22, vic_36) are re-baked from
Hahmlet (docs/fonts/hahmlet, OFL) with the same character set and similar metrics, under the same file names, so
every title in the game changes and nothing else does.

Run after build_super.py. Writes mod/gfx/interface/..., mod/gfx/fonts/korean/... and docs/ui/preview.png.
"""
import colorsys
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_world as world  # noqa: E402

VANILLA, MOD, PROJECT = world.VANILLA, world.MOD, world.PROJECT
GI = VANILLA / "gfx" / "interface"
FONT_FILE = PROJECT / "docs" / "fonts" / "hahmlet" / "Hahmlet.ttf"
# Country names on the map: Song Myung (OFL), a brush-stroke serif. Glyphs it lacks come from Hahmlet Bold.
MAP_FONT_FILE = PROJECT / "docs" / "fonts" / "songmyung" / "SongMyung-Regular.ttf"
FACES = {"hoi_mapfont4": MAP_FONT_FILE}

# ===== Palette: the Empire style - imperial navy, gilt, parchment (2026-11-24, replacing the Art Deco skin) =====
# Frames: deep navy shadows and mid-tones like the throne rooms of the First Empire, gilt on the bright bevels.
# Each stop keeps about the brightness of the vanilla pixel it replaces, so borders and button states stay readable.
STOPS = [(0.0, (6, 9, 20)), (0.15, (16, 24, 48)), (0.3, (30, 42, 78)), (0.45, (58, 68, 104)), (0.6, (142, 118, 76)), (0.75, (202, 170, 104)),
         (0.88, (236, 210, 146)), (1.0, (255, 246, 218))]
# Paper (event reports, news): warm parchment, so the black body text stays readable; dark frame parts turn navy and sepia.
PAPER_STOPS = [(0.0, (12, 14, 24)), (0.3, (48, 40, 32)), (0.55, (168, 136, 86)), (0.7, (228, 210, 172)), (1.0, (248, 238, 214))]
PAPER = re.compile(r"(event_report|event_news_bg|news_bg|report_.*win|paper|focus_popup_bg)", re.I)
GOLD_RULE = (214, 178, 96, 255)
FOLDERS = ["", "tiles", "topbar", "topbar/toolbar", "decisionview", "decisions", "focusview", "focusview/titlebar", "diplomacy", "production",
           "construction", "trade", "tradeview", "politics", "research", "logistics", "occupation"]
INCLUDE = re.compile(r"(bg|background|window|win\b|_win|frame|button|btn|tab|topbar|panel|tile|tiled|header|tooltip|scroll|slider|checkbox|border|box|plate|banner|divider|separator|listbox|option_entry|midsection)", re.I)
EXCLUDE = re.compile(r"(icon|flag|portrait|goal|idea|trait|medal|unit_|equipment|tech_|map|pip|strip|ledger_|loadingscreen|leader|faction_|achievement|decision_icon|event_pic|pic_clip|pic_overlay|news_pic|report_event|ribbon|insignia|silhouette|shine|glow|arrow|cursor|logo|symbol|counters|career_profile|profile_backgrounds|country_selection|browser|matchmaking|ladder|lr_)", re.I)
EXTRA = ["event_report_top_win.dds", "event_report_bottom_win.dds", "event_report_bottom_win_2.dds", "event_report_tileable_midsection.dds",
         "event_option_entry.dds", "event_news_bg.dds", "focus_popup_bg.dds", "topbar/background.dds", "topbar/background_extended.dds"]


def gradient(value, stops=None):
    stops = stops or STOPS
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if value <= b:
            t = (value - a) / (b - a) if b > a else 0
            return tuple(round(ca[i] + (cb[i] - ca[i]) * t) for i in range(3))
    return stops[-1][1]


LUT = [gradient(min(1.0, i / 255 * 1.05)) for i in range(256)]
PAPER_LUT = [gradient(i / 255, PAPER_STOPS) for i in range(256)]


def recolour(image, lut=None):
    """Gradient-map the luminance; keep part of the colour where the pixel is strongly coloured."""
    lut = lut or LUT
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    w, h = rgba.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue
            lum = int(0.299 * r + 0.587 * g + 0.114 * b)
            mr, mg, mb = lut[lum]
            _, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            keep = max(0.0, min(1.0, (s - 0.35) * 2.2)) * (0.5 + 0.5 * v)
            pixels[x, y] = (round(mr + (r - mr) * keep), round(mg + (g - mg) * keep), round(mb + (b - mb) * keep), a)
    return rgba


def deco_frame(image):
    """A double gilt rule inside large panels with a rosette at each corner: the Empire signature."""
    w, h = image.size
    if w < 260 or h < 160:
        return image
    draw = ImageDraw.Draw(image)
    gold, dim = (214, 178, 96, 255), (120, 96, 52, 255)
    for inset, colour in ((9, gold), (13, dim)):
        draw.rectangle((inset, inset, w - 1 - inset, h - 1 - inset), outline=colour, width=1)
    for cx, cy in ((11, 11), (w - 12, 11), (11, h - 12), (w - 12, h - 12)):
        # A rosette: a gilt ring, a darker petal ring and a bright boss.
        draw.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=(14, 20, 40, 255), outline=gold, width=1)
        for angle in range(0, 360, 45):
            import math
            px, py = cx + 4 * math.cos(math.radians(angle)), cy + 4 * math.sin(math.radians(angle))
            draw.ellipse((px - 1.4, py - 1.4, px + 1.4, py + 1.4), fill=dim)
        draw.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=(240, 214, 150, 255))
    # A small gilt lozenge at the middle of the top and bottom rules.
    for my in (9, h - 10):
        draw.polygon([(w // 2, my - 4), (w // 2 + 6, my), (w // 2, my + 4), (w // 2 - 6, my)], fill=gold)
    return image


def gold_edges(image, inset_rule=False):
    """A one-pixel gold line where the texture meets transparency, and for window tiles an inner rule."""
    w, h = image.size
    alpha = image.getchannel("A").load()
    pixels = image.load()
    edge = []
    for y in range(h):
        for x in range(w):
            if alpha[x, y] < 128:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and alpha[nx, ny] < 64:
                    edge.append((x, y))
                    break
    for x, y in edge:
        pixels[x, y] = GOLD_RULE[:3] + (alpha[x, y],)
    if inset_rule and w >= 24 and h >= 24:
        draw = ImageDraw.Draw(image)
        draw.rectangle((4, 4, w - 5, h - 5), outline=(150, 120, 64, 255), width=1)
    return image


def targets():
    found = {}
    for folder in FOLDERS:
        directory = GI / folder
        if not directory.exists():
            continue
        for path in directory.glob("*"):
            if path.suffix.lower() in (".dds", ".tga", ".png") and INCLUDE.search(path.name) and not EXCLUDE.search(path.name):
                found[path.relative_to(GI)] = path
    for name in EXTRA:
        path = GI / name
        if path.exists():
            found[path.relative_to(GI)] = path
    return found


def save(image, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".dds":
        # Pillow's DXT3 writer breaks the alpha of every fourth pixel; DXT5 is sound. The topbar shader refuses
        # DXT5 ("forbidden compression"), so its textures are written uncompressed.
        if "topbar" in path.parts:
            image.save(path)
        else:
            image.save(path, pixel_format="DXT5")
    else:
        image.save(path)


def build_textures():
    done, failed = 0, []
    for rel, source in sorted(targets().items()):
        try:
            image = Image.open(source)
            image.load()
        except Exception as error:
            failed.append((str(rel), str(error)[:40]))
            continue
        paper = bool(PAPER.search(rel.name))
        skinned = recolour(image, PAPER_LUT if paper else LUT)
        tiled = "tiles" in rel.parts or rel.name.startswith("tiled")
        skinned = gold_edges(skinned, inset_rule=tiled and "window" in rel.name)
        if not tiled and not paper:
            skinned = deco_frame(skinned)
        save(skinned, MOD / "gfx" / "interface" / rel)
        done += 1
    return done, failed


# ===== Title font =====
# name: weight, glyph size (None: the vanilla size), atlas width. hoi_mapfont4 draws the country names on the map.
TITLE_FONTS = {"hoi_24header": ("ExtraBold", None, 2048), "hoi_30header": ("ExtraBold", None, 2048), "hoi_36header": ("Black", None, 2048),
               "vic_22": ("Bold", None, 2048), "vic_36": ("Black", None, 2048), "hoi_mapfont4": ("Bold", 60, 4096)}


def read_fnt(path):
    text = path.read_text(encoding="utf-8-sig", errors="ignore")
    common = dict(re.findall(r"(\w+)=(\S+)", re.search(r"^common .*$", text, re.M).group(0)))
    info = dict(re.findall(r"(\w+)=(\"[^\"]*\"|\S+)", re.search(r"^info .*$", text, re.M).group(0)))
    ids = [int(m) for m in re.findall(r"^char id=(\d+)", text, re.M)]
    return info, common, ids


def bake_font(name, weight, size_override=None, width=2048, spacing=1):
    """One bitmap font in the BMFont layout vanilla reads. Glyphs sit on the vanilla baseline."""
    from fontTools.ttLib import TTFont
    source = VANILLA / "gfx" / "fonts" / "korean" / f"{name}.fnt"
    info, common, ids = read_fnt(source)
    size = size_override or abs(int(info["size"]))
    line_height, base = int(common["lineHeight"]), int(common["base"])
    fallback = ImageFont.truetype(str(FONT_FILE), size)
    fallback.set_variation_by_name(weight)
    face_file = FACES.get(name)
    if face_file:
        primary = ImageFont.truetype(str(face_file), size)
        covered = set(TTFont(str(face_file)).getBestCmap())
    else:
        primary, covered = fallback, None
    pad = 3
    glyphs = []
    for cid in ids:
        ch = chr(cid)
        font = primary if covered is None or cid in covered else fallback
        box = font.getbbox(ch, anchor="ls")
        gw, gh = max(1, box[2] - box[0]), max(1, box[3] - box[1])
        glyphs.append((cid, ch, font, box, gw, gh, round(font.getlength(ch)) + spacing))
    x = y = row = 0
    places = []
    for cid, ch, font, box, gw, gh, adv in glyphs:
        if x + gw + pad > width:
            x, y, row = 0, y + row + pad, 0
        places.append((x, y))
        x += gw + pad
        row = max(row, gh)
    height = y + row + pad
    atlas = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(atlas)
    lines = []
    for (cid, ch, font, box, gw, gh, adv), (px, py) in zip(glyphs, places):
        draw.text((px - box[0], py - box[1]), ch, font=font, fill=(255, 255, 255, 255), anchor="ls")
        lines.append(f"char id={cid} x={px} y={py} width={gw} height={gh} xoffset={box[0]} yoffset={box[1] + base} xadvance={adv} page=0 chnl=15")
    face_name = "Song Myung" if face_file else f"Hahmlet {weight}"
    header = [f'info face="{face_name}" size={size} bold=1 italic=0 charset="" unicode=1 stretchH=100 smooth=1 aa=1 padding=0,0,0,0 spacing={pad},{pad} outline=0',
              f"common lineHeight={line_height} base={base} scaleW={width} scaleH={height} pages=1 packed=0 alphaChnl=1 redChnl=4 greenChnl=4 blueChnl=4",
              f'page id=0 file="{name}.dds"', f"chars count={len(lines)}"]
    folder = MOD / "gfx" / "fonts" / "korean"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{name}.fnt").write_text("\n".join(header + lines) + "\n", encoding="utf-8")
    atlas.save(folder / f"{name}.dds", pixel_format="DXT5")
    return len(lines)


# ===== Preview =====
def preview():
    samples = ["topbar/background.dds", "event_report_top_win.dds", "event_option_entry.dds", "button_type_1.dds", "tiles/tiled_window.dds"]
    cells = []
    for rel in samples:
        before, after = GI / rel, MOD / "gfx" / "interface" / rel
        if before.exists() and after.exists():
            cells.append((rel, Image.open(before).convert("RGBA"), Image.open(after).convert("RGBA")))
    width = 1400
    rows = []
    for rel, a, b in cells:
        scale = min(1.0, 640 / max(a.width, 1), 220 / max(a.height, 1))
        size = (max(1, int(a.width * scale)), max(1, int(a.height * scale)))
        rows.append((rel, a.resize(size), b.resize(size)))
    height = sum(r[1].height + 40 for r in rows) + 200
    sheet = Image.new("RGBA", (width, height), (32, 32, 36, 255))
    draw = ImageDraw.Draw(sheet)
    label = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 16)
    y = 10
    for rel, a, b in rows:
        draw.text((10, y), f"{rel}   (왼쪽 바닐라 / 오른쪽 엠파이어)", font=label, fill=(200, 200, 200, 255))
        sheet.alpha_composite(a, (10, y + 24))
        sheet.alpha_composite(b, (width // 2, y + 24))
        y += a.height + 40
    title = ImageFont.truetype(str(FONT_FILE), 40)
    title.set_variation_by_name("Black")
    draw.text((10, y + 20), "제목 글꼴: 함렛 Black · 프랑스 혁명 · 늦게 온 혁명", font=title, fill=(220, 186, 106, 255))
    out = PROJECT / "docs" / "ui" / "preview.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(out)
    return out


def restyle_own():
    """The super event frame and button that build_super.py draws: recoloured and framed like the rest."""
    folder = MOD / "gfx" / "interface" / "lr"
    done = 0
    for name, framed in (("lr_super_frame.dds", True), ("lr_super_button.dds", False)):
        path = folder / name
        if not path.exists():
            continue
        image = recolour(Image.open(path).convert("LA").convert("RGBA"))
        image = gold_edges(image)
        if framed:
            image = deco_frame(image)
        image.save(path, pixel_format="DXT5")
        done += 1
    return done


def main():
    count, failed = build_textures()
    count += restyle_own()
    glyphs = {name: bake_font(name, weight, size, width) for name, (weight, size, width) in TITLE_FONTS.items()}
    out = preview()
    print(f"OK: {count} UI textures re-skinned, {len(failed)} unreadable, title fonts {glyphs}, preview {out.name}")
    if failed:
        print("unreadable:", failed[:10])


if __name__ == "__main__":
    main()
