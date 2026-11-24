"""America's regions and Congress (2026-11-25): build_america.py writes what render() returns.

Regions: every American country (the colony, the Congress and the civil war's factions) keeps a support index, 0 to
100, for each of nine regions it holds. Each region leans toward some governments and away from others (LEAN, added
every month), and drifts back toward 50. Its states get a bonus above 65 and a penalty below 35, and the average sets
national stability and political power. Each region has its own three decisions: a political one (support), a
development one (buildings in that region) and a stabilising one.

Congress: a democratic America has a House (435 seats) and a Senate (96 seats) with a government share in each. A
majority makes the government stronger; without one it is weaker, and the bills in BILLS (focuses) cannot pass. Each
bill spends some of the majority. Midterm elections every two years reseat both houses from the ruling party's
popularity and the regions' support.

Text follows docs/STYLE_GUIDE.md: decisions and descriptions in the polite style.
"""
from split_states import expand

TAGS = ["USA", "CNA", "AMC", "LNG", "DXE"]
IDEOLOGIES = ["democratic", "communism", "fascism", "neutrality"]


def region(key, name, states, start, lean, desc, decisions):
    return dict(key=key, name=name, states=expand(states), start=start, lean=dict(zip(IDEOLOGIES, lean)), desc=desc,
                decisions=decisions)


def d(did, name, desc, icon, cost, gain, kind=None, days=90):
    """kind: None (support only), 'stab', or a building ('industrial_complex', 'arms_factory', 'dockyard', 'infrastructure')."""
    return dict(id=did, name=name, desc=desc, icon=icon, cost=cost, gain=gain, kind=kind, days=days)


