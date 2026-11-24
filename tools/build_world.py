"""Generate the 1936 world from the tables below: python tools/build_world.py

Writes the startup scripted effect, country names, the mod descriptors, and copies of the
vanilla state files whose owner changed, so the country selection map already shows this world.
"""
import json
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
MOD = PROJECT / "mod"
VANILLA = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV")
GAME_MOD_FOLDER = Path.home() / "Documents" / "Paradox Interactive" / "Hearts of Iron IV" / "mod"

# New owner -> vanilla state ids it receives. Unlisted states keep their vanilla owner.
TRANSFERS = {
    # Prussian partition of Poland and Memel stay with the North German Confederation.
    # French central Africa and Indochina went to Prussia after the Great War.
    # Germany keeps its old Pacific colonies: no Japanese mandate in this world.
    # The victor also keeps every colony it had in 1914: German New Guinea, the Bismarck Archipelago, Samoa and
    # Nauru, Tsingtao, Togo, Kamerun, German East Africa (with Ruanda-Urundi) and South-West Africa.
    "GER": [633, 646, 647, 684, 979, 737, 726, 725, 743,
            777, 546, 768, 769, 541, 893, 894, 895,  # all of South-West Africa, not just Windhoek
            85, 86, 762, 807, 188,
            539, 660, 772, 773,
            286, 670, 671, 741, 1017, 1066, 1067, 1068, 1069, 728],
    "BAY": [50, 52, 53, 54, 978],
    # Austria: Hungary, Bohemia, Galicia, Transylvania, Croatia, Bosnia, Lombardy, Veneto.
    "AUS": [43, 154, 155, 973, 974,
            9, 69, 70, 71, 72, 73, 74, 75, 664, 972,
            88, 89, 91,
            76, 80, 82, 83, 84,
            45, 102, 103, 104, 109, 764, 804, 853,
            39, 850, 159, 160, 736, 852, 163],
    # Italy stays divided; the ITA tag is the Kingdom of Sardinia (158, 114).
    # State 735 holds both Savoy and Nice. Toulon (851) stays French.
    "ITA": [735],
    # Abruzzo (157) joins the Papal lands so Lazio and Emilia-Romagna connect.
    "PAP": [2, 161, 157],
    "TOS": [162],
    "TTS": [117, 156, 849, 115],
    # Independent after Russia's defeat.
    "UKR": [137, 192, 193, 196, 197, 198, 199, 200, 201, 202, 203, 221, 225, 226, 227, 228, 259, 834,
            93, 78, 766],
    "BLR": [194, 204, 206, 207, 241, 94, 95, 96],
    "LIT": [784],
    "POL": [90, 98],
    "GEO": [231, 826],
    "ARM": [230],
    "AZR": [229],
    # Greater Bulgaria.
    "BUL": [106, 970, 731, 184, 77, 971, 803],
    # The Ottoman Empire keeps the Middle East and Libya. Saudi Arabia is fully independent.
    # With Britain on its side and the Arab revolt never raised, the Porte keeps the Hejaz, the Red Sea coast from
    # Tabuk to Mecca and Asir, as in Kaiserreich. Nejd stays with the Saudis and Yemen with its imam.
    "TUR": [183, 765, 1014, 554, 677, 680, 799, 553, 454, 455, 291, 675, 676, 1010, 1011, 656, 448, 449, 450, 451, 661, 662, 663, 273, 164,
            679, 855, 856],
    # France keeps West Africa as far as Chad, and took Liberia.
    "FRA": [298],
    # British spoils: French islands, Djibouti, Guiana, plus Italian east Africa and Haiti.
    "ENG": [543, 635, 641, 694, 706, 708, 713, 730, 1071, 310, 320,
            318,
            # Ireland never left.
            113, 134, 135],
    "CAN": [463],
    # New Spain keeps the viceroyalty's northern provinces: no war ever took Texas, New Mexico and Alta California.
    "MEX": [375, 376, 377, 378, 379, 380],
    # Spain keeps what the Spanish-American War took in our history: Puerto Rico and Guam (the Philippines stay a
    # Spanish colony, see SUBJECTS).
    "SPR": [686, 638],
    # No American planters, no 1893 coup: the Kingdom of Hawaii still stands, with Midway and Wake, under Edo's
    # protection (see SUBJECTS).
    "HAW": [629, 631, 632],
    # Spanish America follows the colonial map: viceroyalties are kingdoms, captaincies duchies.
    # New Granada: Colombia, Ecuador, Panama and the canal zone.
    "COL": [305, 490, 649, 304, 685],
    # Rio de la Plata: Argentina, Uruguay, Paraguay, Bolivia.
    "ARG": [300, 945, 946, 301, 688, 302, 487],
    # Captaincy of Guatemala: all of Central America.
    "GUA": [314, 312, 317, 316],
    # Captaincy of Cuba, with Santo Domingo.
    "CUB": [319],
    # Qing China absorbs warlords, communists, Manchuria, Mongolia, Tibet and Taiwan.
    "CHI": [599, 594, 622, 1032, 1046,
            591, 592, 593, 1033,
            615, 621, 746,
            287, 617, 618, 619, 759, 760, 1042,
            283, 604, 616, 753, 754, 755, 756, 1040, 1044, 1045,
            325, 747,
            328, 610, 714, 715, 716, 717, 761,
            611, 612, 1043,
            330, 817, 818, 819, 820, 329,
            322, 601, 757, 758,
            524, 609, 745,
            # Vanilla state files hand these to warlords in a dated 1936.1.1 block,
            # after the plain owner line, so they must be taken back explicitly.
            608, 614, 1039, 605, 751, 752, 1037, 1041, 597, 1038, 744,
            434],
    "ETH": [908, 550, 559, 268, 269, 844],  # the whole Horn of Africa: Afar, Eritrea, the Somalilands, Jubaland
    # Korea was never annexed, and Sakhalin stayed Russian.
    "KOR": [525, 527, 1028, 1029, 1030, 1031],
    "SOV": [537],
}
# The pieces split_states.py cuts from these states go with them; then the pieces with an owner of their own in 1936
# (Abruzzo to Naples, the duchies of Parma and Modena, the Greek salient to Bulgaria) move to that owner.
import split_states as _split  # noqa: E402
TRANSFERS = {tag: _split.expand(states) for tag, states in TRANSFERS.items()}
for _state, _tag in _split.owner_overrides().items():
    for _states in TRANSFERS.values():
        if _state in _states:
            _states.remove(_state)
    TRANSFERS.setdefault(_tag, []).append(_state)

