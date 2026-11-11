"""Red Napoleon: the third road at Napoleon's fork, beside the crown and the presidency.

In 1793 a young artillery captain wrote a Jacobin pamphlet, Le Souper de Beaucaire. In this world the man
born late remembers it: before the crown he turns to the left, and becomes the people's consul of a red France
that carries its revolution across Europe with a red Grande Armée.

new_routes.py calls define(), arrange(), weave_routes() and spirits() from its own hooks and merges the tables.
"""
from france_story import chapter

P = "\\n\\n"
Q = '\\"'


def say(line):
    return f"{Q}{line}{Q}"


RED, RED_ROUTE, FORK = "LR_RED_", "LR_route_red", "LR_NAP_red"
FRIEND = "{tag} = {{ add_opinion_modifier = {{ target = ROOT modifier = medium_increase }} }}"


def popularity(tag, ideology, value):
    return f"{tag} = {{\n\tadd_popularity = {{\n\t\tideology = {ideology}\n\t\tpopularity = {value}\n\t}}\n}}"


IDEAS = [
    ("LR_idea_red_maximum", "곡물 최고 가격령", "1793년처럼 빵값의 상한을 정하고 숨긴 곡물을 징발합니다.", "generic_central_management", {"stability_factor": 0.05, "consumer_goods_factor": -0.03}),
    ("LR_idea_red_workshops", "국민 작업장", "실업자는 국가의 공장에서 일합니다. 그 공장은 대포를 만듭니다.", "generic_license_production", {"production_speed_buildings_factor": 0.05, "industrial_capacity_factory": 0.03}),
    ("LR_idea_red_levee", "국민 총동원령", "모든 프랑스인은 영구히 군대의 징발 대상이다. 1793년 8월 23일의 법령입니다.", "generic_war_preparation", {"conscription_factor": 0.08, "war_support_factor": 0.05}),
    ("LR_idea_red_commissars", "원수와 정치위원", "원수의 명령서에는 위원의 서명이 함께 들어갑니다.", "generic_communist_army", {"army_org_factor": 0.03, "army_morale_factor": 0.05}),
    ("LR_idea_red_sword", "세계 혁명의 칼", "대육군이 가는 곳마다 왕궁이 불타고 인민 공화국이 섭니다.", "generic_communist_army", {"army_attack_factor": 0.05, "political_power_gain": 0.05}),
    ("LR_idea_red_empire", "사회주의 대륙 체제", "혁명은 프랑스의 깃발 아래에서만 안전합니다.", "generic_central_management", {"stability_factor": 0.08, "industrial_capacity_factory": 0.03}),
]

REGIMES = {"red": ("붉은 통령정", {"war_support_factor": 0.1, "stability_factor": -0.03})}
RULER = ("인민의 통령 나폴레옹", "generic_communist_army", {"political_power_gain": 0.1, "war_support_factor": 0.1, "army_morale_factor": 0.05, "communism_drift": 0.02})