# lean: monthly support per government (democratic, communism, fascism, neutrality)
REGIONS = [
    region("new_england", "뉴잉글랜드", [357], 50, (0.6, -0.3, -0.5, 0.0),
           "보스턴의 상인 가문과 회중교회의 마을들은 백 년이 넘도록 타운 미팅에서 스스로 일을 정해 왔습니다. 이곳 사람들은 의회와 법을 존중하고, 위에서 내려오는 명령은 그만큼 의심합니다.",
           [d("town_meetings", "타운 미팅 순회", "정부 각료들이 뉴잉글랜드의 작은 마을을 돌며 타운 미팅에 참석합니다. 질문은 날카롭지만, 질문을 받아 주었다는 것만으로도 마을 사람들은 고개를 끄덕입니다.",
              "generic_political_discourse", 35, 10),
            d("mills", "방직 공장 현대화", "로웰과 맨체스터의 오래된 방직 공장에 새 기계를 들입니다. 백 년 된 벽돌 건물 안에서 처음으로 전동 직기가 돌아갑니다.",
              "generic_factory", 80, 5, "industrial_complex", 120),
            d("harvard", "대학과 손잡기", "하버드와 MIT의 교수들을 정부 위원회에 앉힙니다. 학자들이 정부 편에 서자 보스턴의 신문 논조가 눈에 띄게 부드러워집니다.",
              "generic_research", 50, 6, "stab")]),
    region("mid_atlantic", "중부 대서양", [358, 359, 360], 45, (0.3, 0.2, -0.3, -0.2),
           "뉴욕의 은행과 필라델피아의 공장, 그리고 그 사이를 메운 이민자 동네가 이 나라의 돈과 사람을 쥐고 있습니다. 표는 구역마다 정치 조직이 모으고, 그 조직은 대가 없이 움직이지 않습니다.",
           [d("machine", "정치 조직과의 거래", "뉴욕과 필라델피아의 구역 보스들에게 일자리와 계약을 약속합니다. 그들이 움직이면 다음 선거 날 투표소 앞에 줄이 생깁니다.",
              "generic_political_rally", 45, 12),
            d("wall_street", "월가의 공채 인수", "월가의 은행들이 정부 공채를 인수하는 대신 항만과 철도 사업의 지분을 받습니다. 허드슨강 하구에 새 부두가 들어섭니다.",
              "generic_construction", 90, 4, "industrial_complex", 120),
            d("immigrants", "이민자 구제 사업", "로어이스트사이드와 사우스필라델피아의 공동주택에 무료 진료소와 야간 학교를 엽니다. 이탈리아어와 이디시어로 된 감사 편지가 시청에 쌓입니다.",
              "generic_welfare", 40, 7, "stab")]),
    region("chesapeake", "체서피크", [361, 362, 816], 50, (0.2, -0.4, 0.1, 0.3),
           "버지니아와 메릴랜드의 오래된 지주 가문들은 독립 전쟁 이전부터 이 땅을 다스려 왔습니다. 웨스트버지니아의 탄광촌은 그 가문들과 사이가 나쁘지만, 함께 체서피크만의 항구로 석탄을 내보냅니다.",
           [d("tidewater", "타이드워터 가문의 만찬", "제임스강 변의 오래된 저택에서 지주 가문의 가장들과 만찬을 엽니다. 은 식기 사이로 오간 약속은 다음 주 주 의회에서 표가 됩니다.",
              "generic_political_discourse", 35, 10),
            d("norfolk", "노퍽 조선소 확장", "노퍽과 볼티모어의 조선소에 새 선대를 놓습니다. 탄광촌의 젊은이들이 조선소로 내려와 용접공이 됩니다.",
              "generic_naval", 90, 5, "dockyard", 120),
            d("coal_strike", "탄광 분쟁 조정", "웨스트버지니아 탄광의 노사 대표를 한자리에 앉히고 정부가 중재안을 내놓습니다. 총을 든 경비대가 탄광 입구에서 물러납니다.",
              "generic_civil_support", 45, 7, "stab")]),
    region("great_lakes", "오대호 공업지대", [261, 393, 394, 395, 396], 45, (0.1, 0.6, -0.2, -0.4),
           "디트로이트의 자동차, 피츠버그와 클리블랜드의 철강, 시카고의 도살장과 철도가 모인 곳입니다. 공장 노동자들은 노동조합으로 뭉쳐 있고, 그들의 파업 한 번이면 나라 전체의 생산이 멈춥니다.",
           [d("unions", "노조 지도부 회동", "자동차 노조와 철강 노조의 지도부를 정부 청사로 부릅니다. 임금 인상 약속 한 줄이 파업 결의문 열 장을 거두어들입니다.",
              "generic_political_rally", 45, 12),
            d("assembly_lines", "조립 라인 증설", "디트로이트의 자동차 공장 옆에 군수품 조립 라인을 새로 깝니다. 트럭을 만들던 손이 이제 포탄을 만듭니다.",
              "generic_industry", 100, 4, "arms_factory", 120),
            d("company_towns", "회사 마을 개혁", "공장 주변의 회사 마을에서 회사 상점과 회사 경찰을 없앱니다. 노동자들은 처음으로 월급을 자기가 고른 가게에서 씁니다.",
              "generic_welfare", 40, 7, "stab")]),
    region("upper_south", "내륙 남부", [363, 368, 369], 45, (0.0, -0.3, 0.3, 0.3),
           "애팔래치아 산맥의 골짜기마다 오래된 가문과 오래된 원한이 있습니다. 담배밭과 탄광, 위스키 증류소가 생계를 떠받치고, 사람들은 정부보다 이웃과 교회를 먼저 믿습니다.",
           [d("revival", "천막 부흥회 지원", "여름마다 골짜기를 도는 천막 부흥회에 정부가 천막과 발전기를 대 줍니다. 설교자들이 기도 끝에 정부를 위한 축복을 한 줄 덧붙입니다.",
              "generic_speech", 30, 9),
            d("dams", "테네시강 댐 사업", "테네시강과 컴벌랜드강에 댐을 쌓고 발전소를 세웁니다. 등잔불을 켜던 골짜기에 처음으로 전깃불이 들어옵니다.",
              "generic_electricity", 100, 6, "industrial_complex", 150),
            d("moonshine", "밀주 단속 완화", "골짜기 증류소에 대한 단속을 늦추고 대신 세금을 조금 받습니다. 연방 단속관과 산골 사람들 사이의 총격이 눈에 띄게 줄어듭니다.",
              "generic_police_action", 25, 6, "stab")]),
    region("deep_south", "딥사우스", [364, 365, 366, 367, 370, 371], 40, (-0.3, -0.8, 0.3, 0.6),
           "목화밭과 사탕수수밭, 농장주의 저택과 소작인의 오두막이 이어지는 땅입니다. 농장주 가문들이 주 의회를 쥐고 있고, 흑인 소작인들은 투표소에 가는 길부터 막혀 있습니다.",
           [d("planters", "농장주 의회와의 타협", "농장주 가문의 대표들에게 목화 가격 지지를 약속합니다. 그들은 대가로 주 의회의 표를 내놓지만, 소작인들의 사정은 조금도 달라지지 않습니다.",
              "generic_political_discourse", 35, 10),
            d("gulf_ports", "멕시코만 항구 정비", "뉴올리언스와 모빌의 부두를 넓히고 새 기중기를 들입니다. 목화를 싣던 부두에서 이제 군수품도 실려 나갑니다.",
              "generic_construction", 90, 4, "infrastructure", 120),
            d("sharecroppers", "소작인 구제", "소작인 가족들에게 종자와 농기구를 빌려주는 정부 기금을 만듭니다. 농장주들은 반발하지만, 들판의 소요는 잦아듭니다.",
              "generic_welfare", 50, 5, "stab")]),
    region("plains", "대평원", [372, 373, 374, 383, 384, 389, 390, 391, 392], 45, (0.0, 0.1, 0.5, -0.3),
           "밀과 옥수수가 지평선까지 이어지는 땅입니다. 모래 폭풍과 곡물 가격 폭락이 몇 해째 농민들을 괴롭혔고, 농민들은 협동조합으로 뭉쳐 동부의 은행과 철도 회사를 원망합니다.",
           [d("grain_price", "곡물 가격 지지", "정부가 밀과 옥수수를 정해진 값에 사들이겠다고 발표합니다. 경매에 넘어갈 뻔한 농장들이 한 해를 더 버팁니다.",
              "generic_political_rally", 45, 12),
            d("rural_roads", "농촌 도로망", "농장과 곡물 창고, 철도역을 잇는 자갈길을 놓습니다. 곡물을 싣고 진흙탕에서 빠져나오지 못하던 트럭들이 이제 하루에 두 번 오갑니다.",
              "generic_construction", 80, 5, "infrastructure", 120),
            d("shelterbelt", "방풍림 조성", "평원 한가운데 수백 마일에 걸쳐 나무를 심어 모래 폭풍을 막습니다. 나무 심는 일자리를 얻은 농민의 아들들이 정부를 다시 봅니다.",
              "generic_forestry", 40, 7, "stab")]),
    region("mountain_west", "산악 서부", [381, 382, 387, 388], 50, (0.2, 0.0, 0.2, 0.0),
           "로키산맥의 광산촌과 목장이 띄엄띄엄 흩어진 땅입니다. 구리와 은을 캐는 광부들과 소를 치는 목장주들은 서로를 좋아하지 않지만, 동부에서 온 관리를 싫어한다는 점에서는 한마음입니다.",
           [d("ranchers", "목장주 협회 회동", "덴버의 목장주 협회 연례 회의에 정부 각료가 참석해 방목지 사용료를 깎아 주겠다고 약속합니다. 카우보이모자들이 일제히 박수를 칩니다.",
              "generic_political_discourse", 35, 10),
            d("mines", "광산 철도 부설", "뷰트와 리드빌의 광산에서 본선 철도까지 지선을 놓습니다. 노새가 끌던 광석 수레 대신 화물 열차가 산을 내려갑니다.",
              "generic_train", 80, 5, "industrial_complex", 120),
            d("miners", "광부 안전법", "갱도 붕괴와 가스 폭발을 막는 안전 규정을 법으로 만듭니다. 광부 노조가 처음으로 정부 발표를 환영하는 성명을 냅니다.",
              "generic_civil_support", 40, 7, "stab")]),
    region("pacific", "태평양 연안", [385, 386], 50, (0.3, 0.2, -0.2, 0.0),
           "시애틀과 포틀랜드의 항구, 컬럼비아강의 목재소와 연어 통조림 공장이 모인 곳입니다. 대륙 반대편의 수도는 멀고, 이곳 사람들은 태평양 건너의 무역에 더 관심이 많습니다.",
           [d("longshoremen", "부두 노동자 협약", "시애틀과 포틀랜드의 부두 노동자 노조와 고용 협약을 맺습니다. 부두마다 멈춰 있던 기중기가 다시 움직입니다.",
              "generic_political_rally", 40, 11),
            d("puget_sound", "퓨젓사운드 조선소", "퓨젓사운드의 해군 조선소를 넓히고 새 건선거를 팝니다. 목재소에서 일하던 사람들이 조선소로 옮겨 갑니다.",
              "generic_naval", 90, 5, "dockyard", 120),
            d("columbia", "컬럼비아강 개발", "컬럼비아강에 댐을 쌓아 전기와 물을 끌어옵니다. 메마른 동부 워싱턴의 땅에 처음으로 수로가 놓입니다.",
              "generic_electricity", 60, 6, "stab")]),
]

