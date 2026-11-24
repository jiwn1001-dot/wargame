"""America's focus trees: the colonial government (USA) and the Continental Congress (CNA), and the three factions of
the civil war that follows Washington's murder (AMC, LNG, DXE). build_america.py writes them.

Routes (the user's design, 2026-11-24):
- USA, the colonial government: crush the 1937 rising, then stay loyal to the Empire in the world war, conquer New
  Spain and the Spanish Americas in the King's name, and take Canada in peacefully.
- CNA, the Congress: win the war of independence. Washington's July Fourth speech decides the rest. If he lives, the
  democratic United States. If he dies: riots, a British embargo, the reds rising, MacArthur's coup and a four-way civil
  war - MacArthur (the upper South and the capital), the communists (the North), Long (the Midwest), Dixie (the Deep
  South). Whoever wins makes the country: the Amerigo Empire, the Union of American Socialist Republics, Long's United
  States, or the Amerigo Confederacy.

Descriptions are in the polite style of docs/STYLE_GUIDE.md, section 6.
"""
from split_states import expand

TREES = {
    "lr_usa_focus": {"tags": ["USA"], "show": 10, "focuses": []},
    "lr_cna_focus": {"tags": ["CNA"], "show": 12, "focuses": []},
    "lr_amc_focus": {"tags": ["AMC"], "show": 6, "focuses": []},
    "lr_lng_focus": {"tags": ["LNG"], "show": 6, "focuses": []},
    "lr_dxe_focus": {"tags": ["DXE"], "show": 6, "focuses": []},
}

# New Spain's lands north of the Rio Grande (build_world gives them to MEX) and the Spanish Americas.
NEW_SPAIN_NORTH = expand([375, 376, 377, 378, 379, 380])
SPANISH_AMERICA_NORTH = ["CUB", "GUA"]
SPANISH_AMERICA_ANDES = ["COL", "VEN", "PRU"]
SPANISH_AMERICA_SOUTH = ["ARG", "CHL"]


def indent(text, tabs=1):
    pad = "\t" * tabs
    return "\n".join(pad + line if line else line for line in text.split("\n"))


def build(kind, level):
    return ("random_owned_controlled_state = {\n"
            f"\tadd_extra_state_shared_building_slots = {level}\n"
            f"\tadd_building_construction = {{\n\t\ttype = {kind}\n\t\tlevel = {level}\n\t\tinstant_build = yes\n\t}}\n}}")


def civ(n): return build("industrial_complex", n)
def mil(n): return build("arms_factory", n)
def dock(n):
    return ("random_owned_controlled_state = {\n\tlimit = { is_coastal = yes }\n"
            f"\tadd_extra_state_shared_building_slots = {n}\n"
            f"\tadd_building_construction = {{\n\t\ttype = dockyard\n\t\tlevel = {n}\n\t\tinstant_build = yes\n\t}}\n}}")
def infra(n):
    return ("every_owned_state = {\n\tlimit = { is_controlled_by = ROOT }\n\trandom_select_amount = 3\n"
            f"\tadd_building_construction = {{\n\t\ttype = infrastructure\n\t\tlevel = {n}\n\t\tinstant_build = yes\n\t}}\n}}")
def pp(n): return f"add_political_power = {n}"
def stab(x): return f"add_stability = {x}"
def war(x): return f"add_war_support = {x}"
def xp(kind, n): return f"{kind}_experience = {n}"
def tech(name, category):
    return f"add_tech_bonus = {{\n\tname = {name}\n\tbonus = 1.0\n\tuses = 1\n\tcategory = {category}\n}}"
def idea(name): return f"add_ideas = {name}"
def timed(name, days): return f"add_timed_idea = {{\n\tidea = {name}\n\tdays = {days}\n}}"
def flag(name): return f"set_country_flag = {name}"
def tt(key): return f"custom_effect_tooltip = {key}"
def pop(ideology, value): return f"add_popularity = {{\n\tideology = {ideology}\n\tpopularity = {value}\n}}"
def manpower(n): return f"add_manpower = {n}"
def rifles(n): return f"add_equipment_to_stockpile = {{\n\ttype = infantry_equipment\n\tamount = {n}\n}}"
def event(eid, days=0): return f"country_event = {{ id = {eid}{f' days = {days}' if days else ''} }}"
def opinion(tag, modifier="medium_increase"):
    return f"if = {{\n\tlimit = {{ {tag} = {{ exists = yes }} }}\n\t{tag} = {{ add_opinion_modifier = {{ target = ROOT modifier = {modifier} }} }}\n}}"


def war_on(*tags):
    out = []
    for tag in tags:
        out.append(f"if = {{\n\tlimit = {{\n\t\t{tag} = {{ exists = yes }}\n\t\tNOT = {{ tag = {tag} }}\n\t\tNOT = {{ has_war_with = {tag} }}\n\t}}\n"
                   f"\tdeclare_war_on = {{\n\t\ttarget = {tag}\n\t\ttype = annex_everything\n\t}}\n}}")
    return "\n".join(out)


def claim_tag(*tags):
    return "\n".join(f"every_state = {{\n\tlimit = {{ is_owned_by = {tag} }}\n\tROOT = {{ add_state_claim = PREV }}\n}}" for tag in tags)


def claim_states(states):
    return "\n".join(f"if = {{\n\tlimit = {{ NOT = {{ {s} = {{ is_owned_by = ROOT }} }} }}\n\tadd_state_claim = {s}\n}}" for s in states)


def hurt(tags, value):
    """Stability lost by the other factions of the civil war."""
    return "\n".join(f"if = {{\n\tlimit = {{ {t} = {{ exists = yes has_war_with = ROOT }} }}\n\t{t} = {{ add_stability = {value} }}\n}}" for t in tags)


def focus(tree, fid, icon, x, y, name, desc, *effects, pre=(), me=(), branch=None, available=None, cost=10, ai=1):
    """pre holds AND groups; a tuple inside is an OR group. branch: the country flag that shows and opens the focus."""
    TREES[tree]["focuses"].append(dict(id=fid, icon=icon, x=x, y=y, name=name, desc=desc, effects=effects, pre=pre, me=me,
                                       branch=branch, available=available, cost=cost, ai=ai))


AT_WAR_WITH = "{tag} = {{ exists = yes }}\nhas_war_with = {tag}"
NO_WAR = "has_war = no"

# ============================================================================================================
# The colonial government
# ============================================================================================================
T = "lr_usa_focus"
U = "LR_USA_"
focus(T, U + "colony_1936", "national_unity", 10, 0, "총독부의 1936년",
      "뉴욕 총독 관저 정문에는 1776년 반란군이 남긴 탄흔이 아직 남아 있습니다. 백육십 년 동안 런던은 열세 식민지를 지켰고, 식민지는 런던을 먹여 살렸습니다. "
      "그러나 대전쟁에서 돌아온 식민지 장교들은 더 이상 그 셈법을 믿지 않습니다.",
      pp(50), stab(0.05), cost=5)

# Economy
focus(T, U + "atlantic_trade", "trade", 4, 1, "대서양 무역 협정",
      "식민지의 밀과 면화는 리버풀을 거쳐야만 세상으로 나갈 수 있습니다. 총독부는 런던에 관세를 조금만 낮춰 달라고 청원합니다. "
      "뉴욕 상공회의소가 총독부의 청원서에 함께 서명한 것은 1770년 이후 처음입니다.",
      pp(75), civ(1), pre=[U + "colony_1936"])
focus(T, U + "colonial_industry", "construct_civ_factory", 3, 2, "식민지 공업 진흥",
      "공장 굴뚝이 늘면 반역도 함께 는다는 것이 런던의 오랜 믿음이었습니다. 총독부는 그 믿음을 거스르기로 했습니다. "
      "피츠버그와 클리블랜드에 세울 공장 허가서 스물두 장이 이번 주 우편선으로 런던에 갑니다.",
      civ(2), pre=[U + "atlantic_trade"])
focus(T, U + "arms_subcontract", "construct_mil_factory", 5, 2, "병기 하청",
      "영국 병기창은 본토의 주문만으로도 벅찹니다. 남는 주문을 식민지 공장에 넘기면 런던은 돈을 아끼고 총독부는 일자리를 얻습니다. "
      "다만 그렇게 만든 소총이 결국 누구의 손에 들어갈지는 아무도 장담하지 못합니다.",
      mil(2), pre=[U + "atlantic_trade"])
focus(T, U + "great_lakes_steel", "production", 3, 3, "오대호 제철",
      "미네소타의 철광석이 오대호를 건너 게리와 디트로이트의 용광로로 들어갑니다. 그 용광로의 절반은 아직 영국 자본가의 것입니다. "
      "총독부는 전시에 대비해 이 용광로들을 직접 관리하는 법안을 식민지 의회에 냅니다.",
      tech(U + "great_lakes_steel", "industry"), mil(1), pre=[U + "colonial_industry"])
focus(T, U + "rail_crown", "construct_infrastructure", 5, 3, "총독부 철도청",
      "애팔래치아를 넘는 철도는 열한 개 회사가 제각각 운영합니다. 궤간도 운임도 다릅니다. "
      "총독부는 이들을 총독부 철도청 아래 묶어, 병력과 석탄이 한 시간이라도 빨리 움직이게 하려 합니다.",
      infra(1), civ(1), pre=[U + "arms_subcontract"])
focus(T, U + "kings_college", "scientific_exchange", 4, 4, "킹스 칼리지 연구소",
      "뉴욕의 킹스 칼리지는 영국 귀족 의회가 세운 식민지 최고의 학교입니다. 총독부는 이곳에 전기와 화학 연구소를 붙이려 합니다. "
      "본국에 기대지 않고도 쓸 만한 기술을 얻으려면, 런던보다 먼저 식민지 젊은이들을 붙잡아야 합니다.",
      "add_research_slot = 1", pre=[U + "great_lakes_steel", U + "rail_crown"])

# Politics before the rising
focus(T, U + "royal_garrison", "fortify_city", 10, 1, "제국 수비대 증강",
      "보스턴과 필라델피아의 술집에서 워싱턴이라는 이름이 다시 오르내립니다. 버지니아의 퇴역 소령이 무슨 일을 꾸미는지 총독부는 아직 모릅니다. "
      "우선 제국 수비대를 두 개 대대 늘려 주요 도시에 배치합니다.",
      xp("army", 10), war(0.05), pre=[U + "colony_1936"])
