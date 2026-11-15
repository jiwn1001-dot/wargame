"""What France keeps when it wins, the integration of conquered lands, and elections in the parliamentary republic.

Victory: every country that falls to France loses the European lands the winning kind of France claims,
then everything outside Europe that is not its own core; its overseas subjects become French dominions.
Whatever is left in Europe becomes a French puppet (the war-plan rules and settlements do that).

    parliamentary (democratic government): France of 1936
    socialist (communist government):      + Belgium and Luxembourg + the Jura
    nationalist or monarchist (otherwise):  + Sardinia (Piedmont, the island, Savoy) + the Rhine's left bank
    Napoleon's empire:                      + the Netherlands, Rome, Tuscany, Catalonia, Illyria, the Hanse coast, Valais

build_events.py writes the settlement effect, the integration and election events; build_france.py
adds the integration focuses; build_systems.py runs the election clock.
"""
P = "\\n\\n"
Q = '\\"'


def say(line):
    return f"{Q}{line}{Q}"


# European states. FRANCE_1936 is every European state vanilla France owned in 1936.
FRANCE_1936 = [1, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 735, 785, 806, 851]
BENELUX = [6, 8, 34, 977, 980]
JURA = [845]
SARDINIA = [158, 114, 735]
LEFT_BANK = [42, 51]
NETHERLANDS = [7, 35, 36]
ROME_TUSCANY = [2, 162]
CATALONIA = [165]
ILLYRIA = [853, 852, 103, 163]  # the Illyrian provinces: Ljubljana, Istria, Dalmatia, Zadar; not inland Croatia
HANSE = [56]  # Weser-Ems (Bremen, East Frisia); Holstein stays German
VALAIS = [836]
# Every list also takes the pieces split_states.py cut from its states (Nice and Haute-Savoie from Savoy, and so on).
from split_states import expand as _expand  # noqa: E402
FRANCE_1936, BENELUX, JURA, SARDINIA, LEFT_BANK, NETHERLANDS, ROME_TUSCANY, CATALONIA, ILLYRIA, HANSE, VALAIS = (
    _expand(x) for x in (FRANCE_1936, BENELUX, JURA, SARDINIA, LEFT_BANK, NETHERLANDS, ROME_TUSCANY, CATALONIA, ILLYRIA, HANSE, VALAIS))

SOCIALIST = FRANCE_1936 + BENELUX + JURA
MONARCHIST = SOCIALIST + SARDINIA + LEFT_BANK
NAPOLEON = MONARCHIST + NETHERLANDS + ROME_TUSCANY + CATALONIA + ILLYRIA + HANSE + VALAIS
# The Iberian Americas: when Spain or Portugal falls, or when they fall themselves, they go free, never to France.
IBERIAN_AMERICA = ["MEX", "COL", "PRU", "ARG", "GUA", "CHL", "VEN", "CUB", "BRA", "CNA"]
IBERIAN_CROWNS = ["SPR", "CRL", "ESR", "POR"]
# The British empire: when Britain falls its crown keeps these in Ottawa.
BRITISH = ["CAN", "AST", "NZL", "SAF", "USA", "RAJ", "MAL"]


def take(states):
    unique = sorted(set(states))
    return ("every_owned_state = {\n\tlimit = { OR = { " + " ".join(f"state = {s}" for s in unique) + " } }\n"
            "\tFRA = { transfer_state = PREV }\n}")


def indent(text, tabs=1):
    pad = "\t" * tabs
    return "\n".join(pad + line if line else line for line in text.split("\n"))


