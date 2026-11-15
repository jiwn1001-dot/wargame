"""Country leader traits for France's route leaders: python tools/leader_traits.py

Each route's ruler gets a trait of his own, the way vanilla gives Hitler "Führer". A character with several leader
roles (Napoleon as president, emperor and red consul) gets one trait per ideology. The Girondin, Feuillant and
Commune governments get leaders of their own here, promoted by the events that form those governments.

Run it after tools/build_portraits.py (which rewrites portraits in the same character file) and before
tools/build_diplomacy.py, which recruits the characters listed in RECRUIT there.
"""
import re

import build_world as world

MOD = world.MOD
CHARACTERS = MOD / "common" / "characters" / "lr_characters.txt"
EVENTS = MOD / "events" / "lr_france.txt"

# trait: (name, description in 합쇼체, modifiers)
TRAITS = {
    "LR_trait_lily_guardian": ("백합의 수호자",
        "루이 20세는 패전의 왕으로 기억될까 두려워합니다. 그래서 그는 무엇보다 왕좌가 흔들리지 않는 것을 보여 주려 합니다.",
        {"stability_factor": 0.10, "political_power_factor": 0.10}),
    "LR_trait_king_of_revenge": ("복수의 왕",
        "오를레앙 공은 1918년에 잘려 나간 지도를 들고 왕좌에 올랐습니다. 그를 따르는 군중은 복수를 원하고, 그는 그 열기를 식힐 생각이 없습니다.",
        {"war_support_factor": 0.15, "political_power_factor": 0.15, "army_attack_factor": 0.05, "stability_factor": -0.05}),
    "LR_trait_crown_refused": ("왕관을 거절한 자",
        "그는 대관식 날 제위를 거절하고 연미복을 입었습니다. 병사들은 그를 장군으로, 시민들은 그를 대통령으로 따릅니다.",
        {"stability_factor": 0.10, "political_power_factor": 0.15, "army_org_factor": 0.05}),
    "LR_trait_emperor": ("황제",
        "코르시카의 포병 대위가 프랑스인의 황제가 되었습니다. 그의 말은 곧 법이고, 그의 원수들은 그가 가리키는 곳으로 군대를 몰고 갑니다.",
        {"political_power_factor": 0.25, "army_attack_factor": 0.10, "war_support_factor": 0.10,
         "land_doctrine_cost_factor": -0.10, "weekly_casualties_war_support": 0.001}),
    "LR_trait_red_consul": ("붉은 통령",
        "그는 원로원이 권한 왕관도, 의회가 권한 연미복도 거절했습니다. 대신 대포를 인민에게 돌려주겠다고 했고, 인민은 그 대포를 따라 국경을 넘습니다.",
        {"political_power_factor": 0.15, "army_attack_factor": 0.05, "conscription_factor": 0.05, "communism_drift": 0.05}),
    "LR_trait_verdun_marshal": ("베르됭의 원수",
        "1916년 그는 무너지던 전선을 붙들었습니다. 여든의 원수는 지금도 화력이 죽이고 요새가 지킨다고 믿습니다.",
        {"army_defence_factor": 0.10, "stability_factor": 0.15, "political_power_factor": 0.10, "production_speed_bunker_factor": 0.20}),
    "LR_trait_mountain_tribune": ("산악파의 기수",
        "블룸은 국가가 시민을 돌봐야 한다고 믿습니다. 그 믿음 뒤에는 공안위원회가 있고, 위원회는 반대파의 이름을 매주 새로 적습니다.",
        {"political_power_factor": 0.10, "stability_factor": 0.05, "war_support_factor": 0.05}),
    "LR_trait_free_trader": ("자유 무역의 옹호자",
        "레노는 관세와 허가증을 걷어 내면 프랑스가 스스로 일어선다고 믿습니다. 보르도와 리옹의 상인들이 그의 가장 든든한 후원자입니다.",
        {"industrial_capacity_factory": 0.05, "production_factory_max_efficiency_factor": 0.05, "political_power_factor": 0.05}),
    "LR_trait_notable_of_1791": ("1791년의 명사",
        "플랑댕은 혁명과 반동 사이의 좁은 길을 고집합니다. 그는 아무도 완전히 만족시키지 못하지만, 아무도 그를 쓰러뜨리려 하지는 않습니다.",
        {"stability_factor": 0.15, "political_power_factor": 0.05}),
    "LR_trait_commune_secretary": ("코뮌의 서기장",
        "토레즈는 광부의 아들입니다. 그는 규율 없는 혁명은 석 달도 버티지 못한다고 믿고, 중앙위원회의 계획표를 손에서 놓지 않습니다.",
        {"political_power_factor": 0.15, "industrial_capacity_factory": 0.05, "stability_factor": -0.03}),
    "LR_trait_federation_speaker": ("자유 연합의 대변인",
        "베스나르는 명령하지 않습니다. 그는 총회의 결정을 전할 뿐입니다. 결정은 느리지만, 한번 정해지면 모두가 자기 일처럼 따릅니다.",
        {"stability_factor": 0.10, "political_power_factor": -0.10, "conscription_factor": 0.05}),
    "LR_trait_admiral_of_the_fleet": ("함대의 제독",
        "다를랑은 수병의 아들로 태어나 패전으로 흩어진 함대를 다시 세웠습니다. 그는 바다를 알고, 비시 장관들의 약점도 압니다.",
        {"political_power_factor": 0.10, "stability_factor": 0.05, "naval_doctrine_cost_factor": -0.10}),
    "LR_trait_marshals_pupil": ("원수의 제자",
        "드골은 젊은 시절 원수의 참모로 원수의 이름이 붙은 책을 썼습니다. 그러나 그는 요새가 아니라 전차를 믿습니다.",
        {"political_power_factor": 0.05, "war_support_factor": 0.05, "army_armor_attack_factor": 0.10, "land_doctrine_cost_factor": -0.10}),
    "LR_trait_continental_commander": ("대륙군 총사령관",
        "워싱턴은 영국군 장교로 대전쟁에 나갔다가 식민지인이라는 이유로 진급에서 밀려났습니다. 이제 그는 영국의 군대가 아니라 대륙의 군대를 이끕니다.",
        {"army_morale_factor": 0.10, "war_support_factor": 0.10, "political_power_factor": 0.10}),
}