# Focuses that are bills before Congress: a democratic government needs a House majority, and each spends seats.
BILLS = {"LR_CNA_bill_of_rights": 10, "LR_CNA_federal_treasury": 10, "LR_CNA_western_rail": 15, "LR_CNA_continental_navy": 15,
         "LR_CNA_promise_1778": 20, "LR_CNA_manifest_destiny": 25, "LR_LNG_share_our_wealth": 20, "LR_LNG_presidential_congress": 25}

CONGRESS_DECISIONS = [
    d("whip", "원내 표 단속", "원내 총무가 의원 사무실을 하나씩 돌며 다음 표결의 표를 셉니다. 망설이던 의원 몇은 지역구 우체국장 자리 하나에 마음을 정합니다.",
      "generic_political_discourse", 50, 15, days=60),
    d("pork", "지역구 예산 끼워 넣기", "법안 끝에 의원들의 지역구 다리와 우체국 예산을 붙입니다. 신문은 돼지 여물통이라 비웃지만, 법안은 통과됩니다.",
      "generic_construction", 75, 25, days=90),
    d("senate_deal", "상원 원로와의 거래", "상원 외교위원장을 백악관 저녁 식사에 초대합니다. 그는 디저트가 나오기 전에 자기 주의 군사 기지 이야기를 꺼냅니다.",
      "generic_political_rally", 50, 4, days=90),
    d("fireside", "노변담화", "대통령이 라디오 앞에 앉아 국민에게 직접 법안을 설명합니다. 다음 날 의원 사무실마다 법안을 통과시키라는 편지가 쏟아집니다.",
      "generic_speech", 60, 8, days=120),
]


