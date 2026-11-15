"""News event pictures from public-domain photographs: python tools/news_pictures.py [--fetch] [--sheet]

    --fetch   search Wikimedia Commons for each topic in TOPICS and download public-domain candidates into
              docs/art/news/candidates (needs the network; run it once, or when a topic changes)
    --sheet   draw docs/art/news/candidates/sheet.png: every topic's candidates side by side, to choose from
    (none)    turn the chosen picture of every topic into a 397x153 news picture, define its sprite and point the
              news events at it. tools/build_all.py runs this form; it needs no network.

The chosen candidate of a topic is CHOICE[key] (default 0). The source, author and licence of every picture used
are written to docs/art/news/CREDITS.md. Only public-domain or CC0 files are taken.
"""
import json
import time
import re
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw, ImageEnhance, ImageOps

import build_world as world

MOD = world.MOD
FOLDER = world.PROJECT / "docs" / "art" / "news"
CANDIDATES = FOLDER / "candidates"
SIZE = (397, 153)
AGENT = "LRModNewsArt/1.0 (hobby game mod)"
FREE = ("public domain", "pd", "cc0", "no restrictions")

# key: (Commons search, news events that show it)
TOPICS = {
    "paris_crowd": ("Front populaire 1936 manifestation Paris", ["lr_gnews.1", "lr_gnews.4", "lr_gnews.20"]),
    "barricade": ("Barricade Commune de Paris 1871", ["lr_gnews.19"]),
    "parliament": ("Palais Bourbon Chambre des députés", ["lr_gnews.5", "lr_news.3"]),
    "army_parade": ("défilé militaire Champs-Élysées 14 juillet 1930s", ["lr_gnews.2", "lr_gnews.6", "lr_news.2"]),
    "royal_guard": ("Garde républicaine Paris", ["lr_gnews.3"]),
    "petain": ("Maréchal Pétain portrait", ["lr_gnews.18"]),
    "mobilisation": ("mobilisation 1914 Paris", ["lr_gnews.7", "lr_gnews.8", "lr_gnews.9", "lr_gnews.10", "lr_world.106", "lr_world.110"]),
    "armistice": ("Compiègne armistice wagon 1918", ["lr_gnews.11", "lr_news.11"]),
    "kerensky": ("Kerensky 1917", ["lr_gnews.12", "lr_gnews.14"]),
    "ruhr": ("Ruhrbesetzung 1923", ["lr_gnews.13", "lr_news.10", "lr_news.14"]),
    "spanish_war": ("Spanish Civil War 1936 militia", ["lr_world.101", "lr_gnews.15", "lr_world.103"]),
    "japan_army": ("Japanese soldiers 1937", ["lr_world.105", "lr_gnews.16"]),
    "balkan_war": ("First Balkan War 1912 army", ["lr_world.107", "lr_world.112", "lr_world.113", "lr_world.114", "lr_world.115", "lr_gnews.17"]),
    "liberation": ("Liberation of Paris 1944 crowds Champs Elysees", ["lr_gnews.21"]),
    "treaty": ("Signing of Peace in the Hall of Mirrors", ["lr_gnews.30", "lr_gnews.31", "lr_world.111"]),
    "douala": ("Douala Cameroun 1930", ["lr_gnews.32"]),
    "algiers": ("Alger Casbah 1930", ["lr_news.1"]),
    "london": ("Westminster Palace London 1930s", ["lr_news.12", "lr_world.108"]),
    "ottawa": ("Ottawa Parliament Buildings", ["lr_news.13", "lr_america.101"]),
    "china_revolution": ("Wuchang Uprising revolutionary army 1911", ["lr_world.102"]),
    "continental": ("Washington Crossing the Delaware painting", ["lr_world.104", "lr_america.100"]),
    "winter_war": ("Winter War Finnish soldiers skis 1939", ["lr_world.109"]),
}
CHOICE = {"barricade": 2, "japan_army": 1, "treaty": 2, "ottawa": 1, "china_revolution": 1, "parliament": 2, "petain": 0, "armistice": 1, "kerensky": 1, "ruhr": 2, "balkan_war": 1, "algiers": 1}


def get(url):
    """One polite request: a pause first, and a longer one whenever Commons says it is busy (HTTP 429)."""
    for wait in (2, 15, 45, 90):
        time.sleep(wait)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": AGENT}), timeout=120) as reply:
                return reply.read()
        except urllib.error.HTTPError as error:
            if error.code != 429:
                raise
    raise SystemExit("Commons keeps refusing; try again later")


def api(params):
    return json.loads(get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({**params, "format": "json"})))


