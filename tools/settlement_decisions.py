"""Territory decisions after the peace conference, as Kaiserreich's annexation decisions: one state at a time, on the
map. build_france.py writes the files.

Since 2026-11-25 only three settlements are decisions; puppets, hand-overs and revived countries are made at the
vanilla peace conference:
  LR_dec_settle_annex              - a French core on a state France claims (historical claims); map view, per state
  LR_dec_settle_left_bank          - every left-bank state France owns becomes a core at once
  LR_dec_settle_rhine_confederation - lr_found_rhine_confederation (build_systems.py) on the Rhine and south German land
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
    # Run on its own after a full build, the mod's states are kr_layout's output: read kr_layout's copy of its input.
    cached = Path(__file__).resolve().parent / "kr_layout_cache" / "input" / "states"
    if cached.exists() and all("Generated by tools/kr_layout.py" in p.read_text(encoding="utf-8-sig", errors="ignore")[:200]
                               for p in list((world.MOD / "history" / "states").glob("*.txt"))[:3]):
        files = {p.name: p for p in cached.glob("*.txt")}
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
           '영유권이 있는 주는 합병한다. 라인 연방을 세우거나 라인강 서안을 한꺼번에 합병할 수도 있다. 괴뢰국 수립과 할양은 평화 회의에서 정한다."']

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

    # Since 2026-11-25 only three kinds of land are settled by decision: the Rhine Confederation, the left bank of the
    # Rhine, and the land France has a core or a historical claim on (the annex decision above). Puppets, hand-overs and
    # revived countries are made at the vanilla peace conference instead.
    import build_systems
    import victory
    rhine = [x for x in build_systems.RHINE_STATES + build_systems.SOUTH_GERMANY if x not in victory.HANSE]
    held_rhine = "\n".join(f"{x} = {{ is_controlled_by = ROOT NOT = {{ is_core_of = ROOT }} }}" for x in rhine)
    lines.append(f"""\tLR_dec_settle_rhine_confederation = {{
\t\ticon = generic_form_nation
\t\tcost = 75
\t\tfire_only_once = yes
\t\tvisible = {{
\t\t\ttag = FRA
\t\t\tNOT = {{ RHI = {{ exists = yes }} }}
\t\t}}
\t\tavailable = {{
\t\t\tcustom_trigger_tooltip = {{
\t\t\t\ttooltip = LR_tt_settle_rhine_held
\t\t\t\tcount_triggers = {{
\t\t\t\t\tamount = 2
{tab(held_rhine, 5)}
\t\t\t\t}}
\t\t\t}}
\t\t}}
\t\tcomplete_effect = {{
\t\t\tlr_found_rhine_confederation = yes
\t\t}}
\t\tai_will_do = {{ factor = 5 }}
\t}}""")
    loc.extend([' LR_dec_settle_rhine_confederation:0 "라인 연방 형성"',
                ' LR_dec_settle_rhine_confederation_desc:0 "라인강 동쪽과 남독일에서 손에 넣은 땅의 군주들을 하나의 연방으로 묶어 프랑스의 보호 아래 둔다. 1806년의 라인 연방이 다시 선다."',
                ' LR_tt_settle_rhine_held:0 "라인강 동쪽이나 남독일의 주를 두 곳 이상 점령하고 있다"'])
    left = sorted(set(victory.LEFT_BANK))
    owned_left = "\n".join(f"{x} = {{ is_owned_by = ROOT NOT = {{ is_core_of = ROOT }} }}" for x in left)
    annex_left = "\n".join(f"if = {{\n\tlimit = {{ {x} = {{ is_owned_by = ROOT }} }}\n\t{x} = {{ add_core_of = ROOT }}\n}}" for x in left)
    lines.append(f"""\tLR_dec_settle_left_bank = {{
\t\ticon = generic_nationalism
\t\tcost = 100
\t\tfire_only_once = yes
\t\tvisible = {{ tag = FRA }}
\t\tavailable = {{
\t\t\tcustom_trigger_tooltip = {{
\t\t\t\ttooltip = LR_tt_settle_left_bank
\t\t\t\tOR = {{
{tab(owned_left, 5)}
\t\t\t\t}}
\t\t\t}}
\t\t}}
\t\tcomplete_effect = {{
{tab(annex_left, 3)}
\t\t\tadd_stability = 0.03
\t\t}}
\t\tai_will_do = {{ factor = 10 }}
\t}}""")
    loc.extend([' LR_dec_settle_left_bank:0 "라인강 서안 합병"',
                ' LR_dec_settle_left_bank_desc:0 "리슐리외 이래 프랑스의 장군들이 자연 국경이라 불러 온 라인강까지, 왼쪽 기슭의 땅을 모두 프랑스의 데파르트망으로 삼는다."',
                ' LR_tt_settle_left_bank:0 "라인강 서안에 프랑스의 핵심주가 아닌 프랑스 땅이 있다"'])
    lines.append("}")
    lines.extend(contested(tags_on, known, loc))
    category = ("# Generated by tools/settlement_decisions.py.\nLR_FRA_settlement_category = {\n\ticon = generic_political_actions\n"
                "\tvisible = {\n\t\ttag = FRA\n\t}\n}\n"
                "LR_contested_category = {\n\ticon = generic_political_actions\n\tpriority = 40\n}\n")
    return "\n".join(lines) + "\n", category, loc


def contested(tags_on, known, loc):
    """Any country, not only France (2026-11-25): a state it owns but has no core on, claimed by two or more other
    countries, can be handed to one of them by decision, on the map. One decision per claimant; the states and the
    rival claimants come from the 1936 state histories."""
    states_of = {}
    for state, (cores, claims) in tags_on.items():
        claimants = sorted(t for t in cores | claims if t in known)
        if len(claimants) < 2:
            continue
        for tag in claimants:
            states_of.setdefault(tag, set()).add(state)
    out = ["LR_contested_category = {"]
    for tag, states in sorted(states_of.items()):
        rivals = sorted({t for st in states for t in (tags_on[st][0] | tags_on[st][1]) if t in known})
        counted = "\n".join(f"AND = {{\n\t{r} = {{ exists = yes NOT = {{ tag = ROOT }} }}\n\tFROM = {{ OR = {{ is_core_of = {r} is_claimed_by = {r} }} }}\n}}"
                            for r in rivals)
        name = f"LR_dec_contested_{tag.lower()}"
        out.append(f"""\t{name} = {{
\t\ticon = generic_political_discourse
\t\tcost = 25
\t\tstate_target = yes
\t\ton_map_mode = map_only
\t\ttargets = {{ {' '.join(map(str, sorted(states)))} }}
\t\ttargets_dynamic = no
\t\ttarget_root_trigger = {{
\t\t\tNOT = {{ tag = {tag} }}
\t\t\t{tag} = {{ exists = yes }}
\t\t}}
\t\ttarget_trigger = {{
\t\t\tFROM = {{
\t\t\t\tis_owned_by = ROOT
\t\t\t\tNOT = {{ is_core_of = ROOT }}
\t\t\t\tOR = {{ is_core_of = {tag} is_claimed_by = {tag} }}
\t\t\t}}
\t\t\t{tag} = {{ NOT = {{ has_war_with = ROOT }} }}
\t\t\tcount_triggers = {{
\t\t\t\tamount = 2
{tab(counted, 4)}
\t\t\t}}
\t\t}}
\t\tcomplete_effect = {{
\t\t\t{tag} = {{ transfer_state = FROM }}
\t\t\t{tag} = {{ add_opinion_modifier = {{ target = ROOT modifier = medium_increase }} }}
\t\t}}
\t\tai_will_do = {{
\t\t\tfactor = 0
\t\t\tmodifier = {{
\t\t\t\tadd = 3
\t\t\t\tOR = {{
\t\t\t\t\t{tag} = {{ is_subject_of = ROOT }}
\t\t\t\t\t{tag} = {{ is_in_faction_with = ROOT }}
\t\t\t\t}}
\t\t\t}}
\t\t}}
\t}}""")
        loc.extend([f' {name}:0 "[{tag}.GetName]에 넘긴다"',
                    f' {name}_desc:0 "이 주에는 여러 나라가 핵심주나 영유권을 주장하고 있습니다. 그 가운데 [{tag}.GetName]에 이 주를 넘겨줍니다."'])
    out.append("}")
    loc.extend([' LR_contested_category:0 "분쟁 지역 처분"',
                ' LR_contested_category_desc:0 "우리 핵심주가 아닌 땅에 두 나라 이상이 연고를 주장하고 있다면 누구에게 넘길지 정할 수 있습니다. 지도에서 주를 고르면 넘겨받을 수 있는 나라가 나옵니다."'])
    return out