def define(g):
    focus, extras, CALM = g["focus"], g["extras"], g["CALM"]
    stab, war, pp, xp, civ, mil, pop, tech, goal = (g[n] for n in ("stab", "war", "pp", "xp", "civ", "mil", "pop", "tech", "goal"))
    g["IDEAS"].extend(IDEAS)
    idea = "add_ideas = {}".format
    # The fork itself belongs to Napoleon's trunk, like the coronation and the presidency.
    focus(FORK, "propaganda", 20, 4, "붉은 나폴레옹", "왕관 대신 붉은 깃발을 듭니다. 1922년의 자코뱅 포병 소위가 돌아옵니다.",
          "country_event = { id = lr_novel.1101 }", pre=["LR_NAP_before_the_crown"], route="LR_route_napoleon", me=["LR_NAP_coronation", "LR_NAP_guardian"])
    focus(RED + "tribune", "propaganda", 0, 0, "인민의 호민관", "통령의 견장 위에 붉은 리본이 달립니다.", stab(0.05), pop("communism", 0.15), pre=[FORK], route=RED_ROUTE, cost=5)
    extras(RED, RED_ROUTE, [
        # 내정
        ("maximum", "trade", 0, 0, "곡물 최고 가격령", "빵값의 상한을 정하고 숨긴 곡물을 징발합니다.", ["tribune"], [idea("LR_idea_red_maximum")]),
        ("workshops", "construct_civ_factory", 0, 0, "국민 작업장", "실업자는 국가의 공장에서 일합니다.", ["tribune"], [idea("LR_idea_red_workshops"), civ(2)]),
        ("arsenals", "construct_mil_factory", 0, 0, "인민 병기창", "슈나이더와 르노의 공장이 인민의 병기창이 됩니다.", ["workshops"], [mil(3)]),
        ("soldiers_land", "construct_civilian", 0, 0, "병사에게 땅을", "망명 귀족의 영지를 갈라 제대 군인에게 나눠 줍니다.", ["maximum"], [stab(0.03), "add_manpower = 20000"]),
        ("calendar_plan", "production", 0, 0, "혁명력 경제 계획", "포도의 달에 시작하는 첫 계획이 공장마다 걸립니다.", ["arsenals", "soldiers_land"], [mil(2), civ(1)]),
        # 정치
        ("beaucaire", "propaganda", 0, 0, "보케르의 저녁 식사", "1922년 젊은 포병 소위가 쓴 자코뱅 소책자를 다시 찍습니다.", ["tribune"], [pp(75), pop("communism", 0.05)]),
        ("committee", "political_pressure", 0, 0, "공안위원회 재건", "통령이 의장석에 앉는 공안위원회가 다시 열립니다.", ["beaucaire"], [pp(75)]),
        ("people_vote", "national_unity", 0, 0, "인민 투표", "인민의 통령에 찬성하느냐고 노동자 평의회마다 묻습니다.", ["beaucaire"], [stab(0.05)]),
        ("red_marshals", "military_sphere", 0, 0, "붉은 원수들", "견장에 붉은 별을 단 원수들이 임명됩니다.", ["committee", "people_vote"], [xp("army", 75)]),
        ("sword", "major_war", 0, 0, "세계 혁명의 칼", "대육군이 가는 곳마다 인민 공화국을 세웁니다.", ["red_marshals"], [idea("LR_idea_red_sword")]),
        ("continental_socialism", "national_unity", 0, 0, "사회주의 대륙 체제", "혁명은 프랑스의 깃발 아래에서만 안전합니다.", ["red_marshals"], [idea("LR_idea_red_empire")]),
        # 군사
        ("levee", "allies_build_infantry", 0, 0, "국민 총동원령", "1793년 8월 23일의 법령이 다시 낭독됩니다.", ["tribune"], [idea("LR_idea_red_levee"), "add_manpower = 50000"]),
        ("commissars", "army_doctrines", 0, 0, "원수와 정치위원", "원수의 명령서에 위원의 서명이 함께 들어갑니다.", ["levee"], [idea("LR_idea_red_commissars")]),
        ("red_grande_armee", "army_artillery", 0, 0, "붉은 대육군", "삼색기와 붉은 깃발을 함께 든 대육군이 출범합니다.", ["commissars"], [xp("army", 75), war(0.1)]),
        # 외교
        ("sister_communes", "alliance", 0, 0, "자매 코뮌", "국경 너머 혁명가들에게 파리의 형제가 되자고 편지를 씁니다.", ["tribune"], [pp(50)]),
        ("italian_legion", "propaganda", 0, 0, "이탈리아 군단", "1790년대 혁명 전쟁 때 이탈리아에 섰던 자매 공화국들의 이름으로 이탈리아 혁명가들을 모읍니다.", ["sister_communes"],
         [popularity("TTS", "communism", 0.1), popularity("PAP", "communism", 0.1), popularity("ITA", "communism", 0.1)]),
        ("polish_legion", "propaganda", 0, 0, "폴란드 군단", "돔브로프스키의 군단처럼 폴란드인 의용병을 모읍니다.", ["sister_communes"], [popularity("POL", "communism", 0.15), "add_manpower = 10000"]),
        ("revolution_hq", "major_alliance", 0, 0, "유럽 혁명 사령부", "튈르리 궁에 유럽 혁명의 참모본부가 문을 엽니다.", ["italian_legion", "polish_legion"], [pp(75), war(0.05)]),
        # 안정도
        ("suppress", "political_pressure", 0, 0, "인민 경찰", "푸셰의 밀정들이 이번에는 붉은 완장을 찹니다. 모든 지역 반발도 -15.", ["tribune"], ["lr_fra_op_reduce = yes"]),
        ("uproot", "special_forces", 0, 0, "반혁명 일소", "왕당파의 마지막 음모와 방데의 무기고를 같은 밤에 덮칩니다. 모든 지역 반발도 -30, 이후 반발이 자라지 않습니다.", ["suppress"], ["lr_fra_uproot = yes"]),
    ])
    for item in g["FOCUSES"]:
        if item["id"] == RED + "sword":
            item["me"] = [RED + "continental_socialism"]
        elif item["id"] == RED + "continental_socialism":
            item["me"] = [RED + "sword"]
        elif item["id"] == RED + "uproot":
            item["available"] = CALM
        elif item["id"] in ("LR_NAP_coronation", "LR_NAP_guardian"):
            item["me"] = list(item["me"]) + [FORK]
    focus(RED + "rhine", "major_war", 0, 0, "라인강의 붉은 깃발", "붉은 대육군이 라인강을 건넙니다.", goal("GER"), pre=[RED + "red_grande_armee"], route=RED_ROUTE)
    focus(RED + "danube", "major_war", 0, 0, "아우스터리츠의 해", "합스부르크의 왕관을 부수러 갑니다.", goal("AUS"), pre=[RED + "rhine"], route=RED_ROUTE)
    focus(RED + "channel", "major_war", 0, 0, "불로뉴의 붉은 진영", "귀족 의회의 섬으로 건너갑니다.", goal("ENG"), pre=[RED + "rhine"], route=RED_ROUTE)
    focus(RED + "russia", "major_war", 0, 0, "모스크바로", "혁명의 이름으로 겨울보다 먼저 갑니다.", goal("SOV"), pre=[RED + "channel"], route=RED_ROUTE)


