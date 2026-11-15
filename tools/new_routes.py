"""Two routes added late: Pétain's French State and the anarchist Federation of Free Communes.

Pétain's route opens in any route when regional discontent breaks the threshold (see build_systems.py):
three regions at 80 or more, or three uprisings. The anarchist route is a branch of the socialist
victory: the commune congress chooses between the central committee and the free federation.

build_france.py calls define() once the other routes exist, arrange() after the last route plan,
and spirits() with the other rulers' spirits. The tables below feed the story, branch events,
war speeches, focus texts and the visual-novel scenes.
"""
from france_story import chapter
import algeria  # noqa: E402
import red_napoleon as red
import defeat
import integration_routes as integration
import alliances  # noqa: E402

P = "\\n\\n"
Q = '\\"'


def say(line):
    return f"{Q}{line}{Q}"


PET, PET_ROUTE = "LR_PET_", "LR_route_petain"
ANA, ANA_ROUTE = "LR_ANA_", "LR_route_anarchist"
ALL_ROUTES = ["LR_route_orleans", "LR_route_bourbon", "LR_route_communist", "LR_route_anarchist", "LR_route_jacobin",
              "LR_route_girondin", "LR_route_marais", "LR_route_napoleon", "LR_route_empire", "LR_route_guardian", "LR_route_petain"]
FRIEND = "{tag} = {{ add_opinion_modifier = {{ target = ROOT modifier = medium_increase }} }}"


def popularity(tag, ideology, value):
    return f"{tag} = {{\n\tadd_popularity = {{\n\t\tideology = {ideology}\n\t\tpopularity = {value}\n\t}}\n}}"


IDEAS = [
    ("LR_idea_pet_national_revolution", "국민 혁명", "자유, 평등, 박애 대신 노동, 가족, 조국을 내건 나라입니다.", "generic_central_management", {"stability_factor": 0.05, "political_power_gain": 0.05}),
    ("LR_idea_pet_labour_charter", "노동 헌장", "파업도 직장 폐쇄도 금지됩니다. 노동자와 사장이 같은 조합에 묶였습니다.", "generic_license_production", {"production_factory_max_efficiency_factor": 0.03, "stability_factor": 0.03}),
    ("LR_idea_pet_return_to_soil", "땅으로의 귀환", "흙은 거짓말을 하지 않는다고 원수는 말합니다.", "generic_agrarian_reform", {"stability_factor": 0.05, "consumer_goods_factor": -0.02}),
    ("LR_idea_pet_youth_camps", "청년 작업장", "스무 살 청년들이 여덟 달 동안 숲에서 도끼를 듭니다.", "generic_war_preparation", {"production_speed_buildings_factor": 0.05, "conscription_factor": 0.02}),
    ("LR_idea_pet_legion", "참전용사 군단", "대전쟁의 노병들이 원수의 눈과 귀가 됩니다.", "generic_reserve_divisions", {"war_support_factor": 0.05, "stability_factor": 0.03}),
    ("LR_idea_pet_verdun", "베르됭의 교리", "그들은 지나가지 못한다. 화력과 참호가 공세를 꺾습니다.", "generic_fortify_the_borders", {"army_defence_factor": 0.1}),
    ("LR_idea_ana_self_management", "노동자 자주 관리", "공장은 그곳에서 일하는 사람들의 것입니다.", "generic_local_self_management", {"production_factory_max_efficiency_factor": 0.05, "consumer_goods_factor": -0.02}),
    ("LR_idea_ana_collectives", "자유 집산", "원하는 코뮌은 땅과 쟁기를 함께 씁니다.", "generic_agrarian_reform", {"stability_factor": 0.05}),
    ("LR_idea_ana_rationalist_schools", "합리주의 학교", "신부도 국가도 없는 교실에서 아이들이 스스로 묻는 법을 배웁니다.", "generic_local_self_management", {"research_speed_factor": 0.05}),
    ("LR_idea_ana_columns", "민병대 종대", "계급장 없는 종대가 노래를 부르며 전선으로 갑니다.", "generic_communist_army", {"army_attack_factor": 0.05, "army_org_factor": -0.03, "conscription_factor": 0.05}),
    ("LR_idea_ana_mandates", "위임과 소환", "대표는 명령받은 대로만 말하고, 언제든 소환됩니다.", "generic_constitutional_guarantees", {"stability_factor": 0.05}),
    ("LR_idea_ana_platform", "강령파의 규율", "하나의 강령, 하나의 전술. 자유를 지키려면 조직이 필요합니다.", "generic_army_war_college", {"army_org_factor": 0.05, "political_power_gain": 0.05}),
    ("LR_idea_ana_synthesis", "종합파의 자유", "수단이 목적을 삼키지 않게 합니다. 모든 경향이 같은 회관을 씁니다.", "generic_local_self_management", {"stability_factor": 0.08, "political_power_gain": -0.05}),
]

REGIMES = {
    "petain": ("프랑스국", {"stability_factor": 0.05, "war_support_factor": -0.05}),
    "anarchist": ("자유 코뮌 연합", {"political_power_gain": -0.1, "stability_factor": 0.05}),
}


