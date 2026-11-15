"""Check the laid-out map for what crashes the game when a campaign starts: python tools/check_layout.py

The game checks little of the map when it loads and crashes at the start of a campaign instead, without a crash
report. This step looks for every such case known (each one crashed this mod once, or crashes others):

  - provinces: every land province in exactly one state; definition.csv numbered without gaps, one colour each, every
    colour in provinces.bmp defined; every province in exactly one strategic region; unit positions for new ones;
  - states: numbered without gaps; each in one strategic region; buildings within their caps and the state's slots;
    a dockyard only where the state has a naval base; naval bases only on coasts; victory points in the state;
  - building positions: every state has a position for every kind vanilla gives every state; a port's spawn position
    lies in the port's own province and state;
  - countries: each holds its capital; air wings of the 1936 orders of battle are based in a state of their own with
    an air base; fleets lie in a port of their own.
A problem vanilla has too is not counted (vanilla's own states are checked the same way, and only what is new fails).
"""
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import kr_layout as K  # noqa: E402

MOD, VANILLA = K.MOD, K.VANILLA
errors = []


def states_in(folder_files):
    out = {}
    for path in folder_files:
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        if re.search(r"\bid\s*=\s*\d+", re.sub(r"#[^\n]*", "", text)):
            s = K.read_state(text)
            out[s["id"]] = s
    return out


def building_caps():
    caps = {}
    for path in (VANILLA / "common" / "buildings").glob("*.txt"):
        for name, body in K.get(K.parse(path.read_text(encoding="utf-8-sig", errors="ignore")), "buildings", []):
            if isinstance(body, list):
                cap = K.get(body, "level_cap", [])
                caps[name] = (float(K.get(cap, "state_max", "0") or 0), float(K.get(cap, "province_max", "0") or 0),
                              K.get(cap, "shares_slots") == "yes")
    return caps


def problems(states, rows, prov_map, height, coastal, region_of, slots, caps):
    """Problems of one set of states and building positions, as (kind, state, detail)."""
    out = set()
    state_of = {p: sid for sid, s in states.items() for p in s["provinces"]}

    def at(x, z):
        r, c = height - 1 - int(float(z)), int(float(x))
        return int(prov_map[r, c]) if 0 <= r < height and 0 <= c < prov_map.shape[1] else 0

    kinds = defaultdict(set)
    spawn_provs = defaultdict(set)
    for r in rows:
        sid = int(r[0])
        kinds[sid].add(r[1])
        if r[1] == "naval_base_spawn":
            p = at(r[2], r[4])
            spawn_provs[sid].add(p)
            if state_of.get(p) != sid:
                out.add(("port position in another state", sid, p))
    universal = set.intersection(*kinds.values()) if kinds else set()
    for sid, s in states.items():
        regions = {region_of.get(p) for p in s["provinces"]}
        if len(regions) > 1:
            out.add(("state in several strategic regions", sid, tuple(sorted(map(str, regions)))))
        if None in regions:
            out.add(("province in no strategic region", sid, None))
        for kind in universal - kinds[sid]:
            out.add(("no building position", sid, kind))
        naval = [p for p, b in s["province_blocks"].items() if K.get(b, "naval_base")]
        if s["levels"].get("dockyard") and not any(p in coastal for p in s["provinces"]):
            out.add(("dockyard in a state without a sea coast", sid, None))
        for p in naval:
            if p not in coastal:
                out.add(("naval base inland", sid, p))
            if p not in spawn_provs[sid]:
                out.add(("naval base without spawn position", sid, p))
        shared = 0
        for name, level in s["levels"].items():
            state_max, _, shares = caps.get(name, (0, 0, False))
            if state_max and level > state_max:
                out.add(("building over its cap", sid, name))
            if shares:
                shared += level
        extra = sum(float(v) for k, v in s["extras"] if k == "add_extra_state_shared_building_slots" and not isinstance(v, list))
        if shared > slots.get(s["category"], 0) + extra:
            out.add(("more factories than slots", sid, s["category"]))
        if s["category"] not in slots:
            out.add(("unknown state category", sid, s["category"]))
        for p, block in s["province_blocks"].items():
            if p not in s["provinces"]:
                out.add(("province building outside the state", sid, p))
            for name, level in block:
                _, province_max, _ = caps.get(name, (0, 0, False))
                if province_max and not isinstance(level, list) and level is not None and float(level) > province_max:
                    out.add(("province building over its cap", sid, (p, name)))
        for p, _ in s["vps"]:
            if p not in s["provinces"]:
                out.add(("victory point outside the state", sid, p))
    return out


