"""What makes France's focuses differ from each other: tangible rewards, choices, links between
branches, events placed along the branches, special orders and focus lengths.
build_france.py applies these tables after the trees are built.
"""


def stock(kind, amount):
    return f"add_equipment_to_stockpile = {{\n\ttype = {kind}\n\tamount = {amount}\n}}"


def build_at(state, kind, level, slots=False):
    extra = f"\tadd_extra_state_shared_building_slots = {level}\n" if slots else ""
    return f"{state} = {{\n{extra}\tadd_building_construction = {{\n\t\ttype = {kind}\n\t\tlevel = {level}\n\t\tinstant_build = yes\n\t}}\n}}"


def resource(kind, amount, state):
    return f"add_resource = {{\n\ttype = {kind}\n\tamount = {amount}\n\tstate = {state}\n}}"


def tech(name, category, bonus=0.5):
    return f"add_tech_bonus = {{\n\tname = {name}\n\tbonus = {bonus}\n\tuses = 1\n\tcategory = {category}\n}}"


def corps(name, count, experience=0.4, width=3):
    """Named formations of plain infantry; they exist from the day the focus ends."""
    regiments = "\n".join(f"\t\tinfantry = {{ x = {x} y = {y} }}" for x in range(width) for y in range(3))
    return (f"division_template = {{\n\tname = \"{name}\"\n\tregiments = {{\n{regiments}\n\t}}\n}}\n"
            f"for_loop_effect = {{\n\tend = {count}\n\tcreate_unit = {{\n"
            f"\t\tdivision = \"division_template = \\\"{name}\\\" start_experience_factor = {experience}\"\n\t\towner = FRA\n\t}}\n}}")


def order(flag):
    return f"set_country_flag = {flag}"


def friend(tag):
    return f"{tag} = {{ add_opinion_modifier = {{ target = ROOT modifier = medium_increase }} }}"


