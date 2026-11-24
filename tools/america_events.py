"""America's events, national spirits and the Korean text that goes with them. build_america.py writes them.

Scenes are in 해라체 from one person's view, news in plain 합쇼체 reports (docs/STYLE_GUIDE.md). Britain in this world is
the aristocratic republic: its government is the House of Lords (귀족 의회) and its chairman, never a king.
Paragraphs are separated by blank lines; build_america.py turns them into \\n\\n.
"""

# ------------------------------------------------------------------------------------------------------------
# National spirits: name -> (Korean name, description, picture, modifiers)
# ------------------------------------------------------------------------------------------------------------
IDEAS = {
    # The colonial government
    "LR_usa_coercive": ("강압법", "집회와 신문을 묶어 두었습니다. 거리는 조용해졌지만, 조용한 거리가 안전한 거리라고 믿는 관리는 많지 않습니다.",
                        "generic_oppression", {"political_power_gain": -0.1, "army_defence_factor": 0.05, "stability_factor": 0.05}),
    "LR_usa_conciliation": ("유화 칙령", "식민지 의회가 예산을 다시 심의하고, 식민지 출신 장교도 대령이 될 수 있습니다. 런던의 귀족 몇은 이것을 굴복이라고 부릅니다.",
                            "generic_constitutional_guarantees", {"stability_factor": 0.1, "political_power_gain": 0.1, "war_support_factor": -0.05}),
    "LR_usa_loyalist_militia": ("충성파 민병대", "런던을 조국으로 여기는 가문의 아들들이 총을 들었습니다. 그들은 이웃의 얼굴을 알고, 이웃도 그들의 얼굴을 압니다.",
                                "generic_reserve_divisions", {"army_defence_factor": 0.1, "conscription_factor": 0.03}),
    "LR_usa_crown_offensive": ("총독부의 공세", "총독부군이 본국의 증원을 기다리지 않고 먼저 움직입니다.",
                               "generic_war_preparation", {"army_attack_factor": 0.1, "army_org_factor": 0.05}),
    "LR_usa_hudson_line": ("허드슨 강 방어선", "허드슨 강변의 진지가 뉴잉글랜드와 남부의 반란군을 갈라놓습니다.",
                           "generic_fortify_the_borders", {"army_defence_factor": 0.15}),
    "LR_usa_blockaded": ("해상 봉쇄", "영국 대서양 함대가 항구를 막았습니다. 바다 건너에서 오는 것은 아무것도 없습니다.",
                         "generic_naval_invasion", {"industrial_capacity_factory": -0.1, "consumer_goods_factor": 0.05}),
    "LR_usa_crown_loyalty": ("제국에 대한 충성", "반란을 진압한 총독부는 제국의 가장 충실한 자치령임을 증명했습니다.",
                             "generic_pp_unity_bonus", {"stability_factor": 0.1, "war_support_factor": 0.05, "political_power_gain": 0.1}),
    "LR_usa_empire_partner": ("제국의 동반자", "북아메리카는 제국연맹 이사회에 상임 의석을 가졌습니다. 뉴욕의 목소리가 런던에서도 들립니다.",
                              "generic_license_production", {"industrial_capacity_factory": 0.1, "army_org_factor": 0.05, "political_power_gain": 0.1}),
    "LR_usa_viceroyalty": ("멕시코 총독령", "멕시코시티의 부왕궁에 유니언잭이 올랐습니다. 크리올로 귀족들은 새 주인에게 충성을 맹세했습니다.",
                           "generic_foreign_capital", {"industrial_capacity_factory": 0.05, "stability_factor": 0.05, "production_speed_buildings_factor": 0.1}),
    "LR_usa_heart_of_empire": ("제국의 심장", "북아메리카는 본국보다 크고, 본국보다 부유하며, 본국보다 많은 병사를 냅니다.",
                               "generic_economic_increase", {"industrial_capacity_factory": 0.1, "research_speed_factor": 0.05, "stability_factor": 0.05}),
    # The Congress
    "LR_usa_angry_colonies": ("분노한 식민지", "강압법은 1774년처럼 반란의 불을 더 크게 키웠습니다.",
                              "generic_morale_bonus", {"war_support_factor": 0.15, "army_morale_factor": 0.1, "conscription_factor": 0.05}),
    "LR_usa_hesitant_colonies": ("망설이는 식민지", "총독부의 유화 칙령 이후, 많은 식민지인이 아직 총을 들 때가 아니라고 생각합니다.",
                                 "generic_disjointed_gov", {"conscription_factor": -0.1, "stability_factor": -0.05}),
    "LR_usa_exposed_cells": ("드러난 조직", "총독부 정보국이 대륙 회의의 비밀 조직 여럿을 봉기 전에 찾아냈습니다.",
                             "generic_spy_intel", {"army_org_factor": -0.1, "political_power_gain": -0.1}),
    "LR_usa_hold_philadelphia": ("필라델피아 사수", "수도가 떠나면 혁명도 떠납니다. 대륙군은 필라델피아에서 물러서지 않습니다.",
                                 "generic_fortify_the_borders", {"army_defence_factor": 0.15}),
    "LR_usa_march_north": ("북부 진격", "대륙군이 허드슨 강 계곡을 따라 뉴욕으로 올라갑니다.",
                           "generic_war_preparation", {"army_attack_factor": 0.1}),
    "LR_usa_young_republic": ("젊은 공화국", "공화국은 이제 막 걸음마를 뗐습니다. 모든 것이 처음이고, 모든 사람이 무언가를 기대합니다.",
                              "generic_democratic_drift_bonus", {"political_power_gain": 0.15, "stability_factor": 0.1}),
    "LR_usa_bill_of_rights": ("권리장전", "언론과 집회와 종교의 자유가 헌법에 적혔습니다.",
                              "generic_constitutional_guarantees", {"stability_factor": 0.1, "democratic_drift": 0.05}),
    "LR_usa_monroe": ("먼로 선언", "아메리카 대륙은 더 이상 유럽 왕들의 사냥터가 아닙니다.",
                      "generic_flexible_foreign_policy", {"war_support_factor": 0.1, "political_power_gain": 0.05}),
    "LR_usa_liberty_continent": ("자유의 대륙", "북극해에서 리오그란데까지, 대륙의 대부분이 한 공화국의 헌법 아래 있습니다.",
                                 "generic_economic_increase", {"stability_factor": 0.1, "industrial_capacity_factory": 0.1, "research_speed_factor": 0.05}),
    # The crisis after Washington's murder
    "LR_usa_burning_streets": ("불타는 거리", "대통령이 죽은 뒤, 도시마다 시위와 폭동이 끊이지 않습니다. 사람들은 누가 대통령을 죽였는지를 두고 서로 멱살을 잡습니다.",
                               "generic_disjointed_gov", {"stability_factor": -0.2, "political_power_gain": -0.2}),
    "LR_usa_british_embargo": ("영국의 금수", "영국 귀족 의회가 파운드 결제를 막고 미국 상품에 4할의 관세를 매겼습니다. 공장의 삼분의 일이 멈출 판입니다.",
                               "generic_economic_crisis", {"industrial_capacity_factory": -0.2, "consumer_goods_factor": 0.1}),
    "LR_usa_embargo_eased": ("금수의 그늘", "새 지폐로 급한 불은 껐지만, 영국과의 교역은 아직 막혀 있습니다.",
                             "generic_mild_economic_recovery", {"industrial_capacity_factory": -0.1, "consumer_goods_factor": 0.05}),
    "LR_usa_red_agitation": ("붉은 선동", "문 닫은 공장 앞에서 붉은 깃발이 오릅니다. 노동자들은 공장이 일하는 사람의 것이라고 외칩니다.",
                             "generic_communism_drift_bonus", {"communism_drift": 0.1, "stability_factor": -0.05}),
    "LR_usa_martial_law": ("계엄령", "군이 도시를 순찰합니다. 거리는 조용해졌고, 군의 목소리는 커졌습니다.",
                           "generic_oppression", {"stability_factor": 0.15, "political_power_gain": -0.15}),
    # The civil war
    "LR_usa_brothers_war": ("형제의 전쟁", "대륙군의 장교들이 출신 주에 따라 갈라져 서로에게 총을 겨눕니다.",
                            "generic_usa_conflict", {"conscription_factor": 0.05, "war_support_factor": 0.2, "stability_factor": -0.1}),
    "LR_usa_order_remnant": ("남은 질서", "공화국이 무너지기 전까지 질서를 지킨 덕에 필라델피아의 군대는 흩어지지 않고 내전을 맞았습니다.",
                             "generic_army_war_college", {"army_org_factor": 0.1, "army_defence_factor": 0.1}),
    "LR_usa_appalachian_front": ("애팔래치아 전선", "애팔래치아 산맥이 필라델피아의 첫 방벽입니다.",
                                 "generic_mountain_defensive_training", {"army_defence_factor": 0.15}),
    "LR_usa_final_offensive": ("최후의 공세", "모든 전선에서 동시에 공세가 시작되었습니다.",
                               "generic_war_preparation", {"army_attack_factor": 0.15}),
    "LR_usa_red_offensive": ("평의회군의 남진", "평의회군이 오하이오 강을 건너 남쪽으로 내려갑니다.",
                             "generic_communist_army", {"army_attack_factor": 0.1, "army_org_factor": 0.05}),
    "LR_usa_prairie_offensive": ("미시시피 공세", "롱의 군대가 미시시피 강을 따라 내려갑니다.",
                                 "generic_war_preparation", {"army_attack_factor": 0.1, "army_org_factor": 0.05}),
    "LR_usa_atlanta_line": ("애틀랜타 참호선", "남부 철도의 교차점을 지키는 참호가 도시를 둘러쌌습니다.",
                            "generic_fortify_the_borders", {"army_defence_factor": 0.15}),
    "LR_usa_grey_offensive": ("회색 군대의 북진", "남부 연합군이 버지니아를 향해 북진합니다.",
                              "generic_war_preparation", {"army_attack_factor": 0.1, "army_org_factor": 0.05}),
    # The Amerigo Empire
    "LR_usa_peerage": ("제국 귀족원", "내전의 공신들이 작위를 받았습니다. 귀족원은 황제의 법안을 거부하지 않습니다.",
                       "generic_king_handled", {"stability_factor": 0.15, "political_power_gain": 0.1}),
    "LR_usa_imperial_army": ("제국 육군", "황제가 직접 쓴 교범을 외운 장교들이 제국 육군을 이끕니다.",
                             "generic_army_war_college", {"army_attack_factor": 0.1, "army_org_factor": 0.1}),
    "LR_usa_amerigo_millennium": ("아메리고 천년", "신대륙의 주인이 된 제국은 천 년을 이어 가겠다고 선언했습니다.",
                                  "generic_production_bonus", {"industrial_capacity_factory": 0.1, "war_support_factor": 0.1, "stability_factor": 0.05}),
    # The Union of American Socialist Republics
    "LR_usa_soviet_power": ("평의회 권력", "공장과 마을의 평의회가 연방을 떠받칩니다.",
                            "generic_syndicalism", {"political_power_gain": 0.1, "stability_factor": 0.05, "conscription_factor": 0.05}),
    "LR_usa_five_year_plan": ("제1차 5개년 계획", "계획 위원회는 다섯 해 안에 강철 생산을 세 배로 늘리겠다고 약속했습니다.",
                              "generic_central_management", {"industrial_capacity_factory": 0.1, "production_speed_buildings_factor": 0.15, "consumer_goods_factor": 0.05}),
    "LR_usa_world_revolution": ("세계 혁명", "혁명은 이제 두 대륙의 일입니다.",
                                "generic_communism_drift_bonus", {"war_support_factor": 0.1, "army_morale_factor": 0.1, "communism_drift": 0.05}),
    # Long's United States
    "LR_usa_share_our_wealth": ("부의 공유", "백만 달러를 넘는 소득은 세금으로 걷히고, 모든 가구가 정착금을 받습니다.",
                                "generic_goods_red_bonus", {"stability_factor": 0.15, "consumer_goods_factor": 0.05, "political_power_gain": 0.1}),
    "LR_usa_highways": ("국민 고속도로", "실업자 이백만 명이 대륙을 잇는 도로를 닦습니다.",
                        "generic_build_infrastructure", {"production_speed_infrastructure_factor": 0.3, "production_speed_buildings_factor": 0.1}),
    "LR_usa_kings_nation": ("모든 사람이 왕인 나라", "가난한 집 아들이 대통령이 되었고, 모든 가정에 자동차가 있습니다. 반대하는 목소리는 일요일 방송에 나오지 않습니다.",
                            "generic_political_support", {"stability_factor": 0.1, "war_support_factor": 0.1, "political_power_gain": 0.1}),
    # The Amerigo Confederacy
    "LR_usa_king_cotton": ("면화 왕", "연합국 정부가 면화 수출을 관리해 가격을 끌어올립니다.",
                           "generic_agrarian_society", {"political_power_gain": 0.1, "consumer_goods_factor": -0.05}),
    "LR_usa_golden_circle": ("황금의 원", "아바나를 중심으로 한 원 안의 모든 땅이 연합국의 것이어야 합니다.",
                             "generic_morale_bonus", {"war_support_factor": 0.1, "army_attack_factor": 0.05}),
    "LR_usa_caribbean_empire": ("카리브 제국", "멕시코만은 연합국의 호수가 되었습니다.",
                                "generic_navy_bonus", {"industrial_capacity_factory": 0.05, "stability_factor": 0.05, "war_support_factor": 0.05}),
}