def arrange(g):
    plan, require, BY_ID, FILTERS, add_effects = (g[n] for n in ("plan", "require", "BY_ID", "FILTERS", "add_effects"))
    plan(RED, "tribune", [
        ("내정", ["maximum", "workshops", "arsenals", "soldiers_land", "calendar_plan"]),
        ("정치", ["beaucaire", "committee", "people_vote", "red_marshals", ("sword", "continental_socialism")]),
        ("영토확장", ["levee", "commissars", "red_grande_armee", "rhine"]),
        ("외교", ["sister_communes", "italian_legion", "polish_legion", "revolution_hq"]),
        ("안정도", ["suppress", "uproot"]),
    ])
    for key in ("rhine", "danube", "channel", "russia"):
        BY_ID[RED + key]["filter"] = FILTERS["영토확장"]
    BY_ID[RED + "tribune"]["filter"] = FILTERS["정치"]
    BY_ID[FORK]["filter"] = FILTERS["정치"]
    import algeria
    require(RED + "rhine", "has_completed_focus = LR_FRA_revenge_army\n" + algeria.NOT_CAMPAIGNING)
    require(RED + "channel", "has_completed_focus = LR_FRA_fusiliers_marins")
    require(RED + "russia", "has_country_flag = LR_germany_defeated")
    add_effects(RED + "rhine", "29 = { set_demilitarized_zone = no }")


def weave_routes(g):
    weave = g["weave"]
    weave(RED, "tribune", "내정", [["maximum", "workshops"], ["soldiers_land<maximum", "arsenals<workshops"], ["calendar_plan<soldiers_land+arsenals"]])
    weave(RED, "tribune", "정치", [["beaucaire"], ["committee", "people_vote"], ["red_marshals<committee+people_vote"], [("sword", "continental_socialism")]])
    weave(RED, "tribune", "외교", [["sister_communes"], ["italian_legion", "polish_legion"], ["revolution_hq<italian_legion+polish_legion"]])


def spirits(g):
    spirit = g["spirit"]
    spirit(RED + "tribune", "인민의 호민관", "제1통령의 견장 위에 붉은 리본이 달렸습니다.", "generic_communist_army", {"stability_factor": 0.05, "communism_drift": 0.03})
    spirit(RED + "committee", "공안위원회", "통령이 의장석에 앉은 위원회가 프랑스를 다스립니다.", "generic_central_management", {"political_power_gain": 0.1})