focus(T, U + "coercive_acts", "political_pressure", 9, 2, "강압법",
      "집회를 금하고, 신문을 검열하고, 혐의자는 영장 없이 가둡니다. 1774년에 같은 이름의 법이 무엇을 낳았는지 기억하는 관리도 있습니다. "
      "그러나 총독은 그때보다 더 철저하게 하면 된다고 믿습니다.",
      idea("LR_usa_coercive"), flag("LR_usa_coercive"), tt("LR_tt_usa_coercive"),
      pre=[U + "royal_garrison"], me=[U + "conciliation"])
focus(T, U + "conciliation", "improve_relations", 11, 2, "유화 칙령",
      "식민지 의회에 예산 심의권을 돌려주고, 식민지 출신 장교의 진급 상한을 없앱니다. 런던의 귀족들은 질색할 것입니다. "
      "그러나 반란의 불씨는 분노보다 무시에서 자라고, 총독부는 그 불씨에 먼저 물을 붓기로 했습니다.",
      idea("LR_usa_conciliation"), flag("LR_usa_conciliation"), tt("LR_tt_usa_conciliation"),
      pre=[U + "royal_garrison"], me=[U + "coercive_acts"])
focus(T, U + "loyalist_militia", "allies_build_infantry", 10, 3, "충성파 민병대",
      "뉴욕과 캐롤라이나에는 아직도 런던을 조국으로 여기는 집이 많습니다. 그 집 아들들을 모아 충성파 민병대를 꾸립니다. "
      "정규군만은 못해도, 이웃의 얼굴을 아는 병사는 쓸모가 있습니다.",
      idea("LR_usa_loyalist_militia"), pre=[(U + "coercive_acts", U + "conciliation")])
focus(T, U + "colonial_intelligence", "intelligence_exchange", 10, 4, "총독부 정보국",
      "필라델피아의 비밀 회합, 버지니아의 무기 거래, 보스턴의 지하 인쇄소. 흩어진 소문을 하나로 꿰어 줄 기관이 필요합니다. "
      "총독부 정보국은 런던 경찰청에서 수사관 열두 명을 데려와 출범합니다.",
      flag("LR_usa_intel"), tt("LR_tt_usa_intel"), pp(25), pre=[U + "loyalist_militia"])

# Army before the rising
focus(T, U + "colonial_defence", "army_doctrines", 15, 1, "식민지 방위군",
      "식민지 방위군은 영국군의 하급 조직입니다. 장교의 삼분의 일이 식민지 출신이지만 대령 이상은 한 명도 없습니다. "
      "총독부는 방위군을 다시 편성해, 전쟁이 나면 본국의 증원 없이도 석 달은 버티게 하려 합니다.",
      xp("army", 25), pre=[U + "colony_1936"])
focus(T, U + "springfield", "small_arms", 14, 2, "스프링필드 소총",
      "매사추세츠의 스프링필드 병기창은 식민지에서 가장 오래된 총기 공장입니다. 이곳의 소총은 영국군 제식 소총보다 가볍고 정확합니다. "
      "총독부는 이 소총을 방위군의 표준 장비로 정하고 주문량을 두 배로 늘립니다.",
      tech(U + "springfield", "infantry_weapons"), pre=[U + "colonial_defence"])
focus(T, U + "coastal_guns", "army_artillery", 16, 2, "해안 포대",
      "체서피크 만과 뉴욕 항구의 포대는 1812년 이후 거의 손대지 않았습니다. 대서양 너머의 적보다 항구 안의 적을 겨눌 일이 더 많을지도 모릅니다. "
      "그래도 대포는 어느 쪽으로든 돌릴 수 있습니다.",
      tech(U + "coastal_guns", "artillery"), pre=[U + "colonial_defence"])
focus(T, U + "air_command", "build_airforce", 14, 3, "영국 공군 북미 사령부",
      "영국 공군은 북아메리카에 비행장 일곱 곳과 낡은 복엽기 몇십 대만 두었습니다. 총독부는 식민지 예산으로 비행장을 늘리고 조종사를 기르겠다고 제안했습니다. "
      "런던은 예산 이야기만 귀담아들었습니다.",
      xp("air", 25), pre=[U + "springfield"])
focus(T, U + "detroit_trucks", "army_motorized", 16, 3, "디트로이트의 트럭",
      "디트로이트의 자동차 공장은 하루에 트럭 수천 대를 찍어 냅니다. 이 트럭에 보병을 태우면 식민지의 넓은 땅도 좁아집니다. "
      "방위군은 디트로이트에서 첫 차량화 대대를 꾸립니다.",
      tech(U + "detroit_trucks", "motorized_equipment"), pre=[U + "coastal_guns"])
focus(T, U + "staff_college", "army_doctrines", 15, 4, "킹스턴 참모대학",
      "식민지 장교가 참모 교육을 받으려면 지금까지는 영국 캠벌리까지 가야 했습니다. 그 여비를 감당한 장교는 한 해에 넷뿐이었습니다. "
      "총독부는 온타리오와 맞닿은 킹스턴에 참모대학을 세워 이 길을 넓힙니다.",
      xp("army", 25), tech(U + "staff_college", "land_doctrine"), pre=[U + "air_command", U + "detroit_trucks"])

# The war against the Congress
REBEL_WAR = AT_WAR_WITH.format(tag="CNA")
focus(T, U + "crush_rising", "occupy_start_war", 10, 5, "반란 진압 작전",
      "7월 4일, 워싱턴이 필라델피아에서 독립을 선언했고 열세 식민지의 절반이 그의 깃발을 따랐습니다. "
      "총독부는 본국의 증원을 기다리지 않고, 반란군의 심장인 펜실베이니아를 먼저 치기로 했습니다.",
      xp("army", 25), war(0.1), timed("LR_usa_crown_offensive", 180),
      pre=[U + "colony_1936"], available=REBEL_WAR, cost=5, ai=5)
focus(T, U + "hudson_line", "fortify_city", 9, 6, "허드슨 강 방어선",
      "1777년 영국군은 허드슨 강을 따라 식민지를 둘로 자르려다 사라토가에서 무너졌습니다. 이번에는 강을 지키는 쪽이 총독부입니다. "
      "뉴잉글랜드의 반란군이 남쪽과 손잡지 못하도록 강변에 진지를 쌓습니다.",
      timed("LR_usa_hudson_line", 180), pre=[U + "crush_rising"], available=REBEL_WAR, cost=5, ai=5)
focus(T, U + "blockade", "navy_doctrines_tactics", 11, 6, "해상 봉쇄",
      "반란군에게는 해군이 없습니다. 영국 대서양 함대가 보스턴과 볼티모어 앞바다를 막으면 프랑스제 소총도 스페인 은화도 들어오지 못합니다. "
      "총독부는 해군성에 봉쇄를 정식으로 요청합니다.",
      xp("navy", 25), "CNA = {\n\tadd_timed_idea = {\n\t\tidea = LR_usa_blockaded\n\t\tdays = 180\n\t}\n}",
      pre=[U + "crush_rising"], available=REBEL_WAR, cost=5, ai=5)
focus(T, U + "bounty", "political_pressure", 10, 7, "반란 수괴 현상금",
      "조지 워싱턴의 목에 현상금 1만 파운드가 걸렸습니다. 대륙 회의의 의원과 장군들에게도 각각 값이 매겨졌습니다. "
      "총독부는 반란군 병사들이 그 돈의 무게를 느끼고, 지휘관 가운데 누군가는 계산을 시작하길 바랍니다.",
      "CNA = {\n\tadd_stability = -0.1\n\tadd_war_support = -0.05\n}", pre=[(U + "hudson_line", U + "blockade")],
      available=REBEL_WAR, cost=5, ai=5)

# After the rising is crushed
CRUSHED = "LR_usa_crushed"
focus(T, U + "crown_peace", "national_unity", 10, 8, "제국 아래의 평화",
      "반란은 끝났습니다. 필라델피아 독립기념관의 종은 다시 떼어 냈고, 대륙 회의 의원들은 재판을 기다립니다. "
      "총독부는 이 승리를 어디에 쓸지 정해야 합니다. 본국을 도울 수도, 남쪽을 칠 수도, 북쪽과 손잡을 수도 있습니다.",
      stab(0.1), idea("LR_usa_crown_loyalty"), branch=CRUSHED)
# A: loyal to the Empire
focus(T, U + "oath", "improve_relations", 5, 9, "충성의 맹세",
      "총독은 식민지 의회 의원 전원에게 런던의 귀족 의회에 다시 충성을 맹세하게 했습니다. 맹세를 거부한 열한 명은 의석을 잃었습니다. "
      "런던의 신문들은 맹세하는 의원들의 사진을 일주일 내내 일면에 실었습니다.",
      pp(50), opinion("ENG", "large_increase"), pre=[U + "crown_peace"], branch=CRUSHED)
focus(T, U + "join_league", "major_alliance", 5, 10, "제국연맹 가입",
      "식민지는 지금까지 본국의 전쟁에 세금으로만 참여했습니다. 이제 북아메리카는 제국연맹의 정식 회원으로, 자기 군대를 걸고 회의 탁자에 앉으려 합니다. "
      "오타와와 캔버라는 아직 그런 대우를 받지 못했습니다.",
      "if = {\n\tlimit = {\n\t\tENG = { is_faction_leader = yes }\n\t\tis_in_faction = no\n\t}\n\tENG = { add_to_faction = ROOT }\n}",
      tt("LR_tt_usa_join_league"), pre=[U + "oath"], branch=CRUSHED)
focus(T, U + "convoys", "navy_anti_submarine", 4, 11, "대서양 수송단",
      "식민지의 공장은 본국보다 두 배 많은 강철을 만듭니다. 그 강철이 대서양을 건너야 제국이 싸울 수 있습니다. "
      "뉴욕과 핼리팩스에서 출발하는 수송단을 지킬 구축함 전대를 꾸립니다.",
      dock(2), xp("navy", 25), pre=[U + "join_league"], branch=CRUSHED)