# Countries that get cores on the states they are handed (land that was always theirs in this world).
CORE_ON_TRANSFER = {"MEX"}

# Owned by one country, held by another from the start (Kaiserreich style): state -> controller.
OCCUPIED = {}  # none: the Kuomintang rises on 1936.10.10 and takes Guangzhou then (docs/WORLD.md)

# (overlord, autonomy level, subjects)
SUBJECTS = [
    ("ENG", "autonomy_dominion", ["USA"]),
    ("SPR", "autonomy_dominion", ["MEX", "COL", "PRU", "ARG", "GUA", "CHL", "VEN", "CUB"]),
    ("SPR", "autonomy_colony", ["PHI"]),
    ("POR", "autonomy_dominion", ["BRA"]),
    # The Great War's winners keep the lands they cut from Russia on a leash.
    ("GER", "autonomy_puppet", ["POL", "LIT", "LAT", "EST"]),
    ("AUS", "autonomy_puppet", ["UKR", "BLR"]),
    # Hawaii turned to Edo for protection once no American fleet stood between it and the British.
    ("JAP", "autonomy_puppet", ["HAW"]),
]

# Iberian vassals: (overlord, name, adjective).
# Vanilla names subjects with extra keys, so those are overridden too.
IBERIAN_VASSALS = {
    "MEX": ("SPR", "누에바 에스파냐 왕국", "누에바 에스파냐"),
    "COL": ("SPR", "누에바 그라나다 왕국", "누에바 그라나다"),
    "PRU": ("SPR", "페루 왕국", "페루"),
    "ARG": ("SPR", "리오데라플라타 왕국", "리오데라플라타"),
    "GUA": ("SPR", "과테말라 공국", "과테말라"),
    "CHL": ("SPR", "칠레 공국", "칠레"),
    "VEN": ("SPR", "베네수엘라 공국", "베네수엘라"),
    "CUB": ("SPR", "쿠바 공국", "쿠바"),
    "BRA": ("POR", "브라질 부왕령", "브라질"),
}