def define(g):
    focus, extras, ROOT, CALM = g["focus"], g["extras"], g["ROOT"], g["CALM"]
    stab, war, pp, xp, civ, mil, pop, tech, goal = (g[n] for n in ("stab", "war", "pp", "xp", "civ", "mil", "pop", "tech", "goal"))
    g["IDEAS"].extend(IDEAS)
    idea = "add_ideas = {}".format

    # ===== Pétain =====
    focus(PET + "marshal", "national_unity", 16, 1, "베르됭의 원수", "반발을 다스리지 못한 정부가 무너지고, 여든 살 원수가 전권을 쥡니다.", stab(0.1), pre=[ROOT], route=PET_ROUTE, cost=5)
    extras(PET, PET_ROUTE, [
        # 내정
        ("labour_charter", "production", 0, 0, "노동 헌장", "파업도 직장 폐쇄도 없는 나라. 노사가 한 조합에 묶입니다.", ["marshal"], [idea("LR_idea_pet_labour_charter")]),
        ("family_code", "propaganda", 0, 0, "가족법", "어머니의 날과 다자녀 수당. 원수는 가족이 나라의 세포라고 말합니다.", ["marshal"], [stab(0.03), "add_manpower = 10000"]),
        ("return_to_soil", "construct_civilian", 0, 0, "땅으로의 귀환", "도시의 실업자를 농촌으로 보냅니다.", ["labour_charter"], [idea("LR_idea_pet_return_to_soil")]),
        ("peasant_corporation", "trade", 0, 0, "농민 조합", "모든 농민이 하나의 조합에 들어갑니다.", ["return_to_soil"], [civ(2)]),
        ("youth_camps", "construct_infrastructure", 0, 0, "청년 작업장", "스무 살 청년들을 숲과 산으로 보냅니다.", ["family_code"], [idea("LR_idea_pet_youth_camps")]),
        ("secours_national", "improve_relations", 0, 0, "국민 구호", "원수의 이름으로 겨울 외투와 빵을 나눠 줍니다.", ["family_code"], [stab(0.03), "lr_fra_op_reduce = yes"]),
        ("school_cross", "scientific_exchange", 0, 0, "학교의 십자가", "교실에 다시 십자가가 걸리고 도덕 수업이 시작됩니다.", ["youth_camps"], [tech("LR_PET_school_cross", "electronics")]),
        # 정치
        ("national_revolution", "national_unity", 0, 0, "국민 혁명", "노동, 가족, 조국. 삼색기의 세 낱말이 바뀝니다.", ["marshal"], [idea("LR_idea_pet_national_revolution")]),
        ("constitutional_acts", "political_pressure", 0, 0, "헌법 법령 제1호", "원수가 국가원수의 칭호를 취하고, 의회는 무기한 휴회합니다.", ["national_revolution"], [pp(100)]),
        ("legion", "allies_build_infantry", 0, 0, "참전용사 군단", "베레모를 쓴 노병들이 마을마다 원수의 눈과 귀가 됩니다.", ["national_revolution"], [idea("LR_idea_pet_legion")]),
        ("national_council", "political_pressure", 0, 0, "국민 평의회", "선거 대신 원수가 지명한 명사들이 나라를 논합니다.", ["constitutional_acts"], [pp(50), stab(0.02)]),
        ("riom_trial", "forceful_treaty", 0, 0, "리옴 재판", "패배와 혼란의 책임을 옛 정부에게 묻습니다.", ["constitutional_acts"], [pp(75), war(0.03), stab(-0.02)]),
        ("heir_weygand", "army_doctrines", 0, 0, "베강을 후계자로", "원수 다음은 군대입니다.", ["national_council", "legion"], [xp("army", 75), war(0.05)]),
        ("heir_darlan", "navy_doctrines_tactics", 0, 0, "다를랑을 후계자로", "원수 다음은 함대와 그 제독입니다.", ["national_council", "legion"], [xp("navy", 75), pp(50)]),
        # 외교
        ("madrid_embassy", "improve_relations", 0, 0, "마드리드 대사관", "원수는 한때 마드리드 대사였습니다. 그 인연을 되살립니다.", ["marshal"], [FRIEND.format(tag="SPR"), pp(25)]),
        ("vatican", "improve_relations", 0, 0, "바티칸과의 화해", "교황청이 원수에게 축복을 보냅니다.", ["madrid_embassy"], [stab(0.03), FRIEND.format(tag="PAP")]),
        ("montoire", "dangerous_deal", 0, 0, "몽투아르의 악수", "승전국과 손을 잡습니다. 배상금은 줄고, 칼은 칼집에 들어갑니다.", ["vatican"],
         [pp(100), stab(0.05), war(-0.05), FRIEND.format(tag="GER"), FRIEND.format(tag="ENG")]),
        ("hidden_sword", "military_deal", 0, 0, "칼집 속의 칼", "악수하는 척하며 동원 명부를 다시 씁니다.", ["vatican"], [war(0.05), xp("army", 50)]),
        # 군사
        ("verdun_doctrine", "fortify_city", 0, 0, "베르됭의 교리", "그들은 지나가지 못한다. 화력과 요새로 버팁니다.", ["marshal"], [idea("LR_idea_pet_verdun")]),
        ("maginot", "fortify_city", 0, 0, "마지노선 완공", "멈춰 있던 요새 공사를 끝냅니다.", ["verdun_doctrine"], [xp("army", 50), stab(0.02)]),
        # 안정도
        ("suppress", "political_pressure", 0, 0, "헌병대 계엄", "반발이 큰 지역에 헌병대와 계엄을 보냅니다. 모든 지역 반발도 -15.", ["marshal"], ["lr_fra_op_reduce = yes"]),
        ("uproot", "special_forces", 0, 0, "반국가 세력 일소", "공산주의자와 왕당파 비밀 조직을 함께 쓸어냅니다. 모든 지역 반발도 -30, 이후 반발이 자라지 않습니다.", ["suppress"], ["lr_fra_uproot = yes"]),
    ])
    for key, me in (("montoire", "hidden_sword"), ("hidden_sword", "montoire"), ("heir_weygand", "heir_darlan"), ("heir_darlan", "heir_weygand")):
        for item in g["FOCUSES"]:
            if item["id"] == PET + key:
                item["me"] = [PET + me]
    for item in g["FOCUSES"]:
        if item["id"] == PET + "uproot":
            item["available"] = CALM
    focus(PET + "algeria", "occupy_start_war", 0, 0, "알제리 질서 회복", "원수의 이름으로 지중해 건너의 질서를 되찾습니다.", algeria.CAMPAIGN, pre=[PET + "maginot"], route=PET_ROUTE, available=algeria.OPEN)
    focus(PET + "rhine", "major_war", 0, 0, "베르됭에서 라인으로", "늙은 원수가 마지막 공세를 명령합니다.", goal("GER"), pre=[PET + "maginot"], route=PET_ROUTE)
    focus(PET + "danube", "major_war", 0, 0, "빈으로", "합스부르크를 무너뜨립니다.", goal("AUS"), pre=[PET + "rhine"], route=PET_ROUTE)
    focus(PET + "channel", "major_war", 0, 0, "해협 건너로", "영국을 무너뜨립니다.", goal("ENG"), pre=[PET + "rhine"], route=PET_ROUTE)
    focus(PET + "russia", "major_war", 0, 0, "동쪽의 적", "러시아 공화국과의 마지막 전쟁입니다.", goal("SOV"), pre=[PET + "channel"], route=PET_ROUTE)

    # ===== Anarchist federation =====
    focus(ANA + "federation", "propaganda", 16, 1, "자유 코뮌 연합", "위원회도 당도 없는 혁명이 시작됩니다.", stab(0.05), pop("communism", 0.1), pre=[ROOT], route=ANA_ROUTE, cost=5)
    extras(ANA, ANA_ROUTE, [
        # 내정
        ("syndicates_take", "construct_civ_factory", 0, 0, "공장은 조합의 것", "사장실을 비우고 노동자 총회가 공장을 맡습니다.", ["federation"], [idea("LR_idea_ana_self_management"), civ(2)]),
        ("free_communes", "propaganda", 0, 0, "자유 코뮌", "코뮌마다 스스로 다스리는 총회가 열립니다.", ["federation"], [stab(0.03), pop("communism", 0.05)]),
        ("collectives", "construct_civilian", 0, 0, "자유 집산", "원하는 코뮌은 땅과 쟁기를 함께 씁니다.", ["syndicates_take"], [idea("LR_idea_ana_collectives")]),
        ("abolish_money", "trade", 0, 0, "화폐 없는 코뮌", "몇몇 코뮌이 돈을 불태우고 배급표로 삽니다.", ["collectives"], [civ(1), mil(1), stab(-0.03)]),
        ("housing", "construct_civilian", 0, 0, "빈집 징발", "부자들이 떠난 빈 저택에 판자촌 가족이 들어갑니다.", ["free_communes"], [stab(0.04)]),
        ("rationalist_schools", "scientific_exchange", 0, 0, "합리주의 학교", "신부도 국가도 없는 교실을 엽니다.", ["housing"], [idea("LR_idea_ana_rationalist_schools")]),
        ("ateneos", "propaganda", 0, 0, "민중 회관", "도서관과 강연장과 극장을 겸한 회관이 동네마다 생깁니다.", ["rationalist_schools"], [pp(50), stab(0.02)]),
        # 정치
        ("proudhon", "political_pressure", 0, 0, "프루동의 연방주의", "아래에서 위로, 코뮌에서 연합으로 나라를 다시 묶습니다.", ["federation"], [pp(50)]),
        ("abolish_prefects", "forceful_treaty", 0, 0, "도지사 폐지", "파리가 보낸 도지사들을 집으로 돌려보냅니다.", ["proudhon"], [stab(0.03), "lr_fra_op_reduce = yes"]),
        ("mandates", "national_unity", 0, 0, "위임과 소환", "대표는 명령받은 대로만 말하고, 언제든 소환됩니다.", ["proudhon"], [idea("LR_idea_ana_mandates")]),
        ("congress", "propaganda", 0, 0, "코뮌 대회", "전국의 코뮌과 조합이 대표를 보냅니다.", ["abolish_prefects", "mandates"], [pp(75)]),
        ("platform", "army_doctrines", 0, 0, "강령파", "하나의 강령과 하나의 전술로 혁명을 지킵니다.", ["congress"], [idea("LR_idea_ana_platform")]),
        ("synthesis", "improve_relations", 0, 0, "종합파", "모든 경향이 같은 회관을 쓰는 자유로운 연합을 지킵니다.", ["congress"], [idea("LR_idea_ana_synthesis")]),
        # 군사
        ("columns", "allies_build_infantry", 0, 0, "민병대 종대", "계급장 없는 종대가 노래를 부르며 모입니다.", ["federation"], [idea("LR_idea_ana_columns"), "add_manpower = 30000"]),
        ("elected_officers", "army_doctrines", 0, 0, "장교 선출", "병사들이 손을 들어 대표를 뽑습니다.", ["columns"], [xp("army", 50)]),
        ("militarisation", "political_pressure", 0, 0, "민병대의 군대화", "규율 없는 종대로는 왕들의 군대를 이길 수 없다는 결론에 이릅니다.", ["elected_officers"], [xp("army", 50), war(0.05)]),
        # 외교
        ("cnt_brothers", "alliance", 0, 0, "바르셀로나의 형제들", "피레네 너머 조합원들에게 손을 내밉니다.", ["federation"], [popularity("SPR", "communism", 0.1), pp(25)]),
        ("carrara", "propaganda", 0, 0, "카라라의 채석공", "이탈리아 무정부주의의 요람에 전단과 돈을 보냅니다.", ["cnt_brothers"], [popularity("TOS", "communism", 0.1), popularity("ITA", "communism", 0.05)]),
        ("iwa", "major_alliance", 0, 0, "국제노동자협회", "베를린에서 잠든 조합들의 인터내셔널을 파리에서 다시 깨웁니다.", ["carrara"], [pp(75), war(0.03)]),
        ("free_territory", "propaganda", 0, 0, "자유 영토의 기억", "우크라이나 초원의 흑군을 기억하는 사람들에게 편지를 보냅니다.", ["iwa"], [popularity("UKR", "communism", 0.1)]),
        # 안정도
        ("suppress", "political_pressure", 0, 0, "자경 위원회", "코뮌 총회가 뽑은 자경단이 반혁명 조직을 감시합니다. 모든 지역 반발도 -15.", ["federation"], ["lr_fra_op_reduce = yes"]),
        ("uproot", "special_forces", 0, 0, "반혁명 무장 해제", "왕당파 장교와 지주의 무기고를 모두 비웁니다. 모든 지역 반발도 -30, 이후 반발이 자라지 않습니다.", ["suppress"], ["lr_fra_uproot = yes"]),
    ])
    for item in g["FOCUSES"]:
        if item["id"] == ANA + "platform":
            item["me"] = [ANA + "synthesis"]
        elif item["id"] == ANA + "synthesis":
            item["me"] = [ANA + "platform"]
        elif item["id"] == ANA + "uproot":
            item["available"] = CALM
    focus(ANA + "algerian_freedom", "improve_relations", 0, 0, "알제리 자유 코뮌", "알제리를 다시 정복하는 대신 그 땅의 노동자들에게 손을 내밉니다. 알제의 코뮌이 연합에 들어오면 총성 없이 반란이 끝납니다.",
          algeria.PACIFY, pre=[ANA + "militarisation"], route=ANA_ROUTE, available=algeria.OPEN)
    focus(ANA + "rhine", "major_war", 0, 0, "라인강 건너 형제들에게", "루르의 광부들에게 총과 자유를 함께 가져갑니다.", goal("GER"), pre=[ANA + "militarisation"], route=ANA_ROUTE)
    focus(ANA + "danube", "major_war", 0, 0, "민족의 감옥을 부수다", "합스부르크의 감옥 문을 엽니다.", goal("AUS"), pre=[ANA + "rhine"], route=ANA_ROUTE)
    focus(ANA + "channel", "major_war", 0, 0, "해협 건너로", "귀족 의회의 섬으로 건너갑니다.", goal("ENG"), pre=[ANA + "rhine"], route=ANA_ROUTE)
    red.define(g)
    defeat.define(g)
    alliances.define(g)