focus(T, U + "expedition", "attack_allies", 6, 11, "북미 원정군",
      "1916년, 식민지 병사 이십만 명이 플랑드르의 진흙에 묻혔습니다. 워싱턴도 그 진흙 속에 있었습니다. "
      "이번에는 식민지 장교가 식민지 병사를 이끌고 유럽에 갑니다. 총독부는 제국이 그 대가를 기억해 주길 바랍니다.",
      xp("army", 50), "ENG = {\n\tevery_enemy_country = {\n\t\tlimit = { NOT = { tag = ROOT } }\n\t\tROOT = {\n\t\t\tdeclare_war_on = {\n\t\t\t\ttarget = PREV\n\t\t\t\ttype = annex_everything\n\t\t\t}\n\t\t}\n\t}\n}",
      tt("LR_tt_usa_expedition"), pre=[U + "join_league"], branch=CRUSHED, ai=3)
focus(T, U + "imperial_arsenal", "construct_mil_factory", 5, 12, "제국 병기창",
      "총독부는 식민지 병기창 생산량의 삼분의 일을 본국에 보내기로 했습니다. 의회에서는 반대 목소리도 나왔습니다. "
      "그러나 반란이 진압된 지 얼마 되지 않은 지금, 충성은 말보다 물건으로 증명해야 합니다.",
      mil(3), "if = {\n\tlimit = { ENG = { exists = yes } }\n\tENG = {\n\t\tadd_equipment_to_stockpile = {\n\t\t\ttype = infantry_equipment\n\t\t\tamount = 8000\n\t\t\tproducer = USA\n\t\t}\n\t}\n}",
      pre=[U + "convoys", U + "expedition"], branch=CRUSHED)
focus(T, U + "empire_partner", "military_deal", 5, 13, "제국의 동반자",
      "제국연맹 이사회가 북아메리카에 상임 의석을 주기로 했습니다. 식민지 출신 장군이 제국 참모본부에 들어간 것도 처음입니다. "
      "이제 뉴욕의 목소리는 런던에서도 무게를 가집니다. 그 무게가 언제까지 충성으로만 쓰일지는 두고 볼 일입니다.",
      idea("LR_usa_empire_partner"), stab(0.05), pre=[U + "imperial_arsenal"], branch=CRUSHED)
# B: conquer New Spain and the Spanish Americas
focus(T, U + "southern_threat", "demand_territory", 10, 9, "남쪽 국경의 위협",
      "누에바 에스파냐 왕국은 텍사스에서 캘리포니아까지 북아메리카의 삼분의 일을 쥐고 있습니다. 반란 중에 멕시코시티가 대륙 회의에 은화를 보낸 증거가 나왔습니다. "
      "총독부는 그 증거를 런던에 보내고, 대답을 기다리지 않습니다.",
      claim_tag("MEX"), war(0.05), pre=[U + "crown_peace"], branch=CRUSHED)
focus(T, U + "new_spain_campaign", "occupy_start_war", 10, 10, "누에바 에스파냐 원정",
      "총독부의 군대가 미시시피를 건너 텍사스로, 다시 캘리포니아로 나아갑니다. 스페인 본국은 아직 내전에서 빠져나오지 못했습니다. "
      "멕시코시티의 부왕은 혼자 싸워야 합니다.",
      flag("LR_usa_annex_americas"), tt("LR_tt_usa_annex_americas"), war_on("MEX"), xp("army", 25), pre=[U + "southern_threat"], branch=CRUSHED, available=NO_WAR, ai=5)
focus(T, U + "mexican_viceroyalty", "national_unity", 10, 11, "멕시코 총독령",
      "부왕궁에 유니언잭이 올랐습니다. 멕시코는 독립국도 스페인령도 아닌, 북아메리카 총독부가 다스리는 총독령이 됩니다. "
      "크리올로 귀족들은 작위를 지키는 대가로 새 주인에게 충성을 맹세합니다. 맹세하지 않은 가문의 땅은 경매에 붙여졌습니다.",
      idea("LR_usa_viceroyalty"), stab(0.05), pre=[U + "new_spain_campaign"], branch=CRUSHED,
      available="custom_trigger_tooltip = {\n\ttooltip = LR_tt_usa_mexico_gone\n\tNOT = { MEX = { exists = yes } }\n}")
focus(T, U + "caribbean", "occupy_states_coastal", 9, 12, "카리브와 중미",
      "쿠바와 과테말라는 누에바 에스파냐의 그늘에 기대 온 공국들입니다. 부왕이 무너진 지금 그들은 기댈 곳이 없습니다. "
      "총독부의 함대가 아바나 앞바다에 닻을 내립니다.",
      war_on(*SPANISH_AMERICA_NORTH), pre=[U + "mexican_viceroyalty"], branch=CRUSHED, available=NO_WAR, ai=5)
focus(T, U + "andes", "occupy_states_ongoing_war", 11, 12, "안데스 원정",
      "누에바 그라나다와 베네수엘라, 페루의 왕국들은 내전으로 지쳐 있습니다. 총독부는 파나마를 거쳐 남쪽으로 내려가는 원정을 준비합니다. "
      "런던은 은과 구리, 석유 이야기를 듣고 나서 반대를 거둬들였습니다.",
      war_on(*SPANISH_AMERICA_ANDES), pre=[U + "mexican_viceroyalty"], branch=CRUSHED, available=NO_WAR, ai=4)
focus(T, U + "southern_cone", "territory_or_war", 10, 13, "남방 원정",
      "리오데라플라타와 칠레는 신대륙의 남쪽 끝에서 아직 스페인 왕의 이름으로 다스려집니다. 그들이 무너지면 신대륙의 스페인 깃발은 모두 내려갑니다. "
      "브라질은 포르투갈의 일이니 건드리지 않습니다.",
      war_on(*SPANISH_AMERICA_SOUTH), pre=[U + "caribbean", U + "andes"], branch=CRUSHED, available=NO_WAR, ai=4)
focus(T, U + "new_world_crown", "national_unity", 10, 14, "신대륙의 제국",
      "알래스카에서 파타고니아까지, 신대륙 대부분이 같은 제국의 깃발 아래 들어왔습니다. 그 제국의 대리인은 런던이 아니라 뉴욕에 앉아 있습니다. "
      "총독부는 이 새 질서에 걸맞은 이름을 런던에 청합니다.",
      "set_cosmetic_tag = LR_USA_americas", stab(0.1), pp(100), "news_event = { id = lr_usa.65 days = 1 }",
      pre=[U + "southern_cone"], branch=CRUSHED)
# C: Canada, peacefully
focus(T, U + "open_border", "positive_trade_relations", 15, 9, "국경 없는 자치령",
      "온타리오와 뉴욕 사이의 세관은 1783년 이후 한 번도 닫힌 적이 없습니다. 두 식민지는 같은 의회의 법을 따르고 같은 말을 씁니다. "
      "총독부는 오타와에 관세 동맹을 제안합니다.",
      civ(1), opinion("CAN", "large_increase"), pre=[U + "crown_peace"], branch=CRUSHED)
focus(T, U + "ottawa_talks", "improve_relations", 15, 10, "오타와 회담",
      "캐나다 총리 매켄지 킹은 반란 진압을 지켜보며 다음은 퀘벡일지 모른다는 두려움을 느꼈습니다. "
      "총독부는 두 자치령을 하나로 묶어야만 그런 일이 다시 없을 것이라고 설득합니다. 회담은 열이틀 동안 이어졌습니다.",
      pp(50), opinion("CAN", "large_increase"), pre=[U + "open_border"], branch=CRUSHED)
focus(T, U + "union_bill", "national_unity", 15, 11, "북아메리카 통합",
      "캐나다와 북아메리카 총독부를 하나의 자치령으로 합치는 법안이 웨스트민스터 의회에 올라갔습니다. "
      "최종 결정은 런던의 귀족 의회가 내립니다. 총독부는 런던의 대답을 기다립니다.",
      "ENG = { country_event = { id = lr_usa.62 days = 3 } }", tt("LR_tt_usa_union_bill"), pre=[U + "ottawa_talks"], branch=CRUSHED,
      available="CAN = {\n\texists = yes\n\tis_subject_of = ENG\n}\nENG = { exists = yes }")
focus(T, U + "union_parliament", "political_pressure", 15, 12, "통합 자치령 의회",
      "오타와와 뉴욕에서 뽑힌 의원들이 처음으로 한 의사당에 앉았습니다. 퀘벡 의원들은 프랑스어 통역을 요구했고, 총독부는 들어주었습니다. "
      "북아메리카는 이제 하나의 정부로 움직입니다.",
      stab(0.1), civ(2), "set_cosmetic_tag = LR_USA_dominion", pre=[U + "union_bill"], branch=CRUSHED,
      available="custom_trigger_tooltip = {\n\ttooltip = LR_tt_usa_canada_joined\n\thas_country_flag = LR_usa_canada_joined\n}")
focus(T, U + "sun_never_sets", "national_unity", 10, 15, "해가 지지 않는 대륙",
      "북아메리카는 본국보다 크고, 본국보다 부유하며, 본국보다 많은 병사를 냅니다. 언젠가 제국의 중심이 대서양을 건너올 것이라고 말하는 이들이 런던에도 생겼습니다. "
      "총독부는 그 말을 굳이 부정하지 않습니다.",
      idea("LR_usa_heart_of_empire"), stab(0.05), pre=[U + "new_world_crown", (U + "empire_partner", U + "union_parliament")], branch=CRUSHED)

# ============================================================================================================
# The Continental Congress
# ============================================================================================================
T = "lr_cna_focus"
C = "LR_CNA_"
FIGHTING_GOVERNOR = "has_war = yes"
focus(T, C + "second_congress", "national_unity", 12, 0, "제2차 대륙회의",
      "1937년 7월 4일, 필라델피아 독립기념관에 쉰여섯 명의 대표가 모였습니다. 160년 전 선조들이 실패한 바로 그 자리입니다. "
      "조지 워싱턴이 대륙군 총사령관으로 지명되었고, 이제 남은 일은 이기는 것뿐입니다.",
      pp(50), war(0.05), cost=3)
