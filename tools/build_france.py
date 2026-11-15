"""Generate France's focus tree and its Korean text: python tools/build_france.py

Every route is visible from the start, each in its own columns, and its first focus opens only
once the route is entered. Napoleon's routes stay hidden until the player reaches them.
"""
import re
from pathlib import Path

from PIL import Image

from france_text import TEXT
from event_text import LONG
from branch_text import BRANCH_TEXT
from war_text import PLAN_TEXT
from war_close import PLAN_CLOSE
import algeria
import alliances
from france_story import STORY
from novel_text import BASE, NEXT_LABELS, NOVEL, first_page
FOCUS_FUNDS = {"economy": 80, "society": 30}  # Kept in step with tools/build_economy.py.
from war_plans import FAMILY_CLOSE, PLANS, ROUTE_FAMILY_FLAGS, WAR_PREFIXES
from france_variety import BRANCH_EVENTS, EXCLUSIVE, GATES, OR_PARENTS, ORDERS, REWARDS, ROUTE_FAMILIES, SYNERGY, WAR_EVENTS, focus_weeks
import new_routes
import victory
import integration_routes
TEXT.update(integration_routes.events_and_loc()[2])
# The two late routes join every table the other routes use.
STORY.extend(new_routes.STORY)
BRANCH_EVENTS.extend(new_routes.BRANCH)
BRANCH_TEXT.update(new_routes.BRANCH_TEXT)
TEXT.update(new_routes.FOCUS_TEXT)
NOVEL.update(new_routes.NOVEL)
import styled_scenes  # noqa: E402  the newer scenes in the house style
for _event, _pages in styled_scenes.PAGES.items():
    NOVEL[_event] = {"pages": _pages}
BASE.update(new_routes.NOVEL_BASE)
ROUTE_FAMILIES.update(new_routes.FAMILIES)
for _target, _texts in new_routes.WAR_TEXTS.items():
    WAR_EVENTS[_target][3].update(_texts)
# Part two of the older routes, and an ending for every route.
import part_two
import endings
for _head, _prefix, _route, _base, _chapters in STORY:
    _chapters.extend(part_two.PART2.get(_head, []))
TEXT.update(part_two.FOCUS_TEXT)
_novel, _base, ENDING_EVENTS, ENDING_LOC, _ending_text = endings.novel_and_events()
NOVEL.update(_novel)
BASE.update(_base)
TEXT.update(_ending_text)

PROJECT = Path(__file__).resolve().parent.parent
MOD = PROJECT / "mod"
VANILLA = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV")
FOCUSES = []


def build(kind, level):
    return (
        "random_owned_controlled_state = {\n"
        "\tlimit = { is_core_of = ROOT }\n"
        f"\tadd_extra_state_shared_building_slots = {level}\n"
        f"\tadd_building_construction = {{\n\t\ttype = {kind}\n\t\tlevel = {level}\n\t\tinstant_build = yes\n\t}}\n"
        "}"
    )


def mil(level): return build("arms_factory", level)
def civ(level): return build("industrial_complex", level)
def dock(level): return build("dockyard", level)
def stab(value): return f"add_stability = {value}"
def war(value): return f"add_war_support = {value}"
def pp(value): return f"add_political_power = {value}"
def xp(kind, value): return f"{kind}_experience = {value}"
def ai_will_do(item):
    """How much an AI France wants a focus. Industry comes first while there is peace, a war focus is taken as soon as
    it opens unless France is already fighting a war (one war at a time, as the route plans them), and a focus with
    an ai factor of 0 or less than 1 keeps that choice (the half-chance Russian war, for instance)."""
    text = "\n".join(item["effects"])
    base = item["ai"]
    lines = [f"\t\tai_will_do = {{", f"\t\t\tfactor = {base}"]
    if base >= 1 and "declare_war_on" in text:
        lines[1] = f"\t\t\tfactor = {base * 5}"
        lines.append("\t\t\tmodifier = { factor = 0.1 has_war = yes }")
    elif base >= 1 and any(k in text for k in ("arms_factory", "industrial_complex", "dockyard", "add_research_slot")):
        lines[1] = f"\t\t\tfactor = {base * 3}"
        lines.append("\t\t\tmodifier = { factor = 0.5 has_war = yes }")
    elif base >= 1 and any(k in text for k in ("army_experience", "add_war_support", "_tech", "air_experience")):
        lines[1] = f"\t\t\tfactor = {base * 2}"
    lines.append("\t\t}")
    return "\n".join(lines)


def goal(tag): return f"declare_war_on = {{\n\ttarget = {tag}\n\ttype = annex_everything\n}}"
def pop(ideology, value): return f"add_popularity = {{\n\tideology = {ideology}\n\tpopularity = {value}\n}}"


def tech(name, category):
    return f"add_tech_bonus = {{\n\tname = {name}\n\tbonus = 1.0\n\tuses = 1\n\tcategory = {category}\n}}"


def focus(fid, icon, x, y, name, desc, *effects, pre=(), route=None, me=(), available=None, cost=10, ai=1, seats=None):
    """pre holds AND groups; a tuple inside is an OR group."""
    FOCUSES.append(dict(id=fid, icon=icon, x=x, y=y, name=name, desc=desc, effects=effects,
                        pre=pre, route=route, me=me, available=available, cost=cost, ai=ai, seats=seats))


ROOT = "LR_FRA_the_kings_peace"
focus(ROOT, "national_unity", 10, 0, "패전의 그늘",
      "대전쟁의 패배로 식민지 제국을 잃었습니다. 프랑스는 흔들리는 나라를 다시 추슬러야 합니다.",
      stab(0.05), cost=5)

# Shared economy.
E = "LR_FRA_"
focus(E + "war_reparations", "positive_trade_relations", 2, 1, "배상금 재협상", "승전국들을 설득해 배상금 부담을 줄입니다.", pp(75), pre=[ROOT])
focus(E + "royal_arsenal", "construct_mil_factory", 1, 2, "병기창 재건", "조약의 눈을 피해 병기 공장을 다시 세웁니다.", mil(2), pre=[E + "war_reparations"])
focus(E + "rebuild_railways", "construct_civ_factory", 3, 2, "철도 재건", "전쟁으로 무너진 철도와 공장을 복구합니다.", civ(2), pre=[E + "war_reparations"])
focus(E + "steelworks", "production", 0, 3, "로렌 제철소", "로렌의 철광과 제철소를 다시 돌립니다.", mil(2), pre=[E + "royal_arsenal"])
focus(E + "tunisia_morocco", "construct_infrastructure", 2, 3, "북아프리카 개발", "남은 북아프리카 영토에 공장을 세웁니다.", civ(2), pre=[(E + "royal_arsenal", E + "rebuild_railways")])
focus(E + "ports", "construct_naval_dockyard", 4, 3, "항구 재건", "브레스트와 툴롱의 조선소를 복구합니다.", dock(2), pre=[E + "rebuild_railways"])
focus(E + "mass_production", "construct_military", 0, 4, "대량 생산", "미국식 조립 라인을 도입합니다.", tech("LR_FRA_mass_production", "industry"), pre=[E + "steelworks"])
focus(E + "royal_academy", "scientific_exchange", 2, 4, "과학 아카데미", "전쟁은 패했지만 프랑스의 학문은 건재합니다.", "add_research_slot = 1", pre=[E + "tunisia_morocco"])
focus(E + "rural_power", "construct_civilian", 4, 4, "농촌 전력화", "시골까지 전기를 보내 공장을 분산합니다.", civ(2), pre=[E + "ports"])
focus(E + "synthetic_fuel", "oil_refinery", 1, 5, "합성 연료", "석유 없는 프랑스의 약점을 메웁니다.", tech("LR_FRA_synthetic_fuel", "industry"), pre=[E + "mass_production", E + "royal_academy"])
focus(E + "trade_treaties", "trade", 3, 5, "통상 조약", "중립국과의 무역으로 재원을 마련합니다.", pp(100), pre=[E + "royal_academy", E + "rural_power"])
focus(E + "war_economy", "construct_mil_factory", 2, 6, "전시 경제", "국가의 모든 역량을 복수에 쏟습니다.", mil(3), civ(3), pre=[E + "synthetic_fuel", E + "trade_treaties"])

# Shared military.
focus(E + "lessons_of_defeat", "army_doctrines", 9, 1, "패전의 교훈", "왜 졌는지 정직하게 연구합니다.", xp("army", 25), pre=[ROOT])
focus(E + "infantry_rearm", "small_arms", 7, 2, "보병 재무장", "낡은 소총을 교체합니다.", tech("LR_FRA_infantry_rearm", "infantry_weapons"), pre=[E + "lessons_of_defeat"])
focus(E + "artillery_school", "army_artillery", 9, 2, "포병 학교", "포병은 프랑스 육군의 자존심입니다.", tech("LR_FRA_artillery_school", "artillery"), pre=[E + "lessons_of_defeat"])
focus(E + "mobile_war", "army_tanks", 11, 2, "기동전 연구", "다음 전쟁은 참호에서 끝나지 않을 것입니다.", tech("LR_FRA_mobile_war", "armor"), pre=[E + "lessons_of_defeat"])
focus(E + "general_staff", "army_doctrines", 8, 3, "참모본부 개편", "늙은 장군들을 물러나게 합니다.", xp("army", 25), "set_country_flag = LR_FRA_high_command_open\ncustom_effect_tooltip = LR_tt_high_command_open", pre=[E + "infantry_rearm", E + "artillery_school"])
focus(E + "motorisation", "army_motorized", 10, 3, "차량화", "보병을 트럭에 태웁니다.", tech("LR_FRA_motorisation", "motorized_equipment"), pre=[E + "artillery_school", E + "mobile_war"])
focus(E + "tank_divisions", "build_tank", 12, 3, "기갑 사단", "전차를 집중 운용하는 부대를 만듭니다.", tech("LR_FRA_tank_divisions", "armor"), pre=[E + "mobile_war"])
focus(E + "air_arm", "build_airforce", 7, 4, "공군 창설", "하늘에는 아직 승전국의 조약이 닿지 못합니다.", xp("air", 25), pre=[E + "general_staff"])
focus(E + "revenge_army", "allies_build_infantry", 9, 4, "복수의 군대", "프랑스 육군은 다시 싸울 준비를 합니다.", xp("army", 25), war(0.1), pre=[E + "general_staff", E + "motorisation"])
focus(E + "new_navy", "build_navy", 11, 4, "새 함대", "영국의 바다에 다시 도전할 함대의 기초를 놓습니다.", xp("navy", 25), pre=[E + "motorisation"])
focus(E + "air_doctrine", "air_doctrine", 7, 5, "공군 교리", "공군의 역할을 새로 정합니다.", xp("air", 50), pre=[E + "air_arm"])
focus(E + "radio_net", "radar", 9, 5, "무선 통신망", "기동전의 신경망을 만듭니다.", tech("LR_FRA_radio_net", "electronics"), pre=[E + "revenge_army"])
focus(E + "fleet_doctrine", "navy_doctrines_tactics", 11, 5, "해군 교리", "함대 운용 방식을 다시 씁니다.", xp("navy", 50), pre=[E + "new_navy"])
focus(E + "ready_for_war", "major_war", 9, 6, "전쟁 준비 완료", "이제 프랑스는 다시 싸울 수 있습니다.", xp("army", 50), war(0.1), pre=[E + "air_doctrine", E + "radio_net", E + "fleet_doctrine"])


# National spirits granted by focuses: id, name, desc, picture, modifiers.
IDEAS = [
    ("LR_idea_strong_franc", "포앵카레의 프랑", "1926년의 교훈대로 프랑을 지켜 물가를 잡았습니다.", "generic_central_management", {"consumer_goods_factor": -0.05}),
    ("LR_idea_state_capital", "국가 주도 산업", "국가가 투자의 방향을 정합니다.", "generic_central_management", {"production_speed_buildings_factor": 0.1, "political_power_gain": -0.05}),
    ("LR_idea_private_capital", "민간 자본 유치", "리옹과 파리의 은행이 산업에 돈을 댑니다.", "generic_foreign_capital", {"industrial_capacity_factory": 0.1, "consumer_goods_factor": 0.03}),
    ("LR_idea_artisans", "프랑스 장인 정신", "숙련공의 전통을 공장으로 옮깁니다.", "generic_license_production", {"production_factory_max_efficiency_factor": 0.05}),
    ("LR_idea_petain_school", "방어 우선 교리", "화력과 요새로 적의 공세를 꺾습니다.", "generic_fortify_the_borders", {"army_defence_factor": 0.1}),
    ("LR_idea_degaulle_school", "기갑 우선 교리", "드골의 직업 군대론대로 기갑을 집중합니다.", "generic_armor", {"army_attack_factor": 0.1}),
    ("LR_idea_saint_cyr", "생시르 사관학교", "출신을 묻지 않고 장교를 뽑습니다.", "generic_army_war_college", {"experience_gain_army_factor": 0.1}),
    ("LR_idea_foreign_legion", "외인부대", "북아프리카의 전통을 잇는 정예 부대입니다.", "generic_reserve_divisions", {"conscription_factor": 0.05, "army_org_factor": 0.03}),
    ("LR_idea_general_mobilisation", "총동원 체제", "나라 전체를 전쟁에 맞춥니다.", "generic_war_preparation", {"training_time_factor": -0.1, "war_support_factor": 0.05}),
]


def idea(name):
    return f"add_ideas = {name}"


# Shared economy, second stage.
focus(E + "stabilise_franc", "positive_trade_relations", 0, 6, "프랑 안정화", "포앵카레의 방식으로 통화를 지킵니다.", idea("LR_idea_strong_franc"), pre=[E + "mass_production"])
focus(E + "nord_coal", "production", 4, 6, "북부 탄광 재개발", "노르와 파드칼레의 탄광을 다시 엽니다.", mil(2), pre=[E + "trade_treaties"])
focus(E + "citroen_trucks", "construct_military", 1, 7, "시트로엥 트럭 계약", "군용 트럭을 대량 주문합니다.", tech("LR_FRA_citroen_trucks", "motorized_equipment"), pre=[E + "war_economy"])
focus(E + "alpine_hydro", "construct_civilian", 3, 7, "알프스 수력 발전", "석탄 없는 프랑스의 답입니다.", civ(2), pre=[E + "war_economy"])
focus(E + "state_capital", "construct_civ_factory", 1, 8, "국가 주도 투자", "국가가 산업의 방향을 정합니다.", idea("LR_idea_state_capital"), pre=[E + "citroen_trucks"], me=[E + "private_capital"])
focus(E + "private_capital", "trade", 3, 8, "민간 자본 유치", "은행과 기업에 맡깁니다.", idea("LR_idea_private_capital"), pre=[E + "alpine_hydro"], me=[E + "state_capital"])
focus(E + "artisans", "scientific_exchange", 0, 8, "장인 전통의 산업화", "숙련공을 공장으로 끌어들입니다.", idea("LR_idea_artisans"), pre=[E + "stabilise_franc"])
focus(E + "lyon_chemicals", "oil_refinery", 4, 8, "리옹 화학 공업", "폭약과 합성 고무를 생산합니다.", tech("LR_FRA_lyon_chemicals", "industry"), pre=[E + "nord_coal"])
focus(E + "research_network", "scientific_exchange", 2, 9, "국립 연구 기관", "대학과 공장을 연결합니다.", tech("LR_FRA_research_network", "electronics"), pre=[(E + "state_capital", E + "private_capital")])
focus(E + "arsenal_of_republic", "construct_mil_factory", 2, 10, "프랑스의 병기창", "유럽 제일의 군수 산업을 세웁니다.", mil(4), pre=[E + "research_network"])

# Shared military, second stage.
focus(E + "petain_school", "fortify_city", 7, 7, "방어 우선 교리", "화력과 요새를 믿습니다.", idea("LR_idea_petain_school"), pre=[E + "ready_for_war"], me=[E + "degaulle_school"])
focus(E + "degaulle_school", "build_tank", 11, 7, "기갑 우선 교리", "직업 군대와 전차를 믿습니다.", idea("LR_idea_degaulle_school"), pre=[E + "ready_for_war"], me=[E + "petain_school"])
focus(E + "saint_cyr", "army_doctrines", 9, 7, "생시르 개혁", "사관학교의 문을 넓힙니다.", idea("LR_idea_saint_cyr"), pre=[E + "ready_for_war"])
focus(E + "heavy_artillery", "army_artillery", 7, 8, "75mm의 후계자", "프랑스 포병의 전통을 잇습니다.", tech("LR_FRA_heavy_artillery", "artillery"), pre=[E + "petain_school"])
focus(E + "char_b", "army_tanks", 11, 8, "샤르 B 계획", "주력 전차를 개발합니다.", tech("LR_FRA_char_b", "armor"), pre=[E + "degaulle_school"])
focus(E + "foreign_legion", "allies_build_infantry", 9, 8, "외인부대 확대", "시디벨아베스의 전통을 살립니다.", idea("LR_idea_foreign_legion"), pre=[E + "saint_cyr"])
focus(E + "fighter_school", "air_fighter", 7, 9, "전투기 학교", "새 조종사를 길러냅니다.", xp("air", 50), pre=[(E + "heavy_artillery", E + "foreign_legion")])
focus(E + "submarine_arm", "navy_submarine", 11, 9, "잠수함대", "영국 항로를 위협할 칼입니다.", xp("navy", 50), pre=[(E + "char_b", E + "foreign_legion")])
focus(E + "bomber_command", "air_bomber", 7, 10, "폭격기 사령부", "도시를 칠 수단을 갖춥니다.", xp("air", 50), pre=[E + "fighter_school"])
focus(E + "battleline", "navy_battleship", 11, 10, "주력 함대", "리슐리외급에 뒤지지 않는 전함을 짓습니다.", xp("navy", 50), pre=[E + "submarine_arm"])
focus(E + "general_mobilisation", "major_war", 9, 11, "총동원", "나라 전체를 전쟁에 맞춥니다.", idea("LR_idea_general_mobilisation"), pre=[E + "bomber_command", E + "battleline"])


def wars(prefix, route, x, y, last):
    """Every route ends by retaking Algeria, then attacking Germany, Britain and Russia."""
    focus(prefix + "algeria", "occupy_start_war", x, y, "알제리 진압", "반란군이 쥔 지중해 건너의 땅으로 다시 군대를 보냅니다. 비무장지대를 걷어 낼 때입니다.", algeria.CAMPAIGN, pre=[last], route=route, available=algeria.OPEN)
    focus(prefix + "rhine", "major_war", x, y + 1, "라인강으로", "프로이센이 앗아간 것을 되찾습니다.", goal("GER"), pre=[prefix + "algeria"], route=route)
    focus(prefix + "danube", "major_war", x + 1, y + 2, "빈으로", "합스부르크를 무너뜨립니다.", goal("AUS"), pre=[prefix + "rhine"], route=route)
    focus(prefix + "channel", "major_war", x, y + 2, "해협 건너로", "영국을 무너뜨립니다.", goal("ENG"), pre=[prefix + "rhine"], route=route)
    focus(prefix + "russia", "major_war", x, y + 3, "동쪽의 적", "러시아 공화국과의 마지막 전쟁입니다.", goal("SOV"), pre=[prefix + "channel"], route=route)


# Orleans.
O, R = "LR_ORL_", "LR_route_orleans"
focus(O + "duke", "national_unity", 16, 1, "오를레앙의 왕", "군부가 세운 새 왕이 복수를 맹세합니다.", stab(0.05), war(0.1), pre=[ROOT], route=R, cost=5)
focus(O + "shell_bills", "production", 15, 2, "유령회사 어음", "유령회사 어음으로 조약 밖의 군비를 마련합니다.", pp(100), mil(2), pre=[O + "duke"], route=R)
focus(O + "radical_rearm", "construct_mil_factory", 17, 2, "급진적 재무장", "조약을 찢어버리고 재무장을 선언합니다.", mil(3), war(0.05), pre=[O + "duke"], route=R)
focus(O + "calais", "fortify_city", 16, 3, "노르파드칼레 재무장", "비무장지대에 군대를 다시 들여보냅니다.", war(0.1), xp("army", 25), pre=[O + "shell_bills", O + "radical_rearm"], route=R)
wars(O, R, 16, 4, O + "calais")

# Bourbon.
B, R = "LR_BOU_", "LR_route_bourbon"
focus(B + "restored", "national_unity", 16, 1, "왕좌의 안정", "쿠데타를 꺾은 부르봉 왕가가 권위를 되찾습니다.", stab(0.1), pre=[ROOT], route=R, cost=5)
focus(B + "family_pact", "major_alliance", 15, 2, "가문 협약", "스페인 부르봉 왕가와 관계를 다집니다.", pp(75), "SPR = { add_opinion_modifier = { target = ROOT modifier = medium_increase } }", pre=[B + "restored"], route=R)
focus(B + "two_sicilies", "alliance", 15, 3, "나폴리의 사촌", "양시칠리아 왕에게 뒤를 봐주겠다고 약속합니다.", pp(50), "TTS = { add_opinion_modifier = { target = ROOT modifier = medium_increase } }", pre=[B + "family_pact"], route=R)
focus(B + "italy", "demand_territory", 15, 4, "이탈리아 통일전쟁", "양시칠리아가 교황령과 토스카나로 진군합니다.", goal("AUS"), pre=[B + "two_sicilies"], route=R)
focus(B + "diplomatic_rearm", "military_deal", 17, 2, "재무장 협상", "외교적 거래로 재무장을 인정받습니다.", mil(2), pp(50), pre=[B + "restored"], route=R, me=[B + "open_rearm"])
focus(B + "open_rearm", "construct_mil_factory", 19, 2, "막가파 재무장", "허락은 필요 없습니다.", mil(4), stab(-0.05), pre=[B + "restored"], route=R, me=[B + "diplomatic_rearm"])
wars(B, R, 17, 3, (B + "diplomatic_rearm", B + "open_rearm"))

# Socialist republic.
C, R = "LR_COM_", "LR_route_communist"
focus(C + "commune", "propaganda", 16, 1, "코뮌의 깃발", "150년 만에 혁명이 승리했습니다.", stab(0.05), pop("communism", 0.1), pre=[ROOT], route=R, cost=5)
focus(C + "workers_control", "construct_civ_factory", 16, 2, "노동자 통제", "공장을 노동자의 손에 넘깁니다.", civ(3), pre=[C + "commune"], route=R)
focus(C + "one_country", "national_unity", 15, 3, "일국사회주의", "먼저 프랑스의 사회주의를 지킵니다.", war(0.1), pre=[C + "workers_control"], route=R, me=[C + "world_revolution"])
focus(C + "world_revolution", "propaganda", 17, 3, "세계 혁명", "혁명은 국경에서 멈추지 않습니다.", pp(100), pre=[C + "workers_control"], route=R, me=[C + "one_country"])
focus(C + "annex_algeria", "occupy_start_war", 15, 4, "알제리 혁명 원정", "붉은 연대가 지중해를 건너 반란을 끝내고, 알제리를 코뮌의 일부로 묶습니다.", algeria.CAMPAIGN, pre=[C + "one_country"], route=R, available=algeria.OPEN)
focus(C + "algerian_comrades", "propaganda", 17, 4, "알제리 동지들", "총 대신 손을 내밉니다. 알제의 노동자 평의회가 코뮌과 함께하겠다고 답하면, 전쟁 없이 반란이 끝납니다.", algeria.PACIFY, pre=[C + "world_revolution"], route=R, available=algeria.OPEN)
focus(C + "rhine", "major_war", 16, 5, "라인강으로", "유럽의 왕들을 무너뜨립니다.", goal("GER"), pre=[(C + "annex_algeria", C + "algerian_comrades")], route=R)
focus(C + "channel", "major_war", 16, 6, "해협 건너로", "영국의 귀족 의회를 끝장냅니다.", goal("ENG"), pre=[C + "rhine"], route=R)
focus(C + "danube", "major_war", 17, 6, "빈으로", "민족의 감옥에 혁명의 문을 냅니다.", goal("AUS"), pre=[C + "rhine"], route=R)

# Jacobin.
J, R = "LR_JAC_", "LR_route_jacobin"
focus(J + "committee", "national_unity", 16, 1, "공안위원회", "산악파가 내각을 이끕니다.", stab(0.05), pre=[ROOT], route=R, cost=5)
focus(J + "social_contract", "propaganda", 15, 2, "사회 계약", "노동 시간을 줄이고 연금을 도입합니다.", pp(75), stab(0.05), pre=[J + "committee"], route=R, seats=45)
focus(J + "labour_code", "political_pressure", 17, 2, "노동법", "파업권과 단체 교섭을 법으로 보장합니다.", pop("democratic", 0.1), pre=[J + "committee"], route=R, seats=50)
focus(J + "public_works", "construct_civilian", 15, 3, "국가 공공사업", "국가가 직접 공장과 철도를 짓습니다.", civ(3), pre=[J + "social_contract"], route=R, seats=50)
focus(J + "nationalise", "production", 17, 3, "기간산업 국유화", "철도와 은행을 국가가 맡습니다.", mil(2), pre=[J + "labour_code"], route=R, seats=60)
focus(J + "public_school", "scientific_exchange", 16, 4, "공화국 학교", "모든 시민에게 교육을 보장합니다.", tech("LR_JAC_public_school", "electronics"), pre=[J + "public_works", J + "nationalise"], route=R, seats=55)
focus(J + "reclaim_algeria", "occupy_start_war", 16, 5, "알제리 수복 결정", "반란을 끝낼 원정군을 보냅니다. 그런데 누구를 보낼 것인가?", "country_event = { id = lr_novel.601 }", pre=[J + "public_school"], route=R, available=algeria.OPEN + "\nhas_war = no")
focus(J + "republican_army", "allies_build_infantry", 16, 6, "공화국 군대", "시민의 군대를 다시 일으킵니다.", xp("army", 50), war(0.1), pre=[J + "reclaim_algeria"], route=R, available="has_country_flag = LR_algeria_retaken")
focus(J + "rhine", "major_war", 16, 7, "라인강의 깃발", "프로이센이 앗아간 것을 되찾습니다.", goal("GER"), pre=[J + "republican_army"], route=R)
focus(J + "channel", "major_war", 16, 8, "해협 건너로", "귀족들의 의회가 다스리는 영국을 무너뜨립니다.", goal("ENG"), pre=[J + "rhine"], route=R)
focus(J + "danube", "major_war", 17, 8, "빈으로", "합스부르크를 무너뜨립니다.", goal("AUS"), pre=[J + "rhine"], route=R)
focus(J + "russia", "major_war", 16, 9, "동쪽의 적", "러시아 공화국과의 마지막 전쟁입니다.", goal("SOV"), pre=[J + "channel"], route=R, ai=10)

focus(J + "majority", "political_pressure", 19, 2, "의회 과반", "과반 의석으로 정부를 안정시킵니다.", stab(0.05), pp(50), pre=[J + "committee"], route=R, seats=51)
focus(J + "reform_act", "propaganda", 19, 3, "개혁 입법", "밀어붙일 힘이 생겼습니다.", civ(2), pre=[J + "majority"], route=R, seats=60)
focus(J + "supermajority", "national_unity", 19, 4, "개헌 의석", "3분의 2 의석으로 체제를 굳힙니다.", stab(0.1), war(0.05), pre=[J + "reform_act"], route=R, seats=67)

# Girondin.
G, R = "LR_GIR_", "LR_route_girondin"
focus(G + "cabinet", "national_unity", 16, 1, "지롱드 내각", "시장이 프랑스를 다시 일으킬 것입니다.", stab(0.05), pre=[ROOT], route=R, cost=5)
focus(G + "deregulation", "trade", 15, 2, "탈규제", "기업을 옭아맨 규제를 걷어냅니다.", civ(3), pre=[G + "cabinet"], route=R, seats=50)
focus(G + "free_trade", "positive_trade_relations", 17, 2, "자유 무역", "관세를 낮춰 성장을 이끌어냅니다.", pp(100), pre=[G + "cabinet"], route=R, seats=55)
wars(G, R, 16, 3, (G + "deregulation", G + "free_trade"))

focus(G + "majority", "political_pressure", 19, 2, "의회 과반", "과반 의석으로 정부를 안정시킵니다.", stab(0.05), pp(50), pre=[G + "cabinet"], route=R, seats=51)
focus(G + "reform_act", "propaganda", 19, 3, "개혁 입법", "밀어붙일 힘이 생겼습니다.", civ(2), pre=[G + "majority"], route=R, seats=60)
focus(G + "supermajority", "national_unity", 19, 4, "개헌 의석", "3분의 2 의석으로 체제를 굳힙니다.", stab(0.1), war(0.05), pre=[G + "reform_act"], route=R, seats=67)

# Marais.
M, R = "LR_MAR_", "LR_route_marais"
focus(M + "cabinet", "national_unity", 16, 1, "푀양파 내각", "입헌군주정과 질서를 내세웁니다.", stab(0.1), pre=[ROOT], route=R, cost=5)
focus(M + "constitution", "political_pressure", 15, 2, "입헌군주정 헌법", "왕을 다시 모시되 헌법 아래 둡니다.", pp(100), pre=[M + "cabinet"], route=R, seats=60)
focus(M + "order", "fortify_city", 17, 2, "질서 회복", "거리의 혁명가들을 단속합니다.", stab(0.05), pop("communism", -0.1), pre=[M + "cabinet"], route=R, seats=45)
wars(M, R, 16, 3, (M + "constitution", M + "order"))