def settlement_effect():
    """Runs in the loser's scope at the moment it capitulates to France's side."""
    return "\n".join([
        "lr_fra_victory_settlement = {",
        '\tlog = "LR: French victory settlement for [ROOT.GetTag]"',
        "\t# The European lands this kind of France keeps.",
        "\tif = {\n\t\tlimit = { FRA = { OR = { has_country_flag = LR_route_empire has_country_flag = LR_route_red } } }\n" + indent(take(NAPOLEON), 2) + "\n\t}",
        "\telse_if = {\n\t\tlimit = { FRA = { has_government = democratic } }\n" + indent(take(FRANCE_1936), 2) + "\n\t}",
        "\telse_if = {\n\t\tlimit = { FRA = { has_government = communism } }\n" + indent(take(SOCIALIST), 2) + "\n\t}",
        "\telse = {\n" + indent(take(MONARCHIST), 2) + "\n\t}",
        "\t# Britain is the exception: its crown flees to Ottawa with the empire (lr_settle_britain).",
        "\tif = {\n\t\tlimit = { NOT = { tag = ENG } }",
        "\t# Outside Europe France annexes everything that is not the loser's own core.",
        "\tif = {\n\t\tlimit = { tag = GER }\n\t\tlr_german_exile = yes\n\t}",  # North Germany's colonies: a government in exile
        "\tevery_owned_state = {\n\t\tlimit = {\n\t\t\tNOT = { is_on_continent = europe }\n\t\t\tNOT = { is_core_of = ROOT }\n\t\t}\n\t\tFRA = { transfer_state = PREV }\n\t}",
        "\t# The loser's overseas subjects become French dominions; Spain's and Portugal's Americas go free instead.",
        "\tevery_country = {\n\t\tlimit = {\n\t\t\tis_subject_of = ROOT\n\t\t\tcapital_scope = { NOT = { is_on_continent = europe } }\n\t\t}\n"
        "\t\tROOT = { end_puppet = PREV }\n\t\tif = {\n\t\t\tlimit = { has_war_with = FRA }\n\t\t\tFRA = { white_peace = PREV }\n\t\t}\n"
        "\t\tif = {\n\t\t\tlimit = {\n\t\t\t\tNOT = {\n\t\t\t\t\tAND = {\n\t\t\t\t\t\tROOT = { OR = { " + " ".join(f"tag = {t}" for t in IBERIAN_CROWNS) + " } }\n"
        "\t\t\t\t\t\tcapital_scope = { OR = { is_on_continent = north_america is_on_continent = south_america } }\n\t\t\t\t\t}\n\t\t\t\t}\n\t\t\t}\n"
        "\t\t\tFRA = {\n\t\t\t\tset_autonomy = {\n\t\t\t\t\ttarget = PREV\n\t\t\t\t\tautonomous_state = autonomy_dominion\n\t\t\t\t}\n\t\t\t}\n\t\t}\n\t}",
        "\t}",
        "}",
        "",
        "# A country outside Europe that falls to France: the British empire and the Iberian Americas only make peace,",
        "# anything else is annexed.",
        "lr_fra_overseas_settlement = {",
        "\tif = {\n\t\tlimit = {\n\t\t\tOR = {\n\t\t\t\tis_subject_of = ENG\n\t\t\t\tis_subject_of = CAN\n"
        + "".join(f"\t\t\t\tis_subject_of = {t}\n" for t in IBERIAN_CROWNS)
        + "\t\t\t\t" + " ".join(f"tag = {t}" for t in BRITISH + IBERIAN_AMERICA) + "\n\t\t\t}\n\t\t}\n"
        "\t\tFRA = { white_peace = ROOT }\n\t}",
        "\telse = {\n\t\tFRA = { country_event = { id = lr_world.92 } }\n\t}",
        "}",
    ])