STORY = [
    (FORK, RED, RED_ROUTE, 1600, [
        chapter("souper", "propaganda", "보케르의 저녁", "통령이 1922년에 쓴 소책자를 다시 찍게 합니다.", {"political_power_gain": 0.02},
                "보케르의 저녁 식사", P.join([
                    "튈르리 궁 서재. 통령이 누렇게 바랜 소책자 한 권을 비서에게 건넵니다. 1922년 여름, 아비뇽 포병 연대로 부임하던 스물한 살 소위가 보케르의 여관에서 상인들과 논쟁한 뒤 쓴 글입니다. 대전쟁에서 진 나라의 젊은 장교가 쓴, 혁명과 대포에 관한 글이었습니다. 제목은 보케르의 저녁 식사.",
                    say("나는 그때 공화국이 이길 거라고 썼네. 그리고 그 공화국을 지키는 건 결국 대포라고."),
                    "비서가 묻습니다. 몇 부를 찍을까요?"]), "generic_read_write", [
                    ("100만 부. 모든 병영과 공장에 한 권씩.", {"communism_drift": 0.03, "war_support_factor": 0.02}),
                    ("1,000부만. 원수들과 위원들이 읽으면 된다.", {"political_power_gain": 0.03, "flag": "LR_st_red_quiet"}),
                ]),
        chapter("red_epaulettes", "military_sphere", "붉은 견장", "알제부터 함께 온 원수들이 붉은 깃발 앞에서 머뭇거립니다.", {"army_org_factor": 0.02},
                "원수들의 저녁", P.join([
                    "알제부터 함께 싸운 장군 넷이 통령의 식탁에 앉았습니다. 그들은 나폴레옹을 따랐지, 붉은 깃발을 따른 적은 없습니다.",
                    "가장 나이 많은 장군이 포크를 내려놓습니다. " + say("각하, 저희가 왕을 쓰러뜨린 건 노동자 평의회에 경례하려고가 아니었습니다."),
                    "식탁에 침묵이 내려앉습니다. 통령은 포도주를 한 모금 마시고 장군들을 한 사람씩 바라봅니다."]), "military_planning", [
                    ("견장에 붉은 별을 달아 준다. 원수의 지휘봉도 함께.", {"army_morale_factor": 0.03, "political_power_gain": 0.02}),
                    ("늙은 장군을 해임한다. 대육군의 원수는 혁명이 정한다.", {"communism_drift": 0.03, "army_org_factor": -0.01}),
                ]),
        chapter("concordat_question", "improve_relations", "교회의 자리", "통령이 맺은 정교 협약을 혁명가들이 찢자고 합니다.", {"stability_factor": 0.02},
                "정교 협약의 운명", P.join([
                    "공안위원회 회의실. 위원 하나가 정교 협약 원본을 탁자에 내던집니다. 통령이 교황과 맺은 그 협약입니다.",
                    say("혁명 정부가 주교의 봉급을 대는 나라가 어디 있습니까?"),
                    "통령은 협약문을 집어 들고 천천히 접습니다. 그는 신을 믿지 않지만, 성당에 가는 농민들의 수는 압니다."]), "generic_parliament", [
                    ("협약은 지킨다. 농민의 성당을 빼앗으면 방데가 일어난다.", {"stability_factor": 0.04, "op": 1}),
                    ("협약을 파기하고 교회 재산을 국유화한다.", {"political_power_gain": 0.04, "industrial_capacity_factory": 0.02, "stability_factor": -0.02}),
                ]),
        chapter("robespierre_shadow", "intelligence_exchange", "로베스피에르의 그림자", "혁명가들이 통령을 의심하기 시작합니다. 카이사르인가, 로베스피에르인가.", {"war_support_factor": 0.02},
                "익명의 벽보", P.join([
                    "어느 아침, 생앙투안 거리의 벽마다 같은 벽보가 붙었습니다. 붉은 통령의 초상 아래 두 줄의 글이 적혀 있습니다. 브루투스는 어디 있는가. 테르미도르는 언제 오는가.",
                    "푸셰의 후계자인 경찰장관이 벽보를 붙인 사람들의 명단을 가져왔습니다. 절반은 오래된 코뮌 활동가들입니다.",
                    say("통령 각하, 이들을 어떻게 할까요?")]), "generic_riot", [
                    ("체포한다. 혁명에는 혁명의 적이 있다.", {"political_power_gain": 0.04, "stability_factor": 0.02, "communism_drift": -0.01}),
                    ("벽보를 그대로 둔다. 비판이 두려운 혁명은 혁명이 아니다.", {"stability_factor": -0.01, "communism_drift": 0.03}),
                ]),
        chapter("peoples_emperor", "national_unity", "인민의 황제?", "평의회 대표들이 통령에게 종신직을 바칩니다.", {"stability_factor": 0.03},
                "종신 통령", P.join([
                    "노동자 평의회 전국 대회. 대표들이 기립 박수 속에 결의문을 읽습니다. 인민의 통령 나폴레옹에게 종신의 권한을 바친다.",
                    "통령은 연단에 올라 한참을 말없이 서 있습니다. 왕관을 거절하고 붉은 깃발을 든 사람에게, 그들은 왕관과 다를 것 없는 것을 내밀고 있습니다.",
                    "앞줄의 늙은 코뮌 투사가 팔짱을 낀 채 그의 대답을 기다립니다."]), "france_parade", [
                    ("받아들인다. 혁명은 한 사람의 손에서만 지켜진다.", {"political_power_gain": 0.08, "war_support_factor": 0.04, "avoid": "LR_st_red_quiet"}),
                    ("거절한다. 내 임기는 혁명이 끝나는 날까지다.", {"stability_factor": 0.06, "communism_drift": 0.03}),
                    ("대답하지 않고 원수들을 부른다. 결정은 전장에서 한다.", {"army_morale_factor": 0.04, "war_support_factor": 0.05, "need": "LR_st_red_quiet"}),
                ]),
    ]),
]