focus(M + "majority", "political_pressure", 19, 2, "의회 과반", "과반 의석으로 정부를 안정시킵니다.", stab(0.05), pp(50), pre=[M + "cabinet"], route=R, seats=51)
focus(M + "reform_act", "propaganda", 19, 3, "개혁 입법", "밀어붙일 힘이 생겼습니다.", civ(2), pre=[M + "majority"], route=R, seats=60)
focus(M + "supermajority", "national_unity", 19, 4, "개헌 의석", "3분의 2 의석으로 체제를 굳힙니다.", stab(0.1), war(0.05), pre=[M + "reform_act"], route=R, seats=67)

# Hidden: Napoleon.
N, R = "LR_NAP_", "LR_route_napoleon"
focus(N + "first_consul", "national_unity", 16, 1, "제1통령", "아무도 몰랐던 코르시카의 포병 장교가 프랑스의 주인이 되었습니다.", pp(100), stab(0.05), pre=[ROOT], route=R, cost=5)
focus(N + "civil_code", "political_pressure", 15, 2, "나폴레옹 법전", "혁명의 성과와 질서를 하나의 법으로 묶습니다.", stab(0.1), pre=[N + "first_consul"], route=R)
focus(N + "bank_of_france", "production", 17, 2, "프랑스 은행", "국가 재정을 틀어쥡니다.", pp(75), civ(2), pre=[N + "first_consul"], route=R)
focus(N + "legion_of_honour", "military_sphere", 15, 3, "레지옹 도뇌르", "출신이 아니라 공으로 사람을 씁니다.", xp("army", 50), pre=[N + "civil_code"], route=R)
focus(N + "concordat", "improve_relations", 17, 3, "정교 협약", "교회와 화해합니다.", stab(0.05), pre=[N + "bank_of_france"], route=R)
focus(N + "coronation", "national_unity", 16, 4, "대관식", "노트르담에서 나폴레옹이 스스로 황제의 관을 씁니다.",
      "remove_ideas = LR_FRA_defeat", stab(0.1), war(0.1), "set_politics = {\n\truling_party = fascism\n\telections_allowed = no\n}",
      "promote_character = {\n\tcharacter = FRA_napoleon_bonaparte\n\tideology = fascism_ideology\n}", "set_cosmetic_tag = LR_FRA_empire", "set_country_flag = LR_route_empire", "mark_focus_tree_layout_dirty = yes",
      pre=[N + "legion_of_honour", N + "concordat"], route=R, me=[N + "guardian"])
focus(N + "continental_system", "forceful_treaty", 15, 5, "대륙봉쇄", "유럽의 항구를 영국에게 닫습니다.", pp(75), pre=[N + "coronation"], route="LR_route_empire")
focus(N + "grande_armee", "army_artillery", 17, 5, "대육군", "포병과 전차를 앞세운 대육군이 출범합니다.", xp("army", 75), war(0.1), pre=[N + "coronation"], route="LR_route_empire")
focus(N + "marshals", "military_sphere", 17, 6, "원수단", "황제의 원수들을 임명합니다.", xp("army", 50), pre=[N + "grande_armee"], route="LR_route_empire")
focus(N + "rhine", "major_war", 16, 7, "다시 라인강으로", "황제가 동쪽으로 진군합니다.", goal("GER"), pre=[N + "continental_system", N + "marshals"], route="LR_route_empire")
focus(N + "boulogne", "major_war", 16, 8, "불로뉴의 진영", "150년 전 아무도 하지 못한 영국 상륙을 준비합니다.", goal("ENG"), pre=[N + "rhine"], route="LR_route_empire")
focus(N + "danube", "major_war", 17, 8, "아우스터리츠로", "합스부르크를 무너뜨립니다.", goal("AUS"), pre=[N + "rhine"], route="LR_route_empire")
focus(N + "moscow", "major_war", 16, 9, "모스크바로", "이번에는 겨울이 오기 전에 끝냅니다.", goal("SOV"), pre=[N + "boulogne"], route="LR_route_empire")


# Napoleon's second path: a president who keeps the republic instead of a crown.
focus(N + "guardian", "political_pressure", 18, 4, "공화국의 수호자", "왕관을 거절합니다. 나폴레옹은 황제가 아니라 공화국의 대통령으로 남습니다.",
      "country_event = { id = lr_novel.701 }", pre=[N + "legion_of_honour", N + "concordat"], route="LR_route_napoleon", me=[N + "coronation"])
U, R = "LR_GUA_", "LR_route_guardian"
focus(U + "oath", "national_unity", 16, 5, "대통령 선서", "군복을 벗고 헌법에 손을 얹습니다.", stab(0.05), pop("democratic", 0.1), pre=[N + "guardian"], route=R, cost=5)
focus(U + "civilian_control", "political_pressure", 15, 6, "군의 문민 통제", "장군들을 의회 아래에 둡니다.", pp(75), pre=[U + "oath"], route=R, seats=50)
focus(U + "suffrage", "propaganda", 17, 6, "보통선거 보장", "모든 시민의 투표권을 헌법에 새깁니다.", stab(0.05), pop("democratic", 0.1), pre=[U + "oath"], route=R, seats=45)
focus(U + "social_insurance", "construct_civilian", 15, 7, "사회 보험", "병든 노동자와 노인을 나라가 돌봅니다.", civ(2), pre=[U + "civilian_control"], route=R, seats=55)
focus(U + "constitution", "national_unity", 17, 7, "공화국 헌법", "다시는 황제가 나오지 못하게 합니다.", "add_ideas = LR_idea_guardian_constitution", pre=[U + "suffrage"], route=R, seats=60)
focus(U + "citizen_army", "allies_build_infantry", 16, 8, "시민의 군대", "대육군이 아니라 공화국의 군대입니다.", xp("army", 50), war(0.1), pre=[U + "social_insurance", U + "constitution"], route=R)
focus(U + "rhine", "major_war", 16, 9, "공화국의 라인 원정", "왕들의 유럽에 자유를 가져갑니다.", goal("GER"), pre=[U + "citizen_army"], route=R)
focus(U + "channel", "major_war", 16, 10, "해협 건너로", "귀족 의회의 영국을 무너뜨립니다.", goal("ENG"), pre=[U + "rhine"], route=R)
focus(U + "danube", "major_war", 17, 10, "도나우의 자유", "합스부르크를 무너뜨립니다.", goal("AUS"), pre=[U + "rhine"], route=R)
focus(U + "russia", "major_war", 16, 11, "동쪽의 적", "이 전쟁은 AI일 때 절반의 확률로만 벌어집니다.", goal("SOV"), pre=[U + "channel"], route=R, ai=1)
focus(U + "amnesty", "improve_relations", 19, 5, "대사면", "쿠데타의 상처를 닫습니다.", "lr_fra_op_reduce = yes", pre=[U + "oath"], route=R)
focus(U + "league_of_republics", "alliance", 19, 6, "공화국 동맹", "북아메리카와 러시아의 공화주의자에게 손을 내밉니다.", pp(75), pre=[U + "amnesty"], route=R)

IDEAS.extend([
    ("LR_idea_guardian_constitution", "공화국 헌법", "권력은 시민에게서 나옵니다.", "generic_constitutional_guarantees", {"stability_factor": 0.1, "political_power_gain": 0.05}),
    ("LR_idea_autarky", "자급자족 경제", "수입 없이 전쟁 준비를 합니다.", "generic_central_management", {"production_lack_of_resource_penalty_factor": -0.15, "consumer_goods_factor": 0.03}),
    ("LR_idea_latin_league", "라틴 왕가 동맹", "부르봉 왕가들이 다시 손을 잡습니다.", "generic_flexible_foreign_policy", {"political_power_gain": 0.1}),
    ("LR_idea_planned_economy", "경제 계획", "평의회가 생산을 계획합니다.", "generic_central_management", {"production_speed_buildings_factor": 0.1, "consumer_goods_factor": 0.05}),
    ("LR_idea_tax_cut", "감세 정책", "기업과 부유층의 세금을 줄입니다.", "generic_foreign_capital", {"consumer_goods_factor": -0.05, "stability_factor": -0.03}),
    ("LR_idea_imperial_guard", "제국 근위대", "황제의 정예 부대입니다.", "generic_army_war_college", {"army_org_factor": 0.05, "army_attack_factor": 0.05}),
    ("LR_idea_labour_rights", "노동자의 권리", "주 40시간과 유급 휴가가 보장됩니다.", "generic_local_self_management", {"stability_factor": 0.1, "consumer_goods_factor": 0.03}),
    ("LR_idea_crown_and_altar", "왕관과 제단", "왕정과 교회가 화해합니다.", "generic_king_handled", {"stability_factor": 0.1}),
])


def extras(prefix, route, rows):
    """rows: key, icon, x, y, name, desc, prerequisite keys, effects (and optional seats)."""
    for row in rows:
        key, icon, x, y, name, desc, pre, effects, *seats = row
        focus(prefix + key, icon, x, y, name, desc, *effects, pre=[prefix + q for q in pre], route=route, seats=seats[0] if seats else None)


extras("LR_ORL_", "LR_route_orleans", [
    ("youth", "propaganda", 23, 1, "국민청년단", "복수를 외치는 청년들을 조직합니다.", ["duke"], [pop("fascism", 0.1)]),
    ("veterans", "allies_build_infantry", 23, 2, "재향군인회", "패전의 굴욕을 아는 사람들이 왕의 기둥입니다.", ["youth"], [war(0.05), xp("army", 25)]),
    ("tear_up_treaty", "forceful_treaty", 23, 3, "강화 조약 파기", "치욕의 조약은 더 이상 없습니다.", ["veterans"], [war(0.1), stab(-0.02)]),
    ("secret_staff", "army_doctrines", 25, 1, "비밀 참모본부", "왕실이 해체했던 참모본부 작전과를 되살립니다.", ["duke"], [xp("army", 50)]),
    ("press_control", "political_pressure", 25, 2, "언론 통제", "신문은 왕의 목소리가 됩니다.", ["secret_staff"], [stab(0.05), pp(50)]),
    ("autarky", "production", 25, 3, "자급자족 경제", "봉쇄에도 버틸 경제를 세웁니다.", ["press_control"], ["add_ideas = LR_idea_autarky"]),
    ("latin_front", "military_deal", 24, 4, "라틴 전선", "스페인에 동맹을 제안합니다.", ["tear_up_treaty", "autarky"], [pp(75)]),
])
extras("LR_BOU_", "LR_route_bourbon", [
    ("reims", "national_unity", 23, 1, "랭스 대관식", "역대 왕들처럼 랭스에서 왕관을 씁니다.", ["restored"], [stab(0.05)]),
    ("church", "improve_relations", 23, 2, "교회와의 화해", "왕관과 제단이 다시 손을 잡습니다.", ["reims"], ["add_ideas = LR_idea_crown_and_altar"]),
    ("peers", "political_pressure", 23, 3, "귀족원 부활", "옛 가문들을 국정에 끌어들입니다.", ["church"], [pp(75)]),
    ("colonial_talks", "positive_trade_relations", 25, 1, "식민지 반환 협상", "외교로 잃은 것을 조금씩 되찾으려 합니다.", ["restored"], [pp(50)]),
    ("mediterranean_pact", "navy_doctrines_tactics", 25, 2, "지중해 해군 협정", "스페인과 함께 서지중해를 지킵니다.", ["colonial_talks"], [xp("navy", 50)]),
    ("latin_league", "major_alliance", 25, 3, "라틴 왕가 동맹", "부르봉 왕가들의 동맹을 선포합니다.", ["mediterranean_pact"], ["add_ideas = LR_idea_latin_league"]),
    ("family_council", "military_sphere", 24, 4, "왕가 가족 회의", "마드리드와 나폴리의 친척들이 파리에 모입니다.", ["peers", "latin_league"], [stab(0.05), pp(50)]),
])
extras("LR_COM_", "LR_route_communist", [
    ("red_guards", "allies_build_infantry", 23, 1, "노동자 민병대", "공장마다 총을 나눠 줍니다.", ["commune"], [xp("army", 25)]),
    ("land_reform", "construct_civilian", 23, 2, "토지 개혁", "귀족의 땅을 농민에게 줍니다.", ["red_guards"], [stab(0.05)]),
    ("economic_plan", "construct_civ_factory", 23, 3, "경제 계획", "평의회가 생산을 계획합니다.", ["land_reform"], ["add_ideas = LR_idea_planned_economy"]),
    ("council", "propaganda", 25, 1, "코뮌 평의회", "파리의 구역마다 평의회를 세웁니다.", ["commune"], [pop("communism", 0.1)]),
    ("international", "alliance", 25, 2, "혁명 인터내셔널", "유럽 전역의 혁명가들을 파리로 부릅니다.", ["council"], [pp(75)]),
    ("russian_treaty", "major_alliance", 25, 3, "러시아 공화국과의 조약", "두 공화국이 손을 잡습니다.", ["international"], ["SOV = { add_opinion_modifier = { target = ROOT modifier = medium_increase } }"]),
    ("peoples_army", "army_doctrines", 24, 4, "인민군 창설", "장교단을 선거로 다시 뽑습니다.", ["economic_plan", "russian_treaty"], [xp("army", 50), war(0.05)]),
])
extras("LR_JAC_", "LR_route_jacobin", [
    ("forty_hours", "political_pressure", 23, 1, "주 40시간", "노동 시간을 법으로 줄입니다.", ["committee"], [stab(0.03)], 45),
    ("paid_leave", "propaganda", 23, 2, "유급 휴가", "노동자도 바다를 보러 갑니다.", ["forty_hours"], ["add_ideas = LR_idea_labour_rights"], 55),
    ("laicite", "scientific_exchange", 23, 3, "정교분리 강화", "학교에서 성직자를 내보냅니다.", ["paid_leave"], [pop("democratic", 0.05), stab(-0.02)], 55),
    ("bank_reform", "positive_trade_relations", 25, 1, "프랑스 은행 개혁", "200대 가문의 손에서 은행을 빼앗습니다.", ["committee"], [pp(75)], 50),
    ("arms_nationalised", "construct_mil_factory", 25, 2, "군수 산업 국유화", "슈나이더의 공장을 국가가 인수합니다.", ["bank_reform"], [mil(3)], 60),
])
extras("LR_GIR_", "LR_route_girondin", [
    ("bourse", "trade", 23, 1, "증권 시장 개방", "자본이 파리로 돌아옵니다.", ["cabinet"], [pp(50)]),
    ("tax_cut", "positive_trade_relations", 23, 2, "감세", "기업과 부유층의 세금을 줄입니다.", ["bourse"], ["add_ideas = LR_idea_tax_cut"], 50),
    ("tariffs_down", "trade", 23, 3, "관세 인하", "수출길을 넓힙니다.", ["tax_cut"], [civ(2)], 55),
    ("free_ports", "construct_naval_dockyard", 25, 1, "자유항", "마르세유와 르아브르를 개방합니다.", ["cabinet"], [dock(2)]),
    ("rail_privatised", "construct_civilian", 25, 2, "철도 민영화", "철도를 민간 회사에 넘깁니다.", ["free_ports"], [pp(75), stab(-0.02)], 55),
])
extras("LR_MAR_", "LR_route_marais", [
    ("kings_return", "national_unity", 23, 1, "왕실 귀환 협상", "입헌 군주를 맞이할 조건을 논의합니다.", ["cabinet"], [stab(0.03)], 50),
    ("senate", "political_pressure", 23, 2, "상원 복원", "명사들의 상원으로 민중을 견제합니다.", ["kings_return"], [pp(75)], 55),
    ("civil_law", "scientific_exchange", 23, 3, "재산권 수호법", "혁명기의 몰수를 되돌립니다.", ["senate"], [stab(0.03), pop("communism", -0.05)], 60),
    ("church_schools", "improve_relations", 25, 1, "교회 학교 복원", "교육을 다시 사제에게 맡깁니다.", ["cabinet"], ["add_ideas = LR_idea_crown_and_altar"], 50),
    ("gendarmerie", "fortify_city", 25, 2, "헌병대 강화", "지방의 질서는 헌병이 지킵니다.", ["church_schools"], ["lr_fra_op_reduce = yes"]),
])
extras("LR_NAP_", "LR_route_empire", [
    ("imperial_guard", "army_doctrines", 23, 5, "제국 근위대", "황제의 정예 부대를 창설합니다.", ["coronation"], ["add_ideas = LR_idea_imperial_guard"]),
    ("imperial_nobility", "military_sphere", 23, 6, "제국 귀족", "공을 세운 자에게 작위를 내립니다.", ["imperial_guard"], [pp(75), stab(0.03)]),
    ("rhine_confederation", "demand_territory", 25, 5, "라인 연방의 꿈", "독일 군주들에게 보호를 제안합니다.", ["coronation"], [pp(50), war(0.05)]),
    ("brother_kings", "major_alliance", 25, 6, "형제들의 왕국", "정복지를 보나파르트 일가에 맡길 계획을 세웁니다.", ["rhine_confederation"], [pp(75)]),
])

# Every route can break its opposition for good: this stops growth and the periodic uprising events.
REGION_KEYS = ["paris", "nord", "vendee", "midi", "rhone", "lorraine", "africa"]
CALM = ("custom_trigger_tooltip = {\n\ttooltip = LR_tt_uproot\n"
        + "\n".join(f"\tcheck_variable = {{ LR_op_{key} < 40 }}" for key in REGION_KEYS) + "\n}")
for prefix, route, first, step_one, one_desc, step_two, two_desc in [
    ("LR_ORL_", "LR_route_orleans", "duke", "공화주의자 색출", "군부가 지하 클럽을 뒤집니다. 모든 지역 반발도 -15.", "혁명의 뿌리 뽑기", "혁명 조직을 완전히 해체합니다. 모든 지역 반발도 -30, 이후 혁명파 세력이 늘지 않습니다."),
    ("LR_BOU_", "LR_route_bourbon", "restored", "왕실 경찰 강화", "왕의 경찰이 공화주의자를 추적합니다. 모든 지역 반발도 -15.", "혁명의 뿌리 뽑기", "혁명 조직을 완전히 해체합니다. 모든 지역 반발도 -30, 이후 혁명파 세력이 늘지 않습니다."),
    ("LR_MAR_", "LR_route_marais", "cabinet", "헌법 수호법", "공화국 전복 선동을 법으로 금합니다. 모든 지역 반발도 -15.", "급진파 해산", "급진 조직을 법으로 해산합니다. 모든 지역 반발도 -30, 이후 혁명파 세력이 늘지 않습니다."),
    ("LR_COM_", "LR_route_communist", "commune", "혁명 재판소", "왕당파를 혁명 재판에 세웁니다. 모든 지역 반발도 -15.", "반혁명의 뿌리 뽑기", "옛 귀족과 사제의 조직을 해체합니다. 모든 지역 반발도 -30, 이후 왕당파 세력이 늘지 않습니다."),
    ("LR_JAC_", "LR_route_jacobin", "committee", "공안 경찰", "공안위원회가 왕당파 음모를 추적합니다. 모든 지역 반발도 -15.", "방데 평정", "방데의 왕당파를 완전히 제압합니다. 모든 지역 반발도 -30, 이후 왕당파 세력이 늘지 않습니다."),
    ("LR_GIR_", "LR_route_girondin", "cabinet", "지방 분권 협약", "지방 유지들과 타협해 왕당파를 고립시킵니다. 모든 지역 반발도 -15.", "왕당파 해체", "자금줄을 끊어 왕당파 조직을 무너뜨립니다. 모든 지역 반발도 -30, 이후 왕당파 세력이 늘지 않습니다."),
    ("LR_NAP_", "LR_route_napoleon", "first_consul", "푸셰의 경찰", "치안장관 푸셰처럼 전국에 밀정을 풉니다. 모든 지역 반발도 -15.", "왕당파의 종말", "왕당파의 마지막 음모를 분쇄합니다. 모든 지역 반발도 -30, 이후 왕당파 세력이 늘지 않습니다."),
]:
    focus(prefix + "suppress", "political_pressure", 21, 1, step_one, one_desc, "lr_fra_op_reduce = yes", pre=[prefix + first], route=route)
    focus(prefix + "uproot", "special_forces", 21, 2, step_two, two_desc, "lr_fra_uproot = yes", pre=[prefix + "suppress"], route=route, available=CALM)


LEFT_BANK = """FRA = {
	transfer_state = 42
	transfer_state = 51
}
42 = { add_core_of = FRA }
51 = { add_core_of = FRA }"""
RHINE_HELD = ("custom_trigger_tooltip = {\n\ttooltip = LR_tt_rhine_held\n\tOR = {\n\t\thas_country_flag = LR_germany_defeated\n"
              "\t\t42 = { is_controlled_by = ROOT }\n\t}\n}")

new_routes.define(globals())
IDEAS.append(("LR_idea_continental_system", "대륙봉쇄", "유럽의 항구가 영국 상품에 닫혔습니다.", "generic_central_management", {"production_lack_of_resource_penalty_factor": -0.1, "consumer_goods_factor": 0.02}))
BY_ID = {item["id"]: item for item in FOCUSES}


def replace_effects(fid, *effects):
    BY_ID[fid]["effects"] = effects


def add_effects(fid, *effects):
    BY_ID[fid]["effects"] = tuple(BY_ID[fid]["effects"]) + effects


def require(fid, condition):
    item = BY_ID[fid]
    item["available"] = condition + ("\n" + item["available"] if item["available"] else "")


# Alliances that are real.
replace_effects("LR_BOU_family_pact", pp(50), "create_faction = LR_latin_league", "add_to_faction = SPR")
replace_effects("LR_BOU_two_sicilies", pp(50), "add_to_faction = TTS")
add_effects("LR_BOU_italy", "TTS = {\n\tannex_country = { target = TOS transfer_troops = yes }\n\tannex_country = { target = PAP transfer_troops = yes }\n}")
replace_effects("LR_ORL_latin_front", pp(50), "create_faction = LR_revanche_pact", "add_to_faction = SPR")
replace_effects("LR_COM_russian_treaty", pp(50), "create_faction = LR_red_pact", "add_to_faction = SOV")
replace_effects("LR_COM_algerian_comrades", algeria.PACIFY)
# The Rhine Confederation and the Bonaparte kings.
replace_effects("LR_NAP_rhine_confederation", "lr_found_rhine_confederation = yes", war(0.05))
require("LR_NAP_rhine_confederation", RHINE_HELD)
replace_effects("LR_NAP_brother_kings", pp(75), "every_country = {\n\tlimit = { is_subject_of = ROOT }\n\tadd_stability = 0.1\n\tadd_political_power = 50\n}")
replace_effects("LR_NAP_continental_system", "add_ideas = LR_idea_continental_system", pp(50))
# Nord-Pas-de-Calais opens only through rearmament.
add_effects("LR_ORL_calais", "29 = { set_demilitarized_zone = no }")
add_effects("LR_BOU_diplomatic_rearm", "29 = { set_demilitarized_zone = no }")
add_effects("LR_BOU_open_rearm", "29 = { set_demilitarized_zone = no }")
for prefix in ("LR_COM_", "LR_JAC_", "LR_GIR_", "LR_MAR_", "LR_NAP_", "LR_GUA_"):
    add_effects(prefix + "rhine", "29 = { set_demilitarized_zone = no }")
# The economy: focuses feed the indices, and big focuses need them.
add_effects("LR_FRA_rebuild_railways", "lr_fra_lay_rail = yes")
add_effects("LR_FRA_trade_treaties", "lr_fra_lay_rail = yes")
add_effects("LR_FRA_rural_power", "lr_fra_road_works = yes")
add_effects("LR_FRA_alpine_hydro", "lr_fra_road_works = yes")
add_effects("LR_JAC_public_works", "lr_fra_lay_rail = yes", "lr_fra_road_works = yes")
add_effects("LR_GIR_rail_privatised", "lr_fra_lay_rail = yes")
add_effects("LR_NAP_bank_of_france", "lr_fra_road_works = yes")
add_effects("LR_GUA_social_insurance", "lr_fra_road_works = yes")
require("LR_FRA_war_economy", "custom_trigger_tooltip = {\n\ttooltip = LR_tt_need_rail_3\n\tcheck_variable = { LR_rail_lines > 2 }\n}")
require("LR_FRA_arsenal_of_republic", "custom_trigger_tooltip = {\n\ttooltip = LR_tt_need_rearmament\n\tcheck_variable = { LR_tech_index > 59 }\n}")

# ===== More focuses, written by category =====
IDEAS.extend([
    ("LR_idea_national_labour", "국민 노동 봉사", "청년들이 삽을 들고 왕의 재건에 나섭니다.", "generic_war_preparation", {"production_speed_buildings_factor": 0.05}),
    ("LR_idea_royal_charity", "왕실 구호", "왕이 직접 빈민을 돌본다는 신화를 만듭니다.", "generic_king_handled", {"stability_factor": 0.05}),
    ("LR_idea_guilds", "길드 부활", "장인 조합이 노동을 조직합니다.", "generic_local_self_management", {"production_factory_max_efficiency_factor": 0.03, "stability_factor": 0.03}),
    ("LR_idea_fortress_france", "요새 프랑스", "먼저 이 땅을 지킵니다.", "generic_fortify_the_borders", {"army_defence_factor": 0.1, "conscription_factor": 0.05}),
    ("LR_idea_collective_farms", "농업 협동화", "토지를 합쳐 도시를 먹입니다.", "generic_agrarian_reform", {"consumer_goods_factor": -0.03, "stability_factor": -0.03}),
    ("LR_idea_comintern", "파리 인터내셔널", "세계 혁명의 사령부가 파리에 있습니다.", "generic_communist_army", {"political_power_gain": 0.1, "war_support_factor": 0.05}),
    ("LR_idea_red_volunteers", "국제 여단", "세계의 혁명가들이 프랑스군에 합류합니다.", "generic_communist_army", {"conscription_factor": 0.05, "army_attack_factor": 0.05}),
])
extras("LR_ORL_", "LR_route_orleans", [
    ("royal_council", "political_pressure", 0, 0, "왕실 군사 평의회", "장군들이 내각 위에 앉습니다. 의회는 박수를 치러 모일 뿐입니다.", ["duke"], [pp(75)]),
    ("family_allowance", "propaganda", 0, 0, "다자녀 수당", "병사가 될 아이를 낳는 어머니에게 왕이 메달과 돈을 줍니다.", ["duke"], [stab(0.03), "add_manpower = 5000"]),
    ("labour_service", "construct_civilian", 0, 0, "국민 노동 봉사단", "청년들이 삽을 메고 행진합니다. 도로가 놓이고, 언젠가 그 삽은 소총이 됩니다.", ["duke"], ["add_ideas = LR_idea_national_labour"]),
])
extras("LR_BOU_", "LR_route_bourbon", [
    ("poor_relief", "propaganda", 0, 0, "왕실 구호 기금", "왕비의 이름으로 빵이 나눠집니다. 혁명을 꿈꾸던 입이 빵을 씹기 시작합니다.", ["restored"], ["add_ideas = LR_idea_royal_charity"]),
    ("guilds", "production", 0, 0, "길드 부활", "노동조합 대신 왕의 칙허를 받은 길드입니다. 장인들은 옛 이름을 되찾았다며 기뻐합니다.", ["restored"], ["add_ideas = LR_idea_guilds"]),
    ("provincial_estates", "political_pressure", 0, 0, "지방 삼부회", "프로방스와 브르타뉴의 옛 특권을 돌려줍니다. 파리의 관료들은 불쾌하지만 지방은 왕을 사랑하게 됩니다.", ["restored"], [stab(0.03), pp(50)]),
])
extras("LR_JAC_", "LR_route_jacobin", [
    ("womens_vote", "propaganda", 0, 0, "여성 참정권", "마리 드 구즈의 150년 묵은 요구가 드디어 법이 됩니다.", ["committee"], [pop("democratic", 0.05), stab(0.02)], 55),
])
extras("LR_GIR_", "LR_route_girondin", [
    ("charity_schools", "scientific_exchange", 0, 0, "민간 학교 지원", "기업가들이 세운 기술 학교에 세금 혜택을 줍니다. 노동자의 아이들이 숙련공이 됩니다.", ["cabinet"], [tech("LR_GIR_charity_schools", "electronics")]),
    ("mutual_aid", "propaganda", 0, 0, "상호 부조 협회", "국가 대신 직능별 협회가 병든 노동자를 돌봅니다. 지롱드식 복지입니다.", ["cabinet"], [stab(0.03)], 45),
    ("provincial_power", "political_pressure", 0, 0, "지방 분권법", "파리의 권한을 지방으로 내립니다. 1793년 지롱드파가 목숨을 걸고 지키려던 원칙입니다.", ["cabinet"], [pp(75)], 55),
])
extras("LR_MAR_", "LR_route_marais", [
    ("parish_relief", "improve_relations", 0, 0, "교구 구호", "복지는 국가가 아니라 교구의 일입니다. 수녀들이 다시 병원과 고아원을 맡습니다.", ["cabinet"], [stab(0.03)], 45),
    ("property_franchise", "political_pressure", 0, 0, "재산 선거권", "납세액에 따라 표를 나눕니다. 민중의 표는 줄고 명사의 표는 늘어납니다.", ["cabinet"], [pp(75), pop("communism", -0.05)], 60),
])
extras("LR_NAP_", "LR_route_empire", [
    ("imperial_university", "scientific_exchange", 0, 0, "제국 대학", "교육은 황제의 관할입니다. 리세의 소년들이 제복을 입고 나폴레옹 법전을 외웁니다.", ["coronation"], [tech("LR_NAP_imperial_university", "electronics")]),
])
extras("LR_GUA_", "LR_route_guardian", [
    ("public_education", "scientific_exchange", 0, 0, "공교육 확대", "대통령이 직접 교과서 서문을 씁니다. 첫 문장은 황제가 아니라 시민으로 시작합니다.", ["oath"], [tech("LR_GUA_public_education", "electronics")], 50),
])
# Socialist republic: two lines that never meet.
extras("LR_COM_", "LR_route_communist", [
    ("fortress_france", "fortify_city", 0, 0, "요새 프랑스", "왕들의 군대는 언제든 올 수 있습니다. 혁명을 수출할 군대가 있다면 먼저 국경에 세웁니다.", ["one_country"], ["add_ideas = LR_idea_fortress_france"]),
    ("socialist_industry", "construct_mil_factory", 0, 0, "사회주의 공업화", "제1차 인민 계획. 철강과 전력이 무엇보다 앞섭니다. 소비재는 다음 계획에서 얘기하기로 합니다.", ["fortress_france"], [mil(3), civ(2)]),
    ("collective_farms", "construct_civilian", 0, 0, "농업 협동화", "도시 노동자를 먹이려면 농촌이 바뀌어야 합니다. 방데의 농민들이 다시 총을 꺼내 듭니다.", ["socialist_industry"], ["add_ideas = LR_idea_collective_farms"]),
    ("national_guard", "allies_build_infantry", 0, 0, "국민 방위군", "1792년의 이름을 되살립니다. 공장과 마을마다 방위대가 조직됩니다.", ["collective_farms"], [xp("army", 50), "add_manpower = 20000"]),
    ("no_foreign_masters", "political_pressure", 0, 0, "모스크바와의 거리", "프랑스 혁명의 교과서는 프랑스에서 씁니다. 러시아 고문단이 조용히 귀국 열차를 탑니다.", ["national_guard"], [stab(0.05), pp(75)]),
    ("comintern_paris", "propaganda", 0, 0, "파리 인터내셔널", "세계 혁명의 사령부가 몽마르트르에 문을 엽니다. 23개국 망명자들이 같은 복도를 씁니다.", ["international"], ["add_ideas = LR_idea_comintern"]),
    ("spanish_comrades", "propaganda", 0, 0, "스페인 동지 지원", "피레네 산맥을 넘어 전단과 소총이 갑니다. 마드리드의 왕은 잠을 설칩니다.", ["comintern_paris"], ["SPR = {\n\tadd_popularity = {\n\t\tideology = communism\n\t\tpopularity = 0.15\n\t}\n\tadd_stability = -0.05\n}"]),
    ("italian_workers", "propaganda", 0, 0, "이탈리아 노동자 봉기", "토리노와 나폴리의 공장에 파리의 소식이 도착합니다. 분열된 이탈리아가 혁명으로 먼저 하나가 될지도 모릅니다.", ["comintern_paris"], ["TTS = {\n\tadd_popularity = {\n\t\tideology = communism\n\t\tpopularity = 0.15\n\t}\n}", "ITA = {\n\tadd_popularity = {\n\t\tideology = communism\n\t\tpopularity = 0.15\n\t}\n}"]),
    ("german_spartacists", "propaganda", 0, 0, "독일 노동자 지원", "루르와 함부르크의 노조로 자금이 흘러갑니다. 프로이센 경찰이 찾아낸 돈은 극히 일부입니다.", ["spanish_comrades", "italian_workers"], ["GER = {\n\tadd_popularity = {\n\t\tideology = communism\n\t\tpopularity = 0.2\n\t}\n\tadd_stability = -0.05\n}"]),
    ("british_chartists", "propaganda", 0, 0, "차티스트의 후예", "맨체스터의 부두 노동자들이 파리에서 온 전단을 돌려 읽습니다. 귀족 의회는 이것을 전쟁 행위라 부릅니다.", ["german_spartacists"], ["ENG = {\n\tadd_popularity = {\n\t\tideology = communism\n\t\tpopularity = 0.15\n\t}\n\tadd_stability = -0.05\n}"]),
    ("red_volunteers", "allies_build_infantry", 0, 0, "국제 여단", "베를린의 선반공과 바르샤바의 학생, 나폴리의 부두 노동자가 같은 연대에 섭니다.", ["british_chartists"], ["add_ideas = LR_idea_red_volunteers", xp("army", 50)]),
])