# ===== Integration: a shared branch of focuses, one event each, cores on the land =====
# key, focus name, short focus text, states, event title, event text, picture, two options (text, extra effects).
INTEGRATION = [
    ("netherlands", "네덜란드 통합", "1795년의 바타비아 공화국을 넘어, 네덜란드를 프랑스의 데파르트망으로 묶습니다.", NETHERLANDS, "자위더르해의 데파르트망", P.join([
        "암스테르담 왕궁 앞. 1795년 혁명 프랑스는 이곳에 바타비아 공화국을 세웠고, 2차 대불전쟁의 패배와 함께 잃었습니다. 이번에는 자매 공화국이 아니라 프랑스의 데파르트망입니다. 칙령이 낭독됩니다. 자위더르해 데파르트망, 스헬더 하구 데파르트망, 마스 하구 데파르트망.",
        "상인들은 말없이 듣습니다. 그들의 공화국은 왕들의 유럽에서 몇 안 되는 의회의 나라였습니다.",
        "새 도지사가 묻습니다. " + say("세관과 항구는 어떻게 할까요? 이 사람들은 장사로 먹고삽니다.")]), "generic_sign_treaty1", [
        ("항구는 열어 둔다. 상인이 웃어야 세금도 웃는다.", "add_political_power = 50"),
        ("대륙봉쇄를 이 항구에도 적용한다.", "add_war_support = 0.03\nadd_stability = -0.02"),
    ]),
    ("rhine", "라인강 서안의 데파르트망들", "몽토네르와 루르, 라인강 왼쪽 땅을 프랑스의 데파르트망으로 만듭니다.", LEFT_BANK, "라인강이 국경이다", P.join([
        "코블렌츠의 다리 위. 삼색기가 라인강 왼쪽 기슭의 모든 성당 종탑에 걸렸습니다. 1797년 혁명 프랑스가 처음 이 땅을 합병했을 때 세운 데파르트망의 이름들이 다시 쓰입니다. 몽토네르, 루르, 자르, 라인모젤.",
        "리슐리외 이래 프랑스의 장군들은 라인강을 자연 국경이라 불러 왔습니다. 강 건너편 오른쪽 기슭에서는 라인 연방의 깃발이 이쪽을 바라봅니다.",
        "독일어를 쓰는 시장들이 새 도지사 앞에 줄을 섭니다."]), "france_parade", [
        ("나폴레옹 법전을 그대로 시행한다. 법 앞에서는 모두 같다.", "add_stability = 0.02"),
        ("요새부터 쌓는다. 강은 국경이다.", "army_experience = 25"),
    ]),
    ("savoy", "사부아와 피에몬테", "알프스 양쪽과 사르데냐섬을 프랑스로 묶습니다.", SARDINIA, "몽스니 고개의 양쪽", P.join([
        "토리노 왕궁. 사르데냐 왕가의 문장이 내려지고 그 자리에 삼색기가 걸립니다. 1790년대 혁명가들이 지도 위에 그려 두기만 했던 데파르트망의 이름, 포와 세지아와 마렝고가 처음으로 관보에 실립니다.",
        "알프스 너머 사부아와 니스는 백사십 년 만에 다시 프랑스 땅이 되었습니다. 그러나 토리노의 귀족들은 프랑스어를 할 줄 알면서도 이탈리아어로만 대답합니다.",
        "새 총독이 묻습니다. 사르데냐 왕가의 근위대를 어떻게 할까요?"]), "generic_sign_treaty1", [
        ("프랑스군에 편입한다. 산악전을 아는 병사들이다.", "add_manpower = 15000"),
        ("해산하고 귀족들에게 연금을 준다.", "add_stability = 0.03\nadd_political_power = -25"),
    ]),
    ("alps", "쥐라와 발레", "제네바 호숫가와 심플롱 고개를 프랑스의 데파르트망으로 만듭니다.", JURA + VALAIS, "레만과 심플롱", P.join([
        "제네바 호숫가. 칼뱅의 도시가 다시 레만 데파르트망의 청사가 됩니다. 발레의 산골 마을에는 심플롱 데파르트망이라는 새 이름이 붙습니다. 황제의 공병대가 이 고개에 이탈리아로 가는 길을 닦기 시작합니다.",
        "스위스의 남은 칸톤들은 괴뢰 연방이 되었지만, 쥐라와 발레는 이제 프랑스입니다.",
        "제네바의 은행가들이 새 도지사를 찾아왔습니다. 그들의 금고는 누구의 것이 됩니까?"]), "generic_read_write", [
        ("금고는 손대지 않는다. 은행가는 친구로 두는 편이 낫다.", "add_political_power = 50"),
        ("심플롱 고개에 군용 도로를 다시 닦는다.", "army_experience = 25"),
    ]),
    ("italy", "로마와 토스카나", "티베르 데파르트망과 아르노 데파르트망. 영원의 도시가 프랑스 제국의 두 번째 도시가 됩니다.", ROME_TUSCANY, "제국의 두 번째 도시", P.join([
        "로마 캄피돌리오 언덕. 1798년 혁명 프랑스는 이곳에 로마 공화국을 세웠고, 이듬해 2차 대불전쟁 속에 잃었습니다. 이번 칙령은 로마를 프랑스의 두 번째 도시라 부릅니다. 피렌체에는 아르노 데파르트망의 깃발이 걸립니다.",
        "바티칸의 창문들은 굳게 닫혀 있습니다. 교황은 1798년처럼 파문 칙서를 쓸지, 침묵할지 고민하고 있습니다.",
        say("폐하, 교황을 어떻게 하시겠습니까?")]), "france_parade", [
        ("교황을 바티칸에 남겨 둔다. 순교자를 만들 필요는 없다.", "add_stability = 0.03"),
        ("교황청을 파리로 옮긴다. 제국의 교회는 제국의 수도에 있어야 한다.", "add_political_power = 75\nadd_stability = -0.03"),
    ]),
    ("catalonia", "카탈루냐 합병", "카탈루냐를 스페인에서 떼어 내 프랑스의 네 데파르트망으로 나눕니다.", CATALONIA, "몬세라트와 테르", P.join([
        "바르셀로나 람블라스 거리. 1794년 피레네 전쟁 때 혁명군은 피게레스까지 들어왔다가 물러났습니다. 이번에는 물러나지 않습니다. 카탈루냐가 몬세라트, 테르, 세그레, 에브르 하구의 네 데파르트망으로 나뉘어 관보에 실립니다.",
        "카탈루냐 사람들은 마드리드도 파리도 좋아하지 않습니다. 그러나 적어도 파리는 카탈루냐어 신문을 금지하지는 않겠다고 약속했습니다.",
        "새 도지사가 묻습니다. 그 약속을 지킬까요?"]), "generic_read_write", [
        ("카탈루냐어를 허락한다. 마드리드보다는 나은 주인이 되자.", "add_stability = 0.03"),
        ("프랑스어만 쓴다. 데파르트망은 데파르트망일 뿐이다.", "add_political_power = 50\nadd_stability = -0.02"),
    ]),
    ("illyria", "일리리아 속주", "아드리아해 동쪽 기슭을 프랑스의 일리리아 속주로 묶습니다.", ILLYRIA, "류블랴나의 총독", P.join([
        "류블랴나 성 아래 광장. 합스부르크의 아드리아해 해안이 프랑스의 일리리아 속주로 태어납니다. 고대 로마의 속주 이름을 딴 주입니다. 원수 하나가 첫 총독으로 부임합니다.",
        "슬로베니아 사람들은 빈의 독일어 관리들보다 파리의 관리들이 자기 말을 더 존중해 주기를 기대합니다. 달마티아의 선원들은 아드리아해가 프랑스의 바다가 되는 것을 지켜봅니다.",
        "총독이 첫 칙령의 내용을 고릅니다."]), "generic_sign_treaty1", [
        ("슬로베니아어 학교를 다시 연다.", "add_stability = 0.03"),
        ("트리에스테와 자다르를 군항으로 만든다.", "navy_experience = 25"),
    ]),
    ("hanse", "한자 도시들", "베저 하구와 브레멘을 프랑스의 데파르트망으로 만듭니다.", HANSE, "베저 하구 데파르트망", P.join([
        "브레멘 시청. 황제는 영국 상품의 밀수를 막으려고 북해 해안을 통째로 합병합니다. 베저 하구 데파르트망과 엠스 상류 데파르트망이라는 새 이름이 붙습니다.",
        "한자 동맹의 상인들은 700년 동안 왕도 황제도 모시지 않았습니다. 그들은 대륙봉쇄가 이 항구까지 온다는 소문에 장부를 덮습니다.",
        "새 도지사가 묻습니다. 브레멘의 항구를 어떻게 할까요?"]), "generic_read_write", [
        ("항구는 열어 둔다. 상인들이 프랑스를 위해 돈을 벌게 하라.", "add_political_power = 50"),
        ("밀수꾼을 잡고 영국 배를 막는다.", "add_war_support = 0.03\nnavy_experience = 15"),
    ]),
]
FOCUS_TEXT = {
    "LR_FRA_conquest_office": "정복은 칼로 하지만 통치는 펜으로 합니다. 내무부에 정복지 총독부가 생기고, 새로 얻은 땅마다 도지사와 법전과 세관을 보냅니다. 1790년대 혁명가들이 그랬듯, 프랑스는 땅을 얻으면 그 땅을 데파르트망으로 나눕니다.",
    "LR_FRA_integrate_netherlands": "1795년 혁명 프랑스는 네덜란드에 바타비아 공화국을 세웠고, 2차 대불전쟁의 패배와 함께 잃었습니다. 이번에는 자매 공화국이 아니라 프랑스의 데파르트망으로 묶습니다.",
    "LR_FRA_integrate_rhine": "리슐리외 이래 프랑스의 장군들은 라인강을 자연 국경이라 불렀습니다. 1797년 혁명 프랑스는 그 말을 사실로 만들었습니다. 라인강 왼쪽 기슭의 땅을 다시 프랑스의 데파르트망으로 묶습니다.",
    "LR_FRA_integrate_savoy": "사부아와 니스, 그리고 알프스 너머 피에몬테와 사르데냐섬. 사르데냐 왕국의 땅을 프랑스의 데파르트망으로 묶습니다. 1790년대 혁명가들이 지도 위에 그려 두기만 했던 도들입니다.",
    "LR_FRA_integrate_alps": "제네바 호숫가의 레만 데파르트망, 심플롱 고개의 심플롱 데파르트망. 1798년 혁명 프랑스가 잠시 품었던 칼뱅의 도시가 다시 프랑스가 됩니다.",
    "LR_FRA_integrate_italy": "1798년 혁명 프랑스는 로마에 공화국을 세웠고 이듬해 잃었습니다. 이번에는 티베르 데파르트망과 아르노 데파르트망이 지도에 그려집니다.",
    "LR_FRA_integrate_catalonia": "1794년 피레네 전쟁 때 혁명군은 피게레스까지 들어왔다가 물러났습니다. 이번에는 카탈루냐가 프랑스의 네 데파르트망이 됩니다. 몬세라트, 테르, 세그레, 에브르 하구.",
    "LR_FRA_integrate_illyria": "합스부르크의 아드리아해 해안을 고대 로마의 속주 이름을 딴 일리리아 속주로 묶습니다.",
    "LR_FRA_integrate_hanse": "영국 상품의 밀수를 막으려고 북해 해안을 통째로 합병합니다. 브레멘과 동프리슬란트가 프랑스의 데파르트망이 됩니다.",
}