def arrange(g):
    plan, require, gate, BY_ID, FILTERS, add_effects = (g[n] for n in ("plan", "require", "gate", "BY_ID", "FILTERS", "add_effects"))
    plan(PET, "marshal", [
        ("내정", ["labour_charter", "family_code", "return_to_soil", "peasant_corporation", "youth_camps", "secours_national", "school_cross"]),
        ("정치", ["national_revolution", "constitutional_acts", "legion", "national_council", "riom_trial", ("heir_weygand", "heir_darlan")]),
        ("영토확장", ["verdun_doctrine", "maginot", "rhine"]),
        ("외교", ["madrid_embassy", "vatican", ("montoire", "hidden_sword")]),
        ("안정도", ["suppress", "uproot"]),
    ])
    BY_ID[PET + "algeria"]["pre"] = [PET + "maginot"]
    plan(ANA, "federation", [
        ("내정", ["syndicates_take", "collectives", "abolish_money", "free_communes", "housing", "rationalist_schools", "ateneos"]),
        ("정치", ["proudhon", "abolish_prefects", "mandates", "congress", ("platform", "synthesis")]),
        ("영토확장", ["columns", "elected_officers", "militarisation", "rhine"]),
        ("외교", ["cnt_brothers", "carrara", "iwa", "free_territory"]),
        ("안정도", ["suppress", "uproot"]),
    ])
    BY_ID[ANA + "algerian_freedom"]["pre"] = [ANA + "militarisation"]
    for prefix, keys in ((PET, ["algeria", "rhine", "danube", "channel", "russia"]), (ANA, ["algerian_freedom", "rhine", "danube", "channel"])):
        for key in keys:
            BY_ID[prefix + key]["filter"] = FILTERS["영토확장"]
    for head in (PET + "marshal", ANA + "federation"):
        BY_ID[head]["filter"] = FILTERS["정치"]
    # The great wars wait for the army, the previous war and the Channel fleet, as on every route.
    for prefix in (PET, ANA):
        require(prefix + "rhine", "has_completed_focus = LR_FRA_revenge_army\n" + algeria.NOT_CAMPAIGNING)
        require(prefix + "channel", "has_completed_focus = LR_FRA_fusiliers_marins")
        add_effects(prefix + "rhine", "29 = { set_demilitarized_zone = no }")
    require(PET + "russia", "has_country_flag = LR_germany_defeated")
    red.arrange(g)
    defeat.arrange(g)



def weave_routes(g):
    weave = g["weave"]
    weave(PET, "marshal", "내정", [["labour_charter", "family_code"], ["return_to_soil<labour_charter", "youth_camps<family_code", "secours_national<family_code"],
                                    ["peasant_corporation<return_to_soil", "school_cross<youth_camps"]])
    weave(PET, "marshal", "정치", [["national_revolution"], ["constitutional_acts", "legion"], ["national_council<constitutional_acts", "riom_trial<legion"],
                                    [("heir_weygand<national_council+riom_trial", "heir_darlan<national_council+riom_trial")]])
    weave(PET, "marshal", "외교", [["madrid_embassy"], ["vatican"], [("montoire", "hidden_sword")]])
    weave(ANA, "federation", "내정", [["syndicates_take", "free_communes"], ["collectives<syndicates_take", "housing<free_communes"],
                                       ["abolish_money<collectives", "rationalist_schools<housing"], ["ateneos<rationalist_schools"]])
    weave(ANA, "federation", "정치", [["proudhon"], ["abolish_prefects", "mandates"], ["congress<abolish_prefects+mandates"], [("platform", "synthesis")]])
    red.weave_routes(g)
    defeat.weave_routes(g)


def spirits(g):
    spirit = g["spirit"]
    spirit(PET + "marshal", "베르됭의 원수", "그들은 지나가지 못했다. 그 원수가 이제 나라를 지킵니다.", "generic_fortify_the_borders", {"stability_factor": 0.08, "war_support_factor": 0.03})
    spirit(PET + "constitutional_acts", "국가원수", "공화국 대통령의 자리는 사라지고 국가원수 한 사람이 남았습니다.", "generic_central_management", {"political_power_gain": 0.1})
    spirit(ANA + "federation", "자유 코뮌 연합", "위원회도 당도 없는 혁명입니다. 결정은 느리고, 사람들은 자기 결정을 지킵니다.", "generic_local_self_management", {"stability_factor": 0.05, "communism_drift": 0.02})
    spirit(ANA + "congress", "코뮌 대회", "전국의 코뮌과 조합이 한 회관에 모였습니다.", "generic_local_self_management", {"political_power_gain": 0.05, "stability_factor": 0.03})
    red.spirits(g)
    defeat.spirits(g)