# ------------------------------------------------------------------------------------------------------------
# Characters this tool adds (AMC, LNG and DXE leaders come from build_events.LEADERS)
# ------------------------------------------------------------------------------------------------------------
CHARACTERS = {
    "LR_USA_hoover": ("허버트 후버", "GFX_portrait_unknown", [("conservatism", [])]),
    "LR_CNA_hull": ("코델 헐", "GFX_portrait_LR_USA_generic_3", [("liberalism", [])]),
    "LR_CNA_macarthur": ("더글러스 맥아더", "GFX_portrait_USA_douglas_macarthur", [("fascism_ideology", []), ("despotism", [])]),
}
PORTRAITS = {  # sprite -> vanilla picture
    "GFX_portrait_LR_USA_generic_1": "gfx/leaders/USA/Portrait_USA_Generic_1.dds",
    "GFX_portrait_LR_USA_generic_2": "gfx/leaders/USA/Portrait_USA_Generic_2.dds",
    "GFX_portrait_LR_USA_generic_3": "gfx/leaders/USA/Portrait_USA_Generic_3.dds",
}

# ------------------------------------------------------------------------------------------------------------
# Tooltips and other keys
# ------------------------------------------------------------------------------------------------------------
LOC = {
    "LR_tt_usa_coercive": "대륙군이 봉기하면 대륙 회의가 1년 동안 §R분노한 식민지§!를 얻습니다.",
    "LR_tt_usa_conciliation": "대륙군이 봉기하면 대륙 회의가 1년 동안 §G망설이는 식민지§!를 얻습니다.",
    "LR_tt_usa_intel": "대륙군이 봉기하면 대륙 회의가 180일 동안 §G드러난 조직§!을 얻습니다.",
    "LR_tt_usa_join_league": "영국이 진영을 이끌고 있으면 그 진영에 들어갑니다.",
    "LR_tt_usa_expedition": "영국과 전쟁 중인 모든 나라에 선전포고합니다.",
    "LR_tt_usa_mexico_gone": "누에바 에스파냐 왕국이 사라졌다",
    "LR_tt_usa_union_bill": "영국 귀족 의회가 북아메리카 통합 법안을 심의합니다. 승인되면 §Y캐나다§!를 합병합니다.",
    "LR_tt_usa_canada_joined": "캐나다와 통합했다",
    "LR_tt_usa_secret_service": "독립기념일 암살 시도가 성공할 확률이 §G절반§!으로 줄어듭니다.",
    "LR_tt_usa_july_fourth": "워싱턴이 독립기념일 연설을 합니다. §R그날 무슨 일이 일어날지는 아무도 모릅니다.§!",
    "LR_tt_usa_promise_1778": "진영을 만듭니다. 프랑스가 의회정이나 프롤레타리아 독재정이고 진영이 없으면 진영에 들어옵니다.",
    "LR_tt_usa_emergency_currency": "§R영국의 금수§!가 §Y금수의 그늘§!로 약해집니다.",
    "LR_tt_usa_lean_on_army": "§R맥아더 장군이 권력을 잡습니다.§!",
    "LR_tt_usa_russian_brothers": "진영을 만들고, 진영이 없는 러시아 공화국을 들입니다.",
    "LR_tt_usa_british_compact": "영국이 이끄는 진영에 들어갑니다.",
    "LR_tt_usa_play_cna": "§Y대륙 회의§!로 플레이합니다.",
    "LR_tt_usa_play_amc": "§Y미주 노동자 평의회§!로 플레이합니다.",
    "LR_tt_usa_play_lng": "§Y아메리카 국민 연합§!으로 플레이합니다.",
    "LR_tt_usa_play_dxe": "§Y남부 연합§!으로 플레이합니다.",
    "LR_tt_usa_peace": "영국과 백색 평화를 맺습니다.",
    "LR_tt_usa_canada_march": "전쟁을 계속합니다. §Y캐나다§!가 항복하면 합병하고 영국과 강화합니다.",
    "LR_tt_usa_civil_war": "§R미국이 넷으로 갈라집니다.§! 필라델피아의 위원회, 시카고의 평의회, 캔자스시티의 롱, 애틀랜타의 남부 연합이 서로 전쟁을 벌입니다.",
    "LR_tt_usa_british_return": "북아메리카 내전의 네 진영 모두에 선전포고합니다.",
    "LR_tt_usa_canada_gone": "캐나다 자치령이 사라졌다",
    "LR_tt_usa_cores_north": "북아메리카에서 가진 모든 주를 중심지로 삼습니다.",
    "LR_tt_usa_annex_americas": "이제부터 아메리카 대륙의 나라가 우리나 우리 동맹에게 항복하면 강화 회의 없이 §Y합병§!합니다.",
    "LR_tt_usa_cores_americas": "아메리카 대륙에서 가진 모든 주를 중심지로 삼습니다.",
    "LR_fac_usa_liberty": "자유 동맹",
    "LR_fac_usa_revolution": "혁명 연대",
}

# ------------------------------------------------------------------------------------------------------------
# Events. Each: id -> dict(title, desc, picture, options=[(text, effects, ai, trigger)], news, immediate, hidden, trigger)
# ------------------------------------------------------------------------------------------------------------
EVENTS = {}


def ev(n, title, desc, picture, options, news=False, immediate=None, trigger=None, hidden=False):
    EVENTS[n] = dict(title=title, desc=desc.strip(), picture=picture, options=options, news=news, immediate=immediate,
                     trigger=trigger, hidden=hidden)


def opt(text, effects="", ai=None, trigger=None):
    return (text, effects, ai, trigger)


# ---------------- The colonial government ----------------
ev(1, "총독 관저의 겨울", """
1936년 1월 2일, 뉴욕 총독 관저의 2층 집무실은 난방이 반쯤 고장 나 있었다. 서기관 에드워드 헤일은 외투를 입은 채로 보고서를 넘겼다. 맨 위에 있는 것은 버지니아 마운트버넌 농장에 관한 석 장짜리 문서였다.

"조지 워싱턴. 마흔둘. 퇴역 소령." 그렌빌 총독은 이름을 소리 내어 읽고 안경을 벗었다. "들어 본 이름이군."

"플랑드르에서 훈장을 받았습니다, 각하. 식민지 출신이라 대령 진급이 두 번 거부됐고요." 헤일은 덧붙이지 않았지만, 그 두 번 가운데 한 번은 당시 전쟁성 차관이던 그렌빌이 직접 서류에 줄을 그은 것이었다.

보고서에 따르면 워싱턴은 지난 석 달 동안 필라델피아에 일곱 번 다녀갔다. 매번 같은 여관에 묵었고, 매번 다른 사람들을 만났다. 펜실베이니아 철강 노조 위원장, 보스턴의 신문사 주인, 캐롤라이나의 퇴역 대위 셋.

"모임이야 늘 있지." 총독이 보고서를 덮었다. "식민지 사람들은 모이는 걸 좋아해. 술을 마시고, 런던 욕을 하고, 집에 가지."

헤일은 고개를 끄덕였다. 그러고는 자기 책상으로 돌아가 보고서 사본을 한 부 따로 철했다. 겉장에는 아무것도 쓰지 않았다.
""", "GFX_report_event_generic_read_write", [opt("식민지의 겨울은 길지.")])