# character: {leader ideology: trait}
ASSIGN = {
    "FRA_louis_xx": {"despotism": "LR_trait_lily_guardian"},
    "LR_FRA_orleans": {"fascism_ideology": "LR_trait_king_of_revenge"},
    "FRA_napoleon_bonaparte": {"conservatism": "LR_trait_crown_refused", "fascism_ideology": "LR_trait_emperor",
                               "leninism": "LR_trait_red_consul"},
    "LR_FRA_petain": {"despotism": "LR_trait_verdun_marshal"},
    "LR_FRA_darlan": {"despotism": "LR_trait_admiral_of_the_fleet"},
    "LR_FRA_degaulle": {"despotism": "LR_trait_marshals_pupil"},
    "LR_FRA_blum": {"socialism": "LR_trait_mountain_tribune"},
    "LR_FRA_reynaud": {"liberalism": "LR_trait_free_trader"},
    "LR_FRA_flandin": {"conservatism": "LR_trait_notable_of_1791"},
    "LR_FRA_thorez": {"marxism": "LR_trait_commune_secretary"},
    "LR_FRA_besnard": {"anarchist_communism": "LR_trait_federation_speaker"},
    "USA_george_washington": {"liberalism": "LR_trait_continental_commander"},
}

# New leaders: character, Korean name, portrait sprite, ideology.
NEW = [
    ("LR_FRA_reynaud", "폴 레노", "GFX_portrait_FRA_paul_reynaud", "liberalism"),
    ("LR_FRA_flandin", "피에르에티엔 플랑댕", "GFX_portrait_unknown", "conservatism"),
    ("LR_FRA_thorez", "모리스 토레즈", "GFX_portrait_fra_maurice_thorez", "marxism"),
    # Pétain's successors (tools/endings.py, the marshal's death after the État's ending)
    ("LR_FRA_darlan", "프랑수아 다를랑", "GFX_portrait_FRA_francois_darlan", "despotism"),
    ("LR_FRA_degaulle", "샤를 드골", "GFX_portrait_FRA_charles_de_gaulle", "despotism"),
]
# The event option that forms each new government: (event id, option name, character).
PROMOTE = [("lr_france.14", "lr_france.14.b", "LR_FRA_reynaud"),
           ("lr_france.14", "lr_france.14.c", "LR_FRA_flandin"),
           ("lr_france.50", "lr_france.50.a", "LR_FRA_thorez")]


