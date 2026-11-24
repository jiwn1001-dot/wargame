"""America's minigames: one index per route, decisions that move it, focuses that move it or need it.

Each index runs from 0 to 100 and falls a little every month. A dynamic modifier turns it into national effects
centred on 50 (value - 50 times the scale), so a high index helps and a low one hurts. build_america.py writes the
decisions, categories, modifiers, effects and text; gain() and need() give the focus and event snippets.

Descriptions are in the polite style of docs/STYLE_GUIDE.md, section 6.
"""
from america_focus import civ, infra, mil, manpower, pop, stab, war

TOOLTIPS = {}  # key -> Korean text, filled by gain() and need()


def mg(key, name, title, desc, tags, start, decay, icon, modifier_icon, mods, decisions):
    return dict(key=key, var=f"LR_usa_{key}", name=name, title=title, desc=desc, tags=tags, start=start, decay=decay,
                icon=icon, modifier_icon=modifier_icon, mods=mods, decisions=decisions)


def dec(did, name, desc, icon, cost, gain, *effects, days=60, available=None):
    return dict(id=did, name=name, desc=desc, icon=icon, cost=cost, gain=gain, effects=effects, days=days, available=available)


MINIGAMES = {m["key"]: m for m in [
    mg("loyalty", "식민지 충성도", "총독부 통치",
       "뉴욕 총독부는 식민지인의 마음을 붙잡아야 합니다. 충성도가 높으면 나라가 안정되고, 낮으면 반란의 불씨가 커집니다. "
       "대륙군이 봉기할 때 충성도가 65 이상이면 봉기에 가담하는 사람이 줄어듭니다.",
       ["USA"], 40, 1, "generic_political_actions", "GFX_idea_generic_pp_unity_bonus",
       {"stability_factor": 0.003, "political_power_gain": 0.006},
       [dec("banquet", "충성파 연회", "뉴욕과 찰스턴의 충성파 가문을 총독 관저 만찬에 초대합니다. 그들의 아들들이 다음 주 민병대에 자원합니다.",
            "generic_political_rally", 40, 6),
        dec("arrests", "용의자 검거", "필라델피아와 보스턴의 비밀 회합 장소를 급습합니다. 잡혀 오는 사람보다 숨어드는 사람이 많다는 보고도 있습니다.",
            "generic_arrest", 25, 5, stab(-0.02)),
        dec("assembly", "식민지 의회와의 타협", "식민지 의회 예산안의 몇 줄을 받아들입니다. 런던은 불평하겠지만, 의원들은 오랜만에 총독에게 박수를 쳤습니다.",
            "generic_political_discourse", 60, 9, days=90, available="NOT = { has_country_flag = LR_usa_coercive }"),
        dec("charter", "공장 허가 발급", "런던의 허가를 기다리던 공장 계획 하나를 총독 권한으로 승인합니다. 공장주들이 총독부를 다시 보기 시작합니다.",
            "generic_factory", 90, 3, civ(1), days=120)]),
    mg("union", "연방의 결속", "연방 정부",
       "열세 주와 서부 영토는 아직 하나의 나라라기보다 느슨한 동맹에 가깝습니다. 결속이 높으면 연방 정부가 힘을 얻고, "
       "낮으면 주들이 제각각 움직입니다.",
       ["CNA"], 45, 1, "generic_democracy", "GFX_idea_generic_democratic_drift_bonus",
       {"stability_factor": 0.003, "production_speed_buildings_factor": 0.003},
       [dec("governors", "주지사 회의", "열세 주의 주지사를 필라델피아로 불러 연방 예산을 나눕니다. 회의는 사흘이 걸렸고, 모두가 조금씩 불만이었습니다.",
            "generic_political_discourse", 50, 6),
        dec("public_works", "연방 공공사업", "강과 항구와 도로에 연방 예산을 붓습니다. 일자리를 얻은 사람들은 주가 아니라 연방에 고마워합니다.",
            "generic_construction", 80, 4, civ(1), infra(1), days=120),
        dec("homestead", "서부 자영농법", "미시시피 서쪽의 땅을 160에이커씩 나눠 줍니다. 동부의 젊은이들이 마차와 기차를 타고 서쪽으로 갑니다.",
            "generic_welfare", 60, 5, manpower(20000), days=120),
        dec("pensions", "대륙군 퇴역 연금", "독립 전쟁에서 싸운 병사들에게 연금을 줍니다. 그들은 연방의 가장 충실한 지지자가 됩니다.",
            "generic_army_support", 40, 4, war(0.02), days=90)]),
    mg("order", "공화국의 질서", "흔들리는 공화국",
       "대통령이 죽은 뒤 공화국은 무너지고 있습니다. 질서를 얼마나 지키느냐에 따라 다가올 내전에서 필라델피아가 쥘 힘이 달라집니다. "
       "내전이 터질 때 질서가 50 이상이면 필라델피아의 군대가 단단하게 싸움을 시작합니다.",
       ["CNA"], 25, 2, "generic_crisis", "GFX_idea_generic_disjointed_gov",
       {"stability_factor": 0.003, "political_power_gain": 0.006},
       [dec("police", "경찰 증원", "주 방위군에서 경찰로 사람을 옮깁니다. 거리에 제복이 늘어나면 날아오는 벽돌이 조금 줄어듭니다.",
            "generic_police_action", 30, 5, days=45),
        dec("relief", "실업 구호", "문 닫은 공장 앞에 무료 급식소를 엽니다. 줄은 길지만, 줄을 선 사람은 돌을 던지지 않습니다.",
            "generic_welfare", 60, 7),
        dec("london", "런던과의 협상", "재무장관이 런던에 가서 금수를 풀어 달라고 청합니다. 귀족 의회는 정중하게 들었고, 아무것도 약속하지 않았습니다.",
            "generic_political_discourse", 50, 4, days=90),
        dec("veterans", "퇴역 군인 위로", "대륙군 퇴역 군인회 지도부를 만나 연금을 약속합니다. 그들이 노동자들과 거리에서 싸우는 일은 줄어들 것입니다.",
            "generic_army_support", 40, 5)]),
    mg("army", "군의 충성", "국가 재건 위원회",
       "맥아더의 권력은 군에서 나옵니다. 장교들이 그를 따르는 한 위원회는 무너지지 않습니다. 군의 충성이 높을수록 군대는 단단해지고 나라는 조용해집니다.",
       ["CNA"], 50, 1, "generic_fascism", "GFX_idea_generic_army_war_college",
       {"army_org_factor": 0.002, "stability_factor": 0.003},
       [dec("medals", "훈장 수여식", "필라델피아 광장에서 내전 공훈자 이백 명에게 훈장을 겁니다. 맥아더가 직접 한 사람씩 가슴에 달아 줍니다.",
            "generic_military", 40, 6),
        dec("purge", "장성 정리", "충성이 의심스러운 장군 열한 명을 예편시킵니다. 그 자리에는 맥아더가 필리핀에서 데리고 있던 대령들이 앉습니다.",
            "generic_arrest", 25, 8, stab(-0.02), "army_experience = -10", days=120),
        dec("war_bonds", "전쟁 공채", "전쟁 공채를 찍어 병기 공장 하나를 세웁니다. 공채의 절반은 장교들이 의무적으로 샀습니다.",
            "generic_factory", 80, 3, mil(1), days=120),
        dec("engineers", "공병단 재건 사업", "내전으로 끊긴 다리와 철도를 군 공병단이 다시 놓습니다. 공사장에서는 포로들이 일합니다.",
            "generic_construction", 70, 3, civ(1), infra(1), days=120)]),
    mg("plan", "계획 달성률", "계획 위원회",
       "평의회는 공장을 손에 넣었지만, 공장을 돌리는 일은 또 다른 문제입니다. 계획 달성률이 높으면 공업이 살아나고, 낮으면 공장이 멈춥니다.",
       ["AMC"], 30, 1, "generic_communism", "GFX_idea_generic_central_management",
       {"industrial_capacity_factory": 0.003, "production_speed_buildings_factor": 0.002},
       [dec("shock_work", "돌격 노동 운동", "디트로이트 조립공 스탠리 코발스키의 작업반이 하루 할당량의 세 배를 채웠습니다. 그의 사진이 전국의 공장에 붙습니다.",
            "generic_industry", 40, 6),
        dec("council_elections", "공장 평의회 선거", "공장마다 평의회 대표를 다시 뽑습니다. 투표함 옆에는 정치위원이 서 있습니다.",
            "generic_political_rally", 30, 3, stab(0.03), days=90),
        dec("heavy_industry", "중공업 투자", "계획 위원회가 새 제철소와 병기 공장에 예산을 몰아줍니다. 소비재 공장은 한 해 더 기다려야 합니다.",
            "generic_factory", 90, 5, mil(1), days=120),
        dec("integrate", "해방구 통합", "해방된 땅에 노동자 평의회를 세우고 연방의 정식 일원으로 받아들입니다.",
            "generic_colonial_administration", 75, 2,
            "random_owned_controlled_state = {\n\tlimit = { NOT = { is_core_of = ROOT } }\n\tadd_core_of = ROOT\n}",
            available="any_owned_state = {\n\tis_controlled_by = ROOT\n\tNOT = { is_core_of = ROOT }\n}")]),
    mg("popularity", "킹피시의 인기", "킹피시의 방송",
       "휴이 롱의 힘은 라디오와 군중에서 나옵니다. 인기가 떨어지면 부의 공유 클럽이 흩어지고, 인기가 오르면 평원이 하나로 움직입니다.",
       ["LNG"], 50, 2, "generic_propaganda", "GFX_idea_generic_political_support",
       {"stability_factor": 0.003, "war_support_factor": 0.003},
       [dec("sunday", "일요일 방송", "이번 주 일요일 저녁에도 롱이 마이크 앞에 앉습니다. 은행가와 장군과 빨갱이가 차례로 얻어맞습니다.",
            "generic_speech", 30, 5, days=45),
        dec("cheques", "정착금 지급", "이번 달 정착금 수표가 평원의 농가 삼십만 곳에 배달됩니다. 액수는 약속보다 적지만, 수표는 진짜입니다.",
            "generic_welfare", 60, 9, stab(0.02), days=90),
        dec("roads", "고속도로 착공", "새 고속도로 구간의 착공식에 롱이 직접 삽을 들고 나타납니다. 공사장마다 실업자들이 줄을 섭니다.",
            "generic_construction", 80, 4, civ(1), infra(1), days=120),
        dec("crackdown", "반대파 단속", "롱을 비판하던 신문사 두 곳이 세무 조사를 받습니다. 편집장들은 긴 휴가를 떠났습니다.",
            "generic_police_action", 40, 3, stab(0.03), pop("democratic", -0.03), days=90)]),
    mg("planters", "농장주의 지지", "농장주 회의",
       "남부 연합을 움직이는 것은 땅을 가진 가문들입니다. 그들의 지지가 높으면 정부가 힘을 얻고, 낮으면 원로원이 등을 돌립니다.",
       ["DXE"], 50, 1, "generic_economy", "GFX_idea_generic_agrarian_society",
       {"political_power_gain": 0.006, "stability_factor": 0.003},
       [dec("cotton", "면화 수매", "정부가 올해 면화를 시세보다 비싸게 사들입니다. 농장주들의 저택에서 축배가 오갑니다.",
            "generic_fundraising", 50, 6),
        dec("review", "주 방위군 사열", "회색 군복의 주 방위군이 애틀랜타 거리를 행진합니다. 농장주 가문의 아들들이 말을 타고 선두에 섭니다.",
            "generic_army_support", 30, 4, war(0.02)),
        dec("railways", "남부 철도 부설", "목화밭과 항구를 잇는 철도를 새로 놓습니다. 철도 회사의 주주 명단은 원로원 의원 명단과 거의 같습니다.",
            "generic_train", 80, 3, civ(1), infra(1), days=120),
        dec("labour", "북부 노동자 통제", "점령한 북부 공장에 남부 출신 감독관을 보내 파업을 막습니다. 생산량은 그대로이고 불만은 늘었습니다.",
            "generic_police_action", 40, 5, stab(0.02), days=90)]),
]}