ev(10, "필라델피아의 7월", """
전신이 들어온 것은 7월 4일 오후 두 시 십 분이었다. 뉴욕 총독 관저 지하 전신실에서 마거릿 콜린스는 첫 열두 단어를 받아 적다가 연필을 떨어뜨렸다. 필라델피아 독립기념관. 대표 오십육 명. 독립 선언 서명. 워싱턴 총사령관 지명.

그녀는 연필을 주워 나머지를 받았다. 피츠버그 수비대가 무장 해제됐다. 볼티모어 항구에 민병대가 들어왔다. 보스턴에서는 총독부 세관이 불탔다. 다섯 시가 되자 버지니아와 캐롤라이나, 매사추세츠, 오하이오, 미시간에서 비슷한 전보가 이어졌다. 여섯 시에 필라델피아 회선이 끊겼다.

위층에서는 총독이 런던과 통화하고 있었다. 고함이 계단까지 들렸다. 증원은 석 달 뒤에나 온다, 그동안은 총독부 군대가 알아서 버텨야 한다.

밤 아홉 시, 서기관 헤일이 전신실에 내려와 마지막 전보를 직접 읽었다. 워싱턴의 선언문 전문이었다. 그는 다 읽고 나서도 한참 동안 종이를 손에 쥐고 있었다.

"작년에 보고했는데." 헤일이 말했다. 누구에게 하는 말도 아니었다.

마거릿은 대답하지 않았다. 그녀의 오빠는 피츠버그 제철소에서 일했고, 오늘 오후 수비대를 무장 해제한 노동자들 사이에 있었을지도 몰랐다. 그녀는 그 생각을 머릿속에서 밀어내고 다음 전보를 기다렸다.
""", "GFX_report_event_generic_rally", [
    opt("총독부는 무너지지 않는다.", ai=100),
    opt("필라델피아로 가겠다. 대륙 회의의 편에 선다.", "custom_effect_tooltip = LR_tt_usa_play_cna\nCNA = { change_tag_from = ROOT }", ai=0, trigger="is_ai = no"),
], trigger="CNA = { exists = yes }", immediate="""
if = {
	limit = { has_country_flag = LR_usa_coercive }
	CNA = { add_timed_idea = { idea = LR_usa_angry_colonies days = 365 } }
}
if = {
	limit = { has_country_flag = LR_usa_conciliation }
	CNA = { add_timed_idea = { idea = LR_usa_hesitant_colonies days = 365 } }
}
if = {
	limit = {
		check_variable = { LR_usa_loyalty > 64 }
		NOT = { has_country_flag = LR_usa_conciliation }
	}
	CNA = { add_timed_idea = { idea = LR_usa_hesitant_colonies days = 365 } }
}
if = {
	limit = { has_country_flag = LR_usa_intel }
	CNA = { add_timed_idea = { idea = LR_usa_exposed_cells days = 180 } }
}
news_event = { id = lr_usa.11 days = 1 }
""")

ev(11, "열세 식민지, 다시 독립을 선언하다", """
7월 4일 필라델피아에서 북아메리카 식민지 대표 쉰여섯 명이 영국으로부터의 독립을 선언했습니다. 대륙 회의는 퇴역 소령 조지 워싱턴을 대륙군 총사령관으로 지명했습니다.

런던 「타임스」는 이번 봉기를 "식민지의 열병"이라고 불렀습니다. 전쟁성은 "소수 선동가의 난동"이라며 북아메리카 총독부가 곧 질서를 되찾을 것이라고 밝혔습니다. 그러나 펜실베이니아와 버지니아, 매사추세츠의 수비대가 이미 무장 해제되었다는 보도가 잇따르고 있습니다. 파리의 외교가에서는 1778년 이야기가 다시 오르내린다고 합니다.
""", "GFX_news_event_generic_rally", [opt("160년 만이군.")], news=True)

ev(30, "반란의 끝", """
대륙군의 항복 문서는 필라델피아 독립기념관에서 서명되었다. 서기관 에드워드 헤일은 총독을 따라 그 건물에 들어서며 일 년 전 전신실에서 읽었던 선언문을 떠올렸다. 그 선언문에 서명한 쉰여섯 명 가운데 서른한 명이 지금 이 건물 지하에 갇혀 있었다.

워싱턴은 마지막에 들어왔다. 군복은 깨끗했지만 계급장은 떼어져 있었다. 그는 총독에게 고개를 숙이지 않았고, 총독도 그걸 요구하지 않았다. 둘은 탁자를 사이에 두고 마주 앉아 각자 서명했다. 워싱턴의 서명은 반듯했다.

서명이 끝나자 총독이 무언가 말하려 했다. 워싱턴이 먼저 일어섰다.

"총독 각하, 저는 처음 장교가 되었을 때 런던에 충성을 맹세했습니다. 그 맹세를 먼저 깬 쪽은 제가 아니었습니다."

그는 헌병들을 따라 나갔다. 헤일은 그 말을 받아 적지 않았다. 공식 기록에 남길 말이 아니었다.

자정 무렵 헤일은 1936년 1월에 따로 철해 둔 보고서를 꺼냈다. 겉장에 오늘 날짜를 적고, 서류함 맨 아래 칸에 넣었다. 워싱턴을 런던으로 데려갈 배는 사흘 뒤에 떠났다.
""", "GFX_report_event_generic_sign_treaty1", [opt("제국은 이겼다. 이번에도.")], immediate="""
set_country_flag = LR_usa_crushed
mark_focus_tree_layout_dirty = yes
news_event = { id = lr_usa.38 days = 1 }
""")

ev(38, "대륙 회의 무너지다", """
북아메리카 총독부가 대륙 회의의 반란을 진압했습니다. 대륙군은 항복했고, 반란을 이끈 조지 워싱턴은 체포되어 런던으로 이송될 예정입니다.

총독부는 대륙 회의 의원들을 반역죄로 재판에 넘기겠다고 밝혔습니다. 런던의 귀족 의회는 총독부의 충성에 감사를 표했습니다. 필라델피아 독립기념관의 종은 다시 떼어 내져 뉴욕 총독 관저로 옮겨졌다고 합니다.
""", "GFX_news_event_generic_sign_treaty1", [opt("두 번째도 실패했군.")], news=True)

ev(62, "북아메리카 통합 법안", """
웨스트민스터 귀족 의회의 식민위원회에 북아메리카 통합 법안이 올라왔다. 위원 일곱 명 앞에 놓인 서류는 두 가지였다. 뉴욕 총독부가 보낸 법안 원문과, 오타와의 캐나다 정부가 보낸 동의서였다.

식민위원장 크랜번 자작은 동의서를 먼저 읽었다. 캐나다 총리 매켄지 킹의 서명이 있었고, 퀘벡 주의 프랑스어 사용권을 보장한다는 조항이 붙어 있었다. 반대할 이유를 찾기 어려운 문서였다.

반대는 위원회 안에서 나왔다. 북아메리카 총독부는 이미 본국보다 많은 강철을 만든다. 캐나다까지 합치면 본국보다 땅이 예순 배 넓은 자치령이 생긴다. 한 위원은 그런 자치령이 언제까지 런던의 말을 들을지 물었다. 대답한 사람은 없었다.

크랜번 자작은 펜을 들었다가 내려놓았다. 반란을 진압한 총독부에 상을 주지 않으면 다른 식민지들이 그걸 지켜볼 것이다. 상을 주면, 그 상이 언젠가 칼이 될 수도 있었다.
""", "GFX_report_event_generic_sign_treaty2", [
    opt("승인한다. 충성에는 보답해야 한다.", """USA = {
	annex_country = {
		target = CAN
		transfer_troops = yes
	}
	set_country_flag = LR_usa_canada_joined
}
news_event = { id = lr_usa.64 days = 1 }""", ai="base = 70\nmodifier = {\n\tfactor = 1.5\n\tUSA = { is_in_faction_with = ENG }\n}"),
    opt("거부한다. 자치령은 하나로 충분하다.", "USA = { add_opinion_modifier = { target = ROOT modifier = medium_decrease } }", ai=30),
], trigger="CAN = { exists = yes is_subject_of = ENG }\nUSA = { exists = yes }")

ev(64, "캐나다, 북아메리카 총독부와 통합", """
런던의 귀족 의회가 북아메리카 통합 법안을 승인했습니다. 캐나다 자치령과 북아메리카 총독부는 하나의 자치령으로 합쳐지며, 정부는 뉴욕에 둡니다.

퀘벡 주에는 프랑스어 사용권이 보장되었습니다. 새 자치령은 땅 넓이로 영국 본토의 예순 배가 넘습니다. 런던의 일부 신문은 이것이 제국의 무게중심을 대서양 너머로 옮기는 일이라며 우려를 나타냈습니다.
""", "GFX_news_event_generic_sign_treaty2", [opt("대서양 건너의 거인이로군.")], news=True)

ev(65, "신대륙의 제국", """
북아메리카 총독부가 스페인령 아메리카 정복을 마쳤습니다. 알래스카에서 파타고니아까지 신대륙의 대부분이 영국 제국의 깃발 아래 들어왔습니다.

런던의 귀족 의회는 북아메리카 총독부를 아메리카 대총독령으로 격상했습니다. 뉴욕의 대총독은 이제 런던 다음가는 제국의 권력자로 꼽힙니다. 마드리드는 이 소식에 아무 논평도 내지 않았습니다.
""", "GFX_news_event_soldiers_marching", [opt("해가 지지 않는다.")], news=True)