# Tag -> (name, adjective). FRA, USA and SOV are named by hand in lr_replace_l_korean.yml.
NAMES = {
    "GER": ("북독일 연방", "북독일"),
    "BAY": ("남독일 연방", "남독일"),
    "AUS": ("오스트리아 제국", "오스트리아"),
    "ITA": ("사르데냐 왕국", "사르데냐"),
    "PAP": ("교황령", "교황령"),
    "TOS": ("토스카나 대공국", "토스카나"),
    "TTS": ("양시칠리아 왕국", "양시칠리아"),
    "POL": ("폴란드 공국", "폴란드"),
    "UKR": ("우크라이나 왕국", "우크라이나"),
    "BLR": ("벨라루스 대공국", "벨라루스"),
    "GEO": ("조지아 왕국", "조지아"),
    "ARM": ("아르메니아 왕국", "아르메니아"),
    "AZR": ("아제르바이잔 칸국", "아제르바이잔"),
    "EST": ("에스토니아 공국", "에스토니아"),
    "LAT": ("라트비아 공국", "라트비아"),
    "LIT": ("리투아니아 대공국", "리투아니아"),
    "FIN": ("핀란드 왕국", "핀란드"),
    "TUR": ("오스만 제국", "오스만"),
    "BUL": ("대불가리아 왕국", "불가리아"),
    "YUG": ("세르비아 왕국", "세르비아"),
    "SPR": ("스페인 왕국", "스페인"),
    "CHI": ("청나라", "청"),
    "JAP": ("에도 막부", "일본"),
    "KOR": ("조선", "조선"),
    "HAW": ("하와이 왕국", "하와이"),
    "RHI": ("라인 연방", "라인"),
}

# Stay republics: Britain and the Netherlands (with subjects), and the Russian Republic.
GENERATED_NOTE = "# Generated by tools/build_world.py. Edit the tables there, not this file.\n"


def vanilla_states():
    owners = {}
    for path in (VANILLA / "history" / "states").glob("*.txt"):
        text = re.sub(r"#.*", "", path.read_text(encoding="utf-8-sig", errors="ignore"))
        state = re.search(r"\bid\s*=\s*(\d+)", text)
        owner = re.search(r"\bowner\s*=\s*(\w+)", text)
        if state and owner:
            tag = owner.group(1)
            dated = re.search(r"\b1936\.1\.1\s*=\s*\{", text)
            if dated:
                moved = re.search(r"transfer_state_to\s*=\s*(\w+)", text[dated.end():dated.end() + 600])
                if moved:
                    tag = moved.group(1)
            owners[int(state.group(1))] = tag
    return owners


def lift_demilitarized_zones():
    """Vanilla's demilitarized zones come from the Allies' victory in our Great War: the Rhineland, the Straits,
    Danzig, Samoa. In this world Germany and the Porte won it, so none of them exist in 1936. (Algeria's zone is made
    during the game by its revolt.)"""
    folder = MOD / "history" / "states"
    for path in (VANILLA / "history" / "states").glob("*.txt"):
        if "set_demilitarized_zone = yes" not in path.read_text(encoding="utf-8-sig", errors="ignore"):
            continue
        target = folder / path.name
        text = (target if target.exists() else path).read_text(encoding="utf-8-sig", errors="ignore")
        text = re.sub(r"\n[ \t]*set_demilitarized_zone = yes[ \t]*", "", text)
        if not text.startswith(GENERATED_NOTE):
            text = GENERATED_NOTE + text
        target.write_bytes(text.encode("utf-8"))


def vanilla_capital(tag):
    for path in (VANILLA / "history" / "countries").glob(f"{tag} - *.txt"):
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        match = re.search(r"^capital\s*=\s*(\d+)", text, re.M)
        if match:
            return int(match.group(1))
    raise SystemExit(f"no vanilla capital for {tag}")