BY_ID = {item["id"]: item for item in FOCUSES}
FILTERS = {"정치": "FOCUS_FILTER_POLITICAL", "외교": "FOCUS_FILTER_POLITICAL", "사회": "FOCUS_FILTER_INTERNAL_AFFAIRS",
           "경제": "FOCUS_FILTER_INDUSTRY", "군사": "FOCUS_FILTER_ARMY_XP", "치안": "FOCUS_FILTER_STABILITY",
           "의회": "FOCUS_FILTER_POLITICAL", "전쟁": "FOCUS_FILTER_ANNEXATION", "노선": "FOCUS_FILTER_POLITICAL"}


def plan(prefix, head, branches):
    """Rewire a route: each (category, ids) becomes one straight branch under the route head.
    A tuple in ids is a choice; the next focus accepts either."""
    for rank, (category, ids) in enumerate(branches):
        previous = prefix + head
        for element in ids:
            names = element if isinstance(element, tuple) else (element,)
            for name in names:
                item = BY_ID[prefix + name]
                item["pre"] = [previous]
                item["rank"] = rank
                item["filter"] = FILTERS[category]
            previous = tuple(prefix + n for n in names) if len(names) > 1 else prefix + names[0]


plan("LR_ORL_", "duke", [
    ("정치", ["royal_council", "youth", "press_control", "tear_up_treaty"]),
    ("사회", ["family_allowance", "veterans", "labour_service"]),
    ("경제", ["shell_bills", "radical_rearm", "autarky"]),
    ("군사", ["secret_staff", "calais", "latin_front"]),
    ("치안", ["suppress", "uproot"]),
])
BY_ID["LR_ORL_algeria"]["pre"] = ["LR_ORL_calais"]
plan("LR_BOU_", "restored", [
    ("정치", ["reims", "provincial_estates", "peers", "family_council"]),
    ("사회", ["church", "poor_relief", "guilds"]),
    ("외교", ["family_pact", "two_sicilies", "italy"]),
    ("외교", ["colonial_talks", "mediterranean_pact", "latin_league"]),
    ("군사", [("diplomatic_rearm", "open_rearm")]),
    ("치안", ["suppress", "uproot"]),
])
BY_ID["LR_BOU_algeria"]["pre"] = [("LR_BOU_diplomatic_rearm", "LR_BOU_open_rearm")]
plan("LR_JAC_", "committee", [
    ("사회", ["social_contract", "forty_hours", "paid_leave", "womens_vote", "laicite", "public_school"]),
    ("경제", ["public_works", "labour_code", "nationalise", "bank_reform", "arms_nationalised"]),
    ("의회", ["majority", "reform_act", "supermajority"]),
    ("치안", ["suppress", "uproot"]),
])
BY_ID["LR_JAC_reclaim_algeria"]["pre"] = ["LR_JAC_public_school"]
plan("LR_GIR_", "cabinet", [
    ("경제", ["deregulation", "free_trade", "bourse", "tax_cut", "tariffs_down", "free_ports", "rail_privatised"]),
    ("사회", ["mutual_aid", "charity_schools"]),
    ("정치", ["provincial_power"]),
    ("의회", ["majority", "reform_act", "supermajority"]),
    ("치안", ["suppress", "uproot"]),
])
BY_ID["LR_GIR_algeria"]["pre"] = ["LR_GIR_free_trade"]
plan("LR_MAR_", "cabinet", [
    ("정치", ["constitution", "kings_return", "senate", "property_franchise", "civil_law"]),
    ("사회", ["church_schools", "parish_relief"]),
    ("의회", ["majority", "reform_act", "supermajority"]),
    ("치안", ["order", "gendarmerie", "suppress", "uproot"]),
])
BY_ID["LR_MAR_algeria"]["pre"] = ["LR_MAR_order"]
plan("LR_COM_", "commune", [
    ("정치", ["council"]),
    ("사회", ["land_reform"]),
    ("경제", ["workers_control", "economic_plan"]),
    ("군사", ["red_guards", "peoples_army"]),
    ("노선", ["one_country", "fortress_france", "socialist_industry", "collective_farms", "national_guard", "no_foreign_masters", "annex_algeria"]),
    ("노선", ["world_revolution", "international", "comintern_paris", "spanish_comrades", "german_spartacists", "british_chartists", "red_volunteers"]),
    ("치안", ["suppress", "uproot"]),
])
# The world revolution side branches, and the road to war from either line.
BY_ID["LR_COM_russian_treaty"]["pre"] = ["LR_COM_international"]
BY_ID["LR_COM_algerian_comrades"]["pre"] = ["LR_COM_russian_treaty"]
BY_ID["LR_COM_italian_workers"]["pre"] = ["LR_COM_comintern_paris"]
BY_ID["LR_COM_german_spartacists"]["pre"] = ["LR_COM_spanish_comrades", "LR_COM_italian_workers"]
BY_ID["LR_COM_rhine"]["pre"] = [("LR_COM_annex_algeria", "LR_COM_red_volunteers")]
plan("LR_GUA_", "oath", [
    ("정치", ["civilian_control", "constitution", "league_of_republics"]),
    ("사회", ["suffrage", "public_education", "social_insurance", "amnesty"]),
])
BY_ID["LR_GUA_citizen_army"]["pre"] = ["LR_GUA_constitution", "LR_GUA_social_insurance"]
plan("LR_NAP_", "coronation", [
    ("정치", ["imperial_nobility", "brother_kings"]),
    ("사회", ["imperial_university"]),
    ("경제", ["continental_system"]),
    ("군사", ["imperial_guard", "grande_armee", "marshals"]),
])
BY_ID["LR_NAP_rhine_confederation"]["pre"] = ["LR_NAP_rhine"]
for fid in ("LR_ORL_algeria", "LR_BOU_algeria", "LR_GIR_algeria", "LR_MAR_algeria"):
    BY_ID[fid]["filter"] = FILTERS["전쟁"]
BY_ID["LR_JAC_reclaim_algeria"]["filter"] = FILTERS["전쟁"]

# ===== Military in three services, routes in five branches =====
def doctrine(name, category):
    return f"add_doctrine_cost_reduction = {{\n\tname = {name}\n\tcost_reduction = 0.5\n\tuses = 1\n\tcategory = {category}\n}}"


def rifles(amount):
    return f"add_equipment_to_stockpile = {{\n\ttype = infantry_equipment\n\tamount = {amount}\n}}"


IDEAS.extend([
    ("LR_idea_colonial_regiments", "주아브와 티라외르", "북아프리카 연대가 본토군의 빈자리를 메웁니다.", "generic_reserve_divisions", {"conscription_factor": 0.05, "out_of_supply_factor": -0.1}),
    ("LR_idea_chasseurs_alpins", "알프스 산악병", "베레모를 쓴 푸른 악마들이 산악전을 가르칩니다.", "generic_army_war_college", {"army_org_factor": 0.03, "land_reinforce_rate": 0.02}),
    ("LR_idea_combat_engineers", "공병 전통", "보방의 후예들이 다리와 참호를 책임집니다.", "generic_fortify_the_borders", {"army_defence_factor": 0.05, "supply_consumption_factor": -0.05}),
    ("LR_idea_staff_college", "고등 전쟁 대학", "참모 장교들이 지도 위에서 다음 전쟁을 치릅니다.", "generic_army_war_college", {"planning_speed": 0.1, "max_planning": 0.05}),
    ("LR_idea_combined_fleet", "대서양과 지중해의 두 함대", "브레스트와 툴롱이 한 지휘 아래 움직입니다.", "generic_navy_bonus", {"naval_coordination": 0.1, "naval_morale_factor": 0.1}),
    ("LR_idea_commerce_raiding", "통상 파괴전", "영국의 빵과 석유가 지나는 길을 노립니다.", "generic_sea_focused_navy", {"navy_max_range_factor": 0.1}),
    ("LR_idea_convoy_school", "호송대 학교", "상선단을 지키는 법을 다시 배웁니다.", "generic_coastal_navy", {"convoy_escort_efficiency": 0.1}),
    ("LR_idea_marines", "해병 보병", "식민지 전쟁의 경험을 상륙전 교리로 옮깁니다.", "generic_navy_bonus", {"naval_invasion_prep_speed": 0.1}),
    ("LR_idea_air_aces", "라파예트의 후예", "기욘메르의 전통을 잇는 에이스 학교입니다.", "generic_air_bonus", {"air_ace_generation_chance_factor": 0.25, "air_superiority_efficiency": 0.05}),
    ("LR_idea_air_safety", "항공 안전국", "사고로 잃는 조종사를 줄입니다.", "generic_air_research", {"air_accidents_factor": -0.15, "air_training_xp_gain_factor": 0.1}),
    ("LR_idea_air_detection", "방공 감시망", "해안과 국경에 감시 초소를 잇습니다.", "generic_air_payment", {"air_detection": 0.1, "air_mission_efficiency": 0.05}),
])

extras("LR_FRA_", None, [
    # 육군
    ("colonial_regiments", "allies_build_infantry", 0, 0, "주아브와 티라외르", "모로코와 튀니지 연대를 본토 전선으로 부릅니다. 이들은 프랑스를 위해 싸운 지 백 년이 넘었습니다.", ["lessons_of_defeat"], ["add_ideas = LR_idea_colonial_regiments", "add_manpower = 15000"]),
    ("chasseurs_alpins", "army_doctrines", 0, 0, "알프스 산악병", "샤모니의 훈련장에서 베레모를 쓴 부대가 자랍니다. 사르데냐와 오스트리아 국경은 산악전이 될 것입니다.", ["lessons_of_defeat"], ["add_ideas = LR_idea_chasseurs_alpins", tech("LR_FRA_chasseurs", "cat_mountaineers_doctrine")]),
    ("rifle_stocks", "small_arms", 0, 0, "MAS 소총 양산", "생테티엔 조병창이 드디어 새 소총을 양산합니다. 르벨 소총을 든 마지막 세대가 물러갑니다.", ["lessons_of_defeat"], [rifles(5000), tech("LR_FRA_rifle_stocks", "infantry_weapons")]),
    ("combat_engineers", "fortify_city", 0, 0, "공병 전통", "보방의 나라답게 공병은 프랑스 육군의 자랑입니다. 다리를 놓는 부대가 전쟁의 속도를 정합니다.", ["lessons_of_defeat"], ["add_ideas = LR_idea_combat_engineers", tech("LR_FRA_engineers", "engineers_tech")]),
    ("staff_college", "army_doctrines", 0, 0, "고등 전쟁 대학", "포슈의 강의실이 다시 열립니다. 젊은 대령들이 대전쟁의 작전 지도를 처음부터 다시 그립니다.", ["lessons_of_defeat"], ["add_ideas = LR_idea_staff_college", doctrine("LR_FRA_staff_college", "land_doctrine")]),
    ("armoured_recon", "army_motorized", 0, 0, "기병의 기계화", "소뮈르의 기병 장교들이 말에서 내립니다. 눈물을 흘리는 사람도 있지만 정찰 전차는 말보다 빠릅니다.", ["lessons_of_defeat"], [tech("LR_FRA_armoured_recon", "cat_armored_cars"), xp("army", 25)]),
    # 해군
    ("cruiser_squadron", "navy_cruiser", 0, 0, "대양 순양함대", "제국 없는 해군에게 남은 임무는 항로입니다. 빠른 순양함들이 대서양으로 나갑니다.", ["new_navy"], [tech("LR_FRA_cruisers", "ca_tech"), xp("navy", 25)]),
    ("destroyer_flotillas", "navy_anti_submarine", 0, 0, "구축함 전단", "르 팡타스크급은 세계에서 가장 빠른 구축함입니다. 영국 전함을 괴롭힐 사냥개들입니다.", ["new_navy"], [tech("LR_FRA_destroyers", "dd_tech")]),
    ("commerce_raiding", "navy_submarine", 0, 0, "통상 파괴전", "런던의 빵과 석유는 배로 옵니다. 함대 결전 대신 그 배를 노립니다.", ["new_navy"], ["add_ideas = LR_idea_commerce_raiding", tech("LR_FRA_subs", "ss_tech")]),
    ("bearn_carrier", "navy_carrier", 0, 0, "베아른의 후계자", "프랑스의 유일한 항공모함은 느리고 낡았습니다. 제독들이 처음으로 새 설계안을 꺼냅니다.", ["new_navy"], [tech("LR_FRA_carriers", "cv_tech"), xp("navy", 25)]),
    ("naval_aviation", "air_naval_bomber", 0, 0, "해군 항공대", "공군과의 오랜 다툼 끝에 해군이 자기 비행기를 갖습니다.", ["new_navy"], [tech("LR_FRA_naval_air", "naval_bomber"), xp("air", 25)]),
    ("mers_el_kebir", "construct_naval_dockyard", 0, 0, "지중해 기지", "튀니스 비제르트의 요새 항구를 키웁니다. 지브롤터와 몰타 사이에 프랑스의 닻을 내립니다.", ["new_navy"], ["458 = {\n\tadd_extra_state_shared_building_slots = 2\n\tadd_building_construction = {\n\t\ttype = dockyard\n\t\tlevel = 2\n\t\tinstant_build = yes\n\t}\n}", "add_ideas = LR_idea_combined_fleet"]),
    ("convoy_school", "positive_trade_relations", 0, 0, "호송대 학교", "대전쟁 때 유보트에 배운 교훈입니다. 상선과 군함이 함께 항해하는 법을 다시 익힙니다.", ["new_navy"], ["add_ideas = LR_idea_convoy_school", tech("LR_FRA_convoy", "asw_tech")]),
    ("fusiliers_marins", "amphibious_assault", 0, 0, "해병 보병", "식민지 전쟁의 경험을 교리로 묶습니다. 해협을 건너려면 이들이 먼저 해변에 서야 합니다.", ["new_navy"], ["add_ideas = LR_idea_marines", tech("LR_FRA_marines", "marine_tech")]),
    # 공군
    ("dewoitine_fighters", "air_fighter", 0, 0, "드부아틴 전투기", "툴루즈의 공장에서 단엽 전투기가 굴러 나옵니다. 복엽기의 시대가 끝납니다.", ["air_arm"], [tech("LR_FRA_dewoitine", "light_fighter")]),
    ("air_aces", "air_doctrine", 0, 0, "라파예트의 후예", "기욘메르와 퐁크의 이름을 단 비행단이 창설됩니다. 공군은 영웅이 필요합니다.", ["air_arm"], ["add_ideas = LR_idea_air_aces", xp("air", 25)]),
    ("potez_bombers", "air_bomber", 0, 0, "포테즈 경폭격기", "빠른 쌍발 폭격기가 라인강 다리를 겨냥합니다.", ["air_arm"], [tech("LR_FRA_potez", "tactical_bomber")]),
    ("strategic_force", "air_bomber", 0, 0, "전략 폭격 부대", "두에의 이론을 믿는 장군들이 4발 폭격기 예산을 따냅니다. 육군은 격렬히 반대했습니다.", ["air_arm"], [tech("LR_FRA_strategic", "cat_strategic_bomber"), xp("air", 25)]),
    ("cas_wings", "air_production", 0, 0, "지상 지원 비행단", "전차와 무전으로 연결된 급강하 폭격기입니다. 드골 대령이 이 계획에 사인했습니다.", ["air_arm"], [tech("LR_FRA_cas", "cas_bomber")]),
    ("air_safety", "scientific_exchange", 0, 0, "항공 안전국", "기체 결함으로 잃는 조종사가 전투로 잃는 조종사보다 많습니다. 정비와 훈련부터 고칩니다.", ["air_arm"], ["add_ideas = LR_idea_air_safety"]),
    ("air_detection", "radar", 0, 0, "방공 감시망", "해안과 국경에 감시 초소와 전화선을 잇습니다. 전쟁의 첫 경보가 여기서 울립니다.", ["air_arm"], ["add_ideas = LR_idea_air_detection", tech("LR_FRA_air_watch", "electronics")]),
    ("paratroopers", "special_forces", 0, 0, "공수 부대", "북아프리카에서 첫 강하 실험을 합니다. 낙하산병이라는 말에 참모본부가 웃었지만 곧 웃지 못할 것입니다.", ["air_arm"], [tech("LR_FRA_para", "cat_paratroopers_doctrine"), xp("army", 25)]),
])

# New diplomacy for routes that had none.
FRIEND = "{tag} = {{ add_opinion_modifier = {{ target = ROOT modifier = medium_increase }} }}"
extras("LR_ORL_", "LR_route_orleans", [
    ("neutral_ties", "improve_relations", 0, 0, "중립국 회유", "스웨덴 철광과 스위스 금고는 중립입니다. 왕의 사절이 양쪽 다 찾아갑니다.", ["duke"], [pp(50), FRIEND.format(tag="SWE"), FRIEND.format(tag="SWI")]),
    ("ottoman_talks", "dangerous_deal", 0, 0, "이스탄불 밀담", "승전국 진영의 틈을 노립니다. 오스만이 영국 편에 끝까지 설 이유는 없습니다.", ["neutral_ties"], [pp(50), FRIEND.format(tag="TUR")]),
])
extras("LR_JAC_", "LR_route_jacobin", [
    ("dutch_treaty", "improve_relations", 0, 0, "헤이그 조약", "왕들의 유럽에서 의회를 가진 몇 안 되는 이웃입니다. 네덜란드의 상인 공화국에 손을 내밉니다.", ["committee"], [FRIEND.format(tag="HOL"), pp(50)]),
    ("american_contact", "military_deal", 0, 0, "필라델피아의 친구들", "식민지의 공화주의자들에게 비밀 편지를 보냅니다. 라파예트의 이름은 아직 쓸모가 있습니다.", ["dutch_treaty"], [FRIEND.format(tag="USA"), pp(50)]),
])
extras("LR_GIR_", "LR_route_girondin", [
    ("merchant_envoys", "positive_trade_relations", 0, 0, "상인 사절단", "외교관 대신 은행가가 런던과 암스테르담으로 갑니다. 전쟁보다 어음이 빠릅니다.", ["cabinet"], [FRIEND.format(tag="HOL"), pp(50)]),
    ("atlantic_trade", "trade", 0, 0, "대서양 무역", "보르도 항구에 다시 신대륙 깃발이 들어옵니다.", ["merchant_envoys"], [FRIEND.format(tag="CAN"), civ(1)]),
])
extras("LR_MAR_", "LR_route_marais", [
    ("vienna_talks", "improve_relations", 0, 0, "빈 협상", "입헌 군주정은 왕들과 대화할 수 있다고 믿습니다. 합스부르크의 대사가 파리에 돌아옵니다.", ["cabinet"], [FRIEND.format(tag="AUS"), pp(50)]),
    ("london_model", "military_deal", 0, 0, "영국식 의회", "웨스트민스터에 시찰단을 보냅니다. 적에게서도 배울 것은 배웁니다.", ["vienna_talks"], [FRIEND.format(tag="ENG"), stab(0.02)]),
])
extras("LR_COM_", "LR_route_communist", [
    ("workers_embassy", "alliance", 0, 0, "노동자 대사관", "왕실 외교관을 대신해 선반공 출신 대사들이 유럽의 수도로 나갑니다. 만찬 예절은 없지만 전단은 많습니다.", ["commune"], [pp(50)]),
])
extras("LR_NAP_", "LR_route_empire", [
    ("marriage_diplomacy", "major_alliance", 0, 0, "제국 혼인 외교", "구왕가의 공주가 벼락출세한 황제의 궁정으로 옵니다. 유럽의 왕들이 입술을 깨물고 축하 전보를 보냅니다.", ["coronation"], [FRIEND.format(tag="AUS"), stab(0.03)]),
])
extras("LR_GUA_", "LR_route_guardian", [
    ("national_reconciliation", "national_unity", 0, 0, "국민 화해", "왕당파와 코뮌 지도자가 한자리에 앉습니다. 대통령이 직접 사회를 봅니다.", ["oath"], [stab(0.05), "lr_fra_op_reduce = yes"]),
])

FILTERS.update({"외교": "FOCUS_FILTER_LR_DIPLOMACY", "내정": "FOCUS_FILTER_INTERNAL_AFFAIRS", "안정도": "FOCUS_FILTER_STABILITY", "영토확장": "FOCUS_FILTER_ANNEXATION",
                "육군": "FOCUS_FILTER_ARMY_XP", "해군": "FOCUS_FILTER_NAVY_XP", "공군": "FOCUS_FILTER_AIR_XP"})
BY_ID = {item["id"]: item for item in FOCUSES}


def gate(fid, *needs):
    require(fid, "\n".join(f"has_completed_focus = {n}" for n in needs))


# Three military trees straight off the root, beside the economy.
for rank, fid in enumerate(["war_reparations", "lessons_of_defeat", "new_navy", "air_arm"]):
    BY_ID["LR_FRA_" + fid]["pre"] = [ROOT]
    BY_ID["LR_FRA_" + fid]["rank"] = rank
    BY_ID["LR_FRA_" + fid]["route"] = None
BY_ID = {item["id"]: item for item in FOCUSES}
plan("LR_FRA_", "lessons_of_defeat", [
    ("육군", ["rifle_stocks", "infantry_rearm", "colonial_regiments", "foreign_legion", "chasseurs_alpins"]),
    ("육군", ["artillery_school", "heavy_artillery", "combat_engineers"]),
    ("육군", ["armoured_recon", "mobile_war", "motorisation", "tank_divisions", "char_b"]),
    ("육군", ["general_staff", "staff_college", "saint_cyr", "radio_net", ("petain_school", "degaulle_school"), "revenge_army", "ready_for_war", "general_mobilisation"]),
])
plan("LR_FRA_", "new_navy", [
    ("해군", ["fleet_doctrine", "cruiser_squadron", "destroyer_flotillas", "battleline"]),
    ("해군", ["submarine_arm", "commerce_raiding", "convoy_school"]),
    ("해군", ["bearn_carrier", "naval_aviation"]),
    ("해군", ["mers_el_kebir", "fusiliers_marins"]),
])
plan("LR_FRA_", "air_arm", [
    ("공군", ["fighter_school", "dewoitine_fighters", "air_aces", "air_doctrine"]),
    ("공군", ["bomber_command", "potez_bombers", "strategic_force"]),
    ("공군", ["cas_wings", "paratroopers"]),
    ("공군", ["air_safety", "air_detection"]),
])
BY_ID["LR_FRA_new_navy"]["filter"] = FILTERS["해군"]
BY_ID["LR_FRA_air_arm"]["filter"] = FILTERS["공군"]
BY_ID["LR_FRA_lessons_of_defeat"]["filter"] = FILTERS["육군"]

# Route trees: domestic, political, territorial, diplomatic, stability.
plan("LR_ORL_", "duke", [
    ("내정", ["family_allowance", "labour_service", "shell_bills", "radical_rearm", "autarky"]),
    ("정치", ["royal_council", "youth", "veterans", "press_control", "secret_staff", "tear_up_treaty"]),
    ("영토확장", ["calais", "algeria"]),
    ("외교", ["neutral_ties", "ottoman_talks", "latin_front"]),
    ("안정도", ["suppress", "uproot"]),
])
gate("LR_ORL_calais", "LR_ORL_radical_rearm")
plan("LR_BOU_", "restored", [
    ("내정", ["poor_relief", "guilds", ("diplomatic_rearm", "open_rearm")]),
    ("정치", ["reims", "provincial_estates", "peers", "family_council"]),
    ("영토확장", ["algeria"]),
    ("영토확장", ["italy"]),
    ("외교", ["family_pact", "two_sicilies", "colonial_talks", "mediterranean_pact", "latin_league"]),
    ("안정도", ["church", "suppress", "uproot"]),
])
require("LR_BOU_algeria", "OR = {\n\thas_completed_focus = LR_BOU_diplomatic_rearm\n\thas_completed_focus = LR_BOU_open_rearm\n}")
plan("LR_COM_", "commune", [
    ("내정", ["land_reform", "workers_control", "economic_plan"]),
    ("내정", ["red_guards", "peoples_army"]),
    ("정치", ["council"]),
    ("정치", ["one_country", "fortress_france", "socialist_industry", "collective_farms", "national_guard", "no_foreign_masters"]),
    ("정치", ["world_revolution", "international", "comintern_paris", "spanish_comrades", "italian_workers", "german_spartacists", "british_chartists", "red_volunteers"]),
    ("영토확장", [("annex_algeria", "algerian_comrades")]),
    ("외교", ["workers_embassy", "russian_treaty"]),
    ("안정도", ["suppress", "uproot"]),
])
gate("LR_COM_annex_algeria", "LR_COM_no_foreign_masters")
gate("LR_COM_algerian_comrades", "LR_COM_international")
gate("LR_COM_russian_treaty", "LR_COM_world_revolution")
BY_ID["LR_COM_rhine"]["pre"] = [("LR_COM_annex_algeria", "LR_COM_algerian_comrades")]
plan("LR_JAC_", "committee", [
    ("내정", ["social_contract", "forty_hours", "paid_leave", "public_school"]),
    ("내정", ["public_works", "nationalise", "bank_reform", "arms_nationalised"]),
    ("정치", ["labour_code", "womens_vote", "laicite"]),
    ("정치", ["majority", "reform_act", "supermajority"]),
    ("영토확장", ["reclaim_algeria"]),
    ("외교", ["dutch_treaty", "american_contact"]),
    ("안정도", ["suppress", "uproot"]),
])
gate("LR_JAC_reclaim_algeria", "LR_JAC_public_school")
plan("LR_GIR_", "cabinet", [
    ("내정", ["deregulation", "free_trade", "bourse", "tax_cut", "tariffs_down", "free_ports", "rail_privatised"]),
    ("내정", ["mutual_aid", "charity_schools"]),
    ("정치", ["provincial_power", "majority", "reform_act", "supermajority"]),
    ("영토확장", ["algeria"]),
    ("외교", ["merchant_envoys", "atlantic_trade"]),
    ("안정도", ["suppress", "uproot"]),
])
gate("LR_GIR_algeria", "LR_GIR_free_trade")
plan("LR_MAR_", "cabinet", [
    ("내정", ["church_schools", "parish_relief"]),
    ("정치", ["constitution", "kings_return", "senate", "property_franchise", "civil_law"]),
    ("정치", ["majority", "reform_act", "supermajority"]),
    ("영토확장", ["algeria"]),
    ("외교", ["vienna_talks", "london_model"]),
    ("안정도", ["order", "gendarmerie", "suppress", "uproot"]),
])
gate("LR_MAR_algeria", "LR_MAR_order")
plan("LR_NAP_", "coronation", [
    ("내정", ["imperial_university"]),
    ("정치", ["imperial_nobility", "brother_kings"]),
    ("영토확장", ["grande_armee", "marshals", "rhine"]),
    ("외교", ["continental_system", "marriage_diplomacy"]),
    ("안정도", ["imperial_guard"]),
])
plan("LR_GUA_", "oath", [
    ("내정", ["public_education", "social_insurance"]),
    ("정치", ["civilian_control", "suffrage", "constitution"]),
    ("영토확장", ["citizen_army"]),
    ("외교", ["league_of_republics"]),
    ("안정도", ["amnesty", "national_reconciliation"]),
])
gate("LR_GUA_citizen_army", "LR_GUA_constitution", "LR_GUA_social_insurance")
new_routes.arrange(globals())
for prefix, heads in (("LR_ORL_", ["algeria", "rhine", "danube", "channel", "russia"]), ("LR_BOU_", ["rhine", "danube", "channel", "russia"]),
                      ("LR_COM_", ["rhine", "danube", "channel"]), ("LR_JAC_", ["republican_army", "rhine", "danube", "channel", "russia"]),
                      ("LR_GIR_", ["rhine", "danube", "channel", "russia"]), ("LR_MAR_", ["rhine", "danube", "channel", "russia"]),
                      ("LR_NAP_", ["danube", "boulogne", "moscow", "rhine_confederation"]), ("LR_GUA_", ["rhine", "danube", "channel", "russia"])):
    for key in heads:
        BY_ID[prefix + key]["filter"] = FILTERS["영토확장"]

