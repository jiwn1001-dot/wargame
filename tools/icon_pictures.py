"""Focus icons and national spirit pictures from public-domain photographs: python tools/icon_pictures.py [--fetch]

    --fetch   search Wikimedia Commons for every focus and spirit in docs/art/icon_worklist.csv that has no picture of
              its own and download one public-domain or CC0 photograph each into docs/art/auto/sources (needs the
              network; resumable: what is already downloaded is kept). --refetch ID ... downloads those again.
    (none)    turn every downloaded photograph into an icon: docs/art/auto/goals/<focus>.png (a toned photograph in a
              brass medallion) and docs/art/auto/ideas/<spirit>.png (a toned framed picture). custom_icons.py uses them
              for every focus and spirit without a picture of its own in docs/art/goals or docs/art/ideas.
    --sheet   draw docs/art/auto/sheet_<n>.png: the made icons with their focus names, to look over.

Search words come from the focus id (LR_NAP_civil_code: "civil code"), then from the vanilla icon it shows now (its
theme: war, factory, treaty ...) and its route. A photograph is used once, so focuses of one theme still differ.
Only files Commons marks public domain or CC0 are taken; docs/art/auto/CREDITS.md lists source, author and licence.
"""
import csv
import json
from pathlib import Path

import numpy as np
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

import custom_icons as icons

ART = icons.ART
AUTO = ART / "auto"
SOURCES = AUTO / "sources"
INDEX = SOURCES / "index.json"
AGENT = "LRModIconArt/1.0 (hobby game mod)"
FREE = ("public domain", "pd", "cc0", "no restrictions")
PAGE_WORDS = ("page", "letter", "manuscript", "text", "newspaper", "document", "journal", "book", "pdf", "map of", "location map", "coin", "stamp", "diagram", "chart", "logo", "disney", "screenshot")
SKIP_WORDS = {"lr", "fra", "the", "of", "a", "an", "to", "and", "dyn", "ruler", "regime", "idea", "spirit"}

# Route prefix -> words that place a search in that route's world.
ROUTE_WORDS = {
    "ORL": "French monarchy", "BOU": "Bourbon king", "PET": "Pétain", "NAP": "Napoleon", "GUA": "French Republic",
    "RED": "communist France", "JAC": "French Revolution", "GIR": "French Republic", "MAR": "Third Republic",
    "COM": "Paris Commune", "ANA": "anarchist", "DEF": "occupied France", "FRA": "France 1930s",
}
# The vanilla icon a focus shows now -> a search for its theme.
THEMES = {
    "goal_generic_major_war": "French infantry 1914", "goal_generic_national_unity": "French tricolour crowd",
    "goal_generic_political_pressure": "police 1930s Paris", "goal_generic_propaganda": "French poster 1930s",
    "goal_generic_improve_relations": "diplomats 1930s", "goal_generic_major_alliance": "treaty signing 1920s",
    "goal_generic_demand_territory": "map Europe 1919", "goal_generic_construct_civilian": "construction workers 1930s",
    "goal_generic_army_doctrines": "French army officers", "goal_generic_allies_build_infantry": "infantry soldiers 1918",
    "goal_generic_occupy_start_war": "troops marching 1930s", "goal_generic_military_sphere": "military parade 1930s",
    "goal_generic_navy_doctrines_tactics": "French navy battleship", "goal_generic_positive_trade_relations": "cargo ship port 1930s",
    "goal_generic_trade": "stock exchange Paris", "goal_generic_special_forces": "chasseurs alpins",
    "goal_generic_scientific_exchange": "laboratory 1930s", "goal_generic_construct_civ_factory": "factory 1930s",
    "goal_generic_fortify_city": "Maginot line", "goal_generic_forceful_treaty": "Treaty of Versailles",
    "goal_generic_construct_mil_factory": "munitions factory", "goal_generic_alliance": "handshake treaty",
    "goal_generic_production": "assembly line 1930s", "goal_generic_military_deal": "generals 1930s",
    "goal_generic_intelligence_exchange": "radio operator 1930s", "goal_generic_dangerous_deal": "secret meeting",
    "goal_generic_construct_naval_dockyard": "shipyard 1930s", "goal_generic_army_artillery": "French artillery 1918",
    "goal_generic_small_arms": "rifle 1918", "goal_generic_army_motorized": "military trucks 1930s",
    "goal_generic_air_bomber": "bomber aircraft 1930s", "goal_generic_radar": "radar 1940",
    "goal_generic_navy_submarine": "submarine 1930s", "goal_generic_construction": "road construction 1930s",
    "goal_generic_construct_infrastructure": "railway locomotive France", "goal_generic_army_tanks": "tank 1930s",
    "goal_generic_air_fighter": "fighter aircraft 1930s", "goal_generic_air_doctrine": "airfield 1930s",
}
GOAL_SIZE = 190   # drawn at twice the icon size; custom_icons fits it to 95
IDEA_SIZE = (120, 136)