def fix_history_capital(tag, state):
    """The history file's capital line runs before the start effect: point it at a state the country holds, or the
    game logs that the capital is not theirs."""
    # build_diplomacy.py rewrites many histories from vanilla later: it reads this table and fixes them again.
    table = PROJECT / "tools" / "capital_fixes.json"
    fixes = json.loads(table.read_text(encoding="utf-8")) if table.exists() else {}
    fixes[tag] = state
    table.write_text(json.dumps(fixes, indent=0, sort_keys=True), encoding="utf-8")
    for path in (MOD / "history" / "countries").glob(f"{tag} - *.txt"):
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        fixed = re.sub(r"^capital\s*=\s*\d+[^\n]*", f"capital = {state}", text, count=1, flags=re.M)
        if fixed != text:
            path.write_text(fixed, encoding="utf-8")


def build_effect():
    owners = vanilla_states()
    for _orig, _parts in _split.pieces().items():  # the pieces cut from vanilla states are states too
        for _new, _ in _parts:
            owners[_new] = owners.get(_orig)
    seen = {}
    for tag, states in TRANSFERS.items():
        for state in states:
            if state not in owners:
                raise SystemExit(f"unknown state {state} for {tag}")
            if state in seen:
                raise SystemExit(f"state {state} given to both {seen[state]} and {tag}")
            seen[state] = tag

    final = {state: seen.get(state, owner) for state, owner in owners.items()}
    # Owners are in the state histories (and kr_layout.py redraws them province by province at the end of the build):
    # moving states again at the start would undo that and leave states owned with no occupation data, which crashed
    # the game on its first day.
    lines = ["lr_setup_world = {"]
    lines.append("\t# Owned by one country, held by another")
    lines.extend(f"\t{state} = {{ set_state_controller_to = {holder} }}" for state, holder in OCCUPIED.items())
    lines.append("\t# Capitals of countries that lost or never held their vanilla capital")
    lines.append("\tTUR = { set_capital = { state = 797 } }  # Istanbul, not Ankara")
    # The victors keep their armies, and America its factories, so the world war France starts is no walkover
    # (tools/build_events.py defines the spirits).
    lines.append("\t# The great powers' standing armies")
    for tag in ("ENG", "GER", "AUS", "BAY"):
        lines.append(f"\t{tag} = {{ add_ideas = LR_great_power_army }}")
    lines.append("\tUSA = { add_ideas = LR_USA_arsenal }")
    for tag in sorted((set(TRANSFERS) | set(NAMES)) - {"JAP", "TUR", "RHI", "KMT", "PRM", "MDN", "JBS"}):  # the duchies set their capital in their own history
        held = sorted(state for state, owner in final.items() if owner == tag)
        if not held:
            raise SystemExit(f"{tag} holds no states")
        if vanilla_capital(tag) not in held:
            preferred = {"ITA": 158, "BAY": 53, "YUG": 107}.get(tag, held[0])
            lines.append(f"\t{tag} = {{ set_capital = {{ state = {preferred} }} }}")
            fix_history_capital(tag, preferred)

    lines.append("\t# Subjects")
    for overlord, level, subjects in SUBJECTS:
        lines.append(f"\t{overlord} = {{")
        for subject in subjects:
            lines.extend([
                "\t\tset_autonomy = {",
                f"\t\t\ttarget = {subject}",
                f"\t\t\tautonomous_state = {level}",
                "\t\t}",
            ])
        lines.append("\t}")

    lines.extend([
        "\t# Absolute monarchy is the world norm",
        "\tevery_country = {",
        "\t\tlimit = {",
        "\t\t\tNOT = {",
        "\t\t\t\ttag = ENG",
        "\t\t\t\ttag = HOL",
        "\t\t\t\ttag = SOV",
        "\t\t\t\tis_subject_of = ENG",
        "\t\t\t\tis_subject_of = HOL",
        "\t\t\t}",
        "\t\t}",
        "\t\tset_politics = {",
        "\t\t\truling_party = neutrality",
        "\t\t\telections_allowed = no",
        "\t\t}",
        "\t\tset_popularities = {",
        "\t\t\tneutrality = 75",
        "\t\t\tfascism = 10",
        "\t\t\tdemocratic = 10",
        "\t\t\tcommunism = 5",
        "\t\t}",
        "\t}",
        "\t# Vanilla trees assume our history, so everyone but France uses the generic tree.",
        "\t# Australia keeps its own: a vanilla daily script edits its focuses by name.",
        "\t# British North America gets build_america.py's tree.",
        "\tevery_country = {",
        "\t\tlimit = {",
        "\t\t\tNOT = {",
        "\t\t\t\ttag = FRA",
        "\t\t\t\ttag = AST",
        "\t\t\t\ttag = USA",
        "\t\t\t}",
        "\t\t}",
        "\t\tload_focus_tree = {",
        "\t\t\ttree = generic_focus",
        "\t\t\tkeep_completed = no",
        "\t\t}",
        "\t}",
        "}",
    ])
    path = MOD / "common" / "scripted_effects" / "lr_world_effects.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    if "--no-world" in sys.argv:
        # Crash isolation: keep the mod loaded, skip every world change.
        lines = ["lr_setup_world = {", '\tlog = "LR: world setup disabled by --no-world"', "}"]
    path.write_text(GENERATED_NOTE + "\n".join(lines) + "\n", encoding="utf-8")
    return 0 if "--no-world" in sys.argv else len(seen)