# ===== Story: one chapter per spine focus, each fires its event =====
STORY = [
    ("LR_PET_marshal", PET, PET_ROUTE, 1400, [
        chapter("vichy", "political_pressure", "온천 도시의 정부", "정부가 파리를 떠나 오베르뉴의 온천 도시로 옮겨 갑니다.", {"stability_factor": 0.02},
                "파르크 호텔 3층", P.join([
                    "비시의 파르크 호텔. 온천객이 묵던 객실마다 타자기와 서류철이 들어찼습니다. 욕실은 문서고가 되었고, 3층 복도 끝 방에 원수의 집무실이 차려졌습니다.",
                    "각료들은 방이 좁다고 불평합니다. 원수는 파리의 소음과 거리의 군중에게서 멀리 떨어진 이곳이 마음에 든다고 말합니다.",
                    say("파리는 늘 프랑스를 배신했소."),
                    "비서실장이 조심스럽게 묻습니다. 수도를 정말 이곳에 두시겠습니까?"]), "generic_read_write", [
                    ("비시가 새 수도다. 파리는 혁명의 도시일 뿐이다.", {"stability_factor": 0.03, "flag": "LR_st_pet_vichy"}),
                    ("임시일 뿐이다. 질서가 서면 파리로 돌아간다.", {"political_power_gain": 0.03}),
                ]),
        chapter("portrait", "propaganda", "원수의 초상", "모든 교실과 관공서에 같은 얼굴이 걸립니다.", {"stability_factor": 0.02},
                "원수님, 우리가 여기 있습니다", P.join([
                    "아침 여덟 시, 리모주의 어느 초등학교. 아이들이 칠판 위에 걸린 흰 콧수염의 노인 사진을 향해 노래합니다. 원수님, 우리가 여기 있습니다.",
                    "담배 가게에는 원수의 얼굴이 찍힌 접시와 달력이 쌓였고, 우표에도 그 얼굴이 들어갔습니다. 여든 살 노인은 생애 처음으로 사랑받는 것 같다고 측근에게 털어놓았습니다.",
                    "선전부 장관이 다음 계획서를 내밉니다. 원수의 생일을 국경일로 정하자는 안입니다."]), "france_parade", [
                    ("국경일로 정한다. 나라에는 아버지가 필요하다.", {"stability_factor": 0.04, "war_support_factor": 0.02}),
                    ("과하다. 원수는 군인이지 성인이 아니다.", {"political_power_gain": 0.03, "army_morale_factor": 0.02}),
                ]),
        chapter("laval", "dangerous_deal", "라발의 귀환", "누구와도 거래할 줄 아는 정치인이 원수의 문을 두드립니다.", {"political_power_gain": 0.02},
                "흰 넥타이의 사나이", P.join([
                    "피에르 라발이 언제나처럼 흰 넥타이를 매고 집무실에 들어섭니다. 그는 의회 시절 총리를 두 번 지냈고, 원수는 의회 시절의 모든 것을 경멸합니다.",
                    say("원수님은 군대를 아시고, 저는 사람을 압니다. 런던과 베를린의 사람들 말입니다."),
                    "라발이 나가자 베강 장군이 문을 닫으며 낮게 말합니다. " + say("저 자는 프랑스도 팔 겁니다."),
                    "원수는 대답 없이 창밖의 공원을 오래 바라봅니다."]), "generic_parliament", [
                    ("라발을 부총리로 앉힌다. 더러운 일에는 더러운 손이 필요하다.", {"political_power_gain": 0.05, "stability_factor": -0.02, "flag": "LR_st_pet_laval"}),
                    ("12월 13일, 그를 해임하고 가택에 연금한다.", {"stability_factor": 0.03, "army_morale_factor": 0.02}),
                ]),
        chapter("riom", "forceful_treaty", "리옴 법정", "패배와 혼란의 책임을 물을 재판이 열립니다.", {"war_support_factor": 0.02},
                "피고석의 공화국", P.join([
                    "리옴 법원의 대법정. 피고석에는 옛 총리와 장관, 장군들이 앉아 있습니다. 혐의는 대전쟁의 패배와 그 뒤 프랑스를 약하게 만든 죄입니다.",
                    "그런데 재판이 생각대로 흘러가지 않습니다. 피고들이 거꾸로 검사를 몰아세웁니다. 전쟁 전에 군사 예산을 깎은 위원회의 위원장이 누구였느냐고. 방청석의 기자들이 그 이름을 받아 적습니다. 위원장은 원수 자신이었습니다.",
                    "법무장관이 다급하게 휴정을 건의합니다."]), "generic_read_write", [
                    ("재판을 끝까지 간다. 진실이 원수를 해치지는 않는다.", {"democratic_drift": 0.02, "stability_factor": 0.02}),
                    ("무기한 휴정한다. 판결은 이미 내려져 있다.", {"political_power_gain": 0.04, "fascism_drift": 0.02}),
                ]),
        chapter("last_winter", "national_unity", "늙은 원수의 겨울", "여든을 넘긴 원수에게 남은 시간을 셉니다.", {"stability_factor": 0.03},
                "원수의 유언장", P.join([
                    "비시의 겨울은 춥습니다. 원수는 아침마다 공원을 산책하고 오후에는 낮잠을 잡니다. 그가 대화 도중 이름을 잊는 일이 잦아졌다고 측근들은 쉬쉬합니다.",
                    "변호사가 봉인된 봉투를 들고 왔습니다. 헌법 법령 제4호. 원수가 쓰러지면 국가원수를 이을 사람의 이름이 들어갈 빈칸입니다.",
                    "원수는 만년필을 들었다가 다시 내려놓습니다. 그가 세운 나라는 그가 없어도 서 있을 수 있을까요?"]), "generic_read_write", [
                    ("라발의 이름을 적는다. 그는 살아남는 법을 안다.", {"political_power_gain": 0.08, "need": "LR_st_pet_laval"}),
                    ("군에게 맡긴다. 프랑스를 구한 것은 언제나 군대였다.", {"war_support_factor": 0.05, "army_org_factor": 0.03}),
                    ("빈칸으로 둔다. 국민 혁명이 곧 후계자다.", {"stability_factor": 0.06}),
                ]),
    ]),
    ("LR_ANA_federation", ANA, ANA_ROUTE, 1500, [
        chapter("no_masters", "construct_civ_factory", "주인 없는 공장", "사장이 떠난 공장에서 첫 월요일이 밝습니다.", {"industrial_capacity_factory": 0.02},
                "비양쿠르의 첫 월요일", P.join([
                    "르노 비양쿠르 공장의 월요일 아침. 사장실은 비었고, 정문 위에는 검은색과 붉은색으로 반씩 나뉜 깃발이 걸렸습니다. 노동자 총회가 밤새 생산 계획을 투표로 정했습니다.",
                    "그런데 문제가 생겼습니다. 트럭 라인은 트랙터를 만들자 하고, 엔진 라인은 무기를 만들자 합니다. 누구도 명령할 권한이 없습니다. 그것이 이 혁명의 요점입니다.",
                    "총회 의장이 연합 서기국에 전화를 겁니다. 서기국은 결정할 권한이 없다고 답합니다."]), "generic_factory", [
                    ("총회가 정한다. 시간이 걸려도 그것이 자유다.", {"stability_factor": 0.03, "communism_drift": 0.02}),
                    ("조합들이 모여 전국 생산 조정위원회를 꾸린다.", {"industrial_capacity_factory": 0.03, "flag": "LR_st_ana_coord"}),
                ]),
        chapter("vendee_coop", "construct_civilian", "방데의 농민들", "집산 농장 가입서가 방데의 마을 광장에 도착합니다.", {"stability_factor": 0.02},
                "엽총과 협동조합", P.join([
                    "방데의 어느 마을 광장. 파리에서 온 청년들이 집산 농장 가입서를 탁자에 펼쳤습니다. 농민들은 팔짱을 끼고 서 있습니다.",
                    say("우리는 땅을 원했지, 당신네 공동 농장을 원한 게 아니오."),
                    "청년 하나가 바쿠닌을 인용하자 뒤에서 엽총을 장전하는 소리가 납니다. 그때 늙은 대장장이가 앞으로 나섭니다. 억지로 가입시키는 집산은 지주가 바뀐 것뿐이라고.",
                    "청년들이 서기국에 지시를 청합니다."]), "generic_riot", [
                    ("가입은 자유다. 원하는 사람만 집산한다.", {"stability_factor": 0.04, "op": 1}),
                    ("혁명은 기다려 주지 않는다. 코뮌 총회로 밀어붙인다.", {"industrial_capacity_factory": 0.02, "stability_factor": -0.02, "flag": "LR_st_ana_forced"}),
                ]),
        chapter("platform_debate", "army_doctrines", "강령과 종합", "연합의 두 경향이 벨빌의 회관에서 밤새 맞섭니다.", {"political_power_gain": 0.02},
                "벨빌의 밤샘 토론", P.join([
                    "벨빌의 낡은 노동자 회관. 담배 연기 속에서 두 진영이 밤새 맞서고 있습니다.",
                    "강령파는 우크라이나 초원의 흑군이 왜 무너졌는지 따집니다. 조직이 없었기 때문이라고. 규율과 공동 전술, 하나의 강령이 필요하다고.",
                    "종합파의 늙은 연설가가 일어섭니다. " + say("규율, 강령, 집행부. 동지들, 그런 물건을 사람들은 당이라고 부르오. 우리는 그것을 없애려고 혁명을 했소."),
                    "새벽 다섯 시, 의장이 표결을 부칩니다."]), "generic_parliament", [
                    ("강령파의 손을 든다. 살아남아야 자유도 있다.", {"army_org_factor": 0.03, "political_power_gain": 0.03}),
                    ("종합파의 손을 든다. 수단이 목적을 삼키게 두지 않는다.", {"stability_factor": 0.04, "communism_drift": 0.02}),
                ]),
        chapter("commissars", "intelligence_exchange", "중앙파의 사절", "가죽 외투를 입은 사내들이 파리 북역에 내립니다.", {"war_support_factor": 0.02},
                "가죽 외투의 사내들", P.join([
                    "회색 가죽 외투를 입은 사내 셋이 파리 북역에 내렸습니다. 유럽 각지에서 망명해 온 중앙집권파 공산주의자들의 대표단입니다. 그들이 연합에 조건을 내밉니다.",
                    "무기와 돈을 주겠다. 대신 민병대에 정치위원을 두고, 연합 대회에 당의 대표단을 받아들이라.",
                    "바르셀로나에서 온 동지가 귀띔합니다. " + say("저들이 들어온 도시에서 우리 동지들이 하나둘 사라졌소.")]), "military_planning", [
                    ("무기는 받고 위원은 거절한다.", {"army_attack_factor": 0.02, "political_power_gain": -0.02}),
                    ("문을 닫는다. 붉은 관료도 관료다.", {"stability_factor": 0.03, "war_support_factor": 0.02, "flag": "LR_st_ana_closed"}),
                ]),
        chapter("anarchy_spring", "national_unity", "국가 없는 첫 봄", "연합이 첫돌을 맞습니다. 국경에는 왕들의 군대가 모입니다.", {"stability_factor": 0.03},
                "국가 없는 첫 봄", P.join([
                    "1년이 지났습니다. 파리 시청에는 시장이 없고, 경찰서는 도서관이 되었습니다. 빵은 여전히 모자라지만 줄은 예전보다 짧습니다.",
                    "외국 신문들은 1년 내내 프랑스가 곧 무너질 것이라고 썼습니다. 프랑스는 무너지지 않았습니다. 대신 그들은 묻습니다. 국가 없이 전쟁을 치를 수 있느냐고. 왕들의 군대가 국경에 모이고 있습니다.",
                    "연합 대회가 마지막 의제를 올립니다. 혁명을 지키는 방법입니다."]), "soldiers_marching", [
                    ("모든 코뮌이 무장한다. 침략자는 마을마다 싸워야 할 것이다.", {"army_defence_factor": 0.05, "conscription_factor": 0.03}),
                    ("국경 너머의 노동자들에게 혁명을 가져간다.", {"war_support_factor": 0.05, "army_attack_factor": 0.03}),
                    ("조정위원회에 전시 권한을 준다. 이번 한 번만.", {"political_power_gain": 0.06, "industrial_capacity_factory": 0.03, "need": "LR_st_ana_coord"}),
                ]),
    ]),
]