focus(T, C + "reorganise_army", "army_doctrines", 12, 1, "대륙군 재편",
      "대륙군은 퇴역 장교와 농부, 공장 노동자가 뒤섞인 군대입니다. 워싱턴은 플랑드르에서 배운 대로 이들을 연대와 사단으로 묶습니다. "
      "교범은 영국군의 것을 번역해 씁니다. 장교들도 이 점이 조금 우습다는 것을 압니다.",
      xp("army", 25), pre=[C + "second_congress"], cost=5)
focus(T, C + "supply_lines", "construct_mil_factory", 10, 2, "보급선 확보",
      "대륙군의 탄약은 사흘 치뿐입니다. 피츠버그와 볼티모어의 공장을 전시 생산으로 돌리고, 펜실베이니아 철도를 군이 접수합니다. "
      "철도원 노조는 임금을 두 배로 달라고 했고, 대륙 회의는 들어주었습니다.",
      mil(2), pre=[C + "reorganise_army"], cost=5)
focus(T, C + "minutemen", "allies_build_infantry", 14, 2, "민병대 동원",
      "버지니아와 매사추세츠의 마을마다 민병대가 다시 꾸려집니다. 1775년 렉싱턴의 민병대처럼 일 분이면 싸울 준비가 된다고들 자랑합니다. "
      "신발이 모자라 실제로는 십 분쯤 걸립니다.",
      manpower(60000), rifles(15000), pre=[C + "reorganise_army"], cost=5)
focus(T, C + "hold_philadelphia", "fortify_city", 12, 3, "필라델피아 사수",
      "총독부군이 델라웨어 강을 건너 필라델피아로 다가옵니다. 대륙 회의를 볼티모어로 옮기자는 의원도 있었지만 워싱턴은 거절했습니다. "
      "수도가 떠나면 혁명도 떠난다는 것이 그의 대답이었습니다.",
      timed("LR_usa_hold_philadelphia", 180), war(0.05), pre=[C + "supply_lines", C + "minutemen"], cost=5)
focus(T, C + "letter_to_paris", "improve_relations", 10, 4, "파리에 보내는 서한",
      "벤저민 프랭클린이 1778년 파리에서 해낸 일을 누군가 다시 해야 합니다. 대륙 회의는 프랑스에 무기와 차관을 청하는 서한을 보냅니다. "
      "파리가 지금 누구의 손에 있든, 영국의 적은 대륙 회의의 친구입니다.",
      "if = {\n\tlimit = { FRA = { exists = yes } }\n\tadd_equipment_to_stockpile = {\n\t\ttype = infantry_equipment\n\t\tamount = 6000\n\t\tproducer = FRA\n\t}\n}",
      pp(50), opinion("FRA"), pre=[C + "hold_philadelphia"], cost=5)
focus(T, C + "march_north", "position_armies", 14, 4, "북부 진격",
      "뉴욕은 총독부의 머리입니다. 허드슨 강 계곡을 따라 올라가 총독 관저를 쳐야 전쟁이 끝납니다. "
      "워싱턴은 1776년 롱아일랜드에서 선조들이 당한 패배를 지도 위에 붉은 연필로 직접 표시해 두었습니다.",
      timed("LR_usa_march_north", 180), pre=[C + "hold_philadelphia"], available=FIGHTING_GOVERNOR, cost=5, ai=5)
focus(T, C + "overthrow", "territory_or_war", 12, 5, "총독부 타도",
      "총독부는 무너지고 있습니다. 남은 것은 뉴욕 항구에 웅크린 수비대와 바다 건너의 본국뿐입니다. "
      "대륙군은 마지막 공세를 준비합니다. 이 싸움에서 이기면, 그다음 상대는 영국 그 자체입니다.",
      war(0.1), xp("army", 25), pre=[C + "letter_to_paris", C + "march_north"], cost=5, ai=5)

INDEPENDENT = "LR_usa_independent"
focus(T, C + "morning", "national_unity", 12, 6, "독립의 아침",
      "총독 관저의 깃대에서 유니언잭이 내려왔습니다. 대륙 회의는 열세 식민지와 서부 영토를 아우르는 미합중국의 수립을 선포했습니다. "
      "이제 공화국은 총이 아니라 법으로 스스로를 지켜야 합니다.",
      "remove_ideas = LR_CNA_continental_army", idea("LR_usa_young_republic"), stab(0.1), event("lr_usa.42", 30), branch=INDEPENDENT)
focus(T, C + "convention", "political_pressure", 12, 7, "헌법 제정 회의",
      "각 주의 대표 쉰다섯 명이 필라델피아에 모였습니다. 대통령에게 얼마만큼의 권한을 줄지, 주와 연방이 무엇을 나눠 가질지를 두고 넉 달을 싸웠습니다. "
      "워싱턴은 의장석에서 거의 말하지 않았습니다.",
      pp(100), event("lr_usa.23"), pre=[C + "morning"], branch=INDEPENDENT)
focus(T, C + "bill_of_rights", "propaganda", 10, 8, "권리장전",
      "언론과 집회와 종교의 자유, 영장 없는 수색의 금지. 총독부 시절 사라졌던 권리들이 헌법 맨 뒤에 열 개의 조항으로 붙었습니다. "
      "일부 의원은 이것이 무정부주의자들에게 문을 열어 준다며 끝까지 반대했습니다.",
      idea("LR_usa_bill_of_rights"), pop("democratic", 0.1), pre=[C + "convention"], branch=INDEPENDENT)
focus(T, C + "federal_treasury", "positive_trade_relations", 14, 8, "연방 재무부",
      "전쟁 공채가 대륙 회의 예산의 네 배입니다. 재무장관은 연방은행을 세우고 관세로 빚을 갚자고 제안했습니다. "
      "영국 자본이 빠져나간 자리를 누가 채울지가 남은 문제입니다.",
      civ(2), pre=[C + "convention"], branch=INDEPENDENT)
focus(T, C + "secret_service", "intelligence_exchange", 16, 8, "비밀경호국",
      "총독부 정보국의 요원 일부가 아직 필라델피아 거리를 돌아다닙니다. 대통령을 노리는 이는 그들만이 아닙니다. "
      "재무부 아래 대통령 경호를 맡을 작은 기관을 둡니다. 처음 배치된 요원은 스물네 명입니다.",
      flag("LR_usa_secret_service"), tt("LR_tt_usa_secret_service"), pre=[C + "federal_treasury"], branch=INDEPENDENT, cost=5)
focus(T, C + "july_fourth", "propaganda", 12, 9, "첫 번째 독립기념일",
      "공화국의 첫 독립기념일입니다. 워싱턴은 독립기념관 앞 광장에서 연설합니다. 육만 명이 모일 것으로 보이고, 경찰은 그 절반도 통제할 수 없다고 보고했습니다. "
      "대통령은 연설을 취소하지 않았습니다.",
      event("lr_usa.25", 1), tt("LR_tt_usa_july_fourth"), pre=[C + "bill_of_rights", C + "federal_treasury"], branch=INDEPENDENT)

# Washington lives: the democratic United States
LIVES = "LR_usa_washington_lives"
focus(T, C + "after_shots", "national_unity", 6, 10, "총성 이후",
      "총알은 대통령의 왼쪽 어깨를 스쳤습니다. 워싱턴은 붕대를 감은 채 연설을 끝까지 마쳤고, 그날 광장에 있던 사람들은 그 장면을 평생 이야기할 것입니다. "
      "공화국은 첫 시험을 넘겼습니다.",
      stab(0.15), war(0.05), branch=LIVES)
focus(T, C + "election", "propaganda", 6, 11, "첫 번째 대통령 선거",
      "헌법에 따라 첫 대통령 선거가 치러집니다. 워싱턴은 출마하지 않겠다고 했다가 의원 이백 명의 연서를 받고 마음을 바꿨습니다. "
      "상대 후보는 없습니다. 투표용지에는 찬성과 반대 두 칸만 인쇄되었습니다.",
      pp(100), event("lr_usa.71"), pre=[C + "after_shots"], branch=LIVES)
focus(T, C + "western_rail", "construct_infrastructure", 4, 12, "대륙 횡단 철도",
      "미시시피 서쪽에는 아직 철도가 드뭅니다. 시카고에서 오리건까지 이어질 새 철도는 서부 개척민의 꿈이자 병참 장교의 꿈입니다. "
      "연방 정부가 직접 첫 삽을 뜹니다.",
      civ(2), infra(1), pre=[C + "election"], branch=LIVES)
focus(T, C + "continental_navy", "build_navy", 8, 12, "대륙 해군",
      "독립 전쟁 동안 대륙 회의는 군함 한 척 없이 싸웠고, 영국 함대가 해안을 막는 동안 할 수 있는 일이 없었습니다. "
      "노퍽과 필라델피아 조선소에서 공화국의 첫 순양함들이 진수됩니다.",
      dock(2), xp("navy", 25), pre=[C + "election"], branch=LIVES)
focus(T, C + "monroe", "neutrality_focus", 6, 13, "먼로 선언",
      "유럽의 왕들은 더 이상 아메리카 대륙에 새 식민지를 만들 수 없습니다. 이미 있는 식민지에 대해서도 공화국은 침묵하지 않을 것입니다. "
      "마드리드와 런던은 이 선언을 무시했고, 남미의 혁명가들은 이 선언을 외웠습니다.",
      idea("LR_usa_monroe"), pre=[C + "western_rail", C + "continental_navy"], branch=LIVES)
focus(T, C + "manifest_destiny", "demand_territory", 5, 14, "명백한 운명",
      "텍사스와 뉴멕시코, 캘리포니아. 공화국의 서쪽 땅은 여전히 스페인 부왕의 것입니다. 신문들은 대륙을 바다에서 바다까지 채우는 것이 미국인의 운명이라고 씁니다. "
      "의회는 그 기사들을 결의안으로 바꿨습니다.",
      flag("LR_usa_annex_americas"), tt("LR_tt_usa_annex_americas"), claim_states(NEW_SPAIN_NORTH), war(0.1), pre=[C + "monroe"], branch=LIVES)
focus(T, C + "rio_grande", "occupy_start_war", 5, 15, "리오그란데 전쟁",
      "부왕군이 리오그란데 북쪽에 요새를 쌓는다는 보고가 들어왔습니다. 의회는 선전포고를 두고 사흘 동안 토론했고, 스물두 표 차이로 통과시켰습니다. "
      "대륙군 출신 장교들은 이번에는 공격하는 쪽이라는 것이 낯섭니다.",
      war_on("MEX"), pre=[C + "manifest_destiny"], branch=LIVES, available=NO_WAR, ai=5)