def drop_dated_blocks(body):
    """Remove every dated block (1936.1.1 = { ... }) from a state history. This mod starts only in 1936, and
    vanilla hides DLC transfers to warlords and others in these blocks (KHM = { transfer_state = PREV })."""
    out, i = [], 0
    pattern = re.compile(r"\b\d{3,4}\.\d{1,2}\.\d{1,2}\s*=\s*\{")
    while True:
        found = pattern.search(body, i)
        if not found:
            out.append(body[i:])
            return "".join(out)
        out.append(body[i:found.start()])
        depth, j = 1, found.end()
        while depth and j < len(body):
            depth += {"{": 1, "}": -1}.get(body[j], 0)
            j += 1
        i = j


# Industry and people of this world, by country: (civilian, military, dockyards, manpower) multipliers on vanilla.
# Britain led the winners and rearmed for its empire; the Ottomans and the Habsburgs, victors too, modernised.
# British North America never won its independence and grew as a colony. Russia's republic never had Stalin's
# five-year plans: fewer arms works, more civilian industry, and the people the famines and purges never took.
# France lost, but under no treaty limits: its weak army is a matter of budgets and generals, not factories.
SCALE = {
    "ENG": (1.15, 1.5, 1.1, 1.0),
    "TUR": (1.4, 2.0, 1.5, 1.1),
    "AUS": (1.0, 1.15, 1.5, 1.0),
    "GER": (1.0, 1.2, 1.0, 1.0),
    "BAY": (1.4, 1.0, 1.0, 1.0),
    "USA": (0.6, 0.6, 0.7, 0.85),
    "SOV": (1.15, 0.5, 1.0, 1.1),
}
SLOTS = {"wasteland": 0, "enclave": 0, "tiny_island": 0, "small_island": 1, "pastoral": 1, "rural": 2, "town": 4,
         "large_town": 5, "city": 6, "large_city": 8, "metropolis": 10, "megalopolis": 12}


CARRY = {}  # (tag, building) -> fraction still owed after rounding


