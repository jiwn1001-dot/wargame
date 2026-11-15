"""Each route's signature: a national spirit of its own, strengthened by focuses only that route has, and the two
peace roads, the Feuillants' entente with Britain and the Bourbons' diplomatic revolution with Austria.

build_france.py turns every dict in a row's effects into a boost of the route's signature spirit (line "sig"), and
places the rows like more_focuses(). Texts follow docs/STYLE_GUIDE.md, section 6.
"""

# regime (route flag without LR_route_): spirit name, picture
SIGNATURE = {
    "orleans": ("복수의 맹세", "generic_army_war_college"),
    "bourbon": ("백합과 제단", "generic_king_handled"),
    "marais": ("1791년 헌법", "generic_constitutional_guarantees"),
    "jacobin": ("공안의 공화국", "generic_local_self_management"),
    "girondin": ("상인의 공화국", "generic_license_production"),
    "communist": ("노동자 평의회", "generic_central_management"),
    "anarchist": ("검은 깃발의 규율", "generic_local_self_management"),
    "napoleon": ("통령의 법전", "generic_central_management"),
    "empire": ("제국의 독수리", "generic_army_war_college"),
    "guardian": ("대통령의 서약", "generic_constitutional_guarantees"),
    "red": ("인민의 대육군", "generic_infantry_bonus"),
    "petain": ("노동, 가족, 조국", "generic_fortify_the_borders"),
}

OPINION = "{tag} = {{ add_opinion_modifier = {{ target = ROOT modifier = medium_increase }} }}"
LARGE_OPINION = "{tag} = {{ add_opinion_modifier = {{ target = ROOT modifier = large_increase }} }}"

ENGLAND_AT_PEACE = "ENG = {\n\texists = yes\n\tis_subject = no\n\tNOT = { has_war_with = ROOT }\n}"
AUSTRIA_AT_PEACE = "AUS = {\n\texists = yes\n\tis_subject = no\n\tNOT = { has_war_with = ROOT }\n}"

# The entente: France joins Britain's league. The league's leader makes a faction if it has none.
ENTENTE = ("set_country_flag = LR_entente_cordiale\n"
           "if = {\n\tlimit = { is_in_faction = yes }\n\tleave_faction = yes\n}\n"
           "ENG = {\n\tif = {\n\t\tlimit = { is_in_faction = no }\n\t\tcreate_faction = LR_imperial_league\n\t}\n\tadd_to_faction = ROOT\n}\n"
           "news_event = { id = lr_gnews.30 days = 1 }")
# The diplomatic revolution of 1756 again: Austria leaves Britain and stands with the Bourbons.
REVOLUTION = ("set_country_flag = LR_diplomatic_revolution\n"
              "if = {\n\tlimit = { is_in_faction = no }\n\tcreate_faction = LR_francophonie\n}\n"
              "AUS = {\n\tif = {\n\t\tlimit = { is_in_faction = yes }\n\t\tleave_faction = yes\n\t}\n}\n"
              "add_to_faction = AUS\n"
              "news_event = { id = lr_gnews.31 days = 1 }")
EAST_WAR = "declare_war_on = {\n\ttarget = SOV\n\ttype = annex_everything\n}"