def integration_events():
    import integration_routes
    route_events, route_loc, _ = integration_routes.events_and_loc()
    events = ["# Generated by tools/build_events.py from tools/victory.py and tools/integration_routes.py.\nadd_namespace = lr_integration\nadd_namespace = lr_election\n", route_events]
    loc = list(route_loc)
    for number, (key, _, _, states, title, text, picture, options) in enumerate([], start=1):
        event = f"lr_integration.{number}"
        cores = ("every_owned_state = {\n\t\t\tlimit = { OR = { " + " ".join(f"state = {s}" for s in states) + " } }\n\t\t\tadd_core_of = ROOT\n\t\t}")
        blocks = []
        for letter, (label, extra) in zip("ab", options):
            body = "\n".join("\t\t" + line for line in extra.split("\n"))
            blocks.append(f"\toption = {{\n\t\tname = {event}.{letter}\n\t\t{cores}\n{body}\n\t}}")
            loc.append(f' {event}.{letter}:0 "{label}"')
        events.append(f"country_event = {{\n\tid = {event}\n\ttitle = {event}.t\n\tdesc = {event}.d\n\tpicture = GFX_report_event_{picture}\n\n"
                      f"\tis_triggered_only = yes\n\n" + "\n\n".join(blocks) + "\n}\n")
        loc += [f' {event}.t:0 "{title}"', f' {event}.d:0 "{text}"']
    events.append(ELECTION_EVENT)
    loc += ELECTION_LOC
    return "\n".join(events), loc