def tab(text, n=1):
    pad = "\t" * n
    return "\n".join(pad + line if line else line for line in text.split("\n"))


def in_region(r):
    return "OR = { " + " ".join(f"state = {s}" for s in r["states"]) + " }"


def holds(r):
    return f"any_owned_state = {{ {in_region(r)} }}"


def var(r):
    return f"LR_usa_reg_{r['key']}"


def american():
    return "OR = { " + " ".join(f"tag = {t}" for t in TAGS) + " }"


def building(r, kind):
    if kind == "infrastructure":
        return (f"every_owned_state = {{\n\tlimit = {{ {in_region(r)} is_controlled_by = ROOT }}\n\trandom_select_amount = 2\n"
                f"\tadd_building_construction = {{\n\t\ttype = infrastructure\n\t\tlevel = 1\n\t\tinstant_build = yes\n\t}}\n}}")
    coastal = " is_coastal = yes" if kind == "dockyard" else ""
    return (f"random_owned_controlled_state = {{\n\tlimit = {{ {in_region(r)}{coastal} }}\n\tadd_extra_state_shared_building_slots = 1\n"
            f"\tadd_building_construction = {{\n\t\ttype = {kind}\n\t\tlevel = 1\n\t\tinstant_build = yes\n\t}}\n}}")


