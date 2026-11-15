"""Territory decisions after the peace conference, as Kaiserreich's annexation decisions: one state at a time, on the
map. build_france.py writes the files.

Every state France holds that is not its core shows its choices in the decision map view (state_target):
  annex          - a French core, where this government has claimed it (the route's integration event fires)
  puppet_<tag>   - to the land's own country as France's puppet, if that country is gone or already France's subject
  cede_<tag>     - to any standing country with a core or claim on it, one decision per such country
  revive_<tag>   - a vanished country with a core on it raised again on this state alone, as France's puppet
  free_<tag>     - the same, as a free country
A release hands a country every core France holds; everything but the chosen state comes straight back, so freeing
Prussia from one state does not take the Rhineland with it. The AI annexes what it claims, hands land to a subject
or ally with a core or claim there, raises vanished claimants as puppets, and sets up the land's own country last.
regions() still names the land's own country for each state (Kaiserreich's lands, or the 1936 owner).
"""
from pathlib import Path

import build_world as world
import integration_routes

# key: (name, states, puppet tag)
# Land kept apart by hand from Kaiserreich's lands: Catalonia, which Napoleon's France claims on its own, Königsberg,
# and the Kingdom of Sardinia's historical parts.
SPLIT = {
    "SPR": [("spr_catalonia", "카탈루냐", [165], "CAT")],
    # Königsberg alone, apart from the rest of East Prussia.
    "GER": [("ger_konigsberg", "쾨니히스베르크", [763], "GER")],
    # The Kingdom of Sardinia, by its historical parts (the states cut by tools/split_states.py).
    "ITA": [("ita_savoy_nice", "사부아와 니스", [735, 1129, 1130], "ITA"),
            ("ita_piedmont", "피에몬테", [158, 1112, 1134, 1135, 1136], "ITA"),
            ("ita_liguria", "리구리아", [1111, 1138], "ITA"),
            ("ita_sardinia", "사르데냐섬", [114, 1137], "ITA")],
}
ICON = "generic_civil_support"


def start_owners():
    import split_states
    final = dict(world.vanilla_states())
    for tag, states in world.TRANSFERS.items():
        for state in states:
            final[state] = tag
    overrides = split_states.owner_overrides()
    for orig, parts in split_states.pieces().items():
        for new, _ in parts:
            final[new] = overrides.get(new, final.get(new, final.get(orig)))
    return final


KOREAN = world.VANILLA / "localisation" / "korean"


def korean_names():
    """STATE_n, STRATEGICREGION_n and country names, from the game's Korean files and the mod's own country names."""
    import re
    names = {}
    files = [KOREAN / "state_names_l_korean.yml", KOREAN / "strategic_region_names_l_korean.yml"]
    files += sorted(KOREAN.glob("countries*_l_korean.yml"))
    files += sorted((world.MOD / "localisation" / "korean" / "replace").glob("*.yml"))
    for path in files:
        if path.exists():
            for key, value in re.findall(r'^\s*([\w.]+):\d*\s*"(.*)"', path.read_text(encoding="utf-8-sig", errors="ignore"), re.M):
                names[key] = value
    return names


def state_regions():
    """state -> strategic region, by where most of its provinces lie."""
    import re
    from collections import Counter
    prov_sr = {}
    for path in (world.VANILLA / "map" / "strategicregions").glob("*.txt"):
        text = re.sub(r"#.*", "", path.read_text(encoding="utf-8-sig", errors="ignore"))
        sr = int(re.search(r"\bid\s*=\s*(\d+)", text).group(1))
        found = re.search(r"provinces\s*=\s*\{([^}]*)\}", text)
        for prov in (found.group(1).split() if found else []):
            prov_sr[int(prov)] = sr
    out = {}
    for path in (world.VANILLA / "history" / "states").glob("*.txt"):
        text = re.sub(r"#.*", "", path.read_text(encoding="utf-8-sig", errors="ignore"))
        sid = int(re.search(r"\bid\s*=\s*(\d+)", text).group(1))
        found = re.search(r"provinces\s*=\s*\{([^}]*)\}", text)
        votes = Counter(prov_sr[int(p)] for p in (found.group(1).split() if found else []) if int(p) in prov_sr)
        if votes:
            out[sid] = votes.most_common(1)[0][0]
    import split_states
    for orig, parts in split_states.pieces().items():
        for new, provs in parts:
            votes = Counter(prov_sr[p] for p in provs if p in prov_sr)
            if votes:
                out[new] = votes.most_common(1)[0][0]
    return out