# ===== Branch events: (focus, picture, title, short text, options) =====
BRANCH = [
    ("LR_PET_labour_charter", "generic_factory", "조합의 첫 회의", "노동 헌장에 따라 제철 조합의 첫 회의가 열렸습니다.", [
        ("사장 편을 든다. 질서가 먼저다.", {"industrial_capacity_factory": 0.02, "stability_factor": -0.01}),
        ("노동자 대표에게 빵값만큼은 양보한다.", {"stability_factor": 0.02}),
    ]),
    ("LR_PET_legion", "france_parade", "베레모의 노병들", "참전용사 군단이 마을마다 지부를 세웠습니다.", [
        ("밀고를 맡긴다. 군단은 원수의 눈이다.", {"political_power_gain": 0.03, "raw": ["lr_fra_op_reduce = yes"]}),
        ("구호와 행진만 맡긴다.", {"stability_factor": 0.02}),
    ]),
    ("LR_PET_return_to_soil", "generic_read_write", "흙은 거짓말을 하지 않는다", "도시 실업자들이 농촌으로 보내졌습니다.", [
        ("농기계를 나눠 준다.", {"raw": ["add_political_power = -25"], "dev": 1}),
        ("맨손으로 시작하게 한다. 그것이 정신 교육이다.", {"stability_factor": 0.01, "raw": ["add_manpower = 5000"]}),
    ]),
    ("LR_ANA_syndicates_take", "generic_factory", "경영자 없는 장부", "자주 관리 공장의 첫 결산이 나왔습니다.", [
        ("남는 돈은 다른 공장과 나눈다.", {"stability_factor": 0.02, "communism_drift": 0.01}),
        ("새 기계를 산다.", {"industrial_capacity_factory": 0.02}),
    ]),
    ("LR_ANA_columns", "soldiers_marching", "검은 종대", "첫 민병대 종대가 동부로 떠납니다.", [
        ("대장을 뽑게 둔다.", {"army_morale_factor": 0.03}),
        ("옛 하사관을 고문으로 붙인다.", {"army_org_factor": 0.02}),
    ]),
    ("LR_ANA_abolish_money", "generic_read_write", "쿠폰과 신뢰", "돈을 불태운 마을의 첫 겨울입니다.", [
        ("이웃 코뮌에 밀을 꾸어 준다.", {"stability_factor": 0.02, "raw": ["add_political_power = -25"]}),
        ("실험을 접고 배급표를 돈처럼 쓴다.", {"political_power_gain": 0.02}),
    ]),
]

BRANCH_TEXT = {
    "LR_PET_labour_charter": P.join([
        "로렌 제철 조합의 첫 회의. 긴 탁자 한쪽에는 드방델 가문의 이사들이, 다른 쪽에는 해산된 노조의 옛 간부들이 앉았습니다. 가운데에는 원수의 초상이 걸려 있습니다.",
        "사장 측은 임금을 동결하자고 하고, 노동자 측은 빵값이 두 배가 됐다고 맞섭니다. 파업은 이제 불법입니다.",
        say("원수님은 계급 투쟁을 끝내자고 하셨소. 누가 양보할 차례요?")]),
    "LR_PET_legion": P.join([
        "일요일 아침, 오베르뉴의 어느 마을 광장. 베레모에 훈장을 단 노병들이 원수의 초상을 앞세우고 행진합니다. 참전용사 군단의 마을 지부가 문을 열었습니다.",
        "지부장이 군청에 편지를 보냈습니다. 마을 교사가 수업 시간에 원수를 비웃었고, 우체국장은 런던 방송을 듣는다고.",
        "군수가 묻습니다. 이 편지들을 어떻게 할까요?"]),
    "LR_PET_return_to_soil": P.join([
        "리옹역에서 기차 세 량이 출발합니다. 실직한 선반공과 사무원들이 농촌의 빈 농가로 갑니다. 역 벽에는 원수의 말이 붙어 있습니다. 흙은 거짓말을 하지 않는다.",
        "도착한 마을의 농민들은 고개를 젓습니다. 파리 사람들이 쟁기를 잡는 법부터 배워야 한다고.",
        say("농기계를 보내 주십시오. 아니면 이 사람들이 봄까지 버티지 못합니다.")]),
    "LR_ANA_syndicates_take": P.join([
        "자주 관리 공장의 첫 결산. 회계를 맡은 젊은 여공이 칠판에 숫자를 씁니다. 사장이 가져가던 이윤이 고스란히 남았습니다.",
        "총회가 둘로 갈립니다. 굶는 이웃 공장과 나누자는 쪽과, 낡은 기계부터 바꾸자는 쪽입니다.",
        say("우리 공장만 부자가 되면, 우리가 새 사장이 되는 거요.")]),
    "LR_ANA_columns": P.join([
        "리옹 페라슈역. 첫 민병대 종대가 열차에 오릅니다. 계급장은 없고, 소매에 검붉은 완장을 찼습니다. 플랫폼의 어머니들이 손을 흔듭니다.",
        "종대에는 지휘관이 없습니다. 병사들이 열차 안에서 손을 들어 대표를 뽑기로 했습니다. 대전쟁을 겪은 옛 하사관 하나가 고개를 젓습니다.",
        say("총알은 투표를 기다려 주지 않소.")]),
    "LR_ANA_abolish_money": P.join([
        "돈을 불태운 마을의 첫 겨울. 빵집과 대장간은 배급표로 돌아갑니다. 처음 몇 달은 잘 굴러갔습니다.",
        "그런데 옆 마을에서 밀을 사려면 여전히 프랑이 필요합니다. 그 마을은 아직 돈을 쓰기 때문입니다.",
        "총회 의장이 묻습니다. 이웃 코뮌에 밀을 꾸어 달라고 할까요, 아니면 실험을 여기서 접을까요?"]),
}

