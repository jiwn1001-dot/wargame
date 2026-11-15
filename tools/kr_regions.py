"""Region borders from Kaiserreich (workshop item 1521695605): python tools/kr_regions.py

Kaiserreich names its historical lands in common/scripted_triggers/_region_scripted_triggers.txt (is_bohemia,
is_transylvania, is_rhineland ...), built from its own strategic regions and states. Its map has its own provinces and
state numbers, so this maps every vanilla state onto Kaiserreich's map by pixels: both provinces.bmp files are the
same size, so each vanilla province's pixels show which Kaiserreich province, and so which Kaiserreich state, lies
under it. Each vanilla state then belongs to the smallest Kaiserreich land that holds its Kaiserreich state.

Writes tools/kr_regions.json (vanilla state -> Kaiserreich land), which settlement_decisions.py reads, so the mod
does not need Kaiserreich installed to build. Run again only if Kaiserreich or the vanilla map changes.
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

KR = Path(r"C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\1521695605")
VANILLA = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV")
OUT = Path(__file__).resolve().parent / "kr_regions.json"
# Triggers that are not a land of their own: groupings, claims, checks.
SKIP = re.compile(r"^(is_in_|has_valid_|is_island_region|is_full_germany|is_germany|is_great_britain|is_scandinavia|is_yugoslavia|"
                  r".*_claim.*|is_core_china|is_mainland_america|is_india|is_core_india|is_minimal_india|is_brazil|is_gran_colombia|"
                  r"is_southeast_asia|is_central_asia_plus_claims|is_france|is_greater_)")


def strip(text):
    return re.sub(r"#.*", "", text)


def parse(text):
    tokens = re.findall(r"[{}=]|[^\s{}=]+", strip(text))
    pos = 0

    def block():
        nonlocal pos
        items = []
        while pos < len(tokens):
            tok = tokens[pos]
            if tok == "}":
                pos += 1
                return items
            if pos + 2 < len(tokens) and tokens[pos + 1] == "=":
                key = tok
                pos += 2
                if tokens[pos] == "{":
                    pos += 1
                    items.append((key, block()))
                else:
                    items.append((key, tokens[pos]))
                    pos += 1
            else:
                pos += 1
        return items
    return block()


def provinces_of_states(root):
    out = {}
    for path in (root / "history" / "states").glob("*.txt"):
        text = strip(path.read_text(encoding="utf-8-sig", errors="ignore"))
        sid = re.search(r"\bid\s*=\s*(\d+)", text)
        provs = re.search(r"provinces\s*=\s*\{([^}]*)\}", text)
        if sid and provs:
            out[int(sid.group(1))] = [int(p) for p in provs.group(1).split()]
    return out


def regions_of_provinces(root):
    out = {}
    for path in (root / "map" / "strategicregions").glob("*.txt"):
        text = strip(path.read_text(encoding="utf-8-sig", errors="ignore"))
        rid = int(re.search(r"\bid\s*=\s*(\d+)", text).group(1))
        provs = re.search(r"provinces\s*=\s*\{([^}]*)\}", text)
        for p in (provs.group(1).split() if provs else []):
            out[int(p)] = rid
    return out


def province_map(root):
    """The province id under every pixel."""
    colours = {}
    for line in (root / "map" / "definition.csv").read_text(encoding="utf-8-sig", errors="ignore").splitlines():
        parts = line.split(";")
        if len(parts) > 3 and parts[0].isdigit():
            colours[(int(parts[1]) << 16) | (int(parts[2]) << 8) | int(parts[3])] = int(parts[0])
    pixels = np.asarray(Image.open(root / "map" / "provinces.bmp").convert("RGB"), dtype=np.uint32)
    keys = (pixels[..., 0] << 16) | (pixels[..., 1] << 8) | pixels[..., 2]
    lookup = np.zeros(keys.max() + 1, dtype=np.int32)
    for key, pid in colours.items():
        if key < len(lookup):
            lookup[key] = pid
    return lookup[keys]


def main():
    v_prov, k_prov = province_map(VANILLA), province_map(KR)
    assert v_prov.shape == k_prov.shape, "the two maps differ in size"
    k_state_of_prov = {p: s for s, ps in provinces_of_states(KR).items() for p in ps}
    k_region = regions_of_provinces(KR)
    k_states = provinces_of_states(KR)
    # Vanilla province -> the Kaiserreich province under most of its pixels.
    flat_v, flat_k = v_prov.ravel(), k_prov.ravel()
    pairs = Counter(zip(flat_v.tolist(), flat_k.tolist()))
    best = {}
    for (vp, kp), n in pairs.items():
        if vp and kp and n > best.get(vp, (0, 0))[1]:
            best[vp] = (kp, n)
    # Vanilla state -> Kaiserreich state, by its provinces' votes.
    v_to_k = {}
    for sid, ps in provinces_of_states(VANILLA).items():
        votes = Counter(k_state_of_prov.get(best[p][0]) for p in ps if p in best and best[p][0] in k_state_of_prov)
        if votes:
            v_to_k[sid] = votes.most_common(1)[0][0]
    # Kaiserreich state facts: its strategic region (by most provinces).
    k_state_region = {}
    for s, ps in k_states.items():
        votes = Counter(k_region.get(p) for p in ps if p in k_region)
        if votes:
            k_state_region[s] = votes.most_common(1)[0][0]
    # Evaluate the land triggers on Kaiserreich states.
    triggers = dict(parse((KR / "common" / "scripted_triggers" / "_region_scripted_triggers.txt").read_text(encoding="utf-8-sig", errors="ignore")))
    memo = {}

    def holds(name, state, depth=0):
        key = (name, state)
        if key not in memo:
            memo[key] = all_of(triggers.get(name, []), state, depth + 1) if depth < 40 else False
        return memo[key]

    def one(key, value, state, depth):
        if key == "OR":
            return any(one(k, v, state, depth) for k, v in value)
        if key == "AND":
            return all_of(value, state, depth)
        if key == "NOT":
            return not any(one(k, v, state, depth) for k, v in value)
        if key == "region":
            return k_state_region.get(state) == int(value)
        if key == "state":
            return state == int(value)
        if key in triggers:
            return holds(key, state, depth) == (value == "yes")
        return False  # flags, owners and continents: not a matter of borders

    def all_of(items, state, depth):
        return all(one(k, v, state, depth) for k, v in items)

    lands = {}
    for name in triggers:
        if SKIP.match(name):
            continue
        members = {s for s in k_states if holds(name, s)}
        if members:
            lands[name] = members
    # Each vanilla state: the smallest land that holds its Kaiserreich state.
    out = {}
    for sid, ks in v_to_k.items():
        fits = [(len(m), name) for name, m in lands.items() if ks in m]
        if fits:
            out[sid] = min(fits)[1]
    OUT.write_text(json.dumps({str(k): v for k, v in sorted(out.items())}, ensure_ascii=False, indent=0), encoding="utf-8")
    used = Counter(out.values())
    print(f"OK: {len(out)} of {len(provinces_of_states(VANILLA))} vanilla states placed in {len(used)} Kaiserreich lands")
    return out, used


if __name__ == "__main__":
    main()