BRANCH = [
    ("LR_RED_maximum", "generic_riot", "징발대", "징발대가 보스의 곡창 지대로 떠났습니다.", [
        ("시장 가격의 절반을 지불한다.", {"stability_factor": 0.02, "raw": ["add_political_power = -25"]}),
        ("영수증만 준다. 혁명이 빚을 갚을 것이다.", {"political_power_gain": 0.02, "raw": ["lr_fra_op_reduce = yes"], "stability_factor": -0.01}),
    ]),
    ("LR_RED_red_grande_armee", "soldiers_marching", "두 개의 깃발", "붉은 대육군의 연대마다 어느 깃발을 앞세울지 다툼이 났습니다.", [
        ("삼색기가 앞, 붉은 깃발이 뒤.", {"army_morale_factor": 0.03}),
        ("붉은 깃발 하나만.", {"communism_drift": 0.02, "war_support_factor": 0.02}),
    ]),
    ("LR_RED_sister_communes", "generic_read_write", "자매 코뮌의 편지", "국경 너머 혁명가들의 답장이 도착했습니다.", [
        ("돈과 소총을 보낸다.", {"raw": ["add_political_power = -25"], "war_support_factor": 0.02}),
        ("대육군이 갈 때까지 기다리라고 한다.", {"political_power_gain": 0.02}),
    ]),
]
BRANCH_TEXT = {
    "LR_RED_maximum": P.join([
        "징발대 서른 명이 보스의 곡창 지대로 떠났습니다. 1793년처럼, 붉은 완장을 찬 노동자들과 총을 든 병사들이 함께 갑니다. 파리의 빵값은 상한이 정해졌지만, 빵집 선반은 비어 갑니다.",
        "첫 마을에서 농민들이 곡물을 헛간 바닥에 숨겨 두었다는 보고가 들어옵니다.",
        say("돈을 줄까요, 영수증을 줄까요?")]),
    "LR_RED_red_grande_armee": P.join([
        "샹드마르스의 열병식 전날 밤. 근위 연대와 노동자 연대가 같은 막사에서 다투고 있습니다. 내일 어느 깃발을 앞세울 것인가.",
        "근위대 고참병은 아우스터리츠의 삼색기를, 벨빌의 선반공 출신 병사들은 코뮌의 붉은 깃발을 고집합니다.",
        "연대장이 통령의 결정을 청합니다."]),
    "LR_RED_sister_communes": P.join([
        "튈르리의 우편실에 국경 너머 혁명가들의 편지가 쌓였습니다. 밀라노의 학생, 바르샤바의 장교, 바르셀로나의 인쇄공. 모두 같은 것을 묻습니다. 언제 오느냐고.",
        "1796년, 혁명 프랑스의 군대는 이탈리아의 혁명가들에게 해방을 약속하고 알프스를 넘었습니다.",
        say("지금 돈을 보낼까요, 아니면 대육군이 갈 때까지 기다리라고 할까요?")]),
}