# ===== War speeches for the two new families =====
WAR_TEXTS = {
    "ALG": {
        "petain": P.join([
            "원수가 라디오 마이크 앞에 앉습니다. 떨리는 늙은 목소리가 알제리의 모든 마을에 흘러갑니다.",
            say("나는 프랑스에 내 몸을 바쳤소. 이제 질서를 바치겠소."),
            "툴롱 부두에서 수송선이 떠납니다. 병사들은 원수의 초상이 찍힌 배지를 달았습니다."]),
    },
    "GER": {
        "petain": P.join([
            "원수가 베르됭의 납골당을 찾았습니다. 13만 명의 이름 없는 유골 앞에서 그는 한참을 말없이 서 있었습니다.",
            say("나는 이곳에서 그들이 지나가지 못하게 했소. 이제 우리가 지나갈 차례요."),
            "여든 살 원수의 선전포고문은 짧았습니다. 라인강으로 가는 기차에 오른 병사들은 그가 마지막 전쟁을 이기고 죽기를 바랍니다."]),
        "anarchist": P.join([
            "연합 대회가 표결로 전쟁을 결정했습니다. 찬성 412, 반대 97. 반대한 대표들도 총을 받으러 갑니다.",
            say("우리는 독일과 싸우지 않는다. 베를린의 왕과 싸운다. 루르의 광부들이여, 국경은 왕들이 그은 선일 뿐이다!"),
            "종대들이 노래를 부르며 동쪽으로 갑니다. 그들의 짐 가방에는 탄약보다 전단이 더 많습니다."]),
    },
    "AUS": {
        "petain": P.join([
            "원수가 빈에 보낸 선전포고문에는 혁명도 해방도 없습니다. 오로지 질서와 국경, 그리고 패전의 빚을 갚는다는 말뿐입니다.",
            say("합스부르크는 프랑스를 무릎 꿇린 승전국이오. 그 빚을 받으러 가는 것이오."),
            "참모본부는 원수가 늘 그랬듯 신중한 계획을 세웁니다. 서두르지 않고, 한 걸음씩."]),
        "anarchist": P.join([
            "파리의 라디오가 체코어와 헝가리어, 크로아티아어로 연합의 선언문을 읽습니다.",
            say("민족의 감옥을 부수러 간다. 간수만 바꾸러 가는 것이 아니다. 우리가 지나간 곳에는 황제도, 새 왕도, 위원회도 남지 않을 것이다."),
            "도나우를 향하는 종대의 깃발은 검은색과 붉은색입니다."]),
    },
    "ENG": {
        "petain": P.join([
            "원수는 오래도록 영국을 믿지 않았습니다. 대전쟁 때 영국군이 먼저 후퇴하려 했던 날을 그는 잊지 않았습니다.",
            say("섬나라는 언제나 대륙의 피로 자기 전쟁을 치렀소."),
            "브레스트와 셰르부르의 항구에 함대가 모입니다. 원수의 마지막 명령서가 해군 장관에게 전달됩니다."]),
        "anarchist": P.join([
            "연합 대회가 런던의 귀족 의회에 선전포고합니다. 맨체스터와 글래스고의 부두 노동자들에게 보내는 편지가 함께 실렸습니다.",
            say("우리는 섬을 정복하러 가지 않는다. 그 섬의 주인들을 끝내러 간다."),
            "선원 조합이 투표로 출항을 결정합니다. 함장도 선원 총회에서 뽑혔습니다."]),
    },
    "SOV": {
        "petain": P.join([
            "원수가 러시아에 선전포고합니다. 케렌스키의 공화국은 왕들의 유럽에 남은 마지막 혁명의 등불이고, 원수는 혁명이라는 말을 혐오합니다.",
            say("볼셰비키든 케렌스키든, 혁명은 언제나 같은 곳에서 끝나오."),
            "장군들은 겨울 군복부터 주문합니다. 원수는 겨울을 아는 사람입니다."]),
    },
}
FAMILY_CLOSE = {
    "petain": "원수가 지팡이를 짚고 일어서서 짧게 말합니다. 노동, 가족, 조국. 프랑스 만세, 원수 만세!",
    "anarchist": "연합 대회가 표결을 마치자 회관이 노래로 가득 찹니다. 왕도 신도 주인도 없다! 검붉은 깃발이 국경으로 갑니다.",
}