# Rewards added on top of what a focus already gives.
REWARDS = {
    # Shared economy.
    "LR_FRA_war_reparations": ["add_manpower = 10000"],
    "LR_FRA_royal_arsenal": [stock("infantry_equipment", 3000)],
    "LR_FRA_steelworks": [resource("steel", 12, 28)],
    "LR_FRA_tunisia_morocco": [resource("chromium", 4, 461)],
    "LR_FRA_ports": [build_at(14, "infrastructure", 1), build_at(21, "infrastructure", 1)],
    "LR_FRA_royal_academy": [tech("LR_FRA_royal_academy", "electronics")],
    "LR_FRA_synthetic_fuel": [build_at(32, "synthetic_refinery", 1, True), "add_fuel = 20000"],
    "LR_FRA_trade_treaties": [friend("SWI"), friend("HOL")],
    "LR_FRA_war_economy": [stock("support_equipment", 800), order("LR_ord_fuel")],
    "LR_FRA_stabilise_franc": ["add_political_power = 50"],
    "LR_FRA_nord_coal": [build_at(29, "fuel_silo", 1, True)],
    "LR_FRA_citroen_trucks": [stock("motorized_equipment", 500)],
    "LR_FRA_lyon_chemicals": [build_at(32, "fuel_silo", 1, True), resource("rubber", 4, 32)],
    "LR_FRA_research_network": ["add_research_slot = 1"],
    "LR_FRA_arsenal_of_republic": [stock("artillery_equipment", 1500)],
    # Army.
    "LR_FRA_lessons_of_defeat": ["add_command_power = 20"],
    "LR_FRA_rifle_stocks": [stock("infantry_equipment", 5000)],
    "LR_FRA_artillery_school": [stock("artillery_equipment", 300)],
    "LR_FRA_general_staff": ["add_command_power = 25", order("LR_ord_manoeuvres")],
    "LR_FRA_staff_college": ["army_experience = 25"],
    "LR_FRA_armoured_recon": [stock("motorized_equipment", 300)],
    "LR_FRA_colonial_regiments": ["add_manpower = 30000", corps("Tirailleurs Coloniaux", 3, 0.3)],
    "LR_FRA_foreign_legion": [corps("Legion Etrangere", 2, 0.7), order("LR_ord_legion")],
    "LR_FRA_chasseurs_alpins": [corps("Chasseurs Alpins", 2, 0.5, 2), build_at(851, "anti_air_building", 1)],
    "LR_FRA_combat_engineers": [stock("support_equipment", 500)],
    "LR_FRA_radio_net": [build_at(16, "radar_station", 1)],
    "LR_FRA_revenge_army": ["add_manpower = 40000"],
    "LR_FRA_ready_for_war": [stock("anti_tank_equipment", 500), stock("anti_air_equipment", 500)],
    "LR_FRA_general_mobilisation": ["add_manpower = 150000", stock("infantry_equipment", 15000)],
    # Navy.
    "LR_FRA_new_navy": ["navy_experience = 15", order("LR_ord_shipyards")],
    "LR_FRA_mers_el_kebir": [build_at(461, "infrastructure", 1)],
    "LR_FRA_fusiliers_marins": [corps("Fusiliers Marins", 2, 0.5, 2)],
    "LR_FRA_convoy_school": [tech("LR_FRA_convoy_school", "naval_equipment")],
    "LR_FRA_submarine_arm": [tech("LR_FRA_submarine_arm", "naval_equipment")],
    # Air.
    "LR_FRA_air_arm": [build_at(16, "air_base", 2)],
    "LR_FRA_air_safety": [build_at(32, "air_base", 2)],
    "LR_FRA_air_detection": [build_at(17, "radar_station", 1), build_at(29, "anti_air_building", 2)],
    "LR_FRA_dewoitine_fighters": [tech("LR_FRA_dewoitine_fighters", "air_equipment")],
    "LR_FRA_potez_bombers": [tech("LR_FRA_potez_bombers", "air_equipment"), build_at(19, "air_base", 2)],
    "LR_FRA_paratroopers": [corps("Parachutistes", 2, 0.6, 2)],
    # Orleans.
    "LR_ORL_labour_service": ["add_manpower = 20000"],
    "LR_ORL_veterans": [corps("Vieux Soldats", 2, 0.6), order("LR_ord_review")],
    "LR_ORL_secret_staff": ["add_command_power = 30"],
    "LR_ORL_autarky": [resource("steel", 8, 29), resource("aluminium", 6, 22)],
    "LR_ORL_officers_oath": ["add_command_power = 15"],
    "LR_ORL_ottoman_talks": [friend("TUR")],
    "LR_ORL_royal_security": ["add_political_power = 50"],
    # Bourbon.
    "LR_BOU_reims": [order("LR_ord_progress")],
    "LR_BOU_swiss_guard": [corps("Gardes Suisses", 2, 0.7)],
    "LR_BOU_guilds": [stock("support_equipment", 300)],
    "LR_BOU_colonial_talks": ["add_political_power = 25", friend("ENG")],
    "LR_BOU_mediterranean_pact": [friend("TTS")],
    "LR_BOU_church": ["add_manpower = 15000"],
    # Commune.
    "LR_COM_red_guards": [corps("Gardes Rouges", 4, 0.1)],
    "LR_COM_workers_control": [order("LR_ord_subbotnik")],
    "LR_COM_land_reform": ["add_manpower = 40000"],
    "LR_COM_workers_university": [tech("LR_COM_workers_university", "electronics")],
    "LR_COM_national_guard": [corps("Garde Nationale", 4, 0.2)],
    "LR_COM_collective_farms": ["add_manpower = 30000"],
    "LR_COM_red_volunteers": [stock("infantry_equipment", 8000)],
    "LR_COM_workers_embassy": [friend("SOV")],
    # Montagnards.
    "LR_JAC_public_housing": ["add_manpower = 20000"],
    "LR_JAC_majority": [order("LR_ord_subscription")],
    "LR_JAC_womens_vote": ["add_manpower = 30000"],
    "LR_JAC_dutch_treaty": [friend("HOL")],
    "LR_JAC_citizen_police": [corps("Gardes Civiques", 2, 0.2)],
    # Girondins.
    "LR_GIR_bourse": [order("LR_ord_bonds")],
    "LR_GIR_free_ports": [build_at(19, "infrastructure", 1), resource("rubber", 6, 19)],
    "LR_GIR_merchant_envoys": [friend("POR")],
    "LR_GIR_atlantic_trade": [resource("tungsten", 4, 14)],
    "LR_GIR_civic_guard": [corps("Milices Provinciales", 3, 0.2)],
    # Feuillants.
    "LR_MAR_chartered_works": [resource("steel", 6, 32)],
    "LR_MAR_senate": [order("LR_ord_royal_tour")],
    "LR_MAR_london_model": [friend("ENG")],
    "LR_MAR_bourgeois_guard": [corps("Garde Bourgeoise", 3, 0.3)],
    # Napoleon.
    "LR_NAP_legion_of_honour": ["add_command_power = 30"],
    "LR_NAP_bank_of_france": ["add_political_power = 50"],
    "LR_NAP_marshals": ["add_command_power = 50", corps("Grenadiers", 3, 0.6)],
    "LR_NAP_imperial_guard": [corps("Garde Imperiale", 4, 0.8), order("LR_ord_conscription")],
    "LR_NAP_old_guard": [corps("Vieille Garde", 2, 0.9)],
    "LR_NAP_continental_system": [resource("steel", 10, 16)],
    "LR_GUA_public_education": ["add_research_slot = 1"],
    "LR_GUA_civilian_control": ["add_political_power = 50"],
    "LR_GUA_citizen_army": ["add_manpower = 60000"],
    "LR_GUA_amnesty": ["add_manpower = 20000"],
}

# A bonus only for those who walked the other road first.
SYNERGY = {
    "LR_FRA_war_economy": ("LR_FRA_mass_production", [stock("infantry_equipment", 5000)]),
    "LR_FRA_tank_divisions": ("LR_FRA_citroen_trucks", [stock("motorized_equipment", 300)]),
    "LR_FRA_char_b": ("LR_FRA_steelworks", ["army_experience = 25"]),
    "LR_FRA_battleline": ("LR_FRA_ports", ["navy_experience = 50"]),
    "LR_FRA_bomber_command": ("LR_FRA_synthetic_fuel", ["add_fuel = 15000"]),
    "LR_FRA_general_mobilisation": ("LR_FRA_rural_power", ["add_manpower = 50000"]),
    "LR_ORL_tear_up_treaty": ("LR_ORL_secret_staff", ["add_command_power = 40"]),
    "LR_ORL_renault_seized": ("LR_ORL_autarky", [stock("motorized_equipment", 500)]),
    "LR_BOU_family_council": ("LR_BOU_church", ["add_political_power = 75"]),
    "LR_BOU_latin_league": ("LR_BOU_family_pact", [friend("POR")]),
    "LR_COM_five_year_plan": ("LR_COM_workers_university", ["add_research_slot = 1"]),
    "LR_COM_red_volunteers": ("LR_COM_red_guards", [corps("Brigades Internationales", 3, 0.4)]),
    "LR_JAC_arms_nationalised": ("LR_JAC_labour_code", [stock("artillery_equipment", 500)]),
    "LR_JAC_supermajority": ("LR_JAC_womens_vote", ["add_political_power = 100"]),
    "LR_GIR_rail_privatised": ("LR_GIR_bourse", ["add_political_power = 75"]),
    "LR_GIR_supermajority": ("LR_GIR_provincial_power", ["add_political_power = 100"]),
    "LR_MAR_supermajority": ("LR_MAR_kings_return", ["add_political_power = 100"]),
    "LR_NAP_grande_armee": ("LR_NAP_legion_of_honour", ["add_command_power = 50"]),
    "LR_GUA_constitution": ("LR_GUA_suffrage", ["add_political_power = 75"]),
}

