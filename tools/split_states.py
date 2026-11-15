"""Split the world's vanilla states along Kaiserreich's state borders: python tools/split_states.py --compute

Kaiserreich (workshop 1521695605) cuts Europe into more, smaller states. Both maps are the same size, so each vanilla
province's pixels show which Kaiserreich state lies under it. A vanilla state is cut wherever its provinces fall in
different Kaiserreich states, but only into pieces that are real: a piece counts when most of that Kaiserreich
state's pixels lie inside this vanilla state, so slivers made by the two maps' different province shapes stay with
the main piece. The main piece keeps the vanilla id, its factories and resources; every other piece becomes a new
state numbered from 1082 up, with its own provinces, victory points, port and fort buildings and a share of manpower.

France's own states are left whole: the regional opposition, the elections and the campaign map are drawn on them.

--compute (needs Kaiserreich installed) writes tools/state_splits.json; build_world.py then applies it with apply(),
so the mod builds without Kaiserreich. expand() turns any list of vanilla states into the list with their pieces.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "state_splits.json"
FIRST_NEW = 1082
# Hand cuts on top of Kaiserreich's: Emilia (Kaiserreich state 1004) becomes the duchies of Parma (west) and Modena (east).
HAND = {"emilia": {"kr": 1004, "west": ("parma", "파르마"), "east": ("modena", "모데나")}}


def load():
    return json.loads(DATA.read_text(encoding="utf-8")) if DATA.exists() else {"pieces": {}, "names": {}, "tags": {}}


# Pieces cut by hand, for borders Kaiserreich does not draw (ids fixed, after the computed ones):
# original vanilla state -> [(new state id, Korean name, provinces)]. The original keeps the rest.
EXTRA = {
    # The Kingdom of Sardinia's mainland divisions: Turin keeps Piedmont's id, the others are cut from it.
    158: [(1134, "쿠네오", [770, 11721, 11723]),
          (1135, "알레산드리아", [771, 9741]),
          (1136, "노바라", [776, 6635, 11726])],
    # The island: Cagliari keeps the id, Sassari and the north are cut from it.
    114: [(1137, "사사리", [6891, 9772, 9863, 11755])],
    # La Spezia (Genoese, then Sardinian) and the Po plain around Mirandola (Modenese) lie in another strategic
    # region than Liguria and Modena, so each becomes a small state of its own rather than joining them.
    162: [(1138, "라스페치아", [6973])],
    159: [(1139, "미란돌라", [11734])],
    # Vanilla's Savoy reaches into the Dauphiné and the Ubaye (Gap, Briançon, Barcelonnette), French since 1713:
    # they go back to France, and the Kingdom narrows above the County of Nice as it did.
    735: [(1407, "브리앙송", [9736, 3764, 6975])],
}
# Provinces moved by hand into a piece, from whatever state holds them:
#   Florina joins Veria, so the whole Greek salient goes to Bulgaria.
MOVE = {9837: 1118}
# Victory points named or added by hand: vanilla calls Emilia's chief town (around Reggio and Modena) Parma; Parma
# itself lies in the province west of it.
VP_NAMES = {9752: "모데나", 6790: "파르마"}
VP_ADDED = {6790: "3"}


def pieces():
    """original vanilla state -> list of (new state id, provinces)."""
    out = {int(k): [(int(a), list(b)) for a, b in v] for k, v in load()["pieces"].items()}
    for orig, parts in EXTRA.items():
        out.setdefault(orig, []).extend((new, list(provs)) for new, _, provs in parts)
    for prov, target in MOVE.items():
        for parts in out.values():
            for new, provs in parts:
                if prov in provs and new != target:
                    provs.remove(prov)
                if new == target and prov not in provs:
                    provs.append(prov)
    return out


def province_blocks(text):
    """(province, block) for every province building block ("\\n\\t\\t\\t9998 = { naval_base = 6 }"), its braces matched,
    so a block holding a landmark with its own nested blocks is taken whole."""
    out = []
    for m in re.finditer(r"\n\t\t\t(\d+)\s*=\s*\{", text):
        depth, end = 1, m.end()
        while depth and end < len(text):
            depth += {"{": 1, "}": -1}.get(text[end], 0)
            end += 1
        out.append((int(m.group(1)), text[m.start():end]))
    return out


def vp_pairs_in(body):
    """(province, value) pairs of a victory_points block, written "6780 5" or "province = 6780 value = 5"."""
    if "province" in body:
        return [(int(a), b) for a, b in re.findall(r"province\s*=\s*(\d+)\s+value\s*=\s*([\d.]+)", body)]
    return [(int(a), b) for a, b in zip(*[iter(body.split())] * 2)]


def hand_names():
    return {new: name for parts in EXTRA.values() for new, name, _ in parts}


def expand(states):
    """A list of vanilla states, with every piece cut from them added after them."""
    cut = pieces()
    out = []
    for s in states:
        out.append(s)
        out += [new for new, _ in cut.get(s, [])]
    return out


def compute():
    import numpy as np
    sys.path.insert(0, str(ROOT))
    import kr_regions as k
    import settlement_decisions as sd
    v_prov, k_prov = k.province_map(k.VANILLA), k.province_map(k.KR)
    vflat, kflat = v_prov.ravel(), k_prov.ravel()
    v_states = k.provinces_of_states(k.VANILLA)
    k_states = k.provinces_of_states(k.KR)
    k_state_of = {p: s for s, ps in k_states.items() for p in ps}
    # Pixel counts: (vanilla province, Kaiserreich province).
    pairs = Counter(zip(vflat.tolist(), kflat.tolist()))
    best = {}
    for (vp, kp), n in pairs.items():
        if vp and kp and n > best.get(vp, (0, 0))[1]:
            best[vp] = (kp, n)
    v_state_of = {p: s for s, ps in v_states.items() for p in ps}
    # Where each Kaiserreich state mostly lies, by pixels.
    k_home = defaultdict(Counter)
    for (vp, kp), n in pairs.items():
        if vp in v_state_of and kp in k_state_of:
            k_home[k_state_of[kp]][v_state_of[vp]] += n
    home = {ks: c.most_common(1)[0][0] for ks, c in k_home.items()}
    owners = sd.start_owners()
    # Europe: by the continent column of vanilla's definition.csv.
    continent = {}
    for line in (k.VANILLA / "map" / "definition.csv").read_text(encoding="utf-8-sig", errors="ignore").splitlines():
        parts = line.split(";")
        if len(parts) > 7 and parts[0].isdigit() and parts[7].strip().isdigit():
            continent[int(parts[0])] = int(parts[7])
    # Pixel centres of provinces, for the hand cut and for names.
    ys, xs = np.nonzero(v_prov)
    ids = v_prov[ys, xs]
    sums = defaultdict(lambda: [0, 0, 0])
    for pid, x, y in zip(ids.tolist(), xs.tolist(), ys.tolist()):
        t = sums[pid]
        t[0] += x
        t[1] += y
        t[2] += 1
    centre = {p: (t[0] / t[2], t[1] / t[2]) for p, t in sums.items()}
    # Pieces already cut keep their ids (other tables name them); states not cut yet get ids after the last one.
    old = load()
    result, names, tags = dict(old["pieces"]), dict(old["names"]), dict(old["tags"])
    taken = [int(a) for parts in result.values() for a, _ in parts] + [new for parts in EXTRA.values() for new, _, _ in parts]
    next_id = max(taken + [FIRST_NEW - 1]) + 1
    first = next_id
    names_ko = sd.korean_names()
    for sid in sorted(v_states):
        ps = v_states[sid]
        if owners.get(sid) == "FRA" or str(sid) in result or sid in EXTRA:
            continue
        groups = defaultdict(list)
        # Outside Europe vanilla's states are already as small as Kaiserreich's but drawn elsewhere, so a Kaiserreich
        # state rarely lies mostly inside one of them. There Kaiserreich's borders are laid over vanilla's: every
        # Kaiserreich state with two or more provinces in a vanilla state becomes a piece of it.
        overlay = Counter(continent.get(p, 0) for p in ps).most_common(1)[0][0] != 1
        for p in ps:
            ks = k_state_of.get(best.get(p, (None,))[0])
            groups[ks if ks is not None and (overlay or home.get(ks) == sid) else None].append(p)
        if overlay:
            for g in [g for g in groups if g is not None and len(groups[g]) < 2]:
                groups[None].extend(groups.pop(g))
        real = [g for g in groups if g is not None]
        if len(real) <= 1 and not any(HAND[h]["kr"] in groups for h in HAND):
            continue
        # The main piece: the one holding the most provinces (with the slivers).
        main = max(real, key=lambda g: len(groups[g]))
        main_provs = groups[main] + groups.get(None, [])
        cut = []
        for g in sorted(real):
            if g == main:
                continue
            hand = next((h for h in HAND.values() if h["kr"] == g), None)
            if hand and len(groups[g]) >= 2:
                order = sorted(groups[g], key=lambda p: centre.get(p, (0, 0))[0])
                half = len(order) // 2
                for provs, (key, name) in ((order[:half], hand["west"]), (order[half:], hand["east"])):
                    cut.append((next_id, sorted(provs)))
                    names[str(next_id)] = name
                    tags[key] = next_id
                    next_id += 1
                continue
            cut.append((next_id, sorted(groups[g])))
            next_id += 1
        if cut:
            result[str(sid)] = cut
            # The Kaiserreich state number of each piece, for its name.
            for new, provs in cut:
                if str(new) not in names:
                    ks = Counter(k_state_of.get(best.get(p, (None,))[0]) for p in provs).most_common(1)[0][0]
                    names[str(new)] = f"kr:{ks}"
    DATA.write_text(json.dumps({"pieces": result, "names": names, "tags": tags, "main": {}}, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"OK: {len(result)} states cut, {next_id - first} new states this time ({first}-{next_id - 1})")


# Who holds the pieces in 1936, where it is not the original's owner. Keys are state ids or HAND piece names.
OWNERS = {
    157: "TTS",      # Abruzzo: Naples held it for centuries; the Marches and Umbria, cut from it, stay with the Pope
    1109: "PAP",     # the Marches
    1110: "PAP",     # Umbria
    "parma": "PRM",  # the duchies of Parma and Modena, cut from Emilia
    "modena": "MDN",
    1118: "BUL",     # the northern arm of Epirus, the Greek salient between Debar and Central Macedonia
    1138: "ITA",     # La Spezia
    1139: "MDN",     # Mirandola
    1407: "FRA",     # Briançon, Gap and Barcelonnette
    1093: "AUS",     # Southern Bukovina (Suceava), with the northern half Austria already holds
    # Asir (856) stays Ottoman with Mecca (1264, cut from it), and Aden British: Yemen keeps its 1936 size.
    # Arabia as in Kaiserreich: the Rashidi emirate of Jabal Shammar holds the north between the Ottomans and Nejd,
    # the Trucial coast is Ottoman.
    675: "JBS", 854: "JBS", 857: "JBS", 1010: "JBS", 1316: "JBS", 1375: "JBS",
    658: "TUR",
    187: "TUR",      # the Dodecanese
}
DIRECTIONS = [("북부", 0, -1), ("남부", 0, 1), ("서부", -1, 0), ("동부", 1, 0)]
# Originals renamed because the town they were named after went to a piece: Sofia's state keeps Vidin, Istria's Rijeka.
ORIGINAL_NAMES = {48: "비딘", 852: "리예카", 161: "로마냐", 158: "토리노", 114: "칼리아리", 856: "아시르"}
# Korean names of the Kaiserreich states the pieces come from (Kaiserreich's English names in the comments).
KR_NAMES = {
    764: "비테르보", 978: "림뷔르흐", 979: "서스헬더", 36: "프리슬란트", 664: "미슈콜츠", 768: "테살리아", 48: "소피아", 781: "라인란트 서부",
    147: "프로이센령 작센", 83: "파르티움", 789: "세케이 지방", 713: "수체아바", 1088: "헤움", 93: "브레스트", 997: "폴레시에", 204: "노보그루데크",
    1107: "카라반켄", 108: "크랄레보", 794: "스렘", 1125: "슬라보니아", 122: "사우스웨일스", 123: "콘월", 1122: "웨식스", 1121: "에어셔",
    148: "토르니오", 835: "케른텐", 836: "잘츠부르크", 157: "마르케", 1005: "움브리아", 838: "리구리아", 1003: "아오스타", 759: "프리울리",
    184: "코모티니", 758: "이오니아 제도", 1076: "베리아", 1087: "모길료프", 771: "바르나", 1089: "크르잘리", 791: "스타로두프",
    226: "예카테리노슬라프", 787: "테레크", 234: "예카테리노다르", 241: "호멜", 909: "하파란다", 731: "플로리나", 762: "니스",
    943: "오트사부아", 683: "고리치아", 736: "이스트리아", 741: "베르비에",
}


def owner_overrides():
    data = load()
    return {(data["tags"][k] if isinstance(k, str) else k): v for k, v in OWNERS.items() if not isinstance(k, str) or k in data["tags"]}


def apply(mod, vanilla, note):
    """Write the cut states: the original with fewer provinces and every piece as a state of its own, the building
    positions they need (map/buildings.txt), their Korean names, and the owners in OWNERS. Called by build_world.py
    after it has written the state histories."""
    import numpy as np
    from PIL import Image
    data = load()
    cut = pieces()
    if not cut:
        return 0
    owners = owner_overrides()
    folder = mod / "history" / "states"
    vfiles = {int(re.search(r"\bid\s*=\s*(\d+)", re.sub(r"#.*", "", p.read_text(encoding="utf-8-sig", errors="ignore"))).group(1)): p
              for p in (vanilla / "history" / "states").glob("*.txt")}
    # Province pixels, for building positions and names.
    colours = {}
    for line in (vanilla / "map" / "definition.csv").read_text(encoding="utf-8-sig", errors="ignore").splitlines():
        parts = line.split(";")
        if len(parts) > 3 and parts[0].isdigit():
            colours[(int(parts[1]) << 16) | (int(parts[2]) << 8) | int(parts[3])] = int(parts[0])
    pixels = np.asarray(Image.open(vanilla / "map" / "provinces.bmp").convert("RGB"), dtype=np.uint32)
    keys = (pixels[..., 0] << 16) | (pixels[..., 1] << 8) | pixels[..., 2]
    lookup = np.zeros(keys.max() + 1, dtype=np.int32)
    for key, pid in colours.items():
        lookup[key] = pid
    prov_map = lookup[keys]
    height = prov_map.shape[0]

    def province_at(x, z, allowed=None):
        """The province under a building position, truncating the coordinates as the game does (rounding put coastal
        buildings in the sea). With `allowed`, a position that still misses those provinces takes the nearest of them."""
        row, col = height - 1 - int(z), int(x)
        here = int(prov_map[row, col]) if 0 <= row < height and 0 <= col < prov_map.shape[1] else 0
        if allowed is None or here in allowed:
            return here
        best, best_d = here, None
        for dr in range(-4, 5):
            for dc in range(-4, 5):
                r, c = row + dr, col + dc
                if 0 <= r < height and 0 <= c < prov_map.shape[1] and int(prov_map[r, c]) in allowed:
                    d = dr * dr + dc * dc
                    if best_d is None or d < best_d:
                        best, best_d = int(prov_map[r, c]), d
        return best

    # Each province's pixels, found once: scanning the whole map for every piece took a quarter of an hour.
    flat = prov_map.ravel()
    order = np.argsort(flat, kind="stable")
    starts = np.searchsorted(flat[order], np.arange(int(flat.max()) + 2))
    width = prov_map.shape[1]

    def pixels(provs):
        idx = np.sort(np.concatenate([order[starts[p]:starts[p + 1]] for p in provs]))  # map order, as before
        return idx // width, idx % width

    def centre(provs):
        ys, xs = pixels(provs)
        return float(xs.mean()), float(height - 1 - ys.mean())

    land_points = {}

    def land_point(provs):
        """A point inside the provinces, as near their middle as their shape allows (the mean of an island chain or
        a crescent can lie in the sea); written so the game's truncation lands on the same pixel."""
        key = tuple(sorted(provs))
        if key not in land_points:
            ys, xs = pixels(provs)
            i = int(np.argmin((xs - xs.mean()) ** 2 + (ys - ys.mean()) ** 2))
            land_points[key] = (float(xs[i]) + 0.5, float(height - 1 - ys[i]) + 0.5)
        return land_points[key]

    # Korean names of victory points, for the pieces' names.
    vp_names, state_names = {}, {}
    for path in (vanilla / "localisation" / "korean").glob("*.yml"):
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        vp_names.update(re.findall(r'^\s*VICTORY_POINTS_(\d+):\d*\s*"(.*)"', text, re.M))
        state_names.update(re.findall(r'^\s*STATE_(\d+):\d*\s*"(.*)"', text, re.M))
    building_lines = (vanilla / "map" / "buildings.txt").read_text(encoding="utf-8-sig", errors="ignore").splitlines()
    by_state = defaultdict(list)
    for i, line in enumerate(building_lines):
        parts = line.split(";")
        if len(parts) >= 7 and parts[0].isdigit():
            by_state[int(parts[0])].append(i)
    # Everything below is worked out from the vanilla histories, so running it again gives the same states.
    vtexts = {sid: re.sub(r"#[^\n]*", "", p.read_text(encoding="utf-8-sig", errors="ignore")) for sid, p in vfiles.items()}
    vprovs = {sid: [int(x) for x in re.search(r"provinces\s*=\s*\{([^}]*)\}", t).group(1).split()] for sid, t in vtexts.items()}
    home_of = {p: sid for sid, ps in vprovs.items() for p in ps}
    taken = {p for parts in cut.values() for _, ps in parts for p in ps}
    vp_of, pb_of = {}, {}  # victory points and province buildings by province
    for t in vtexts.values():
        for block in re.finditer(r"victory_points\s*=\s*\{([^}]*)\}", t):
            for a, b in vp_pairs_in(block.group(1)):
                vp_of[a] = b
        for pid, block in province_blocks(t):
            pb_of[pid] = block
    vp_of.update(VP_ADDED)
    hand = hand_names()
    names = {**{int(k): v for k, v in data["names"].items()}, **hand}
    loc = ["l_korean:"]
    written = 0
    # Every state that loses provinces: the originals with pieces, and any state a hand move takes a province from.
    sources = sorted(set(cut) | {home_of[p] for p in taken if p in home_of})
    for orig in sources:
        parts_ = cut.get(orig, [])
        current = folder / vfiles[orig].name
        text = (current if current.exists() else vfiles[orig]).read_text(encoding="utf-8-sig", errors="ignore")
        text = re.sub(r"#[^\n]*", "", text.removeprefix(note))  # comments ("#Sofia") would break the parsing below
        provs_all = vprovs[orig]
        moved = set(provs_all) & taken
        keep = [p for p in provs_all if p not in moved]
        manpower = int(re.search(r"manpower\s*=\s*(\d+)", vtexts[orig]).group(1))
        share = lambda ps, total=len(provs_all), mp=manpower: int(mp * len(ps) / max(1, total))
        orig_owner = re.search(r"\bowner\s*=\s*(\w+)", text).group(1)
        cx0, cz0 = centre(keep)
        # The original: fewer provinces and men, without the moved provinces' victory points and buildings.
        new_text = re.sub(r"provinces\s*=\s*\{[^}]*\}", "provinces = {\n\t\t" + " ".join(map(str, keep)) + "\n\t}", text, count=1)
        new_text = re.sub(r"manpower\s*=\s*\d+", f"manpower = {manpower - share(moved)}", new_text, count=1)
        for pid, block in province_blocks(new_text):
            if pid in moved:
                new_text = new_text.replace(block, "")

        def kept_vps(block):
            pairs = [(a, b) for a, b in vp_pairs_in(block.group(1)) if a not in moved]
            # The game takes one province and one value per block.
            return "\n\t\t".join(f"victory_points = {{ {a} {b} }}" for a, b in pairs)

        new_text = re.sub(r"victory_points\s*=\s*\{([^}]*)\}", kept_vps, new_text)
        if orig in owners:
            new_text = re.sub(r"\bowner\s*=\s*\w+", f"owner = {owners[orig]}", new_text, count=1)
            new_text = re.sub(r"(history\s*=\s*\{)", rf"\1\n\t\tadd_core_of = {owners[orig]}", new_text, count=1)
        # A dockyard needs a port: when every naval base went to the pieces, so does the dockyard.
        dockyard = None
        if parts_ and not any("naval_base" in pb_of.get(p, "") for p in keep):
            found = re.search(r"\n\t+dockyard\s*=\s*(\d+)", new_text)
            if found:
                dockyard = found.group(1)
                new_text = re.sub(r"\n\t+dockyard\s*=\s*\d+[ \t]*", "", new_text)
        (folder / vfiles[orig].name).write_bytes((note + new_text).encode("utf-8"))
        # Each piece.
        category = re.search(r"state_category\s*=\s*(\w+)", text).group(1)
        infra = re.search(r"infrastructure\s*=\s*(\d+)", text)
        cores = re.findall(r"add_core_of\s*=\s*(\w+)", text)
        claims = re.findall(r"add_claim_by\s*=\s*(\w+)", text)
        for new, ps in parts_:
            owner = owners.get(new, orig_owner)
            vps = [(p, vp_of[p]) for p in ps if p in vp_of]
            pbs = "".join(pb_of[p] for p in ps if p in pb_of)
            men = sum(int(int(re.search(r"manpower\s*=\s*(\d+)", vtexts[s]).group(1)) / max(1, len(vprovs[s])))
                      for s in (home_of[p] for p in ps if p in home_of))
            hist = [f"\t\towner = {owner}"]
            if vps:
                hist += [f"\t\tvictory_points = {{ {a} {b} }}" for a, b in vps]  # one pair per block
            yard = ""
            if dockyard and "naval_base" in pbs:
                yard, dockyard = f"\n\t\t\tdockyard = {dockyard}", None
            hist.append("\t\tbuildings = {\n" + (f"\t\t\tinfrastructure = {infra.group(1)}" if infra else "") + yard + pbs + "\n\t\t}")
            for tag in sorted(set(cores + ([owner] if owner != orig_owner else []))):
                hist.append(f"\t\tadd_core_of = {tag}")
            for tag in sorted(set(claims)):
                hist.append(f"\t\tadd_claim_by = {tag}")
            body = (f"state = {{\n\tid = {new}\n\tname = \"STATE_{new}\"\n\tmanpower = {men}\n\n\tstate_category = {category}\n\n"
                    "\thistory = {\n" + "\n".join(hist) + "\n\t}\n\n\tprovinces = {\n\t\t" + " ".join(map(str, ps)) + "\n\t}\n\n\tlocal_supplies = 0.0\n}\n")
            (folder / f"{new}-{orig}_piece.txt").write_bytes((note + body).encode("utf-8"))
            # Its name: given by hand, or the biggest victory point's town, or the original's name and a direction.
            name = names.get(new, "")
            if name.startswith("kr:") and int(name[3:]) in KR_NAMES:
                name = KR_NAMES[int(name[3:])]
            if not name or name.startswith("kr:"):
                name = ""
                if vps:
                    best = max(vps, key=lambda v: float(v[1]))[0]
                    name = vp_names.get(str(best), "")
                if not name:  # any town of the piece the game has a Korean name for
                    name = next((vp_names[str(p)] for p in ps if str(p) in vp_names), "")
                if not name:
                    cx, cz = centre(ps)
                    dx, dz = cx - cx0, -(cz - cz0)
                    word = max(DIRECTIONS, key=lambda d: d[1] * dx + d[2] * dz)[0]
                    name = f"{state_names.get(str(orig), orig)} {word}"
            loc.append(f' STATE_{new}:0 "{name}"')
            # Building positions standing inside the piece move to it, from whichever state held them; any kind the
            # original has that the piece is left without gets a position at the piece's middle.
            kinds_here = set()
            for src in sorted({home_of[p] for p in ps if p in home_of}):
                for i in by_state[src]:
                    parts = building_lines[i].split(";")
                    if province_at(float(parts[2]), float(parts[4]), set(vprovs[src])) in ps:
                        parts[0] = str(new)
                        building_lines[i] = ";".join(parts)
                        kinds_here.add(parts[1])
            cx, cz = centre(ps)
            ys = [float(building_lines[i].split(";")[3]) for i in by_state[orig]] or [10.0]
            y = sum(ys) / len(ys)
            for kind in sorted({building_lines[i].split(";")[1] for i in by_state[orig]} - kinds_here):
                if kind in ("naval_base_spawn", "coastal_bunker", "floating_harbor", "dockyard"):
                    continue  # tied to a coast this piece may not have
                lx, lz = land_point(ps)
                building_lines.append(f"{new};{kind};{lx:.2f};{y:.2f};{lz:.2f};0.00;0")
            written += 1
        # The original keeps a position for every kind it had: its air wings (and rocket sites, coastal guns...) need
        # one, and a state with an air force but no air base position crashes the game on the first day.
        if parts_ and keep:
            had = {building_lines[i].split(";")[1] for i in by_state[orig]}
            left = {building_lines[i].split(";")[1] for i in by_state[orig] if building_lines[i].split(";")[0] == str(orig)}
            ys = [float(building_lines[i].split(";")[3]) for i in by_state[orig]] or [10.0]
            y = sum(ys) / len(ys)
            lx, lz = land_point(keep)
            for kind in sorted(had - left):
                if kind in ("naval_base_spawn", "coastal_bunker", "floating_harbor", "dockyard"):
                    continue  # tied to a coast the original may no longer have
                building_lines.append(f"{orig};{kind};{lx:.2f};{y:.2f};{lz:.2f};0.00;0")
    (mod / "map").mkdir(parents=True, exist_ok=True)
    # No blank last line: the game reads it as a building with no fields.
    (mod / "map" / "buildings.txt").write_text("\n".join(line for line in building_lines if line.strip()), encoding="utf-8")
    loc += [f' STATE_{sid}:0 "{name}"' for sid, name in ORIGINAL_NAMES.items() if sid in cut]
    loc += [f' VICTORY_POINTS_{p}:0 "{name}"' for p, name in VP_NAMES.items()]
    (mod / "localisation" / "korean" / "replace" / "lr_states_l_korean.yml").write_text("\n".join(loc) + "\n", encoding="utf-8-sig")
    return written


if __name__ == "__main__":
    if "--compute" in sys.argv:
        compute()