# ---------------- The war of independence ----------------
ev(20, "총독 관저의 깃발", """
뉴욕 총독 관저의 정문은 잠겨 있지 않았다. 대륙군 제3연대의 존 매클레인 대위는 부하 여섯 명과 함께 계단을 올라가며, 누군가 총을 쏠 것에 대비해 권총을 뽑아 들고 있었다. 아무도 쏘지 않았다.

2층 집무실에는 총독과 서기관 하나가 남아 있었다. 총독은 정장 차림이었고, 책상 위에는 항복 문서 두 부가 이미 놓여 있었다. 서기관은 문서 옆에 만년필을 가지런히 올려 두었다.

"워싱턴 장군은 어디 있소?" 총독이 물었다.

"브루클린에 계십니다. 내일 오십니다." 매클레인은 그렇게 대답하고서야 자기가 존댓말을 쓰고 있다는 걸 깨달았다. 열한 달 전까지 이 사람은 그의 총독이었다.

총독이 서명했다. 서기관이 서명했다. 매클레인은 무엇에 서명해야 할지 몰라 문서를 들고 서 있다가, 결국 대위 계급과 이름을 적었다. 나중에 역사책에 실린 항복 문서에 대위의 서명이 들어간 것은 그 때문이었다.

지붕의 깃대에서 유니언잭을 내린 것은 병사 셋이었다. 그들은 깃발을 어떻게 접어야 하는지 몰라서 둘둘 말아 겨드랑이에 끼고 내려왔다. 거리에 모인 사람들이 그 모습을 보고 박수를 쳤다.

저녁 아홉 시 필라델피아의 대륙 회의에는 런던에서 온 전보가 기다리고 있었다. 영국 귀족 의회는 아직 전쟁이 끝나지 않았다고 했다. 북쪽 국경 너머에는 캐나다 자치령이 있었고, 그곳에는 영국군 두 개 사단이 있었다.
""", "GFX_report_event_generic_sign_treaty1", [
    opt("독립이면 충분하다. 런던과 강화한다.", "custom_effect_tooltip = LR_tt_usa_peace\nhidden_effect = {\n\tevery_enemy_country = {\n\t\tROOT = { white_peace = PREV }\n\t}\n}", ai=60),
    opt("캐나다까지 간다.", "custom_effect_tooltip = LR_tt_usa_canada_march\nset_country_flag = LR_usa_canada_march", ai=40),
], immediate="""
set_cosmetic_tag = LR_CNA_usa
set_country_flag = LR_usa_independent
lr_usa_mg_union_start = yes
mark_focus_tree_layout_dirty = yes
news_event = { id = lr_usa.21 days = 1 }
country_event = { id = lr_usa.24 days = 420 }
""")

ev(21, "미합중국 수립", """
북아메리카 총독부가 항복했습니다. 대륙 회의는 열세 식민지와 서부 영토를 아우르는 미합중국의 수립을 선포했습니다. 뉴욕 총독 관저의 항복 문서에는 대륙군 대위 한 명의 서명이 들어갔다고 합니다.

파리의 「르탕」은 이를 "1783년에 왔어야 할 소식"이라고 썼습니다. 워싱턴 총사령관은 "이 공화국은 어느 왕도, 어느 귀족도 섬기지 않는다"고 말했습니다. 런던의 귀족 의회는 아직 공식 반응을 내놓지 않았습니다. 유럽 각국의 궁정은 이 소식을 불편한 침묵으로 받아들이고 있는 것으로 보입니다.
""", "GFX_news_event_generic_rally", [opt("왕 없는 나라라니.")], news=True)

ev(22, "멈춘 시계", """
오타와 의사당 평화의 탑에는 커다란 시계가 있었다. 대륙군 제1군단 통신병 해럴드 브릭스는 의사당 계단에 무전기를 내려놓다가, 그 시계가 오후 세 시 십오 분에 멈춰 있는 걸 보았다. 포탄 파편이 시곗바늘을 부러뜨린 것이었다.

캐나다 정부는 이틀 전 퀘벡으로 떠났고, 의사당에 남은 것은 서기 몇 명과 경비원 하나였다. 경비원은 총을 내려놓고 대륙군 장교에게 의사당 열쇠 꾸러미를 건넸다. 열쇠는 열여섯 개였는데, 어느 열쇠가 어느 문에 맞는지는 경비원도 몰랐다.

브릭스가 필라델피아에 보낸 전문은 짧았다. 오타와 점령. 저항 없음. 시계 고장.

마지막 두 단어는 실수로 들어간 것이었다. 그러나 다음 날 필라델피아의 신문들은 그 전문을 그대로 실었고, 사람들은 그걸 영국의 시간이 멈췄다는 뜻으로 읽었다. 런던의 귀족 의회는 그 주 안에 강화를 제안했다. 대서양 너머에서 지켜야 할 것이 너무 많았다.
""", "GFX_report_event_canadian_soldiers", [
    opt("북쪽 국경은 이제 북극해다.", "hidden_effect = {\n\tevery_enemy_country = {\n\t\tlimit = { OR = { tag = ENG is_subject_of = ENG is_in_faction_with = ENG } }\n\t\tROOT = { white_peace = PREV }\n\t}\n}"),
], immediate="clr_country_flag = LR_usa_canada_march")

ev(23, "의자 하나", """
속기사 루스 에이브럼스는 넉 달 동안 연필 이백 자루를 썼다. 필라델피아 독립기념관 동쪽 방에서 대표 쉰다섯 명이 하루 아홉 시간씩 떠드는 걸 받아 적으려면 그만큼이 필요했다.

가장 길었던 논쟁은 대통령의 임기였다. 버지니아 대표는 종신을 주장했고, 매사추세츠 대표는 그럴 바엔 차라리 스페인에서 왕을 하나 빌려 오자고 비꼬았다. 회의장이 웃음과 고함으로 뒤집혔을 때 루스는 둘 다 받아 적었다. 사 년으로 정해진 것은 그다음 주였다.

두 번째로 길었던 논쟁은 서부였다. 미시시피 서쪽의 영토를 주로 쪼갤 것인가, 연방이 직접 다스릴 것인가. 오하이오 대표 하나가 의자를 던졌고, 의자는 아무도 맞히지 않고 창문을 깼다. 그 창문은 헌법에 서명할 때까지 판자로 막혀 있었다.

워싱턴은 의장석에 앉아 거의 말하지 않았다. 루스의 속기록에서 그의 발언은 넉 달 동안 모두 열한 줄이었다. 그중 아홉 줄은 "다음 발언자"였다.

서명식이 끝나고 대표들이 빠져나간 뒤, 워싱턴이 속기사 자리로 와서 모든 걸 다 적었느냐고 물었다. 루스는 의자 던진 것까지 적었다고 대답했다. 워싱턴은 잠시 생각하더니, 그건 지우지 말라고 했다.
""", "GFX_report_event_generic_read_write", [opt("의자 하나쯤은 괜찮지.")])

ev(24, "", "", "", [], hidden=True, trigger="has_country_flag = LR_usa_independent\nNOT = { has_country_flag = LR_usa_july_fourth_done }",
   immediate="country_event = { id = lr_usa.25 }")
ev(25, "", "", "", [], hidden=True, trigger="NOT = { has_country_flag = LR_usa_july_fourth_done }", immediate="""
set_country_flag = LR_usa_july_fourth_done
random_list = {
	60 = {
		modifier = {
			factor = 0.5
			has_country_flag = LR_usa_secret_service
		}
		country_event = { id = lr_usa.26 }
	}
	40 = {
		country_event = { id = lr_usa.40 }
	}
}
""")

# ---------------- Washington lives ----------------
ev(40, "빗나간 총알", """
오전 열한 시 사 분, 워싱턴이 독립기념관 앞 연단에 올랐다. 「필라델피아 인콰이어러」의 사진기자 프랭크 오도널은 연단 왼쪽 세 번째 줄에서 사진기를 들고 있었다. 광장에는 육만 명이 모였고, 첫 문장은 바람에 반쯤 날아갔다.

오도널이 세 번째 사진을 찍으려고 필름을 감을 때 총성이 났다. 대통령이 왼쪽으로 비틀거렸고, 연단 옆에 서 있던 경호원 하나가 그를 덮쳐 쓰러뜨렸다. 두 번째 총알은 연단의 나무판을 뚫었다. 세 번째 총알은 날아오지 않았다. 독립기념관 2층 창문에서 경찰관 두 명이 범인과 뒤엉켜 있었다.

광장이 조용해진 것은 오 분쯤 뒤였다. 워싱턴이 다시 연단에 올라왔다. 왼쪽 어깨의 셔츠가 피에 젖어 있었다. 경호원이 팔을 붙잡았지만 그는 그 손을 떼어 냈다. 그러고는 원고를 다시 펼쳐, 총성이 울리기 직전에 읽던 문장부터 이어서 읽었다.

오도널은 그 장면을 찍었다. 다음 날 그 사진은 미국의 모든 신문 일면에 실렸다. 피 묻은 셔츠를 입고 원고를 읽는 대통령. 오도널은 그 사진으로 상을 받았지만, 평생 그 사진보다 그날 광장의 침묵을 더 자주 떠올렸다. 육만 명이 한꺼번에 숨을 참는 소리를 그는 그때 처음 들었다.
""", "GFX_report_event_journalists_speech", [opt("공화국은 살아남았다.")], immediate="""
set_country_flag = LR_usa_washington_lives
mark_focus_tree_layout_dirty = yes
news_event = { id = lr_usa.39 days = 1 }
""")

ev(39, "워싱턴 대통령, 저격에서 살아남다", """
독립기념일 연설 도중 총격을 받은 조지 워싱턴 대통령이 가벼운 부상만 입고 목숨을 건졌습니다. 대통령은 피 묻은 셔츠 차림으로 연설을 끝까지 마쳤습니다.

범인은 현장에서 체포되었습니다. 「필라델피아 인콰이어러」의 사진기자가 찍은 사진을 비롯해, 필라델피아의 신문들은 피 묻은 셔츠를 입고 원고를 읽는 대통령의 사진을 일제히 일면에 실었습니다. 정부는 범인의 배후를 조사하고 있다고 밝혔습니다.
""", "GFX_news_event_journalists_speech", [opt("질긴 사람이군.")], news=True)

ev(71, "어깨는 괜찮으신지", """
선거관리위원 마사 하인즈는 펜실베이니아 랭커스터 카운티 개표소에서 투표함 마흔두 개를 열었다. 투표용지에는 대통령 후보가 한 명뿐이었다. 찬성과 반대 두 칸 가운데 하나에 표시하는 방식이었다.

개표는 지루했다. 찬성, 찬성, 찬성. 가끔 반대가 나왔고, 칸 옆에 무언가를 적어 넣은 용지도 있었다. "왕보다는 낫다." "세금이나 내려라." "어깨는 괜찮으신지." 마사는 규정대로 그런 용지를 무효로 분류하려다가, 위원장에게 물어보고 유효로 쳤다. 표시는 칸 안에 제대로 되어 있었으니까.

자정이 넘어 집계가 끝났다. 랭커스터 카운티의 찬성률은 팔십구 퍼센트였다. 전국 결과는 사흘 뒤에 나왔는데 팔십일 퍼센트였다. 반대표가 가장 많이 나온 곳은 뉴욕이었다. 총독부 시절의 관리와 상인들이 많이 사는 도시였다.

워싱턴은 취임 연설에서 그 숫자를 직접 언급했다. 열아홉 퍼센트의 국민이 자신을 원하지 않았고, 그들 역시 이 공화국의 국민이라고 했다. 마사는 라디오로 그 연설을 들으며, 랭커스터에서 개표한 용지 가운데 그 한 장을 떠올렸다.
""", "GFX_report_event_usa_election_generic", [opt("공화국은 반대표도 센다.")])

