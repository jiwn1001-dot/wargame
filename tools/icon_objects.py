"""Object photographs for the frameless icons: python tools/icon_objects.py [--limit N] [--redo]

A frameless cut-out (icon_pictures.exhibit) only looks good when the photograph shows one object on a plain ground,
the way a museum photographs its collection. This fetch replaces the picture of every open focus and spirit with
such a photograph: the focus's vanilla icon gives a theme, the theme gives object searches (helmets, sabres, medals,
ship models, inkwells...), and each candidate is cut out on the spot and kept only if the object stands clear of
its background (a fair share of the frame, and not running off more than one edge). Public domain and CC0 only,
each photograph used once. Resumable: items already fetched this way are skipped (--redo starts over).

Writes docs/art/auto/sources/<id>.jpg, the cut in docs/art/auto/cut/<id>.png, and marks the item "object" in the
index. Then run python tools/icon_pictures.py (make) and the build.
"""
import io
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import icon_pictures as I  # noqa: E402

M = " museum"
ROYAL = ["crown regalia" + M, "sceptre" + M, "fleur-de-lis object" + M, "royal crown jewel", "throne chair" + M]
EMPIRE = ["Napoleon bicorne hat", "imperial eagle standard Napoleon", "Napoleonic sword" + M, "Legion of Honour insignia", "Empire style clock" + M]
REVOLUTION = ["Phrygian cap", "tricolour cockade", "Marianne bust", "French Revolution object" + M, "pike head" + M]
RED = ["red flag banner" + M, "workers union banner", "hammer tool antique", "anvil antique", "sickle antique tool"]
DEFAULT_UNITY = ["Marianne bust", "bronze bust" + M, "French flag antique", "laurel wreath bronze", "standard bearer statuette"]
ROUTE_UNITY = {"ORL": ROYAL, "BOU": ROYAL, "PET": ["kepi" + M, "marshal baton", "Francisque badge", "military medal" + M, "oak leaves bronze"],
               "NAP": EMPIRE, "GUA": EMPIRE, "COM": RED, "ANA": RED, "RED": RED + EMPIRE[:2],
               "JAC": REVOLUTION, "GIR": REVOLUTION, "MAR": REVOLUTION}

