"""Leader portraits from public-domain photographs: python tools/leader_photos.py [--fetch] [--refetch ID...]

--fetch  finds a public-domain or CC0 photograph on Wikimedia Commons for every leader in LEADERS that has no
         picture of its own (docs/art/portrait_*.png, which always wins) and saves it to
         docs/art/auto/portraits/sources/<id>.jpg (resumable; --refetch ID... forgets those and fetches again).
(none)   makes docs/art/auto/portraits/<id>.png: the person cut out of the photograph (rembg) and set on one studio
         backdrop, toned alike, so every portrait looks like part of the same set. build_portraits.py uses them.
"""
import json
import sys
import time
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import icon_pictures as icons  # noqa: E402  the Commons search and download helpers

ART = Path(__file__).resolve().parent.parent / "docs" / "art"
OUT = ART / "auto" / "portraits"
SOURCES = OUT / "sources"
INDEX = SOURCES / "index.json"
SIZE = (156, 210)  # vanilla leader portraits

# Character id -> Commons search: France and America only for now (2026-11-25; China and the rest are still being
# written). Characters with a picture of their own in docs/art are left out on purpose: FRA_louis_xx,
# FRA_napoleon_bonaparte, LR_FRA_flandin (the user's art). Vanilla portraits are replaced by photographs too.
LEADERS = {
    # America
    "USA_george_washington": "George Washington Gilbert Stuart portrait",
    "LR_USA_hoover": "Herbert Hoover portrait",
    "LR_CNA_hull": "Cordell Hull",
    "LR_CNA_macarthur": "Douglas MacArthur 1930s",
    "LR_AMC_browder": "Earl Browder",
    "LR_LNG_long": "Huey Long",
    "LR_DXE_bilbo": "Theodore G. Bilbo",
    # France: leaders
    "FRA_leon_blum": "Léon Blum",
    "LR_FRA_orleans": "Jean d'Orléans duc de Guise",
    "FRA_philippe_petain": "Philippe Pétain portrait",
    "LR_FRA_besnard": "Pierre Besnard syndicaliste",
    "FRA_paul_reynaud": "Paul Reynaud",
    "FRA_maurice_thorez": "Maurice Thorez",
    "FRA_francois_darlan": "François Darlan amiral",
    "FRA_charles_de_gaulle": "Charles de Gaulle 1942",
    "FRA_pierre_laval": "Pierre Laval",
    "FRA_edouard_daladier": "Édouard Daladier",
    "FRA_denis_guillaumat": "Denis Guillaumat",
    "FRA_marcel_bucard": "Marcel Bucard",
    "FRA_marcel_deat": "Marcel Déat",
    "FRA_charles_maurras": "Charles Maurras",
    "FRA_jacques_duclos": "Jacques Duclos",
    # France: generals and admirals
    "FRA_jean_de_lattre_de_tassigny": "Jean de Lattre de Tassigny",
    "FRA_alphonse_juin": "Alphonse Juin",
    "FRA_maurice_gamelin": "Maurice Gamelin",
    "FRA_maxime_weygand": "Maxime Weygand",
    "FRA_alphonse_georges": "Alphonse Georges général",
    "FRA_antoinemariebenoit_besson": "Antoine Besson général",
    "FRA_philippe_leclerc": "Philippe Leclerc de Hauteclocque",
    "FRA_henri_giraud": "Henri Giraud général",
    "FRA_charles_huntziger": "Charles Huntziger",
    "FRA_gastonhenri_billotte": "Gaston Billotte",
    "FRA_henry_freydenberg": "Henry Freydenberg",
    "FRA_rene_olry": "René Olry",
    "FRA_jeanmarie_charles_abrial": "Jean-Marie Charles Abrial",
    "FRA_jeanpierre_esteva": "Jean-Pierre Esteva",
    "FRA_rene_emile_godfroy": "René-Émile Godfroy",
    "FRA_jean_de_laborde": "Jean de Laborde amiral",
    # France: scientists and designers
    "FRA_irene_joliot_curie": "Irène Joliot-Curie",
    "FRA_frederic_joliot_curie": "Frédéric Joliot-Curie",
    "FRA_louis_renault": "Louis Renault industriel",
    "FRA_eugene_schneider_ii": "Eugène Schneider II",
    "FRA_emile_rimailho": "Émile Rimailho",
}
# The same person under the mod's own character id: one photograph for both.
ALIAS = {"LR_FRA_blum": "FRA_leon_blum", "LR_FRA_petain": "FRA_philippe_petain", "LR_FRA_reynaud": "FRA_paul_reynaud",
         "LR_FRA_thorez": "FRA_maurice_thorez", "LR_FRA_darlan": "FRA_francois_darlan", "LR_FRA_degaulle": "FRA_charles_de_gaulle"}