def gain_region(r, n):
    return f"add_to_variable = {{ {var(r)} = {n} }}\nclamp_variable = {{ var = {var(r)} min = 0 max = 100 }}"


# ------------------------------------------------------------------------------------------------------------
def effects():
    init = "\n".join(f"set_variable = {{ {var(r)} = {r['start']} }}" for r in REGIONS)
    out = [f"lr_usa_regions_init = {{\n\tif = {{\n\t\tlimit = {{ NOT = {{ has_country_flag = LR_usa_regions }} }}\n\t\tset_country_flag = LR_usa_regions\n"
           f"{tab(init, 2)}\n\t\tadd_dynamic_modifier = {{ modifier = LR_usa_regions }}\n\t}}\n}}"]
    monthly = ["lr_usa_regions_init = yes", "set_variable = { LR_usa_reg_sum = 0 }", "set_variable = { LR_usa_reg_count = 0 }"]
    for r in REGIONS:
        v = var(r)
        lean = "\n".join(f"if = {{ limit = {{ has_government = {ideo} }} add_to_variable = {{ {v} = {x} }} }}" for ideo, x in r["lean"].items() if x)
        body = f"""{lean}
set_temp_variable = {{ lr_drift = {v} }}
subtract_from_temp_variable = {{ lr_drift = 50 }}
multiply_temp_variable = {{ lr_drift = 0.03 }}
subtract_from_variable = {{ {v} = lr_drift }}
clamp_variable = {{ var = {v} min = 0 max = 100 }}
add_to_variable = {{ LR_usa_reg_sum = {v} }}
add_to_variable = {{ LR_usa_reg_count = 1 }}
every_owned_state = {{
	limit = {{ {in_region(r)} }}
	if = {{
		limit = {{ ROOT = {{ check_variable = {{ {v} > 64 }} }} }}
		if = {{ limit = {{ NOT = {{ has_dynamic_modifier = {{ modifier = LR_usa_reg_loyal }} }} }} add_dynamic_modifier = {{ modifier = LR_usa_reg_loyal }} }}
		if = {{ limit = {{ has_dynamic_modifier = {{ modifier = LR_usa_reg_unrest }} }} remove_dynamic_modifier = {{ modifier = LR_usa_reg_unrest }} }}
	}}
	else_if = {{
		limit = {{ ROOT = {{ check_variable = {{ {v} < 35 }} }} }}
		if = {{ limit = {{ NOT = {{ has_dynamic_modifier = {{ modifier = LR_usa_reg_unrest }} }} }} add_dynamic_modifier = {{ modifier = LR_usa_reg_unrest }} }}
		if = {{ limit = {{ has_dynamic_modifier = {{ modifier = LR_usa_reg_loyal }} }} remove_dynamic_modifier = {{ modifier = LR_usa_reg_loyal }} }}
	}}
	else = {{
		if = {{ limit = {{ has_dynamic_modifier = {{ modifier = LR_usa_reg_loyal }} }} remove_dynamic_modifier = {{ modifier = LR_usa_reg_loyal }} }}
		if = {{ limit = {{ has_dynamic_modifier = {{ modifier = LR_usa_reg_unrest }} }} remove_dynamic_modifier = {{ modifier = LR_usa_reg_unrest }} }}
	}}
}}"""
        monthly.append(f"if = {{\n\tlimit = {{ {holds(r)} }}\n{tab(body)}\n}}")
    popularity = "\n".join(f"if = {{ limit = {{ has_government = {i} }} add_popularity = {{ ideology = {i} popularity = 0.005 }} }}" for i in IDEOLOGIES)
    monthly.append(f"""set_variable = {{ LR_usa_reg_avg = 50 }}
if = {{
	limit = {{ check_variable = {{ LR_usa_reg_count > 0 }} }}
	set_variable = {{ LR_usa_reg_avg = LR_usa_reg_sum }}
	divide_variable = {{ LR_usa_reg_avg = LR_usa_reg_count }}
}}
set_variable = {{ LR_usa_reg_stab = LR_usa_reg_avg }}
subtract_from_variable = {{ LR_usa_reg_stab = 50 }}
multiply_variable = {{ LR_usa_reg_stab = 0.003 }}
set_variable = {{ LR_usa_reg_pp = LR_usa_reg_avg }}
subtract_from_variable = {{ LR_usa_reg_pp = 50 }}
multiply_variable = {{ LR_usa_reg_pp = 0.008 }}
# Well-held regions win the ruling party votes; a country in revolt loses them.
if = {{
	limit = {{ check_variable = {{ LR_usa_reg_avg > 60 }} }}
{tab(popularity)}
}}""")
    out.append("lr_usa_regions_monthly = {\n\tif = {\n\t\tlimit = { " + american() + " }\n" + tab("\n".join(monthly), 2) + "\n\t}\n}")

    # Congress
    out.append("""lr_usa_congress_monthly = {
	if = {
		limit = {
			has_government = democratic
			NOT = { has_country_flag = LR_usa_congress }
		}
		set_country_flag = LR_usa_congress
		set_variable = { LR_usa_house = 230 }
		set_variable = { LR_usa_senate = 50 }
		set_variable = { LR_usa_cg_months = 0 }
		add_dynamic_modifier = { modifier = LR_usa_congress }
	}
	if = {
		limit = {
			has_country_flag = LR_usa_congress
			NOT = { has_government = democratic }
		}
		clr_country_flag = LR_usa_congress
		remove_dynamic_modifier = { modifier = LR_usa_congress }
	}
	if = {
		limit = { has_country_flag = LR_usa_congress }
		add_to_variable = { LR_usa_cg_months = 1 }
		if = {
			limit = { check_variable = { LR_usa_cg_months > 23 } }
			set_variable = { LR_usa_cg_months = 0 }
			lr_usa_congress_election = yes
			news_event = { id = lr_usacg.1 }
		}
		lr_usa_congress_update = yes
	}
}

# Seats from the ruling party's popularity (half) and the regions' support (half), with a little luck.
lr_usa_congress_election = {
	set_temp_variable = { lr_share = party_popularity@democratic }
	multiply_temp_variable = { lr_share = 0.5 }
	set_temp_variable = { lr_reg = LR_usa_reg_avg }
	multiply_temp_variable = { lr_reg = 0.005 }
	add_to_temp_variable = { lr_share = lr_reg }
	set_temp_variable = { lr_luck = random }
	multiply_temp_variable = { lr_luck = 0.1 }
	subtract_from_temp_variable = { lr_luck = 0.05 }
	add_to_temp_variable = { lr_share = lr_luck }
	set_variable = { LR_usa_house = lr_share }
	multiply_variable = { LR_usa_house = 435 }
	round_variable = LR_usa_house
	set_variable = { LR_usa_senate = lr_share }
	multiply_variable = { LR_usa_senate = 96 }
	round_variable = LR_usa_senate
	lr_usa_congress_update = yes
}

lr_usa_congress_update = {
	clamp_variable = { var = LR_usa_house min = 0 max = 435 }
	clamp_variable = { var = LR_usa_senate min = 0 max = 96 }
	set_variable = { LR_usa_cg_pp = LR_usa_house }
	subtract_from_variable = { LR_usa_cg_pp = 218 }
	multiply_variable = { LR_usa_cg_pp = 0.002 }
	set_variable = { LR_usa_cg_stab = LR_usa_senate }
	subtract_from_variable = { LR_usa_cg_stab = 48 }
	multiply_variable = { LR_usa_cg_stab = 0.002 }
}""")
    return "\n\n".join(out)