WAR_TEXTS = {
    "GER": {"red": P.join([
        "통령이 샹드마르스에 선 붉은 대육군 앞에서 말에 오릅니다. 삼색기와 붉은 깃발이 나란히 펄럭입니다.",
        say("병사들이여! 너희는 헐벗고 굶주렸다. 베를린의 궁전에는 너희 몫의 빵이 쌓여 있다. 가서 그것을 인민에게 돌려주어라!"),
        "알제리 원정 때 굶주린 병사들에게 했던 연설을 거의 그대로 고쳐 쓴 말입니다. 병사들의 함성이 샹드마르스를 덮습니다."])},
    "AUS": {"red": P.join([
        "통령이 지도 위 도나우강의 작은 마을을 짚습니다. 아우스터리츠.",
        say("이번에 우리가 무너뜨리는 것은 황제 하나가 아니다. 민족의 감옥 전체다."),
        "프라하와 부다페스트의 혁명가들에게 보내는 격문이 포탄과 함께 실립니다."])},
    "ENG": {"red": P.join([
        "불로뉴 해안에 붉은 대육군이 막사를 쳤습니다. 통령이 해협 너머 백악 절벽을 바라봅니다.",
        say("런던의 귀족들은 150년 동안 대륙의 왕들에게 돈을 댔다. 이제 그 은행을 닫으러 간다."),
        "선원 평의회와 해군 장교단이 처음으로 같은 출항 명령서에 서명합니다."])},
    "SOV": {"red": P.join([
        "통령이 러시아 지도를 펼칩니다. 측근 누구도 겨울 이야기를 꺼내지 않습니다.",
        say("케렌스키는 혁명을 반쯤 하다 말았다. 우리가 나머지 절반을 가져간다."),
        "대육군이 니에멘강을 건넙니다. 이번에는 겨울 군복이 먼저 실렸습니다."])},
}
FAMILY_CLOSE = {"red": "통령이 지휘봉을 들어 동쪽을 가리킵니다. 인민의 이름으로, 진군! 삼색기와 붉은 깃발이 함께 국경을 넘습니다."}