# ===== Focus descriptions =====
FOCUS_TEXT = {
    "LR_PET_marshal": "반발을 다스리지 못한 정부가 무너졌습니다. 대전쟁에서 베르됭을 지킨 여든 살 원수가 전권을 쥡니다. 그는 혁명도 왕정도 아닌 세 번째 길을 약속합니다. 질서, 노동, 가족, 조국. 프랑스는 다시 아버지를 갖게 되었습니다.",
    "LR_PET_labour_charter": "파업도 직장 폐쇄도 없는 나라. 노동조합과 사장 단체를 해산하고, 업종마다 노동자와 사장이 함께 들어가는 조합을 세웁니다. 계급 투쟁은 법으로 금지됩니다. 원수는 이것을 화해라고 부르고, 노동자들은 침묵이라고 부릅니다.",
    "LR_PET_family_code": "대전쟁이 앗아간 한 세대의 빈자리가 아직 메워지지 않았습니다. 어머니의 날이 국가 기념일이 되고, 아이를 셋 이상 둔 가정에는 수당이 나옵니다. 이혼은 어려워지고, 기혼 여성은 공직에서 물러나야 합니다.",
    "LR_PET_return_to_soil": "흙은 거짓말을 하지 않는다. 원수의 말이 역마다 붙습니다. 도시의 실업자와 노동자를 농촌의 빈 농가로 보냅니다. 공장과 노조가 혁명을 낳았다면, 밭과 교회는 질서를 낳을 것이라고 정부는 믿습니다.",
    "LR_PET_peasant_corporation": "모든 농민이 하나의 조합에 가입합니다. 조합은 씨앗과 비료를 나누고 수확량과 가격을 정합니다. 그 조합의 지도부는 원수가 임명한 지방 명사들입니다.",
    "LR_PET_youth_camps": "스무 살 청년들이 군복과 비슷한 초록색 제복을 입고 여덟 달 동안 숲과 산으로 갑니다. 그들은 나무를 베고 길을 닦고 저녁마다 원수에게 바치는 노래를 부릅니다. 징병이 금지된 나라에서 이것은 징병과 아주 닮았습니다.",
    "LR_PET_secours_national": "국민 구호 단체가 원수의 이름으로 겨울 외투와 빵을 나눠 줍니다. 빵 봉투에는 원수의 얼굴이 찍혀 있습니다. 배부른 마을은 바리케이드를 쌓지 않습니다.",
    "LR_PET_school_cross": "공화국이 50년 전에 떼어 냈던 십자가가 교실 벽에 다시 걸립니다. 교과서에서 혁명의 영웅들이 빠지고 잔 다르크와 성왕 루이가 들어옵니다. 교사 노조는 해산되었습니다.",
    "LR_PET_national_revolution": "자유, 평등, 박애. 150년 동안 공화국의 동전에 새겨진 세 낱말이 노동, 가족, 조국으로 바뀝니다. 원수는 이것을 국민 혁명이라고 부릅니다. 혁명을 가장 싫어하는 사람이 혁명이라는 말을 고른 것입니다.",
    "LR_PET_constitutional_acts": "헌법 법령 제1호. 원수가 국가원수의 칭호를 취합니다. 대통령의 자리는 사라지고, 의회는 무기한 휴회합니다. 법은 이제 원수의 서명 하나로 만들어집니다.",
    "LR_PET_legion": "대전쟁의 참전용사들이 하나의 군단으로 묶입니다. 베레모를 쓴 노병들은 마을마다 지부를 세우고 원수의 초상을 앞세워 행진합니다. 그리고 이웃의 이름을 적어 군청에 보냅니다.",
    "LR_PET_national_council": "선거로 뽑힌 의원 대신 원수가 지명한 명사들이 국민 평의회에 모입니다. 주교, 장군, 농민 조합장, 사장, 몇 명의 노동자 대표. 그들은 토론하지만 결정하지는 않습니다.",
    "LR_PET_riom_trial": "패배와 혼란의 책임을 옛 정부의 총리와 장관, 장군들에게 묻습니다. 리옴의 법정에서 공화국 그 자체가 피고석에 앉습니다. 그러나 피고들은 순순히 고개를 숙일 사람들이 아닙니다.",
    "LR_PET_heir_weygand": "원수 다음은 군대입니다. 대전쟁 때 포슈의 참모장이었던 베강 장군이 후계자로 지명됩니다. 그는 원수보다도 늙었고, 원수보다도 의회를 싫어합니다.",
    "LR_PET_heir_darlan": "원수 다음은 함대입니다. 해군을 손에 쥔 다를랑 제독이 후계자로 지명됩니다. 그는 누구와도 거래할 줄 알고, 해군만은 끝까지 지킨 사람입니다.",
    "LR_PET_madrid_embassy": "원수는 젊은 날 모로코에서 스페인군과 함께 싸웠고, 그 인연으로 마드리드 대사를 지냈습니다. 그 시절의 친구들이 지금 스페인 궁정의 장군들입니다. 피레네 너머로 다시 편지를 씁니다.",
    "LR_PET_vatican": "교황청이 원수에게 축복을 보냅니다. 교회의 재산이 돌아오고, 수도회가 다시 학교를 맡습니다. 혁명이 쫓아낸 신부들이 150년 만에 강단으로 돌아옵니다.",
    "LR_PET_montoire": "몽투아르의 작은 역에서 원수가 승전국의 대표와 악수합니다. 배상금은 줄고, 국경은 조용해집니다. 그 대신 프랑스의 칼은 칼집에 들어갑니다. 사진 한 장이 전 세계 신문에 실립니다.",
    "LR_PET_hidden_sword": "악수는 하되 칼은 숨깁니다. 원수의 참모들이 동원 명부를 다시 쓰고, 무기를 산속 창고로 옮깁니다. 감독관들이 오면 빈 창고와 차 한 잔이 그들을 맞습니다.",
    "LR_PET_verdun_doctrine": "그들은 지나가지 못한다. 1916년 베르됭에서 원수가 남긴 말이 육군의 교리가 됩니다. 화력과 요새, 참호와 예비대. 원수는 공세를 믿지 않습니다. 먼저 버티고, 적이 지칠 때 나아갑니다.",
    "LR_PET_maginot": "예산이 끊겨 멈춰 있던 요새 공사를 다시 시작합니다. 콘크리트와 강철이 알자스와 로렌의 언덕 아래로 들어갑니다. 원수는 공사장을 둘러보며 만족스럽게 고개를 끄덕입니다.",
    "LR_PET_suppress": "반발이 큰 지역마다 헌병대와 계엄령이 내려집니다. 통행금지, 검문, 신문 검열. 원수의 프랑스에서 질서는 협상의 대상이 아닙니다.",
    "LR_PET_uproot": "공산주의자의 비밀 인쇄소와 왕당파의 무기고를 같은 날 덮칩니다. 원수의 경찰은 좌우를 가리지 않습니다. 그날 이후 프랑스의 지하에는 아무도 남지 않습니다.",
    "LR_PET_algeria": "알제리는 다시 질서를 원한다고 원수는 믿습니다. 원수의 초상이 찍힌 배지를 단 병사들이 툴롱 부두에서 수송선에 오릅니다.",
    "LR_PET_rhine": "여든 살 원수가 생애 마지막 공세를 명령합니다. 그는 베르됭에서 지켰고, 이제 라인강으로 나아갑니다. 신중하게, 한 걸음씩.",
    "LR_PET_danube": "프랑스를 무릎 꿇린 승전국들 가운데 가장 오래된 왕가가 빈에 있습니다. 원수는 그 빚을 받으러 갑니다.",
    "LR_PET_channel": "원수는 대전쟁 때 영국군이 먼저 물러나려 했던 날을 잊지 않았습니다. 이번에는 해협을 건너갑니다.",
    "LR_PET_russia": "왕들의 유럽에 남은 마지막 혁명의 나라입니다. 원수는 혁명이라는 말을 혐오하고, 겨울을 아는 사람입니다.",
    "LR_PET_vichy": "정부가 파리를 떠나 오베르뉴의 온천 도시 비시로 옮겨 갑니다. 파리는 언제나 혁명의 도시였고, 원수는 혁명의 도시에서 다스리고 싶지 않습니다.",
    "LR_PET_portrait": "흰 콧수염의 노인 사진이 모든 교실과 관공서, 담배 가게와 우표에 걸립니다. 원수의 얼굴은 이제 프랑스의 얼굴입니다.",
    "LR_PET_laval": "흰 넥타이의 사나이 피에르 라발이 원수의 문을 두드립니다. 그는 누구와도 거래할 줄 압니다. 그것이 그의 장점이고, 그것이 그의 위험입니다.",
    "LR_PET_riom": "리옴 법원에서 옛 공화국의 지도자들이 재판을 받습니다. 그러나 피고들은 순순히 고개를 숙이지 않습니다.",
    "LR_PET_last_winter": "여든을 넘긴 원수에게 남은 시간을 세는 사람들이 있습니다. 그가 세운 나라는 그가 없어도 서 있을 수 있을까요.",
    "LR_ANA_federation": "총선에서 이긴 사회주의자들이 둘로 갈라졌습니다. 중앙위원회 대신 코뮌과 조합의 자유 연합을 택한 사람들이 이겼습니다. 파리 시청에 검은색과 붉은색으로 나뉜 깃발이 오릅니다. 위원회도 당도 없는 혁명이 시작됩니다.",
    "LR_ANA_syndicates_take": "사장실이 비었습니다. 공장마다 노동자 총회가 생산 계획과 임금과 근무 시간을 투표로 정합니다. 공장은 그곳에서 일하는 사람들의 것입니다.",
    "LR_ANA_free_communes": "파리가 보낸 시장 대신 코뮌 총회가 코뮌을 다스립니다. 일요일 오후 성당 앞 광장에서 사람들이 손을 들어 우물과 학교와 도로를 정합니다.",
    "LR_ANA_collectives": "원하는 코뮌은 땅과 쟁기와 수확을 함께 씁니다. 원하지 않는 사람은 자기 밭을 그대로 갈아도 됩니다. 강제로 만든 집산은 지주가 바뀐 것뿐이라고 연합은 말합니다.",
    "LR_ANA_abolish_money": "몇몇 코뮌이 마을 광장에서 프랑 지폐를 불태웁니다. 빵집과 대장간은 배급표로 돌아갑니다. 유럽의 은행가들은 이 소식에 웃음을 터뜨렸다가 곧 웃음을 멈춥니다.",
    "LR_ANA_housing": "부자들이 떠난 빈 저택과 아파트에 판자촌의 가족들이 들어갑니다. 16구의 응접실에서 벨빌의 아이들이 숙제를 합니다.",
    "LR_ANA_rationalist_schools": "바르셀로나의 페레르가 꿈꾸던 학교가 프랑스에 문을 엽니다. 신부도 국가도 없는 교실에서 아이들은 외우는 대신 묻는 법을 배웁니다. 시험도 상장도 없습니다.",
    "LR_ANA_ateneos": "동네마다 민중 회관이 생깁니다. 낮에는 도서관이고 저녁에는 강연장이며 주말에는 극장입니다. 글을 모르던 노인들이 여기서 처음 신문을 읽습니다.",
    "LR_ANA_proudhon": "재산은 도둑질이다라고 쓴 사람, 프루동의 연방주의를 꺼냅니다. 나라는 위에서 아래로가 아니라, 코뮌에서 지역으로, 지역에서 연합으로, 아래에서 위로 묶입니다.",
    "LR_ANA_abolish_prefects": "나폴레옹 이래 파리의 명령을 지방에 전하던 도지사들을 모두 집으로 돌려보냅니다. 도청 건물은 학교와 병원이 됩니다.",
    "LR_ANA_mandates": "대표는 총회가 정해 준 대로만 말하고, 총회는 언제든 대표를 불러들일 수 있습니다. 직업 정치인이라는 말이 이 나라에서 사라집니다.",
    "LR_ANA_congress": "전국의 코뮌과 조합이 대표를 보내 첫 연합 대회를 엽니다. 회의는 엿새 동안 이어지고, 의장은 하루에 한 번씩 바뀝니다.",
    "LR_ANA_platform": "강령파가 이겼습니다. 하나의 강령, 하나의 전술, 공동의 책임. 우크라이나 초원의 흑군이 조직이 없어서 무너졌다는 교훈을 그들은 잊지 않았습니다.",
    "LR_ANA_synthesis": "종합파가 이겼습니다. 아나코생디칼리스트도, 개인주의자도, 공산주의적 아나키스트도 같은 회관을 씁니다. 수단이 목적을 삼키게 두지 않겠다는 약속입니다.",
    "LR_ANA_columns": "계급장 없는 민병대 종대가 조직됩니다. 소매에는 검붉은 완장을 차고, 노래를 부르며 열차에 오릅니다. 그들에게는 장군 대신 대표가 있습니다.",
    "LR_ANA_elected_officers": "병사들이 손을 들어 대표를 뽑습니다. 대표는 앞장서서 싸우고, 잘못하면 다음 날 소환됩니다. 옛 장교들은 이것이 군대인지 묻습니다.",
    "LR_ANA_militarisation": "왕들의 군대는 노래를 부르며 오지 않습니다. 긴 토론 끝에 연합은 결론에 이릅니다. 민병대에도 규율과 훈련과 참모가 필요하다고. 옛 하사관들이 다시 교관이 됩니다.",
    "LR_ANA_cnt_brothers": "피레네 너머 바르셀로나에는 프랑스보다 오래된 조합 운동이 있습니다. 그들에게 전단과 돈, 그리고 언젠가는 총을 보냅니다.",
    "LR_ANA_carrara": "토스카나의 대리석 채석장 카라라는 이탈리아 무정부주의의 요람입니다. 채석공들의 조합에 파리의 편지가 도착합니다.",
    "LR_ANA_iwa": "베를린에서 세워졌다가 잠든 조합들의 인터내셔널, 국제노동자협회를 파리에서 다시 깨웁니다. 스웨덴과 포르투갈과 아르헨티나의 조합원들이 답장을 보냅니다.",
    "LR_ANA_free_territory": "대전쟁 뒤 우크라이나 초원에서 흑군이 세웠던 자유 영토를 기억하는 사람들이 아직 살아 있습니다. 그들에게 편지를 보냅니다.",
    "LR_ANA_suppress": "코뮌 총회가 뽑은 자경단이 반혁명 조직을 감시합니다. 경찰은 없지만 눈은 많습니다.",
    "LR_ANA_uproot": "왕당파 장교와 지주의 비밀 무기고를 모두 비웁니다. 총을 내려놓은 사람은 집으로 돌아갈 수 있습니다. 그날 이후 반혁명은 무기를 잃습니다.",
    "LR_ANA_algerian_freedom": "알제리를 다시 정복하는 대신, 그 땅의 부두 노동자와 농민들에게 손을 내밉니다. 국경은 왕들이 그은 선일 뿐이라고 연합은 말합니다.",
    "LR_ANA_rhine": "루르의 광부들에게 총과 자유를 함께 가져갑니다. 이것은 프랑스와 독일의 전쟁이 아니라 노동자와 왕의 전쟁이라고 연합 대회는 선언했습니다.",
    "LR_ANA_danube": "합스부르크의 민족의 감옥을 부수러 갑니다. 간수만 바꾸러 가는 것이 아닙니다.",
    "LR_ANA_channel": "런던의 귀족 의회를 끝내러 갑니다. 선원 조합이 투표로 출항을 결정했습니다.",
    "LR_ANA_no_masters": "사장이 떠난 공장에서 첫 월요일이 밝습니다. 누구도 명령할 권한이 없습니다. 그것이 이 혁명의 요점입니다.",
    "LR_ANA_vendee_coop": "집산 농장 가입서가 방데의 마을 광장에 도착합니다. 150년 전에도 방데는 파리의 혁명과 싸웠습니다.",
    "LR_ANA_platform_debate": "연합의 두 경향, 강령파와 종합파가 벨빌의 낡은 회관에서 밤새 맞섭니다.",
    "LR_ANA_commissars": "회색 가죽 외투를 입은 중앙집권파의 사절들이 무기와 조건을 들고 파리 북역에 내립니다.",
    "LR_ANA_anarchy_spring": "연합이 첫돌을 맞습니다. 국가 없는 1년을 버텼습니다. 그러나 국경에는 왕들의 군대가 모이고 있습니다.",
}