focus(T, C + "promise_1778", "major_alliance", 7, 14, "1778년의 약속",
      "1778년 프랑스 왕은 반란을 일으킨 식민지와 동맹을 맺었습니다. 그 조약은 혁명이 실패하면서 휴지가 되었습니다. "
      "160년 뒤, 공화국은 그 조약문을 다시 꺼내 자유를 지키려는 나라들과 새 동맹을 맺습니다.",
      "if = {\n\tlimit = { is_in_faction = no }\n\tcreate_faction = LR_fac_usa_liberty\n}",
      opinion("FRA", "large_increase"), "if = {\n\tlimit = {\n\t\tFRA = {\n\t\t\texists = yes\n\t\t\tis_in_faction = no\n\t\t\tOR = {\n\t\t\t\thas_government = democratic\n\t\t\t\thas_government = communism\n\t\t\t}\n\t\t\tNOT = { has_war_with = ROOT }\n\t\t}\n\t}\n\tadd_to_faction = FRA\n}",
      tt("LR_tt_usa_promise_1778"), pre=[C + "monroe"], branch=LIVES)
focus(T, C + "arsenal", "construct_mil_factory", 6, 16, "민주주의의 무기고",
      "공화국의 공장들은 유럽의 어느 나라보다 많은 강철을 만듭니다. 대통령은 이 강철을 왕들의 전쟁이 아니라 자유를 위한 전쟁에 쓰겠다고 말했습니다. "
      "디트로이트의 조립 라인에서 전차가 나오기 시작합니다.",
      mil(3), tech(C + "arsenal", "industry"), pre=[(C + "rio_grande", C + "promise_1778")], branch=LIVES)
focus(T, C + "northern_brothers", "occupy_start_war", 6, 17, "북쪽의 형제들",
      "캐나다는 아직 영국 귀족 공화국의 자치령입니다. 몬트리올과 토론토에는 공화국을 동경하는 젊은이가 많습니다. "
      "공화국은 그들의 해방을 내걸고 국경을 넘습니다. 이번에는 1812년처럼 끝나지 않을 것입니다.",
      war_on("CAN"), pre=[C + "arsenal"], branch=LIVES, available=NO_WAR, ai=3)
focus(T, C + "continent_of_liberty", "national_unity", 6, 18, "자유의 대륙",
      "북극해에서 리오그란데까지, 대륙의 대부분이 한 공화국의 헌법 아래 있습니다. 워싱턴은 두 번째 임기를 마치면 버지니아로 돌아가겠다고 말합니다. "
      "공화국이 한 사람에게 기대지 않아도 되는 날이 오기를, 그는 누구보다 바랍니다.",
      idea("LR_usa_liberty_continent"), stab(0.1), "news_event = { id = lr_usa.72 days = 1 }", pre=[C + "northern_brothers"], branch=LIVES)

# Washington dies: the crisis
CRISIS = "LR_usa_crisis"
focus(T, C + "acting_president", "political_pressure", 16, 10, "임시 대통령 헐",
      "부통령 코델 헐이 병원 복도에서 취임 선서를 했습니다. 테네시의 변호사 출신인 그는 관세와 조약에는 밝지만 성난 군중을 다뤄 본 적은 없습니다. "
      "거리에서는 누가 대통령을 죽였는지를 두고 벌써 세 가지 소문이 돕니다.",
      stab(0.05), pp(50), branch=CRISIS, cost=5)
focus(T, C + "martial_law", "fortify_city", 15, 11, "계엄령",
      "필라델피아와 뉴욕, 시카고에 계엄령을 선포합니다. 집회는 금지되고 야간 통행에는 군의 허가가 필요합니다. "
      "헐은 서명하기 전에 한참 손을 떨었습니다. 집행은 대륙군 사령관 맥아더 장군이 맡습니다.",
      idea("LR_usa_martial_law"), flag("LR_usa_army_grip"), pre=[C + "acting_president"], me=[C + "dialogue"], branch=CRISIS, cost=5)
focus(T, C + "dialogue", "improve_relations", 17, 11, "시위대와의 대화",
      "헐은 파업 지도부와 퇴역 군인 대표를 독립기념관으로 불렀습니다. 그들의 요구는 열네 가지였고, 그중 아홉 가지는 들어줄 수 있는 것이었습니다. "
      "군은 이 회담을 굴복이라고 부릅니다.",
      stab(0.1), pop("communism", 0.05), "remove_ideas = LR_usa_burning_streets", pre=[C + "acting_president"], me=[C + "martial_law"],
      branch=CRISIS, cost=5)
focus(T, C + "emergency_currency", "trade", 16, 12, "긴급 통화 조치",
      "영국의 금수 조치로 파운드 결제가 막혔습니다. 재무부는 금 태환을 중단하고 새 지폐를 찍습니다. "
      "공장 노동자의 주급은 두 주 만에 반값이 되었습니다. 헐은 석 달만 버티면 된다고 말합니다.",
      "if = {\n\tlimit = { has_idea = LR_usa_british_embargo }\n\tswap_ideas = {\n\t\tremove_idea = LR_usa_british_embargo\n\t\tadd_idea = LR_usa_embargo_eased\n\t}\n}",
      tt("LR_tt_usa_emergency_currency"), pre=[(C + "martial_law", C + "dialogue")], branch=CRISIS, cost=5)
focus(T, C + "lean_on_army", "army_doctrines", 16, 13, "군에 기대다",
      "질서를 되찾을 수 있는 조직은 군뿐이라는 보고서가 헐의 책상에 올라왔습니다. 작성자는 맥아더 장군입니다. "
      "헐은 보고서를 읽고, 다시 읽고, 서랍에 넣었습니다. 사흘 뒤 그는 서랍을 다시 열었습니다.",
      "set_country_flag = LR_usa_coup_called", event("lr_usa.31", 3), tt("LR_tt_usa_lean_on_army"),
      pre=[C + "emergency_currency"], branch=CRISIS, cost=5)

# MacArthur's war
CIVIL = "LR_usa_civil_war_on"
focus(T, C + "junta", "political_pressure", 16, 14, "국가 재건 위원회",
      "맥아더 장군은 대통령 직무 대행이 아니라 국가 재건 위원회 의장이라는 직함을 택했습니다. 헌법은 정지되지 않았다고 그는 말합니다. "
      "잠시 서랍 속에 들어갔을 뿐이라고.",
      pp(100), war(0.1), branch=CIVIL, cost=5)
focus(T, C + "west_point", "army_doctrines", 15, 15, "웨스트포인트의 장교들",
      "대륙군 장교의 절반이 맥아더를 따랐고, 나머지 절반은 고향 주의 깃발을 택했습니다. "
      "남은 장교들을 다시 하나로 묶으려면 진급과 훈장, 그리고 무엇보다 승리가 필요합니다.",
      xp("army", 50), tech(C + "west_point", "land_doctrine"), pre=[C + "junta"], branch=CIVIL, cost=5)
focus(T, C + "appalachian_front", "position_armies", 17, 15, "애팔래치아 전선",
      "펜실베이니아와 버지니아에는 공화국의 공업과 정통성이 몰려 있습니다. 북쪽의 평의회군, 서쪽의 롱, 남쪽의 남부 연합이 모두 이곳을 노립니다. "
      "애팔래치아 산맥이 첫 방벽입니다.",
      timed("LR_usa_appalachian_front", 180), pre=[C + "junta"], branch=CIVIL, cost=5)
focus(T, C + "final_offensive", "attack_allies", 16, 16, "최후의 공세",
      "탄약은 석 달 치, 병력은 여섯 달 치가 남았습니다. 맥아더는 기다리면 진다고 판단했습니다. 모든 전선에서 동시에 공세를 시작합니다. "
      "성공하면 내전이 끝나고, 실패하면 맥아더가 끝납니다.",
      timed("LR_usa_final_offensive", 120), hurt(["AMC", "LNG", "DXE"], -0.05), pre=[C + "west_point", C + "appalachian_front"], branch=CIVIL, cost=5, ai=5)

# The Amerigo Empire
EMPIRE = "LR_route_amerigo_empire"
focus(T, C + "generalissimo", "national_unity", 16, 17, "대원수",
      "내전은 끝났습니다. 의회는 맥아더에게 공화국 대원수라는 칭호를 바쳤습니다. 그는 칭호를 받고, 다음 날 의회를 해산했습니다. "
      "필라델피아의 신문들은 이 소식을 3면에 실었습니다.",
      stab(0.1), pp(100), branch=EMPIRE)
focus(T, C + "crowned_general", "political_pressure", 16, 18, "왕관을 쓴 장군",
      "신대륙에 처음 이름을 준 사람, 아메리고 베스푸치의 이름을 딴 새 나라가 선포됩니다. 대관식은 필라델피아 독립기념관에서 열립니다. "
      "워싱턴이 마지막 연설을 했던 바로 그 광장입니다.",
      event("lr_usa.81"), pre=[C + "generalissimo"], branch=EMPIRE)
focus(T, C + "peerage", "improve_relations", 15, 19, "제국 귀족원",
      "황제는 내전에서 공을 세운 장군 마흔 명과 그들을 도운 실업가 스무 명에게 작위를 내렸습니다. "
      "귀족원은 황제의 법안을 한 번도 거부하지 않았고, 앞으로도 그럴 생각이 없습니다.",
      idea("LR_usa_peerage"), pre=[C + "crowned_general"], branch=EMPIRE)
focus(T, C + "imperial_army", "army_tanks", 17, 19, "제국 육군",
      "대륙군이라는 이름은 사라지고 아메리고 제국 육군이 남았습니다. 황제는 필리핀에서 배운 기동전과 플랑드르에서 배운 포병전을 섞은 새 교범을 직접 썼습니다. "
      "장교들은 그 교범을 외워야 진급합니다.",
      idea("LR_usa_imperial_army"), tech(C + "imperial_army", "armor"), pre=[C + "crowned_general"], branch=EMPIRE)