def integration_focuses(g):
    """Called from build_france.py: the conquest office and one focus per region, beside Algeria and Belgium."""
    focus, ROOT = g["focus"], g["ROOT"]
    focus("LR_FRA_conquest_office", "demand_territory", 0, 0, "정복지 총독부", "새로 얻은 땅마다 도지사와 법전을 보냅니다.", "add_political_power = 25", pre=[ROOT])
    for number, (key, name, desc, states, *_) in enumerate(INTEGRATION, start=1):
        owned = "any_owned_state = { OR = { " + " ".join(f"state = {s}" for s in states) + " } }"
        focus(f"LR_FRA_integrate_{key}", "demand_territory", 0, 0, name, desc, f"country_event = lr_integration.{number}", pre=["LR_FRA_conquest_office"], available=owned)


# ===== Elections in the parliamentary republic: every 24 months the Chamber changes =====
ELECTION_MONTHS = 24
SWING = "\t\tlr_fra_election_count = yes\n"  # build_campaign.py: region by region, after stability, war and chance.
APPLY = "\t\tadd_to_variable = {{ LR_seats = LR_election_swing }}\n\t\tadd_to_variable = {{ LR_seats = {extra} }}\n\t\tclamp_variable = {{ var = LR_seats min = 100 max = 560 }}\n\t\tlr_fra_sync_seats = yes\n"
ELECTION_EVENT = (
    "# Every 24 months the republic votes; the government's seats move with stability, war, discontent and the campaign.\n"
    "country_event = {\n\tid = lr_election.1\n\ttitle = lr_election.1.t\n\tdesc = lr_election.1.d\n\tpicture = GFX_report_event_election_vote\n\n"
    "\tis_triggered_only = yes\n\n\timmediate = {\n\t\thidden_effect = {\n" + "\n".join("\t" + line for line in SWING.rstrip("\n").split("\n")) + "\n\t\t}\n\t}\n\n"
    "\toption = {\n\t\tname = lr_election.1.a\n" + APPLY.format(extra=0) + "\t\tadd_stability = 0.02\n\t}\n\n"
    "\toption = {\n\t\tname = lr_election.1.b\n" + APPLY.format(extra=6) + "\t\tadd_war_support = 0.03\n\t}\n\n"
    "\toption = {\n\t\tname = lr_election.1.c\n" + APPLY.format(extra=12) + "\t\tadd_stability = -0.03\n\t}\n}\n"
)
ELECTION_LOC = [
    ' lr_election.1.t:0 "총선"',
    ' lr_election.1.d:0 "선거 운동 마지막 주. 파리의 벽마다 포스터가 세 겹으로 붙었습니다. 카페에서는 신문을 펼친 사람들이 목소리를 높이고, 시골 장터에서는 후보들이 수레 위에 올라가 연설합니다.'
    + P + '개표가 끝나 갑니다. 지역별 여당 득표: 파리 [?LR_vote_paris|0]% · 북부 [?LR_vote_nord|0]% · 방데 [?LR_vote_vendee|0]% · 남부 [?LR_vote_midi|0]% · 론 [?LR_vote_rhone|0]% · 로렌 [?LR_vote_lorraine|0]% · 북아프리카 [?LR_vote_africa|0]%. 여당 의석은 §Y[?LR_election_forecast|0]§!석, 지난 의회보다 §Y[?LR_election_swing|+0]§!석입니다. 선거 운동 본부가 공들인 지역이 결과를 갈랐습니다.'
    + P + '선거 운동의 마지막 메시지를 고릅니다."',
    ' lr_election.1.a:0 "지난 임기의 업적을 내세운다."',
    ' lr_election.1.b:0 "조국과 군대를 앞세운다. 의석 +6"',
    ' lr_election.1.c:0 "야당의 추문을 터뜨린다. 의석 +12, 안정도 -3%"',
]