def modifiers():
    return """LR_usa_regions = {
	enable = { always = yes }
	icon = GFX_idea_generic_pp_unity_bonus
	stability_factor = LR_usa_reg_stab
	political_power_gain = LR_usa_reg_pp
}

LR_usa_reg_loyal = {
	enable = { always = yes }
	icon = GFX_idea_generic_pp_unity_bonus
	state_production_speed_buildings_factor = 0.15
	state_resources_factor = 0.1
}

LR_usa_reg_unrest = {
	enable = { always = yes }
	icon = GFX_idea_generic_disjointed_gov
	state_production_speed_buildings_factor = -0.2
	state_resources_factor = -0.15
}

LR_usa_congress = {
	enable = { always = yes }
	icon = GFX_idea_generic_democratic_drift_bonus
	political_power_gain = LR_usa_cg_pp
	stability_factor = LR_usa_cg_stab
}
"""


def categories():
    return ("LR_usa_cat_regions = {\n\ticon = generic_political_actions\n\tpriority = 55\n"
            f"\tallowed = {{ {american()} }}\n\tvisible = {{ has_country_flag = LR_usa_regions }}\n}}\n\n"
            "LR_usa_cat_congress = {\n\ticon = generic_democracy\n\tpriority = 58\n"
            f"\tallowed = {{ {american()} }}\n\tvisible = {{ has_country_flag = LR_usa_congress }}\n}}\n")