# Mutually exclusive roads. Parents listed in OR_PARENTS are opened up so both roads still lead on.
EXCLUSIVE = [
    ("LR_FRA_cruiser_squadron", "LR_FRA_destroyer_flotillas"),
    ("LR_FRA_cas_wings", "LR_FRA_strategic_force"),
    ("LR_ORL_youth", "LR_ORL_veterans"),
    ("LR_ORL_ottoman_talks", "LR_ORL_latin_front"),
    ("LR_BOU_poor_relief", "LR_BOU_guilds"),
    ("LR_BOU_provincial_estates", "LR_BOU_peers"),
    ("LR_COM_electrification", "LR_COM_five_year_plan"),
    ("LR_JAC_forty_hours", "LR_JAC_paid_leave"),
    ("LR_GIR_free_trade", "LR_GIR_tax_cut"),
    ("LR_MAR_gendarmerie", "LR_MAR_suppress"),
]
OR_PARENTS = {
    "LR_FRA_battleline": [("LR_FRA_cruiser_squadron", "LR_FRA_destroyer_flotillas")],
    "LR_ORL_tear_up_treaty": [("LR_ORL_press_control", "LR_ORL_secret_staff")],
    "LR_BOU_diplomatic_rearm": [("LR_BOU_poor_relief", "LR_BOU_guilds")],
    "LR_BOU_open_rearm": [("LR_BOU_poor_relief", "LR_BOU_guilds")],
    "LR_BOU_family_council": [("LR_BOU_provincial_estates", "LR_BOU_peers")],
    "LR_GIR_rail_privatised": [("LR_GIR_bourse", "LR_GIR_tariffs_down")],
    "LR_MAR_uproot": [("LR_MAR_gendarmerie", "LR_MAR_suppress")],
}
# Branches that wait on each other without drawing a line across the tree.
GATES = {
    "LR_FRA_tank_divisions": ["LR_FRA_steelworks"],
    "LR_FRA_battleline": ["LR_FRA_ports"],
    "LR_FRA_synthetic_fuel": ["LR_FRA_rebuild_railways"],
    "LR_FRA_strategic_force": ["LR_FRA_mass_production"],
    "LR_FRA_naval_aviation": ["LR_FRA_air_arm"],
    "LR_FRA_paratroopers": ["LR_FRA_chasseurs_alpins"],
    "LR_ORL_renault_seized": ["LR_ORL_officers_oath"],
    "LR_ORL_tear_up_treaty": ["LR_ORL_radical_rearm"],
    "LR_ORL_royal_security": ["LR_ORL_press_control"],
    "LR_BOU_peasant_credit": ["LR_BOU_church"],
    "LR_BOU_swiss_guard": ["LR_BOU_family_pact"],
    "LR_COM_five_year_plan": ["LR_COM_council"],
    "LR_COM_electrification": ["LR_COM_council"],
    "LR_COM_peoples_army": ["LR_COM_council"],
    "LR_JAC_arms_nationalised": ["LR_JAC_majority"],
    "LR_JAC_free_press": ["LR_JAC_public_school"],
    "LR_GIR_credit_lyonnais": ["LR_GIR_majority"],
    "LR_GIR_hudson_loans": ["LR_GIR_free_ports"],
    "LR_MAR_civil_law": ["LR_MAR_order"],
    "LR_MAR_hague_arbitration": ["LR_MAR_civil_law"],
    "LR_NAP_imperial_works": ["LR_NAP_imperial_nobility"],
    "LR_GUA_truth_commission": ["LR_GUA_suffrage"],
}

# Days a focus takes, in weeks. Anything not listed is judged by what it does (see focus_weeks).
WEEKS = {
    "LR_FRA_the_kings_peace": 2, "LR_FRA_lessons_of_defeat": 4, "LR_FRA_war_reparations": 5,
    "LR_FRA_ready_for_war": 12, "LR_FRA_general_mobilisation": 14, "LR_FRA_arsenal_of_republic": 16,
    "LR_FRA_war_economy": 14, "LR_FRA_research_network": 12, "LR_FRA_royal_academy": 10,
    "LR_FRA_foreign_legion": 7, "LR_FRA_saint_cyr": 8, "LR_FRA_fusiliers_marins": 7, "LR_FRA_bearn_carrier": 14,
    "LR_ORL_tear_up_treaty": 6, "LR_BOU_reims": 8, "LR_BOU_family_council": 10, "LR_COM_land_reform": 9,
    "LR_COM_economic_plan": 12, "LR_COM_world_republic": 12, "LR_JAC_supermajority": 12, "LR_GIR_supermajority": 12,
    "LR_MAR_supermajority": 12, "LR_MAR_kings_return": 8, "LR_NAP_coronation": 6, "LR_NAP_guardian": 6, "LR_NAP_civil_code": 12,
}