# ===== Italian war, alliances by consent, war readiness =====
IDEAS.append(("LR_idea_italian_volunteers", "나폴리로 가는 의용병", "왕의 이름으로 모집한 지원병이 양시칠리아군에 합류합니다.",
              "generic_reserve_divisions", {"send_volunteer_size": 2, "send_volunteer_divisions_required": -0.5}))
for index, row in enumerate(IDEAS):
    if row[0] == "LR_idea_general_mobilisation":
        IDEAS[index] = row[:4] + ({**row[4], "consumer_goods_factor": 0.05},)

extras("LR_BOU_", "LR_route_bourbon", [
    ("italian_arms", "small_arms", 0, 0, "왕의 소총", "툴롱에서 나폴리로 가는 화물선에 농기구라고 적힌 상자가 실립니다. 프랑스의 무기고가 그만큼 줄어듭니다.", ["two_sicilies"],
     ["send_equipment = {\n\ttarget = TTS\n\ttype = infantry_equipment\n\tamount = 3000\n}",
      "TTS = {\n\tdivision_template = {\n\t\tname = \"Volontaires Francais\"\n\t\tis_locked = yes\n\t\tpriority = 1\n\t\tregiments = {\n\t\t\tinfantry = { x = 0 y = 0 }\n\t\t\tinfantry = { x = 0 y = 1 }\n\t\t\tinfantry = { x = 1 y = 0 }\n\t\t\tinfantry = { x = 1 y = 1 }\n\t\t}\n\t}\n}"]),
    ("north_italy", "army_motorized", 0, 0, "피에몬테로", "로마와 피렌체가 떨어지면 토리노만 남습니다. 마지막 싸움을 앞둔 나폴리에 소총 5000정을 더 보냅니다.", ["italy"],
     ["send_equipment = {\n\ttarget = TTS\n\ttype = infantry_equipment\n\tamount = 5000\n}"]),
    ("italian_kingdom", "major_alliance", 0, 0, "이탈리아 왕국", "나폴리의 왕이 로마에서 이탈리아 왕관을 씁니다. 약속대로 그는 이제 부르봉 동맹의 일원으로 프랑스 곁에 섭니다. 다음 상대는 밀라노의 오스트리아인입니다.", ["north_italy"],
     ["set_global_flag = LR_italy_united",
      "remove_ideas = LR_idea_italian_volunteers",
      "every_country = {\n\tlimit = {\n\t\tOR = {\n\t\t\ttag = PAP\n\t\t\ttag = TOS\n\t\t\ttag = ITA\n\t\t}\n\t\tis_subject_of = TTS\n\t}\n\tTTS = { annex_country = { target = PREV transfer_troops = yes } }\n}",
      "TTS = {\n\tset_cosmetic_tag = FRA_TTS_italy\n\tadd_stability = 0.1\n\tadd_opinion_modifier = { target = ROOT modifier = medium_increase }\n}",
      "if = {\n\tlimit = { is_in_faction = no }\n\tcreate_faction = LR_francophonie\n}",
      "add_to_faction = TTS"]),
])

replace_effects("LR_BOU_family_pact", pp(50), "SPR = { add_opinion_modifier = { target = ROOT modifier = medium_increase } }")
replace_effects("LR_BOU_two_sicilies", pp(50), "TTS = { add_opinion_modifier = { target = ROOT modifier = medium_increase } }")
replace_effects("LR_BOU_italy",
                "set_country_flag = LR_italian_war",
                "add_ideas = LR_idea_italian_volunteers",
                "add_war_support = 0.03")
BY_ID = {item["id"]: item for item in FOCUSES}
TAKE_FACTION = "if = {{\n\tlimit = {{ is_in_faction = no }}\n\tcreate_faction = {faction}\n}}"
OFFER = "{tag} = {{ country_event = {{ id = lr_dipl.1 days = 3 }} }}"
# Whoever won the Spanish civil war receives the offer.
OFFER_SPAIN = ("if = {\n\tlimit = { SPR = { exists = yes } }\n\t" + OFFER.format(tag="SPR") + "\n}\n"
               "else_if = {\n\tlimit = { CRL = { exists = yes } }\n\t" + OFFER.format(tag="CRL") + "\n}\n"
               "else_if = {\n\tlimit = { ESR = { exists = yes } }\n\t" + OFFER.format(tag="ESR") + "\n}")
NO_SPANISH_WAR = "custom_trigger_tooltip = {\n\ttooltip = LR_tt_spain_at_peace\n\tNOT = { has_global_flag = LR_spain_civil_war }\n}"
# The old alliance focuses found the national bloc (alliances.py); its invitations are focuses of their own.
add_effects("LR_BOU_latin_league", TAKE_FACTION.format(faction="LR_francophonie"))
replace_effects("LR_ORL_latin_front", pp(50), TAKE_FACTION.format(faction="LR_francophonie"))
require("LR_BOU_latin_league", NO_SPANISH_WAR)
require("LR_ORL_latin_front", NO_SPANISH_WAR)
replace_effects("LR_COM_russian_treaty", pp(50), "SOV = { add_opinion_modifier = { target = ROOT modifier = medium_increase } }")
for _fid in alliances.MADE:
    BY_ID[_fid]["filter"] = FILTERS["외교"]

plan("LR_BOU_", "restored", [
    ("내정", ["poor_relief", "guilds", ("diplomatic_rearm", "open_rearm")]),
    ("정치", ["reims", "provincial_estates", "peers", "family_council"]),
    ("영토확장", ["algeria"]),
    ("영토확장", ["two_sicilies", "italian_arms", "italy", "north_italy", "italian_kingdom"]),
    ("외교", ["family_pact", "colonial_talks", "mediterranean_pact", "latin_league"]),
    ("안정도", ["church", "suppress", "uproot"]),
])
require("LR_BOU_italy", "custom_trigger_tooltip = {\n\ttooltip = LR_tt_italian_war_on\n\thas_global_flag = LR_italian_war_on\n}\nTTS = { exists = yes }")
require("LR_BOU_north_italy", "TTS = {\n\towns_state = 2\n\towns_state = 162\n}")
require("LR_BOU_italian_kingdom", "TTS = {\n\thas_war = no\n\towns_state = 2\n\towns_state = 162\n\towns_state = 158\n}")
BY_ID["LR_BOU_italian_kingdom"]["filter"] = FILTERS["영토확장"]

# Great wars wait until the army is ready and the previous war is over.
for fid in ("LR_ORL_rhine", "LR_BOU_rhine", "LR_COM_rhine", "LR_JAC_rhine", "LR_GIR_rhine", "LR_MAR_rhine", "LR_NAP_rhine", "LR_GUA_rhine"):
    require(fid, "has_completed_focus = LR_FRA_revenge_army\n" + algeria.NOT_CAMPAIGNING)
for fid in ("LR_ORL_channel", "LR_BOU_channel", "LR_COM_channel", "LR_JAC_channel", "LR_GIR_channel", "LR_MAR_channel", "LR_NAP_boulogne", "LR_GUA_channel"):
    require(fid, "has_completed_focus = LR_FRA_fusiliers_marins")
for item in FOCUSES:
    if item["id"].startswith("LR_MAR_plan_") or item["id"] in ("LR_MAR_rhine", "LR_MAR_danube", "LR_MAR_channel"):
        require(item["id"], "NOT = { has_country_flag = LR_entente_cordiale }")
    if item["id"].startswith("LR_BOU_plan_") or item["id"] in ("LR_BOU_italy", "LR_BOU_danube"):
        require(item["id"], "NOT = { has_country_flag = LR_diplomatic_revolution }")
for fid in ("LR_ORL_russia", "LR_BOU_russia", "LR_JAC_russia", "LR_GIR_russia", "LR_MAR_russia", "LR_NAP_moscow", "LR_GUA_russia"):
    require(fid, "has_country_flag = LR_germany_defeated")


ITALY_DECISIONS = """# Generated by tools/build_france.py.
LR_FRA_italy_category = {
	LR_dec_volunteer_division = {
		icon = generic_civil_support
		cost = 25
		days_re_enable = 30
		visible = {
			has_country_flag = LR_italian_war
			NOT = { has_global_flag = LR_italy_united }
		}
		available = {
			TTS = { has_war = yes }
			has_manpower > 9999
			has_equipment = { infantry_equipment > 999 }
			check_variable = { LR_volunteers_sent < 6 }
		}
		complete_effect = {
			add_manpower = -8000
			add_to_variable = { LR_volunteers_sent = 1 }
			send_equipment = {
				target = TTS
				type = infantry_equipment
				amount = 1000
			}
			TTS = {
				add_opinion_modifier = { target = ROOT modifier = small_increase }
			}
			create_unit = {
				division = "division_template = \\"Volontaires Francais\\" start_experience_factor = 0.3"
				owner = TTS
			}
		}
		ai_will_do = { factor = 1 }
	}
	LR_dec_italy_arms = {
		icon = generic_fundraising
		cost = 15
		days_re_enable = 30
		visible = {
			has_country_flag = LR_italian_war
			NOT = { has_global_flag = LR_italy_united }
		}
		available = {
			TTS = { has_war = yes }
			has_equipment = { infantry_equipment > 1999 }
		}
		complete_effect = {
			send_equipment = {
				target = TTS
				type = infantry_equipment
				amount = 2000
			}
		}
		ai_will_do = { factor = 1 }
	}
}
"""
ITALY_CATEGORY = """# Generated by tools/build_france.py.
LR_FRA_italy_category = {
	icon = generic_civil_support
	visible = {
		tag = FRA
		has_country_flag = LR_italian_war
		NOT = { has_global_flag = LR_italy_united }
	}
}
"""
DIPLOMACY_EVENTS = """# Generated by tools/build_france.py.
add_namespace = lr_dipl

# An alliance offer from France. FROM is France.
country_event = {
	id = lr_dipl.1
	title = lr_dipl.1.t
	desc = lr_dipl.1.d
	picture = GFX_report_event_generic_sign_treaty1
	is_triggered_only = yes
	option = {
		name = lr_dipl.1.a
		ai_chance = {
			factor = 30
			modifier = {
				factor = 3
				FROM = { has_country_flag = LR_route_bourbon }
			}
			modifier = {
				factor = 2
				has_opinion = { target = FROM value > 49 }
			}
			modifier = {
				factor = 2
				has_war = no
				is_in_faction = no
			}
		}
		if = {
			limit = { is_in_faction = yes }
			leave_faction = yes
		}
		FROM = {
			add_to_faction = ROOT
			country_event = { id = lr_dipl.2 }
		}
	}
	option = {
		name = lr_dipl.1.b
		ai_chance = {
			factor = 70
			modifier = {
				factor = 0.15
				FROM = { has_country_flag = LR_route_bourbon }
			}
		}
		FROM = {
			add_political_power = 25
			country_event = { id = lr_dipl.3 }
		}
	}
}

country_event = {
	id = lr_dipl.2
	title = lr_dipl.2.t
	desc = lr_dipl.2.d
	picture = GFX_report_event_generic_sign_treaty1
	is_triggered_only = yes
	option = { name = lr_dipl.2.a }
}

country_event = {
	id = lr_dipl.3
	title = lr_dipl.3.t
	desc = lr_dipl.3.d
	picture = GFX_report_event_generic_sign_treaty1
	is_triggered_only = yes
	option = { name = lr_dipl.3.a }
}
"""
ITALY_LOC = [
    ' FOCUS_FILTER_LR_ITALY_PLACEHOLDER:0 ""',
    ' LR_tt_spain_at_peace:0 "§Y스페인 내전§!이 끝나야 합니다."',
    ' LR_tt_italian_war_on:0 "§Y이탈리아 통일전쟁§!이 벌어지고 있어야 합니다. 1938년 7월에 터집니다."',
    ' FRA_TTS_italy:0 "이탈리아 왕국"',
    ' FRA_TTS_italy_DEF:0 "이탈리아 왕국"',
    ' FRA_TTS_italy_ADJ:0 "이탈리아"',
    ' LR_FRA_italy_category:0 "이탈리아 통일전쟁"',
    ' LR_FRA_italy_category_desc:0 "프랑스는 이 전쟁의 교전국이 아닙니다. 대신 지원병과 소총을 보내 나폴리의 왕을 돕습니다."',
    ' LR_dec_volunteer_division:0 "의용 사단 파견"',
    ' LR_dec_volunteer_division_desc:0 "지원병 사단 하나를 양시칠리아군에 넣습니다. 인력 8000과 소총 1000정이 프랑스에서 빠져나갑니다. 최대 6개 사단입니다."',
    ' LR_dec_italy_arms:0 "나폴리에 소총 보내기"',
    ' LR_dec_italy_arms_desc:0 "프랑스 비축분에서 소총 2000정을 나폴리로 보냅니다."',
    ' lr_dipl.1.t:0 "프랑스의 동맹 제안"',
    ' lr_dipl.1.d:0 "파리에서 온 특사가 왕궁 응접실에서 봉인된 서한을 내밉니다. 프랑스가 우리에게 동맹을 제안합니다.\\n\\n대전쟁에서 진 나라와 손을 잡는 것은 위험한 도박입니다. 승전국들은 이 조약을 도전으로 받아들일 것이고, 프랑스의 다음 전쟁은 우리의 전쟁이 됩니다. 그러나 프랑스는 다시 일어서고 있고, 그 곁에 서는 나라는 다음 유럽의 지도를 함께 그리게 될 것입니다.\\n\\n외무장관이 서한을 국왕 앞에 내려놓습니다."',
    ' lr_dipl.1.a:0 "동맹을 받아들인다"',
    ' lr_dipl.1.b:0 "정중히 거절한다"',
    ' lr_dipl.2.t:0 "동맹 체결"',
    ' lr_dipl.2.d:0 "특사가 서명된 조약문을 들고 돌아왔습니다. 상대가 우리의 제안을 받아들였습니다.\\n\\n외무부 복도에서 샴페인 코르크가 터지는 동안, 전신실에서는 벌써 런던과 빈에서 온 항의 전보가 쌓이기 시작합니다. 강화 조약을 위반하는 동맹이라고.\\n\\n외무장관은 전보 더미를 흘끗 보고 서랍에 넣습니다. \\"답장은 다음 주에 하지.\\""',
    ' lr_dipl.2.a:0 "좋습니다"',
    ' lr_dipl.3.t:0 "동맹 거절"',
    ' lr_dipl.3.d:0 "특사가 빈손으로 돌아왔습니다. 상대는 정중하게, 그러나 분명하게 거절했습니다.\\n\\n\\"귀국의 우정에는 감사하나, 지금은 때가 아닙니다.\\"\\n\\n외교관들은 그 말의 뜻을 압니다. 승전국들을 적으로 돌리기에는 프랑스가 아직 충분히 강해 보이지 않는다는 것입니다. 외무장관은 거절 서한을 서류철에 끼우며 날짜를 적어 둡니다. 언젠가 다시 꺼내 보게 될 날짜입니다."',
    ' lr_dipl.3.a:0 "언젠가 후회할 것입니다"',
]
ITALY_LOC.remove(' FOCUS_FILTER_LR_ITALY_PLACEHOLDER:0 ""')

# ===== Woven trees: branches that split and merge instead of straight lines =====
ROUTE_ORDER = {"FOCUS_FILTER_INTERNAL_AFFAIRS": 0, "FOCUS_FILTER_POLITICAL": 1, "FOCUS_FILTER_ANNEXATION": 2, "FOCUS_FILTER_LR_DIPLOMACY": 3, "FOCUS_FILTER_STABILITY": 4}