FOCUS_TEXT = {
    "LR_NAP_red": "1922년 여름, 스물한 살의 포병 소위는 자코뱅 소책자를 썼습니다. 대전쟁의 패배 속에서 그가 처음 꿈꾼 것은 왕관이 아니라 혁명이었습니다. 원로원이 왕관을 내미는 지금, 그는 그 소책자를 기억해 냅니다. 붉은 깃발과 대포를 함께 든 혁명입니다.",
    "LR_RED_tribune": "제1통령의 견장 위에 붉은 리본이 달립니다. 노동자 평의회가 통령을 인민의 호민관으로 추대합니다. 왕당파는 망명길에 오르고, 사회주의자들은 이 사람을 믿어도 되는지 아직 확신하지 못합니다.",
    "LR_RED_maximum": "1793년 국민공회는 빵값의 상한을 정하고 숨긴 곡물을 징발했습니다. 붉은 통령이 그 법령을 다시 꺼냅니다. 도시는 먹고, 농촌은 투덜댑니다.",
    "LR_RED_workshops": "1848년 실패한 국민 작업장을 이번에는 국가가 끝까지 책임집니다. 실업자는 국가의 공장에서 일하고, 그 공장들은 무엇보다 대포를 만듭니다.",
    "LR_RED_arsenals": "슈나이더와 르노와 오치키스의 공장이 인민의 병기창이 됩니다. 사주들은 망명했고, 공장장은 노동자 평의회와 포병 장교가 함께 맡습니다.",
    "LR_RED_soldiers_land": "망명한 귀족들의 영지를 갈라 제대 군인에게 나눠 줍니다. 로마의 장군들이 그랬듯, 병사들은 땅을 준 사람을 잊지 않습니다.",
    "LR_RED_calendar_plan": "포도의 달에 시작하는 첫 경제 계획이 공장마다 걸립니다. 혁명력과 5개년 계획이 한 장의 포스터에 같이 인쇄됩니다.",
    "LR_RED_beaucaire": "1922년, 아비뇽으로 가던 젊은 포병 소위가 보케르의 여관에서 상인들과 논쟁한 뒤 쓴 소책자, 보케르의 저녁 식사. 공화국은 이길 것이고, 그것을 지키는 것은 대포라는 내용입니다. 그 소책자를 다시 찍습니다.",
    "LR_RED_committee": "통령이 의장석에 앉는 공안위원회가 다시 열립니다. 로베스피에르의 위원회와 다른 점은 단 하나, 의장이 포병 장교라는 것입니다.",
    "LR_RED_people_vote": "인민의 통령에 찬성합니까? 투표는 투표소가 아니라 공장과 병영의 평의회에서 손을 들어 치러집니다.",
    "LR_RED_red_marshals": "견장에 붉은 별을 단 원수들이 임명됩니다. 알제부터 함께 온 장군들과 공장 평의회 출신의 젊은 지휘관들이 같은 지휘봉을 받습니다.",
    "LR_RED_sword": "대육군이 가는 곳마다 왕궁이 불타고 인민 공화국이 섭니다. 혁명은 수출되어야 살아남는다고 통령은 믿습니다.",
    "LR_RED_continental_socialism": "혁명은 프랑스의 깃발 아래에서만 안전합니다. 유럽의 인민 공화국들은 파리를 중심으로 하나의 대륙 체제에 묶입니다. 그 체제의 이름이 제국이 아니라는 것만 다릅니다.",
    "LR_RED_levee": "모든 프랑스인은 영구히 군대의 징발 대상이다. 1793년 8월 23일의 국민 총동원령이 다시 낭독됩니다. 젊은이는 싸우고, 기혼자는 무기를 만들고, 여자는 천막을 짓습니다.",
    "LR_RED_commissars": "원수의 명령서에는 정치위원의 서명이 함께 들어갑니다. 원수들은 불평하지만, 병사들은 위원이 자기들과 같은 솥의 수프를 먹는다는 것을 압니다.",
    "LR_RED_red_grande_armee": "삼색기와 붉은 깃발을 함께 든 대육군이 출범합니다. 근위대 고참병과 벨빌의 선반공이 같은 막사에서 잡니다.",
    "LR_RED_sister_communes": "국경 너머 혁명가들에게 편지를 씁니다. 파리의 형제가 되자고. 밀라노와 바르샤바와 바르셀로나에서 답장이 옵니다.",
    "LR_RED_italian_legion": "1790년대 혁명 전쟁 때 이탈리아에 섰던 자매 공화국들의 이름으로 이탈리아 혁명가들을 모읍니다. 나폴리와 로마와 토리노의 다락방에서 젊은이들이 짐을 쌉니다.",
    "LR_RED_polish_legion": "1797년 돔브로프스키가 이탈리아에서 폴란드 군단을 만들었을 때 부른 노래는 지금 폴란드의 국가가 되었습니다. 그 노래를 부르며 폴란드인 의용병이 파리로 옵니다.",
    "LR_RED_revolution_hq": "튈르리 궁의 한 층이 유럽 혁명 사령부가 됩니다. 지도 위에 꽂힌 붉은 핀은 대육군이 갈 곳이자, 인민 공화국이 설 곳입니다.",
    "LR_RED_suppress": "푸셰의 밀정들이 이번에는 붉은 완장을 찹니다. 왕당파 살롱과 망명자의 편지가 같은 서류철에 들어갑니다.",
    "LR_RED_uproot": "왕당파의 마지막 음모와 방데의 무기고를 같은 밤에 덮칩니다. 그날 이후 반혁명은 지도자를 잃습니다.",
    "LR_RED_rhine": "붉은 대육군이 라인강을 건넙니다. 베를린의 궁전에 쌓인 빵을 인민에게 돌려주러 간다고 통령은 연설했습니다.",
    "LR_RED_danube": "아우스터리츠. 이번에 무너뜨리는 것은 황제 하나가 아니라 민족의 감옥 전체입니다.",
    "LR_RED_channel": "불로뉴의 붉은 진영. 대륙의 왕들에게 150년 동안 돈을 댄 런던의 은행을 닫으러 갑니다.",
    "LR_RED_russia": "케렌스키는 혁명을 반쯤 하다 말았다고 통령은 말합니다. 대육군이 니에멘강을 건넙니다. 이번에는 겨울 군복이 먼저 실렸습니다.",
    "LR_RED_souper": "통령이 1922년에 쓴 소책자, 보케르의 저녁 식사를 다시 찍게 합니다.",
    "LR_RED_red_epaulettes": "알제부터 함께 온 원수들이 붉은 깃발 앞에서 머뭇거립니다.",
    "LR_RED_concordat_question": "통령이 교황과 맺은 정교 협약을 혁명가들이 찢자고 합니다.",
    "LR_RED_robespierre_shadow": "생앙투안 거리의 벽보가 묻습니다. 브루투스는 어디 있는가, 테르미도르는 언제 오는가.",
    "LR_RED_peoples_emperor": "노동자 평의회가 통령에게 종신의 권한을 바칩니다. 왕관을 거절한 사람에게 왕관과 다를 것 없는 것을 내밉니다.",
}