# English Wikipedia article for each leader whose search above is not the article's own title. The article's lead
# picture is tried first (it is that person, and en.wikipedia.org answers when Commons' search is busy).
WIKI = {
    "USA_george_washington": "George Washington", "LR_USA_hoover": "Herbert Hoover", "LR_CNA_macarthur": "Douglas MacArthur",
    "LR_FRA_orleans": "Prince Jean, Duke of Guise", "FRA_philippe_petain": "Philippe Pétain", "LR_FRA_besnard": "Pierre Besnard",
    "FRA_francois_darlan": "François Darlan", "FRA_charles_de_gaulle": "Charles de Gaulle", "FRA_alphonse_georges": "Alphonse Joseph Georges",
    "FRA_antoinemariebenoit_besson": "Antoine Besson", "FRA_philippe_leclerc": "Philippe Leclerc de Hauteclocque",
    "FRA_henri_giraud": "Henri Giraud", "FRA_jean_de_laborde": "Jean de Laborde", "FRA_louis_renault": "Louis Renault (industrialist)",
    "FRA_eugene_schneider_ii": "Eugène II Schneider", "FRA_gastonhenri_billotte": "Gaston Billotte",
}


def wiki_lead(key, query):
    """The lead picture of the person's Wikipedia article, if it is free: (title, info, licence) or None."""
    import urllib.parse
    title = WIKI.get(key, query)
    for lang in ("en", "fr"):
        api = f"https://{lang}.wikipedia.org/w/api.php?"
        data = json.loads(icons.get(api + urllib.parse.urlencode(
            {"action": "query", "titles": title, "prop": "pageimages", "piprop": "name", "redirects": 1, "format": "json"})))
        name = next((pg.get("pageimage") for pg in data.get("query", {}).get("pages", {}).values() if pg.get("pageimage")), None)
        if not name:
            continue
        data = json.loads(icons.get(api + urllib.parse.urlencode(
            {"action": "query", "titles": f"File:{name}", "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": 600,
             "iiextmetadatafilter": "LicenseShortName|Artist", "format": "json"})))
        for pg in data.get("query", {}).get("pages", {}).values():
            info = (pg.get("imageinfo") or [{}])[0]
            licence = info.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "")
            if info and any(word in licence.lower() for word in icons.FREE):
                return {"title": f"File:{name}"}, info, licence
    return None


SKIP_TITLE = ("grave", "tomb", "statue", "monument", "house", "signature", "stamp", "coin", "family", "funeral", "map", "letter")


def fetch():
    SOURCES.mkdir(parents=True, exist_ok=True)
    index = json.loads(INDEX.read_text(encoding="utf-8")) if INDEX.exists() else {}
    for key in sys.argv[sys.argv.index("--refetch") + 1:] if "--refetch" in sys.argv else []:
        index.pop(key, None)
        (SOURCES / f"{key}.jpg").unlink(missing_ok=True)
    for key, query in LEADERS.items():
        if key in index and (SOURCES / f"{key}.jpg").exists():
            continue
        found = wiki_lead(key, query)
        try:
            pages = [] if found else icons.search(query)
        except SystemExit:  # Commons is busy: leave this one for the next run
            pages = []
        for page in pages:
            info = (page.get("imageinfo") or [{}])[0]
            meta = info.get("extmetadata", {})
            licence = meta.get("LicenseShortName", {}).get("value", "")
            title = page.get("title", "")
            if not any(word in licence.lower() for word in icons.FREE):
                continue
            if any(word in title.lower() for word in SKIP_TITLE + icons.PAGE_WORDS):
                continue
            if info.get("height", 0) < info.get("width", 1) * 0.9:  # a portrait stands upright
                continue
            found = (page, info, licence)
            break
        if not found:
            print(f"  {key}: nothing free found for '{query}'")
            continue
        page, info, licence = found
        (SOURCES / f"{key}.jpg").write_bytes(icons.get(info.get("thumburl") or info["url"]))
        artist = info.get("extmetadata", {}).get("Artist", {}).get("value", "")
        index[key] = {"title": page["title"], "page": info.get("descriptionurl", ""), "licence": licence, "artist": artist[:200]}
        INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  {key}: {page['title']}")
        time.sleep(1)
    print(f"OK: {len(index)} of {len(LEADERS)} leaders have a photograph")