def main():
    import numpy as np
    from PIL import Image
    shared_names, slots = K.building_rules()
    caps = building_caps()
    # The map.
    definition = [l.split(";") for l in K.map_file("definition.csv").read_text(encoding="utf-8-sig", errors="ignore").splitlines()
                  if l.split(";")[0].isdigit()]
    ids = [int(r[0]) for r in definition]
    if ids != list(range(len(ids))):
        errors.append("definition.csv: province numbers have gaps or are out of order")
    colours = Counter((r[1], r[2], r[3]) for r in definition)
    if any(n > 1 for n in colours.values()):
        errors.append("definition.csv: two provinces share a colour")
    prov_map = K.province_pixels()
    present = set(np.unique(prov_map).tolist())
    land = {int(r[0]) for r in definition if r[4] == "land"}
    coastal = {int(r[0]) for r in definition if r[5].strip().lower() == "true"}
    region_files = {p.name: p for p in (VANILLA / "map" / "strategicregions").glob("*.txt")}
    region_files.update({p.name: p for p in (MOD / "map" / "strategicregions").glob("*.txt")})
    region_of, seen = {}, Counter()
    for path in region_files.values():
        text = re.sub(r"#[^\n]*", "", path.read_text(encoding="utf-8-sig", errors="ignore"))
        rid = int(re.search(r"\bid\s*=\s*(\d+)", text).group(1))
        for p in re.search(r"provinces\s*=\s*\{([^}]*)\}", text).group(1).split():
            region_of[int(p)] = rid
            seen[int(p)] += 1
    if [p for p, n in seen.items() if n > 1]:
        errors.append(f"provinces in two strategic regions: {[p for p, n in seen.items() if n > 1][:10]}")
    import kr_provinces
    news = kr_provinces.new_provinces()
    for p in news:
        if p not in present:
            errors.append(f"new province {p} is not on provinces.bmp")
        if p not in region_of:
            errors.append(f"new province {p} is in no strategic region")
    # Which provinces touch: railways must run between touching provinces, and a port must touch its sea.
    touching = set()
    for a, b in ((prov_map[1:, :], prov_map[:-1, :]), (prov_map[:, 1:], prov_map[:, :-1])):
        d = a != b
        touching.update(np.unique(np.minimum(a[d], b[d]).astype(np.int64) * 100000 + np.maximum(a[d], b[d])).tolist())

    def touch(a, b):
        return min(a, b) * 100000 + max(a, b) in touching

    vanilla_map = __import__("kr_regions").province_map(VANILLA)
    touching_vanilla = set()
    for a, b in ((vanilla_map[1:, :], vanilla_map[:-1, :]), (vanilla_map[:, 1:], vanilla_map[:, :-1])):
        d = a != b
        touching_vanilla.update(np.unique(np.minimum(a[d], b[d]).astype(np.int64) * 100000 + np.maximum(a[d], b[d])).tolist())

    def touch_vanilla(a, b):
        return min(a, b) * 100000 + max(a, b) in touching_vanilla

    for line in K.map_file("railways.txt").read_text(encoding="utf-8-sig", errors="ignore").splitlines():
        words = line.split()
        if len(words) >= 3:
            provs = [int(w) for w in words[2:]]
            if int(words[1]) != len(provs):
                errors.append(f"railway with a wrong count: {line.strip()}")
            for a, b in zip(provs, provs[1:]):
                if not touch(a, b) and (a in news or b in news or touch_vanilla(a, b)):  # vanilla's straits stay
                    errors.append(f"railway between provinces that do not touch: {a}-{b}")
    stacks = Counter(l.split(";")[0] for l in K.map_file("unitstacks.txt").read_text(encoding="utf-8-sig", errors="ignore").splitlines())
    for p in news:
        if stacks[str(p)] < 10:
            errors.append(f"new province {p} has no unit positions")
    # The states.
    final = states_in((MOD / "history" / "states").glob("*.txt"))
    if sorted(final) != list(range(1, len(final) + 1)):
        errors.append("states: numbers have gaps")
    count = Counter(p for s in final.values() for p in s["provinces"])
    if [p for p, n in count.items() if n > 1]:
        errors.append(f"provinces in two states: {[p for p, n in count.items() if n > 1][:10]}")
    vanilla = states_in((VANILLA / "history" / "states").glob("*.txt"))
    wanted = {p for s in vanilla.values() for p in s["provinces"]} | set(news)
    missing = wanted - set(count)
    if missing:
        errors.append(f"provinces in no state: {sorted(missing)[:10]}")
    rows = [l.split(";") for l in (MOD / "map" / "buildings.txt").read_text(encoding="utf-8").splitlines() if l]
    vrows = [l.split(";") for l in (VANILLA / "map" / "buildings.txt").read_text(encoding="utf-8-sig", errors="ignore").splitlines()
             if len(l.split(";")) >= 7 and l.split(";")[0].isdigit()]
    height = prov_map.shape[0]
    # Every coastal province has a port position standing on it, filed under its state (else the game crashes:
    # "setup as coastal but has no port building in the nudger"); no position stands on a lake.
    kind_of = {int(r[0]): r[4] for r in definition}
    state_of_final = {p: sid for sid, s in final.items() for p in s["provinces"]}
    ported = set()
    on_water = 0
    for r in rows:
        here = int(prov_map[height - 1 - int(float(r[4])), int(float(r[2]))])
        if r[1] == "naval_base_spawn" and state_of_final.get(here) == int(r[0]):
            ported.add(here)
        if r[1] not in ("floating_harbor", "naval_base_spawn") and kind_of.get(here) != "land":
            on_water += 1
    unported = sorted(p for p in coastal if kind_of.get(p) == "land" and p in state_of_final and p not in ported)
    if unported:
        errors.append(f"coastal provinces without a port position: {unported[:10]}")
    vanilla_on_water = sum(1 for r in vrows if r[1] not in ("floating_harbor", "naval_base_spawn")
                           and kind_of.get(int(vanilla_map[height - 1 - int(float(r[4])), int(float(r[2]))])) != "land")
    if on_water > vanilla_on_water:
        errors.append(f"building positions on water: {on_water} (vanilla {vanilla_on_water})")
    # No new corner where four provinces meet or two cross (the game's "invalid X crossing").

    def crossings(m):
        a, b, c, d = m[:-1, :-1], m[:-1, 1:], m[1:, :-1], m[1:, 1:]
        return ((a != b) & (a != c) & (a != d) & (b != c) & (b != d) & (c != d)) | ((a == d) & (b == c) & (a != b))

    new_crossings = int((crossings(prov_map) & ~crossings(vanilla_map)).sum())
    if new_crossings:
        errors.append(f"{new_crossings} new X crossings on provinces.bmp")
    # Sea regions keep vanilla's land (an island moved out leaves the region "fractioned").
    vanilla_region = {}
    for path in (VANILLA / "map" / "strategicregions").glob("*.txt"):
        text = re.sub(r"#[^\n]*", "", path.read_text(encoding="utf-8-sig", errors="ignore"))
        rid = int(re.search(r"\bid\s*=\s*(\d+)", text).group(1))
        for p in re.search(r"provinces\s*=\s*\{([^}]*)\}", text).group(1).split():
            vanilla_region[int(p)] = rid
    naval = {rid for p, rid in vanilla_region.items() if kind_of.get(p) == "sea"}
    moved_at_sea = [p for p, rid in vanilla_region.items() if region_of.get(p) != rid and (rid in naval or region_of.get(p) in naval)]
    if moved_at_sea:
        errors.append(f"provinces moved into or out of a sea region: {moved_at_sea[:10]}")
    cut_off = [(r[0], r[6]) for r in rows if r[1] == "naval_base_spawn" and r[6] != "0"
               and not touch(int(prov_map[height - 1 - int(float(r[4])), int(float(r[2]))]), int(r[6]))]
    if cut_off:
        errors.append(f"ports that do not touch their sea: {cut_off[:5]}")
    vmap =__import__("kr_regions").province_map(VANILLA)
    known = {(kind, detail if kind != "no building position" else detail) for kind, _, detail in
             problems(vanilla, vrows, vmap, vmap.shape[0], coastal, region_of, slots, caps)}
    known_kinds = Counter(kind for kind, _, _ in problems(vanilla, vrows, vmap, vmap.shape[0], coastal, region_of, slots, caps))
    found = problems(final, rows, prov_map, height, coastal, region_of, slots, caps)
    by_kind = defaultdict(list)
    for kind, sid, detail in found:
        by_kind[kind].append((sid, detail))
    for kind, items in sorted(by_kind.items()):
        if len(items) > known_kinds.get(kind, 0):  # more than vanilla has of the same
            errors.append(f"{kind}: {len(items)} (vanilla {known_kinds.get(kind, 0)}), e.g. {sorted(items, key=str)[:5]}")
    # The start effect must not move states again: the histories own that (moving them at the start undid the layout
    # and left states owned with no occupation data, which crashed the first day).
    start = MOD / "common" / "scripted_effects" / "lr_world_effects.txt"
    if start.exists():
        body = re.search(r"lr_setup_world\s*=\s*\{(.*?)\n\}", start.read_text(encoding="utf-8-sig"), re.S)
        if body and "transfer_state" in body.group(1):
            errors.append("lr_setup_world moves states at the start (the state histories already set every owner)")
    # The countries.
    owner_of = {sid: s["owner"] for sid, s in final.items()}
    holders = set(owner_of.values())
    files = {p.name: p for p in (VANILLA / "history" / "countries").glob("*.txt")}
    files.update({p.name: p for p in (MOD / "history" / "countries").glob("*.txt")})
    oobs = set()
    for name, path in files.items():
        tag = name[:3]
        if tag not in holders:
            continue
        text = re.sub(r"#[^\n]*", "", path.read_text(encoding="utf-8-sig", errors="ignore"))
        text = re.sub(r"\n\d+\.\d+\.\d+\s*=\s*\{.*", "", text, flags=re.S)  # the 1936 start only
        found_capital = re.search(r"^\s*capital\s*=\s*(\d+)", text, re.M)
        if found_capital and owner_of.get(int(found_capital.group(1))) != tag:
            errors.append(f"{tag}: capital {found_capital.group(1)} is not its own")
        oobs |= {(tag, o) for o in re.findall(r'\b(?:oob|set_naval_oob|set_air_oob|load_oob)\s*=\s*"([^"]+)"', text)}
    units = {p.stem: p for p in (VANILLA / "history" / "units").glob("*.txt")}
    units.update({p.stem: p for p in (MOD / "history" / "units").glob("*.txt")})
    state_of = {p: sid for sid, s in final.items() for p in s["provinces"]}
    air_positions = {int(r[0]) for r in rows if r[1] == "air_base"}
    ports = {p for s in final.values() for p, b in s["province_blocks"].items() if K.get(b, "naval_base")}
    for tag, oob in sorted(oobs):
        path = units.get(oob)
        if not path:
            continue
        top = K.parse(path.read_text(encoding="utf-8-sig", errors="ignore"))
        for key, value in K.get(top, "air_wings", []):
            if key and key.isdigit():
                sid = int(key)
                s = final.get(sid)
                if not s or s["owner"] != tag or s["levels"].get("air_base", 0) <= 0 or sid not in air_positions:
                    errors.append(f"{oob}: air wings in state {sid} ({s and s['owner']}, air base {s and s['levels'].get('air_base', 0)})")
        for key, value in K.get(top, "units", []):
            if key == "fleet" and isinstance(value, list):
                base = K.get(value, "naval_base")
                # A fleet at a province with no naval base crashes the campaign start ("move navy to land province").
                if base and int(base) not in ports:
                    errors.append(f"{oob}: a fleet's port {base} has no naval base")
                if base and owner_of.get(state_of.get(int(base))) != tag:
                    # The game moves such a fleet home (Poland's at Gdynia ran before the layout too): a note only.
                    print(f"note: {oob}: a fleet's port {base} is not {tag}'s")
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print(f"OK: {len(final)} states, {len(ids)} provinces ({len(news)} new), {len(rows)} building positions, "
          f"{len(oobs)} orders of battle checked")


if __name__ == "__main__":
    main()