def decisions():
    regions = []
    for r in REGIONS:
        for x in r["decisions"]:
            effects = [gain_region(r, x["gain"])]
            if x["kind"] == "stab":
                effects.append("add_stability = 0.02")
            elif x["kind"]:
                effects.append(building(r, x["kind"]))
            regions.append(f"""\tLR_usa_reg_{r['key']}_{x['id']} = {{
\t\ticon = {x['icon']}
\t\tcost = {x['cost']}
\t\tdays_re_enable = {x['days']}
\t\tvisible = {{ {holds(r)} }}
\t\tcomplete_effect = {{
{tab(chr(10).join(effects), 3)}
\t\t}}
\t\tai_will_do = {{
\t\t\tbase = 1
\t\t\tmodifier = {{ add = 4 check_variable = {{ {var(r)} < 40 }} }}
\t\t}}
\t}}""")
    congress = []
    for x in CONGRESS_DECISIONS:
        if x["id"] == "senate_deal":
            effect = f"add_to_variable = {{ LR_usa_senate = {x['gain']} }}"
        elif x["id"] == "fireside":
            effect = f"add_to_variable = {{ LR_usa_house = {x['gain']} }}\nadd_popularity = {{ ideology = democratic popularity = 0.03 }}"
        else:
            effect = f"add_to_variable = {{ LR_usa_house = {x['gain']} }}"
        if x["id"] == "pork":
            effect += "\nadd_stability = -0.01"
        congress.append(f"""\tLR_usa_cg_{x['id']} = {{
\t\ticon = {x['icon']}
\t\tcost = {x['cost']}
\t\tdays_re_enable = {x['days']}
\t\tcomplete_effect = {{
{tab(effect, 3)}
\t\t\tlr_usa_congress_update = yes
\t\t}}
\t\tai_will_do = {{
\t\t\tbase = 1
\t\t\tmodifier = {{ add = 5 check_variable = {{ LR_usa_house < 218 }} }}
\t\t}}
\t}}""")
    return "LR_usa_cat_regions = {\n" + "\n".join(regions) + "\n}\n\nLR_usa_cat_congress = {\n" + "\n".join(congress) + "\n}\n"


def events():
    return """add_namespace = lr_usacg

news_event = {
	id = lr_usacg.1
	title = lr_usacg.1.t
	desc = lr_usacg.1.d
	picture = GFX_news_event_election_vote
	major = no
	is_triggered_only = yes
	option = {
		name = lr_usacg.1.a
	}
}
"""


def link_bills(by_id):
    """Each bill needs a House majority under a democratic government and spends some of it."""
    for fid, cost in BILLS.items():
        item = by_id[fid]
        need = ("custom_trigger_tooltip = {\n\ttooltip = LR_tt_usa_congress_majority\n\tOR = {\n\t\tNOT = { has_country_flag = LR_usa_congress }\n"
                "\t\tcheck_variable = { LR_usa_house > 217 }\n\t}\n}")
        item["available"] = "\n".join(x for x in (item["available"], need) if x)
        item["effects"] = tuple(item["effects"]) + (
            f"if = {{\n\tlimit = {{ has_country_flag = LR_usa_congress }}\n\tadd_to_variable = {{ LR_usa_house = -{cost} }}\n\tlr_usa_congress_update = yes\n"
            f"\tcustom_effect_tooltip = LR_tt_usa_bill_{cost}\n}}",)