# (prefix, route flag, category, rows); a row is key, icon, name, desc, prerequisite keys, effects, extra fields.
ROWS = [
    # ----- Feuillants: the entente with Britain
    ("LR_MAR_", "LR_route_marais", "외교", [
        ("creditors_talks", "positive_trade_relations", "채권자와의 대화",
         "프랑스는 아직 런던의 채무자다. 배상금 장부를 쥔 시티의 은행가들은 혁명보다 파산을 더 두려워한다. 재무장관이 도버행 배에 오른다. 이번에는 사과가 아니라 제안을 들고 간다.",
         ["london_model"], [OPINION.format(tag="ENG"), {"political_power_gain": 0.05}], {"available": ENGLAND_AT_PEACE}),
        ("reparations_rescheduled", "forceful_treaty", "배상금 재조정 협정",
         "상환 기한을 스무 해 늘리고, 이자의 절반을 프랑스 철도 채권으로 받는다. 런던은 돈을 받고 파리는 숨을 쉰다. 의회 우파는 굴욕이라 외치지만, 빵값은 석 달 만에 내려간다.",
         ["creditors_talks"], [{"consumer_goods_factor": -0.03, "stability_factor": 0.04}], {"available": ENGLAND_AT_PEACE}),
        ("channel_agreement", "navy_doctrines_tactics", "해협 신사협정",
         "포츠머스와 브레스트의 제독들이 한 식탁에 앉는다. 해협에서는 서로의 함대를 세지 않기로 한다. 백 년 전쟁 이래 처음으로 프랑스 해군이 북쪽을 등지고 지중해를 본다.",
         ["reparations_rescheduled"], [LARGE_OPINION.format(tag="ENG"), {"convoy_escort_efficiency": 0.05, "naval_morale_factor": 0.03}], {"available": ENGLAND_AT_PEACE}),
        ("entente_cordiale", "major_alliance", "앙탕트 코르디알",
         "웨스트민스터를 본뜬 헌법을 가진 나라가 웨스트민스터의 동맹이 된다. 1918년의 승전국과 패전국이 같은 깃발 아래 선다. 라인강의 복수를 꿈꾸던 장교들은 이 조약을 끝내 용서하지 않을 것이다.",
         ["channel_agreement"], [ENTENTE, {"stability_factor": 0.05, "political_power_gain": 0.05}],
         {"available": ENGLAND_AT_PEACE + "\nhas_war = no", "me": ["channel", "found_bloc"]}),
        ("eastern_crusade", "major_war", "동방 원정",
         "영국은 대륙에 군대를 보내지 않는다. 그 대신 러시아 공화국이 유럽의 질서를 흔들 때 그것을 막을 칼을 원한다. 프랑스가 그 칼이 된다. 이번에는 패배를 씻는 전쟁이 아니라 동맹의 값을 치르는 전쟁이다.",
         ["entente_cordiale"], [EAST_WAR, {"war_support_factor": 0.05, "army_morale_factor": 0.03}],
         {"available": "has_country_flag = LR_entente_cordiale\nhas_completed_focus = LR_FRA_revenge_army\nSOV = { exists = yes NOT = { is_in_faction_with = ROOT } }"}),
    ]),
    ("LR_MAR_", "LR_route_marais", "정치", [
        ("salon_doctrinaires", "political_pressure", "공론가들의 살롱",
         "기조와 루아예콜라르의 책이 다시 팔린다. 생제르맹의 살롱에서 은행가와 교수들이 왕권과 의회의 경계를 밤새 다툰다. 그들의 결론은 늘 같다. 질서는 재산 있는 자의 손에 있어야 한다.",
         ["senate"], [{"political_power_gain": 0.05, "democratic_drift": 0.02}]),
        ("responsible_ministry", "national_unity", "책임 내각제",
         "장관은 왕이 아니라 의회에 답한다. 왕은 서명하고, 총리는 설명한다. 1830년에 피를 흘리고서야 얻었던 원칙을 이번에는 법전 한 줄로 얻는다.",
         ["salon_doctrinaires"], [{"stability_factor": 0.05}]),
    ]),
    # ----- Bourbons: the diplomatic revolution with Austria
    ("LR_BOU_", "LR_route_bourbon", "외교", [
        ("schonbrunn_envoy", "improve_relations", "쇤브룬의 사절",
         "마리 앙투아네트의 나라에 부르봉의 사절이 간다. 빈의 궁정은 프랑스 혁명을 꺾은 왕을 의심 반, 호기심 반으로 맞는다. 사절의 짐 속에는 루이 16세의 편지 사본이 들어 있다.",
         ["family_pact"], [OPINION.format(tag="AUS"), {"political_power_gain": 0.05}], {"available": AUSTRIA_AT_PEACE}),
        ("habsburg_marriage", "alliance", "합스부르크 혼약",
         "왕세자와 합스부르크 대공녀의 혼담이 오간다. 두 왕가는 세 세기 동안 서로 싸웠고 그만큼 자주 결혼했다. 파리의 신문은 혼수 목록을 1면에 싣고, 혁명가들은 단두대 그림을 담벼락에 그린다.",
         ["schonbrunn_envoy"], [LARGE_OPINION.format(tag="AUS"), {"stability_factor": 0.04, "political_power_gain": 0.05}], {"available": AUSTRIA_AT_PEACE}),
        ("catholic_crowns", "military_deal", "가톨릭 왕관 협약",
         "빈과 파리와 마드리드가 교황 앞에서 서로의 왕좌를 보장한다. 혁명은 한 나라의 일이 아니라 모든 왕관의 적이다. 협약문 초안은 2차 대불전쟁 뒤 맺은 신성 동맹의 문장을 거의 그대로 옮겼다.",
         ["habsburg_marriage"], [OPINION.format(tag="PAP"), {"conscription_factor": 0.02, "stability_factor": 0.03}], {"available": AUSTRIA_AT_PEACE}),
        ("diplomatic_revolution", "major_alliance", "외교 혁명",
         "1756년 카우니츠는 영국을 버리고 베르사유와 손잡았다. 오늘 빈의 외무장관이 같은 결정을 내린다. 런던의 제국연맹에서 오스트리아의 의자가 빈다. 유럽의 지도가 하룻밤 사이에 다시 그려진다.",
         ["catholic_crowns", "latin_league"], [REVOLUTION, {"stability_factor": 0.05, "army_org_factor": 0.03}],
         {"available": AUSTRIA_AT_PEACE + "\nhas_war = no\nAUS = { has_war = no }", "me": ["italy", "danube"]}),
    ]),
    ("LR_BOU_", "LR_route_bourbon", "정치", [
        ("royal_touch", "national_unity", "왕의 손길",
         "랭스의 대관식 다음 날, 왕이 생마르쿨 수도원에서 연주창 환자들의 이마를 만진다. 의사들은 웃지만 몰려든 농민은 수천 명이다. 왕이 낫게 하는지는 몰라도 왕을 믿게 하는 것은 확실하다.",
         ["reims"], [{"stability_factor": 0.04, "war_support_factor": 0.02}]),
        ("bishops_council", "political_pressure", "주교 회의",
         "혁명이 빼앗았던 교회 재산의 일부가 돌아간다. 그 대가로 주교들은 강론에서 왕의 이름을 먼저 부른다. 공화주의 교사들은 학교에서 성호를 긋는 아이들을 보며 이를 간다.",
         ["church"], [{"political_power_gain": 0.07}]),
    ]),
    # ----- Orleans
    ("LR_ORL_", "LR_route_orleans", "정치", [
        ("revenge_oath", "army_doctrines", "복수의 맹세",
         "앵발리드의 돔 아래서 대전쟁 참전 용사 만 명이 왕 앞에 무릎을 꿇는다. 그들은 1918년 11월의 날짜를 군모 안쪽에 새겨 넣었다. 그 날짜를 지울 때까지 이 맹세는 끝나지 않는다.",
         ["veterans"], [{"war_support_factor": 0.05, "army_morale_factor": 0.03}]),
        ("officer_purge", "military_sphere", "장교단 숙청",
         "왕실이 고른 늙은 장군들 가운데 쿠데타를 반대한 자들의 명단이 작성된다. 그들은 연금을 받고 지방으로 간다. 빈자리는 알제리에서 피를 본 대령들이 채운다.",
         ["officers_oath"], [{"army_org_factor": 0.03, "experience_gain_army_factor": 0.05}]),
    ]),
    ("LR_ORL_", "LR_route_orleans", "내정", [
        ("war_industries_office", "construct_mil_factory", "군수 산업청",
         "슈네데르와 르노와 시트로엥의 사장들이 왕실 군수청 회의실에 불려 온다. 그들에게는 선택권이 없다. 대신 계약서의 숫자가 크다.",
         ["autarky"], [{"production_factory_max_efficiency_factor": 0.03, "industrial_capacity_factory": 0.03}]),
    ]),
    # ----- Jacobins
    ("LR_JAC_", "LR_route_jacobin", "정치", [
        ("public_safety", "political_pressure", "공안 위원회",
         "1793년의 이름이 다시 의사당에 걸린다. 이번 위원회에는 단두대가 없다. 대신 은행 장부와 신문사 소유권 명부를 연다. 왕당파 장교 서른 명이 퇴역 통지를 받는다.",
         ["committee"], [{"stability_factor": 0.03, "political_power_gain": 0.05}]),
        ("citizen_army_law", "allies_build_infantry", "시민군 법",
         "모든 시민은 병사이고 모든 병사는 시민이다. 장교는 연대 투표로 추천되고, 귀족 출신 장교의 특권은 폐지된다. 생시르의 교관들은 반발하지만 지원자 수는 두 배가 된다.",
         ["public_safety"], [{"conscription_factor": 0.03, "army_morale_factor": 0.03}]),
        ("pantheon_ceremony", "propaganda", "팡테옹 안장식",
         "조레스의 유해가 팡테옹으로 옮겨진다. 대전쟁 직전 암살당한 사회주의자를 공화국이 위인으로 모신다. 수플로 거리를 따라 노동자들이 붉은 카네이션을 던진다.",
         ["citizen_army_law"], [{"war_support_factor": 0.03, "stability_factor": 0.03}]),
    ]),
    # ----- Girondins
    ("LR_GIR_", "LR_route_girondin", "내정", [
        ("bordeaux_exchange", "positive_trade_relations", "보르도 거래소",
         "지롱드 사람들의 수도는 언제나 보르도였다. 파리 증권거래소의 독점을 깨고 보르도에 두 번째 거래소를 연다. 포도주 상인과 선주들이 첫날 거래량으로 파리를 앞지른다.",
         ["bourse"], [{"industrial_capacity_factory": 0.03, "consumer_goods_factor": -0.02}]),
        ("departmental_charter", "political_pressure", "데파르트망 자치 헌장",
         "파리가 모든 것을 정하던 시대가 끝난다. 각 데파르트망은 자기 예산과 자기 의회를 갖는다. 리옹과 마르세유는 환호하고 파리 시청은 침묵한다.",
         ["provincial_power"], [{"stability_factor": 0.04, "political_power_gain": 0.03}]),
        ("colonial_bank", "construct_civ_factory", "대서양 식민 은행",
         "다카르와 아비장과 카옌을 잇는 은행이 문을 연다. 남은 식민지에서 나는 땅콩과 카카오와 금이 보르도로 온다. 은행 이사회 명단의 절반은 지롱드 의원의 사촌이다.",
         ["atlantic_trade"], [{"production_speed_buildings_factor": 0.03, "industrial_capacity_factory": 0.02}]),
    ]),
    # ----- Commune
    ("LR_COM_", "LR_route_communist", "정치", [
        ("mandat_imperatif", "political_pressure", "명령적 위임",
         "대의원은 언제든 소환될 수 있다. 공장 총회가 손을 들면 그 대의원은 다음 날 아침 공장으로 돌아간다. 파리 코뮌이 1871년에 약속했던 원칙이 법이 된다.",
         ["council"], [{"stability_factor": 0.03, "communism_drift": 0.03}]),
        ("workers_militia", "allies_build_infantry", "노동자 민병대",
         "공장마다 무기고가 생긴다. 교대가 끝난 선반공들이 소총을 메고 운하 둑을 따라 행진한다. 붉은 군대의 장교들은 이 민병대를 오합지졸이라 부르지만, 바리케이드에서는 그들이 더 빠르다.",
         ["red_guards"], [{"conscription_factor": 0.03, "army_morale_factor": 0.02}]),
        ("commune_calendar", "propaganda", "코뮌 기념일",
         "3월 18일이 국경일이 된다. 몽마르트르 언덕에 1871년 연맹병들의 이름이 새겨진 벽이 선다. 아이들은 학교에서 그 이름을 외운다.",
         ["mandat_imperatif"], [{"war_support_factor": 0.04, "stability_factor": 0.02}]),
    ]),
    # ----- Anarchists
    ("LR_ANA_", "LR_route_anarchist", "정치", [
        ("federal_pact", "national_unity", "연방 협약",
         "프루동이 꿈꾼 대로, 코뮌들은 서로 계약을 맺어 연방을 이룬다. 누구도 누구를 다스리지 않는다. 협약문은 열네 쪽이고, 마지막 쪽에는 탈퇴 조항이 있다.",
         ["proudhon"], [{"stability_factor": 0.04, "political_power_gain": 0.03}]),
        ("column_discipline", "army_doctrines", "종대의 규율",
         "장교는 없지만 규율은 있다. 종대마다 선출된 대표가 작전 회의에 들어간다. 계급장 대신 검은 완장을 찬 병사들이 스페인 내전의 교훈을 손으로 받아 적는다.",
         ["columns"], [{"army_org_factor": 0.03, "army_morale_factor": 0.03}]),
        ("free_schools", "construction", "자유 학교",
         "페레르의 합리주의 학교가 마을마다 선다. 시험도 체벌도 교리문답도 없다. 공장 노동자들이 밤에 같은 교실에서 화학과 기하학을 배운다.",
         ["rationalist_schools"], [{"research_speed_factor": 0.03}]),
    ]),
    # ----- Consulate
    ("LR_NAP_", "LR_route_napoleon", "정치", [
        ("council_of_state", "political_pressure", "국무원",
         "통령은 법률가 마흔 명을 국무원에 앉힌다. 그들은 밤새 법조문을 다듬고, 통령은 새벽에 들어와 한 줄씩 지운다. 국무원은 두려워하면서도 그 새벽을 기다린다.",
         ["civil_code"], [{"political_power_gain": 0.07}]),
        ("lycees", "construction", "국립 리세",
         "데파르트망마다 국립 고등학교가 선다. 학생들은 군복을 닮은 교복을 입고, 북소리에 맞춰 교실을 옮긴다. 졸업생은 공무원이 되거나 장교가 된다.",
         ["council_of_state"], [{"research_speed_factor": 0.03, "experience_gain_army_factor": 0.03}]),
        ("gendarmerie_nationale", "fortify_city", "국가 헌병대",
         "산적과 왕당파 게릴라가 들끓던 시골길에 헌병대가 다시 순찰을 돈다. 그들은 통령에게 직접 보고한다. 지방 명사들은 처음으로 밤에 문을 열어 둔다.",
         ["lycees"], [{"stability_factor": 0.05}]),
    ]),
    # ----- Empire
    ("LR_NAP_", "LR_route_empire", "정치", [
        ("imperial_eagles", "army_doctrines", "독수리 기장",
         "연대마다 금빛 독수리 기장이 내려진다. 황제가 직접 샹드마르스에서 나누어 주며 말한다. 이 독수리를 잃느니 죽으라고. 병사들은 그 말을 농담으로 듣지 않는다.",
         ["coronation"], [{"army_morale_factor": 0.04, "war_support_factor": 0.03}]),
        ("imperial_court", "national_unity", "제국 궁정",
         "튈르리 궁에 다시 시종장과 의전관이 선다. 대혁명 이전의 귀족과 새 제국 귀족이 같은 무도회장에 선다. 옛 귀족은 새 귀족의 말투를 비웃고, 새 귀족은 옛 귀족의 빚을 비웃는다.",
         ["imperial_eagles"], [{"political_power_gain": 0.05, "stability_factor": 0.03}]),
        ("conscription_decree", "allies_build_infantry", "징병 칙령",
         "주르당 법이 다시 시행된다. 스무 살 남자는 모두 병적부에 이름을 올린다. 마을마다 추첨 날이면 어머니들이 성당에 촛불을 켠다.",
         ["imperial_court"], [{"conscription_factor": 0.04}]),
    ]),
    # ----- Guardian president
    ("LR_GUA_", "LR_route_guardian", "정치", [
        ("presidential_address", "propaganda", "대통령 담화",
         "매주 일요일 밤 대통령이 라디오에 나온다. 그는 원고 없이 말하고, 가끔 말을 멈추고 기침을 한다. 다음 날 아침 공장과 카페에서 사람들은 그 기침까지 흉내 낸다.",
         ["first_address"], [{"stability_factor": 0.03, "war_support_factor": 0.03}]),
        ("council_of_honour", "national_unity", "명예 위원회",
         "왕당파 원수와 공화파 노조 지도자가 같은 위원회에 앉는다. 대통령은 그들에게 화해가 아니라 협력을 요구한다. 첫 회의는 고성으로 끝났지만, 둘째 회의에는 둘 다 나왔다.",
         ["national_reconciliation"], [{"stability_factor": 0.04, "political_power_gain": 0.03}]),
        ("reserve_officers", "army_doctrines", "예비역 장교단",
         "교사와 변호사와 기술자가 여름마다 군복을 입는다. 공화국의 군대는 직업 군인만의 것이 아니라는 대통령의 신념이다. 장군들은 반대했지만 예산은 의회를 통과했다.",
         ["citizen_army"], [{"experience_gain_army_factor": 0.05, "conscription_factor": 0.02}]),
    ]),
    # ----- Red Napoleon
    ("LR_RED_", "LR_route_red", "정치", [
        ("red_eagle", "army_doctrines", "붉은 독수리",
         "독수리 기장이 붉게 칠해진다. 병사들은 황제가 아니라 인민에게 맹세하지만, 맹세를 받는 사람은 여전히 코르시카의 포병 장교다. 코뮌의 위원들은 그 차이를 두고 밤새 논쟁한다.",
         ["tribune"], [{"army_morale_factor": 0.04, "war_support_factor": 0.03}]),
        ("levee_en_masse_red", "allies_build_infantry", "인민 총동원",
         "1793년의 총동원령이 붉은 인쇄로 다시 붙는다. 공장은 소총을, 농촌은 빵을, 학교는 병사를 낸다. 노인들은 탄약 상자를 나르고 여자들은 천막을 꿰맨다.",
         ["red_eagle"], [{"conscription_factor": 0.04}]),
        ("commissar_corps", "political_pressure", "인민 위원단",
         "연대마다 정치 위원이 장교 곁에 선다. 장교는 전투를 지휘하고 위원은 장교를 지켜본다. 통령은 두 사람 모두 자기에게 보고하게 만든다.",
         ["levee_en_masse_red"], [{"army_org_factor": 0.03, "political_power_gain": 0.03}]),
    ]),
    # ----- Petain
    ("LR_PET_", "LR_route_petain", "정치", [
        ("work_family_fatherland", "propaganda", "노동, 가족, 조국",
         "자유, 평등, 박애가 관공서 현관에서 지워지고 새 표어가 새겨진다. 원수는 프랑스가 진 것은 쾌락의 정신 때문이라고 말한다. 많은 사람이 그 말에 고개를 끄덕인다. 그만큼 패배는 길었다.",
         ["national_revolution"], [{"stability_factor": 0.04, "war_support_factor": 0.02}]),
        ("peasant_return", "construct_civilian", "농촌 회귀",
         "도시의 실업자들에게 땅과 씨앗을 준다. 원수는 흙은 거짓말을 하지 않는다고 말한다. 공장 굴뚝 대신 밀밭이 프랑스의 얼굴이 되기를 바란다.",
         ["return_to_soil"], [{"stability_factor": 0.03, "consumer_goods_factor": -0.02}]),
        ("verdun_veterans", "military_sphere", "베르됭 전우회",
         "원수와 함께 베르됭을 지킨 병사들이 전국 조직을 만든다. 그들은 마을마다 원수의 초상을 걸고, 젊은이들에게 참호의 이야기를 한다. 이야기는 늘 버텼다는 말로 끝난다.",
         ["legion"], [{"army_defence_factor": 0.04, "war_support_factor": 0.02}]),
    ]),
]