ev(72, "북아메리카, 하나의 헌법 아래", """
미합중국 의회가 새로 편입된 북부와 서부 영토에 연방 헌법을 적용하는 법안을 통과시켰습니다. 북극해에서 리오그란데까지 대륙의 대부분이 한 공화국의 헌법 아래 놓였습니다.

워싱턴 대통령은 두 번째 임기를 마지막으로 물러나겠다는 뜻을 다시 밝혔습니다. 유럽의 왕정 국가들은 대서양 건너의 거대한 공화국을 불안한 눈으로 지켜보고 있습니다.
""", "GFX_news_event_generic_rally", [opt("왕 없는 대륙이다.")], news=True)

# ---------------- Washington dies ----------------
ev(26, "피의 독립기념일", """
사진기자 프랭크 오도널은 연단 왼쪽 세 번째 줄에 자리를 잡았다. 「필라델피아 인콰이어러」가 그에게 내준 자리였고, 그는 거기서 대통령의 옆얼굴을 가장 잘 찍을 수 있다고 믿었다.

오전 열한 시 사 분, 워싱턴이 연단에 올랐다. 광장에 모인 사람은 경찰 추산 육만이었다. 첫 문장은 바람에 반쯤 날아갔다. 두 번째 문장에서 사람들이 웃었다. 공화국은 어느 귀족에게도 생일 축하 전보를 보내지 않는다는 농담이었다.

오도널이 세 번째 사진을 찍으려고 필름을 감을 때 첫 총성이 났다. 그는 처음에 폭죽인 줄 알았다. 두 번째 총성에 연단 위의 대통령이 오른쪽으로 기울었다. 세 번째 총성은 듣지 못했다. 그때는 이미 사람들이 비명을 지르며 그를 밀치고 있었다.

그는 넘어지면서도 사진기를 놓지 않았다. 나중에 현상해 보니 그 순간의 사진은 석 장이었다. 첫 장에는 연설하는 워싱턴. 둘째 장에는 하늘. 셋째 장에는 독립기념관 2층 창문과, 그 안에서 무언가를 들고 서 있는 흐릿한 사람의 윤곽.

대통령은 펜실베이니아 병원으로 가는 구급차 안에서 숨졌다. 범인은 그 자리에서 경찰의 총에 맞아 죽었고, 이름은 사흘 뒤에야 나왔다. 그때쯤엔 아무도 이름 따위에 관심이 없었다. 영국의 첩자라는 사람, 빨갱이라는 사람, 군대가 꾸민 일이라는 사람이 거리마다 서로 멱살을 잡고 있었다.
""", "GFX_report_event_usa_funeral", [opt("공화국은 이 사람 없이 살아남아야 한다.")], immediate="""
set_country_flag = LR_usa_crisis
lr_usa_mg_union_stop = yes
lr_usa_mg_order_start = yes
kill_country_leader = yes
recruit_character = LR_CNA_hull
promote_character = LR_CNA_hull
mark_focus_tree_layout_dirty = yes
news_event = { id = lr_usa.34 days = 1 }
country_event = { id = lr_usa.27 days = 20 }
country_event = { id = lr_usa.28 days = 50 }
country_event = { id = lr_usa.29 days = 90 }
country_event = { id = lr_usa.31 days = 140 }
""")

ev(34, "워싱턴 대통령 피살", """
미합중국의 조지 워싱턴 대통령이 독립기념일 연설 도중 필라델피아에서 총에 맞아 숨졌습니다. 범인은 현장에서 사살되었으며, 정부는 아직 범인의 신원과 배후를 밝히지 않았습니다.

부통령 코델 헐이 대통령직을 승계했습니다. 필라델피아와 뉴욕, 시카고에서는 영국 영사관과 노동회관을 겨냥한 소요가 잇따르고 있다고 합니다. 런던의 귀족 의회는 조의를 표하면서도, 대서양 너머의 혼란이 영국인의 재산을 위협한다는 우려를 함께 밝혔습니다.
""", "GFX_news_event_generic_funeral", [opt("총알 하나에 공화국이 흔들리는군.")], news=True)

ev(27, "거리의 분노", """
시카고 경찰 제7관구의 토머스 키어넌 경사는 장례식 다음 날부터 집에 들어가지 못했다. 사우스사이드의 제철소 노동자들이 공장 문을 닫고 거리로 나왔고, 웨스트사이드에서는 퇴역 군인회가 영국 영사관을 향해 행진했다. 둘은 서로 다른 것을 외쳤지만, 경찰에게 던지는 벽돌은 같았다.

사흘째 되는 날 영사관 유리창이 모두 깨졌다. 나흘째에는 누군가 노동회관에 불을 질렀다. 노동자들은 퇴역 군인회를 의심했고, 퇴역 군인회는 노동자들의 자작극이라고 했다. 키어넌은 불탄 건물 앞에서 양쪽을 갈라놓다가 왼쪽 귀를 다쳤다.

필라델피아에서 온 지시는 질서를 유지하되 발포는 하지 말라는 것이었다. 키어넌은 그 지시문을 읽고 한참 웃었다. 그의 관구에 남은 순경은 마흔 명이었고, 거리에 나온 사람은 이만 명이었다.

밤이 되면 시위대는 흩어졌다가 아침이면 다시 모였다. 사람들은 이제 누가 대통령을 죽였는지보다 다음 달 집세를 어떻게 낼지를 더 많이 이야기했다. 공장의 절반이 문을 닫았기 때문이었다.
""", "GFX_report_event_generic_riot", [opt("이건 시작일 뿐이야.")], immediate="""
if = {
	limit = { NOT = { has_completed_focus = LR_CNA_dialogue } }
	add_ideas = LR_usa_burning_streets
}
""", trigger="has_country_flag = LR_usa_crisis\nNOT = { has_country_flag = LR_usa_coup_done }")

ev(28, "런던의 보복", """
재무부 국제결제과의 프랜시스 웰던은 런던에서 온 통고문을 세 번 읽었다. 영국 귀족 의회는 미합중국과의 모든 파운드화 결제를 중단하고, 영국 항구에 들어오는 미국 선박에 화물 가치의 4할을 관세로 매기기로 했다. 대통령 암살 이후의 혼란이 영국 투자자의 재산을 위협한다는 것이 이유였다.

웰던은 숫자를 계산해 보았다. 미국 면화의 육 할, 밀의 사 할이 리버풀로 갔다. 피츠버그 철강 회사들의 빚은 대부분 런던 은행에 있었다. 결제가 막히면 그 빚은 다음 주부터 연체가 된다.

그는 보고서를 쓰다가 펜을 내려놓고 창밖을 봤다. 재무부 건물 앞에서도 시위가 벌어지고 있었다. 팻말에는 영국을 몰아내라고 적혀 있었다. 웰던은 그 사람들이 이미 영국을 몰아냈다는 사실을 떠올렸다. 그리고 영국이 몰려난 뒤에도 영국의 돈은 떠나지 않았다는 사실도.

보고서의 결론은 한 줄이었다. 석 달 안에 공장의 삼분의 일이 멈춥니다. 헐 대통령은 그 줄에 밑줄을 긋고 아무 말도 하지 않았다.
""", "GFX_report_event_generic_factory", [opt("런던은 이걸 기다렸던 거야.")], immediate="add_ideas = LR_usa_british_embargo",
   trigger="has_country_flag = LR_usa_crisis\nNOT = { has_country_flag = LR_usa_coup_done }")

ev(29, "붉은 깃발", """
디트로이트 캐딜락 광장에 모인 사람의 숫자는 신문마다 달랐다. 「디트로이트 프리 프레스」는 삼만, 노동 신문 「데일리 워커」는 십오만이라고 썼다. 그 자리에 있던 포드 공장 조립공 스탠리 코발스키는 숫자 같은 건 세지 않았다. 그의 눈에는 앞사람의 등과 붉은 깃발만 보였다.

연단에 오른 사람은 캔자스 출신의 얼 브라우더였다. 그는 워싱턴을 죽인 것이 누구든, 그 죽음으로 이득을 보는 것은 런던의 은행과 필라델피아의 장군들이라고 말했다. 공장을 닫은 것은 노동자가 아니라 사장들이고, 그 사장들의 빚은 영국에 있다고 했다. 그리고 이렇게 말했다. 공산주의는 모스크바에서 온 것이 아니라 1776년에 시작해 끝내지 못한 일을 마저 하는 것이라고. 이 세기의 아메리카니즘이라고.

코발스키의 공장은 지난주에 문을 닫았다. 그는 일당 육 달러를 받았었고, 아내는 셋째를 임신 중이었다. 브라우더가 공장은 일하는 사람의 것이라고 외쳤을 때 코발스키도 함께 소리를 질렀다. 무엇이라고 질렀는지는 나중에 기억나지 않았다.

새벽 두 시 디트로이트의 공장 열두 곳이 노동자 위원회의 손에 넘어갔다. 경찰은 오지 않았다. 경찰들도 그 광장에 있었다.
""", "GFX_report_event_generic_rally_3", [opt("빨갱이들이 거리로 나왔군.")], immediate="""
add_ideas = LR_usa_red_agitation
add_popularity = { ideology = communism popularity = 0.15 }
""", trigger="has_country_flag = LR_usa_crisis\nNOT = { has_country_flag = LR_usa_coup_done }")