def fetch():
    CANDIDATES.mkdir(parents=True, exist_ok=True)
    index_path = CANDIDATES / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {}
    for key, (query, _) in TOPICS.items():
        if index.get(key) and "--refetch" not in sys.argv:
            continue  # already has candidates
        data = api({"action": "query", "generator": "search", "gsrsearch": f"{query} filetype:bitmap", "gsrnamespace": 6,
                    "gsrlimit": 30, "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": 1200,
                    "iiextmetadatafilter": "LicenseShortName|Artist|ImageDescription"})
        pages = sorted(data.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
        picked = []
        for page in pages:
            info = page["imageinfo"][0]
            meta = info.get("extmetadata", {})
            licence = meta.get("LicenseShortName", {}).get("value", "")
            if not any(word in licence.lower() for word in FREE):
                continue
            if info["width"] < 700 or info["width"] < info["height"] * 1.15:
                continue
            target = CANDIDATES / f"{key}_{len(picked)}.jpg"
            target.write_bytes(get(info.get("thumburl") or info["url"]))
            artist = re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", "")).strip()
            picked.append({"file": target.name, "title": page["title"], "page": info["descriptionurl"],
                           "licence": licence, "artist": artist})
            if len(picked) == 3:
                break
        index[key] = picked
        print(f"{key}: {len(picked)} candidates")
        index_path.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")


def newsprint(path):
    """Crop to the news frame and tone it like a 1930s newspaper photograph."""
    picture = Image.open(path).convert("L")
    picture = ImageOps.fit(picture, (SIZE[0] * 2, SIZE[1] * 2), Image.LANCZOS, centering=(0.5, 0.4))
    picture = ImageOps.autocontrast(picture, cutoff=1)
    picture = ImageEnhance.Contrast(picture).enhance(1.15).resize(SIZE, Image.LANCZOS)
    return ImageOps.colorize(picture, black=(28, 22, 16), white=(236, 226, 204)).convert("RGBA")


def sheet():
    index = json.loads((CANDIDATES / "index.json").read_text(encoding="utf-8"))
    rows = [(key, items) for key, items in index.items()]
    w, h = 300, 116
    out = Image.new("RGB", (160 + 3 * (w + 6), len(rows) * (h + 6)), (40, 40, 40))
    draw = ImageDraw.Draw(out)
    for y, (key, items) in enumerate(rows):
        draw.text((6, y * (h + 6) + h // 2), key, fill=(255, 255, 255))
        for x, item in enumerate(items):
            out.paste(newsprint(CANDIDATES / item["file"]).convert("RGB").resize((w, h)), (160 + x * (w + 6), y * (h + 6)))
    out.save(CANDIDATES / "sheet.png")


def apply():
    index_path = CANDIDATES / "index.json"
    if not index_path.exists():
        print("OK: no news pictures fetched yet (python tools/news_pictures.py --fetch)")
        return
    index = json.loads(index_path.read_text(encoding="utf-8"))
    folder = MOD / "gfx" / "event_pictures" / "lr_news"
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    sprites, credits, picture_of = [], ["# 뉴스 이벤트 사진 출처", "", "모두 위키미디어 공용의 퍼블릭 도메인(또는 CC0) 파일입니다.", ""], {}
    for key, (_, events) in TOPICS.items():
        items = index.get(key) or []
        if not items:
            continue
        item = items[min(CHOICE.get(key, 0), len(items) - 1)]
        newsprint(CANDIDATES / item["file"]).save(folder / f"{key}.dds")
        sprite = f"GFX_news_event_lr_{key}"
        sprites.append(f'\tspriteType = {{\n\t\tname = "{sprite}"\n\t\ttexturefile = "gfx/event_pictures/lr_news/{key}.dds"\n\t}}\n')
        credits.append(f"- `{key}` ({', '.join(events)}): [{item['title']}]({item['page']}), {item['artist'] or '작자 미상'}, {item['licence']}")
        for event in events:
            picture_of[event] = sprite
    (MOD / "interface" / "lr_news_pictures.gfx").write_text("spriteTypes = {\n" + "".join(sprites) + "}\n", encoding="utf-8")
    (FOLDER / "CREDITS.md").write_text("\n".join(credits) + "\n", encoding="utf-8")
    changed = 0
    for path in sorted((MOD / "events").glob("*.txt")):
        raw = path.read_bytes()
        bom = raw.startswith(b"\xef\xbb\xbf")
        text = raw.decode("utf-8-sig")

        def block(match):
            nonlocal changed
            sprite = picture_of.get(match.group(2))
            if not sprite:
                return match.group(0)
            changed += 1
            return re.sub(r"picture = GFX_\w+", f"picture = {sprite}", match.group(0), count=1)

        new = re.sub(r"(news_event = \{\s*id = ([\w.]+)\b.*?\n\})", block, text, flags=re.S)
        if new != text:
            path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + new.encode("utf-8"))
    print(f"OK: {len(sprites)} news pictures on {changed} news events")


if __name__ == "__main__":
    if "--fetch" in sys.argv:
        fetch()
    if "--sheet" in sys.argv:
        sheet()
    if not ({"--fetch", "--sheet"} & set(sys.argv)):
        apply()