# World news for the two peace roads (build_events.py adds them to GREAT_NEWS): title, text, the reader's reply.
NEWS = {
    30: ("앙탕트 코르디알",
         "프랑스가 영국의 제국연맹에 가입했습니다. 런던 외무부에서 열린 서명식에는 프랑스 총리와 영국 외무장관이 참석했으며, 양국은 배상금 재조정과 해협 신사협정을 조약에 포함했다고 밝혔습니다.@@1918년의 승전국과 패전국이 같은 동맹에 선 것은 처음입니다. 베를린과 빈은 아직 공식 논평을 내지 않았고, 파리에서는 재향군인회가 항의 집회를 예고했습니다.",
         "세상이 변했군."),
    31: ("외교 혁명",
         "오스트리아가 영국의 제국연맹을 탈퇴하고 프랑스가 이끄는 프랑코포니에 가입했습니다. 빈의 외무부는 부르봉 왕가와 합스부르크 왕가의 혼약을 계기로 두 왕관이 서로의 왕좌를 보장하기로 했다고 발표했습니다.@@런던은 이 결정을 배신이라고 규탄했습니다. 1756년 이래 두 번째 외교 혁명이라는 평가가 나오는 가운데, 베를린은 동부 국경 수비대를 늘리기 시작한 것으로 알려졌습니다.",
         "카우니츠가 무덤에서 웃겠군."),
    32: ("두알라의 망명정부",
         "북독일 연방의 빌헬름 황태자가 카메룬의 두알라에서 독일 망명정부 수립을 선포했습니다. 베를린이 함락된 뒤 연방의 해외 영토는 프랑스에 넘어가지 않고 이 망명정부의 관할로 남았습니다.@@망명정부는 카메룬과 적도 아프리카, 인도차이나, 태평양의 섬들을 다스린다고 밝혔습니다. 런던은 아직 승인 여부를 밝히지 않았고, 파리 외무부는 이 정부를 인정하지 않는다고 발표했습니다.",
         "끝까지 버티겠다는 건가."),
}
NEWS = {k: (t, d.replace("@@", chr(92) + "n" + chr(92) + "n"), r) for k, (t, d, r) in NEWS.items()}