FOCUS_SPEED = 0.6  # Everything takes this share of the times below.


def focus_weeks(fid, effects, spine, last_chapters):
    if fid.startswith("LR_CRI_"):
        return 1  # The crisis moves fast: one week a focus.
    return max(1, round(base_weeks(fid, effects, spine, last_chapters) * FOCUS_SPEED))


def base_weeks(fid, effects, spine, last_chapters):
    if fid in WEEKS:
        return WEEKS[fid]
    if fid in last_chapters:
        return 9
    if fid in spine:
        return 5
    text = "\n".join(effects)
    if "declare_war_on" in text:
        return 3
    if "lr_fra_uproot" in text:
        return 14
    if "create_unit" in text:
        return 7
    levels = sum(int(n) for n in __import__("re").findall(r"type = (?:arms_factory|industrial_complex|dockyard)\n\s*level = (\d+)", text))
    if levels:
        return 6 + 2 * min(levels, 4)
    if "add_research_slot" in text:
        return 11
    if "add_tech_bonus" in text:
        return 6
    if "add_opinion_modifier" in text or "add_to_faction" in text:
        return 4
    if "LR_seats" in text:
        return 5
    if "experience" in text:
        return 5
    if "lr_fra_op_reduce" in text:
        return 6
    return 8


# Special orders opened by focuses: key, flag, icon, cost, days until usable again, name, text, effects.
ORDERS = [
    ("legion", "LR_ord_legion", "generic_military", 40, 120, "외인부대 모집", "시디벨아베스에 지원자가 줄을 섭니다. 정예 사단 1개를 편성합니다.", corps("Legion Etrangere", 1, 0.7)),
    ("manoeuvres", "LR_ord_manoeuvres", "generic_army_support", 35, 90, "대규모 기동 훈련", "참모본부가 샹파뉴 평원에서 사단을 움직여 봅니다. 육군 경험치 +30, 지휘력 +15.", "army_experience = 30\nadd_command_power = 15"),
    ("shipyards", "LR_ord_shipyards", "generic_industry", 40, 120, "해군 긴급 발주", "조선소에 초과 근무를 시킵니다. 해군 경험치 +30.", "navy_experience = 30"),
    ("fuel", "LR_ord_fuel", "generic_fundraising", 30, 90, "연료 비축 명령", "민간 소비를 줄여 전략 비축유를 쌓습니다. 연료 +20000.", "add_fuel = 20000"),
    ("review", "LR_ord_review", "generic_speech", 25, 60, "왕의 사열", "왕이 노병들 앞을 지나갑니다. 전쟁 지지도 +3%.", "add_war_support = 0.03"),
    ("progress", "LR_ord_progress", "generic_nationalism", 30, 90, "왕실 순행", "왕이 지방 도시를 돕니다. 안정도 +3%.", "add_stability = 0.03"),
    ("subbotnik", "LR_ord_subbotnik", "generic_factory", 30, 90, "토요 자원 노동", "노동자들이 쉬는 날 공장에 나옵니다. 소총 4000정을 비축합니다.", stock("infantry_equipment", 4000)),
    ("subscription", "LR_ord_subscription", "generic_civil_support", 20, 90, "공화국 국민 모금", "시민들이 재건 기금에 돈을 냅니다. 경제 재건 +1.", "add_to_variable = { LR_rec_focus = 1 }\nlr_fra_sync_industry = yes"),
    ("bonds", "LR_ord_bonds", "generic_fundraising", 15, 120, "철도 채권 발행", "파리 증권거래소에서 채권을 모집합니다. 정치력 +60, 경제 재건 +1.", "add_political_power = 60\nadd_to_variable = { LR_rec_focus = 1 }\nlr_fra_sync_industry = yes"),
    ("royal_tour", "LR_ord_royal_tour", "generic_political_discourse", 30, 90, "입헌 왕의 순방", "왕이 내각과 함께 지방을 돕니다. 의석 +24.", "add_to_variable = { LR_seats = 24 }\nlr_fra_sync_seats = yes"),
    ("conscription", "LR_ord_conscription", "generic_military", 40, 90, "황제의 징집령", "황제가 또 한 번 젊은이들을 부릅니다. 인력 +50000, 안정도 -2%.", "add_manpower = 50000\nadd_stability = -0.02"),
]