ev(31, "맥아더의 아침", """
오전 여섯 시, 필라델피아의 대통령 관저 앞에 장갑차 네 대가 섰다. 관저 경비대장 윌리엄 프레스턴 대위는 정문에서 장갑차의 해치가 열리는 걸 지켜보며, 자기가 총을 뽑아야 하는지 경례를 해야 하는지 몰랐다. 장갑차에서 내린 사람이 대륙군 사령관 더글러스 맥아더 장군이었기 때문이다. 프레스턴은 1932년 여름을 기억했다. 대전쟁 보상금을 달라며 스쿨킬 강변에 천막을 친 퇴역 군인 이만 명을 기병과 최루가스로 쫓아낸 사람도 이 장군이었다. 그때 맥아더는 총독부의 장교였다.

맥아더가 먼저 경례를 했다. 그러고는 대통령을 깨우지 말고 기다리겠다고 했다. 그는 현관 대기실에서 사십 분 동안 파이프를 피웠다. 그동안 관저를 둘러싼 병사는 이백 명으로 늘었다.

헐 대통령은 잠옷 위에 외투를 걸치고 내려왔다. 둘이 대기실에서 나눈 대화는 십오 분이었고, 문이 닫혀 있어 프레스턴은 들을 수 없었다. 한 번 헐의 목소리가 높아졌다가 다시 낮아졌을 뿐이다.

문이 열렸을 때 헐의 손에는 사직서가 들려 있었다. 서명은 이미 되어 있었다. 맥아더는 사직서를 받아 접어서 가슴 주머니에 넣었다.

여덟 시, 라디오에서 맥아더의 목소리가 나왔다. 국가 재건 위원회가 공화국을 맡는다고, 헌법은 정지되지 않으며 혼란이 끝나는 대로 선거를 치른다고 했다. 같은 시각 시카고와 캔자스시티, 애틀랜타의 방송국에서는 전혀 다른 목소리들이 전혀 다른 말을 하고 있었다.
""", "GFX_report_event_usa_macarthur_speech", [opt("질서다. 우선은.")], immediate="""
set_country_flag = LR_usa_coup_done
lr_usa_mg_army_start = yes
retire_character = LR_CNA_hull
recruit_character = LR_CNA_macarthur
set_politics = {
	ruling_party = fascism
	elections_allowed = no
}
set_popularities = {
	fascism = 45
	democratic = 25
	communism = 20
	neutrality = 10
}
promote_character = {
	character = LR_CNA_macarthur
	ideology = fascism_ideology
}
set_cosmetic_tag = LR_CNA_junta
country_event = { id = lr_usa.32 days = 7 }
""", trigger="has_country_flag = LR_usa_crisis\nNOT = { has_country_flag = LR_usa_coup_done }")

ev(32, "갈라진 나라", """
맥아더의 방송이 끝나고 이틀 뒤, 지도가 다시 그려졌다.

시카고 노동회관에서는 북부 여덟 개 주의 노동자 평의회가 맥아더를 반역자로 선언했다. 디트로이트와 클리블랜드, 뉴욕의 공장들이 그들의 편이었다. 캔자스시티에서는 휴이 롱이 라디오에 나와 장군도 빨갱이도 아닌 보통 사람의 미국을 외쳤고, 평원과 서부의 주지사 열네 명이 그날 저녁 그의 편에 섰다. 애틀랜타에서는 시어도어 빌보가 남부 여섯 개 주의 연방 탈퇴를 선언했다. 필라델피아에 남은 것은 펜실베이니아와 메릴랜드, 버지니아, 캐롤라이나 북부와 테네시, 켄터키였다.

국가 재건 위원회 작전과장 조지프 스틸웰 대령은 밤 열 시 작전실 벽에 지도를 붙이고 색연필 네 자루로 칠했다. 파랑은 위원회, 빨강은 평의회, 초록은 롱, 회색은 남부. 다 칠하고 나니 파랑이 가장 작았다.

"장군께 보고드릴까요?" 부관이 물었다.

스틸웰은 색연필을 내려놓았다. "장군은 이미 아셔. 그래서 서두르신 거지."

대륙군이 독립을 위해 함께 싸운 지 몇 해 만에, 대륙군의 장교들은 서로에게 총을 겨누게 되었다.
""", "GFX_report_event_spain_civil_war_soldiers", [
    opt("필라델피아를 지킨다. 맥아더와 함께.", ai=100),
    opt("시카고의 평의회에 합류한다.", "custom_effect_tooltip = LR_tt_usa_play_amc\nAMC = { change_tag_from = ROOT }", ai=0, trigger="is_ai = no\nAMC = { exists = yes }"),
    opt("캔자스시티의 롱에게 간다.", "custom_effect_tooltip = LR_tt_usa_play_lng\nLNG = { change_tag_from = ROOT }", ai=0, trigger="is_ai = no\nLNG = { exists = yes }"),
    opt("애틀랜타의 남부 연합에 선다.", "custom_effect_tooltip = LR_tt_usa_play_dxe\nDXE = { change_tag_from = ROOT }", ai=0, trigger="is_ai = no\nDXE = { exists = yes }"),
], immediate="""
custom_effect_tooltip = LR_tt_usa_civil_war
if = {
	limit = { check_variable = { LR_usa_order > 49 } }
	add_timed_idea = { idea = LR_usa_order_remnant days = 365 }
}
lr_usa_mg_order_stop = yes
lr_usa_civil_war = yes
mark_focus_tree_layout_dirty = yes
news_event = { id = lr_usa.35 days = 1 }
ENG = { country_event = { id = lr_usa.36 days = 30 } }
""", trigger="NOT = { has_global_flag = LR_usa_civil_war }")

ev(35, "미합중국, 내전에 빠지다", """
맥아더 장군의 국가 재건 위원회가 필라델피아에서 권력을 잡자 미합중국이 넷으로 갈라졌습니다. 시카고의 노동자 평의회, 캔자스시티의 휴이 롱, 애틀랜타의 남부 연합이 각각 위원회를 인정하지 않는다고 선언했습니다.

대륙군은 출신 주에 따라 갈라졌고, 네 진영이 서로에게 선전포고한 것으로 알려졌습니다. 런던 「타임스」는 이를 "아메리카의 30년 전쟁"이라고 불렀습니다. 유럽의 외교가에서는 독립한 지 몇 해 되지 않은 공화국이 스스로 무너지고 있다는 평이 나옵니다. 런던이 이 기회를 어떻게 쓸지에 관심이 쏠립니다.
""", "GFX_news_event_soldiers_marching", [opt("공화국이란 게 이렇지.")], news=True)

# Britain decides whether to come back. A British focus can decide it later: it sets LR_eng_reconquest_america.
ev(36, "대서양 건너의 내전", """
웨스트민스터 귀족 의회 외교위원회 회의실에는 북아메리카 지도가 두 장 걸려 있었다. 하나는 1937년 반란 이전의 것이고, 다른 하나는 어제 필라델피아 영사관에서 보내온 것이었다. 두 번째 지도는 네 가지 색으로 칠해져 있었다.

해군 제1위원 체트우드 경이 먼저 말했다. 대서양 함대는 육 주 안에 노바스코샤에 육군 다섯 개 사단을 내려놓을 수 있다. 네 진영 가운데 어느 쪽에도 해군다운 해군이 없으니 해안은 무방비다.

재무위원 맨스필드 백작은 숫자를 들고 왔다. 미국에 묶인 영국 자본은 십사억 파운드였다. 내전이 길어지면 그 돈의 절반은 돌아오지 않는다.

반대한 것은 외교위원장이었다. 유럽에서 제국연맹이 감당할 일이 이미 많고, 대서양 건너에서 또 전쟁을 벌이면 프랑스가 그 틈을 놓치지 않을 것이라고 했다. 그는 지도 위의 사라토가와 필라델피아를 차례로 짚었다. 영국이 북아메리카에서 이긴 적은 생각보다 드물었다.

투표는 둘로 갈렸고, 결정은 의장에게 넘어왔다.
""", "GFX_report_event_generic_read_write", [
    opt("식민지를 되찾는다. 함대를 보내라.", """custom_effect_tooltip = LR_tt_usa_british_return
set_global_flag = LR_usa_british_return
every_country = {
	limit = {
		OR = { tag = CNA tag = AMC tag = LNG tag = DXE }
		exists = yes
		NOT = { has_war_with = ROOT }
	}
	ROOT = {
		declare_war_on = {
			target = PREV
			type = annex_everything
		}
	}
}
news_event = { id = lr_usa.37 days = 1 }""", ai="base = 40\nmodifier = {\n\tfactor = 0.3\n\thas_war = yes\n}\nmodifier = {\n\tfactor = 100\n\thas_country_flag = LR_eng_reconquest_america\n}"),
    opt("그들끼리 싸우게 두지.", "", ai="base = 60\nmodifier = {\n\tfactor = 0\n\thas_country_flag = LR_eng_reconquest_america\n}"),
], trigger="has_global_flag = LR_usa_civil_war")

ev(37, "영국, 북아메리카에 돌아오다", """
영국 귀족 공화국이 내전 중인 북아메리카의 네 진영에 선전포고했습니다. 대서양 함대가 노바스코샤와 뉴펀들랜드에서 출항했으며, 육군 다섯 개 사단이 함께 움직이는 것으로 알려졌습니다.

귀족 의회는 "북아메리카의 질서와 영국인의 재산을 지키기 위한 조치"라고 밝혔습니다. 네 진영은 모두 영국의 개입을 비난했지만, 서로에게 겨눈 총구를 거두지는 않았습니다.
""", "GFX_news_event_soldiers_marching", [opt("또 영국인가.")], news=True)

ev(49, "", "", "", [], hidden=True, immediate="""
if = {
	limit = {
		tag = CNA
		NOT = { AMC = { exists = yes } }
		NOT = { LNG = { exists = yes } }
		NOT = { DXE = { exists = yes } }
	}
	country_event = { id = lr_usa.51 }
}
else_if = {
	limit = {
		tag = AMC
		NOT = { CNA = { exists = yes } }
		NOT = { LNG = { exists = yes } }
		NOT = { DXE = { exists = yes } }
	}
	country_event = { id = lr_usa.52 }
}
else_if = {
	limit = {
		tag = LNG
		NOT = { CNA = { exists = yes } }
		NOT = { AMC = { exists = yes } }
		NOT = { DXE = { exists = yes } }
	}
	country_event = { id = lr_usa.53 }
}
else_if = {
	limit = {
		tag = DXE
		NOT = { CNA = { exists = yes } }
		NOT = { AMC = { exists = yes } }
		NOT = { LNG = { exists = yes } }
	}
	country_event = { id = lr_usa.54 }
}
""")