focus(T, C + "imperial_roads", "construct_infrastructure", 16, 20, "황제의 도로",
      "내전으로 끊긴 철도와 다리를 다시 놓습니다. 새 도로는 모두 필라델피아에서 시작해 황제의 이름을 달고 뻗어 나갑니다. "
      "공사장에는 내전 포로 이십만 명이 투입되었습니다.",
      civ(3), infra(1), pre=[C + "peerage", C + "imperial_army"], branch=EMPIRE)
focus(T, C + "northern_campaign", "occupy_start_war", 15, 21, "북방 원정",
      "캐나다는 내전 동안 국경 너머로 영국군을 들여왔습니다. 황제는 이를 잊지 않았습니다. "
      "제국 육군이 세인트로렌스 강을 건넙니다. 황제는 오타와에서 겨울을 나겠다고 말했습니다.",
      war_on("CAN"), flag("LR_usa_annex_americas"), tt("LR_tt_usa_annex_americas"), pre=[C + "imperial_roads"], branch=EMPIRE,
      available=NO_WAR, ai=4)
focus(T, C + "canada_crown", "national_unity", 14, 22, "북방 왕령",
      "오타와 의사당에 제국의 깃발이 올랐습니다. 캐나다는 더 이상 영국의 자치령이 아니라 아메리고 제국의 북방 왕령입니다. "
      "황제는 퀘벡의 프랑스어 학교를 그대로 두겠다고 약속했고, 토론토의 은행가들에게는 제국 귀족원의 의석을 내밀었습니다.",
      "every_owned_state = {\n\tlimit = {\n\t\tis_on_continent = north_america\n\t\tNOT = { is_core_of = ROOT }\n\t}\n\tadd_core_of = ROOT\n}",
      stab(0.05), tt("LR_tt_usa_cores_north"), pre=[C + "northern_campaign"], branch=EMPIRE,
      available="custom_trigger_tooltip = {\n\ttooltip = LR_tt_usa_canada_gone\n\tNOT = { CAN = { exists = yes } }\n}")
focus(T, C + "pacific_emperor", "build_navy", 17, 21, "태평양의 황제",
      "황제는 젊은 시절 필리핀에서 근무하며 태평양을 보았습니다. 하와이 왕국과 스페인령 필리핀은 그 바다의 디딤돌입니다. "
      "제국 해군의 새 전함들이 샌프란시스코 대신 시애틀에서 서쪽으로 출항합니다.",
      dock(3), xp("navy", 50), claim_tag("HAW"), pre=[C + "imperial_roads"], branch=EMPIRE)
focus(T, C + "old_grudge", "major_war", 16, 22, "묵은 원한",
      "160년 전 영국은 식민지를 짓밟았고, 몇 해 전에는 내전에 끼어들 궁리를 했습니다. "
      "황제는 대서양 건너의 귀족 의회와 자신의 왕관 가운데 하나만 남아야 한다고 믿습니다. 장군들은 반대하지 않았습니다.",
      war_on("ENG"), pre=[C + "northern_campaign", C + "pacific_emperor"], branch=EMPIRE, available=NO_WAR, ai=2)
focus(T, C + "amerigo_millennium", "national_unity", 16, 23, "아메리고 천년",
      "제국은 신대륙의 주인이 되었습니다. 황제는 일흔을 바라보고 있고, 후계자는 아직 정하지 않았습니다. "
      "궁정에서는 벌써 원수 세 명이 서로를 견제하고 있습니다.",
      idea("LR_usa_amerigo_millennium"), stab(0.1), "news_event = { id = lr_usa.82 days = 1 }", event("lr_usa.85", 200), pre=[(C + "old_grudge", C + "canada_crown")], branch=EMPIRE)

# ============================================================================================================
# The civil war factions
# ============================================================================================================
OTHERS = {"AMC": ["CNA", "LNG", "DXE"], "LNG": ["CNA", "AMC", "DXE"], "DXE": ["CNA", "AMC", "LNG"]}

T = "lr_amc_focus"
A = "LR_AMC_"
focus(T, A + "council", "national_unity", 6, 0, "미주 노동자 평의회",
      "시카고 노동회관에 북부 여덟 개 주의 평의회 대표 사백 명이 모였습니다. 그들은 대륙 회의도, 맥아더의 군정도 인정하지 않는다고 선언했습니다. "
      "의장은 캔자스 출신의 얼 브라우더입니다.",
      pp(50), war(0.05), cost=3)
focus(T, A + "red_guards", "allies_build_infantry", 5, 1, "붉은 근위대",
      "디트로이트 자동차 공장의 노동자 삼만 명이 공장 경비대를 근위대로 바꿨습니다. "
      "그들의 무기는 총독부 시절 숨겨 둔 스프링필드 소총과 공장에서 갓 나온 트럭입니다.",
      manpower(80000), rifles(20000), pre=[A + "council"], cost=5)
focus(T, A + "detroit_arsenal", "construct_mil_factory", 7, 1, "디트로이트 병기창",
      "포드와 제너럴 모터스의 조립 라인이 노동자 위원회의 손에 넘어갔습니다. 공장장들은 쫓겨나지 않고 기술 고문이 되었습니다. "
      "그들 가운데 몇은 이쪽이 회사보다 낫다고 몰래 말합니다.",
      mil(3), pre=[A + "council"], cost=5)
focus(T, A + "general_strike", "propaganda", 6, 2, "총파업 호소",
      "평의회는 남부와 서부의 노동자들에게 총파업을 호소합니다. 롱의 지지자 가운데 상당수가 철도원과 광부입니다. "
      "그들이 기차를 멈추면 롱의 군대도 멈춥니다.",
      hurt(OTHERS["AMC"], -0.08), pre=[A + "red_guards", A + "detroit_arsenal"], cost=5)
focus(T, A + "march_south", "attack_allies", 6, 3, "남쪽으로",
      "평의회군이 오하이오 강을 건넙니다. 첫 목표는 피츠버그의 제철소, 그다음은 필라델피아입니다. "
      "1937년에 독립을 선언한 그 도시에서, 이번에는 혁명을 선언할 것입니다.",
      timed("LR_usa_red_offensive", 180), pre=[A + "general_strike"], cost=5, ai=5)
AMC_ROUTE = "LR_route_amc_union"
focus(T, A + "union", "national_unity", 6, 4, "연방 선포",
      "필라델피아 독립기념관에 붉은 깃발이 올랐습니다. 대표자 대회는 각 주를 사회주의 공화국으로 다시 세우고 이들을 하나의 연방으로 묶기로 했습니다. "
      "러시아 공화국 이후 두 번째로 살아남은 혁명입니다.",
      stab(0.1), idea("LR_usa_soviet_power"), branch=AMC_ROUTE)
focus(T, A + "federal_treaty", "political_pressure", 5, 5, "연방 조약",
      "뉴욕, 일리노이, 버지니아. 조약은 각 사회주의 공화국이 탈퇴할 권리를 가진다고 씁니다. "
      "중앙위원회는 그 권리를 쓰려는 공화국은 없을 것이라고 확신합니다.",
      pp(100), stab(0.05), pre=[A + "union"], branch=AMC_ROUTE)
focus(T, A + "five_year_plan", "production", 7, 5, "제1차 5개년 계획",
      "내전으로 무너진 공업을 다시 세웁니다. 계획 위원회는 강철 생산을 다섯 해 안에 세 배로 늘리겠다고 약속했습니다. "
      "숫자는 대담하고, 계획 위원들은 요즘 잠을 자지 않습니다.",
      idea("LR_usa_five_year_plan"), civ(2), pre=[A + "union"], branch=AMC_ROUTE)
focus(T, A + "red_army", "army_doctrines", 5, 6, "미주 적군",
      "평의회군과 붉은 근위대를 하나의 정규군으로 묶습니다. 장교는 노동자 출신이어야 한다는 원칙과, 장교는 싸울 줄 알아야 한다는 원칙이 부딪쳤습니다. "
      "결국 정치위원이 둘을 이어 붙였습니다.",
      xp("army", 50), tech(A + "red_army", "land_doctrine"), pre=[A + "federal_treaty"], branch=AMC_ROUTE)
focus(T, A + "electrification", "construct_civilian", 7, 6, "전국 전력화",
      "테네시 강에 댐 열두 개를 짓습니다. 남부의 농가에 처음으로 전등이 켜집니다. "
      "남부 연합을 지지하던 농민들도 전등 아래에서는 조금 덜 투덜댑니다.",
      civ(2), "add_research_slot = 1", pre=[A + "five_year_plan"], branch=AMC_ROUTE)
focus(T, A + "russian_brothers", "major_alliance", 6, 7, "러시아의 형제들",
      "러시아 공화국은 세계에서 유일하게 혁명을 지켜 낸 나라였습니다. 이제 그 나라는 외롭지 않습니다. "
      "대서양과 태평양을 사이에 둔 두 혁명이 손을 잡습니다.",
      "if = {\n\tlimit = { is_in_faction = no }\n\tcreate_faction = LR_fac_usa_revolution\n}",
      "if = {\n\tlimit = {\n\t\tSOV = {\n\t\t\texists = yes\n\t\t\tis_in_faction = no\n\t\t\tNOT = { has_war_with = ROOT }\n\t\t}\n\t}\n\tadd_to_faction = SOV\n}",
      opinion("SOV", "large_increase"), tt("LR_tt_usa_russian_brothers"), pre=[A + "red_army", A + "electrification"], branch=AMC_ROUTE)
AMERICAS = ["CAN", "MEX", "CUB", "GUA", "COL", "VEN", "PRU", "ARG", "CHL", "BRA"]
focus(T, A + "liberation", "propaganda", 6, 8, "미주 해방 선언",
      "중앙위원회는 북극해에서 티에라델푸에고까지, 아메리카 대륙의 모든 노동자를 해방하겠다고 선언했습니다. "
      "왕과 부왕과 총독이 다스리는 땅은 모두 연방의 일원이 될 것입니다. 선언문은 영어와 스페인어, 포르투갈어, 프랑스어로 동시에 인쇄되었습니다.",
      flag("LR_usa_annex_americas"), tt("LR_tt_usa_annex_americas"), claim_tag(*AMERICAS), war(0.1),
      pre=[A + "russian_brothers"], branch=AMC_ROUTE)