def scale_state(body, tag):
    """Multiply a state's factories and manpower by its owner's factors, within the state's building slots."""
    civ, mil, dock, people = SCALE[tag]
    category = re.search(r"state_category\s*=\s*(\w+)", body)
    slots = SLOTS.get(category.group(1), 12) if category else 12
    counts = {}
    for key in ("industrial_complex", "arms_factory", "dockyard"):
        found = re.search(rf"\b{key}\s*=\s*(\d+)", body)
        counts[key] = int(found.group(1)) if found else 0
    wanted = {}
    for key, factor in (("industrial_complex", civ), ("arms_factory", mil), ("dockyard", dock)):
        # Carry the fraction to the owner's next state, so a country's total follows its factor even when most of
        # its states hold one or two factories.
        exact = counts[key] * factor + CARRY.get((tag, key), 0.0)
        wanted[key] = max(0, int(exact + 0.5)) if counts[key] or exact >= 1 else 0
        CARRY[(tag, key)] = exact - wanted[key]
    need = sum(wanted.values())
    if category and need > slots:
        # A country that grew faster in this world has grown its towns too: raise the state's category as far as needed.
        ladder = sorted((v, k) for k, v in SLOTS.items() if v > 0)
        bigger = next((k for v, k in ladder if v >= need), "megalopolis")
        body = body.replace(category.group(0), f"state_category = {bigger}", 1)
        slots = SLOTS[bigger]
    room = max(slots, sum(counts.values()))  # never fewer slots than vanilla already fills
    for key in ("dockyard", "arms_factory", "industrial_complex"):  # trim growth that does not fit
        while sum(wanted.values()) > room and wanted[key] > counts[key]:
            wanted[key] -= 1
    for key, value in wanted.items():
        if value == counts[key]:
            continue
        if re.search(rf"\b{key}\s*=\s*\d+", body):
            body = re.sub(rf"\b{key}\s*=\s*\d+", f"{key} = {value}", body, count=1)
        elif value > 0:
            body = re.sub(r"(buildings\s*=\s*\{)", rf"\1\n\t\t\t{key} = {value}", body, count=1)
    body = re.sub(r"\bmanpower\s*=\s*(\d+)", lambda m: f"manpower = {round(int(m.group(1)) * people)}", body, count=1)
    return body



def build_state_history():
    """Copies of the vanilla state files whose owner changed, so the country selection map shows this world.

    Only the owner moves: every owner and controller line is dropped and the new owner is written at the
    top of the history block. Dated blocks stay, so later bookmarks would still be vanilla.
    The startup script still transfers the same states, which does nothing once they are already right.
    """
    owners = vanilla_states()
    final = dict(owners)
    TRANSFERRED = {s for states in TRANSFERS.values() for s in states}
    for tag, states in TRANSFERS.items():
        for state in states:
            final[state] = tag
    folder = MOD / "history" / "states"
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("*.txt"):
        head = old.read_text(encoding="utf-8-sig", errors="ignore")[:200]
        # Its own states, and kr_layout.py's from the last build (that step lays the states out again at the end).
        if GENERATED_NOTE.strip() in head or "Generated by tools/kr_layout.py" in head:
            old.unlink()
    written = 0
    for path in (VANILLA / "history" / "states").glob("*.txt"):
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        found = re.search(r"\bid\s*=\s*(\d+)", re.sub(r"#.*", "", text))
        if not found:
            continue
        state = int(found.group(1))
        if state not in final or (final[state] == owners.get(state) and state not in TRANSFERRED and state not in OCCUPIED
                                  and final[state] not in SCALE):
            continue
        lines = [line for line in text.split("\n") if not re.match(r"\s*(owner|controller|transfer_state_to)\s*=\s*\w+\s*(#.*)?$", line)]
        body = drop_dated_blocks("\n".join(lines))
        if final[state] in SCALE:
            body = scale_state(body, final[state])
        opened = re.search(r"history\s*=\s*\{", body)
        if not opened:
            raise SystemExit(f"state {state}: no history block")
        holder = f"\n\t\tcontroller = {OCCUPIED[state]}" if state in OCCUPIED else ""
        if final[state] in CORE_ON_TRANSFER and state in TRANSFERRED and f"add_core_of = {final[state]}" not in body:
            holder += f"\n\t\tadd_core_of = {final[state]}"
        body = body[:opened.end()] + f"\n\t\towner = {final[state]}{holder}" + body[opened.end():]
        # Some vanilla files carry a byte-order mark the reader keeps; one stray mark breaks the whole state.
        body = body.replace("﻿", "")
        # Vanilla state files have no byte-order mark, and the game rejects one at the start of a state file.
        (folder / path.name).write_bytes((GENERATED_NOTE + body).encode("utf-8"))
        written += 1
    return written


def vanilla_subject_keys():
    """Vanilla keys like POL_GER_autonomy_puppet, grouped by the subject tag."""
    found = {}
    for path in (VANILLA / "localisation" / "korean").rglob("*.yml"):
        for key in re.findall(r"^ *([A-Z]{3})_([A-Z]{3})_([a-z_]*autonomy[a-z_]*|[a-z_]*subject[a-z_]*)(?::\d*)? ", path.read_text(encoding="utf-8-sig", errors="ignore"), re.M):
            found.setdefault(key[0], set()).add("_".join(key))
    return {tag: sorted(keys) for tag, keys in found.items()}