def write_traits():
    out = ["# Generated by tools/leader_traits.py\nleader_traits = {\n"]
    for trait, (_, _, mods) in TRAITS.items():
        body = "".join(f"\t\t{k} = {v:g}\n" for k, v in mods.items())
        out.append(f"\t{trait} = {{\n\t\trandom = no\n{body}\t\tai_will_do = {{ factor = 1 }}\n\t}}\n")
    out.append("}\n")
    path = MOD / "common" / "country_leader" / "lr_traits.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(out), encoding="utf-8")
    loc = ["l_korean:"]
    for trait, (name, desc, _) in TRAITS.items():
        loc += [f' {trait}:0 "{name}"', f' {trait}_desc:0 "{desc}"']
    for character, name, _, _ in NEW:
        loc.append(f' {character}:0 "{name}"')
    (MOD / "localisation" / "korean" / "lr_traits_l_korean.yml").write_text("\n".join(loc) + "\n", encoding="utf-8-sig")


def patch_characters():
    raw = CHARACTERS.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf"), "character files must not start with a BOM"
    text = raw.decode("utf-8")
    for character, name, portrait, ideology in NEW:
        if f"\t{character}={{" in text:
            continue
        block = (f"\t{character}={{\n\t\tname={character}\n\t\tportraits={{\n\t\t\tcivilian={{\n\t\t\t\tlarge=\"{portrait}\"\n"
                 f"\t\t\t}}\n\t\t}}\n\t\tcountry_leader={{\n\t\t\tideology={ideology}\n\t\t\ttraits={{ }}\n"
                 f"\t\t\texpire=\"1965.1.1.1\"\n\t\t\tid=-1\n\t\t}}\n\t}}\n")
        end = text.rindex("}")
        text = text[:end] + block + text[end:]
    for character, roles in ASSIGN.items():
        # A character's block runs to the next character (or the file's closing brace).
        found = re.search(rf"\t{character}={{.*?(?=\n\t\w+={{|\n\}}\s*$)", text, re.S)
        assert found, f"character not found: {character}"
        block = found.group(0)

        def leader(match):
            role = match.group(0)
            ideology = re.search(r"ideology=(\w+)", role).group(1)
            trait = roles.get(ideology)
            return re.sub(r"traits=\{[^}]*\}", f"traits={{ {trait} }}", role, count=1) if trait else role

        new = re.sub(r"country_leader=\{.*?\n\t\t\}", leader, block, flags=re.S)
        assert new != block or all(t in block for t in roles.values()), f"no leader role matched: {character}"
        text = text.replace(block, new)
    CHARACTERS.write_bytes(text.encode("utf-8"))


def patch_events():
    raw = EVENTS.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8")
    for _, option, character in PROMOTE:
        found = re.search(rf"\t\tname = {re.escape(option)}(\r?\n)", text)
        assert found and len(re.findall(rf"name = {re.escape(option)}\s", text)) == 1, option
        eol = found.group(1)
        start = found.end()
        end = text.index(f"{eol}\t}}{eol}", start)
        if f"promote_character = {character}" not in text[start:end]:
            text = text[:start] + f"\t\tpromote_character = {character}{eol}" + text[start:]
    EVENTS.write_bytes(text.encode("utf-8"))


def main():
    write_traits()
    patch_characters()
    patch_events()
    print(f"OK: {len(TRAITS)} leader traits on {len(ASSIGN)} characters, {len(NEW)} new leaders")


if __name__ == "__main__":
    main()