MAX_REGION = 4  # only names the land's own country now (regions()); the decisions themselves are per state


def centres():
    """state -> (x, z) on the map, the mean of its building positions (map/buildings.txt)."""
    sums = {}
    source = world.MOD / "map" / "buildings.txt"
    source = source if source.exists() else world.VANILLA / "map" / "buildings.txt"
    for line in source.read_text(encoding="utf-8-sig", errors="ignore").splitlines():
        parts = line.split(";")
        if len(parts) >= 5 and parts[0].isdigit():
            x, z = float(parts[2]), float(parts[4])
            total = sums.setdefault(int(parts[0]), [0.0, 0.0, 0])
            total[0] += x
            total[1] += z
            total[2] += 1
    return {sid: (t[0] / t[2], t[1] / t[2]) for sid, t in sums.items() if t[2]}


def clusters(states, where, size=MAX_REGION):
    """Cut a list of states into geographic groups of at most about `size`, by k-means on their map positions."""
    import math
    known = [s for s in states if s in where]
    if len(states) <= size or len(known) < 2:
        return [states]
    k = math.ceil(len(states) / (size - 1))
    ordered = sorted(known, key=lambda s: where[s])
    seeds = [where[ordered[round(i * (len(ordered) - 1) / (k - 1))]] for i in range(k)]
    for _ in range(20):
        groups = [[] for _ in range(k)]
        for s in known:
            x, z = where[s]
            groups[min(range(k), key=lambda i: (seeds[i][0] - x) ** 2 + (seeds[i][1] - z) ** 2)].append(s)
        seeds = [(sum(where[s][0] for s in g) / len(g), sum(where[s][1] for s in g) / len(g)) if g else seeds[i] for i, g in enumerate(groups)]
    groups = [sorted(g) for g in groups if g]
    groups[0] += [s for s in states if s not in where]
    return groups


def kr_lands():
    """vanilla state -> Kaiserreich land (tools/kr_regions.json, written by kr_regions.py)."""
    import json
    path = Path(__file__).resolve().parent / "kr_regions.json"
    lands = {int(k): v for k, v in json.loads(path.read_text(encoding="utf-8")).items()} if path.exists() else {}
    import split_states
    for orig, parts in split_states.pieces().items():
        for new, _ in parts:
            if orig in lands:
                lands[new] = lands[orig]
    return lands


def existing_tags():
    import re
    tags = set()
    for root in (world.VANILLA, world.MOD):
        for path in (root / "common" / "country_tags").glob("*.txt"):
            tags |= set(re.findall(r"^\s*([A-Z][A-Z0-9]{2})\s*=", path.read_text(encoding="utf-8-sig", errors="ignore"), re.M))
    return tags


def state_tags():
    """state -> (countries with a core there, countries with a claim there) in 1936, from the state histories."""
    import kr_layout
    files = {p.name: p for p in (world.VANILLA / "history" / "states").glob("*.txt")}
    files.update({p.name: p for p in (world.MOD / "history" / "states").glob("*.txt")})
    out = {}
    for path in files.values():
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        if "Generated by tools/kr_layout.py" in text[:200]:
            continue  # only the earlier steps' states (vanilla numbers) are this step's input
        try:
            s = kr_layout.read_state(text)
        except Exception:
            continue
        out[s["id"]] = (set(s["cores"]), set(s["claims"]))
    return out