focus(T, A + "northern_revolution", "occupy_start_war", 4, 9, "북방 혁명",
      "퀘벡과 온타리오의 노동자들이 국경 너머를 바라보고 있습니다. 평의회는 그들에게 해방을 약속합니다. "
      "영국 귀족 공화국의 자치령은 미주 혁명의 첫 수출품을 받게 될 것입니다.",
      war_on("CAN"), pre=[A + "liberation"], branch=AMC_ROUTE, available=NO_WAR, ai=4)
focus(T, A + "southern_revolution", "occupy_start_war", 6, 9, "남방 혁명",
      "누에바 에스파냐의 광부와 농민은 크리올로 귀족의 땅에서 일합니다. 그들에게 필요한 것은 총과 깃발입니다. "
      "미주 적군이 리오그란데를 건넙니다.",
      war_on("MEX"), pre=[A + "liberation"], branch=AMC_ROUTE, available=NO_WAR, ai=4)
focus(T, A + "caribbean_revolution", "occupy_states_coastal", 8, 9, "카리브의 붉은 바다",
      "아바나와 과테말라시티의 사탕수수 농장에서는 아직 스페인 귀족이 채찍을 듭니다. "
      "미주 적군의 상륙함대가 노퍽에서 출항합니다. 쿠바의 담배 노동자 조합은 이미 무기를 숨겨 두었습니다.",
      war_on("CUB", "GUA"), pre=[A + "liberation"], branch=AMC_ROUTE, available=NO_WAR, ai=4)
focus(T, A + "andes_revolution", "occupy_states_ongoing_war", 5, 10, "안데스의 광부들",
      "볼리비아의 주석 광산과 페루의 은 광산, 베네수엘라의 유전에서 일하는 사람들은 하루 열네 시간을 일하고 빚만 늘어갑니다. "
      "미주 적군이 파나마 지협을 넘어 남쪽으로 내려갑니다.",
      war_on("COL", "VEN", "PRU"), pre=[(A + "southern_revolution", A + "caribbean_revolution")], branch=AMC_ROUTE, available=NO_WAR, ai=4)
focus(T, A + "southern_star", "territory_or_war", 7, 10, "남십자성 아래의 혁명",
      "리오데라플라타의 팜파스와 칠레의 구리 광산, 브라질의 커피 농장. 신대륙 남쪽의 왕국과 부왕령이 마지막 목표입니다. "
      "부에노스아이레스의 부두 노동자들은 북쪽에서 오는 배를 기다리고 있습니다.",
      war_on("ARG", "CHL", "BRA"), pre=[A + "andes_revolution"], branch=AMC_ROUTE, available=NO_WAR, ai=4)
focus(T, A + "union_of_americas", "national_unity", 6, 11, "아메리카 연방 편입",
      "해방된 땅마다 노동자 평의회가 세워졌습니다. 대표자 대회는 그 평의회들을 연방의 사회주의 공화국으로 받아들이기로 했습니다. "
      "멕시코시티와 아바나, 리마의 대표들이 필라델피아에 도착합니다.",
      "every_owned_state = {\n\tlimit = {\n\t\tOR = {\n\t\t\tis_on_continent = north_america\n\t\t\tis_on_continent = south_america\n\t\t}\n\t\tNOT = { is_core_of = ROOT }\n\t}\n\tadd_core_of = ROOT\n}",
      stab(0.05), tt("LR_tt_usa_cores_americas"), pre=[(A + "northern_revolution", A + "southern_star")], branch=AMC_ROUTE)
focus(T, A + "second_capital", "national_unity", 6, 12, "혁명의 두 번째 수도",
      "필라델피아에서 페트로그라드까지, 혁명은 이제 두 대륙의 일입니다. 런던과 파리의 왕들은 밤마다 같은 악몽을 꿉니다. "
      "중앙위원회는 다음 대회를 아바나에서 열자는 안건을 검토하고 있습니다.",
      idea("LR_usa_world_revolution"), stab(0.05), "news_event = { id = lr_usa.92 days = 1 }",
      pre=[A + "union_of_americas"], branch=AMC_ROUTE)

T = "lr_lng_focus"
L = "LR_LNG_"
focus(T, L + "every_man", "national_unity", 6, 0, "모든 사람이 왕이다",
      "캔자스시티의 방송국에서 휴이 롱이 연설합니다. 은행가와 장군과 빨갱이를 모두 쓸어버리고, 모든 미국인에게 집 한 채와 자동차 한 대를 주겠다고. "
      "평원의 농민 수백만 명이 라디오 앞에서 고개를 끄덕였습니다.",
      pp(50), stab(0.05), cost=3)
focus(T, L + "share_clubs", "propaganda", 5, 1, "부의 공유 클럽",
      "롱의 지지자 모임인 부의 공유 클럽은 회원이 칠백만 명이라고 주장합니다. "
      "클럽마다 무기고가 하나씩 딸려 있다는 사실은 덜 알려져 있습니다.",
      manpower(70000), rifles(15000), pre=[L + "every_man"], cost=5)
focus(T, L + "prairie_army", "army_motorized", 7, 1, "평원의 군대",
      "평원의 농부들은 트랙터를 몰 줄 압니다. 트랙터를 모는 사람은 트럭도, 전차도 몰 수 있다고 롱은 말합니다. "
      "오클라호마의 정유소가 이 군대에 기름을 댑니다.",
      tech(L + "prairie_army", "motorized_equipment"), xp("army", 25), pre=[L + "every_man"], cost=5)
focus(T, L + "radio_war", "propaganda", 6, 2, "라디오 전쟁",
      "롱의 목소리는 전선보다 먼저 도착합니다. 매일 밤 아홉 시, 적 진영의 병사들도 그의 방송을 몰래 듣습니다. "
      "다음 날 아침이면 탈영병이 늘어나 있습니다.",
      hurt(OTHERS["LNG"], -0.08), pre=[L + "share_clubs", L + "prairie_army"], cost=5)
focus(T, L + "mississippi", "attack_allies", 6, 3, "미시시피 장악",
      "미시시피 강을 쥐는 쪽이 대륙의 심장을 쥡니다. 롱의 군대가 세인트루이스에서 뉴올리언스까지 강을 따라 내려갑니다. "
      "롱은 루이지애나의 고향 집에 돌아가겠다고 약속했습니다.",
      timed("LR_usa_prairie_offensive", 180), pre=[L + "radio_war"], cost=5, ai=5)
LNG_ROUTE = "LR_route_lng_usa"
focus(T, L + "restored_usa", "national_unity", 6, 4, "미합중국 재건",
      "내전에서 이긴 휴이 롱은 공화국의 옛 이름을 되살렸습니다. 미합중국. 그는 이 이름이 워싱턴의 것이 아니라 평범한 미국인 모두의 것이라고 말합니다. "
      "헌법은 아직 손대지 않았습니다.",
      stab(0.1), pp(100), branch=LNG_ROUTE)
focus(T, L + "share_our_wealth", "consumer_goods", 5, 5, "부의 공유법",
      "연 소득 백만 달러를 넘는 부분은 모두 세금으로 걷고, 모든 가구에 오천 달러의 정착금을 줍니다. "
      "경제학자들은 계산이 맞지 않는다고 하고, 롱은 경제학자들도 정착금을 받을 수 있다고 대답합니다.",
      idea("LR_usa_share_our_wealth"), pre=[L + "restored_usa"], branch=LNG_ROUTE)
focus(T, L + "highways", "construct_infrastructure", 7, 5, "국민 고속도로",
      "모든 미국인에게 자동차를 주겠다는 약속에는 도로가 필요합니다. 연방 고속도로청은 대륙을 가로세로로 잇는 사만 마일의 도로 계획을 발표했습니다. "
      "실업자 이백만 명이 삽을 들었습니다.",
      idea("LR_usa_highways"), infra(1), civ(1), pre=[L + "restored_usa"], branch=LNG_ROUTE)
focus(T, L + "national_radio", "propaganda", 5, 6, "전국 방송망",
      "모든 마을 회관에 라디오 한 대씩을 보냅니다. 대통령의 연설은 매주 일요일 저녁에 나가고, 다른 방송국은 그 시간에 음악만 틀어야 합니다. "
      "가장 인기 있는 곡은 롱이 직접 작사한 노래입니다.",
      pp(100), pop("fascism", 0.1), pre=[L + "share_our_wealth"], branch=LNG_ROUTE)
focus(T, L + "presidential_congress", "political_pressure", 7, 6, "대통령의 의회",
      "의회는 비상시 법률을 제정할 권한을 대통령에게 넘기는 법안을 통과시켰습니다. 반대한 의원 열여섯 명 가운데 열 명은 다음 선거에서 떨어졌습니다. "
      "나머지 여섯 명은 출마하지 않았습니다.",
      stab(0.05), pp(50), mil(2), pre=[L + "highways"], branch=LNG_ROUTE)
focus(T, L + "kingfish_police", "intelligence_exchange", 6, 7, "킹피시의 경찰",
      "루이지애나 주 경찰을 본뜬 연방 치안국이 생겼습니다. 그들의 관심사는 은행가들의 장부와 신문사의 편집회의입니다. "
      "롱은 이들이 부자들만 감시한다고 말합니다.",
      stab(0.1), pre=[L + "national_radio", L + "presidential_congress"], branch=LNG_ROUTE)
focus(T, L + "american_market", "trade", 5, 8, "아메리카 경제권",
      "누에바 에스파냐와 카리브의 공국들은 미국 상품 없이는 버티지 못합니다. 롱은 그들에게 무역 협정과 차관을 내밀었습니다. "
      "조건은 하나, 미국의 친구가 되는 것입니다.",
      civ(2), opinion("CUB"), opinion("GUA"), pre=[L + "kingfish_police"], branch=LNG_ROUTE)
focus(T, L + "highway_south", "occupy_start_war", 7, 8, "남쪽으로 뻗는 고속도로",
      "멕시코시티의 부왕은 롱의 협정을 거절했습니다. 고속도로 공병대보다 군대가 먼저 리오그란데를 건넙니다. "
      "롱은 이 전쟁이 부왕과 크리올로 귀족만을 겨냥한다고 방송합니다.",
      flag("LR_usa_annex_americas"), tt("LR_tt_usa_annex_americas"), war_on("MEX"), pre=[L + "kingfish_police"], branch=LNG_ROUTE, available=NO_WAR, ai=4)