ROUTE_FAMILIES = {
    "king": ("LR_route_orleans", "LR_route_bourbon"),
    "commune": ("LR_route_communist",),
    "republic": ("LR_route_jacobin", "LR_route_girondin", "LR_route_marais"),
    "emperor": ("LR_route_empire",),
    "guardian": ("LR_route_guardian",),
}
# The speech when a war focus ends. Target: event number, picture, title, text by family, options.
WAR_EVENTS = {
    "ALG": (1201, "soldiers_marching", "지중해를 다시 건너다", {
        "king": "알제항으로 향하는 수송선마다 왕의 깃발이 걸렸습니다. 왕을 몰아낼 뻔한 그 땅으로 왕의 군대가 돌아갑니다. 마르세유 부두의 여인들은 이번에는 손을 흔들지 않습니다.",
        "commune": "코뮌의 함대가 알제로 향합니다. 왕의 전쟁을 끝낸 혁명이 왕의 전쟁을 다시 시작한다는 비난이 시청 앞에 나붙었습니다. 위원회는 이것은 식민 전쟁이 아니라 통일이라고 답합니다.",
        "republic": "의회가 표결로 파병을 승인했습니다. 왕정을 무너뜨린 바로 그 전쟁입니다. 찬성표를 던진 의원들은 투표 뒤 기자들을 피해 뒷문으로 나갔습니다.",
    }, [
        ("이번에는 끝을 본다.", {"war_support_factor": 0.03}),
        ("빠르게 끝내고 사면을 약속한다.", {"stability_factor": 0.02, "op": 1}),
    ]),
    "GER": (1202, "france_parade", "라인강으로", {
        "king": "왕이 말에 올라 군대 앞에 섰습니다. 1918년의 항복 문서를 쓴 공화주의자들은 이제 없습니다. 왕은 알자스의 흙 한 줌을 쥐고 베를린 쪽을 가리킵니다. 유럽은 다시 전쟁입니다.",
        "commune": "동무들이여, 이것은 프랑스와 독일의 전쟁이 아닙니다. 혁명과 왕들의 전쟁입니다. 라인강 건너 공장의 노동자들에게 뿌릴 전단이 포탄보다 먼저 실렸습니다.",
        "republic": "총리가 의사당에서 선전포고문을 읽습니다. 공화국은 복수하러 가는 것이 아니라 해방하러 간다고 합니다. 의원들은 일어서서 라 마르세예즈를 부르고, 창밖에서 신병들이 행진합니다.",
        "emperor": "황제가 지도에서 눈을 들었습니다. 대육군, 행군. 그 두 마디로 유럽의 평화는 끝났습니다. 원수들은 이미 말 위에 있습니다.",
        "guardian": "대통령이 군복을 다시 입었습니다. 임기 중에 입지 않겠다고 약속한 옷입니다. 그는 의회의 승인을 받은 뒤에야 참모본부로 향했습니다.",
    }, [
        ("베를린까지 멈추지 마라.", {"war_support_factor": 0.04, "army_morale_factor": 0.02}),
        ("우리 땅을 되찾는 것이 먼저다.", {"stability_factor": 0.03, "army_org_factor": 0.02}),
    ]),
    "AUS": (1203, "soldiers_marching", "빈으로", {
        "king": "합스부르크는 프랑스를 무릎 꿇린 승전국 가운데 가장 오래된 왕가입니다. 부르봉과 합스부르크의 싸움은 400년이나 되었습니다. 왕의 사절이 빈에 선전포고문을 전했습니다.",
        "commune": "민족의 감옥에 혁명의 문을 냅니다. 체코와 헝가리, 크로아티아의 혁명가들이 파리 방송을 듣고 있습니다. 왕관을 쓴 마지막 노인에게 선전포고가 전달되었습니다.",
        "republic": "공화국이 합스부르크 제국에 선전포고합니다. 빈 체제 이후 한 세기 동안 유럽의 자유주의자를 가둔 나라입니다. 신문은 이탈리아와 헝가리의 해방을 말합니다.",
        "emperor": "황제의 군대가 다시 도나우강으로 향합니다. 아우스터리츠라는 이름이 이번 전쟁에서 처음 지도에 표시되었습니다. 황제는 빈의 궁전을 어떻게 쓸지 벌써 생각합니다.",
        "guardian": "대통령은 오스트리아 신민들에게 보내는 공개 서한과 함께 선전포고문을 냈습니다. 당신들의 황제에게 전쟁을 선포합니다, 당신들에게가 아니라.",
    }, [
        ("제국을 해체한다.", {"war_support_factor": 0.03}),
        ("체코와 헝가리에 사절을 보낸다.", {"political_power_gain": 0.03}),
    ]),
    "ENG": (1204, "sailors_in_working_rig", "해협 건너로", {
        "king": "왕이 영국 귀족 공화국에 선전포고했습니다. 백년전쟁 이래 언제나 저 섬이 문제였습니다. 왕의 함대는 아직 충분하지 않지만, 왕의 인내는 이미 바닥났습니다.",
        "commune": "런던의 귀족 의회에 선전포고합니다. 맨체스터의 차티스트들이 일어서기를 기다리며, 코뮌의 함대가 브레스트를 떠납니다.",
        "republic": "프랑스 공화국이 해협 건너의 귀족 공화국에 선전포고합니다. 공화국끼리의 전쟁이라고 런던 신문이 비웃습니다. 총리는 우리는 시민의 공화국이라고 답했습니다.",
        "emperor": "불로뉴 숙영지에 나팔이 울립니다. 황제는 해협을 바라보며 맑은 날 사흘이면 된다고 말합니다. 넬슨의 후예들은 이미 바다에 나와 있습니다.",
        "guardian": "대통령은 해협을 건너는 것이 평화로 가는 유일한 길이라고 의회를 설득했습니다. 표결은 간신히 통과되었습니다. 해군 장관은 표결 결과를 듣기 전에 출항 명령을 내렸습니다.",
    }, [
        ("해군을 모두 건다.", {"war_support_factor": 0.03, "raw": ["navy_experience = 50"]}),
        ("하늘부터 빼앗는다.", {"political_power_gain": 0.02, "raw": ["air_experience = 50"]}),
    ]),
    "SOV": (1205, "generic_battle", "동쪽의 적", {
        "king": "러시아는 프랑스의 옛 동맹이었고, 함께 졌습니다. 이제 케렌스키의 공화국은 왕들의 유럽에 남은 마지막 큰 위협입니다. 왕의 사절이 페테르부르크로 떠났습니다.",
        "republic": "공화국이 또 하나의 공화국에 선전포고합니다. 케렌스키는 의회 연단에서 프랑스의 배신을 규탄했습니다. 눈이 오기 전에 끝내야 한다고 참모본부는 말합니다.",
        "emperor": "황제가 러시아 지도를 펼칩니다. 측근들은 겨울 이야기를 꺼내지 않습니다. 대육군이 니에멘강을 건넙니다. 이 이름은 어쩐지 불길합니다.",
        "guardian": "대통령은 이 전쟁만큼은 하고 싶지 않았다고 말합니다. 그러나 동쪽 국경이 안전하지 않으면 공화국도 없다고 합니다. 장군들은 겨울 군복 주문부터 넣었습니다.",
    }, [
        ("겨울 전에 끝낸다.", {"army_morale_factor": 0.03}),
        ("겨울 장비부터 챙긴다.", {"raw": ["add_equipment_to_stockpile = {\n\ttype = support_equipment\n\tamount = 800\n}"]}),
    ]),
}