# ===== Names of France's puppets, by the kind of France that made them =====
# Parliamentary France raises sister republics with classical names, as in the 1790s; socialist France people's
# republics; the anarchist federation free communes; kings, nationalists and the marshal keep the old crowns;
# Napoleon makes the satellite kingdoms and duchies of 1806-1812. Britain's crown sits in Ottawa, so the home
# islands are a republic whoever wins.
PUPPET_BASE = {
    "BEL": "벨기에", "LUX": "룩셈부르크", "HOL": "네덜란드", "SWI": "스위스", "BAY": "남독일", "SPR": "스페인", "CRL": "스페인", "ESR": "스페인",
    "POR": "포르투갈", "ITA": "피에몬테", "PAP": "로마", "TOS": "토스카나", "TTS": "나폴리", "DEN": "덴마크", "NOR": "노르웨이", "SWE": "스웨덴",
    "FIN": "핀란드", "ICE": "아이슬란드", "POL": "폴란드", "LIT": "리투아니아", "LAT": "라트비아", "EST": "에스토니아", "BLR": "벨라루스",
    "UKR": "우크라이나", "GEO": "조지아", "ARM": "아르메니아", "AZR": "아제르바이잔", "BUL": "불가리아", "YUG": "세르비아", "GRE": "그리스",
    "ROM": "루마니아", "ALB": "알바니아", "MNT": "몬테네그로", "MOL": "몰다비아", "TUR": "튀르크", "ENG": "브리튼", "AUS": "다뉴브",
}
# Sister republics: the names of 1795-1799, or the republics these nations proclaimed themselves after 1917.
PARL_NAMES = {
    "HOL": "바타비아 공화국", "SWI": "헬베티아 공화국", "POR": "루시타니아 공화국", "ITA": "수발피나 공화국", "PAP": "로마 공화국",
    "TTS": "파르테노페아 공화국", "GRE": "헬라스 공화국", "ENG": "브리타니아 공화국", "UKR": "우크라이나 인민 공화국",
    "BLR": "벨라루스 인민 공화국", "GEO": "조지아 민주 공화국", "AZR": "아제르바이잔 민주 공화국", "AUS": "다뉴브 연방 공화국",
}
SOC_NAMES = {"UKR": "우크라이나 노동자 공화국", "BLR": "벨라루스 노동자 공화국", "ENG": "브리튼 노동자 공화국"}
# Kings and the marshal keep the old crowns, except where the crown is gone.
AUTH_NAMES = {"ENG": "브리튼 공화국", "AUS": "오스트리아 대공국"}
# Napoleon's satellites.
EMP_NAMES = {"POL": "바르샤바 대공국", "TTS": "나폴리 왕국", "BAY": "바이에른 왕국", "SWI": "헬베티아 연방", "HOL": "홀란트 왕국",
             "TOS": "에트루리아 왕국", "SPR": "보나파르트 스페인 왕국", "CRL": "보나파르트 스페인 왕국", "ESR": "보나파르트 스페인 왕국",
             "ENG": "브리타니아 공화국", "AUS": "오스트리아 제국"}