focus(T, L + "caribbean_highway", "occupy_states_coastal", 8, 9, "카리브 고속도로",
      "쿠바와 과테말라의 공국들은 롱의 무역 협정을 받아들였다가, 부왕이 무너지자 곧바로 영국 상선을 다시 불러들였습니다. "
      "롱은 플로리다 키웨스트에서 아바나까지 다리를 놓겠다고 방송했습니다. 다리보다 상륙함이 먼저 갑니다.",
      war_on("CUB", "GUA"), pre=[L + "highway_south"], branch=LNG_ROUTE, available=NO_WAR, ai=4)
focus(T, L + "kings_nation", "national_unity", 6, 9, "모든 사람이 왕인 나라",
      "가난한 집 아들이 대통령이 된 나라, 모든 가정에 자동차가 있는 나라. 롱은 약속을 지켰다고 말합니다. "
      "반대한 사람들이 그 약속의 값을 어떻게 치렀는지는 일요일 방송에 나오지 않습니다.",
      idea("LR_usa_kings_nation"), stab(0.05), "news_event = { id = lr_usa.93 days = 1 }",
      pre=[(L + "american_market", L + "highway_south")], branch=LNG_ROUTE)

T = "lr_dxe_focus"
D = "LR_DXE_"
focus(T, D + "confederacy", "national_unity", 6, 0, "남부 연합 선언",
      "애틀랜타의 조지아 주 의사당에서 남부 여섯 개 주의 대표가 연방 탈퇴를 선언했습니다. 의장은 미시시피의 시어도어 빌보입니다. "
      "그들은 각 주의 권리가 필라델피아의 어떤 군인보다도 앞선다고 선언했습니다.",
      pp(50), war(0.05), cost=3)
focus(T, D + "grey_army", "allies_build_infantry", 5, 1, "회색 군대",
      "남부의 주 방위군이 회색 군복을 입었습니다. 장교는 대부분 농장주 가문의 아들이고, 병사는 대부분 소작농입니다. "
      "둘은 북부 사람을 싫어한다는 점에서만 같습니다.",
      manpower(70000), rifles(15000), xp("army", 15), pre=[D + "confederacy"], cost=5)
focus(T, D + "cotton_bonds", "trade", 7, 1, "면화 담보 공채",
      "남부 연합에게는 공장보다 면화가 많습니다. 리버풀과 맨체스터의 상인들은 면화를 담보로 돈을 빌려줄 준비가 되어 있습니다. "
      "런던은 이 거래를 막지 않았습니다.",
      pp(50), "if = {\n\tlimit = { ENG = { exists = yes } }\n\tadd_equipment_to_stockpile = {\n\t\ttype = infantry_equipment\n\t\tamount = 8000\n\t\tproducer = ENG\n\t}\n}",
      pre=[D + "confederacy"], cost=5)
focus(T, D + "defend_atlanta", "fortify_city", 6, 2, "애틀랜타 방어",
      "애틀랜타는 남부 철도의 교차점입니다. 이곳을 잃으면 남부 연합은 둘로 갈라집니다. "
      "빌보는 도시 둘레에 참호를 파라고 명령했고, 흑인 노동자 만 이천 명이 강제로 동원되었습니다.",
      timed("LR_usa_atlanta_line", 180), pre=[D + "grey_army", D + "cotton_bonds"], cost=5)
focus(T, D + "march_north", "attack_allies", 6, 3, "북진",
      "리치먼드는 남부의 오래된 도시이고, 지금은 맥아더의 땅입니다. 남부 연합군은 버지니아를 되찾아 남부의 모든 주를 하나로 묶으려 합니다. "
      "그다음은 메릴랜드, 그다음은 필라델피아입니다.",
      timed("LR_usa_grey_offensive", 180), hurt(OTHERS["DXE"], -0.05), pre=[D + "defend_atlanta"], cost=5, ai=5)
DXE_ROUTE = "LR_route_dxe_csa"
focus(T, D + "csa", "national_unity", 6, 4, "아메리고 연합국",
      "내전에서 살아남은 남부의 대표들이 새 나라의 이름을 정했습니다. 아메리고 연합국. 수도는 애틀랜타이고, 국기에는 별 열세 개가 대각선으로 놓였습니다. "
      "북부의 공장 도시들은 이제 남부의 점령지입니다.",
      stab(0.1), pp(100), branch=DXE_ROUTE)
focus(T, D + "constitution", "political_pressure", 5, 5, "연합 헌법",
      "연합 헌법은 각 주의 권리를 연방보다 앞에 둡니다. 투표권은 재산과 문해력 시험을 통과한 사람에게만 주어집니다. "
      "농장주들은 이 헌법이 질서를 지킨다고 말하고, 시험관은 모두 농장주가 임명합니다.",
      pp(100), stab(0.05), pre=[D + "csa"], branch=DXE_ROUTE)
focus(T, D + "king_cotton", "trade", 7, 5, "면화 왕",
      "남부의 부는 면화에서 나옵니다. 연합국 정부는 면화 수출을 국가가 관리해 가격을 끌어올립니다. "
      "맨체스터의 방적 공장들은 불평하면서도 값을 치릅니다.",
      idea("LR_usa_king_cotton"), pre=[D + "csa"], branch=DXE_ROUTE)
focus(T, D + "planter_senate", "improve_relations", 5, 6, "농장주 원로원",
      "원로원 의원은 각 주 의회가 뽑고, 각 주 의회는 땅을 가진 사람들이 뽑습니다. "
      "그러니 원로원은 땅의 목소리라고 빌보는 말합니다. 땅이 없는 사람들의 목소리에 대해서는 말하지 않았습니다.",
      stab(0.1), pre=[D + "constitution"], branch=DXE_ROUTE)
focus(T, D + "northern_factories", "construct_mil_factory", 7, 6, "북부 공장 접수",
      "피츠버그와 디트로이트의 공장들이 연합국의 전리품이 되었습니다. 북부 노동자들은 남부 출신 감독관 아래에서 일합니다. "
      "파업은 반역으로 다뤄집니다.",
      mil(3), pre=[D + "king_cotton"], branch=DXE_ROUTE)
focus(T, D + "golden_circle", "demand_territory", 6, 7, "황금의 원",
      "아바나를 중심으로 원을 그리면 쿠바와 멕시코, 중미, 카리브가 그 안에 들어옵니다. 1850년대 남부 농장주들이 꾸던 오래된 꿈입니다. "
      "연합국은 그 원 안의 모든 땅을 요구합니다.",
      flag("LR_usa_annex_americas"), tt("LR_tt_usa_annex_americas"), claim_tag("MEX", "CUB", "GUA"), idea("LR_usa_golden_circle"), pre=[D + "planter_senate", D + "northern_factories"], branch=DXE_ROUTE)
focus(T, D + "havana", "occupy_states_coastal", 5, 8, "아바나 원정",
      "쿠바 공국은 스페인 왕실의 마지막 카리브 보석입니다. 연합국 해군이 플로리다 키웨스트에서 출항합니다. "
      "아바나의 사탕수수 농장주들은 이미 연합국과 거래를 시작했습니다.",
      war_on("CUB", "GUA"), pre=[D + "golden_circle"], branch=DXE_ROUTE, available=NO_WAR, ai=4)
focus(T, D + "mexico", "occupy_start_war", 7, 8, "멕시코 원정",
      "누에바 에스파냐의 북부는 텍사스부터 캘리포니아까지 이어집니다. 농장주들은 그 땅에 면화를 심을 수 있다고 계산했습니다. "
      "회색 군대가 서쪽으로 진군합니다.",
      war_on("MEX"), pre=[D + "golden_circle"], branch=DXE_ROUTE, available=NO_WAR, ai=4)
focus(T, D + "british_compact", "military_deal", 6, 9, "영국과의 협약",
      "연합국을 가장 먼저 승인한 나라는 영국이었습니다. 연합국에는 면화가, 영국에는 해군이 있습니다. "
      "빌보는 런던과 상호방위조약을 맺습니다. 160년 전의 적이 지금의 친구가 되었습니다.",
      opinion("ENG", "large_increase"),
      "if = {\n\tlimit = {\n\t\tENG = {\n\t\t\texists = yes\n\t\t\tis_faction_leader = yes\n\t\t\tNOT = { has_war_with = ROOT }\n\t\t}\n\t\tis_in_faction = no\n\t}\n\tENG = { add_to_faction = ROOT }\n}",
      tt("LR_tt_usa_british_compact"), pre=[(D + "havana", D + "mexico")], branch=DXE_ROUTE)
focus(T, D + "caribbean_empire", "national_unity", 6, 10, "카리브 제국",
      "멕시코만은 이제 연합국의 호수입니다. 아바나와 베라크루스, 뉴올리언스의 항구가 같은 깃발 아래 있습니다. "
      "빌보는 다음 목표로 남미를 지목했습니다. 장군들은 아직 지도를 펴지 않았습니다.",
      idea("LR_usa_caribbean_empire"), stab(0.05), "news_event = { id = lr_usa.94 days = 1 }", pre=[D + "british_compact"], branch=DXE_ROUTE)
focus(T, D + "south_america", "occupy_start_war", 6, 11, "남미 원정",
      "빌보는 멕시코만 너머 누에바 그라나다와 베네수엘라의 땅을 지목했습니다. 커피와 석유, 그리고 값싼 일손이 있는 땅입니다. "
      "연합국 해군이 카리브해를 건너 카르타헤나 앞바다에 닻을 내립니다.",
      war_on("COL", "VEN", "PRU"), pre=[D + "caribbean_empire"], branch=DXE_ROUTE, available=NO_WAR, ai=3)

# ============================================================================================================
# Economy, army, navy and air: four branches beside each tree's story (america_development.py)
# ============================================================================================================
import sys as _sys  # noqa: E402
import america_development as _dev  # noqa: E402

for _tree, _prefix in (("lr_usa_focus", "LR_USA_"), ("lr_cna_focus", "LR_CNA_"), ("lr_amc_focus", "LR_AMC_"),
                       ("lr_lng_focus", "LR_LNG_"), ("lr_dxe_focus", "LR_DXE_")):
    _dev.development(_sys.modules[__name__], _tree, _prefix, max(f["x"] for f in TREES[_tree]["focuses"]) + 3)