def get(url):
    """One polite request, with longer pauses whenever Commons says it is busy (HTTP 429)."""
    for wait in (1, 15, 45, 90):
        time.sleep(wait)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": AGENT}), timeout=120) as reply:
                return reply.read()
        except urllib.error.HTTPError as error:
            if error.code != 429:
                raise
    raise SystemExit("Commons keeps refusing; try again later")


def search(query):
    params = {"action": "query", "generator": "search", "gsrsearch": f"{query} filemime:image/jpeg", "gsrnamespace": 6,
              "gsrlimit": 20, "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": 400,
              "iiextmetadatafilter": "LicenseShortName|Artist", "format": "json"}
    data = json.loads(get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)))
    return sorted(data.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))


def rows():
    """Focuses and spirits still without a picture of their own: (kind, id, route code, name, vanilla icon)."""
    codes = {name: code for code, name in icons.ROUTES.items()}
    with open(ART / "icon_worklist.csv", encoding="utf-8-sig") as source:
        for row in csv.DictReader(source):
            kind = "goal" if row["종류"] == "중점" else "idea"
            folder = "goals" if kind == "goal" else "ideas"
            if any((ART / folder / f"{row['ID']}{ext}").exists() for ext in icons.EXTENSIONS):
                continue
            if hand_made(row["지금 아이콘"]):
                continue
            yield kind, row["ID"], codes.get(row["루트"], "FRA"), row["이름"], row["지금 아이콘"]


def hand_made(icon):
    """The mod's own drawn icons (docs/art/goal_*.png, sprites GFX_goal_LR_*): never replaced by a photograph."""
    return "_LR_" in f"_{icon}" or icon.startswith(("goal_LR", "GFX_goal_LR", "GFX_idea_LR", "idea_LR"))


def words_of(item_id):
    parts = [w for w in re.split(r"_+", item_id) if w]
    parts = [w for w in parts if w.lower() not in SKIP_WORDS and not (w.isupper() and len(w) == 3)]
    return " ".join(parts)


def queries(kind, item_id, code, icon):
    words = words_of(item_id)
    route = ROUTE_WORDS.get(code, "France 1930s")
    out = []
    if words:
        out += [f"{words} France", words]
    theme = THEMES.get(icon)
    if theme:
        out += [f"{theme} {route}", theme]
    out.append(route)
    return out