NOVEL = {
    "lr_france.52": {
        "pages": [
            P.join([
                "새벽 세 시, 튈르리 궁 서재.",
                "원로원 대표단이 돌아간 뒤에도 통령은 잠들지 못했습니다. 책상 위에는 두 개의 초안이 놓여 있습니다. 하나는 대관식 의전, 하나는 공화국 대통령 선서문입니다.",
                "그런데 그가 서랍에서 꺼낸 것은 세 번째 종이입니다. 누렇게 바랜 소책자. 1922년, 스물한 살 포병 소위가 쓴 자코뱅의 글입니다.",
            ]),
            P.join([
                "아침, 통령이 비서를 부릅니다. " + say("생앙투안 거리의 노동자 평의회 대표들을 불러 오게. 원로원 의원들은 기다리라고 하고."),
                "점심 무렵 튈르리 궁의 정원에 작업복 차림의 사내들이 모여듭니다. 경비병들은 어리둥절한 얼굴로 그들을 들여보냅니다.",
                "통령이 발코니에 나타납니다. 그는 군복 차림이고, 견장 위에 붉은 리본을 달았습니다.",
            ]),
            P.join([
                say("시민들이여. 원로원은 나에게 왕관을 권했고, 의회는 연미복을 권했다. 나는 둘 다 거절한다."),
                "정원이 술렁입니다. 통령이 소책자를 높이 들어 올립니다.",
                say("열네 해 전 나는 이렇게 썼다. 공화국은 이길 것이고, 그것을 지키는 것은 대포라고. 이제 그 대포를 인민에게 돌려주겠다!"),
            ]),
            P.join([
                "정원이 폭발하듯 함성을 지릅니다. 작업모가 하늘로 날아오르고, 누군가 라 마르세예즈를 시작했다가 인터내셔널로 바꿔 부릅니다.",
                "같은 시각, 뤽상부르 궁의 원로원 회의실. 대관식 의전을 준비하던 의원들이 창가에 몰려 튈르리 쪽의 함성을 듣습니다. 늙은 백작 하나가 의자에 주저앉습니다.",
                say("우리가 황제를 만들려 했는데, 그는 로베스피에르가 되려는군."),
                "그날 밤, 원로원 의원 열한 명이 스위스행 기차표를 샀습니다.",
            ]),
        ],
    },
}
NOVEL_BASE = {"lr_france.52": 1100}
FORK_EVENT = '''
# 52. Red Napoleon: before the crown, he turns to the left.
country_event = {
	id = lr_france.52
	title = lr_france.52.t
	desc = lr_france.52.d
	picture = GFX_report_event_generic_riot

	is_triggered_only = yes

	option = {
		name = lr_france.52.a
		custom_effect_tooltip = LR_tt_red
		set_country_flag = LR_route_red
		mark_focus_tree_layout_dirty = yes
		lr_fra_regime_red = yes
		lr_fra_ruler_red = yes
		set_politics = {
			ruling_party = communism
			elections_allowed = no
		}
		set_popularities = {
			communism = 55
			neutrality = 25
			democratic = 15
			fascism = 5
		}
		promote_character = {
			character = FRA_napoleon_bonaparte
			ideology = leninism
		}
		set_cosmetic_tag = LR_FRA_red
		news_event = { id = lr_gnews.20 days = 1 }
	}
}
'''
LOC = {
    "LR_tt_red": "§R붉은 나폴레옹 루트§! 진입: 황제와 대통령의 길이 닫히고 인민의 통령 줄기가 열립니다.",
    "lr_france.52.t": "붉은 통령",
    "lr_france.52.d": "튈르리 궁 정원의 노동자들이 처음에는 침묵하고, 다음에는 웅성거리고, 마침내 환호합니다. 누군가 라 마르세예즈를 부르기 시작하고, 다른 누군가는 인터내셔널을 부릅니다. 두 노래가 한데 뒤섞입니다." + P
                      + "원로원 의원들은 창문 뒤에서 그 광경을 내려다봅니다. 그들이 바친 왕관은 아직 상자 안에 있습니다." + P
                      + "통령이 발코니에서 돌아서며 비서에게 짧게 말합니다. " + say("원수들을 부르게. 할 일이 많아."),
    "lr_france.52.a": "인민의 이름으로.",
}
NEWS = ("붉은 나폴레옹", "프랑스의 제1통령 나폴레옹 보나파르트가 원로원이 바친 왕관을 거절하고 노동자 평의회의 손을 잡았습니다. 튈르리 궁에는 삼색기와 붉은 깃발이 나란히 걸렸고, 통령은 스스로를 인민의 통령이라 부릅니다.\\n\\n유럽의 왕실은 공포에 빠졌습니다. 혁명이 포병 장교를 얻었다는 것, 그것이 그들이 150년 동안 가장 두려워한 일이었습니다.", "대포를 든 혁명이다.")