FLAG_BASE = {"CRL": "SPR", "ESR": "SPR"}
CATEGORIES = [  # key, trigger on France, ideology set on the puppet (None keeps it), flag ideology.
    ("emp", "has_country_flag = LR_route_empire", None, "neutrality"),
    ("ana", "has_country_flag = LR_route_anarchist", "communism", "communism"),
    ("parl", "has_government = democratic", "democratic", "democratic"),
    ("soc", "has_government = communism", "communism", "communism"),
    ("auth", None, None, "neutrality"),
]


def puppet_name(tag, category):
    base = PUPPET_BASE[tag]
    if category == "parl":
        return PARL_NAMES.get(tag, f"{base} 공화국")
    if category == "soc":
        return SOC_NAMES.get(tag, f"{base} 인민 공화국")
    if category == "ana":
        return f"{base} 자유 코뮌"
    return (AUTH_NAMES if category == "auth" else EMP_NAMES).get(tag)


def flag_source(tag, ideology, vanilla_flags):
    base = FLAG_BASE.get(tag, tag)
    for name in (f"{base}_{ideology}", f"{base}_neutrality", f"{base}_democratic", f"{base}_communism", base):
        if (vanilla_flags / f"{name}.tga").exists():
            return name
    raise SystemExit(f"no flag for puppet {tag}")