def fetch():
    SOURCES.mkdir(parents=True, exist_ok=True)
    index = json.loads(INDEX.read_text(encoding="utf-8")) if INDEX.exists() else {}
    redo = set(sys.argv[sys.argv.index("--refetch") + 1:]) if "--refetch" in sys.argv else set()
    used = {entry["title"] for key, entry in index.items() if key not in redo}
    todo = [r for r in rows() if r[1] not in index or r[1] in redo]
    print(f"{len(todo)} pictures to find")
    for number, (kind, item_id, code, name, icon) in enumerate(todo, start=1):
        found = None
        for query in queries(kind, item_id, code, icon):
            try:
                pages = search(query)
            except Exception as error:  # a broken query should not stop the run
                print(f"  {item_id}: search failed ({error})")
                continue
            for page in pages:
                info = (page.get("imageinfo") or [{}])[0]
                meta = info.get("extmetadata", {})
                licence = meta.get("LicenseShortName", {}).get("value", "")
                if page["title"] in used or not any(w in licence.lower() for w in FREE):
                    continue
                if any(w in page["title"].lower() for w in PAGE_WORDS):
                    continue  # scanned pages and letters make poor icons
                if info.get("width", 0) < 250 or info.get("height", 0) < 200:
                    continue
                found = (page, info, licence, re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", "")).strip(), query)
                break
            if found:
                break
        if not found:
            print(f"[{number}/{len(todo)}] {item_id}: nothing free found")
            continue
        page, info, licence, artist, query = found
        target = SOURCES / f"{item_id}.jpg"
        try:
            target.write_bytes(get(info.get("thumburl") or info["url"]))
        except Exception as error:
            print(f"  {item_id}: download failed ({error})")
            continue
        used.add(page["title"])
        index[item_id] = {"kind": kind, "name": name, "title": page["title"], "page": info.get("descriptionurl", ""),
                          "licence": licence, "artist": artist, "query": query}
        INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"[{number}/{len(todo)}] {item_id}: {page['title']} ({query})", flush=True)


def tone(picture):
    """A 1930s look: grey, then dark navy to warm parchment, with some contrast."""
    grey = ImageOps.autocontrast(ImageOps.grayscale(picture), cutoff=2)
    return ImageOps.colorize(grey, black=(28, 30, 40), mid=(122, 106, 84), white=(236, 222, 190))


def square(picture, size):
    side = min(picture.size)
    left, top = (picture.width - side) // 2, max(0, (picture.height - side) // 3)
    return picture.crop((left, top, left + side, top + side)).resize((size, size), Image.LANCZOS)


# The frame of the mod's own drawn icons (chain ring, navy disc, purple laurel): the median of those icons, so the
# photographs sit in the same badge (tools/icon_frame_median.png). The disc's centre and radius on that 95-pixel frame.
FRAME = Path(__file__).resolve().parent / "icon_frame_median.png"
DISC = (48, 47, 26)
RED_ROUTES = {"COM", "ANA", "RED"}  # like the mod's red revolution icons


def medallion(path, code="FRA"):
    """The photograph engraved in silver on the navy disc of the mod's own badge: bright parts silver, dark parts let
    the disc show through, as the drawn icons put silver objects on navy. Red routes are engraved in red."""
    scale = 2
    s = 95 * scale
    frame = Image.open(FRAME).convert("RGBA").resize((s, s), Image.LANCZOS)
    cx, cy, r = (v * scale for v in DISC)
    photo = square(Image.open(path).convert("RGB"), 2 * r)
    grey = ImageOps.autocontrast(ImageOps.grayscale(photo), cutoff=3)
    if np.asarray(grey).mean() > 140:
        grey = ImageOps.invert(grey)  # a print or a drawing on pale paper: its dark lines become the silver
    if code in RED_ROUTES:
        ink = ImageOps.colorize(grey, black=(60, 6, 6), mid=(150, 32, 26), white=(236, 160, 128))
    else:
        ink = ImageOps.colorize(grey, black=(40, 44, 60), mid=(150, 152, 162), white=(242, 242, 246))
    # Bright parts stay, dark parts fade into the disc.
    alpha = grey.point(lambda v: int(min(230, max(0, (v - 60) * 1.6))))
    disc = Image.new("L", (2 * r, 2 * r), 0)
    ImageDraw.Draw(disc).ellipse((2, 2, 2 * r - 2, 2 * r - 2), fill=255)
    disc = disc.filter(ImageFilter.GaussianBlur(2))
    alpha = Image.fromarray(((np.asarray(alpha).astype(float) * np.asarray(disc).astype(float)) / 255).astype("uint8"))
    ink = ink.convert("RGBA")
    ink.putalpha(alpha)
    out = frame.copy()
    out.alpha_composite(ink, (cx - r, cy - r))
    # A soft shade along the disc's upper rim, as on the drawn icons.
    rim = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(rim).ellipse((cx - r, cy - r, cx + r, cy + r), outline=(10, 12, 24, 160), width=3 * scale)
    out.alpha_composite(rim.filter(ImageFilter.GaussianBlur(scale)))
    return out