def backdrop():
    """A studio backdrop in the mod's colours: midnight navy, lighter behind the head, darker at the corners."""
    w, h = SIZE[0] * 2, SIZE[1] * 2
    base = Image.new("RGB", (w, h), (18, 24, 44))
    glow = Image.new("L", (w, h), 0)
    ImageDraw.Draw(glow).ellipse((-w * 0.2, -h * 0.05, w * 1.2, h * 0.9), fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(w // 4))
    light = Image.new("RGB", (w, h), (70, 74, 96))
    return Image.composite(light, base, glow)


def tone(person):
    """Old-photograph tone: grey, a touch of warmth, firm contrast."""
    rgb, alpha = person.convert("RGB"), person.getchannel("A")
    grey = ImageOps.autocontrast(ImageOps.grayscale(rgb), cutoff=1)
    warm = ImageOps.colorize(grey, black=(20, 16, 14), mid=(130, 118, 102), white=(242, 234, 216))
    warm = ImageEnhance.Contrast(warm).enhance(1.1)
    out = warm.convert("RGBA")
    out.putalpha(alpha)
    return out


def portrait(path, session):
    from rembg import remove
    photo = Image.open(path).convert("RGB")
    photo.thumbnail((700, 700))
    cut = remove(photo, session=session)
    box = cut.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
    w, h = SIZE[0] * 2, SIZE[1] * 2
    canvas = backdrop().convert("RGBA")
    if not box or (box[2] - box[0]) * (box[3] - box[1]) < photo.width * photo.height * 0.08:
        # The cut found no clear person: use the photograph itself, toned, with soft edges.
        person = tone(photo.convert("RGBA"))
        person = ImageOps.fit(person, (w, h), centering=(0.5, 0.2))
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).rectangle((w * 0.06, h * 0.04, w * 0.94, h * 0.97), fill=255)
        person.putalpha(mask.filter(ImageFilter.GaussianBlur(14)))
        canvas.alpha_composite(person)
    else:
        person = tone(cut.crop(box))
        # Head and shoulders: the top of the figure fills the frame, the bottom runs off the edge.
        scale = w * 0.92 / person.width
        if person.height * scale < h * 0.95:
            scale = h * 0.95 / person.height
        person = person.resize((round(person.width * scale), round(person.height * scale)), Image.LANCZOS)
        x, y = (w - person.width) // 2, round(h * 0.08)
        shadow = Image.new("RGBA", person.size, (0, 0, 0, 0))
        shadow.putalpha(person.getchannel("A").point(lambda v: v * 0.55).filter(ImageFilter.GaussianBlur(10)))
        canvas.alpha_composite(shadow, (x + 6, y + 8))
        canvas.alpha_composite(person, (x, y))
    edge = ImageDraw.Draw(canvas)
    edge.rectangle((0, 0, w - 1, h - 1), outline=(176, 146, 84, 255), width=3)  # a hairline of gold, like the mod's frames
    return canvas.resize(SIZE, Image.LANCZOS)


def make():
    from rembg import new_session
    session = new_session("u2net")
    index = json.loads(INDEX.read_text(encoding="utf-8")) if INDEX.exists() else {}
    made = 0
    credits = ["# 자동 초상화 출처", "", "`tools/leader_photos.py`가 만드는 목록입니다. 모두 위키미디어 공용의 퍼블릭 도메인 또는 CC0 파일입니다.", "",
               "| 인물 | 원본 | 라이선스 |", "|---|---|---|"]
    for key in LEADERS:
        source = SOURCES / f"{key}.jpg"
        if not source.exists():
            continue
        target = OUT / f"{key}.png"
        if not target.exists() or target.stat().st_mtime < max(source.stat().st_mtime, Path(__file__).stat().st_mtime):
            portrait(source, session).save(target)
        made += 1
        entry = index.get(key, {})
        credits.append(f"| {key} | [{entry.get('title', '?')}]({entry.get('page', '')}) | {entry.get('licence', '?')} |")
    import shutil
    for alias, key in ALIAS.items():
        if (OUT / f"{key}.png").exists():
            shutil.copyfile(OUT / f"{key}.png", OUT / f"{alias}.png")
    for stale in OUT.glob("*.png"):  # people dropped from LEADERS (China, for now)
        if stale.stem not in LEADERS and stale.stem not in ALIAS:
            stale.unlink()
    (OUT / "CREDITS.md").write_text("\n".join(credits) + "\n", encoding="utf-8")
    print(f"OK: {made} leader portraits from public-domain photographs")


if __name__ == "__main__":
    fetch() if "--fetch" in sys.argv else make()