def puppet_cosmetics(vanilla_flags):
    """Cosmetic tags for build_events.COSMETICS: key -> (name, adjective, flag source)."""
    found = {}
    for tag in PUPPET_BASE:
        for category, _, _, flag_ideology in CATEGORIES:
            name = puppet_name(tag, category)
            if name:
                found[f"LR_{tag}_pup_{category}"] = (name, PUPPET_BASE[tag], flag_source(tag, flag_ideology, vanilla_flags))
    return found


def naming_effect():
    """Runs in the puppet's scope right after France makes it a subject."""
    branches = []
    for number, (category, trigger, ideology, _) in enumerate(CATEGORIES):
        lines = []
        for tag in PUPPET_BASE:
            name = puppet_name(tag, category)
            politics = ideology or ("democratic" if tag == "ENG" and category in ("auth", "emp") else None)
            body = []
            if name:
                body.append(f"set_cosmetic_tag = LR_{tag}_pup_{category}")
            if politics:
                body.append(f"set_politics = {{\n\truling_party = {politics}\n\telections_allowed = {'yes' if politics == 'democratic' else 'no'}\n}}")
                body.append(f"set_popularities = {{\n\t{politics} = 70\n\tneutrality = {30 if politics != 'neutrality' else 70}\n}}" if politics != "neutrality" else "")
            if body:
                lines.append(f"if = {{\n\tlimit = {{ tag = {tag} }}\n" + indent("\n".join(b for b in body if b)) + "\n}")
        inner = indent("\n".join(lines))
        if trigger is None:
            branches.append("else = {\n" + inner + "\n}")
        else:
            branches.append(f"{'if' if number == 0 else 'else_if'} = {{\n\tlimit = {{ FRA = {{ {trigger} }} }}\n" + inner + "\n}")
    return "lr_fra_name_puppet = {\n" + indent("\n".join(branches)) + "\n}"


ELECTION_EVENT += '\n# Six months without a majority: the Chamber moves a vote of no confidence.\ncountry_event = {\n\tid = lr_election.2\n\ttitle = lr_election.2.t\n\tdesc = lr_election.2.d\n\tpicture = GFX_report_event_generic_parliament\n\n\tis_triggered_only = yes\n\n\toption = {\n\t\tname = lr_election.2.a\n\t\tai_chance = { factor = 40 }\n\t\tadd_political_power = -100\n\t\tadd_to_variable = { LR_seats = 45 }\n\t\tlr_fra_sync_seats = yes\n\t\tadd_stability = -0.03\n\t}\n\n\toption = {\n\t\tname = lr_election.2.b\n\t\tai_chance = { factor = 40 }\n\t\tset_variable = { LR_election_clock = 0 }\n\t\tcountry_event = { id = lr_election.1 days = 3 }\n\t}\n\n\toption = {\n\t\tname = lr_election.2.c\n\t\tai_chance = { factor = 20 }\n\t\tadd_stability = -0.1\n\t\tadd_war_support = -0.05\n\t\tadd_to_variable = { LR_seats = 20 }\n\t\tlr_fra_sync_seats = yes\n\t}\n}\n'
ELECTION_LOC += [' lr_election.2.t:0 "불신임안"', ' lr_election.2.d:0 "부르봉 궁 회의장. 야당 대표가 연단에 올라 불신임안을 읽어 내려갑니다. 내각이 과반을 잃은 지 여섯 달, 의원 117명이 서명했습니다.\\n\\n\\"이 내각은 프랑스를 다스리는 것이 아니라 버티고 있을 뿐입니다!\\"\\n\\n여당 원내대표가 총리에게 쪽지를 건넵니다. 연정을 꾸리려면 장관 자리 셋이 필요하고, 그게 싫다면 국민에게 직접 묻는 수밖에 없습니다."', ' lr_election.2.a:0 "연정을 꾸린다. 장관 자리 셋을 내준다. 의석 +45"', ' lr_election.2.b:0 "의회를 해산하고 조기 총선을 치른다."', ' lr_election.2.c:0 "표결을 버틴다. 정부는 물러나지 않는다."']