def loc():
    out = {}
    lines = []
    for r in REGIONS:
        lines.append(f"§Y{r['name']}§!: [?ROOT.{var(r)}|0]")
        for x in r["decisions"]:
            out[f"LR_usa_reg_{r['key']}_{x['id']}"] = f"{r['name']}: {x['name']}"
            out[f"LR_usa_reg_{r['key']}_{x['id']}_desc"] = r["desc"] + "\n\n" + x["desc"]
    out["LR_usa_cat_regions"] = "지역 민심"
    out["LR_usa_cat_regions_desc"] = ("이 대륙은 한 나라라 부르기에는 너무 넓고, 지역마다 바라는 정부가 다릅니다. 지역의 민심은 0에서 100 사이에서 움직이며, "
                                      "정부의 성향에 따라 오르거나 내리고 시간이 지나면 50으로 돌아갑니다. 65를 넘는 지역의 주는 건설과 자원이 늘고, 35 아래로 떨어진 지역의 주는 줄어듭니다. "
                                      "가진 지역의 평균이 나라의 안정도와 정치력을 정하고, 평균이 60을 넘으면 집권당의 지지율이 오릅니다.\n\n"
                                      + "\n".join(lines) + "\n\n평균: [?ROOT.LR_usa_reg_avg|0]")
    out["LR_usa_regions"] = "지역 민심"
    out["LR_usa_reg_loyal"] = "정부를 지지하는 지역"
    out["LR_usa_reg_unrest"] = "정부에 등 돌린 지역"
    out["LR_usa_cat_congress"] = "연방 의회"
    out["LR_usa_cat_congress_desc"] = ("민주 정부는 의회의 다수 없이 법을 만들 수 없습니다. 하원 435석 가운데 218석을 넘기면 정부가 힘을 얻고, 그 아래로 떨어지면 법안이 막히고 정치력이 줄어듭니다. "
                                       "상원의 의석은 나라의 안정도를 움직입니다. 법안 중점을 통과시킬 때마다 하원의 표가 조금씩 빠져나가고, "
                                       "2년마다 치르는 중간선거는 집권당의 지지율과 지역 민심으로 의석을 다시 나눕니다.\n\n"
                                       "§Y하원§!: [?ROOT.LR_usa_house|0] / 435 (과반 218)\n§Y상원§!: [?ROOT.LR_usa_senate|0] / 96 (과반 49)\n"
                                       "다음 선거까지: [?ROOT.LR_usa_cg_months|0] / 24개월")
    out["LR_usa_congress"] = "연방 의회"
    for x in CONGRESS_DECISIONS:
        out[f"LR_usa_cg_{x['id']}"] = x["name"]
        out[f"LR_usa_cg_{x['id']}_desc"] = x["desc"]
    out["LR_tt_usa_congress_majority"] = "민주 정부라면 하원 과반(218석)이 필요하다"
    for cost in sorted(set(BILLS.values())):
        out[f"LR_tt_usa_bill_{cost}"] = f"법안 통과에 하원 표 §R{cost}§!석을 쓴다"
    out["lr_usacg.1.t"] = "중간선거 결과 발표"
    out["lr_usacg.1.d"] = ("2년 만의 중간선거가 끝났습니다. 개표는 밤새 이어졌고, 각 지역의 결과가 전신으로 수도에 모였습니다. "
                           "새 의회에서 정부를 지지하는 의원은 하원 [?ROOT.LR_usa_house|0]석, 상원 [?ROOT.LR_usa_senate|0]석입니다. "
                           "정치 평론가들은 지역마다 갈린 표심을 두고 정부가 어느 지역의 마음을 얻었고 어느 지역을 잃었는지 따지는 기사를 쏟아내고 있습니다.")
    out["lr_usacg.1.a"] = "새 의회와 일할 준비를 합니다."
    return out