VANILLA_SUBJECT_KEYS = vanilla_subject_keys()


def build_names():
    lines = ["l_korean:"]
    entries = {tag: (None, *names) for tag, names in NAMES.items()}
    entries.update(IBERIAN_VASSALS)
    for tag, (overlord, name, adjective) in entries.items():
        suffixes = ["", "_DEF"] + [f"_{i}{d}" for i in ("neutrality", "fascism", "democratic", "communism") for d in ("", "_DEF")]
        lines.extend(f' {tag}_{i}_ADJ:0 "{adjective}"' for i in ("neutrality", "fascism", "democratic", "communism"))
        if overlord:
            suffixes += [f"_{overlord}_neutrality_subject", f"_{overlord}_neutrality_subject_DEF",
                         "_autonomy_dominion", "_autonomy_dominion_DEF",
                         "_subject", "_subject_DEF"]
            lines.append(f' {tag}_{overlord}_neutrality_subject_ADJ:0 "{adjective}"')
        for suffix in suffixes:
            lines.append(f' {tag}{suffix}:0 "{name}"')
        lines.append(f' {tag}_ADJ:0 "{adjective}"')
        for key in VANILLA_SUBJECT_KEYS.get(tag, ()):
            lines.append(f' {key}:0 "{adjective if key.endswith("_ADJ") else name}"')
    path = MOD / "localisation" / "korean" / "replace" / "lr_countries_l_korean.yml"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def build_descriptors():
    """Never add replace_path for common/national_focus: removing vanilla trees crashes on day one."""
    for name in ("generic.txt", "australia_taog.txt"):
        (MOD / "common" / "national_focus" / name).unlink(missing_ok=True)
    base = (
        'version="0.2.0"\n'
        'tags={\n\t"Alternative History"\n}\n'
        'name="The Belated Revolution"\n'
        'picture="thumbnail.png"\n'
        'supported_version="1.19.*"\n'
    )
    # The Steam Workshop needs a thumbnail under 1 MB next to the descriptor.
    from PIL import Image
    logo = Image.open(PROJECT / "docs" / "art" / "logo.png").convert("RGB")
    logo.thumbnail((512, 512))
    canvas = Image.new("RGB", (512, 512), (20, 20, 30))
    canvas.paste(logo, ((512 - logo.width) // 2, (512 - logo.height) // 2))
    canvas.save(MOD / "thumbnail.png", optimize=True)

    def keep(path, key):
        """The launcher writes the Workshop id (and an absolute path) into the descriptors: keep them."""
        found = re.search(rf'^{key}="[^"]*"', path.read_text(encoding="utf-8", errors="ignore"), re.M) if path.exists() else None
        return found.group(0) + "\n" if found else ""

    game_mod = GAME_MOD_FOLDER / "belated_revolution.mod"
    remote = keep(MOD / "descriptor.mod", "remote_file_id") or keep(game_mod, "remote_file_id")
    path = keep(game_mod, "path") or 'path="mod/belated_revolution"\n'
    (MOD / "descriptor.mod").write_text(base + remote, encoding="utf-8")
    game_mod.write_text(base + path + remote, encoding="utf-8")


def drop_layout_copies():
    """kr_layout.py's translated copies of vanilla histories, from the last build: the build starts from vanilla."""
    for sub in ("countries", "units"):
        for path in (MOD / "history" / sub).glob("*.txt"):
            if "Generated by tools/kr_layout.py" in path.read_text(encoding="utf-8-sig", errors="ignore")[:200]:
                path.unlink()


if __name__ == "__main__":
    drop_layout_copies()
    count = build_effect()
    histories = build_state_history()
    import split_states  # Europe's states cut along Kaiserreich's borders (tools/state_splits.json)
    pieces = split_states.apply(MOD, VANILLA, GENERATED_NOTE)
    lift_demilitarized_zones()
    build_names()
    build_descriptors()
    print(f"OK: {histories} state history files rewritten for the selection map, {pieces} new states cut from them")
    print(f"OK: {count} states transferred, {len(NAMES)} countries named")