THEMES = {
    "major_war": ["cavalry sabre" + M, "cuirassier helmet", "Adrian helmet", "bayonet" + M, "officer sword" + M, "military drum" + M, "cuirass armour" + M],
    "occupy_start_war": ["artillery shell" + M, "field gun model" + M, "cannon" + M, "trench helmet"],
    "demand_territory": ["antique globe" + M, "brass compass antique", "telescope antique" + M, "surveying instrument" + M],
    "forceful_treaty": ["seal matrix" + M, "wax seal antique", "inkwell" + M, "quill pen antique"],
    "political_pressure": ["inkwell" + M, "gavel antique", "seal matrix" + M, "quill pen antique", "desk set" + M],
    "propaganda": ["gramophone" + M, "megaphone antique", "microphone 1930s", "printing press model", "drum" + M],
    "improve_relations": ["Sevres porcelain vase", "porcelain vase" + M, "snuff box" + M, "pocket watch" + M, "fan" + M],
    "major_alliance": ["order insignia" + M, "Legion of Honour insignia", "medal" + M, "order of chivalry badge", "collar of order" + M],
    "alliance": ["medal" + M, "order insignia" + M, "badge enamel" + M],
    "military_deal": ["military medal" + M, "officer epaulette" + M, "order insignia" + M],
    "military_sphere": ["shako" + M, "military medal" + M, "officer helmet" + M, "gorget" + M],
    "dangerous_deal": ["dagger" + M, "pistol antique" + M, "key antique iron", "cipher device" + M],
    "intelligence_exchange": ["cipher machine" + M, "key antique iron", "binoculars antique", "pocket pistol" + M],
    "special_forces": ["dagger" + M, "trench knife", "pistol antique" + M],
    "construct_civilian": ["anvil antique", "steam engine model" + M, "gear wheel antique", "lathe antique"],
    "construct_civ_factory": ["steam engine model" + M, "gear wheel antique", "machine model" + M],
    "construct_mil_factory": ["artillery shell" + M, "rifle" + M, "cartridge" + M],
    "construction": ["trowel antique", "surveying instrument" + M, "hammer antique tool"],
    "production": ["anvil antique", "gear wheel antique", "steam engine model" + M],
    "construct_infrastructure": ["locomotive model" + M, "railway lantern antique", "railway signal lamp"],
    "construct_naval_dockyard": ["ship model" + M, "anchor" + M],
    "army_doctrines": ["kepi" + M, "officer epaulette" + M, "binoculars antique", "military map case" + M],
    "allies_build_infantry": ["Lebel rifle", "infantry helmet" + M, "soldier backpack" + M, "rifle" + M],
    "axis_build_infantry": ["rifle" + M, "infantry helmet" + M],
    "fortify_city": ["cannonball" + M, "fortress model" + M, "helmet" + M],
    "army_artillery": ["cannon" + M, "artillery shell" + M, "field gun model" + M],
    "army_artillery2": ["cannon" + M, "artillery shell" + M],
    "small_arms": ["rifle" + M, "revolver" + M, "pistol antique" + M],
    "army_motorized": ["toy truck antique", "car model" + M, "motorcycle antique"],
    "army_tanks": ["tank model" + M, "Renault FT tank"], "build_tank": ["tank model" + M, "Renault FT tank"],
    "navy_doctrines_tactics": ["ship model" + M, "sextant antique", "naval telescope", "anchor" + M],
    "navy_battleship": ["battleship model" + M], "navy_cruiser": ["cruiser model" + M], "navy_carrier": ["aircraft carrier model"],
    "navy_submarine": ["submarine model" + M], "navy_anti_submarine": ["depth charge" + M, "ship model" + M],
    "build_navy": ["ship model" + M, "anchor" + M],
    "air_doctrine": ["airplane model" + M, "propeller" + M, "aviator helmet" + M], "air_bomber": ["bomber model" + M, "aerial bomb" + M],
    "air_fighter": ["airplane model" + M, "aviator helmet" + M], "air_naval_bomber": ["seaplane model" + M], "air_production": ["propeller" + M],
    "build_airforce": ["airplane model" + M, "propeller" + M], "amphibious_assault": ["landing boat model", "anchor" + M],
    "radar": ["radio valve antique", "radio receiver 1930s"], "scientific_exchange": ["microscope antique", "telescope antique" + M, "scientific instrument" + M],
    "trade": ["balance scale antique", "merchant ship model", "money chest" + M], "positive_trade_relations": ["balance scale antique", "merchant ship model"],
    "oil_refinery": ["oil lamp antique", "oil can antique"],
    "central_management": ["ballot box antique", "inkwell" + M, "ledger desk" + M], "disjointed_gov": ["broken sculpture" + M, "ballot box antique"],
    "political_support": ["ballot box antique", "rosette ribbon"], "king_handled": ROYAL, "constitutional_guarantees": ["ballot box antique", "scales of justice statue"],
    "local_self_management": ["town hall bell", "ballot box antique"], "license_production": ["gear wheel antique"],
    "infantry_bonus": ["rifle" + M], "fortify_the_borders": ["helmet" + M, "cannonball" + M], "army_war_college": ["kepi" + M, "officer sword" + M],
    "navy_bonus": ["ship model" + M], "air_bonus": ["airplane model" + M], "artillery_regiments": ["cannon" + M], "armor": ["tank model" + M],
    "supply_line": ["military wagon model", "soldier backpack" + M], "sea_focused_navy": ["ship model" + M], "navy_submarines": ["submarine model" + M],
    "navy_carrier_bonus": ["aircraft carrier model"], "communist_army": RED, "foreign_capital": ["money chest" + M], "war_preparation": ["military drum" + M],
    "production_bonus": ["anvil antique"],
}
FALLBACK = ["antique object" + M, "bronze statuette" + M, "military object" + M]


GENERIC = {"museum", "antique", "model", "1930s", "object", "of", "the", "and", "tool", "french", "bronze", "military", "officer",
           "napoleon", "napoleonic", "imperial", "royal", "jewel", "style", "revolution", "workers", "union", "order", "aerial"}


def theme_of(icon):
    name = icon.replace("GFX_", "").replace("goal_generic_", "").replace("idea_generic_", "").replace("generic_", "")
    return name


def searches(code, icon):
    theme = theme_of(icon)
    if theme in ("national_unity", "neutrality_focus", "war_with_comintern") or theme not in THEMES:
        base = ROUTE_UNITY.get(code, DEFAULT_UNITY) if theme in ("national_unity", "neutrality_focus") else []
        return base + THEMES.get(theme, []) + FALLBACK
    return THEMES[theme] + ROUTE_UNITY.get(code, DEFAULT_UNITY)[:2] + FALLBACK


CLEVELAND = "https://openaccess-api.clevelandart.org/api/artworks/?"
# The Cleveland Museum of Art's open access collection (CC0) photographs its objects on plain grounds: ideal cut-outs.
# Departments far from 1930s France are skipped so a focus does not end up with an Edo helmet.
FAR = ("African", "Chinese", "Japanese", "Korean", "Indian", "Southeast Asian", "Ancient Americas", "Oceania", "Egyptian",
       "Near Eastern", "Islamic", "Medieval", "Greek", "Roman")