# Focus -> (index, change). Focuses raise their route's index.
GAINS = {
    "LR_USA_royal_garrison": ("loyalty", 5), "LR_USA_coercive_acts": ("loyalty", 5), "LR_USA_conciliation": ("loyalty", 15),
    "LR_USA_loyalist_militia": ("loyalty", 5), "LR_USA_crown_peace": ("loyalty", 10), "LR_USA_oath": ("loyalty", 10),
    "LR_USA_mexican_viceroyalty": ("loyalty", 5), "LR_USA_union_parliament": ("loyalty", 10),
    "LR_CNA_morning": ("union", 5), "LR_CNA_convention": ("union", 10), "LR_CNA_bill_of_rights": ("union", 10),
    "LR_CNA_federal_treasury": ("union", 5), "LR_CNA_after_shots": ("union", 15), "LR_CNA_western_rail": ("union", 5),
    "LR_CNA_continent_of_liberty": ("union", 10),
    "LR_CNA_acting_president": ("order", 5), "LR_CNA_martial_law": ("order", 15), "LR_CNA_dialogue": ("order", 15),
    "LR_CNA_emergency_currency": ("order", 10),
    "LR_CNA_junta": ("army", 5), "LR_CNA_west_point": ("army", 10), "LR_CNA_final_offensive": ("army", 5),
    "LR_CNA_generalissimo": ("army", 10), "LR_CNA_peerage": ("army", 10), "LR_CNA_imperial_army": ("army", 10),
    "LR_AMC_council": ("plan", 5), "LR_AMC_detroit_arsenal": ("plan", 5), "LR_AMC_union": ("plan", 5),
    "LR_AMC_five_year_plan": ("plan", 15), "LR_AMC_electrification": ("plan", 10),
    "LR_LNG_every_man": ("popularity", 5), "LR_LNG_share_clubs": ("popularity", 5), "LR_LNG_restored_usa": ("popularity", 5),
    "LR_LNG_share_our_wealth": ("popularity", 15), "LR_LNG_national_radio": ("popularity", 10),
    "LR_DXE_confederacy": ("planters", 5), "LR_DXE_cotton_bonds": ("planters", 5), "LR_DXE_csa": ("planters", 5),
    "LR_DXE_constitution": ("planters", 10), "LR_DXE_planter_senate": ("planters", 15),
}
# Focus -> (index, at least). Later focuses of a route need its index.
NEEDS = {
    "LR_USA_join_league": ("loyalty", 50), "LR_USA_union_bill": ("loyalty", 60), "LR_USA_sun_never_sets": ("loyalty", 70),
    "LR_CNA_manifest_destiny": ("union", 55), "LR_CNA_northern_brothers": ("union", 65),
    "LR_CNA_crowned_general": ("army", 55), "LR_CNA_old_grudge": ("army", 70),
    "LR_AMC_liberation": ("plan", 50), "LR_AMC_second_capital": ("plan", 70),
    "LR_LNG_presidential_congress": ("popularity", 50), "LR_LNG_kings_nation": ("popularity", 70),
    "LR_DXE_golden_circle": ("planters", 60), "LR_DXE_caribbean_empire": ("planters", 70),
}