# ===== Visual-novel scenes: pages before the hand-written events =====
NOVEL = {
    "lr_france.51": {
        "pages": [
            P.join([
                "새벽 네 시, 파리 앵발리드.",
                "참모본부 지하 회의실의 전등이 밤새 꺼지지 않았습니다. 탁자 위에는 지방 도지사들이 보낸 전보가 수북합니다. 방데에서 경찰서가 불탔고, 리옹에서는 노동자들이 시청을 점거했으며, 북부의 탄광은 석 달째 멈춰 있습니다.",
                "장군 하나가 전보 더미를 손바닥으로 내리칩니다. " + say("이 정부로는 겨울을 넘기지 못하오."),
            ]),
            P.join([
                "같은 시각, 파리 서쪽의 작은 저택. 여든 살 노인이 이미 일어나 군복 단추를 채우고 있습니다.",
                "필리프 페탱 원수. 1916년 베르됭에서 그들은 지나가지 못한다고 말한 사람입니다. 대전쟁에서 진 나라에서 유일하게 지지 않은 이름입니다.",
                "현관에 차가 멈춥니다. 내린 장교들이 경례합니다. 원수는 지팡이를 짚고 천천히 계단을 내려옵니다.",
                say("늦었구먼. 10년은 늦었어."),
            ]),
            P.join([
                "차 안. 원수는 창밖의 파리를 말없이 봅니다. 센강 다리 위에 노동자 민병대의 붉은 완장이 보이고, 그 옆에서 헌병들이 못 본 척 담배를 피웁니다.",
                "옆자리의 젊은 대령이 서류철을 내밉니다. 체포할 각료 명단, 장악할 방송국, 해산할 노조 목록. 원수는 그것을 펼쳐 보지도 않고 무릎 위에 놓습니다.",
                say("대령, 이 명단에 있는 사람들도 프랑스인이네. 총은 쏘지 말게. 문만 닫게."),
                "대령은 경례했지만, 서류철 맨 뒷장에 따로 적힌 또 하나의 명단에 대해서는 말하지 않았습니다.",
            ]),
            P.join([
                "아침 아홉 시, 정부 청사 앞. 전차 여섯 대가 정문을 막아섰습니다. 경비병들은 총을 내려놓았습니다. 누구도 원수에게 총을 겨누려 하지 않았습니다.",
                "회의실에 들어선 원수가 각료들을 둘러봅니다. 아무도 일어서지 않습니다. 그가 낮은 목소리로 말합니다.",
                say("여러분은 프랑스를 다스리지 못했소. 이제 내가 프랑스에 내 몸을 바치겠소."),
            ]),
        ],
    },
    "lr_france.50": {
        "pages": [
            P.join([
                "총선 다음 날 밤, 파리 시청 대회의실.",
                "사회주의 세력이 이겼습니다. 그런데 이긴 사람들이 하나가 아닙니다. 대회의실 왼쪽에는 중앙위원회를 세우자는 공산주의자들이, 오른쪽에는 위원회 자체를 없애자는 아나키스트들이 앉았습니다.",
                "그 사이 통로에서 벨빌의 노동자들이 담배를 피우며 기다립니다. 누가 이기든 내일 아침 공장 문은 열려야 합니다.",
            ]),
            P.join([
                "공산주의자 대표가 연단에 오릅니다.",
                say("혁명은 아직 끝나지 않았소. 왕들의 군대가 국경에 있소. 중앙위원회 없이, 규율 없이, 우리는 석 달도 버티지 못할 것이오."),
                "박수가 절반쯤 터집니다. 나머지 절반은 팔짱을 낍니다.",
            ]),
            P.join([
                "조합 연합의 늙은 서기가 일어섭니다. 1906년 아미앵 헌장에 서명한 사람입니다.",
                say("동지들, 우리는 왕을 쫓아냈소. 그 자리에 위원회를 앉히려고 그랬소? 공장은 노동자에게, 마을은 마을 사람에게. 우리는 국가를 빼앗으러 온 게 아니라 끝내러 왔소."),
                "회의실이 함성과 야유로 가득 찹니다. 의장이 종을 칩니다. 표결입니다.",
            ]),
            P.join([
                "휴회 십오 분. 복도에서 두 사람이 마주칩니다. 붉은 별을 단 젊은 위원과, 검은 스카프를 두른 철도원입니다. 둘은 생탕투안의 같은 바리케이드에서 사흘을 함께 버텼습니다.",
                say("자네들이 이기면 누가 군대를 지휘하나? 왕들이 쳐들어오면 투표로 막을 텐가?"),
                say("자네들이 이기면 누가 위원회를 지휘하나? 위원회가 왕이 되면 그때는 누구에게 투표하나?"),
                "둘은 대답하지 않고 담배 한 개비를 나눠 피웁니다. 종이 울립니다. 둘은 서로 다른 문으로 회의실에 돌아갑니다.",
            ]),
        ],
    },
}
NOVEL_BASE = {"lr_france.50": 900, "lr_france.51": 1000}


# Red Napoleon joins every table.
STORY.extend(red.STORY)
BRANCH.extend(red.BRANCH)
BRANCH_TEXT.update(red.BRANCH_TEXT)
for _target, _texts in red.WAR_TEXTS.items():
    WAR_TEXTS.setdefault(_target, {}).update(_texts)
FAMILY_CLOSE.update(red.FAMILY_CLOSE)
FOCUS_TEXT.update(red.FOCUS_TEXT)
NOVEL.update(red.NOVEL)
NOVEL_BASE.update(red.NOVEL_BASE)
REGIMES.update(red.REGIMES)
FAMILIES = {"petain": (PET_ROUTE,), "anarchist": (ANA_ROUTE,), "red": (red.RED_ROUTE,)}

# The occupation after a defeat joins the tables too.
STORY.extend(defeat.STORY)
BRANCH.extend(defeat.BRANCH)
BRANCH_TEXT.update(defeat.BRANCH_TEXT)
FOCUS_TEXT.update(defeat.FOCUS_TEXT)
NOVEL.update(defeat.NOVEL)
NOVEL_BASE.update(defeat.NOVEL_BASE)
REGIMES.update(defeat.REGIMES)