def cleveland(term):
    """(title, image url, licence, page) for CC0 objects matching a search, European and American first."""
    import urllib.parse
    query = term.replace(" museum", "").replace(" antique", "").strip()
    params = urllib.parse.urlencode({"q": query, "has_image": 1, "cc0": 1, "limit": 40})
    try:
        data = json.loads(I.get(CLEVELAND + params))
    except Exception as error:
        print(f"  Cleveland search failed for {query}: {error}")
        return []
    out = []
    for art in data.get("data", []):
        if any(word in (art.get("department") or "") for word in FAR):
            continue
        url = ((art.get("images") or {}).get("web") or {}).get("url")
        if url:
            title = f"Cleveland {art.get('accession_number')}: {art.get('title')}"
            out.append((title, url, "CC0", art.get("url", "")))
    return out


PLACES = ("hall", "building", "house", "church", "castle", "street", "station", "view", "card", "barnsley", "panorama", "aerial view")


def commons(term):
    out = []
    for page in I.search(term):
        info = (page.get("imageinfo") or [{}])[0]
        licence = info.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "")
        title = page.get("title", "")
        if any(word in licence.lower() for word in I.FREE) and not any(w in title.lower() for w in I.PAGE_WORDS + PLACES):
            out.append((title, info.get("thumburl") or info["url"], licence, info.get("descriptionurl", "")))
    return out


def score(cut):
    """0 for a photograph whose object does not stand clear; more is better."""
    alpha = np.asarray(cut.getchannel("A")) > 60
    coverage = alpha.mean()
    if not 0.1 < coverage < 0.65:
        return 0
    ys, xs = np.nonzero(alpha)
    h, w = alpha.shape
    edges = sum([xs.min() <= 1, ys.min() <= 1, xs.max() >= w - 2, ys.max() >= h - 2])
    if edges > 1:
        return 0
    span_w, span_h = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
    if span_w > span_h * 3.2 or span_h > span_w * 3.2:  # a sliver at icon size
        return 0
    return 1 + (1 - abs(coverage - 0.35)) - edges * 0.3


def main():
    from rembg import new_session, remove
    session = new_session("u2net")
    index = json.loads(I.INDEX.read_text(encoding="utf-8")) if I.INDEX.exists() else {}
    if "--redo" in sys.argv:
        for entry in index.values():
            entry.pop("object", None)
    used = {e["title"] for e in index.values() if e.get("object")}
    pages_cache = {}
    cleveland_tried = {}
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    todo = [r for r in I.rows() if not index.get(r[1], {}).get("object")]
    if limit:
        todo = todo[:limit]
    I.CUT.mkdir(parents=True, exist_ok=True)
    for number, (kind, item_id, code, name, icon) in enumerate(todo, 1):
        best = None
        for query in searches(code, icon):
            for source in ("cleveland", "commons"):
                key = (source, query)
                if key not in pages_cache:
                    try:
                        pages_cache[key] = cleveland(query) if source == "cleveland" else commons(query)
                    except BaseException as error:  # Commons refusing for a while ends in SystemExit
                        print(f"  {source} search failed for {query}: {error}")
                        pages_cache[key] = []
                nouns = [w for w in query.lower().replace("-", " ").split() if w not in GENERIC]
                for title, url, licence, page_url in pages_cache[key]:
                    if not any(noun in title.lower() for noun in nouns):
                        continue  # the search engines are loose: the object must be named in the title
                    if source == "cleveland":
                        cleveland_tried[query] = True
                    if title in used:
                        continue
                    used.add(title)  # tried once is enough, whether or not it is kept
                    try:
                        data = I.get(url)
                        photo = Image.open(io.BytesIO(data)).convert("RGB")
                    except BaseException:
                        continue
                    photo.thumbnail((520, 520))
                    cut = remove(photo, session=session)
                    if score(cut) > 0:
                        best = (title, page_url, licence, data, cut, query)
                        break
                if best:
                    break
            if best:
                break
        if not best:
            print(f"[{number}/{len(todo)}] {item_id}: no clear object found", flush=True)
            continue
        title, page_url, licence, data, cut, query = best
        photo = Image.open(io.BytesIO(data)).convert("RGB")
        photo.save(I.SOURCES / f"{item_id}.jpg", quality=90)
        cut.save(I.CUT / f"{item_id}.png")
        index[item_id] = {"kind": kind, "name": name, "title": title, "page": page_url,
                          "licence": licence, "artist": "", "query": query, "object": True}
        I.INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"[{number}/{len(todo)}] {item_id}: {title} ({query})", flush=True)
    print(f"OK: {sum(1 for e in index.values() if e.get('object'))} object photographs")


if __name__ == "__main__":
    main()