def gain(key, n):
    """An effect that moves an index, with a readable tooltip."""
    tip = f"LR_tt_usa_mg_{key}_{'m' if n < 0 else ''}{abs(n)}"
    colour = "G" if n > 0 else "R"
    TOOLTIPS[tip] = f"{MINIGAMES[key]['name']} §{colour}{'+' if n > 0 else ''}{n}§!"
    return (f"custom_effect_tooltip = {tip}\nhidden_effect = {{\n\tadd_to_variable = {{ {MINIGAMES[key]['var']} = {n} }}\n"
            f"\tlr_usa_mg_{key}_update = yes\n}}")


def need(key, n):
    tip = f"LR_tt_usa_need_{key}_{n}"
    name = MINIGAMES[key]["name"]
    particle = "이" if (ord(name[-1]) - 0xAC00) % 28 else "가"  # 받침이 있으면 '이'
    TOOLTIPS[tip] = f"{name}{particle} {n} 이상"
    return f"custom_trigger_tooltip = {{\n\ttooltip = {tip}\n\tcheck_variable = {{ {MINIGAMES[key]['var']} > {n - 1} }}\n}}"


def start(key): return f"lr_usa_mg_{key}_start = yes"
def stop(key): return f"lr_usa_mg_{key}_stop = yes"