MAX_CLAIMANTS = None  # per region: every country with a core or claim on its states, most first


def claimants(states, tags, puppet, known):
    """The countries other than France and the region's own that hold a core or claim on the region's states."""
    from collections import Counter
    count = Counter()
    for s in states:
        cores, claims = tags.get(s, (set(), set()))
        for tag in cores | claims:
            if tag not in ("FRA", puppet) and tag in known:
                count[tag] += 1
    return [t for t, _ in count.most_common(MAX_CLAIMANTS)]


def regions():
    """Each region: Kaiserreich's land (or, where it names none, the strategic region) and the 1936 owner, cut into
    geographic pieces of at most MAX_REGION states."""
    from collections import defaultdict
    import kr_land_names
    owners = start_owners()
    names = korean_names()
    lands = kr_lands()
    tags = existing_tags()
    out = []
    for tag, parts in SPLIT.items():
        out += parts
    hand = {s for parts in SPLIT.values() for _, _, states, _ in parts for s in states}
    groups = defaultdict(list)
    for sid, sr in state_regions().items():
        owner = owners.get(sid)
        if owner and owner != "FRA" and sid not in hand:
            groups[(lands.get(sid) or f"sr{sr}", owner)].append(sid)
    shared = defaultdict(int)
    for land, owner in groups:
        shared[land] += 1
    where = centres()
    for (land, owner), states in sorted(groups.items()):
        states.sort()
        if land.startswith("sr"):
            region_name = names.get(f"STRATEGICREGION_{land[2:]}") or f"{land[2:]}번 지역"
            puppet = owner
        else:
            region_name = kr_land_names.NAMES.get(land, land)
            puppet = kr_land_names.PUPPET.get(land, owner)
            puppet = puppet if puppet in tags else owner
        # Vanilla's strategic regions say 미국 (the United States), which this world never had.
        region_name = region_name.replace("미국령", "북아메리카령").replace("미국", "북아메리카")
        parts = clusters(states, where)
        for number, part in enumerate(parts, start=1):
            if len(parts) > 1 and len(part) == 1:
                base = f"{region_name} ({names.get(f'STATE_{part[0]}', part[0])})"
            elif len(parts) > 1:
                # Named after the state nearest the piece's middle.
                cx = sum(where[s][0] for s in part if s in where) / max(1, sum(1 for s in part if s in where))
                cz = sum(where[s][1] for s in part if s in where) / max(1, sum(1 for s in part if s in where))
                middle = min((s for s in part if s in where), key=lambda s: (where[s][0] - cx) ** 2 + (where[s][1] - cz) ** 2, default=part[0])
                base = f"{region_name} ({names.get(f'STATE_{middle}', middle)} 일대)"
            elif land.startswith("sr") and len(part) == 1:
                base = names.get(f"STATE_{part[0]}") or region_name
            else:
                base = region_name
            if shared[land] > 1:
                base += f" - {names.get(owner, owner)}"
            key = f"{land.removeprefix('is_')}_{owner.lower()}" + (f"_{number}" if len(parts) > 1 else "")
            out.append((key, base, part, puppet))
    # Names that still repeat get a number.
    seen = {}
    for i, (key, name, states, puppet) in enumerate(out):
        seen[name] = seen.get(name, 0) + 1
        if seen[name] > 1:
            out[i] = (key, f"{name} {seen[name]}", states, puppet)
    return out


def eul(word):
    """The object particle after a Korean word: 을 after a final consonant, 를 after a vowel."""
    last = word.rstrip()[-1]
    return word + ("을" if "가" <= last <= "힣" and (ord(last) - 0xAC00) % 28 else "를")


def tab(text, n):
    return "\n".join("\t" * n + line for line in text.split("\n"))


