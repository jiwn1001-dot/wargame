"""Cut vanilla provinces along Kaiserreich's state borders: python tools/kr_provinces.py

    python tools/kr_provinces.py --compute   once, with Kaiserreich installed: finds the cuts and stores them in
                                             tools/kr_provinces.png (which new province each pixel becomes) and
                                             tools/kr_provinces.json (their parents); the build runs without it.
                                             Then run python tools/kr_layout.py --compute, which reads the cut map.

The states are Kaiserreich's (kr_layout.py), but vanilla's provinces are cut differently from Kaiserreich's, so states
drawn province by province miss Kaiserreich's borders by a province here and there. Wherever a Kaiserreich state
border crosses a vanilla province, the smaller side (at least MIN_PIXELS and MIN_SHARE of it) becomes a province of its
own. The other provinces keep their numbers, so every army, port and victory point stays where it was.

The build step writes the mod's map/provinces.bmp, map/definition.csv (the new provinces after vanilla's last
number), the strategic regions holding them, and map/unitstacks.txt. kr_layout.py then puts each new province in its
parent's state and draws the states.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
PROJECT = TOOLS.parent
MOD = PROJECT / "mod"
VANILLA = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV")
DATA = TOOLS / "kr_provinces.json"
MASK = TOOLS / "kr_provinces.png"
MIN_PIXELS = 12         # a smaller side stays with the province (smaller ones cannot hold a unit)
MIN_SHARE = 0.0
# Land this world draws by hand, not by Kaiserreich's states: (owner, the countries it is taken from, outline in
# (longitude, latitude)). New Spain keeps the Adams-Onis line of 1819: the 42nd parallel from the Pacific, south from
# it to the source of the Arkansas, down the Arkansas to the 100th meridian, south to the Red River, down the Red
# River to the Sabine and down the Sabine to the Gulf. Provinces are cut along it like along a state border.
AREAS = [
    ("MEX", {"USA"}, [
        (-126.0, 42.0), (-106.3, 42.0), (-106.3, 39.25), (-106.0, 38.53), (-105.24, 38.44), (-104.61, 38.27),
        (-103.54, 37.98), (-102.62, 38.09), (-102.05, 38.0), (-100.87, 37.97), (-100.0, 37.75), (-100.0, 34.56),
        (-99.2, 34.25), (-98.0, 34.1), (-97.0, 33.85), (-96.0, 33.85), (-95.0, 33.88), (-94.04, 33.55),
        (-94.04, 32.0), (-93.85, 31.0), (-93.7, 30.1), (-93.84, 29.6), (-93.84, 20.0), (-126.0, 20.0)]),
]
# Longitude and latitude on the vanilla map, measured on the straight borders of the American states (Colorado,
# Wyoming, Utah, Kansas, Oregon, New Mexico): 15.57 pixels a degree of longitude; latitude by those borders' rows.
LON_X = (-109.05, 1104.0, 15.57)
LAT_Y = [(31.33, 661.0), (37.0, 560.0), (41.0, 486.0), (42.0, 467.0), (45.0, 409.0), (46.26, 384.0)]


def area_mask(shape, outline):
    """The pixels inside an outline given in longitude and latitude (only good near the American West)."""
    import numpy as np
    from PIL import Image, ImageDraw
    lats, rows = zip(*LAT_Y)
    slope = (rows[-1] - rows[0]) / (lats[-1] - lats[0])

    def row(lat):
        if lats[0] <= lat <= lats[-1]:
            return float(np.interp(lat, lats, rows))
        edge = 0 if lat < lats[0] else -1
        return rows[edge] + (lat - lats[edge]) * slope

    points = [(LON_X[1] + (lon - LON_X[0]) * LON_X[2], row(lat)) for lon, lat in outline]
    picture = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(picture).polygon(points, fill=1)
    return np.asarray(picture).astype(bool)


VP_NEAR = 8            # pixels for a city Kaiserreich spells differently
VP_REACH = 25          # pixels between a vanilla city and Kaiserreich's of the same name
SPARE = {230, 231, 856}  # vanilla states not cut: Armenia and Asir keep this world's owners (kr_layout.KR_BORDERS_SPARE, KR_BORDERS_KEEP)


def definition(root):
    rows = {}
    for line in (root / "map" / "definition.csv").read_text(encoding="utf-8-sig", errors="ignore").splitlines():
        parts = line.split(";")
        if len(parts) >= 8 and parts[0].isdigit():
            rows[int(parts[0])] = parts
    return rows


def components(flat_indices, width):
    """The 4-connected pieces of a set of pixels (flat indices)."""
    left = set(int(i) for i in flat_indices)
    out = []
    while left:
        start = left.pop()
        part, stack = [start], [start]
        while stack:
            i = stack.pop()
            for j in (i - 1 if i % width else -1, i + 1 if (i + 1) % width else -1, i - width, i + width):
                if j in left:
                    left.remove(j)
                    part.append(j)
                    stack.append(j)
        out.append(part)
    return out


def compute():
    import numpy as np
    sys.path.insert(0, str(TOOLS))
    import kr_regions as k
    import kr_layout
    v = k.province_map(k.VANILLA).astype(np.int64)
    kp = k.province_map(k.KR).astype(np.int64)
    # Kaiserreich's state under each pixel: every vanilla province a Kaiserreich state border crosses is cut there, so
    # the states kr_layout.py draws have Kaiserreich's borders, not vanilla's province edges near them.
    k_states = k.provinces_of_states(k.KR)
    state_of_kprov = np.zeros(kp.max() + 1, dtype=np.int32)
    for s, ps in k_states.items():
        for p in ps:
            if p < len(state_of_kprov):
                state_of_kprov[p] = s
    owner = state_of_kprov[kp]
    areas = []
    import build_world
    vanilla_owner = build_world.vanilla_states()
    vanilla_states = k.provinces_of_states(k.VANILLA)
    for number, (_, taken_from, outline) in enumerate(AREAS, start=1):
        # Only the land of the countries it is taken from: the outline's far edges never cut anyone else's provinces.
        theirs_now = [q for sid, ps in vanilla_states.items() if vanilla_owner.get(sid) in taken_from for q in ps]
        inside = area_mask(v.shape, outline) & np.isin(v, theirs_now)
        areas.append(inside)
        owner = np.where((owner > 0) & inside, owner + 100000 * number, owner)
    # Land provinces in states (not Armenia's).
    land = set()
    spare = set()
    for sid, ps in k.provinces_of_states(k.VANILLA).items():
        (spare if sid in SPARE else land).update(ps)
    land -= spare
    land = {p for p, r in definition(VANILLA).items() if r[4] == "land"} & land  # lakes have no unit positions to share
    mask = np.zeros(v.shape, dtype=np.uint16)
    parents = []
    flat_v = v.ravel()
    order = np.argsort(flat_v, kind="stable")
    sorted_v = flat_v[order]
    starts = np.searchsorted(sorted_v, np.arange(v.max() + 2))
    for p in sorted(land):
        idx = order[starts[p]:starts[p + 1]]
        if idx.size < MIN_PIXELS * 2:
            continue
        o = owner.ravel()[idx]
        present = set(np.unique(o).tolist()) - {0}
        if len(present) < 2:
            continue
        counts = {t: int((o == t).sum()) for t in present}
        keep = max(counts, key=counts.get)  # the province keeps its biggest side
        for t, n in counts.items():
            if t == keep or n < MIN_PIXELS or n < MIN_SHARE * idx.size:
                continue
            for part in components(idx[o == t], v.shape[1]):
                if len(part) >= MIN_PIXELS:
                    parents.append(p)
                    mask.ravel()[np.array(part)] = len(parents)
    # No four provinces may meet at one point, nor two cross diagonally (the game's "invalid X crossing"): where a
    # cut made such a corner, one pixel of the new province goes back to its parent, until none is left.
    base = int(v.max()) + 1

    def crossings(ids):
        a, b, c, d = ids[:-1, :-1], ids[:-1, 1:], ids[1:, :-1], ids[1:, 1:]
        four = (a != b) & (a != c) & (a != d) & (b != c) & (b != d) & (c != d)
        return four | ((a == d) & (b == c) & (a != b))

    def lonely(ids):
        """Pixels none of whose four neighbours is of their own province (the game's "one-pixel province colour")."""
        same = np.zeros(ids.shape, dtype=bool)
        same[1:, :] |= ids[1:, :] == ids[:-1, :]
        same[:-1, :] |= ids[:-1, :] == ids[1:, :]
        same[:, 1:] |= ids[:, 1:] == ids[:, :-1]
        same[:, :-1] |= ids[:, :-1] == ids[:, 1:]
        return ~same

    old_bad = crossings(v)
    old_lonely = lonely(v)

    def reattach():
        """A parent the cuts left in pieces: the pieces off its main body join the new province they touch."""
        moved = 0
        for parent in set(parents):
            idx = order[starts[parent]:starts[parent + 1]]
            rest = idx[mask.ravel()[idx] == 0]
            parts = components(rest, v.shape[1])
            if len(parts) <= len(components(idx, v.shape[1])):
                continue
            parts.sort(key=len)
            for part in parts[:-1]:
                touching = []
                for i in part:
                    y, x = divmod(i, v.shape[1])
                    for r, c in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                        if 0 <= r < v.shape[0] and 0 <= c < v.shape[1] and mask[r, c] and v[r, c] == parent:
                            touching.append(int(mask[r, c]))
                if touching:
                    mask.ravel()[np.array(part)] = max(set(touching), key=touching.count)
                    moved += 1
        return moved

    for _ in range(80):
        if _ % 10 == 0:
            reattach()
        ids = np.where(mask > 0, base + mask.astype(np.int64), v)
        ys, xs = np.nonzero(crossings(ids) & ~old_bad)
        ly, lx = np.nonzero(lonely(ids) & ~old_lonely)
        if not len(ys) and not len(ly):
            if reattach():
                continue
            break
        if _ >= 40:
            # Still there: the two fixes undo each other. Give the corner's neighbourhood back to the parents.
            for y, x in list(zip(ys.tolist(), xs.tolist())) + list(zip(ly.tolist(), lx.tolist())):
                mask[max(y - 2, 0):y + 3, max(x - 2, 0):x + 3] = 0
            continue
        for y, x in zip(ys.tolist(), xs.tolist()):
            for yy, xx in ((y, x), (y, x + 1), (y + 1, x), (y + 1, x + 1)):
                if mask[yy, xx]:
                    mask[yy, xx] = 0
                    break
        # A lone pixel takes the side of its neighbours: back to the parent, or into the new province around it.
        for y, x in zip(ly.tolist(), lx.tolist()):
            around = [int(mask[r, c]) for r, c in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
                      if 0 <= r < mask.shape[0] and 0 <= c < mask.shape[1] and v[r, c] == v[y, x]]
            mask[y, x] = max(set(around), key=around.count) if around else 0
    else:
        raise SystemExit("could not clear the X crossings and lone pixels the cuts made")
    # A cut that lost all its pixels there is no province: number the rest without gaps.
    alive = [i for i in range(1, len(parents) + 1) if (mask == i).any()]
    renumber = np.zeros(len(parents) + 1, dtype=np.uint16)
    for new_index, i in enumerate(alive, start=1):
        renumber[i] = new_index
    mask = renumber[mask]
    parents = [parents[i - 1] for i in alive]
    from PIL import Image
    Image.fromarray(mask).save(MASK)
    # Victory points go where Kaiserreich puts the city: a vanilla victory point whose city Kaiserreich has, under the
    # same English name within VP_REACH pixels, moves to the province (vanilla or cut piece) under Kaiserreich's one.
    # Vanilla's Dresden sits on a province that is mostly Prussian Saxony; Kaiserreich's lies further south in Saxony.
    import re

    import unicodedata

    def plain(name):
        name = unicodedata.normalize("NFKD", name.strip().lower())
        return "".join(c for c in name if c.isalnum())

    def vp_names(root, sub):
        """province -> every English name it goes by (vanilla also names cities per country: CZE_VICTORY_POINTS_n)."""
        names = defaultdict(set)
        for path in (root / "localisation" / "english").rglob("*.yml"):
            if sub and sub not in path.name.lower():
                continue
            for pid, name in re.findall(r'^\s*(?:\w+_)?VICTORY_POINTS_(\d+):\d*\s*"(.*)"', path.read_text(encoding="utf-8-sig", errors="ignore"), re.M):
                if plain(name):
                    names[int(pid)].add(plain(name))
        return names

    def vp_provinces(root):
        found = set()
        for path in (root / "history" / "states").glob("*.txt"):
            text = re.sub(r"#[^\n]*", "", path.read_text(encoding="utf-8-sig", errors="ignore"))
            found.update(int(x) for x in re.findall(r"victory_points\s*=\s*\{\s*(\d+)", text))
        return found

    def centres(arr, wanted):
        flat = arr.ravel()
        order_ = np.argsort(flat, kind="stable")
        sorted_ = flat[order_]
        out = {}
        for q in wanted:
            lo, hi = np.searchsorted(sorted_, q), np.searchsorted(sorted_, q, side="right")
            if hi > lo:
                ys, xs = np.divmod(order_[lo:hi], arr.shape[1])
                out[q] = (float(xs.mean()), float(ys.mean()), order_[lo:hi])
        return out

    ours, theirs = vp_provinces(VANILLA), vp_provinces(k.KR)
    our_names, their_names = vp_names(VANILLA, "victory_points"), vp_names(k.KR, "")
    by_name = defaultdict(list)
    for q in theirs:
        for name in their_names.get(q, ()):
            by_name[name].append(q)
    our_c, their_c = centres(v, ours), centres(kp, theirs)
    final_ids = np.where(mask > 0, base + mask.astype(np.int64), v).ravel()
    vp_moves = {}
    taken = set(ours)

    def dist(p, q):
        return (their_c[q][0] - our_c[p][0]) ** 2 + (their_c[q][1] - our_c[p][1]) ** 2

    # First the same city by name within VP_REACH; then a city left over with no name in common, if Kaiserreich has one
    # within VP_NEAR pixels that no other city took (the same place under another spelling).
    matched = {}
    for p in sorted(ours):
        if p not in our_c:
            continue
        near = {q for name in our_names.get(p, ()) for q in by_name.get(name, []) if q in their_c and dist(p, q) <= VP_REACH ** 2}
        if near:
            matched[p] = min(near, key=lambda q: dist(p, q))
    used = set(matched.values())
    for p in sorted(ours):
        if p in matched or p not in our_c:
            continue
        near = [q for q in their_c if q not in used and dist(p, q) <= VP_NEAR ** 2]
        if near:
            matched[p] = min(near, key=lambda q: dist(p, q))
            used.add(matched[p])
    for p, q in sorted(matched.items()):
        # The province holding most of Kaiserreich's city, unless that is another city's: then the next one.
        counts = np.bincount(final_ids[their_c[q][2]])
        target = next((int(t) for t in np.argsort(-counts) if counts[t] and (t == p or t not in taken)), p)
        if target != p:
            vp_moves[p] = target
            taken.add(target)
    area_provinces = {}
    for (tag, _, _), inside in zip(AREAS, areas):
        flat = final_ids.ravel() if final_ids.ndim > 1 else final_ids
        ins = np.bincount(flat[inside.ravel()], minlength=flat.max() + 1)
        tot = np.bincount(flat, minlength=flat.max() + 1)
        area_provinces[tag] = [int(q) for q in np.nonzero(ins * 2 > tot)[0] if q]
    DATA.write_text(json.dumps({"parents": parents, "vp_moves": vp_moves, "areas": area_provinces}), encoding="utf-8")
    print(f"OK: {len(parents)} new provinces cut from {len(set(parents))} vanilla provinces along Kaiserreich's state borders")


def new_provinces():
    """{new province id: parent} as the build numbers them (after vanilla's last province)."""
    if not DATA.exists():
        return {}
    parents = json.loads(DATA.read_text(encoding="utf-8"))["parents"]
    first = max(definition(VANILLA)) + 1
    return {first + i: p for i, p in enumerate(parents)}


def area_owners():
    """{province: owner} for the hand-drawn areas (AREAS), in the build's numbering, with the countries it replaces."""
    if not DATA.exists():
        return {}
    data = json.loads(DATA.read_text(encoding="utf-8"))
    first = max(definition(VANILLA)) + 1
    base = first
    out = {}
    for tag, taken_from, _ in AREAS:
        for q in data.get("areas", {}).get(tag, []):
            out[first + q - base - 1 if q >= base else q] = (tag, taken_from)
    return out


def vp_moves():
    """{vanilla province: new province} for victory points that go with their city to a cut piece."""
    if not DATA.exists():
        return {}
    data = json.loads(DATA.read_text(encoding="utf-8"))
    first = max(definition(VANILLA)) + 1
    base = max(definition(VANILLA)) + 1
    # Stored as the compute step numbers them: cut pieces after the bitmap's last province.
    return {int(p): (first + t - base - 1 if t >= base else t) for p, t in data.get("vp_moves", {}).items()}


def build():
    import numpy as np
    from PIL import Image
    news = new_provinces()
    out = MOD / "map"
    out.mkdir(parents=True, exist_ok=True)
    names = ("provinces.bmp", "definition.csv", "unitstacks.txt", "railways.txt")
    if not news:
        for name in names:
            (out / name).unlink(missing_ok=True)
        print("OK: no provinces cut")
        return
    # The map work takes minutes and its inputs rarely change: when they have not, only the strategic regions (which
    # kr_layout.py overwrites every build) are written again.
    stamp_path = Path(__file__).resolve().parent / "kr_layout_cache" / "kr_provinces_stamp.json"
    inputs = [MASK, DATA, Path(__file__), VANILLA / "map" / "provinces.bmp", VANILLA / "map" / "definition.csv",
              VANILLA / "map" / "unitstacks.txt", VANILLA / "map" / "railways.txt"]
    stamp = [f"{p.name}:{p.stat().st_size}:{int(p.stat().st_mtime)}" for p in inputs]
    if stamp_path.exists() and all((out / name).exists() for name in names):
        saved = json.loads(stamp_path.read_text(encoding="utf-8"))
        if saved.get("stamp") == stamp:
            write_strategic_regions(out, saved["regions"])
            print(f"OK: {len(news)} provinces cut along Kaiserreich's state borders ({min(news)}-{max(news)}), map unchanged")
            return
    mask = np.asarray(Image.open(MASK))
    rgb = np.asarray(Image.open(VANILLA / "map" / "provinces.bmp").convert("RGB")).copy()
    rows = definition(VANILLA)
    used = {(int(r[1]), int(r[2]), int(r[3])) for r in rows.values()}
    rng = np.random.default_rng(1936)
    lines = (VANILLA / "map" / "definition.csv").read_text(encoding="utf-8-sig", errors="ignore").rstrip("\r\n").splitlines()
    stacks = (VANILLA / "map" / "unitstacks.txt").read_text(encoding="utf-8-sig", errors="ignore").rstrip("\r\n").splitlines()
    stack_of = defaultdict(list)
    for line in stacks:
        stack_of[line.split(";")[0]].append(line.split(";"))
    sea = {pid for pid, r in rows.items() if r[4] == "sea"}
    # Vanilla province ids under each pixel, to tell which new provinces touch the sea.
    key = (rgb[..., 0].astype(np.int64) << 16) | (rgb[..., 1].astype(np.int64) << 8) | rgb[..., 2]
    colour_to_id = {(int(r[1]) << 16) | (int(r[2]) << 8) | int(r[3]): pid for pid, r in rows.items()}
    sea_keys = np.array(sorted(k for k, pid in colour_to_id.items() if pid in sea), dtype=np.int64)
    is_sea = np.isin(key, sea_keys)
    height = rgb.shape[0]
    region_add = defaultdict(list)
    region_of = {}
    for path in (VANILLA / "map" / "strategicregions").glob("*.txt"):
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        import re
        body = re.search(r"provinces\s*=\s*\{([^}]*)\}", re.sub(r"#[^\n]*", "", text))
        for p in body.group(1).split():
            region_of[int(p)] = path.name
    for new, parent in news.items():
        part = mask == (new - min(news) + 1)
        while True:
            colour = tuple(int(c) for c in rng.integers(1, 255, 3))
            if colour not in used:
                used.add(colour)
                break
        rgb[part] = colour
        ys, xs = np.nonzero(part)
        grown = np.zeros_like(part)
        grown[1:, :] |= part[:-1, :]
        grown[:-1, :] |= part[1:, :]
        grown[:, 1:] |= part[:, :-1]
        grown[:, :-1] |= part[:, 1:]
        coastal = bool((grown & is_sea).any())
        r = list(rows[parent])
        r[0], r[1], r[2], r[3] = str(new), str(colour[0]), str(colour[1]), str(colour[2])
        r[5] = "true" if coastal else "false"
        lines.append(";".join(r))
        # Unit positions: the parent's, moved to the middle of the new province.
        i = int(np.argmin((xs - xs.mean()) ** 2 + (ys - ys.mean()) ** 2))
        x, z = float(xs[i]) + 0.5, float(height - 1 - ys[i]) + 0.5
        for s in stack_of.get(str(parent), []):
            s = list(s)
            s[0], s[2], s[4] = str(new), f"{x:.2f}", f"{z:.2f}"
            stacks.append(";".join(s))
        region_add[region_of[parent]].append(new)
    Image.fromarray(rgb, "RGB").save(out / "provinces.bmp")
    # Railways run between touching provinces: where a new province now lies between two stations, the line goes
    # through it (a railway between provinces that do not touch crashes the game when a campaign starts).
    ids = np.zeros(key.shape, dtype=np.int64)
    lookup = {k: pid for k, pid in colour_to_id.items()}
    flat_keys, inverse = np.unique(key, return_inverse=True)
    ids = np.array([lookup.get(int(k), 0) for k in flat_keys], dtype=np.int64)[inverse].reshape(key.shape)
    def pairs(m):
        found = set()
        for a, b in ((m[1:, :], m[:-1, :]), (m[:, 1:], m[:, :-1])):
            d = a != b
            found.update(np.unique(np.minimum(a[d], b[d]) * 100000 + np.maximum(a[d], b[d])).tolist())
        return found

    vanilla_touching = pairs(ids)
    for new in news:
        ids[mask == (new - min(news) + 1)] = new
    touching = pairs(ids)
    # A parent's unit positions that now lie in a cut piece move to the nearest pixel still the parent's (the game
    # logs "too far away from center" and draws the parent's units in its neighbour).
    parents = set(news.values())
    for i, line in enumerate(stacks):
        f = line.split(";")
        if len(f) < 5 or not f[0].isdigit() or int(f[0]) not in parents:
            continue
        p = int(f[0])
        x, y = int(float(f[2])), height - 1 - int(float(f[4]))
        if 0 <= y < height and 0 <= x < ids.shape[1] and ids[y, x] == p:
            continue
        ys, xs = np.nonzero(ids[max(0, y - 60):y + 60, max(0, x - 60):x + 60] == p)
        if not len(xs):
            continue
        j = int(np.argmin((xs + max(0, x - 60) - x) ** 2 + (ys + max(0, y - 60) - y) ** 2))
        nx, ny = xs[j] + max(0, x - 60), ys[j] + max(0, y - 60)
        f[2], f[4] = f"{nx + 0.5:.2f}", f"{height - 1 - ny + 0.5:.2f}"
        stacks[i] = ";".join(f)
    # A parent whose coast all went to the new province is no longer coastal (the game wants a port position for
    # every province marked coastal, and crashes on one that cannot have it).
    on_coast = set()
    for code in touching:
        a, b = divmod(code, 100000)
        if a in sea:
            on_coast.add(b)
        if b in sea:
            on_coast.add(a)
    line_of = {l.split(";")[0]: i for i, l in enumerate(lines)}
    for p in set(news.values()) | set(news):
        fields = lines[line_of[str(p)]].split(";")
        if fields[4] == "land":
            fields[5] = "true" if p in on_coast else "false"
            lines[line_of[str(p)]] = ";".join(fields)

    def touch(a, b):
        code = min(a, b) * 100000 + max(a, b)
        if a in news or b in news:
            return code in touching
        return code in touching or code not in vanilla_touching  # a crossing vanilla draws (a strait) stays

    rail_lines = []
    for line in (VANILLA / "map" / "railways.txt").read_text(encoding="utf-8-sig", errors="ignore").splitlines():
        words = line.split()
        if len(words) < 3:
            rail_lines.append(line)
            continue
        provs = [int(w) for w in words[2:]]
        fixed = [provs[0]]
        for b in provs[1:]:
            a = fixed[-1]
            if not touch(a, b):
                between = [n for n in news if touch(a, n) and touch(n, b)]
                if not between:
                    raise SystemExit(f"railway {a}-{b} is cut and no new province joins them")
                fixed.append(between[0])
            fixed.append(b)
        rail_lines.append(" ".join([words[0], str(len(fixed))] + [str(p) for p in fixed]) + " ")
    (out / "railways.txt").write_text("\n".join(rail_lines) + "\n", encoding="utf-8")
    (out / "definition.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / "unitstacks.txt").write_text("\n".join(stacks) + "\n", encoding="utf-8")
    write_strategic_regions(out, region_add)
    stamp_path.parent.mkdir(parents=True, exist_ok=True)
    stamp_path.write_text(json.dumps({"stamp": stamp, "regions": region_add}), encoding="utf-8")
    print(f"OK: {len(news)} provinces cut along Kaiserreich's state borders ({min(news)}-{max(news)})")


def write_strategic_regions(out, region_add):
    regions = out / "strategicregions"
    regions.mkdir(exist_ok=True)
    for path in regions.glob("*.txt"):
        path.unlink()
    import re
    for name, provs in region_add.items():
        text = (VANILLA / "map" / "strategicregions" / name).read_text(encoding="utf-8-sig", errors="ignore")
        text = re.sub(r"(provinces\s*=\s*\{)([^}]*)\}", lambda m: m.group(1) + m.group(2).rstrip() + " " + " ".join(map(str, provs)) + " \n\t}", text, count=1)
        (regions / name).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    compute() if "--compute" in sys.argv else build()