def weave(prefix, head, category, rows):
    """Rows of focuses. A tuple is an exclusive choice. "x<a+b" needs a and b, "x<a/b" needs either.
    Without "<": same width pairs up, one child needs every parent, otherwise the nearest parents, either one."""
    previous, groups = [prefix + head], [None]
    slot = 0
    for row in rows:
        entries = []
        for number, element in enumerate(row):
            for name in (element if isinstance(element, tuple) else (element,)):
                entries.append((name, number if isinstance(element, tuple) else None))
        new_ids, new_groups = [], []
        for index, (entry, group) in enumerate(entries):
            name, _, links = entry.partition("<")
            if links:
                parents = []
                for need in links.split("+"):
                    either = tuple(prefix + o for o in need.split("/"))
                    parents.append(either if len(either) > 1 else either[0])
            elif len(previous) == 1:
                parents = [previous[0]]
            elif len(entries) == 1:
                parents, seen = [], {}
                for fid, mark in zip(previous, groups):
                    if mark is None:
                        parents.append(fid)
                    else:
                        seen.setdefault(mark, []).append(fid)
                parents.extend(tuple(v) for v in seen.values())
            elif len(entries) == len(previous):
                parents = [previous[index]]
            else:
                low = index * len(previous) // len(entries)
                high = -(-(index + 1) * len(previous) // len(entries)) - 1
                near = previous[low:high + 1]
                parents = [near[0]] if len(near) == 1 else [tuple(near)]
            item = BY_ID[prefix + name]
            item["pre"] = parents
            item["slot"] = slot
            item["filter"] = FILTERS[category]
            slot += 1
            new_ids.append(prefix + name)
            new_groups.append(group)
        previous, groups = new_ids, new_groups


weave("LR_FRA_", "lessons_of_defeat", "육군", [
    ["rifle_stocks", "artillery_school", "general_staff", "armoured_recon"],
    ["infantry_rearm", "heavy_artillery", "staff_college", "mobile_war"],
    ["colonial_regiments", "combat_engineers<heavy_artillery+infantry_rearm", "saint_cyr", "motorisation"],
    ["foreign_legion<colonial_regiments", "chasseurs_alpins<colonial_regiments/combat_engineers", "radio_net<saint_cyr", "tank_divisions<motorisation"],
    [("petain_school<radio_net", "degaulle_school<radio_net+tank_divisions"), "char_b<tank_divisions"],
    ["revenge_army<petain_school/degaulle_school"],
    ["ready_for_war"],
    ["general_mobilisation"],
])
weave("LR_FRA_", "new_navy", "해군", [
    ["fleet_doctrine", "submarine_arm", "mers_el_kebir"],
    ["cruiser_squadron<fleet_doctrine", "destroyer_flotillas<fleet_doctrine", "commerce_raiding<submarine_arm", "fusiliers_marins<mers_el_kebir"],
    ["battleline<cruiser_squadron+destroyer_flotillas", "convoy_school<destroyer_flotillas/commerce_raiding", "bearn_carrier<mers_el_kebir"],
    ["naval_aviation<bearn_carrier"],
])
weave("LR_FRA_", "air_arm", "공군", [
    ["fighter_school", "bomber_command", "air_safety"],
    ["dewoitine_fighters<fighter_school", "air_aces<fighter_school", "potez_bombers<bomber_command", "air_detection<air_safety"],
    ["air_doctrine<dewoitine_fighters+air_aces", "cas_wings<potez_bombers", "strategic_force<potez_bombers"],
    ["paratroopers<air_doctrine/cas_wings"],
])

weave("LR_ORL_", "duke", "내정", [["family_allowance", "labour_service"], ["shell_bills"], ["radical_rearm", "autarky"]])
weave("LR_ORL_", "duke", "정치", [["royal_council"], ["youth", "veterans"], ["press_control", "secret_staff"], ["tear_up_treaty"]])
weave("LR_ORL_", "duke", "외교", [["neutral_ties"], ["ottoman_talks", "latin_front"]])

weave("LR_BOU_", "restored", "내정", [["poor_relief", "guilds"], [("diplomatic_rearm<poor_relief+guilds", "open_rearm<poor_relief+guilds")]])
weave("LR_BOU_", "restored", "정치", [["reims"], ["provincial_estates", "peers"], ["family_council"]])
weave("LR_BOU_", "restored", "외교", [
    ["family_pact"],
    ["colonial_talks", "two_sicilies"],
    ["mediterranean_pact", "italian_arms"],
    ["latin_league", "italy"],
])
weave("LR_BOU_", "italy", "영토확장", [["north_italy"], ["italian_kingdom"]])
for key in ("two_sicilies", "italian_arms", "italy"):
    BY_ID["LR_BOU_" + key]["filter"] = FILTERS["영토확장"]
weave("LR_BOU_", "restored", "안정도", [["church", "suppress"], ["uproot"]])

weave("LR_COM_", "commune", "내정", [["land_reform", "red_guards"], ["workers_control", "peoples_army"], ["economic_plan<workers_control"]])
weave("LR_COM_", "commune", "정치", [
    ["council"],
    [("one_country", "world_revolution")],
    ["fortress_france", "socialist_industry", "international", "comintern_paris"],
    ["national_guard", "collective_farms", "spanish_comrades<comintern_paris", "italian_workers<comintern_paris"],
    ["no_foreign_masters<national_guard+collective_farms", "german_spartacists<spanish_comrades", "british_chartists<italian_workers"],
    ["red_volunteers<german_spartacists+british_chartists"],
])

weave("LR_JAC_", "committee", "내정", [
    ["social_contract", "public_works"],
    ["forty_hours<social_contract", "paid_leave<social_contract", "nationalise<public_works"],
    ["public_school<forty_hours/paid_leave", "bank_reform<nationalise"],
    ["arms_nationalised<bank_reform"],
])
weave("LR_JAC_", "committee", "정치", [
    ["labour_code", "majority"],
    ["womens_vote<labour_code", "laicite<labour_code", "reform_act<majority"],
    ["supermajority<reform_act"],
])

weave("LR_GIR_", "cabinet", "내정", [
    ["deregulation", "mutual_aid"],
    ["free_trade<deregulation", "tax_cut<deregulation", "charity_schools<mutual_aid"],
    ["bourse<free_trade", "tariffs_down<tax_cut"],
    ["free_ports<bourse/tariffs_down", "rail_privatised<bourse+tariffs_down"],
])
weave("LR_GIR_", "cabinet", "정치", [["provincial_power", "majority"], ["reform_act<majority"], ["supermajority"]])

weave("LR_MAR_", "cabinet", "정치", [
    ["constitution", "majority"],
    ["kings_return<constitution", "senate<constitution", "reform_act<majority"],
    ["civil_law<kings_return/senate", "property_franchise<senate", "supermajority<reform_act"],
])
weave("LR_MAR_", "cabinet", "안정도", [["order"], ["gendarmerie", "suppress"], ["uproot"]])

weave("LR_GUA_", "oath", "정치", [["civilian_control", "suffrage"], ["constitution"]])
new_routes.weave_routes(globals())

# ===== Rulers and focus rewards as national spirits =====
IDEAS.extend([
])
INSTANT = ("add_stability", "add_war_support", "add_political_power")


def spirit(fid, name, desc, picture, modifiers, replaces=()):
    """The focus now grants a spirit instead of one-off stability, war support and political power."""
    idea_id = "LR_idea_" + fid.removeprefix("LR_").lower()
    IDEAS.append((idea_id, name, desc, picture, modifiers))
    kept = [e for e in BY_ID[fid]["effects"] if not str(e).startswith(INSTANT)]
    BY_ID[fid]["effects"] = tuple(kept) + tuple(f"remove_ideas = {old}" for old in replaces) + (f"add_ideas = {idea_id}",)
    return idea_id


def royal(fid, new, *old):
    kept = [e for e in BY_ID[fid]["effects"] if not str(e).startswith(INSTANT)]
    BY_ID[fid]["effects"] = tuple(kept) + tuple(f"remove_ideas = {o}" for o in old) + (f"add_ideas = {new}",)


GOV, LOCAL, ARMY, AIR, NAVY, CHURCH, LAW = ("generic_central_management", "generic_local_self_management", "generic_army_war_college",
                                            "generic_air_bonus", "generic_navy_bonus", "generic_king_handled", "generic_constitutional_guarantees")
# Shared.
spirit("LR_FRA_war_reparations", "배상금 유예", "승전국들이 상환 일정을 늦췄습니다. 재무부가 숨을 돌립니다.", GOV, {"political_power_gain": 0.05, "consumer_goods_factor": -0.02})
spirit("LR_FRA_general_staff", "새 참모본부", "늙은 장군들이 물러나고 대령들이 지도를 펼칩니다.", ARMY, {"experience_gain_army_factor": 0.05, "planning_speed": 0.05})
revenge = spirit("LR_FRA_revenge_army", "복수의 군대", "프랑스 육군은 다음 전쟁만 기다립니다.", "generic_war_preparation", {"war_support_factor": 0.1})
spirit("LR_FRA_ready_for_war", "전쟁 준비 완료", "동원 계획이 금고에서 나왔습니다. 이제 명령만 남았습니다.", "generic_war_preparation", {"war_support_factor": 0.15, "army_org_factor": 0.03}, [revenge])
spirit("LR_FRA_air_doctrine", "공군 교리", "공군이 육군의 정찰병 노릇을 그만둡니다.", AIR, {"air_doctrine_cost_factor": -0.1})
spirit("LR_FRA_fighter_school", "전투기 학교", "이스트르 비행장에 젊은 조종사들이 모입니다.", AIR, {"air_superiority_efficiency": 0.05})
spirit("LR_FRA_fleet_doctrine", "해군 교리", "브레스트의 제독들이 함대 운용을 다시 씁니다.", NAVY, {"naval_doctrine_cost_factor": -0.1})
spirit("LR_FRA_battleline", "주력 함대", "됭케르크급 전함이 프랑스의 깃발을 달고 나갑니다.", NAVY, {"naval_morale_factor": 0.05, "navy_org_factor": 0.03})

# Orleans.
spirit("LR_ORL_duke", "복수의 맹세", "새 왕이 군 앞에서 맹세합니다. 빼앗긴 것을 모두 되찾겠다고.", "generic_war_preparation", {"war_support_factor": 0.05, "stability_factor": 0.03})
council = spirit("LR_ORL_royal_council", "왕실 군사 평의회", "왕의 곁에 장군들이 앉습니다. 내각은 그들의 결정을 받아 적습니다.", GOV, {"political_power_gain": 0.1})
vets = spirit("LR_ORL_veterans", "재향군인회", "대전쟁의 노병들이 왕의 지지 기반이 됩니다.", ARMY, {"war_support_factor": 0.05, "experience_gain_army_factor": 0.05})
spirit("LR_ORL_secret_staff", "비밀 참모본부", "왕실이 해체한 작전과가 민간 회사의 간판을 달고 다시 일합니다.", ARMY, {"war_support_factor": 0.05, "experience_gain_army_factor": 0.1, "planning_speed": 0.05}, [vets])
youth = spirit("LR_ORL_youth", "국민청년단", "제복을 입은 소년들이 왕의 이름을 외칩니다.", "generic_reserve_divisions", {"fascism_drift": 0.03, "conscription_factor": 0.02})
spirit("LR_ORL_press_control", "언론 통제", "파리의 신문들이 같은 사설을 싣기 시작합니다.", GOV, {"fascism_drift": 0.03, "conscription_factor": 0.02, "stability_factor": 0.05, "political_power_gain": 0.05}, [youth])
spirit("LR_ORL_tear_up_treaty", "조약을 찢은 나라", "베르사유의 서명은 이제 휴지입니다. 유럽이 프랑스를 경계합니다.", "generic_war_preparation", {"war_support_factor": 0.1, "stability_factor": -0.02})
spirit("LR_ORL_family_allowance", "다자녀 수당", "사라진 세대를 메우려 국가가 요람에 돈을 댑니다.", LOCAL, {"stability_factor": 0.03, "conscription_factor": 0.02})

# Bourbon.
royal("LR_BOU_restored", "LR_FRA_king_restored", "LR_FRA_king_louis")
royal("LR_BOU_reims", "LR_FRA_king_crowned", "LR_FRA_king_restored")
estates = spirit("LR_BOU_provincial_estates", "지방 삼부회", "두 세기 만에 지방 신분회가 다시 열립니다.", LOCAL, {"stability_factor": 0.03, "political_power_gain": 0.05})
peers = spirit("LR_BOU_peers", "귀족원", "옛 가문들이 왕의 곁으로 돌아옵니다.", CHURCH, {"political_power_gain": 0.1})
spirit("LR_BOU_family_council", "왕가 가족 회의", "마드리드와 나폴리의 친척들이 파리에서 프랑스의 앞날을 논합니다.", CHURCH, {"stability_factor": 0.08, "political_power_gain": 0.15}, [estates, peers])
spirit("LR_BOU_colonial_talks", "식민지 반환 협상", "런던은 땅을 내주지 않지만 대화 자체가 왕의 체면을 세웁니다.", "generic_flexible_foreign_policy", {"political_power_gain": 0.05})

# Commune.
spirit("LR_COM_commune", "코뮌의 깃발", "150년을 기다린 붉은 깃발이 시청에 오릅니다.", "generic_communist_army", {"stability_factor": 0.05, "communism_drift": 0.02})
spirit("LR_COM_council", "코뮌 평의회", "공장과 구역의 대표들이 나라를 운영합니다.", LOCAL, {"political_power_gain": 0.05, "communism_drift": 0.03})
one = spirit("LR_COM_one_country", "일국사회주의", "먼저 프랑스를 세웁니다. 세계는 그다음입니다.", GOV, {"stability_factor": 0.1})
world = spirit("LR_COM_world_revolution", "세계 혁명", "혁명은 국경에서 멈추지 않습니다.", "generic_communist_army", {"political_power_gain": 0.1, "war_support_factor": 0.03})
spirit("LR_COM_international", "혁명 인터내셔널", "세계의 혁명가들이 파리로 편지를 보냅니다.", "generic_communist_army", {"political_power_gain": 0.2, "war_support_factor": 0.03}, [world])
spirit("LR_COM_no_foreign_masters", "모스크바와의 거리", "프랑스 혁명은 누구의 지시도 받지 않습니다.", GOV, {"stability_factor": 0.15, "political_power_gain": 0.1}, [one])
spirit("LR_COM_land_reform", "토지 개혁", "농민이 자기 땅에서 일합니다. 혁명의 가장 든든한 지지층입니다.", "generic_agrarian_reform", {"stability_factor": 0.05})
spirit("LR_COM_peoples_army", "인민군", "장교를 선출하는 군대가 탄생합니다.", "generic_communist_army", {"war_support_factor": 0.05, "conscription_factor": 0.03})

# Democracy, three parties.
for tag, cabinet, name, desc, values in (
    ("LR_JAC_", "committee", "공안위원회", "로베스피에르의 이름은 금기지만 위원회는 돌아왔습니다.", {"stability_factor": 0.05}),
    ("LR_GIR_", "cabinet", "지롱드 내각", "보르도의 상인들이 내각을 차지했습니다.", {"stability_factor": 0.05}),
    ("LR_MAR_", "cabinet", "푀양파 내각", "온건한 명사들이 질서와 법을 약속합니다.", {"stability_factor": 0.1}),
):
    spirit(tag + cabinet, name, desc, GOV, values)
    held = spirit(tag + "majority", "의회 과반", "내각이 표를 걱정하지 않고 법안을 냅니다.", LAW, {"stability_factor": 0.05, "political_power_gain": 0.05})
    spirit(tag + "supermajority", "개헌 의석", "헌법까지 바꿀 수 있는 다수가 모였습니다. 야당은 항의문만 씁니다.", LAW, {"stability_factor": 0.1, "war_support_factor": 0.05, "political_power_gain": 0.05}, [held])
spirit("LR_JAC_social_contract", "사회 계약", "루소의 이름으로 국가가 시민에게 빚을 인정합니다.", LOCAL, {"political_power_gain": 0.05, "war_support_factor": 0.05})
spirit("LR_JAC_forty_hours", "주 40시간", "공장의 시계가 처음으로 노동자 편입니다.", LOCAL, {"stability_factor": 0.03})
spirit("LR_JAC_bank_reform", "은행 개혁", "200가문의 손에서 중앙은행을 가져옵니다.", GOV, {"political_power_gain": 0.1})
spirit("LR_JAC_republican_army", "공화국 군대", "시민이 된 병사들이 공화국을 위해 행군합니다.", "generic_reserve_divisions", {"war_support_factor": 0.1})
spirit("LR_GIR_free_trade", "자유 무역", "항구의 세관원들이 할 일이 없어졌습니다.", "generic_foreign_capital", {"political_power_gain": 0.1})
spirit("LR_GIR_bourse", "증권 시장 개방", "파리 증권거래소가 외국 자본으로 붐빕니다.", "generic_foreign_capital", {"political_power_gain": 0.05})
spirit("LR_GIR_mutual_aid", "상호 부조 협회", "국가 대신 시민이 서로를 돌봅니다.", LOCAL, {"stability_factor": 0.03})
spirit("LR_GIR_provincial_power", "지방 분권", "파리의 힘이 지방 의회로 내려갑니다.", LOCAL, {"political_power_gain": 0.05, "stability_factor": 0.02})
spirit("LR_MAR_constitution", "입헌군주정 헌법", "1791년의 약속이 마침내 법이 되었습니다. 왕의 자리는 비어 있습니다.", LAW, {"political_power_gain": 0.1})
royal("LR_MAR_kings_return", "LR_FRA_king_constitutional")
spirit("LR_MAR_senate", "상원", "명사들의 상원이 하원의 열기를 식힙니다.", LAW, {"political_power_gain": 0.1})
spirit("LR_MAR_parish_relief", "교구 구호", "교회가 다시 가난한 이들을 돌봅니다.", LOCAL, {"stability_factor": 0.03})

# Napoleon.
consul = spirit("LR_NAP_first_consul", "제1통령", "모든 권력이 한 사람의 책상으로 모입니다.", GOV, {"political_power_gain": 0.1, "war_support_factor": 0.05})
spirit("LR_NAP_civil_code", "나폴레옹 법전", "법 앞의 평등이 2천 개 조문으로 적혔습니다.", LAW, {"stability_factor": 0.1})
spirit("LR_NAP_concordat", "정교 협약", "교황이 공화국과 화해했습니다.", CHURCH, {"stability_factor": 0.05})
spirit("LR_NAP_legion_of_honour", "레지옹 도뇌르", "출신이 아니라 공으로 사람을 씁니다.", ARMY, {"experience_gain_army_factor": 0.1})
royal("LR_NAP_coronation", "LR_FRA_emperor", consul)
royal("LR_NAP_guardian", "LR_FRA_president", consul)
spirit("LR_NAP_grande_armee", "대육군", "다시 한 번 유럽이 그 행군 소리를 듣습니다.", "generic_war_preparation", {"war_support_factor": 0.1})
spirit("LR_NAP_imperial_nobility", "제국 귀족", "새 공작들은 칼로 작위를 얻었습니다.", CHURCH, {"political_power_gain": 0.05, "stability_factor": 0.03})
spirit("LR_GUA_oath", "대통령 선서", "군복을 벗고 헌법에 손을 얹었습니다.", LAW, {"stability_factor": 0.05})
spirit("LR_GUA_civilian_control", "군의 문민 통제", "장군 출신 대통령이 장군들을 내각 밖으로 내보냅니다.", LAW, {"political_power_gain": 0.05})
spirit("LR_GUA_suffrage", "보통선거", "처음으로 모든 시민이 표를 던집니다.", LAW, {"stability_factor": 0.05})
spirit("LR_GUA_citizen_army", "시민의 군대", "시민은 나라를 지키기 위해서만 총을 듭니다.", "generic_reserve_divisions", {"war_support_factor": 0.1})
spirit("LR_GUA_national_reconciliation", "국민 화해", "왕당파와 코뮌파가 같은 식탁에 앉았습니다.", LOCAL, {"stability_factor": 0.05})
new_routes.spirits(globals())

# Filters left over: the economy tree and the Napoleonic trunk.
for item in FOCUSES:
    if item["id"].startswith("LR_FRA_") and not item.get("filter") and item["id"] != ROOT:
        item["filter"] = FILTERS["경제"]
for fid, category in (("first_consul", "정치"), ("civil_code", "내정"), ("bank_of_france", "내정"), ("legion_of_honour", "정치"),
                      ("concordat", "외교"), ("coronation", "정치"), ("guardian", "정치"), ("suppress", "안정도"), ("uproot", "안정도")):
    BY_ID["LR_NAP_" + fid]["filter"] = FILTERS[category]
BY_ID["LR_GUA_oath"]["filter"] = FILTERS["정치"]
for fid in ("LR_ORL_duke", "LR_BOU_restored", "LR_COM_commune", "LR_JAC_committee", "LR_GIR_cabinet", "LR_MAR_cabinet"):
    BY_ID[fid]["filter"] = FILTERS["정치"]

# ===== More route focuses =====
def boost(name, values):
    """A reward that strengthens the focus's fixed spirit."""
    IDEAS.append(("LR_idea_x_" + name, "", "", "generic_central_management", values))
    return "add_ideas = LR_idea_x_" + name


FRIEND_OF = "{tag} = {{ add_opinion_modifier = {{ target = ROOT modifier = medium_increase }} }}"
SEAT_SCALE = 6  # Chapters speak in small numbers; the Chamber has 610 seats.
SEATS_UP = "add_to_variable = {{ LR_seats = {n} }}\nlr_fra_sync_seats = yes"


def more_focuses(prefix, route, category, rows):
    extras(prefix, route, rows)
    for row in rows:
        BY_ID_NEW.append((prefix + row[0], category))


BY_ID_NEW = []
more_focuses("LR_ORL_", "LR_route_orleans", "내정", [
    ("royal_roads", "construct_infrastructure", 0, 0, "왕립 고속도로", "실업자들이 삽을 들고 국경으로 가는 넓은 길을 냅니다. 공식 용도는 관광입니다.", ["autarky"], [civ(2), "lr_fra_road_works = yes"]),
    ("renault_seized", "construct_mil_factory", 0, 0, "르노 공장 접수", "왕의 군수국이 비양쿠르 공장의 문을 엽니다. 루이 르노는 항의문을 쓸 시간도 없었습니다.", ["radical_rearm"], [mil(3), boost("orl_renault", {"production_factory_max_efficiency_factor": 0.03})]),
])
more_focuses("LR_ORL_", "LR_route_orleans", "정치", [
    ("officers_oath", "army_doctrines", 0, 0, "장교단의 충성 서약", "장교들이 헌법이 아니라 왕 개인에게 맹세합니다.", ["tear_up_treaty"], [boost("orl_oath", {"army_org_factor": 0.03, "political_power_gain": 0.03})]),
    ("camelots", "propaganda", 0, 0, "왕의 행동대", "왕당파 청년들이 지팡이를 들고 파리 대로를 돌아다닙니다. 반대파 신문사의 유리창이 남아나지 않습니다.", ["press_control"], [boost("orl_camelots", {"fascism_drift": 0.03}), "lr_fra_op_reduce = yes"]),
])
more_focuses("LR_ORL_", "LR_route_orleans", "외교", [
    ("madrid_renounce", "improve_relations", 0, 0, "스페인 왕위 포기 선언", "오를레앙 가문은 마드리드의 왕위에 관심이 없다고 공식 선언합니다. 스페인 왕실이 처음으로 답장을 보냅니다.", ["latin_front"], [FRIEND_OF.format(tag="SPR"), boost("orl_madrid", {"political_power_gain": 0.03})]),
])
more_focuses("LR_ORL_", "LR_route_orleans", "안정도", [
    ("royal_security", "intelligence_exchange", 0, 0, "왕실 보안국", "전화국과 우체국에 왕의 사람들이 앉습니다. 뿌리 뽑힌 공화주의자들을 이제 서류로 관리합니다.", ["uproot"], [boost("orl_security", {"stability_factor": 0.05})]),
])

more_focuses("LR_BOU_", "LR_route_bourbon", "내정", [
    ("royal_manufactures", "construct_civ_factory", 0, 0, "왕립 매뉴팩처", "콜베르의 전통을 되살립니다. 왕의 인장이 찍힌 공장에 왕의 주문이 들어갑니다.", ["guilds"], [civ(3)]),
    ("peasant_credit", "construct_civilian", 0, 0, "농민 대출 금고", "왕이 농민의 빚을 대신 집니다. 시골의 충성은 이렇게 삽니다.", ["poor_relief"], [boost("bou_credit", {"stability_factor": 0.03, "conscription_factor": 0.02})]),
])
more_focuses("LR_BOU_", "LR_route_bourbon", "정치", [
    ("salic_law", "political_pressure", 0, 0, "살리카 법 재확인", "오를레앙 가문의 계승권 주장을 법정에서 영원히 끝냅니다.", ["family_council"], [boost("bou_salic", {"stability_factor": 0.05})]),
    ("swiss_guard", "military_sphere", 0, 0, "스위스 근위대 재건", "튈르리의 스위스 근위병이 돌아옵니다. 왕은 다시 자기 군대를 갖습니다.", ["reims"], [boost("bou_guard", {"army_morale_factor": 0.03, "political_power_gain": 0.03})]),
])
more_focuses("LR_BOU_", "LR_route_bourbon", "외교", [
    ("lisbon_treaty", "improve_relations", 0, 0, "리스본 조약", "리스본의 사촌도 초대합니다. 브라질의 금이 라틴 동맹으로 흐릅니다.", ["latin_league"], [FRIEND_OF.format(tag="POR"), boost("bou_lisbon", {"political_power_gain": 0.03})]),
])
more_focuses("LR_BOU_", "LR_route_bourbon", "안정도", [
    ("parish_registers", "national_unity", 0, 0, "교구 등록부", "신부가 마을의 공화주의자 이름까지 적습니다.", ["uproot"], [boost("bou_registers", {"stability_factor": 0.03}), "lr_fra_op_reduce = yes"]),
])

more_focuses("LR_COM_", "LR_route_communist", "내정", [
    ("electrification", "construct_civilian", 0, 0, "전국 전력망", "코뮌은 곧 전기입니다. 모든 마을에 전등이 들어옵니다.", ["economic_plan"], [civ(3), boost("com_power", {"production_speed_buildings_factor": 0.05})]),
    ("five_year_plan", "construct_mil_factory", 0, 0, "5개년 계획", "계획위원회가 강철과 대포의 숫자를 벽에 붙입니다.", ["economic_plan"], [mil(3), boost("com_plan", {"production_factory_max_efficiency_factor": 0.03})]),
])
more_focuses("LR_COM_", "LR_route_communist", "정치", [
    ("workers_university", "scientific_exchange", 0, 0, "노동자 대학", "소르본의 문이 선반공에게 열립니다.", ["council"], [boost("com_school", {"research_speed_factor": 0.03})]),
    ("french_road", "national_unity", 0, 0, "프랑스식 사회주의", "1793년과 1871년의 전통 위에 우리 길을 세웁니다.", ["no_foreign_masters"], [boost("com_french_road", {"stability_factor": 0.05, "war_support_factor": 0.03})]),
    ("world_republic", "major_war", 0, 0, "세계 공화국 선언", "파리는 더 이상 프랑스의 수도가 아닙니다. 세계 혁명의 수도입니다.", ["red_volunteers"], [boost("com_world", {"war_support_factor": 0.1, "communism_drift": 0.03})]),
])
more_focuses("LR_COM_", "LR_route_communist", "외교", [
    ("workers_solidarity", "improve_relations", 0, 0, "국제 노동 연대", "암스테르담 부두 노동자들에게 파업 기금을 보냅니다. 네덜란드 공화국이 불쾌해하면서도 받습니다.", ["workers_embassy"], [FRIEND_OF.format(tag="HOL"), boost("com_solidarity", {"political_power_gain": 0.03})]),
])
more_focuses("LR_COM_", "LR_route_communist", "안정도", [
    ("neighbourhood_committees", "national_unity", 0, 0, "구역 위원회", "모든 건물에 위원이 있습니다. 왕당파 노인도 이제 눈치를 봅니다.", ["uproot"], [boost("com_committees", {"stability_factor": 0.05})]),
])

more_focuses("LR_JAC_", "LR_route_jacobin", "내정", [
    ("public_housing", "construct_civilian", 0, 0, "공공 주택", "파리 외곽에 노동자 주택이 올라갑니다. 벽돌공들이 공화국에 표를 줍니다.", ["public_school"], [civ(2), boost("jac_housing", {"stability_factor": 0.03})]),
    ("arsenal_of_people", "construct_mil_factory", 0, 0, "시민의 조병창", "국유화된 공장이 공화국의 대포를 만듭니다.", ["arms_nationalised"], [mil(3)]),
])
more_focuses("LR_JAC_", "LR_route_jacobin", "정치", [
    ("republican_clubs", "propaganda", 0, 0, "공화주의 클럽", "자코뱅 클럽의 이름을 물려받은 토론회가 전국에 생깁니다. 의석 +30.", ["laicite"], [SEATS_UP.format(n=30)]),
    ("free_press", "political_pressure", 0, 0, "언론 자유법", "왕의 검열관이 일자리를 잃었습니다.", ["womens_vote"], [boost("jac_press", {"democratic_drift": 0.03, "stability_factor": 0.02})]),
])
more_focuses("LR_JAC_", "LR_route_jacobin", "외교", [
    ("swiss_asylum", "improve_relations", 0, 0, "제네바의 망명자들", "유럽 왕국들에서 쫓겨난 자유주의자들이 제네바에 모입니다. 공화국이 그들에게 여권을 줍니다.", ["american_contact"], [FRIEND_OF.format(tag="SWI"), boost("jac_asylum", {"political_power_gain": 0.03})]),
])
more_focuses("LR_JAC_", "LR_route_jacobin", "안정도", [
    ("citizen_police", "national_unity", 0, 0, "시민 경찰", "왕의 경찰을 해산하고 지방 의회 아래 새 경찰을 둡니다.", ["uproot"], [boost("jac_police", {"stability_factor": 0.05})]),
])

more_focuses("LR_GIR_", "LR_route_girondin", "내정", [
    ("bordeaux_wharves", "construct_naval_dockyard", 0, 0, "보르도 부두", "지롱드의 고향이 다시 대서양을 봅니다.", ["free_ports"], [dock(2), civ(1)]),
    ("credit_lyonnais", "trade", 0, 0, "리옹 신용은행", "은행이 산업에 돈을 대고, 산업이 내각에 돈을 댑니다.", ["bourse"], [boost("gir_credit", {"industrial_capacity_factory": 0.05})]),
])
more_focuses("LR_GIR_", "LR_route_girondin", "정치", [
    ("press_barons", "propaganda", 0, 0, "언론 재벌", "신문사 사주들이 내각 편에 섭니다. 의석 +30.", ["provincial_power"], [SEATS_UP.format(n=30)]),
])
more_focuses("LR_GIR_", "LR_route_girondin", "외교", [
    ("hudson_loans", "positive_trade_relations", 0, 0, "뉴욕의 차관", "영국령 북아메리카의 은행가들이 보르도에 지점을 냅니다.", ["atlantic_trade"], [FRIEND_OF.format(tag="USA"), boost("gir_loans", {"consumer_goods_factor": -0.02})]),
])
more_focuses("LR_GIR_", "LR_route_girondin", "안정도", [
    ("civic_guard", "national_unity", 0, 0, "지방 시민군", "파리가 아니라 각 데파르트망이 자기 질서를 지킵니다.", ["uproot"], [boost("gir_guard", {"stability_factor": 0.05})]),
])

more_focuses("LR_MAR_", "LR_route_marais", "내정", [
    ("agrarian_credit", "construct_civilian", 0, 0, "농업 신용", "지방 명사들의 은행이 농민에게 돈을 빌려줍니다.", ["parish_relief"], [civ(2), boost("mar_credit", {"stability_factor": 0.02})]),
    ("chartered_works", "construct_civ_factory", 0, 0, "칙허 회사", "왕의 칙허와 의회의 예산이 함께 들어간 공장입니다.", ["church_schools"], [civ(2)]),
])
more_focuses("LR_MAR_", "LR_route_marais", "정치", [
    ("parliament_coronation", "national_unity", 0, 0, "의회의 대관식", "왕이 의원들 앞에서 헌법에 먼저 맹세합니다. 왕관은 그다음입니다.", ["kings_return"], ["add_ideas = LR_FRA_king_parliament"]),
])
more_focuses("LR_MAR_", "LR_route_marais", "외교", [
    ("hague_arbitration", "improve_relations", 0, 0, "헤이그 중재 재판", "분쟁을 법정으로 가져가자고 제안합니다. 왕들은 웃었지만 대표를 보냅니다.", ["london_model"], [FRIEND_OF.format(tag="HOL"), boost("mar_hague", {"political_power_gain": 0.03})]),
])
more_focuses("LR_MAR_", "LR_route_marais", "안정도", [
    ("bourgeois_guard", "national_unity", 0, 0, "국민방위대", "라파예트의 흰 깃털이 돌아왔습니다. 재산 있는 시민들이 질서를 지킵니다.", ["gendarmerie"], [boost("mar_guard", {"stability_factor": 0.05})]),
])

more_focuses("LR_NAP_", "LR_route_napoleon", "내정", [
    ("prefects", "political_pressure", 0, 0, "도지사 제도", "파리가 임명한 도지사가 프랑스 전역을 하나로 묶습니다.", ["civil_code"], [boost("nap_prefects", {"stability_factor": 0.03, "political_power_gain": 0.03})]),
])
more_focuses("LR_NAP_", "LR_route_empire", "내정", [
    ("imperial_works", "construct_civilian", 0, 0, "제국 대공사", "개선문이 또 하나 올라가고, 그 뒤에는 공장이 들어섭니다.", ["imperial_university"], [civ(3), mil(2)]),
])
more_focuses("LR_NAP_", "LR_route_empire", "정치", [
    ("imperial_catechism", "propaganda", 0, 0, "제국 교리문답", "어린이들이 황제에 대한 의무를 외웁니다.", ["brother_kings"], [boost("nap_catechism", {"stability_factor": 0.05, "political_power_gain": 0.03})]),
])
more_focuses("LR_NAP_", "LR_route_empire", "외교", [
    ("sister_kingdoms", "major_alliance", 0, 0, "자매 왕국", "황제의 형제들이 유럽의 왕좌에 앉습니다. 조약문에는 동맹이라 적혀 있습니다.", ["marriage_diplomacy"], [boost("nap_sisters", {"political_power_gain": 0.05, "war_support_factor": 0.03})]),
])
more_focuses("LR_NAP_", "LR_route_empire", "안정도", [
    ("old_guard", "military_sphere", 0, 0, "노근위대", "황제와 함께 늙은 병사들이 제국의 마지막 예비대가 됩니다.", ["imperial_guard"], [boost("nap_old_guard", {"army_org_factor": 0.03, "army_morale_factor": 0.03})]),
])
more_focuses("LR_GUA_", "LR_route_guardian", "내정", [
    ("workers_compensation", "construct_civilian", 0, 0, "산업 재해 보상", "공화국이 공장의 다친 손까지 책임집니다.", ["social_insurance"], [civ(2), boost("gua_compensation", {"stability_factor": 0.03})]),
])
more_focuses("LR_GUA_", "LR_route_guardian", "정치", [
    ("republican_senate", "political_pressure", 0, 0, "공화국 상원", "대통령이 자기 권한을 스스로 나눕니다. 다음 대통령은 군인이 아닐지도 모릅니다.", ["constitution"], [boost("gua_senate", {"stability_factor": 0.05, "political_power_gain": 0.03})]),
])
more_focuses("LR_GUA_", "LR_route_guardian", "외교", [
    ("european_congress", "improve_relations", 0, 0, "유럽 공화주의자 회의", "빈 체제의 반대편에서 유럽의 공화주의자들이 파리에 모입니다.", ["league_of_republics"], [boost("gua_congress", {"political_power_gain": 0.05})]),
])
more_focuses("LR_GUA_", "LR_route_guardian", "안정도", [
    ("truth_commission", "national_unity", 0, 0, "진상 조사 위원회", "왕정과 혁명의 범죄를 함께 조사합니다. 양쪽 모두 불만이지만 총은 내려놓습니다.", ["national_reconciliation"], [boost("gua_truth", {"stability_factor": 0.05}), "lr_fra_op_reduce = yes"]),
])
# Each route's signature spirit and its focuses, and the two peace roads (route_signature.py).
import route_signature  # noqa: E402
SIG_FOCUS = set()
for _prefix, _route, _category, _rows in route_signature.ROWS:
    for _key, _icon, _name, _desc, _pre, _effects, *_extra in _rows:
        _opts = _extra[0] if _extra else {}
        focus(_prefix + _key, _icon, 0, 0, _name, _desc, *[boost("sig_" + _key, e) if isinstance(e, dict) else e for e in _effects],
              pre=[_prefix + q for q in _pre], route=_route, available=_opts.get("available"), me=[_prefix + q for q in _opts.get("me", ())])
        BY_ID_NEW.append((_prefix + _key, _category))
        SIG_FOCUS.add(_prefix + _key)
# The Algerian crisis: crush or abandon, a short road, then revolution or coup, and events settle the route.
X = "LR_CRI_"
WAIT_REVOLT = "custom_trigger_tooltip = {\n\ttooltip = LR_tt_wait_revolt\n\thas_country_flag = LR_algerian_revolt\n}"
WAIT_ELECTION = "custom_trigger_tooltip = {\n\ttooltip = LR_tt_wait_election\n\thas_country_flag = LR_election_parliament\n}"
# The crisis itself runs on dates: lr_france.1 asks the king, then events follow (mod/events/lr_france.txt).
CRISIS_FOCUSES = [item["id"] for item in FOCUSES if item["id"].startswith(X)]
# Every route can also plan a war on the rest of Europe, region by region, after the Rhine.
WAR_PLAN_FOCUSES = []

# Each route's story runs down its middle: one focus per chapter, and each fires its event.
SPINES = {}
for head, prefix, route, base, chapters in STORY:
    previous = head
    SPINES[head] = []
    for number, part in enumerate(chapters, start=1):
        fid = prefix + part["key"]
        focus(fid, part["icon"], 0, 0, part["name"], part["desc"],
              boost(f"story_{base + number}", part["reward"]),
              f"country_event = {{ id = lr_story.{base + number} days = 3 }}",
              pre=[previous], route=route)
        BY_ID_NEW.append((fid, "정치"))
        SPINES[head].append(fid)
        previous = fid
for prefix, route, head in WAR_PREFIXES:
    for plan in PLANS:
        fid = prefix + "plan_" + plan["key"]
        parent = prefix + "plan_" + plan["after"] if plan["after"] else head
        focus(fid, plan["icon"], 0, 0, plan["name"], plan["desc"], f"set_country_flag = LR_plan_{plan['key']}",
              f"country_event = {{ id = lr_story.{plan['event']} days = 1 }}", pre=[parent], route=route)
        BY_ID_NEW.append((fid, "영토확장"))
endings.add_epilogues(globals())
BY_ID = {item["id"]: item for item in FOCUSES}
for fid, category in BY_ID_NEW:
    BY_ID[fid]["filter"] = FILTERS[category]
for _fid in sorted(SIG_FOCUS):
    for _other in BY_ID[_fid]["me"]:
        BY_ID[_other]["me"] = list(BY_ID[_other]["me"]) + [_fid]
for fid in CRISIS_FOCUSES:
    BY_ID[fid]["filter"] = FILTERS["정치"]
# The fork in Napoleon's story comes after the last chapter of his trunk.
require("LR_NAP_before_the_crown", "has_completed_focus = LR_NAP_concordat\nhas_completed_focus = LR_NAP_legion_of_honour")
BY_ID["LR_NAP_coronation"]["pre"] = ["LR_NAP_before_the_crown"]
BY_ID["LR_NAP_guardian"]["pre"] = ["LR_NAP_before_the_crown"]
# The oath is part of the president's story, so his branches can open on both sides of it.
SPINES["LR_NAP_guardian"].insert(0, "LR_GUA_oath")
SPINES["LR_NAP_red"].insert(0, "LR_RED_tribune")
# Part two waits for the war.
for _fid, _gate in part_two.GATES.items():
    require(_fid, _gate)
BY_ID["LR_RED_souper"]["pre"] = ["LR_RED_tribune"]
BY_ID["LR_GUA_first_address"]["pre"] = ["LR_GUA_oath"]

# ===== Claims: the lands the old automatic settlement took (Europe only) are now won at the peace conference =====
# Each chunk is claimed by the focus that opens its war, on the routes whose settlement used to take it.
import victory as _victory  # noqa: E402
CLAIM_CHUNKS = {  # chunk: (focus suffix, states, the name the tooltip shows)
    "left_bank": ("rhine", _victory.LEFT_BANK + _victory.HANSE, "라인강 서안과 브레멘"),
    "low": ("plan_low", _victory.BENELUX + _victory.NETHERLANDS + _victory.JURA + _victory.VALAIS, "베네룩스와 쥐라, 발레"),
    "italy": ("plan_italy", _victory.SARDINIA + _victory.ROME_TUSCANY, "사르데냐 왕국과 로마, 토스카나"),
    "iberia": ("plan_iberia", _victory.CATALONIA, "카탈루냐"),
    "illyria": ("danube", _victory.ILLYRIA, "일리리아"),
}
# Savoy and Nice, which the first republic annexed in 1792 (state 735 and the pieces cut from it).
SAVOY_NICE = _victory._expand([735])
CLAIM_NAMES = {  # the tooltip's name for a claim that is not a whole chunk
    tuple(sorted(set(SAVOY_NICE))): "사부아와 니스",
    tuple(sorted(set(_victory.SARDINIA))): "사르데냐 왕국 (사부아·니스·피에몬테·리구리아·사르데냐섬)",
    tuple(sorted(set(_victory.BENELUX + _victory.JURA))): "베네룩스와 쥐라",
    tuple(sorted(set(_victory.LEFT_BANK))): "라인강 서안",
}
# Two measures of France. The First Empire at its height (1812, the departments Paris ruled itself, not the
# satellites): the Rhine and the Hanseatic north to Lübeck, the Low Countries, Geneva and the Valais, Piedmont, Liguria,
# Parma, Tuscany, Rome and Umbria, the Illyrian provinces and Catalonia. And France as it stood in 1936, with Belgium,
# the left bank of the Rhine, Savoy, Nice and Upper Savoy.
_E = _victory._expand
BELGIUM = _E([6, 34, 977, 980])
EMPIRE_NORTH = _E(_victory.LEFT_BANK + [56, 57, 58, 59])           # Moselle, Rhineland; Weser-Ems, Westphalia, Hanover, Holstein
EMPIRE_LOW = _E([6, 8, 34, 977, 980] + _victory.NETHERLANDS + [845, 847])  # Belgium, Luxembourg, Holland; Jura (Geneva), Valais
EMPIRE_ITALY = _E([735, 158, 162, 2, 1110, 1114])                  # Savoy-Nice, Piedmont-Liguria, Tuscany, Lazio, Umbria, Parma
EMPIRE_ILLYRIA = _E(_victory.ILLYRIA + [736])                      # and Trieste and Gorizia
FRANCE_1936 = _E(_victory.FRANCE_1936)
EMPIRE = {"left_bank": FRANCE_1936 + EMPIRE_NORTH, "low": EMPIRE_LOW, "italy": EMPIRE_ITALY,
          "iberia": _E(_victory.CATALONIA), "illyria": EMPIRE_ILLYRIA}
FRANCE_OF_1936 = {"left_bank": FRANCE_1936 + _E(_victory.LEFT_BANK), "low": BELGIUM, "italy": SAVOY_NICE}
CLAIM_CHUNKS["left_bank"] = ("rhine", EMPIRE["left_bank"], "제1제국의 북부 (라인강 서안, 한자 도시들, 베스트팔렌, 하노버)")
CLAIM_CHUNKS["low"] = ("plan_low", EMPIRE_LOW, "저지대와 제네바, 발레")
CLAIM_CHUNKS["italy"] = ("plan_italy", EMPIRE_ITALY, "사부아·니스·피에몬테·리구리아·파르마·토스카나·로마")
CLAIM_CHUNKS["illyria"] = ("danube", EMPIRE_ILLYRIA, "일리리아와 트리에스테")
CLAIM_NAMES[tuple(sorted(set(FRANCE_OF_1936["left_bank"])))] = "1936년의 프랑스 본토와 라인강 서안"
CLAIM_NAMES[tuple(sorted(set(BELGIUM)))] = "벨기에"
CLAIM_ROUTES = {  # route prefix: the lands its focuses claim
    "LR_NAP_": EMPIRE, "LR_GUA_": EMPIRE, "LR_RED_": EMPIRE, "LR_ORL_": EMPIRE,  # Napoleon's France, and Orléans as much
    **{p: FRANCE_OF_1936 for p in ("LR_BOU_", "LR_JAC_", "LR_GIR_", "LR_MAR_", "LR_COM_", "LR_ANA_", "LR_PET_")},
}
# A route without the focus a chunk belongs to claims it with the next of these it has.
CLAIM_FALLBACK = ["plan_italy", "rhine", "plan_low", "danube"]
CLAIM_LOC = []
for _prefix, _chunks in CLAIM_ROUTES.items():
    for _chunk, _states in _chunks.items():
        _suffix, _, _name = CLAIM_CHUNKS[_chunk]
        _fid = next((_prefix + s for s in [_suffix] + CLAIM_FALLBACK if _prefix + s in BY_ID), None)
        if _fid is None:
            raise SystemExit(f"{_prefix}: no focus to carry the claims on {_name}")
        _tip = f"LR_tt_claims_{_prefix[3:6].lower()}_{_chunk}"
        _limit = " ".join(f"state = {_s}" for _s in sorted(set(_states)))
        BY_ID[_fid]["effects"] = tuple(BY_ID[_fid]["effects"]) + (
            f"custom_effect_tooltip = {_tip}\nhidden_effect = {{\n\tevery_state = {{\n\t\tlimit = {{\n\t\t\tOR = {{ {_limit} }}\n"
            "\t\t\tNOT = { is_core_of = ROOT }\n\t\t\tNOT = { is_owned_by = ROOT }\n\t\t}\n\t\tadd_claim_by = ROOT\n\t}\n}",)
        _named = _name if _states == CLAIM_CHUNKS[_chunk][1] else CLAIM_NAMES.get(tuple(sorted(set(_states))), _name)
        CLAIM_LOC.append(f' {_tip}:0 "§Y{_named}§!에 영유권을 주장합니다. 평화 회의에서 이 땅을 요구하기가 쉬워집니다."')

# ===== Algeria as part of France: every route can make the départements of Algeria French core land =====
# After the route's Algeria focus where it has one (the campaign that ends the rebellion), else after its first focus;
# open once the rebellion is over and France holds Algiers.
ALGERIA_AFTER = {
    "LR_ORL_": ["LR_ORL_algeria"], "LR_BOU_": ["LR_BOU_algeria"], "LR_GIR_": ["LR_GIR_algeria"],
    "LR_MAR_": ["LR_MAR_algeria"], "LR_PET_": ["LR_PET_algeria"], "LR_JAC_": ["LR_JAC_reclaim_algeria"],
    "LR_COM_": [("LR_COM_annex_algeria", "LR_COM_algerian_comrades")], "LR_ANA_": ["LR_ANA_algerian_freedom"],
    "LR_NAP_": ["LR_NAP_algiers_return"], "LR_GUA_": ["LR_GUA_oath"], "LR_RED_": ["LR_RED_tribune"],
}
_algeria_limit = "OR = { " + " ".join(f"state = {s}" for s in algeria.STATES) + " }"
for _prefix, _pre in ALGERIA_AFTER.items():
    _first = _pre[0][0] if isinstance(_pre[0], tuple) else _pre[0]
    _fid = _prefix + "algeria_departments"
    focus(_fid, "national_unity", 0, 0, "알제리 데파르트망",
          "알제는 식민지가 아니라 프랑스의 데파르트망입니다. 지중해 건너의 세 데파르트망을 본토와 똑같은 프랑스의 땅으로 선포합니다.",
          "custom_effect_tooltip = LR_tt_algeria_departments",
          f"hidden_effect = {{\n\tevery_state = {{\n\t\tlimit = {{\n\t\t\t{_algeria_limit}\n\t\t\tis_owned_by = ROOT\n\t\t}}\n\t\tadd_core_of = ROOT\n\t}}\n}}",
          stab(0.05), pre=_pre, route=BY_ID[_first]["route"],
          available=("custom_trigger_tooltip = {\n\ttooltip = LR_tt_algeria_settled\n\tNOT = { has_country_flag = LR_algeria_dmz }\n"
                     "\tNOT = { has_country_flag = LR_algeria_campaign }\n}\n459 = { is_owned_by = ROOT }"))
    BY_ID[_fid] = FOCUSES[-1]
    BY_ID[_fid]["filter"] = FILTERS["영토확장"]
CLAIM_LOC += [' LR_tt_algeria_departments:0 "프랑스가 가진 §Y알제리§!의 모든 주가 §Y프랑스의 핵심주§!가 됩니다."',
              ' LR_tt_algeria_settled:0 "알제리의 반란이 끝났고 프랑스가 알제를 가지고 있습니다."']

for item in FOCUSES:
    if item["route"] and item.get("filter") in ROUTE_ORDER:
        item["rank"] = ROUTE_ORDER[item["filter"]]

# ===== Fixed spirits: focuses strengthen them, or weaken the debuff =====
LABELS = {
    "air_accidents_factor": "항공 사고", "air_ace_generation_chance_factor": "에이스 출현", "air_detection": "항공 탐지",
    "air_doctrine_cost_factor": "공군 교리 비용", "air_mission_efficiency": "항공 임무 효율", "air_superiority_efficiency": "제공권 효율",
    "air_training_xp_gain_factor": "항공 훈련 경험", "army_attack_factor": "육군 공격력", "army_defence_factor": "육군 방어력",
    "army_morale_factor": "육군 사기", "army_org_factor": "육군 조직력", "communism_drift": "사회주의 지지",
    "conscription_factor": "징집 인구", "consumer_goods_factor": "소비재 공장", "convoy_escort_efficiency": "호송 효율",
    "democratic_drift": "의회정 지지", "experience_gain_army_factor": "육군 경험치", "fascism_drift": "독재정 지지",
    "industrial_capacity_factory": "공장 생산량", "land_reinforce_rate": "증원율", "max_planning": "최대 계획",
    "naval_coordination": "해군 협동", "naval_doctrine_cost_factor": "해군 교리 비용", "naval_invasion_prep_speed": "상륙 준비",
    "naval_morale_factor": "해군 사기", "navy_max_range_factor": "함대 작전 반경", "navy_org_factor": "해군 조직력",
    "out_of_supply_factor": "보급 부족 페널티", "planning_speed": "계획 속도", "political_power_gain": "정치력",
    "production_factory_max_efficiency_factor": "최대 생산 효율", "production_lack_of_resource_penalty_factor": "자원 부족 페널티",
    "production_speed_buildings_factor": "건설 속도", "send_volunteer_divisions_required": "의용군 필요 사단", "send_volunteer_size": "의용군 규모",
    "research_speed_factor": "연구 속도", "army_infantry_attack_factor": "보병 공격력", "army_artillery_attack_factor": "포병 공격력", "army_armor_attack_factor": "기갑 공격력", "army_armor_defence_factor": "기갑 방어력", "breakthrough_factor": "돌파", "dig_in_speed_factor": "참호 구축 속도", "army_core_defence_factor": "중핵 영토 방어", "special_forces_attack_factor": "특수부대 공격력", "navy_capital_ship_attack_factor": "주력함 공격력", "navy_capital_ship_defence_factor": "주력함 방어력", "navy_screen_attack_factor": "호위함 공격력", "navy_submarine_attack_factor": "잠수함 공격력", "convoy_raiding_efficiency_factor": "통상 파괴 효율", "navy_carrier_air_attack_factor": "함재기 공격력", "navy_carrier_air_targetting_factor": "함재기 표적 획득", "production_factory_efficiency_gain_factor": "생산 효율 증가", "stability_factor": "안정도", "supply_consumption_factor": "보급 소모", "training_time_factor": "훈련 시간", "war_support_factor": "전쟁 지지",
}
SPIRITS = {  # line: variable prefix, display name, picture.
    "economy": ("LR_eco_", "프랑스 경제", "generic_license_production"),
    "army": ("LR_arm_", "프랑스 육군", "generic_army_war_college"),
    "navy": ("LR_nav_", "프랑스 해군", "generic_navy_bonus"),
    "air": ("LR_air_", "프랑스 공군", "generic_air_bonus"),
    "society": ("LR_soc_", "사회 정책", "generic_local_self_management"),
    # Balance (playtest, 2026-11): combat power, spread over several spirits instead of one.
    "army_fire": ("LR_af_", "보병과 포병", "generic_artillery_regiments"),
    "army_armour": ("LR_am_", "기갑과 기동", "generic_armor"),
    "army_staff": ("LR_as_", "참모본부", "generic_army_war_college"),
    "army_supply": ("LR_au_", "보급과 방어", "generic_supply_line"),
    "army_elite": ("LR_ae_", "정예 부대", "generic_infantry_bonus"),
    "navy_line": ("LR_nl_", "주력 함대", "generic_sea_focused_navy"),
    "navy_light": ("LR_ns_", "경함대와 잠수함", "generic_navy_submarines"),
    "navy_air": ("LR_na_", "해군 항공대", "generic_navy_carrier_bonus"),
}
# Which combat spirit each army and navy focus strengthens, and by how much per focus.
SUBLINE = {
    "LR_FRA_infantry_rearm": "army_fire", "LR_FRA_artillery_school": "army_fire", "LR_FRA_heavy_artillery": "army_fire",
    "LR_FRA_rifle_stocks": "army_fire", "LR_FRA_combat_engineers": "army_fire",
    "LR_FRA_mobile_war": "army_armour", "LR_FRA_tank_divisions": "army_armour", "LR_FRA_char_b": "army_armour",
    "LR_FRA_armoured_recon": "army_armour", "LR_FRA_degaulle_school": "army_armour",
    "LR_FRA_lessons_of_defeat": "army_staff", "LR_FRA_general_staff": "army_staff", "LR_FRA_radio_net": "army_staff",
    "LR_FRA_revenge_army": "army_staff", "LR_FRA_ready_for_war": "army_staff", "LR_FRA_staff_college": "army_staff",
    "LR_FRA_petain_school": "army_supply", "LR_FRA_motorisation": "army_supply", "LR_FRA_general_mobilisation": "army_supply",
    "LR_FRA_saint_cyr": "army_elite", "LR_FRA_foreign_legion": "army_elite", "LR_FRA_colonial_regiments": "army_elite",
    "LR_FRA_chasseurs_alpins": "army_elite",
    "LR_FRA_new_navy": "navy_line", "LR_FRA_fleet_doctrine": "navy_line", "LR_FRA_battleline": "navy_line", "LR_FRA_mers_el_kebir": "navy_line",
    "LR_FRA_submarine_arm": "navy_light", "LR_FRA_cruiser_squadron": "navy_light", "LR_FRA_destroyer_flotillas": "navy_light",
    "LR_FRA_commerce_raiding": "navy_light", "LR_FRA_convoy_school": "navy_light",
    "LR_FRA_bearn_carrier": "navy_air", "LR_FRA_naval_aviation": "navy_air",
}
# A full branch of five focuses adds about +20-25% to its main stat: enough to wipe out the disarmament penalty
# (-20% attack) and end clearly ahead, without the +50% that 10% a focus would give.
SUB_BONUS = {
    "army_fire": {"army_attack_factor": 0.03, "army_infantry_attack_factor": 0.04, "army_artillery_attack_factor": 0.05},
    "army_armour": {"army_armor_attack_factor": 0.05, "army_armor_defence_factor": 0.03, "breakthrough_factor": 0.04},
    "army_staff": {"army_org_factor": 0.04, "planning_speed": 0.05, "max_planning": 0.03, "army_defence_factor": 0.02},
    "army_supply": {"supply_consumption_factor": -0.05, "out_of_supply_factor": -0.06, "army_defence_factor": 0.04, "dig_in_speed_factor": 0.08},
    "army_elite": {"army_morale_factor": 0.04, "experience_gain_army_factor": 0.06, "special_forces_attack_factor": 0.05, "army_core_defence_factor": 0.03},
    "navy_line": {"navy_capital_ship_attack_factor": 0.06, "navy_capital_ship_defence_factor": 0.05},
    "navy_light": {"navy_screen_attack_factor": 0.05, "navy_submarine_attack_factor": 0.05, "convoy_raiding_efficiency_factor": 0.05},
    "navy_air": {"navy_carrier_air_attack_factor": 0.08, "navy_carrier_air_targetting_factor": 0.08},
}
REGIMES = {  # name, base modifiers.
    "provisional": ("임시 정부", {"stability_factor": -0.05}),
    "orleans": ("오를레앙 왕정", {"war_support_factor": 0.1}),
    "bourbon": ("부르봉 왕정", {"stability_factor": 0.05}),
    "communist": ("프랑스 코뮌", {"war_support_factor": 0.05}),
    "jacobin": ("산악파 정부", {"stability_factor": 0.05}),
    "girondin": ("지롱드 정부", {"political_power_gain": 0.1}),
    "marais": ("푀양파 정부", {"stability_factor": 0.05}),
    "napoleon": ("통령 정부", {"war_support_factor": 0.1}),
    "empire": ("프랑스 제국", {"war_support_factor": 0.1}),
    "guardian": ("공화국의 수호자", {"stability_factor": 0.05}),
    **new_routes.REGIMES,
}
RULERS = {  # name, picture, base modifiers.
    "louis": ("국왕 루이 20세", "generic_king_handled", {"stability_factor": 0.05, "political_power_gain": 0.05, "war_support_factor": -0.05}),
    "orleans": ("국왕 장 드 오를레앙", "generic_king_handled", {"war_support_factor": 0.1, "army_morale_factor": 0.03, "stability_factor": -0.03}),
    "constitutional": ("입헌 국왕", "generic_king_handled", {"stability_factor": 0.12, "political_power_gain": 0.03, "democratic_drift": 0.02}),
    "emperor": ("황제 나폴레옹", "generic_king_handled", {"political_power_gain": 0.15, "war_support_factor": 0.1, "stability_factor": 0.05, "army_morale_factor": 0.05}),
    "president": ("대통령 나폴레옹", "generic_constitutional_guarantees", {"political_power_gain": 0.1, "stability_factor": 0.1, "democratic_drift": 0.02}),
    "petain": ("국가원수 페탱", "generic_fortify_the_borders", {"stability_factor": 0.08, "army_defence_factor": 0.05, "war_support_factor": -0.03}),
    "red": new_routes.red.RULER,
}
RULER_KEYS = sorted({key for _, _, values in RULERS.values() for key in values})
RULER_BOOST = {"LR_FRA_king_restored": {"stability_factor": 0.07},
               "LR_FRA_king_crowned": {"stability_factor": 0.05, "political_power_gain": 0.05, "war_support_factor": 0.03},
               "LR_FRA_king_parliament": {"stability_factor": 0.05, "political_power_gain": 0.03}}
DISARMED = {"army_attack_factor": (-0.2, 0.01), "army_defence_factor": (-0.1, 0.005), "army_org_factor": (-0.1, 0.005), "training_time_factor": (0.2, -0.01)}
# Treaty-breaking focuses lift more; every other military focus lifts one or two steps.
RELIEF_EXTRA = {"LR_ORL_tear_up_treaty": 5, "LR_ORL_radical_rearm": 3, "LR_ORL_calais": 2, "LR_BOU_open_rearm": 4, "LR_BOU_diplomatic_rearm": 2,
                "LR_COM_peoples_army": 3, "LR_JAC_republican_army": 3, "LR_NAP_grande_armee": 4, "LR_GUA_citizen_army": 3,
                "LR_PET_hidden_sword": 3, "LR_ANA_militarisation": 3, "LR_RED_red_grande_armee": 4}
RELIEF_BY_LINE = {"army": 2, "navy": 1, "air": 1}
# Three reforms lift the disarmament penalties: weapons lift the attack penalty, command lifts
# organisation and defence, the officer corps lifts training time. Each runs from 0 to 100.
REFORM_VARS = {"tech": "LR_tech_index", "command": "LR_cmd_index", "officers": "LR_off_index"}
REFORM_NAMES = {"tech": "기술혁신", "command": "지휘체계 개편", "officers": "장교단 육성"}
REFORM_OF = {  # Focuses whose reform is not obvious from their effects.
    "LR_FRA_lessons_of_defeat": "command", "LR_FRA_general_staff": "command", "LR_FRA_staff_college": "officers",
    "LR_FRA_radio_net": "command", "LR_FRA_saint_cyr": "officers", "LR_FRA_revenge_army": "command",
    "LR_FRA_ready_for_war": "command", "LR_FRA_petain_school": "command", "LR_FRA_degaulle_school": "command",
    "LR_FRA_foreign_legion": "officers", "LR_FRA_general_mobilisation": "command", "LR_FRA_air_doctrine": "command",
    "LR_FRA_fleet_doctrine": "command",
}
# Points a military focus adds to its reform directly: an army focus counts double. Most of the reform now
# comes from the reform council (build_minigames.py): each military focus also gives reform drive, which the
# council spends on exercises that raise the indices.
REFORM_POINTS = {"army": 4, "navy": 2, "air": 2}
REFORM_DRIVE = {"army": 1, "navy": 1, "air": 1}


def reform_gains(item, line):
    """Which reform a focus advances, and by how much. The treaty-breaking focuses advance all three."""
    gains = {}
    if line in REFORM_POINTS:
        text = "\n".join(str(e) for e in item["effects"])
        kind = REFORM_OF.get(item["id"]) or ("tech" if "add_tech_bonus" in text else "officers" if "experience" in text or "create_unit" in text else "command")
        gains[kind] = REFORM_POINTS[line]
    if item["id"] in RELIEF_EXTRA:
        for kind in REFORM_VARS:
            gains[kind] = gains.get(kind, 0) + RELIEF_EXTRA[item["id"]] * 5
    return gains
RULER_SET = {"LR_FRA_king_constitutional": "constitutional", "LR_FRA_emperor": "emperor", "LR_FRA_president": "president"}
DEFEAT = {"stability_factor": -0.1, "political_power_gain": -0.1, "war_support_factor": 0.1}
HEALERS = {"LR_FRA_war_reparations", "LR_FRA_stabilise_franc", "LR_FRA_lessons_of_defeat", "LR_FRA_trade_treaties",
           "LR_ORL_duke", "LR_BOU_restored", "LR_COM_commune", "LR_JAC_committee", "LR_GIR_cabinet", "LR_MAR_cabinet", "LR_NAP_first_consul",
           "LR_ORL_uproot", "LR_BOU_uproot", "LR_COM_uproot", "LR_JAC_uproot", "LR_GIR_uproot", "LR_MAR_uproot",
           "LR_PET_marshal", "LR_ANA_federation", "LR_PET_uproot", "LR_ANA_uproot"}
FILTER_LINE = {"FOCUS_FILTER_INDUSTRY": "economy", "FOCUS_FILTER_ARMY_XP": "army", "FOCUS_FILTER_NAVY_XP": "navy", "FOCUS_FILTER_AIR_XP": "air"}
SOURCES = {row[0]: row[4] for row in IDEAS}
IDEAS[:] = []
LINE_KEYS = {line: set() for line in SPIRITS}
REGIME_KEYS = set(k for _, values in REGIMES.values() for k in values)
SIG_KEYS = set()
SPIRIT_LOC = []


def line_of(item):
    if item["id"] in SIG_FOCUS:
        return "sig"
    if item["route"]:
        if item.get("filter") == "FOCUS_FILTER_INTERNAL_AFFAIRS":
            return "society"
        return "regime"
    return FILTER_LINE.get(item.get("filter"), "economy")


def regime_of(item):
    return item["route"].removeprefix("LR_route_")


def shown(key, value):
    if key == "send_volunteer_size":
        return f"{LABELS[key]} {value:+g}"
    return f"{LABELS[key]} {round(value * 100):+d}%"


def apply_line(prefix, deltas, modifier):
    moves = "\n".join(f"\tadd_to_variable = {{ {prefix}{key} = {round(value, 3):g} }}" for key, value in sorted(deltas.items()))
    return moves, modifier


# Balance (playtest, 2026-11): stability and war support came too easily, armies and industry too slowly.
CALM_SCALE = 0.5  # Stability and war support from focuses count half.
# Equipment no longer arrives in crates: each grant becomes better factories instead.
EQUIPMENT_AS = {"production_factory_efficiency_gain_factor": 0.04, "production_factory_max_efficiency_factor": 0.02}
# What every military or economic focus adds to its line's spirit, besides its own reward.
LINE_EXTRA = {
    "economy": {"industrial_capacity_factory": 0.02, "production_speed_buildings_factor": 0.02},
    "navy": {"navy_org_factor": 0.02, "naval_morale_factor": 0.03},
    "air": {"air_superiority_efficiency": 0.03, "air_mission_efficiency": 0.02},
}
REFORM_EXTRA = {  # army focuses, by the reform they advance; combat bonuses now live in SUB_BONUS
    "tech": {"production_factory_max_efficiency_factor": 0.01},
    "command": {},
    "officers": {},
}
LOWER_IS_BETTER = {"consumer_goods_factor", "training_time_factor", "production_lack_of_resource_penalty_factor", "supply_consumption_factor",
                   "air_accidents_factor", "out_of_supply_factor", "send_volunteer_divisions_required", "air_doctrine_cost_factor", "naval_doctrine_cost_factor"}
# What one reform point lifts from the disarmament penalties (see build_systems.DISARM_FROM).
REFORM_LIFT = {"tech": [("육군 공격력", 0.002)], "command": [("육군 조직력", 0.001), ("육군 방어력", 0.001)], "officers": [("훈련 시간", -0.002)]}


def effect_line(key, value):
    """One modifier the way vanilla prints it under a national spirit: name, then the value coloured good or bad."""
    good = (value < 0) if key in LOWER_IS_BETTER else (value > 0)
    colour = "G" if good else "R"
    amount = f"{value:+g}" if key == "send_volunteer_size" else f"{round(value * 100, 1):+g}%"
    return f"\\n  {LABELS[key]}: §{colour}{amount}§!"


def convert_to_spirits():
    for item in FOCUSES:
        if item["id"].startswith("LR_CRI_"):
            continue  # The crisis has one-off effects: no standing spirit exists yet to strengthen.
        changes, ruler, kept = {}, {}, []
        for effect in item["effects"]:
            text = str(effect)
            word, _, value = text.partition(" = ")
            line = line_of(item)
            if word == "add_ideas" and value in SOURCES:
                for key, amount in SOURCES[value].items():
                    changes[key] = changes.get(key, 0) + amount
            elif word == "remove_ideas" and value in SOURCES:
                for key, amount in SOURCES[value].items():
                    changes[key] = changes.get(key, 0) - amount
            elif word == "add_ideas" and value in RULER_BOOST:
                ruler.update(RULER_BOOST[value])
            elif word == "add_ideas" and value in RULER_SET:
                kept.append(f"custom_effect_tooltip = LR_tt_ruler_{RULER_SET[value]}")
                kept.append(f"hidden_effect = {{ lr_fra_ruler_{RULER_SET[value]} = yes }}")
            elif word == "remove_ideas" and value == "LR_FRA_defeat":
                kept.append("custom_effect_tooltip = LR_tt_defeat_end")
                kept.append("hidden_effect = { lr_fra_defeat_end = yes }")
            elif word == "remove_ideas" and value.startswith(("LR_FRA_king", "LR_idea_nap_first_consul")):
                continue
            elif word == "add_stability" and item["id"] != ROOT:
                changes["stability_factor"] = changes.get("stability_factor", 0) + float(value)
            elif word == "add_war_support" and item["id"] != ROOT:
                changes["war_support_factor"] = changes.get("war_support_factor", 0) + float(value)
            elif text.startswith("add_equipment_to_stockpile"):
                for key, amount in EQUIPMENT_AS.items():
                    changes[key] = changes.get(key, 0) + amount
            elif word == "add_political_power" and item["id"] != ROOT:
                changes["political_power_gain"] = changes.get("political_power_gain", 0) + max(round(float(value) / 1500, 2), 0.01)
            else:
                kept.append(effect)
        for key in ("stability_factor", "war_support_factor"):
            if key in changes and changes[key] > 0:
                changes[key] = round(changes[key] * CALM_SCALE, 3)
        line = line_of(item)
        if item["id"] != ROOT:
            for key, amount in LINE_EXTRA.get(line, {}).items():
                changes[key] = changes.get(key, 0) + amount
            if line == "army":
                for kind in reform_gains(item, line):
                    for key, amount in REFORM_EXTRA[kind].items():
                        changes[key] = changes.get(key, 0) + amount
        changes = {k: v for k, v in changes.items() if abs(v) > 1e-9}
        tips, hidden = [], []
        if changes:
            line = line_of(item)
            if line == "regime":
                regime = regime_of(item)
                name = REGIMES[regime][0]
                prefix = "LR_reg_"
                REGIME_KEYS.update(changes)
                guard = ""
            elif line == "sig":
                regime = regime_of(item)
                name = route_signature.SIGNATURE[regime][0]
                prefix = "LR_sig_"
                SIG_KEYS.update(changes)
                guard = (f"\tif = {{\n\t\tlimit = {{ NOT = {{ has_dynamic_modifier = {{ modifier = LR_dyn_sig_{regime} }} }} }}\n"
                         f"\t\tadd_dynamic_modifier = {{ modifier = LR_dyn_sig_{regime} }}\n\t}}\n")
            else:
                prefix, name, _ = SPIRITS[line]
                LINE_KEYS[line].update(changes)
                guard = f"\tif = {{\n\t\tlimit = {{ NOT = {{ has_dynamic_modifier = {{ modifier = LR_dyn_{line} }} }} }}\n\t\tadd_dynamic_modifier = {{ modifier = LR_dyn_{line} }}\n\t}}\n"
            tips.append(f"국민정신 §Y{name}§!에 효과가 추가됩니다:" + "".join(effect_line(k, v) for k, v in sorted(changes.items())))
            hidden.append(guard + "\n".join(f"\tadd_to_variable = {{ {prefix}{k} = {round(v, 3):g} }}" for k, v in sorted(changes.items())))
        sub_line = SUBLINE.get(item["id"])
        if sub_line:
            sub_prefix, sub_name, _ = SPIRITS[sub_line]
            bonus = SUB_BONUS[sub_line]
            LINE_KEYS[sub_line].update(bonus)
            tips.append(f"국민정신 §Y{sub_name}§!에 효과가 추가됩니다:" + "".join(effect_line(k, v) for k, v in sorted(bonus.items())))
            hidden.append(f"\tif = {{\n\t\tlimit = {{ NOT = {{ has_dynamic_modifier = {{ modifier = LR_dyn_{sub_line} }} }} }}\n\t\tadd_dynamic_modifier = {{ modifier = LR_dyn_{sub_line} }}\n\t}}\n"
                          + "\n".join(f"\tadd_to_variable = {{ {sub_prefix}{k} = {v:g} }}" for k, v in sorted(bonus.items())))
        if ruler:
            tips.append("국민정신 §Y통치자§!에 효과가 추가됩니다:" + "".join(effect_line(k, v) for k, v in sorted(ruler.items())))
            hidden.append("\n".join(f"\tadd_to_variable = {{ LR_rul_{k} = {v:g} }}" for k, v in sorted(ruler.items())))
        if item["id"] in HEALERS:
            tips.append("국민정신 §R대전쟁의 굴욕§!의 페널티가 줄어듭니다:\\n  안정도: §G+2%§!\\n  정치력: §G+2%§!")
            hidden.append("\tlr_fra_heal_defeat = yes")
        line = line_of(item)
        rebuilt = 1.5 if line == "economy" and item["id"] != ROOT else 1 if line == "society" else 0
        funds = FOCUS_FUNDS.get(line, 0) if item["id"] != ROOT else 0
        if funds:
            tips.append(f"§Y자금§! +{funds}")
            hidden.append(f"\tadd_to_variable = {{ LR_funds = {funds} }}")
        if rebuilt:
            tips.append(f"§G경제 재건§! +{rebuilt:g}")
            hidden.append(f"\tadd_to_variable = {{ LR_rec_focus = {rebuilt:g} }}\n\tlr_fra_sync_industry = yes")
        gains = reform_gains(item, line)
        drive = REFORM_DRIVE.get(line, 0)
        if gains or drive:
            # One header line for the reform, then the penalty it lifts.
            parts = [f"{REFORM_NAMES[k]} §G+{v:g}§!" for k, v in gains.items()] + ([f"개혁 동력 §G+{drive}§!"] if drive else [])
            tips.append("§Y군사 개혁§!: " + ", ".join(parts))
        if gains:
            lifts = {}
            for kind, points in gains.items():
                for label, per in REFORM_LIFT[kind]:
                    lifts[label] = lifts.get(label, 0) + points * per
            tips.append("국민정신 §R버려진 군대§!의 페널티가 줄어듭니다:"
                        + "".join(f"\\n  {label}: §G{round(v * 100, 1):+g}%§!" for label, v in lifts.items()))
            hidden.append("\n".join(f"\tadd_to_variable = {{ {REFORM_VARS[k]} = {v:g} }}" for k, v in gains.items()) + "\n\tlr_fra_sync_reform = yes")
        if drive:
            hidden.append(f"\tadd_to_variable = {{ LR_reform_drive = {drive} }}")
        works = sum(1.5 if "lr_fra_lay_rail" in str(e) else 1 if "lr_fra_road_works" in str(e) else 0 for e in item["effects"])
        if works:
            tips.append(f"§G철도·도로 공사§!: 경제 재건 +{works:g}")
        if tips:
            key = "LR_tt_s_" + item["id"]
            SPIRIT_LOC.append(f' {key}:0 "' + "\\n".join(tips) + '"')
            kept.append(f"custom_effect_tooltip = {key}")
            kept.append("hidden_effect = {\n" + "\n".join(hidden) + "\n\tforce_update_dynamic_modifier = yes\n}")
        item["effects"] = tuple(kept)


add_effects("LR_NAP_coronation", "hidden_effect = { lr_fra_regime_empire = yes }", "news_event = { id = lr_gnews.6 days = 1 }")


def lay_down(mtg_type, version, legacy_type, progresses):
    """Ships put on the slipways, half built: the Man the Guns design if it is there, the old hull if not."""
    def order(kind, name, progress):
        named = f'\n\t\tversion_name = "{name}"' if name else ""
        return (f"add_equipment_production = {{\n\tequipment = {{\n\t\ttype = {kind}\n\t\tcreator = \"FRA\"{named}\n\t}}\n"
                f"\trequested_factories = 1\n\tprogress = {progress}\n\tamount = 1\n}}")
    mtg = "\n".join(order(mtg_type, version, p) for p in progresses)
    legacy = "\n".join(order(legacy_type, None, p) for p in progresses)
    indent_ = lambda s: "\n".join("\t" + line for line in s.split("\n"))
    return f"if = {{\n\tlimit = {{ has_dlc = \"Man the Guns\" }}\n{indent_(mtg)}\n}}\nelse = {{\n{indent_(legacy)}\n}}"


SHIPYARD = {
    "LR_FRA_battleline": lay_down("ship_hull_heavy_2", "Richelieu Class", "battleship_2", (0.4, 0.25)),
    "LR_FRA_bearn_carrier": lay_down("ship_hull_carrier_1", "Joffre Class", "carrier_1", (0.4,)),
    "LR_FRA_naval_aviation": lay_down("ship_hull_carrier_1", "Joffre Class", "carrier_1", (0.25,)),
}
for _fid, _effect in SHIPYARD.items():
    add_effects(_fid, _effect)


# ===== Variety: tangible rewards, real choices, links between branches, events along them =====
for fid, effects in REWARDS.items():
    add_effects(fid, *effects)
# Synergies that used to hand out crates of equipment now raise the army's production efficiency instead.
SYNERGY_EQUIPMENT = ("custom_effect_tooltip = LR_tt_synergy_production\nhidden_effect = {\n"
                     "\tif = {\n\t\tlimit = { NOT = { has_dynamic_modifier = { modifier = LR_dyn_army } } }\n\t\tadd_dynamic_modifier = { modifier = LR_dyn_army }\n\t}\n"
                     "\tadd_to_variable = { LR_arm_production_factory_efficiency_gain_factor = 0.03 }\n"
                     "\tadd_to_variable = { LR_arm_production_factory_max_efficiency_factor = 0.01 }\n\tforce_update_dynamic_modifier = yes\n}")
LINE_KEYS["army"].update({"production_factory_efficiency_gain_factor": 0, "production_factory_max_efficiency_factor": 0})
SPIRIT_LOC.append(' LR_tt_synergy_production:0 "국민정신 §Y프랑스 육군§!에 효과가 추가됩니다:\\n  생산 효율 증가: §G+3%§!\\n  최대 생산 효율: §G+1%§!"')
for fid, (other, effects) in SYNERGY.items():
    effects = [SYNERGY_EQUIPMENT if str(e).startswith("add_equipment_to_stockpile") else e for e in effects]
    add_effects(fid, f"if = {{\n\tlimit = {{ has_completed_focus = {other} }}\n" + "\n".join("\t" + line for e in effects for line in e.split("\n")) + "\n}")
for first, second in EXCLUSIVE:
    BY_ID[first]["me"] = tuple(BY_ID[first]["me"]) + (second,)
    BY_ID[second]["me"] = tuple(BY_ID[second]["me"]) + (first,)
for fid, parents in OR_PARENTS.items():
    BY_ID[fid]["pre"] = parents
for fid, others in GATES.items():
    require(fid, "\n".join(f"has_completed_focus = {other}" for other in others))
BRANCH_NUMBER = {}
for index, row in enumerate(BRANCH_EVENTS, start=1):
    BRANCH_NUMBER[row[0]] = 1000 + index
    add_effects(row[0], f"country_event = {{ id = lr_story.{1000 + index} days = 4 }}")
WAR_COUNT = 0
GREAT_WAR_NEWS = {"GER": 7, "AUS": 8, "ENG": 9, "SOV": 10}
for item in FOCUSES:
    for target in re.findall(r"declare_war_on = \{\s*target = (\w+)", "\n".join(str(e) for e in item["effects"])):
        if target not in WAR_EVENTS:
            raise SystemExit(f"{item['id']}: no war event for {target}")
        add_effects(item["id"], f"country_event = {{ id = lr_story.{WAR_EVENTS[target][0]} days = 1 }}")
        WAR_COUNT += 1
        if target in GREAT_WAR_NEWS:
            add_effects(item["id"], f"news_event = {{ id = lr_gnews.{GREAT_WAR_NEWS[target]} days = 1 }}")
convert_to_spirits()
ORDER_FLAGS = {row[1] for row in ORDERS}
SPINE_IDS = {fid for chapters in SPINES.values() for fid in chapters}
LAST_CHAPTERS = {chapters[-1] for chapters in SPINES.values() if chapters}
for item in FOCUSES:
    item["cost"] = focus_weeks(item["id"], [str(e) for e in item["effects"]], SPINE_IDS, LAST_CHAPTERS)


def story_option(event, letter, text, effects):
    """One answer of a story event: what the player reads, and what it really does."""
    tips, hidden, shown_lines, gates = [], [], [], []
    values = {}
    for key, value in effects.items():
        if key == "need":
            gates.append(f"trigger = {{ has_country_flag = {value} }}")
        elif key == "avoid":
            gates.append(f"trigger = {{ NOT = {{ has_country_flag = {value} }} }}")
        elif key == "flag":
            tips.append("§Y이 선택은 이 루트의 결말을 바꿉니다.§!")
            hidden.append(f"set_country_flag = {value}")
        elif key == "seats":
            tips.append(f"§Y의석§! {value * SEAT_SCALE:+d}")
            hidden.append(f"add_to_variable = {{ LR_seats = {value * SEAT_SCALE} }}\nlr_fra_sync_seats = yes")
        elif key == "op":
            tips.append("모든 지역 §Y반발도§! -15")
            hidden.append("lr_fra_op_reduce = yes")
        elif key == "dev":
            tips.append(f"§G경제 재건§! +{value:g}")
            hidden.append(f"add_to_variable = {{ LR_rec_focus = {value:g} }}\nlr_fra_sync_industry = yes")
        elif key == "relief":
            tips.append(", ".join(f"§G{name}§! +{value * 5}" for name in REFORM_NAMES.values()))
            hidden.append("\n".join(f"add_to_variable = {{ {var} = {value * 5} }}" for var in REFORM_VARS.values()) + "\nlr_fra_sync_reform = yes")
        elif key == "raw":
            shown_lines.extend(value)
        elif key == "civ":
            shown_lines.append(civ(value))
        elif key == "mil":
            shown_lines.append(mil(value))
        elif key == "friend":
            shown_lines.append(FRIEND_OF.format(tag=value))
        elif key in LABELS:
            values[key] = value
        else:
            raise SystemExit(f"{event}: unknown story effect {key}")
    if values:
        REGIME_KEYS.update(values)
        tips.insert(0, "§Y정부 정신§! 변화: " + ", ".join(shown(k, v) for k, v in sorted(values.items())))
        hidden.extend(f"add_to_variable = {{ LR_reg_{k} = {round(v, 3):g} }}" for k, v in sorted(values.items()))
    lines = [f"\tname = {event}.{letter}"] + [f"\t{gate}" for gate in gates]
    lines += [f"\t{line}" for line in "\n".join(shown_lines).split("\n") if line]
    loc = [f' {event}.{letter}:0 "{text}"']
    if tips:
        key = f"LR_tt_st_{event.replace('.', '_')}_{letter}"
        loc.append(f' {key}:0 "' + "\\n".join(tips) + '"')
        lines.append(f"\tcustom_effect_tooltip = {key}")
    if hidden:
        body = "\n".join(hidden + ["force_update_dynamic_modifier = yes"])
        lines.append("\thidden_effect = {\n" + "\n".join("\t\t" + l for l in body.split("\n")) + "\n\t}")
    return "\toption = {\n" + "\n".join("\t" + l for l in "\n".join(lines).split("\n")) + "\n\t}", loc


def story_files():
    """The events of the story spines and their text."""
    events, loc = ["# Generated by tools/build_france.py from tools/france_story.py.\nadd_namespace = lr_story\n"], []
    for head, prefix, route, base, chapters in STORY:
        for number, part in enumerate(chapters, start=1):
            event = f"lr_story.{base + number}"
            loc.append(f' {event}.t:0 "{part["title"]}"')
            loc.append(f' {event}.d:0 "{LONG.get(event + ".d", part["text"])}"')
            if part["alt"]:
                flag, other = part["alt"]
                loc.append(f' {event}.d2:0 "{LONG.get(event + ".d2", other)}"')
                desc = (f"\tdesc = {{\n\t\ttext = {event}.d2\n\t\ttrigger = {{ has_country_flag = {flag} }}\n\t}}\n"
                        f"\tdesc = {{\n\t\ttext = {event}.d\n\t\ttrigger = {{ NOT = {{ has_country_flag = {flag} }} }}\n\t}}")
            else:
                desc = f"\tdesc = {event}.d"
            options = []
            for letter, (text, effects) in zip("abcd", part["options"]):
                block, lines = story_option(event, letter, text, effects)
                options.append(block)
                loc.extend(lines)
            events.append(f"country_event = {{\n\tid = {event}\n\ttitle = {event}.t\n{desc}\n"
                          f"\tpicture = GFX_report_event_{part['picture']}\n\n\tis_triggered_only = yes\n\n"
                          f"\ttrigger = {{ has_country_flag = {route} }}\n\n" + "\n\n".join(options) + "\n}\n")
    # Events along the branches. Shared ones fire on any route, so only their own effects can apply.
    for row in BRANCH_EVENTS:
        fid, picture, title, text, choices, *_ = row
        number = BRANCH_NUMBER[fid]
        event = f"lr_story.{number}"
        loc.append(f' {event}.t:0 "{title}"')
        loc.append(f' {event}.d:0 "{BRANCH_TEXT.get(fid, text)}"')
        route = BY_ID[fid]["route"]
        guard = f"\ttrigger = {{ has_country_flag = {route} }}\n\n" if route else ""
        blocks = []
        for letter, (label, effects) in zip("abcd", choices):
            block, lines = story_option(event, letter, label, effects)
            blocks.append(block)
            loc.extend(lines)
        events.append(f"country_event = {{\n\tid = {event}\n\ttitle = {event}.t\n\tdesc = {event}.d\n"
                      f"\tpicture = GFX_report_event_{picture}\n\n\tis_triggered_only = yes\n\n{guard}" + "\n\n".join(blocks) + "\n}\n")
    # The speech when war is declared, in the voice of the government declaring it.
    for target, (number, picture, title, texts, choices) in WAR_EVENTS.items():
        event = f"lr_story.{number}"
        loc.append(f' {event}.t:0 "{title}"')
        descs = []
        for family, body in texts.items():
            key = f"{event}.d_{family}"
            loc.append(f' {key}:0 "{LONG.get(key, body)}"')
            flags = " ".join(f"has_country_flag = {flag}" for flag in ROUTE_FAMILIES[family])
            descs.append(f"\tdesc = {{\n\t\ttext = {key}\n\t\ttrigger = {{ OR = {{ {flags} }} }}\n\t}}")
        blocks = []
        for letter, (label, effects) in zip("abcd", choices):
            block, lines = story_option(event, letter, label, effects)
            blocks.append(block)
            loc.extend(lines)
        events.append(f"country_event = {{\n\tid = {event}\n\ttitle = {event}.t\n" + "\n".join(descs)
                      + f"\n\tpicture = GFX_report_event_{picture}\n\n\tis_triggered_only = yes\n\n" + "\n\n".join(blocks) + "\n}\n")
    # The great speeches when a war plan is ready, one region text with the voice of the government closing it.
    for plan in PLANS:
        event = f"lr_story.{plan['event']}"
        loc.append(f' {event}.t:0 "{plan["title"]}"')
        descs = []
        for family, closing in FAMILY_CLOSE.items():
            key = f"{event}.d_{family}"
            closing = PLAN_CLOSE.get((plan["key"], family), closing)
            loc.append(f' {key}:0 "{PLAN_TEXT.get(plan["key"], plan["text"])}\\n\\n{closing}"')
            flags = " ".join(f"has_country_flag = {flag}" for flag in ROUTE_FAMILY_FLAGS[family])
            descs.append(f"\tdesc = {{\n\t\ttext = {key}\n\t\ttrigger = {{ OR = {{ {flags} }} }}\n\t}}")
        blocks = []
        for letter, (label, effects) in zip("abcd", plan["options"]):
            block, lines = story_option(event, letter, label, effects)
            blocks.append(block)
            loc.extend(lines)
        events.append(f"country_event = {{\n\tid = {event}\n\ttitle = {event}.t\n" + "\n".join(descs)
                      + f"\n\tpicture = GFX_report_event_{plan['picture']}\n\n\tis_triggered_only = yes\n\n" + "\n\n".join(blocks) + "\n}\n")
    return "\n".join(events), loc


STORY_EVENTS, STORY_LOC = story_files()


def novel_files():
    """Pages before the big scenes. Each page's only option turns to the next; the last page is the event itself."""
    events = ["# Generated by tools/build_france.py from tools/novel_text.py.\nadd_namespace = lr_novel\n"]
    loc = [f' lr_novel.next_{i}:0 "{label}"' for i, label in enumerate(NEXT_LABELS)]
    for event, scene in NOVEL.items():
        pages = scene["pages"]
        picture = {"lr_france.14": "generic_parliament", "lr_france.33": "france_parade", "lr_france.2": "military_planning", "lr_france.20": "military_planning",
                   "lr_france.30": "generic_read_write", "lr_france.10": "generic_riot"}.get(event, "soldiers_marching")
        for number, text in enumerate(pages, start=1):
            page = f"lr_novel.{BASE[event] + number}"
            following = f"lr_novel.{BASE[event] + number + 1}" if number < len(pages) else event
            loc.append(f' {page}.d:0 "{text}"')
            events.append(f"country_event = {{\n\tid = {page}\n\ttitle = {event}.t\n\tdesc = {page}.d\n\tpicture = GFX_report_event_{picture}\n\n"
                          f"\tis_triggered_only = yes\n\n\toption = {{\n\t\tname = lr_novel.next_{(number - 1) % len(NEXT_LABELS)}\n"
                          f"\t\tcountry_event = {{ id = {following} }}\n\t}}\n}}\n")
    return "\n".join(events), loc


def plan_files():
    """One decision for each European country, opened by the region's war plan."""
    lines = ["# Generated by tools/build_france.py.", "LR_FRA_war_plans_category = {"]
    loc = [' LR_FRA_war_plans_category:0 "전쟁 계획"',
           ' LR_FRA_war_plans_category_desc:0 "전쟁 계획 중점으로 열리는 선전포고다. 전쟁은 평화 회의로 끝나고, 회의에서 얻은 땅은 영토 결단 디시전으로 권역마다 합병하거나 괴뢰국으로 세운다. 전쟁 중점이 준 영유권이 있는 땅은 회의에서 요구하기가 쉽다."']
    for plan in PLANS:
        for tag, name in plan["targets"].items():
            key = f"LR_dec_war_{tag}"
            lines.append(f"\t{key} = {{\n\t\ticon = generic_military\n\t\tcost = 50\n\t\tvisible = {{\n\t\t\thas_country_flag = LR_plan_{plan['key']}\n"
                         f"\t\t\t{tag} = {{\n\t\t\t\texists = yes\n\t\t\t\tNOT = {{ is_subject_of = ROOT }}\n\t\t\t\tNOT = {{ is_in_faction_with = ROOT }}\n\t\t\t}}\n"
                         f"\t\t\tNOT = {{ has_war_with = {tag} }}\n\t\t}}\n"
                         f"\t\tcomplete_effect = {{\n\t\t\tdeclare_war_on = {{\n\t\t\t\ttarget = {tag}\n\t\t\t\ttype = annex_everything\n\t\t\t}}\n\t\t}}\n\t\tai_will_do = {{ factor = 0 }}\n\t}}")
            loc.append(f' {key}:0 "{name} 침공"')
            loc.append(f' {key}_desc:0 "§Y{name}§!에 선전포고합니다."')
    # North Germany's government in exile keeps its colonies until France comes for them.
    lines.append("\tLR_dec_war_GEX = {\n\t\ticon = generic_military\n\t\tcost = 50\n\t\tvisible = {\n\t\t\thas_country_flag = LR_germany_defeated\n"
                 "\t\t\tGEX = {\n\t\t\t\texists = yes\n\t\t\t\tNOT = { is_in_faction_with = ROOT }\n\t\t\t}\n\t\t\tNOT = { has_war_with = GEX }\n\t\t}\n"
                 "\t\tavailable = {\n\t\t\thas_war = no\n\t\t}\n"
                 "\t\tcomplete_effect = {\n\t\t\tdeclare_war_on = {\n\t\t\t\ttarget = GEX\n\t\t\t\ttype = annex_everything\n\t\t\t}\n\t\t}\n\t\tai_will_do = { factor = 1 }\n\t}")
    loc.append(' LR_dec_war_GEX:0 "망명정부 토벌"')
    loc.append(' LR_dec_war_GEX_desc:0 "베를린을 잃은 북독일의 황태자가 두알라에 망명정부를 세웠다. 카메룬과 인도차이나와 태평양의 섬들이 아직 그의 깃발 아래 있다. §Y독일 망명정부§!에 선전포고한다. 항복하면 그 땅은 모두 프랑스의 것이 된다."')
    lines.append("}")
    flags = " ".join(f"has_country_flag = LR_plan_{plan['key']}" for plan in PLANS) + " has_country_flag = LR_germany_defeated"
    category = f"# Generated by tools/build_france.py.\nLR_FRA_war_plans_category = {{\n\ticon = generic_military\n\tvisible = {{\n\t\ttag = FRA\n\t\tOR = {{ {flags} }}\n\t}}\n}}\n"
    return "\n".join(lines) + "\n", category, loc


def order_files():
    """Special orders opened by focuses."""
    lines = ["# Generated by tools/build_france.py.", "LR_FRA_orders_category = {"]
    loc = [' LR_FRA_orders_category:0 "특별 명령"', ' LR_FRA_orders_category_desc:0 "중점으로 열리는 명령입니다. 정치력을 들여 되풀이해서 내릴 수 있습니다."']
    for key, flag, icon, cost, again, name, text, effect in ORDERS:
        body = "\n".join("\t\t\t" + line for line in effect.split("\n"))
        lines.append(f"\tLR_dec_order_{key} = {{\n\t\ticon = {icon}\n\t\tcost = {cost}\n\t\tdays_re_enable = {again}\n"
                     f"\t\tvisible = {{\n\t\t\thas_country_flag = {flag}\n\t\t}}\n\t\tcomplete_effect = {{\n{body}\n\t\t}}\n\t\tai_will_do = {{ factor = 1 }}\n\t}}")
        loc.append(f' LR_dec_order_{key}:0 "{name}"')
        loc.append(f' LR_dec_order_{key}_desc:0 "{text}"')
    lines.append("}")
    flags = " ".join(f"has_country_flag = {row[1]}" for row in ORDERS)
    category = f"# Generated by tools/build_france.py.\nLR_FRA_orders_category = {{\n\ticon = generic_military\n\tvisible = {{\n\t\ttag = FRA\n\t\tOR = {{ {flags} }}\n\t}}\n}}\n"
    return "\n".join(lines) + "\n", category, loc


def check_choices():
    """A focus must never need both sides of an exclusive choice, directly or through its ancestors."""
    needs = {}

    def required(fid):
        if fid not in needs:
            found = set()
            item = BY_ID[fid]
            for group in item["pre"]:
                if not isinstance(group, tuple):
                    found |= {group} | required(group)
            for other in GATES.get(fid, []):
                found |= {other} | required(other)
            needs[fid] = found
        return needs[fid]

    for item in FOCUSES:
        chain = required(item["id"]) | {item["id"]}
        for first, second in EXCLUSIVE:
            if first in chain and second in chain:
                raise SystemExit(f"{item['id']} needs both {first} and {second}")
    for fid, others in GATES.items():
        for other in others:
            if fid in required(other):
                raise SystemExit(f"{fid} and {other} wait for each other")

SEAT_GATE = {45: 275, 50: 305, 51: 306, 55: 336, 60: 366, 67: 407}
for item in FOCUSES:
    if item["seats"]:
        item["seats"] = SEAT_GATE[item["seats"]]


def spirit_files():
    """Dynamic modifiers, the effects that drive them, and their names."""
    def modifier(name, picture, pairs):
        return f"{name} = {{\n\ticon = GFX_idea_{picture}\n" + "".join(f"\t{k} = {v}\n" for k, v in pairs) + "}\n"

    mods = ["# Generated by tools/build_france.py."]
    for line, (prefix, name, picture) in SPIRITS.items():
        mods.append(modifier(f"LR_dyn_{line}", picture, [(k, prefix + k) for k in sorted(LINE_KEYS[line])]))
    for regime in REGIMES:
        mods.append(modifier(f"LR_dyn_regime_{regime}", "generic_central_management", [(k, "LR_reg_" + k) for k in sorted(REGIME_KEYS)]))
    for ruler, (_, picture, _) in RULERS.items():
        mods.append(modifier(f"LR_dyn_ruler_{ruler}", picture, [(k, "LR_rul_" + k) for k in sorted(RULER_KEYS)]))
    for regime, (_, picture) in route_signature.SIGNATURE.items():
        mods.append(modifier(f"LR_dyn_sig_{regime}", picture, [(k, "LR_sig_" + k) for k in sorted(SIG_KEYS)]))
    mods.append(modifier("LR_dyn_defeat", "generic_disjointed_gov", [(k, "LR_def_" + k) for k in sorted(DEFEAT)]))
    mods.append(modifier("LR_dyn_disarmed", "generic_disjointed_gov", [(k, "LR_dis_" + k) for k in sorted(DISARMED)]))

    fx = ["# Generated by tools/build_france.py."]
    # Only what is there: removing a modifier the country lacks is logged as an error.
    drop_rulers = "".join(f"\tif = {{ limit = {{ has_dynamic_modifier = {{ modifier = LR_dyn_ruler_{r} }} }} "
                          f"remove_dynamic_modifier = {{ modifier = LR_dyn_ruler_{r} }} }}\n" for r in RULERS)
    for ruler, (_, _, values) in RULERS.items():
        sets = "".join(f"\tset_variable = {{ LR_rul_{k} = {values.get(k, 0):g} }}\n" for k in RULER_KEYS)
        fx.append(f"lr_fra_ruler_{ruler} = {{\n{drop_rulers}{sets}\tadd_dynamic_modifier = {{ modifier = LR_dyn_ruler_{ruler} }}\n\tforce_update_dynamic_modifier = yes\n}}\n")
    fx.append("lr_fra_ruler_none = {\n" + drop_rulers + "".join(f"\tset_variable = {{ LR_rul_{k} = 0 }}\n" for k in RULER_KEYS) + "}\n")
    drop_regimes = "".join(f"\tif = {{ limit = {{ has_dynamic_modifier = {{ modifier = LR_dyn_regime_{r} }} }} "
                           f"remove_dynamic_modifier = {{ modifier = LR_dyn_regime_{r} }} }}\n" for r in REGIMES)
    base_keys = sorted({k for _, values in REGIMES.values() for k in values})
    for regime, (_, values) in REGIMES.items():
        moves = "".join(f"\tsubtract_from_variable = {{ LR_reg_{k} = LR_base_{k} }}\n\tset_variable = {{ LR_base_{k} = {values.get(k, 0):g} }}\n\tadd_to_variable = {{ LR_reg_{k} = LR_base_{k} }}\n" for k in base_keys)
        fx.append(f"lr_fra_regime_{regime} = {{\n{drop_regimes}{moves}\tadd_dynamic_modifier = {{ modifier = LR_dyn_regime_{regime} }}\n\tforce_update_dynamic_modifier = yes\n}}\n")
    fx.append("lr_fra_defeat_end = {\n\tremove_dynamic_modifier = { modifier = LR_dyn_defeat }\n" + "".join(f"\tset_variable = {{ LR_def_{k} = 0 }}\n" for k in DEFEAT) + "}\n")
    fx.append("""lr_fra_heal_defeat = {
	add_to_variable = { LR_def_stability_factor = 0.02 }
	add_to_variable = { LR_def_political_power_gain = 0.02 }
	add_to_variable = { LR_def_war_support_factor = -0.02 }
	clamp_variable = { var = LR_def_stability_factor min = -0.1 max = 0 }
	clamp_variable = { var = LR_def_political_power_gain min = -0.1 max = 0 }
	clamp_variable = { var = LR_def_war_support_factor min = 0 max = 0.1 }
	if = {
		limit = { check_variable = { LR_def_stability_factor > -0.001 } }
		lr_fra_defeat_end = yes
	}
}
""")
    relief = "".join(f"\tadd_to_variable = {{ LR_dis_{k} = {step:g} }}\n\tclamp_variable = {{ var = LR_dis_{k} min = {min(start, 0):g} max = {max(start, 0):g} }}\n"
                     for k, (start, step) in DISARMED.items())
    fx.append("lr_fra_spirits_init = {\n" + "".join(f"\tset_variable = {{ LR_def_{k} = {v:g} }}\n" for k, v in DEFEAT.items())
              + "".join(f"\tset_variable = {{ LR_dis_{k} = {start:g} }}\n" for k, (start, _) in DISARMED.items())
              + "".join(f"\tset_variable = {{ {var} = 0 }}\n" for var in REFORM_VARS.values())
              + "\tadd_dynamic_modifier = { modifier = LR_dyn_defeat }\n\tadd_dynamic_modifier = { modifier = LR_dyn_disarmed }\n\tadd_dynamic_modifier = { modifier = LR_dyn_rebuild }\n"
              "\tforce_update_dynamic_modifier = yes\n\tlr_fra_ruler_louis = yes\n}\n")
    loc = [f' LR_dyn_{line}:0 "{name}"' for line, (_, name, _) in SPIRITS.items()]
    loc += [f' LR_dyn_regime_{r}:0 "{name}"' for r, (name, _) in REGIMES.items()]
    loc += [f' LR_dyn_ruler_{r}:0 "{name}"' for r, (name, _, _) in RULERS.items()]
    loc += [f' LR_tt_ruler_{r}:0 "§Y{name}§! 정신을 얻습니다."' for r, (name, _, _) in RULERS.items()]
    loc += [' LR_dyn_disarmed:0 "버려진 군대"']
    loc += [f' LR_dyn_sig_{r}:0 "{name}"' for r, (name, _) in route_signature.SIGNATURE.items()]
    loc += CLAIM_LOC
    loc += [' LR_tt_high_command_open:0 "잠겨 있던 군사 고문이 풀립니다: 육군 총사령관 §Y모리스 가믈랭§!, §Y막심 베강§!, 군사 이론가 §Y막심 베강§!, §Y샤를 드골§!"']
    loc += [' LR_dyn_defeat:0 "대전쟁의 굴욕"', ' LR_tt_defeat_end:0 "§R대전쟁의 굴욕§!이 완전히 사라집니다."']
    return "\n".join(mods), "\n".join(fx), loc + SPIRIT_LOC


# The written descriptions.
for fid, desc in TEXT.items():
    if fid in BY_ID:
        BY_ID[fid]["desc"] = desc
UNWRITTEN = [item["id"] for item in FOCUSES if item["id"] not in TEXT]


def indent(text, tabs):
    pad = "\t" * tabs
    return "\n".join(pad + line for line in text.split("\n"))


# Left to right: monarchy (Orleans, Bourbon), revolution, the parliamentary republic, then Napoleon.
LAYOUT = [
    ("LR_route_orleans",), ("LR_route_bourbon",),
    ("LR_route_communist",), ("LR_route_anarchist",),
    ("LR_route_jacobin",), ("LR_route_girondin",), ("LR_route_marais",),
    ("LR_route_napoleon", "LR_route_empire", "LR_route_guardian", "LR_route_red"),
    ("LR_route_petain",),
    ("LR_route_vanquished",),
]
FAMILY_GAP_AFTER = {"LR_route_bourbon", "LR_route_anarchist", "LR_route_marais", "LR_route_guardian"}
HIDDEN_ROUTES = {"LR_route_napoleon", "LR_route_empire", "LR_route_guardian", "LR_route_petain", "LR_route_anarchist", "LR_route_red", "LR_route_vanquished"}
CELL, BRANCH_GAP, ROUTE_GAP, FAMILY_GAP = 2, 0, 2, 2  # A focus name needs two columns; branches sit shoulder to shoulder.
SPINE_STEP = 2  # Rows between chapters of a story; a shelf hangs right under one.
POSITION = {}
FINAL_Y = {}
# Focuses with art of their own: focus id, sprite name, source picture in docs/art.
CUSTOM_GOALS = {
    ROOT: ("GFX_goal_LR_FRA_shadow_of_defeat", "goal_shadow_of_defeat"),
    "LR_FRA_war_reparations": ("GFX_goal_LR_FRA_war_reparations", "goal_war_reparations"),
    "LR_COM_world_revolution": ("GFX_goal_LR_COM_world_revolution", "goal_world_revolution"),
    "LR_COM_one_country": ("GFX_goal_LR_COM_one_country", "goal_one_country"),
    "LR_FRA_lessons_of_defeat": ("GFX_goal_LR_FRA_lessons_of_defeat", "goal_lessons_of_defeat"),
    "LR_FRA_royal_arsenal": ("GFX_goal_LR_FRA_royal_arsenal", "goal_royal_arsenal"),
    "LR_FRA_tunisia_morocco": ("GFX_goal_LR_FRA_tunisia_morocco", "goal_tunisia_morocco"),
    "LR_FRA_rebuild_railways": ("GFX_goal_LR_FRA_rebuild_railways", "goal_rebuild_railways"),
    "LR_FRA_arsenal_of_republic": ("GFX_goal_LR_FRA_arsenal_of_republic", "goal_arsenal_of_republic"),
    "LR_FRA_air_arm": ("GFX_goal_LR_FRA_air_arm", "goal_air_arm"),
    "LR_FRA_new_navy": ("GFX_goal_LR_FRA_new_navy", "goal_new_navy"),
    "LR_FRA_royal_academy": ("GFX_goal_LR_FRA_royal_academy", "goal_royal_academy"),
    "LR_FRA_mass_production": ("GFX_goal_LR_FRA_mass_production", "goal_mass_production"),
    "LR_FRA_steelworks": ("GFX_goal_LR_FRA_steelworks", "goal_steelworks"),
    "LR_FRA_nord_coal": ("GFX_goal_LR_FRA_nord_coal", "goal_nord_coal"),
    "LR_FRA_citroen_trucks": ("GFX_goal_LR_FRA_citroen_trucks", "goal_citroen_trucks"),
    "LR_FRA_alpine_hydro": ("GFX_goal_LR_FRA_alpine_hydro", "goal_alpine_hydro"),
    "LR_FRA_war_economy": ("GFX_goal_LR_FRA_war_economy", "goal_war_economy"),
    "LR_FRA_trade_treaties": ("GFX_goal_LR_FRA_trade_treaties", "goal_trade_treaties"),
    "LR_FRA_lyon_chemicals": ("GFX_goal_LR_FRA_lyon_chemicals", "goal_lyon_chemicals"),
}


def first_option(group):
    return group[0] if isinstance(group, tuple) else group


def options(group):
    return group if isinstance(group, tuple) else (group,)


SUB_HEADS = {"LR_NAP_coronation", "LR_NAP_guardian", "LR_NAP_red"}


def build_layout():
    """Each connected branch under a head becomes one block; a row centres under its parents."""
    by_id = {item["id"]: item for item in FOCUSES}
    order = {item["id"]: index for index, item in enumerate(FOCUSES)}
    parents = {fid: [o for g in by_id[fid]["pre"] for o in options(g)] for fid in by_id}
    children = {fid: [] for fid in by_id}
    for fid, ups in parents.items():
        for up in ups:
            children[up].append(fid)
    rows = {}

    def row(fid):
        if fid not in rows:
            rows[fid] = 1 + max((row(o) for o in parents[fid]), default=-1)
        return rows[fid]

    def sort_key(fid):
        return (by_id[fid].get("slot", 10_000), order[fid])

    def place_block(ids, level_of=row):
        """Top-down: wish to sit under the parents, then push apart and recentre the row."""
        x = {}
        for level in sorted({level_of(f) for f in ids}):
            members = sorted((f for f in ids if level_of(f) == level), key=sort_key)
            wish = {}
            for number, fid in enumerate(members):
                ups = [x[u] for u in parents[fid] if u in x]
                wish[fid] = sum(ups) / len(ups) if ups else None
            placed = [f for f in members if wish[f] is not None]
            free = [f for f in members if wish[f] is None]
            placed.sort(key=lambda f: (wish[f], sort_key(f)))
            line = placed + free
            cursor = None
            spots = []
            for fid in line:
                want = round(wish[fid]) if wish[fid] is not None else (cursor + CELL if cursor is not None else 0)
                cursor = want if cursor is None else max(want, cursor + CELL)
                spots.append(cursor)
            pairs = [(wish[f], s) for f, s in zip(line, spots) if wish[f] is not None]
            shift = round(sum(w - s for w, s in pairs) / len(pairs)) if pairs else 0
            for fid, spot in zip(line, spots):
                x[fid] = spot + shift
        low = min(x.values())
        return {fid: value - low for fid, value in x.items()}, max(x.values()) - low + CELL

    def lay(head):
        """Columns of everything under head, from 0, and the width used."""
        members = []
        subs = []
        stack = list(children[head])
        seen = set()
        while stack:
            fid = stack.pop()
            if fid in seen:
                continue
            seen.add(fid)
            if fid in SUB_HEADS:
                subs.append(fid)
                continue
            members.append(fid)
            stack.extend(children[fid])
        parent_of = {fid: fid for fid in members}

        def find(fid):
            while parent_of[fid] != fid:
                parent_of[fid] = parent_of[parent_of[fid]]
                fid = parent_of[fid]
            return fid

        for fid in members:
            for up in parents[fid]:
                if up in parent_of:
                    parent_of[find(fid)] = find(up)
        blocks = {}
        for fid in members:
            blocks.setdefault(find(fid), []).append(fid)
        ordered = sorted(blocks.values(), key=lambda ids: min((by_id[f].get("rank", 99), sort_key(f)) for f in ids))
        result = {}
        cursor = 0
        subs.sort(key=lambda f: order[f])

        def put(columns, width):
            nonlocal cursor
            for fid, value in columns.items():
                result[fid] = value + cursor
            cursor += width + BRANCH_GAP

        if subs:
            put(*lay(subs[0]))
        trunk_start = cursor
        for number, ids in enumerate(ordered):
            # Blocks of one category sit shoulder to shoulder.
            if number and by_id[ids[0]].get("filter") == by_id[ordered[number - 1][0]].get("filter"):
                cursor -= BRANCH_GAP
            put(*place_block(ids))
        trunk_end = cursor - BRANCH_GAP
        for sub in subs[1:]:
            put(*lay(sub))
        direct = [result[f] for f in children[head] if f in result and f not in SUB_HEADS]
        result[head] = round(sum(direct) / len(direct)) if direct else (trunk_start + trunk_end) // 2
        return result, max(cursor - BRANCH_GAP, CELL)

    def lay_route(head):
        """The story runs down the middle; each category hangs off it on either side, stacked downward.
        Returns columns and rows relative to the head, and the width and depth used."""
        spine = [head] + SPINES.get(head, [])
        members, seen = [], set(spine) | SUB_HEADS
        stack = [child for node in spine for child in children[node]]
        while stack:
            fid = stack.pop()
            if fid in seen:
                continue
            seen.add(fid)
            members.append(fid)
            stack.extend(children[fid])
        inside = set(members)
        link = {fid: fid for fid in members}

        def find(fid):
            while link[fid] != fid:
                link[fid] = link[link[fid]]
                fid = link[fid]
            return fid

        for fid in members:
            for up in parents[fid]:
                if up in inside:
                    link[find(fid)] = find(up)
        groups = {}
        for fid in members:
            groups.setdefault(find(fid), []).append(fid)
        ordered = sorted(groups.values(), key=lambda ids: min((by_id[f].get("rank", 99), sort_key(f)) for f in ids))

        # Blocks of one category share a shelf.
        shelves = []
        for ids in ordered:
            rank = min(by_id[f].get("rank", 99) for f in ids)
            if not shelves or shelves[-1][0] != rank:
                shelves.append((rank, []))
            memo = {}

            def level(fid, memo=memo, ids=frozenset(ids)):
                if fid not in memo:
                    memo[fid] = 1 + max((level(o) for o in parents[fid] if o in ids), default=-1)
                return memo[fid]

            found, width = place_block(ids, level)
            shelves[-1][1].append((ids, found, width, {f: level(f) for f in ids}))

        xs, ys = {}, {}
        for number, node in enumerate(spine):
            xs[node], ys[node] = 0, number * SPINE_STEP
        sides = {-1: {"top": 1, "offset": 0, "width": 0, "outer": False}, 1: {"top": 1, "offset": 0, "width": 0, "outer": False}}
        for _, blocks in shelves:
            shelf_width = sum(b[2] for b in blocks) + BRANCH_GAP * (len(blocks) - 1)
            depth = max(max(b[3].values()) for b in blocks) + 1
            side = -1 if sides[-1]["top"] <= sides[1]["top"] else 1
            state = sides[side]
            top = state["top"] + (state["top"] + 1) % 2  # Shelves start right under a chapter.
            attach = (top - 1) // SPINE_STEP
            if state["outer"] or attach >= len(spine):
                # The story has ended: open a new column from the head, whose line runs above everything.
                state["offset"] += state["width"] + BRANCH_GAP
                state["width"], state["outer"], top, attach = 0, True, 1, 0
            shift = 0
            for ids, found, width, levels in blocks:
                for fid in ids:
                    column = found[fid] + shift
                    xs[fid] = CELL + BRANCH_GAP + state["offset"] + column if side > 0 else -BRANCH_GAP - state["offset"] - shelf_width + column
                    ys[fid] = top + levels[fid]
                    by_id[fid]["pre"] = [tuple(spine[attach] if o in spine else o for o in group) if isinstance(group, tuple)
                                         else spine[attach] if group in spine else group for group in by_id[fid]["pre"]]
                shift += width + BRANCH_GAP
            state["width"] = max(state["width"], shelf_width)
            state["top"] = top + depth + 1
        low = min(xs.values())
        return {f: v - low for f, v in xs.items()}, ys, max(xs.values()) - low + CELL, max(ys.values())

    def lay_napoleon(head):
        """His trunk, then the three roads he can take, side by side beneath it: crown, presidency, red flag."""
        trunk, trunk_y, trunk_width, trunk_depth = lay_route(head)
        xs, ys = {}, {}
        roads = {}
        for road in ("LR_NAP_coronation", "LR_NAP_guardian", "LR_NAP_red"):
            found, found_y, width, depth = lay_route(road)
            if found[road] > width - CELL - found[road]:
                # Mirror a road whose wide side is on the left, so it does not push the shared column right.
                found = {fid: width - CELL - value for fid, value in found.items()}
            roads[road] = (found, found_y, width, depth)
        # Only one road is ever drawn, so all three hang from the same column under the trunk.
        middle = max(found[road] for road, (found, *_rest) in roads.items())
        for number, (road, (found, found_y, width, _)) in enumerate(roads.items()):
            for fid, value in found.items():
                xs[fid], ys[fid] = value + middle - found[road], found_y[fid] + trunk_depth + 2
            xs[road] = middle + (number - 1) * CELL  # the three choices stand side by side above their roads
        for fid, value in trunk.items():
            xs[fid], ys[fid] = value + middle - trunk[head], trunk_y[fid]
        low = min(xs.values())
        return {f: v - low for f, v in xs.items()}, ys, max(xs.values()) - low + CELL

    columns = {}
    cursor = 0
    tops = sorted(children[ROOT], key=lambda f: (by_id[f].get("rank", 99), order[f]))

    def place_top(fid):
        nonlocal cursor
        found, width = lay(fid)
        for key, value in found.items():
            columns[key] = value + cursor
        cursor += width

    for fid in tops:
        if by_id[fid]["route"] is None:
            place_top(fid)
            cursor += FAMILY_GAP
    shared_end = cursor
    route_start = cursor
    for group in LAYOUT:
        # Only one route is ever drawn, so every route starts at the same column.
        cursor = route_start
        for fid in tops:
            if by_id[fid]["route"] in group:
                if fid == "LR_NAP_first_consul":
                    found, found_y, width = lay_napoleon(fid)
                else:
                    found, found_y, width, _ = lay_route(fid)
                # Close the empty rows: chapters sit two rows apart so shelves can hang between them, but a
                # row with nothing in it only stretches the lines. The order of rows stays, so lines still run down.
                used = {value: number for number, value in enumerate(sorted(set(found_y.values())))}
                found_y = {key: used[value] for key, value in found_y.items()}
                for key, value in found.items():
                    columns[key] = value + cursor
                FINAL_Y.update(found_y)
                cursor += width
        cursor += FAMILY_GAP if group[0] in FAMILY_GAP_AFTER else ROUTE_GAP
    columns[ROOT] = (shared_end - FAMILY_GAP) // 2

    for item in FOCUSES:
        POSITION[item["id"]] = (columns[item["id"]], FINAL_Y[item["id"]] if item["id"] in FINAL_Y else row(item["id"]))
    shared_depth = max(row(item["id"]) for item in FOCUSES if item["route"] is None)
    return columns[ROOT], (shared_depth + 2) * 130


def render_focus(item):
    x, y = POSITION[item["id"]]
    sprite = CUSTOM_GOALS[item["id"]][0] if item["id"] in CUSTOM_GOALS else f"GFX_goal_generic_{item['icon']}"
    lines = ["\tfocus = {", f"\t\tid = {item['id']}", f"\t\ticon = {sprite}",
             f"\t\tx = {x}", f"\t\ty = {y}"]
    for group in item["pre"]:
        options = group if isinstance(group, tuple) else (group,)
        # Route heads stand alone as their own trees; the route condition is what locks them.
        if item["route"] and options == (ROOT,):
            continue
        lines.append("\t\tprerequisite = { " + " ".join(f"focus = {o}" for o in options) + " }")
    if item["me"]:
        lines.append("\t\tmutually_exclusive = { " + " ".join(f"focus = {o}" for o in item["me"]) + " }")
    conditions = []
    if item["route"]:
        # The tree shows the shared focuses and the route France is on; the others are not drawn at all.
        lines.append(f"\t\tallow_branch = {{ has_country_flag = {item['route']} }}")
    if item["route"] and item["route"] not in HIDDEN_ROUTES:
        # Every focus of a visible route needs the route, so leaving it (Jacobin to Napoleon) closes the rest.
        conditions.append(f"custom_trigger_tooltip = {{\n\ttooltip = {item['route']}_tt\n\thas_country_flag = {item['route']}\n}}")
    if item["available"]:
        conditions.append(item["available"])
    if item["seats"]:
        conditions.append(f"custom_trigger_tooltip = {{\n\ttooltip = LR_tt_seats_{item['seats']}\n"
                          f"\tcheck_variable = {{ LR_seats > {item['seats'] - 1} }}\n}}")
    if conditions:
        lines.extend(["\t\tavailable = {", indent("\n".join(conditions), 3), "\t\t}"])
    if item.get("bypass"):
        lines.append("\t\tbypass = {\n" + indent(item["bypass"], 3) + "\n\t\t}")
    if item["available"] and "LR_tt_algeria_open" in item["available"]:
        # Once Algeria is pacified, its other focuses must not block the rest of the route.
        lines.append(f"\t\tbypass = {{ {algeria.BYPASS} }}")
    if item.get("filter"):
        lines.append(f"\t\tsearch_filters = {{ {item['filter']} }}")
    lines.extend([f"\t\tcost = {item['cost']}", ai_will_do(item), "\t\tcompletion_reward = {"])
    lines.extend(indent(effect, 3) for effect in item["effects"])
    lines.extend(["\t\t}", "\t}"])
    return "\n".join(lines)


def write_custom_goals():
    """The user's pictures become focus icons, each with the same shine vanilla icons get."""
    shine = (VANILLA / "interface" / "goals_shine.gfx").read_text(encoding="utf-8-sig", errors="ignore")
    start = [m.start() for m in re.finditer(r"[sS]priteType\s*=\s*\{", shine[:shine.index('"GFX_goal_generic_national_unity_shine"')])][-1]
    end, depth = shine.index("{", start) + 1, 1
    while depth:
        depth += {"{": 1, "}": -1}.get(shine[end], 0)
        end += 1
    template = shine[start:end]
    plain, shining = [], []
    folder = MOD / "gfx" / "interface" / "goals"
    folder.mkdir(parents=True, exist_ok=True)
    for sprite, art in CUSTOM_GOALS.values():
        picture = Image.open(MOD.parent / "docs" / "art" / f"{art}.png").convert("RGBA")
        picture = picture.crop(picture.getbbox())  # No empty margin, so a small drawing still fills the icon.
        picture.thumbnail((102, 102), Image.LANCZOS)  # Vanilla icons are about this size.
        picture.save(folder / f"{art}.dds")
        path = f"gfx/interface/goals/{art}.dds"
        plain.append(f'\tspriteType = {{\n\t\tname = "{sprite}"\n\t\ttexturefile = "{path}"\n\t}}\n')
        shining.append("\t" + template.replace("GFX_goal_generic_national_unity_shine", f"{sprite}_shine")
                       .replace("gfx/interface/goals/goal_generic_national_unity.dds", path) + "\n")
    (MOD / "interface" / "lr_goals.gfx").write_text("spriteTypes = {\n" + "".join(plain) + "}\n", encoding="utf-8")
    (MOD / "interface" / "lr_goals_shine.gfx").write_text("spriteTypes = {\n" + "".join(shining) + "}\n", encoding="utf-8")


def main():
    check_choices()
    root_x, panel_y = build_layout()
    if UNWRITTEN:
        print("no written description:", UNWRITTEN)
    ids = [item["id"] for item in FOCUSES]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate focus id")
    for item in FOCUSES:
        for group in item["pre"]:
            for option in (group if isinstance(group, tuple) else (group,)):
                if option not in ids:
                    raise SystemExit(f"{item['id']}: unknown prerequisite {option}")

    tags = "\n".join(p.read_text(encoding="utf-8-sig", errors="ignore") for p in (VANILLA / "common" / "technology_tags").glob("*.txt"))
    gfx = (VANILLA / "interface" / "goals.gfx").read_text(encoding="utf-8-sig", errors="ignore")
    for item in FOCUSES:
        if item["id"] not in CUSTOM_GOALS and f'"GFX_goal_generic_{item["icon"]}"' not in gfx:
            raise SystemExit(f"{item['id']}: unknown icon {item['icon']}")
        for effect in item["effects"]:
            for category in re.findall(r"category = (\w+)", effect):
                if not re.search(rf"^\s*{category}\s*$", tags, re.M):
                    raise SystemExit(f"{item['id']}: unknown technology category {category}")

    header = (
        "# Generated by tools/build_france.py. Edit the tables there, not this file.\n"
        "focus_tree = {\n\tid = french_focus\n\n\tcountry = {\n\t\tfactor = 0\n\n\t\tmodifier = {\n"
        "\t\t\tadd = 10\n\t\t\ttag = FRA\n\t\t}\n\t}\n\n"
        f"\tcontinuous_focus_position = {{ x = 50 y = {panel_y} }}\n\n\tinitial_show_position = {{\n\t\tx = {root_x}\n\t}}\n\n\tdefault = no\n\n"
    )
    body = "\n\n".join(render_focus(item) for item in FOCUSES)
    (MOD / "common" / "national_focus" / "france.txt").write_text(header + body + "\n}\n", encoding="utf-8")

    loc = ["l_korean:"]
    loc.append(' FOCUS_FILTER_LR_DIPLOMACY:0 "외교"')
    loc.extend(ITALY_LOC)
    spirit_mods, spirit_fx, spirit_loc = spirit_files()
    loc.extend(spirit_loc)
    (MOD / "common" / "dynamic_modifiers" / "lr_france_spirits.txt").write_text(spirit_mods, encoding="utf-8")
    (MOD / "common" / "scripted_effects" / "lr_france_spirit_effects.txt").write_text(spirit_fx, encoding="utf-8")
    (MOD / "common" / "decisions" / "lr_italy_decisions.txt").write_text(ITALY_DECISIONS, encoding="utf-8")
    (MOD / "common" / "decisions" / "categories" / "lr_italy_categories.txt").write_text(ITALY_CATEGORY, encoding="utf-8")
    (MOD / "events" / "lr_france_diplomacy.txt").write_text(DIPLOMACY_EVENTS, encoding="utf-8")
    write_custom_goals()
    (MOD / "events" / "lr_france_story.txt").write_text(STORY_EVENTS, encoding="utf-8")
    novel_events, novel_loc = novel_files()
    (MOD / "events" / "lr_novel.txt").write_text(novel_events, encoding="utf-8")
    loc.extend(novel_loc)
    algeria.main()
    alliance_loc = ["l_korean:"] + [f' {k}:0 "{v}"' for k, v in alliances.TEXT.items()]
    (MOD / "localisation" / "korean" / "lr_alliances_l_korean.yml").write_text("\n".join(alliance_loc) + "\n", encoding="utf-8-sig")
    import novel_text
    novel_text.patch_last(MOD / "localisation" / "korean" / "lr_l_korean.yml")
    plan_decisions, plan_category, plan_loc = plan_files()
    (MOD / "common" / "decisions" / "lr_france_war_plans.txt").write_text(plan_decisions, encoding="utf-8")
    (MOD / "common" / "decisions" / "categories" / "lr_france_war_plans_categories.txt").write_text(plan_category, encoding="utf-8")
    loc.extend(plan_loc)
    integ_decisions, integ_category, integ_loc = integration_routes.decisions_and_loc()
    import settlement_decisions
    settle_decisions, settle_category, settle_loc = settlement_decisions.build()
    (MOD / "common" / "decisions" / "lr_france_settlement.txt").write_text(settle_decisions, encoding="utf-8")
    (MOD / "common" / "decisions" / "categories" / "lr_france_settlement_categories.txt").write_text(settle_category, encoding="utf-8")
    loc.extend(settle_loc)
    (MOD / "common" / "decisions" / "lr_france_integration.txt").write_text(integ_decisions, encoding="utf-8")
    (MOD / "common" / "decisions" / "categories" / "lr_france_integration_categories.txt").write_text(integ_category, encoding="utf-8")
    loc.extend(integ_loc)
    order_decisions, order_category, order_loc = order_files()
    (MOD / "common" / "decisions" / "lr_france_orders.txt").write_text(order_decisions, encoding="utf-8")
    (MOD / "common" / "decisions" / "categories" / "lr_france_orders_categories.txt").write_text(order_category, encoding="utf-8")
    loc.extend(order_loc)
    (MOD / "localisation" / "korean" / "lr_france_story_l_korean.yml").write_text("l_korean:\n" + "\n".join(STORY_LOC) + "\n", encoding="utf-8-sig")
    (MOD / "interface" / "lr_focus_filters.gfx").write_text(
        'spriteTypes = {\n\tspriteType = {\n\t\tname = "GFX_FOCUS_FILTER_LR_DIPLOMACY"\n'
        '\t\ttextureFile = "gfx/interface/focusview/filter/international_trade_icon.dds"\n\t}\n}\n', encoding="utf-8")
    for route, name in (("orleans", "오를레앙"), ("bourbon", "부르봉"), ("communist", "사회주의"),
                        ("jacobin", "산악파"), ("girondin", "지롱드"), ("marais", "푀양파")):
        loc.append(f' LR_route_{route}_tt:0 "§Y{name} 루트§!에 들어가야 합니다. 알제리 반란의 결과로 정해집니다."')
    loc.append(' LR_tt_need_rail_3:0 "철도 §Y3개 구간§! 이상을 깔아야 합니다."')
    loc.append(' LR_tt_need_rearmament:0 "§Y기술혁신 60§! 이상이어야 합니다. 군사 중점과 §Y군사 개혁 위원회§!의 훈련·시험으로 오릅니다."')
    for seats in sorted({item["seats"] for item in FOCUSES if item["seats"]}):
        loc.append(f' LR_tt_seats_{seats}:0 "의회 의석 §Y{seats}석§! 이상 필요"')
    for item in FOCUSES:
        loc.append(f' {item["id"]}:0 "{item["name"]}"')
        loc.append(f' {item["id"]}_desc:0 "{item["desc"]}"')
    (MOD / "localisation" / "korean" / "lr_france_focus_l_korean.yml").write_text("\n".join(loc) + "\n", encoding="utf-8-sig")

    tokens = "\n".join(path.read_text(encoding="utf-8-sig", errors="ignore") for path in (VANILLA / "common" / "ideas").glob("*.txt"))
    pictures = (VANILLA / "interface" / "ideas.gfx").read_text(encoding="utf-8-sig", errors="ignore")
    block = ["# Generated by tools/build_france.py. Edit the tables there, not this file.", "ideas = {", "\tcountry = {"]
    for key, name, desc, picture, modifiers in IDEAS:
        if f'"GFX_idea_{picture}"' not in pictures:
            raise SystemExit(f"{key}: unknown picture {picture}")
        block += [f"\t\t{key} = {{", "\t\t\tremoval_cost = -1", f"\t\t\tpicture = {picture}", "\t\t\tmodifier = {"]
        for token, value in modifiers.items():
            if not re.search(rf"^\s*{token}\s*=", tokens, re.M):
                raise SystemExit(f"{key}: unknown modifier {token}")
            block.append(f"\t\t\t\t{token} = {value}")
        block += ["\t\t\t}", "\t\t}"]
        loc.append(f' {key}:0 "{name}"')
        loc.append(f' {key}_desc:0 "{desc}"')
    block += ["\t}", "}"]
    (MOD / "common" / "ideas" / "lr_france_ideas.txt").write_text("\n".join(block) + "\n", encoding="utf-8")
    (MOD / "localisation" / "korean" / "lr_france_focus_l_korean.yml").write_text("\n".join(loc) + "\n", encoding="utf-8-sig")

    counts = {}
    for item in FOCUSES:
        key = item["route"] or "shared"
        counts[key] = counts.get(key, 0) + 1
    print(f"OK: {len(FOCUSES)} focuses", counts)


if __name__ == "__main__":
    main()
    import build_debug
    build_debug.main()
    (MOD / "events" / "lr_endings.txt").write_text("# Generated by tools/build_france.py from tools/endings.py.\n" + ENDING_EVENTS, encoding="utf-8")
    (MOD / "localisation" / "korean" / "lr_endings_l_korean.yml").write_text("l_korean:\n" + "\n".join(ENDING_LOC) + "\n", encoding="utf-8-sig")
    print(f"OK: {len(ENDING_LOC) // 3} endings")


if __name__ == "__main__":
    import polish_text
    polish_text.apply()