ev(51, "창문", """
마지막 항복 문서가 들어온 날, 맥아더는 필라델피아 독립기념관 2층 창가에 서 있었다. 워싱턴을 쏜 총알이 날아온 그 창문이었다. 그는 일부러 그 방을 집무실로 골랐다고 측근들에게 말한 적이 있다. 그 창문에서 무엇이 보이는지 알아야 한다고.

부관 코트니 휘트니 소령이 전문을 읽었다. 마지막 남은 진영의 군대가 무기를 내려놓았다는 내용이었다. 맥아더는 끝까지 듣고, 파이프에 불을 붙인 뒤 한 가지만 물었다. 포로가 몇 명이냐고. 이십삼만 명이라는 대답에 그는 고개를 끄덕였다. 도로를 놓을 사람이 필요하다고 했다.

광장에서는 군악대가 행진곡을 연습하고 있었다. 일주일 뒤면 승전 행진이 이 광장을 지날 것이다. 휘트니는 창밖을 내려다보며, 공화국의 헌법이 아직 장군의 서랍 속에 있다는 걸 떠올렸다. 그 서랍이 언제 열리느냐고 묻는 사람은 이제 없었다.

해가 진 뒤 위원회는 맥아더에게 새 칭호를 바치는 결의안을 준비했다. 초안은 휘트니가 썼다. 맥아더는 초안을 읽고 한 단어를 고쳤다. 공화국이라는 단어였다.
""", "GFX_report_event_soldiers_parade", [opt("이제 질서를 세울 시간이다.")], immediate="""
lr_usa_civil_war_end = yes
set_country_flag = LR_route_amerigo_empire
mark_focus_tree_layout_dirty = yes
news_event = { id = lr_usa.55 days = 1 }
""")

ev(52, "평의회 트럭", """
필라델피아에 들어온 미주 적군 선두 부대는 디트로이트 공장에서 만든 트럭을 타고 있었다. 트럭 옆면에는 회사 이름 대신 평의회라고 페인트로 쓰여 있었다. 운전병 스탠리 코발스키는 독립기념관 앞에서 시동을 끄고, 이 년 전 캐딜락 광장에서 붉은 깃발을 보던 날을 떠올렸다.

얼 브라우더는 독립기념관 동쪽 방에서 대표자 대회를 열었다. 헌법 제정 회의가 열렸던 바로 그 방이었다. 대표들은 각 주를 사회주의 공화국으로 다시 세우고 하나의 연방으로 묶는다는 결의안을 통과시켰다. 반대는 세 표였고, 그 세 표를 던진 버지니아 대표들은 다음 날 아침 회의장에 나오지 않았다.

새 나라의 이름은 미주 사회주의 공화국 연방이었다. 미주라는 말은 브라우더가 직접 골랐다. 언젠가 캐나다와 멕시코와 쿠바도 이 연방에 들어올 테니, 나라 이름에 경계를 박아 둘 필요가 없다고 했다.

코발스키는 그날 저녁 트럭 짐칸에 앉아 집에 편지를 썼다. 공장이 다시 돌아가면 일당이 얼마가 될지 아무도 모른다고 썼다. 그래도 이번에는 공장이 우리 것이라고 썼다. 셋째가 태어난 지 석 달째였고, 그는 아직 그 아이를 보지 못했다.
""", "GFX_report_event_soviet_soldiers", [opt("혁명은 대서양을 건넜다.")], immediate="""
lr_usa_civil_war_end = yes
set_country_flag = LR_route_amc_union
set_cosmetic_tag = LR_AMC_union
mark_focus_tree_layout_dirty = yes
news_event = { id = lr_usa.56 days = 1 }
""")

ev(53, "원고 없는 방송", """
휴이 롱은 승전 연설을 필라델피아가 아니라 캔자스시티 방송국에서 했다. 측근들은 의아해했지만 롱의 설명은 간단했다. 필라델피아는 장군과 은행가의 도시이고, 캔자스시티는 처음 자기를 믿어 준 사람들의 도시라는 것이었다.

방송국 기술자 얼 매코이는 마이크 앞에 앉은 롱을 유리창 너머로 지켜보았다. 롱은 원고를 들고 들어왔다가 첫 문장만 읽고 원고를 뒤집어 버렸다. 그다음 사십 분은 원고 없이 이어졌다. 그는 맥아더를 훈장 단 허수아비라고, 빨갱이들을 모스크바 흉내쟁이라고 불렀다. 그리고 모든 미국 가정에 오천 달러를 주겠다고 약속했다.

매코이가 그 약속을 들은 것은 세 번째였다. 첫 번째는 내전이 시작되던 날, 두 번째는 미시시피 강을 건너던 날이었다. 액수는 그때마다 조금씩 늘었다.

방송이 끝나자 롱은 유리창을 두드려 매코이를 불렀다. 그리고 기술자 월급이 얼마냐고 물었다. 매코이가 대답하자 롱은 그 자리에서 두 배로 올려 주겠다고 했다. 매코이는 그 약속이 지켜졌는지 확인하는 데 넉 달이 걸렸다. 지켜졌다. 다만 그 뒤로 매달 월급의 일 할이 롱의 공제 상자로 들어갔다. 열쇠는 롱만 가지고 있다는 그 초록색 철제 상자였다.
""", "GFX_report_event_journalists_speech", [opt("모든 사람이 왕이다!")], immediate="""
lr_usa_civil_war_end = yes
set_country_flag = LR_route_lng_usa
set_cosmetic_tag = LR_LNG_usa
mark_focus_tree_layout_dirty = yes
news_event = { id = lr_usa.57 days = 1 }
""")

ev(54, "빠진 문장", """
애틀랜타 조지아 주 의사당의 금빛 돔 아래에서 빌보는 남부 연합의 승리를 선언했다. 의사당 계단에는 회색 군복을 입은 장교들이 줄지어 서 있었고, 그 아래 광장은 흰 정장과 모자를 쓴 시민들로 가득했다. 광장 가장자리에는 흑인 노동자들이 따로 모여 있었다. 행사장 청소를 위해 불려 나온 사람들이었다.

연합국 정부 의전 담당 찰스 펜들턴은 의사당 안에서 새 국기를 펼쳤다. 붉은 바탕에 파란 대각선, 그 위에 흰 별 열세 개. 별은 남부 여섯 개 주와 내전에서 점령한 주들을 뜻했다. 북부의 주들까지 별로 그려 넣자는 안은 의회에서 격론 끝에 통과되었다. 그 주의 주민들이 이 깃발을 어떻게 생각하는지는 아무도 묻지 않았다.

빌보의 연설은 짧았다. 남부는 북부의 공장도, 서부의 평원도 원하지 않았지만, 지켜야 할 것을 지키기 위해 어쩔 수 없이 손에 넣었다고 했다. 광장에서 박수가 터졌다.

펜들턴은 그 연설문을 직접 다듬었기 때문에, 빌보가 원고에서 한 문장을 뺐다는 걸 알았다. 1833년에 폐지된 노예제를 되살리지 않겠다는 문장이었다.
""", "GFX_report_event_soldiers_parade", [opt("남부는 다시 일어선다.")], immediate="""
lr_usa_civil_war_end = yes
set_country_flag = LR_route_dxe_csa
set_cosmetic_tag = LR_DXE_csa
set_capital = { state = 365 }
mark_focus_tree_layout_dirty = yes
news_event = { id = lr_usa.58 days = 1 }
""")

ev(55, "아메리카 내전, 맥아더의 승리로 끝나다", """
국가 재건 위원회가 미국 내전에서 승리했습니다. 맥아더 장군의 군대가 마지막 남은 반대 세력의 항복을 받아 냈습니다.

위원회는 헌법을 언제 되살릴지 밝히지 않았습니다. 필라델피아에서는 맥아더에게 새 칭호를 바치는 결의안이 준비되고 있다는 소문이 돌고 있습니다.
""", "GFX_news_event_soldiers_marching", [opt("장군의 나라로군.")], news=True)
ev(56, "미주 사회주의 공화국 연방 수립", """
미국 내전이 노동자 평의회의 승리로 끝났습니다. 필라델피아에서 열린 대표자 대회는 미주 사회주의 공화국 연방의 수립을 선포했습니다.

러시아 공화국 이후 두 번째로 혁명 정부가 살아남은 것입니다. 유럽 각국의 궁정은 경계를 늦추지 않고 있으며, 런던 증권거래소에서는 미국 관련 채권 값이 하루 만에 사 할 넘게 떨어졌습니다.
""", "GFX_news_event_generic_rally", [opt("두 번째 혁명이라니.")], news=True)
ev(57, "휴이 롱, 미국 내전 승리", """
휴이 롱의 군대가 미국 내전에서 승리했습니다. 롱은 캔자스시티에서 방송 연설을 통해 미합중국의 재건을 선포하고, 모든 가정에 오천 달러를 주겠다고 약속했습니다.

「캔자스시티 스타」는 이를 "킹피시의 해일"이라고 불렀습니다. 경제학자들은 이 약속이 실현될 수 없다고 지적합니다. 그러나 롱의 연설을 들은 미국인 가운데 상당수는 경제학자의 말을 듣지 않는 것으로 보입니다.
""", "GFX_news_event_journalists_speech", [opt("킹피시가 이겼군.")], news=True)
ev(58, "아메리고 연합국 수립", """
남부 연합이 미국 내전에서 승리했습니다. 애틀랜타의 의회는 새 국호를 아메리고 연합국으로 정하고, 북부의 주들을 점령지로 편입했습니다.

연합국은 영국과 가까운 관계를 맺을 것으로 보입니다. 리버풀과 맨체스터의 면화 상인들은 이 소식을 반겼다고 합니다.
""", "GFX_news_event_soldiers_marching", [opt("남부가 북부를 삼켰다고?")], news=True)

# ---------------- The routes' later events ----------------
ev(81, "금 단추 사천 개", """
대관식 날 아침 필라델피아에는 비가 왔다. 의전관 로버트 아이컬버거 장군은 독립기념관 앞 광장에 깔아 둔 붉은 융단이 젖는 것을 보며, 오늘 행사를 또 미뤄야 하는지 계산하고 있었다. 이미 두 번 미뤄졌다. 첫 번째는 왕관이 완성되지 않아서였고, 두 번째는 황제의 칭호를 두고 귀족원이 결정을 못 해서였다.

칭호는 결국 아메리고의 황제, 신대륙의 수호자로 정해졌다. 왕관은 웨스트포인트 생도들의 금 단추 사천 개를 녹여 만들었다. 생도들은 그 대신 은 단추를 받았다.

열한 시, 비가 그쳤다. 맥아더는 대원수 군복 위에 흰 망토를 걸치고 연단에 올랐다. 워싱턴이 마지막 연설을 했던 자리에 새로 지은 연단이었다. 왕관을 씌운 사람은 대주교가 아니라 맥아더 자신이었다. 그는 왕관을 두 손으로 들어 올린 채 광장의 군중을 한 바퀴 둘러보고 나서 머리에 썼다.

아이컬버거는 그 장면을 연단 아래에서 지켜보았다. 나중에 그는 회고록에 이렇게 썼다. 황제가 왕관을 들어 올렸을 때 군중은 박수를 쳤지만, 독립기념관 2층 창문은 모두 닫혀 있었다. 그 창문을 닫으라고 명령한 것은 아이컬버거 자신이었다.
""", "GFX_report_event_royal_parade", [opt("황제 폐하 만세.")], immediate="""
set_politics = {
	ruling_party = neutrality
	elections_allowed = no
}
set_popularities = {
	neutrality = 55
	fascism = 25
	democratic = 10
	communism = 10
}
promote_character = {
	character = LR_CNA_macarthur
	ideology = despotism
}
set_cosmetic_tag = LR_CNA_empire
news_event = { id = lr_usa.83 days = 1 }
""")