def framed(path):
    """A toned picture in a thin dark frame, the shape of a national spirit."""
    w, h = IDEA_SIZE
    picture = Image.open(path).convert("RGB")
    ratio = w / h
    if picture.width / picture.height > ratio:
        nw = int(picture.height * ratio)
        picture = picture.crop(((picture.width - nw) // 2, 0, (picture.width - nw) // 2 + nw, picture.height))
    else:
        nh = int(picture.width / ratio)
        picture = picture.crop((0, 0, picture.width, nh))
    out = tone(picture.resize((w, h), Image.LANCZOS)).convert("RGBA")
    edge = ImageDraw.Draw(out)
    edge.rectangle((0, 0, w - 1, h - 1), outline=(40, 32, 20, 255), width=4)
    edge.rectangle((4, 4, w - 5, h - 5), outline=(176, 146, 84, 255), width=2)
    return out


def make():
    index = json.loads(INDEX.read_text(encoding="utf-8")) if INDEX.exists() else {}
    for sub in ("goals", "ideas"):
        (AUTO / sub).mkdir(parents=True, exist_ok=True)
        for old in (AUTO / sub).glob("*.png"):
            old.unlink()
    still_open = {item_id for _, item_id, _, _, _ in rows()}  # not drawn by hand, here or in docs/art
    made = 0
    credits = ["# 자동 아이콘 출처", "", "`tools/icon_pictures.py`가 만드는 목록입니다. 모두 위키미디어 공용의 퍼블릭 도메인 또는 CC0 파일입니다.", "",
               "| 아이콘 | 이름 | 원본 | 작가 | 라이선스 |", "|---|---|---|---|---|"]
    for item_id, entry in sorted(index.items()):
        source = SOURCES / f"{item_id}.jpg"
        if not source.exists() or item_id not in still_open:
            continue
        # A picture of its own (docs/art/goals, docs/art/ideas) wins; none is made for it then.
        folder = "goals" if entry["kind"] == "goal" else "ideas"
        if any((ART / folder / f"{item_id}{ext}").exists() for ext in icons.EXTENSIONS):
            continue
        try:
            picture = medallion(source, item_id[3:6])  # spirits wear the same round badge as focuses
        except Exception as error:
            print(f"  {item_id}: {error}")
            continue
        picture.save(AUTO / folder / f"{item_id}.png")
        made += 1
        artist = (entry["artist"] or "?").replace("|", "/")[:60]
        credits.append(f"| {item_id} | {entry['name']} | [{entry['title']}]({entry['page']}) | {artist} | {entry['licence']} |")
    (AUTO / "CREDITS.md").write_text("\n".join(credits) + "\n", encoding="utf-8")
    print(f"OK: {made} automatic icons from public-domain photographs")


def sheet():
    index = json.loads(INDEX.read_text(encoding="utf-8")) if INDEX.exists() else {}
    files = sorted((AUTO / "goals").glob("*.png"))
    try:
        font = ImageFont.truetype("malgun.ttf", 13)
    except OSError:
        font = ImageFont.load_default()
    per, cols, cell = 60, 10, (150, 140)
    for n in range(0, len(files), per):
        page = Image.new("RGB", (cols * cell[0], ((min(per, len(files) - n) + cols - 1) // cols) * cell[1]), (32, 34, 40))
        for i, path in enumerate(files[n:n + per]):
            x, y = (i % cols) * cell[0], (i // cols) * cell[1]
            icon = Image.open(path).resize((95, 95), Image.LANCZOS)
            page.paste(icon, (x + 27, y + 4), icon)
            ImageDraw.Draw(page).text((x + 4, y + 104), index.get(path.stem, {}).get("name", path.stem)[:11], fill=(230, 225, 210), font=font)
        page.save(AUTO / f"sheet_{n // per + 1}.png")
    print(f"OK: {(len(files) + per - 1) // per} sheets")


if __name__ == "__main__":
    if "--fetch" in sys.argv or "--refetch" in sys.argv:
        fetch()
    elif "--sheet" in sys.argv:
        sheet()
    else:
        make()