def build():
    """Kaiserreich-style decisions on the map: every state France holds that is not its core shows its own choices
    in the decision map view (state_target), so a choice settles that one state and nothing else."""
    integ = integration_routes
    tags_on = state_tags()
    known = existing_tags()
    puppet_of = {s: puppet for _, _, states, puppet in regions() for s in states}
    held = "FROM = {\n\tis_owned_by = ROOT\n\tNOT = { is_core_of = ROOT }\n}"
    lines = ["# Generated by tools/settlement_decisions.py.", "LR_FRA_settlement_category = {"]
    loc = [' LR_FRA_settlement_category:0 "영토 결단"',
           ' LR_FRA_settlement_category_desc:0 "평화 회의에서 얻은 땅의 운명을 주마다 정한다. 지도에서 프랑스가 가진 주를 고르면 그 주에 맞는 선택지가 나온다. '
           '영유권이 있으면 합병하고, 그 땅에 핵심주나 영유권이 있는 나라에 넘기거나, 사라진 나라를 되살린다."']

    def decision(name, cost, targets, trigger, effect, ai, label, desc):
        target_line = f"\t\ttargets = {{ {' '.join(map(str, sorted(targets)))} }}\n\t\ttargets_dynamic = no\n" if targets else ""
        # map_only: the choices show on the state in the decision map view, not as hundreds of lines in the list.
        lines.append(f"\t{name} = {{\n\t\ticon = {ICON}\n\t\tcost = {cost}\n\t\tstate_target = yes\n\t\ton_map_mode = map_only\n"
                     f"{target_line}\t\ttarget_root_trigger = {{ tag = FRA }}\n"
                     f"\t\ttarget_trigger = {{\n{tab(held, 3)}\n{tab(trigger, 3) if trigger else ''}\n\t\t}}\n"
                     f"\t\tcomplete_effect = {{\n{tab(effect, 3)}\n\t\t}}\n\t\tai_will_do = {{\n{tab(ai, 3)}\n\t\t}}\n\t}}")
        loc.extend([f' {name}:0 "{label}"', f' {name}_desc:0 "{desc}"'])

    # Annex: a French core where this government has claimed the land; the route's integration event for it fires.
    events = []
    for (prefix, region), _ in integ.T.items():
        if region == "algeria":
            continue
        route = integ.ROUTES[prefix][0]
        flag = f"LR_integ_{prefix[3:6].lower()}_{region}"
        inside = "OR = { " + " ".join(f"state = {s}" for s in integ.REGIONS[region]) + " }"
        events.append(f"if = {{\n\tlimit = {{\n\t\thas_country_flag = {route}\n\t\tNOT = {{ has_country_flag = {flag} }}\n\t\tFROM = {{ {inside} }}\n\t}}\n"
                      f"\tset_country_flag = {flag}\n\tcountry_event = {integ.event_id(prefix, region)}\n}}")
    decision("LR_dec_settle_annex", 50, None, "FROM = { is_claimed_by = ROOT }",
             "FROM = { add_core_of = ROOT }" + ("\n" + "\n".join(events) if events else ""), "factor = 10",
             "합병", "이 주를 프랑스의 땅으로 삼는다. 지금의 정부가 영유권을 주장한 주에만 쓸 수 있다.")

    # The land's own country as France's puppet (only if it is gone or already France's subject).
    by_puppet = {}
    for s, puppet in puppet_of.items():
        if puppet in known and puppet != "FRA":
            by_puppet.setdefault(puppet, set()).add(s)
    for tag, states in sorted(by_puppet.items()):
        decision(f"LR_dec_settle_puppet_{tag.lower()}", 25, states, f"{tag} = {{\n\tOR = {{\n\t\texists = no\n\t\tis_subject_of = ROOT\n\t}}\n}}",
                 f"if = {{\n\tlimit = {{ {tag} = {{ exists = yes }} }}\n\t{tag} = {{ transfer_state = FROM }}\n}}\n"
                 f"else = {{\n\t{tag} = {{ transfer_state = FROM }}\n\tset_autonomy = {{\n\t\ttarget = {tag}\n\t\tautonomous_state = autonomy_puppet\n\t}}\n"
                 f"\t{tag} = {{ lr_fra_name_puppet = yes }}\n}}",
                 "factor = 3", f"괴뢰국 수립: [{tag}.GetName]",
                 f"이 주를 [{tag}.GetName]의 땅으로 삼고, 그 나라를 프랑스의 보호 아래 둔다. 그 나라의 이름과 정부는 지금 프랑스의 체제를 따른다.")

    # Every country with a core or claim on the state: hand it over, or raise the vanished country again.
    claims_on, cores_on = {}, {}
    for s, (cores, claims) in tags_on.items():
        for tag in cores | claims:
            claims_on.setdefault(tag, set()).add(s)
        for tag in cores:
            cores_on.setdefault(tag, set()).add(s)
    keep = ("FROM = { set_state_flag = LR_settle_keep }\n"
            "every_state = {\n\tlimit = {\n\t\tis_owned_by = TAG\n\t\tNOT = { has_state_flag = LR_settle_keep }\n\t}\n\tROOT = { transfer_state = PREV }\n}\n"
            "FROM = { clr_state_flag = LR_settle_keep }")
    # Kaiserreich's historical claims are added to the states at the end of the build (kr_layout.py), after these
    # numbers: those countries get the decisions too, and the hand-over decisions look at every state, not a list.
    import json
    import kr_layout
    kr_tags = {t for c in json.loads(kr_layout.DATA.read_text(encoding="utf-8")).get("kr_claims", {}).values() for t in c}
    for t in kr_tags:
        claims_on.setdefault(t, set())
    for tag in sorted(t for t in claims_on if t in known and t != "FRA"):
        friend = f"{tag} = {{\n\tOR = {{\n\t\tis_in_faction_with = ROOT\n\t\tis_subject_of = ROOT\n\t}}\n}}"
        decision(f"LR_dec_settle_cede_{tag.lower()}", 10, None,
                 f"{tag} = {{\n\texists = yes\n\tNOT = {{ has_war_with = ROOT }}\n}}\nFROM = {{ OR = {{ is_core_of = {tag} is_claimed_by = {tag} }} }}",
                 f"{tag} = {{ transfer_state = FROM }}", f"factor = 0\nmodifier = {{\n\tadd = 6\n{tab(friend, 1)}\n}}",
                 f"할양: [{tag}.GetName]", f"이 주를 핵심주나 영유권을 가진 [{tag}.GetName]에 넘긴다.")
        if tag not in cores_on:
            continue
        revive = f"{tag} = {{ exists = no }}\nFROM = {{ is_core_of = {tag} }}"
        decision(f"LR_dec_settle_revive_{tag.lower()}", 25, cores_on[tag], revive,
                 f"release_puppet = {tag}\n{keep.replace("TAG", tag)}\n{tag} = {{ lr_fra_name_puppet = yes }}", "factor = 4",
                 f"괴뢰국 재건: [{tag}.GetName]", f"사라진 나라 [{tag}.GetName]을 이 주에 되살려 프랑스의 보호 아래 둔다. 다른 주는 프랑스령으로 남는다.")
        decision(f"LR_dec_settle_free_{tag.lower()}", 10, cores_on[tag], revive,
                 f"release = {tag}\n{keep.replace("TAG", tag)}", "factor = 0",
                 f"독립: [{tag}.GetName]", f"사라진 나라 [{tag}.GetName]을 이 주에 독립국으로 되살린다. 다른 주는 프랑스령으로 남는다.")
    lines.append("}")
    category = ("# Generated by tools/settlement_decisions.py.\nLR_FRA_settlement_category = {\n\ticon = generic_political_actions\n"
                "\tvisible = {\n\t\ttag = FRA\n\t}\n}\n")
    return "\n".join(lines) + "\n", category, loc