ev(83, "아메리고 제국 선포", """
맥아더 장군이 필라델피아에서 스스로 왕관을 쓰고 아메리고 제국의 황제로 즉위했습니다. 독립한 지 몇 해 되지 않은 미국 공화국은 이로써 막을 내렸습니다.

새 국호는 신대륙에 이름을 준 아메리고 베스푸치에서 따왔습니다. 유럽의 왕실들은 새 황제에게 축전을 보낼지를 두고 고민하는 것으로 알려졌습니다. 그들 가운데 상당수는 군인이 스스로 왕관을 쓴 전례를 반기지 않습니다.
""", "GFX_news_event_french_parade", [opt("공화국은 끝났다.")], news=True)

ev(82, "아메리고 제국, 신대륙을 석권하다", """
아메리고 제국이 북아메리카와 태평양에서 잇따라 승리하며 신대륙의 패권을 쥐었습니다.

맥아더 황제는 아직 후계자를 정하지 않았으며, 제국 궁정의 원수들 사이에 긴장이 높아지고 있다는 관측이 나옵니다. 런던과 마드리드는 대서양 건너에 나타난 새 제국을 경계하고 있습니다.
""", "GFX_news_event_soldiers_marching", [opt("제국의 시대로군.")], news=True)

ev(92, "미주 혁명, 국경을 넘다", """
미주 사회주의 공화국 연방의 혁명이 이웃 나라로 번지고 있습니다. 미주 적군은 캐나다와 누에바 에스파냐에서 잇따라 승리했으며, 점령지마다 노동자 평의회가 세워지고 있습니다.

필라델피아와 러시아 공화국의 지도자들은 공동 성명을 내고 세계 노동자의 연대를 선언했습니다. 유럽의 왕정 국가들은 혁명이 두 대륙에 뿌리를 내렸다는 사실에 크게 긴장하고 있습니다.
""", "GFX_news_event_generic_rally", [opt("혁명은 수출된다.")], news=True)

ev(93, "롱의 미국, 아메리카를 쥐다", """
휴이 롱 대통령의 미합중국이 경제와 군사 양면에서 아메리카 대륙을 장악했습니다. 롱은 일요일 방송에서 모든 미국인이 왕처럼 살게 되었다고 선언했습니다.

그러나 의회는 지난 두 해 동안 대통령의 법안을 단 한 번도 부결하지 않았고, 비판적인 신문 세 곳이 문을 닫았습니다. 외국의 관찰자들은 롱의 미국을 민주주의라고 불러야 할지를 두고 의견이 갈립니다.
""", "GFX_news_event_journalists_speech", [opt("왕은 하나뿐이야.")], news=True)

ev(94, "카리브 제국의 탄생", """
아메리고 연합국이 쿠바와 누에바 에스파냐를 정복하며 멕시코만 전체를 손에 넣었습니다. 빌보 대통령은 이를 황금의 원의 완성이라고 불렀습니다.

연합국은 영국과의 동맹을 바탕으로 남미 진출을 준비하는 것으로 보입니다. 정복지에서도 재산과 문해력 시험에 따른 투표권 제한이 그대로 적용되고 있습니다.
""", "GFX_news_event_soldiers_marching", [opt("황금의 원이라.")], news=True)

ev(84, "캐나다, 아메리고 제국에 병합되다", """
캐나다 자치령이 아메리고 제국에 항복했습니다. 맥아더 황제는 캐나다 전역을 제국의 북방 왕령으로 병합한다고 선포했습니다.

캐나다 정부의 일부 각료는 영국으로 망명한 것으로 알려졌습니다. 영국 귀족 의회는 병합을 인정하지 않는다고 밝혔지만, 대서양 함대를 움직이지는 않았습니다. 퀘벡에서는 프랑스어 학교를 그대로 두겠다는 황제의 약속이 지켜질지를 두고 의견이 갈립니다.
""", "GFX_news_event_soldiers_marching", [opt("북쪽은 이제 제국의 것이다.")], news=True)

# A conquered American country: take it whole, or leave a government that does as it is told. FROM surrendered.
ALIGN = "\n".join(f"""if = {{
	limit = {{ has_government = {g} }}
	FROM = {{
		set_politics = {{
			ruling_party = {g}
			elections_allowed = no
		}}
	}}
}}""" for g in ("democratic", "communism", "fascism", "neutrality"))
ev(86, "[From.GetName] 항복", """
[From.GetName] 정부가 항복 문서에 서명했다. 수도에는 우리 군대가 들어가 있고, 남은 각료들은 대통령궁 응접실에서 처분을 기다리고 있었다.

참모 회의는 둘로 갈렸다. 한쪽은 그 땅을 통째로 우리 영토로 삼자고 했다. 철도와 광산과 항구를 직접 다스리면 누구의 눈치도 볼 필요가 없다는 것이었다. 다른 쪽은 말 잘 듣는 정부를 세워 두고 손을 떼자고 했다. 낯선 땅을 직접 다스리려면 그 땅의 반란도 직접 감당해야 한다는 것이었다.

회의록을 정리하던 서기는 마지막 줄에 결정은 정부 수반이 내린다고 적었다. 응접실의 각료들은 그동안 커피를 두 번 더 청했다.
""", "GFX_report_event_generic_sign_treaty1", [
    opt("통째로 삼킨다.", """annex_country = {
	target = FROM
	transfer_troops = yes
}
if = {
	limit = {
		FROM = { tag = CAN }
		has_country_flag = LR_route_amerigo_empire
	}
	news_event = { id = lr_usa.84 days = 1 }
}""", ai=60),
    opt("말 잘 듣는 정부를 세운다.", "puppet = FROM\n" + ALIGN, ai=40),
], trigger="FROM = { exists = yes }")

ev(42, "안경", """
뉴욕 뉴버그의 대륙군 숙영지에 익명의 편지가 돈 것은 3월이었다. 장교들은 열네 달째 급료를 받지 못했고, 대륙 회의는 돈이 없다는 말만 되풀이하고 있었다. 편지는 장교들에게 필라델피아로 행진하자고 했다. 회의가 급료를 치를 때까지 무기를 내려놓지 말자고.

존 매클레인 대위도 그 편지를 읽었다. 뉴욕 총독 관저에서 항복 문서에 대위 계급으로 서명했던 그 사람이었다. 그날 이후 그는 진급하지 못했고, 고향의 어머니는 집을 팔았다.

회합은 숙영지 식당에서 열렸다. 장교 이백여 명이 모였을 때 워싱턴이 예고 없이 들어왔다. 그는 연단에 서서 준비해 온 글을 읽었다. 반응은 차가웠다. 매클레인은 옆자리 소령이 팔짱을 끼는 것을 보았다.

워싱턴은 의회 의원 한 사람이 보낸 편지를 꺼내 읽으려다 멈칫했다. 글씨가 작았다. 그는 주머니에서 안경을 꺼냈다. 장교들 가운데 그가 안경 쓴 모습을 본 사람은 거의 없었다.

"여러분, 양해해 주시오. 나는 여러분을 섬기다 머리가 셌고, 이제 눈까지 멀어 가는 것 같소."

식당이 조용해졌다. 매클레인은 팔짱을 꼈던 소령이 손등으로 눈가를 훔치는 것을 보았다. 워싱턴이 나간 뒤 장교들은 행진 대신 의회에 보낼 청원서를 쓰기로 표결했다. 찬성은 만장일치였다. 매클레인은 청원서에 서명하면서, 이번에도 대위 계급을 적었다.
""", "GFX_report_event_soldiers_marching", [
    opt("급료는 반드시 치른다. 내 이름을 걸고.", """custom_effect_tooltip = LR_tt_usa_mg_union_5
hidden_effect = {
	add_to_variable = { LR_usa_union = 5 }
	lr_usa_mg_union_update = yes
}
add_stability = 0.05
add_political_power = -50"""),
])

# New: the old soldier. MacArthur at West Point, near the end.
ev(85, "노병", """
웨스트포인트 사관학교 연병장에 생도 이천사백 명이 정렬했다. 졸업식 연설은 황제가 직접 하기로 되어 있었다. 시종무관 로버트 아이컬버거 원수는 연단 뒤에서 원고를 들고 서 있었다. 대관식 날 의전을 맡았던 그 사람이었고, 이제 머리가 하얗게 셌다.

황제는 원고를 받지 않았다. 일흔이 넘은 노인은 지팡이 없이 연단에 올라, 옥수숫대 파이프를 연단 위에 내려놓고 말을 시작했다. 필리핀의 정글, 플랑드르의 진흙, 필라델피아의 겨울. 그가 지휘했던 부대의 번호를 하나씩 불렀다. 생도들은 그 번호 대부분을 교과서에서만 보았다.

연설 끝에 황제는 자기가 생도였을 때 숙영지에서 부르던 노래를 이야기했다. 노병은 죽지 않는다, 다만 사라질 뿐이라는 노랫말이었다. 그는 그 구절을 두 번 되풀이했다. 두 번째에는 목소리가 갈라졌다.

아이컬버거는 생도들의 얼굴을 보았다. 맨 앞줄의 생도 하나가 차렷 자세로 울고 있었다. 그 옆의 생도는 황제가 아니라 연병장 끝에 선 세 원수의 수행원들을 흘끔거리고 있었다.

연설이 끝나고 황제가 연단을 내려올 때, 아이컬버거는 파이프가 연단 위에 그대로 남아 있는 것을 보았다. 그는 그것을 주머니에 넣었다. 돌려줄 기회는 오지 않았다.
""", "GFX_report_event_usa_macarthur_speech", [opt("노병은 사라질 뿐이다.")])

# The scenes, rewritten to docs/STYLE_GUIDE.md section 9 (america_prose.py).
from america_prose import PROSE as _PROSE  # noqa: E402
for _n, _text in _PROSE.items():
    EVENTS[_n]["desc"] = _text.strip()