# Events along the branches. Focus, picture, title, text, options; options as in france_story.py, with "raw" for plain effects.
BRANCH_EVENTS = [
    # Shared.
    ("LR_FRA_war_reparations", "generic_sign_treaty1", "런던의 회계사들", "배상 위원회의 영국인 회계사가 파리 재무부 금고를 확인하러 왔습니다. 그가 가져온 일정대로면 프랑스는 1980년까지 배상금을 냅니다. 재무장관은 장부를 두 권 준비했습니다.", [
        ("진짜 장부를 보여 주고 동정을 산다.", {"raw": ["add_political_power = 50"]}),
        ("가짜 장부를 내민다. 모자라는 돈은 조선소로 간다.", {"raw": ["navy_experience = 25", "add_stability = -0.02"]}),
    ]),
    ("LR_FRA_steelworks", "generic_factory", "로렌의 굴뚝", "낭시의 제철소들이 다시 불을 지핍니다. 문제는 숙련공입니다. 대전쟁에서 살아 돌아온 사람이 많지 않습니다. 사장들은 이탈리아 이민자를 쓰자고 하고, 노조는 프랑스인을 먼저 뽑으라고 합니다.", [
        ("이민자를 받는다. 강철에는 국적이 없다.", {"mil": 1, "raw": ["add_stability = -0.01"]}),
        ("제대 군인을 재교육한다. 느리더라도.", {"raw": ["add_manpower = 10000", "add_stability = 0.01"]}),
    ]),
    ("LR_FRA_general_staff", "military_planning", "젊은 대령의 메모", "참모본부 개편 위원회에 드골이라는 대령이 메모를 보내왔습니다. 전차를 분산하지 말고 한데 모으자는 내용입니다. 페탱 원수는 메모를 끝까지 읽지 않았습니다. 위원회는 어느 쪽 의견을 들을지 묻습니다.", [
        ("대령의 메모를 돌려 읽게 한다.", {"raw": ["army_experience = 25"]}),
        ("원수의 경험을 존중한다.", {"raw": ["add_command_power = 25"]}),
    ]),
    ("LR_FRA_new_navy", "sailors_in_working_rig", "제독의 예산안", "해군 참모총장이 조선 계획을 들고 왔습니다. 항공모함이 미래인가, 전함이 체면인가. 조약은 둘 다 금지하고, 예산은 하나만 허락합니다.", [
        ("전함은 나라의 얼굴이다.", {"raw": ["navy_experience = 40"]}),
        ("베아른호를 고쳐 쓴다. 비행기가 답이다.", {"raw": ["air_experience = 40"]}),
    ]),
    ("LR_FRA_air_arm", "generic_read_write", "이스트르 비행장의 추락", "시험 비행 중이던 신형기가 파리 교외에 추락했습니다. 신문은 조약 위반보다 조종사 장례식을 크게 다룹니다. 항공 장관은 비행을 계속할지 결정해야 합니다.", [
        ("설계부터 다시 한다.", {"raw": ["add_stability = 0.01", "air_experience = 15"]}),
        ("계속 난다. 조종사는 그 일을 알고 왔다.", {"raw": ["air_experience = 40", "add_war_support = 0.01"]}),
    ]),
    ("LR_FRA_ready_for_war", "military_planning", "금고에서 나온 계획", "참모본부 금고에서 동원 계획 제17호를 꺼냈습니다. 1914년의 계획을 고쳐 쓴 것입니다. 젊은 장교들은 이 계획으로 또 진다고 말합니다. 시간은 충분하지 않습니다.", [
        ("처음부터 다시 쓴다.", {"raw": ["add_command_power = 40"]}),
        ("철도표는 믿을 만하다. 고쳐 쓰면 된다.", {"raw": ["add_manpower = 50000"]}),
    ]),
    # Orleans.
    ("LR_ORL_family_allowance", "generic_read_write", "요람과 대포", "다자녀 수당의 재원이 모자랍니다. 왕실 회의는 대포 예산을 건드릴 수 없다고 하고, 내무장관은 사라진 세대를 메우지 않으면 20년 뒤 대포 쏠 사람이 없다고 합니다.", [
        ("요람이 먼저다.", {"stability_factor": 0.02, "raw": ["add_manpower = 15000"]}),
        ("20년 뒤는 없다. 대포가 먼저다.", {"stability_factor": -0.01}),
    ]),
    ("LR_ORL_press_control", "journalists_speech", "르 피가로의 사설", "왕의 검열관이 지운 자리를 신문사가 흰 칸으로 남겨 발행했습니다. 파리 시민들은 흰 칸을 보고 더 많이 수군거립니다. 편집장을 어떻게 할까요?", [
        ("체포하고 신문사를 접수한다.", {"political_power_gain": 0.02, "stability_factor": -0.01}),
        ("식사에 초대한다. 왕실 인터뷰도 주자.", {"stability_factor": 0.02}),
    ]),
    ("LR_ORL_radical_rearm", "france_tank_production", "르노의 항의", "루이 르노가 왕실 군수국에 항의문을 보냈습니다. 납품가가 원가의 절반이고, 트럭 라인을 전차로 돌리라는 명령은 파산하라는 말입니다. 왕의 장군들은 그를 체포하자고 합니다.", [
        ("값을 올려 준다. 공장은 사장이 돌린다.", {"mil": 1, "political_power_gain": -0.01}),
        ("공장은 왕의 것이다. 납품가는 그대로.", {"stability_factor": -0.01}),
    ]),
    # Bourbon.
    ("LR_BOU_family_pact", "generic_sign_treaty1", "사촌의 편지", "마드리드의 사촌이 친필 편지를 보냈습니다. 카를로스파가 북부에서 무기를 사 모으고 있으니 피레네 국경을 닫아 달라는 내용입니다. 카를로스파 쪽 대리인도 베르사유에 와 있습니다.", [
        ("국경을 닫는다. 왕은 왕을 돕는다.", {"friend": "SPR"}),
        ("두 쪽 모두에게 팔 것이 있다.", {"political_power_gain": 0.03}),
    ]),
    ("LR_BOU_church", "generic_read_write", "로마에서 온 사절", "교황 사절이 왕실 예배당에서 미사를 집전하고 싶어 합니다. 대신 프랑스 주교 임명권을 돌려 달라고 합니다. 갈리아 교회의 자유는 루이 14세도 포기하지 않았습니다.", [
        ("주교는 왕이 뽑는다.", {"political_power_gain": 0.03}),
        ("로마와 화해한다.", {"stability_factor": 0.03, "friend": "PAP"}),
    ]),
    ("LR_BOU_open_rearm", "france_tank_production", "베르사유의 포병대", "왕이 조약을 어기고 베르사유 궁전 앞마당에 야포를 늘어놓았습니다. 영국 대사가 항의하러 왔고, 궁정 사람들은 그를 샴페인으로 맞이합니다. 왕이 뭐라고 대답할까요?", [
        ("왕의 정원에 왕의 대포가 있을 뿐이다.", {"war_support_factor": 0.03}),
        ("불꽃놀이 준비였다고 전하라.", {"political_power_gain": 0.03}),
    ]),
    # Commune.
    ("LR_COM_land_reform", "generic_riot", "방데의 농민들", "방데의 농민들이 땅 문서를 받고도 코뮌 위원을 쫓아냈습니다. 그들에게 혁명은 여전히 교회를 닫는 사람들입니다. 위원회는 군대를 보낼지 신부를 돌려줄지 정해야 합니다.", [
        ("교회 문을 연다. 땅이 먼저다.", {"stability_factor": 0.03, "communism_drift": -0.01}),
        ("이번에는 방데도 혁명을 받아들인다.", {"op": 1, "stability_factor": -0.02}),
    ]),
    ("LR_COM_one_country", "generic_communist_congress", "국경의 동지들", "독일과 스페인의 동지들이 무기를 보내 달라고 간청합니다. 일국사회주의를 택한 코뮌은 이제 그들을 어떻게 대할까요?", [
        ("코뮌을 지키는 것이 세계 혁명을 지키는 것이다.", {"stability_factor": 0.03}),
        ("창고에 남는 소총은 보낸다.", {"communism_drift": 0.02, "raw": ["add_war_support = 0.02"]}),
    ]),
    ("LR_COM_world_revolution", "generic_communist_congress", "파리의 망명자들", "유럽 각지에서 쫓겨난 혁명가들이 파리 호텔을 메웁니다. 절반은 서로를 배신자라 부릅니다. 인터내셔널 집행부 자리는 하나뿐이고, 러시아 공화국 대사관도 이들을 눈여겨봅니다.", [
        ("프랑스 동지가 의장을 맡는다.", {"political_power_gain": 0.03}),
        ("모두에게 자리를 준다. 싸움은 지면으로 하라.", {"communism_drift": 0.03}),
    ]),
    # Montagnards.
    ("LR_JAC_forty_hours", "generic_strike", "공장의 새 시계", "주 40시간 법이 시행되자 군수 공장에서도 저녁 6시면 기계가 멈춥니다. 전쟁부 장관은 총리에게 말합니다. 왕들은 40시간만 일하지 않습니다.", [
        ("법은 법이다.", {"seats": 2, "stability_factor": 0.02}),
        ("군수 공장만 예외로 둔다.", {"mil": 1, "seats": -1}),
    ], "LR_JAC_paid_leave"),
    ("LR_JAC_labour_code", "generic_strike", "공장 점거", "노동법이 통과되기도 전에 노동자들이 공장을 점거했습니다. 사장들은 정부에 경찰을 요구하고, 노조는 공안위원회가 누구 편인지 묻습니다.", [
        ("점거는 파업의 일부로 인정한다.", {"seats": 3}),
        ("공장 문은 다시 열려야 한다.", {"stability_factor": 0.02, "dev": 1}),
    ]),
    ("LR_JAC_majority", "generic_parliament", "과반의 첫날", "산악파가 처음으로 혼자 과반을 넘었습니다. 복도에서 지롱드 의원이 묻습니다. 이제 우리를 어떻게 하실 겁니까. 1793년에는 답이 간단했습니다.", [
        ("상임위원장 자리를 나눈다.", {"stability_factor": 0.03}),
        ("이긴 쪽이 전부 갖는다.", {"political_power_gain": 0.04, "seats": 2}),
    ]),
    # Girondins.
    ("LR_GIR_deregulation", "generic_stock_traders", "규제 없는 빵값", "빵값 상한이 풀리자 파리 빵값이 첫 주에 40% 올랐습니다. 총리는 곧 내린다고 설명합니다. 시위대는 1789년 10월의 베르사유 행진 이야기를 꺼냅니다.", [
        ("시장을 믿는다.", {"dev": 2, "stability_factor": -0.02}),
        ("겨울 동안만 빵값을 다시 묶는다.", {"stability_factor": 0.02}),
    ]),
    ("LR_GIR_provincial_power", "generic_conference", "83개 데파르트망의 예산", "각 데파르트망 의회가 자기 예산을 쓰기 시작하자 도로가 데파르트망 경계에서 끊겼습니다. 옆 데파르트망과 합의가 안 됐다고 합니다. 파리는 웃지만 내각은 웃을 수 없습니다.", [
        ("데파르트망끼리 조정 위원회를 만들게 한다.", {"seats": 3}),
        ("간선 도로만은 중앙이 맡는다.", {"dev": 2, "seats": -1}),
    ]),
    ("LR_GIR_bourse", "generic_stock_traders", "외국 자본", "뉴욕과 암스테르담의 자본이 파리 증권거래소로 몰려옵니다. 그들이 원하는 것은 프랑스 철도 주식입니다. 내각 안에서도 군용 철도까지 팔아도 되느냐는 질문이 나왔습니다.", [
        ("돈에 국적을 묻지 않는다.", {"dev": 3, "political_power_gain": 0.01}),
        ("군용 노선은 뺀다.", {"stability_factor": 0.02, "war_support_factor": 0.01}),
    ]),
    # Feuillants.
    ("LR_MAR_constitution", "generic_parliament", "헌법 제1조", "입헌군주정 헌법 제1조에 프랑스 왕이라고 쓸 것인지 프랑스인의 왕이라고 쓸 것인지 의회가 나흘째 다툽니다. 한 글자 차이로 주권의 주인이 바뀝니다.", [
        ("프랑스인의 왕.", {"democratic_drift": 0.02, "seats": 3}),
        ("프랑스의 왕.", {"stability_factor": 0.03}),
    ]),
    ("LR_MAR_order", "gathering_protest", "흰 깃털과 붉은 깃발", "파리 교외에서 국민방위대와 노동자 시위대가 맞붙었습니다. 부상자가 100명입니다. 푀양파 의원들은 질서를, 산악파 의원들은 진상 조사를 요구합니다.", [
        ("방위대를 지지한다.", {"op": 1, "seats": -1}),
        ("지휘관을 해임하고 조사한다.", {"seats": 3, "stability_factor": 0.01}),
    ]),
    ("LR_MAR_senate", "generic_parliament", "상원의 첫 부결", "새 상원이 첫 법안으로 하원의 소득세 법안을 부결시켰습니다. 하원은 분노했고, 상원 의원들은 그것이 상원이 하는 일이라고 태연히 답합니다.", [
        ("상원을 지지한다.", {"political_power_gain": 0.03}),
        ("타협안을 만든다.", {"stability_factor": 0.02, "dev": 1}),
    ]),
    # Napoleon.
    ("LR_NAP_civil_code", "generic_read_write", "2,281개의 조문", "법전 초안이 올라왔습니다. 통령이 직접 회의를 주재하며 법률가들을 몰아세웁니다. 그가 끝까지 고치라고 한 조문은 상속과 이혼입니다. 이 법은 앞으로 유럽 절반이 베낄 것입니다.", [
        ("장남 상속을 없앤다.", {"stability_factor": 0.02, "democratic_drift": 0.01}),
        ("가장의 권위를 지킨다.", {"political_power_gain": 0.03}),
    ]),
    ("LR_NAP_grande_armee", "soldiers_marching", "불로뉴 숙영지", "대육군이 불로뉴에 모였습니다. 황제는 병사들 이름을 기억하고 귀를 잡아당깁니다. 원수들은 해협을 건널 배가 없다고 보고합니다. 황제는 그래도 훈련을 계속하라고 합니다.", [
        ("훈련은 전쟁의 절반이다.", {"experience_gain_army_factor": 0.03, "raw": ["army_experience = 40"]}),
        ("배를 지어라.", {"raw": ["navy_experience = 40"]}),
    ]),
    ("LR_GUA_suffrage", "election_vote", "첫 보통선거", "대통령이 약속한 대로 모든 시민이 투표합니다. 개표소를 지키는 병사들에게 대통령이 내린 명령은 단 하나입니다. 아무것도 하지 말 것. 군은 그 명령을 이해하지 못합니다.", [
        ("결과를 그대로 받아들인다.", {"seats": 4, "democratic_drift": 0.02}),
        ("대통령 지지 후보들을 조용히 돕는다.", {"seats": 8, "stability_factor": -0.02}),
    ]),
]
