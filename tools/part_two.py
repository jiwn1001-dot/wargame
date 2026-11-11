"""Part two of the eight older routes: three chapters that follow the great war.

Chapter six opens when the war has begun, chapter seven when Prussia has fallen, chapter eight when Prussia and
one more great enemy (Austria or Britain) have fallen. build_france.py appends these to each route's story and
gates them with GATES.
"""
from france_story import chapter

P = "\\n\\n"
Q = '\\"'


def say(line):
    return f"{Q}{line}{Q}"


AT_WAR = "custom_trigger_tooltip = {\n\ttooltip = LR_tt_part2_war\n\tOR = {\n\t\thas_war = yes\n\t\thas_country_flag = LR_germany_defeated\n\t}\n}"
PRUSSIA = "custom_trigger_tooltip = {\n\ttooltip = LR_tt_part2_prussia\n\thas_country_flag = LR_germany_defeated\n}"
NEW_EUROPE = ("custom_trigger_tooltip = {\n\ttooltip = LR_tt_part2_europe\n\thas_country_flag = LR_germany_defeated\n"
              "\tOR = {\n\t\thas_country_flag = LR_austria_defeated\n\t\thas_global_flag = LR_settled_britain\n\t}\n}")
TOOLTIPS = {
    "LR_tt_part2_war": "대전쟁이 시작되었거나 프로이센을 이미 꺾었어야 합니다.",
    "LR_tt_part2_prussia": "§Y프로이센§!을 꺾었어야 합니다.",
    "LR_tt_part2_europe": "§Y프로이센§!과 함께 §Y합스부르크§!나 §Y영국§! 가운데 하나를 꺾었어야 합니다.",
}

PART2 = {
    # ===== Orleans: the king of revenge =====
    "LR_ORL_duke": [
        chapter("mobilisation_day", "military_sphere", "동원의 날", "왕의 동원령이 전국의 교회 종탑에서 울립니다.", {"war_support_factor": 0.02},
                "종이 울리는 아침", P.join([
                    "8월의 아침, 프랑스 전역의 교회 종이 한꺼번에 울립니다. 1914년에도 이 종소리로 전쟁이 시작되었습니다. 마을 광장마다 동원령 포스터가 붙고, 젊은이들이 역으로 걸어갑니다.",
                    "동역 플랫폼에서 왕이 출정하는 연대를 사열합니다. 1914년의 병사들은 크리스마스 전에 돌아온다고 노래했습니다. 이번 병사들은 아무 노래도 부르지 않습니다.",
                    "참모총장이 왕에게 묻습니다. " + say("폐하께서 직접 전선에 나가시겠습니까, 파리에서 지휘하시겠습니까?")]), "soldiers_marching", [
                    ("왕은 전선에 선다. 1918년의 장군들처럼 뒤에 숨지 않는다.", {"army_morale_factor": 0.04, "stability_factor": -0.02}),
                    ("왕은 파리에 남는다. 전쟁은 참모본부에서 이긴다.", {"political_power_gain": 0.03, "army_org_factor": 0.02}),
                ]),
        chapter("rhine_crossed", "major_war", "라인강을 건너다", "프로이센이 무너졌습니다. 왕은 베를린에서 무엇을 할 것인가.", {"war_support_factor": 0.03},
                "포츠담의 왕", P.join([
                    "포츠담 상수시 궁전. 프리드리히 대왕의 서재에 프랑스 왕이 앉았습니다. 1871년 베르사유 거울의 방에서 독일 제국을 선포한 그 가문의 궁전입니다.",
                    "참모들이 파리에서 온 전보를 읽습니다. 국민은 열광하고 있고, 재향군인회는 베를린에서 개선 행진을 하자고 요구합니다.",
                    "그런데 왕의 책상에는 다른 서류도 있습니다. 동원된 병사 가족들의 청원서입니다. 이제 아들을 돌려 달라고."]), "france_parade", [
                    ("베를린에서 개선 행진을 한다. 1871년의 빚을 갚는다.", {"war_support_factor": 0.05, "stability_factor": 0.02}),
                    ("일부 연대를 귀향시킨다. 전쟁은 아직 끝나지 않았지만, 약속은 지킨다.", {"stability_factor": 0.04, "political_power_gain": 0.02}),
                ]),
        chapter("kings_europe", "national_unity", "왕들의 새 유럽", "복수는 끝났습니다. 왕은 무엇을 남길 것인가.", {"stability_factor": 0.03},
                "복수 다음의 날", P.join([
                    "튈르리 궁 회의실. 탁자 위의 유럽 지도에는 이제 프랑스의 색이 라인강 너머까지 칠해져 있습니다. 1918년의 항복 문서에 서명한 장군들은 모두 죽거나 물러났습니다.",
                    "그런데 회의실의 장군들은 만족하지 않습니다. 대령들의 음모를 꾸몄던 젊은 장교들이 이제 장군이 되었고, 그들은 다음 전쟁을 원합니다.",
                    "늙은 재무장관이 조용히 말합니다. " + say("폐하, 복수는 끝났습니다. 이제 무엇을 위해 싸우십니까?")]), "generic_parliament", [
                    ("군을 줄이고 국경을 굳힌다. 왕은 평화로 기억될 것이다.", {"stability_factor": 0.06, "war_support_factor": -0.03}),
                    ("군은 줄이지 않는다. 프랑스의 영광은 국경선에서 멈추지 않는다.", {"war_support_factor": 0.05, "army_morale_factor": 0.03}),
                ]),
    ],
    # ===== Bourbon: the restored crown =====
    "LR_BOU_restored": [
        chapter("te_deum", "national_unity", "출정 미사", "노트르담에서 왕이 출정 미사를 올립니다.", {"stability_factor": 0.02},
                "노트르담의 테 데움", P.join([
                    "노트르담 대성당. 파리 대주교가 출정하는 군대를 위해 테 데움을 부릅니다. 왕은 성왕 루이의 검을 제단 위에 올려놓았다가 다시 집어 듭니다.",
                    "미사가 끝나고 성당 앞 광장에 나서자 군중이 환호합니다. 그런데 광장 한쪽 구석에는 침묵하는 사람들도 있습니다. 노동자 구역에서 온 사람들입니다. 그들의 아들들도 내일 기차에 오릅니다.",
                    "궁정 대신이 왕에게 속삭입니다. 노동자들에게도 한마디를 해 주시라고."]), "france_parade", [
                    ("왕은 노동자 구역을 직접 찾아간다.", {"stability_factor": 0.04, "communism_drift": -0.02}),
                    ("왕은 왕의 자리에 있는다. 신은 프랑스와 함께한다.", {"war_support_factor": 0.04}),
                ]),
        chapter("cousins_war", "major_alliance", "사촌들의 전쟁", "마드리드와 나폴리의 사촌들이 함께 싸우고 있습니다.", {"political_power_gain": 0.02},
                "베를린에서 온 승전보", P.join([
                    "프로이센이 무너졌다는 승전보가 마드리드와 나폴리에도 동시에 전해졌습니다. 세 부르봉 왕가의 왕궁에서 같은 날 축포가 울립니다.",
                    "마드리드의 사촌이 축하 편지와 함께 청구서를 보냈습니다. 스페인 군대가 피레네를 지킨 대가로 모로코의 땅을 달라고.",
                    "궁정 대신들이 의견을 나눕니다. 가문의 의리와 프랑스의 이익이 늘 같은 것은 아닙니다."]), "generic_sign_treaty1", [
                    ("사촌의 청을 들어준다. 부르봉의 피는 땅보다 진하다.", {"political_power_gain": 0.03, "friend": "SPR"}),
                    ("정중히 미룬다. 왕관은 프랑스의 것이다.", {"stability_factor": 0.03}),
                ]),
        chapter("holy_alliance", "major_alliance", "신성 동맹", "2차 대불전쟁 뒤 빈에서처럼 왕들의 동맹이 다시 맺어집니다. 이번에는 프랑스가 주인입니다.", {"stability_factor": 0.03},
                "왕들의 회의", P.join([
                    "베르사유 궁 거울의 방. 유럽의 왕과 대공들이 모였습니다. 2차 대불전쟁 뒤 빈 회의에서 혁명 프랑스를 묶었던 왕들의 후손들이, 이번에는 부르봉의 초대로 왔습니다.",
                    "왕이 일어서서 신성 동맹의 부활을 제안합니다. 왕관과 제단을 지키는 왕들의 동맹. 다시는 어느 나라에서도 혁명이 일어나지 않도록.",
                    "회의장 끝자리에서 젊은 대공 하나가 손을 듭니다. " + say("폐하, 프랑스는 150년 전 혁명을 막지 못했습니다. 이번에는 무엇이 다릅니까?")]), "generic_parliament", [
                    ("왕관과 제단의 동맹을 맺는다. 혁명은 다시 오지 않는다.", {"stability_factor": 0.05, "political_power_gain": 0.03}),
                    ("동맹 대신 헌장을 약속한다. 왕도 법 아래 있다.", {"stability_factor": 0.04, "democratic_drift": 0.02}),
                ]),
    ],
    # ===== Commune: the red republic =====
    "LR_COM_commune": [
        chapter("levee_red", "allies_build_infantry", "붉은 총동원", "1793년처럼 조국이 위험에 처했다고 위원회가 선언합니다.", {"war_support_factor": 0.02},
                "조국이 위험하다", P.join([
                    "시청 발코니에 커다란 현수막이 걸립니다. 조국이 위험하다. 1792년 국민공회가 내걸었던 그 문장입니다.",
                    "공장 평의회마다 지원병 명부가 돌고, 하루 만에 10만 명이 이름을 적었습니다. 그런데 장교가 모자랍니다. 왕의 사관학교를 나온 장교들은 대부분 망명했거나 감옥에 있습니다.",
                    "국방 위원이 위원회에 묻습니다. 감옥의 장교들을 풀어 줄 것인가."]), "soldiers_marching", [
                    ("감옥의 장교들을 풀고 정치위원을 붙인다.", {"army_org_factor": 0.03, "communism_drift": -0.01}),
                    ("노동자 중에서 장교를 뽑는다. 혁명의 군대는 혁명가가 이끈다.", {"army_morale_factor": 0.03, "communism_drift": 0.02}),
                ]),
        chapter("ruhr_soviets", "propaganda", "루르의 평의회", "프로이센이 무너지자 루르의 광부들이 평의회를 세웁니다.", {"political_power_gain": 0.02},
                "에센의 붉은 깃발", P.join([
                    "에센의 크루프 공장. 프랑스 코뮌군이 도착하기 전에 광부들이 먼저 공장을 점거했습니다. 굴뚝마다 붉은 깃발이 걸렸습니다.",
                    "루르 평의회의 대표단이 파리로 와서 묻습니다. 우리는 프랑스의 일부가 되는가, 아니면 독일 코뮌을 세우는가.",
                    "위원회가 둘로 나뉩니다. 독일 노동자들의 자결권을 존중하자는 쪽과, 혁명의 심장은 하나여야 한다는 쪽입니다."]), "generic_factory", [
                    ("독일 코뮌을 세우게 한다. 형제는 형제일 뿐 신하가 아니다.", {"stability_factor": 0.03, "communism_drift": 0.02}),
                    ("파리의 지도를 받게 한다. 혁명에는 하나의 심장이 필요하다.", {"political_power_gain": 0.04, "industrial_capacity_factory": 0.02}),
                ]),
        chapter("red_continent", "national_unity", "붉은 대륙", "유럽 절반에 붉은 깃발이 걸렸습니다. 코뮌은 무엇이 될 것인가.", {"stability_factor": 0.03},
                "인터내셔널의 대회", P.join([
                    "몽마르트르의 인터내셔널 회관. 유럽 각지에서 온 대표 3백 명이 모였습니다. 2년 전만 해도 망명자였던 그들이 이제 각자의 나라에서 정부를 이끌고 있습니다.",
                    "의제는 하나입니다. 유럽 노동자 공화국 연방을 세울 것인가. 파리 대표는 수도를 파리에 두자고 하고, 베를린 대표는 돌아가며 맡자고 합니다.",
                    "회의장 뒤편에서 늙은 코뮌 투사가 중얼거립니다. " + say("1871년에는 72일 만에 끝났지. 이번에는 얼마나 갈까.")]), "generic_parliament", [
                    ("연방의 수도는 파리다. 혁명이 시작된 곳이다.", {"political_power_gain": 0.05, "war_support_factor": 0.02}),
                    ("수도는 돌아가며 맡는다. 연방은 평등해야 한다.", {"stability_factor": 0.05, "communism_drift": 0.03}),
                ]),
    ],
    # ===== Montagnards =====
    "LR_JAC_committee": [
        chapter("war_vote", "political_pressure", "개전 표결", "의회가 전쟁을 표결합니다. 공안위원회의 이름이 무겁습니다.", {"war_support_factor": 0.02},
                "부르봉 궁의 밤", P.join([
                    "부르봉 궁 회의장, 새벽 두 시. 선전포고 표결이 열네 시간째 이어지고 있습니다. 산악파 의원들은 1792년의 의용병 이야기를 꺼내고, 반대파는 1914년의 전사자 명단을 읽습니다.",
                    "총리가 마지막 연설을 합니다. 공화국은 왕들의 유럽에 둘러싸여 있고, 지금 싸우지 않으면 다음에는 공화국 자체가 없을 것이라고.",
                    "의장이 표결을 부칩니다. 찬성표가 과반을 조금 넘습니다. 반대한 의원들은 자리에 앉은 채 고개를 숙입니다."]), "generic_parliament", [
                    ("반대한 의원들에게도 전시 내각의 자리를 준다.", {"stability_factor": 0.04, "seats": 3}),
                    ("반대파를 패배주의자로 규정한다.", {"war_support_factor": 0.04, "stability_factor": -0.02}),
                ]),
        chapter("liberators", "propaganda", "해방자인가 정복자인가", "프로이센이 무너지자 공화국 군대가 점령지를 다스리게 됩니다.", {"political_power_gain": 0.02},
                "쾰른 시청의 삼색기", P.join([
                    "쾰른 시청 광장. 공화국 군대가 왕의 동상을 끌어내리고 자유의 나무를 심습니다. 1794년 프랑스 혁명군이 이 도시에 들어왔을 때 했던 그대로입니다.",
                    "그런데 시민들의 표정은 엇갈립니다. 시장 노동자들은 환호하지만, 상인들은 징발 명령서를 들고 군정청 앞에 줄을 섰습니다.",
                    "군정 장관이 파리에 묻습니다. 우리는 해방자로 왔습니까, 정복자로 왔습니까?"]), "france_parade", [
                    ("징발을 멈추고 시민 의회를 선거로 세운다.", {"stability_factor": 0.03, "democratic_drift": 0.02}),
                    ("징발은 계속한다. 해방에도 값이 있다.", {"industrial_capacity_factory": 0.03, "stability_factor": -0.01}),
                ]),
        chapter("sister_republics", "national_unity", "자매 공화국들", "공화국이 이긴 땅마다 새 공화국이 섭니다.", {"stability_factor": 0.03},
                "공화국들의 회의", P.join([
                    "파리 뤽상부르 궁. 프랑스 군대가 지나간 땅마다 세워진 자매 공화국의 대표들이 모였습니다. 바타비아, 헬베티아, 라인, 남독일.",
                    "그들은 프랑스에 감사하지만 동시에 묻습니다. 우리 군대에 프랑스 장교가 있는 것은 언제까지냐고. 우리 헌법을 우리가 쓰는 것은 언제부터냐고.",
                    "총리가 회의를 마치며 말합니다. " + say("1795년의 자매 공화국들은 우리가 지켜 주지 못해 2차 대불전쟁에서 무너졌습니다. 이번에는 그들이 스스로 설 수 있게 하겠습니다.")]), "generic_parliament", [
                    ("자매 공화국에 완전한 자치를 약속한다.", {"stability_factor": 0.05, "democratic_drift": 0.03}),
                    ("공동 방위 조약으로 묶는다. 왕들은 아직 남아 있다.", {"war_support_factor": 0.04, "political_power_gain": 0.03}),
                ]),
    ],
    # ===== Girondins =====
    "LR_GIR_cabinet": [
        chapter("war_bonds", "trade", "전쟁 채권", "전쟁 비용을 세금이 아니라 채권으로 마련합니다.", {"political_power_gain": 0.02},
                "증권거래소의 애국심", P.join([
                    "파리 증권거래소 객장. 정부가 발행한 첫 전쟁 채권이 개장 한 시간 만에 매진되었습니다. 보르도와 리옹의 상인들이 앞다투어 샀습니다.",
                    "그런데 재무장관의 책상에는 다른 보고서가 있습니다. 채권을 산 사람들은 대부분 은행가와 선주들이고, 노동자들은 오른 빵값을 감당하느라 채권을 살 돈이 없습니다.",
                    "산악파 신문이 1면에 썼습니다. 부자들은 이자를 받고, 가난한 자들은 피를 바친다."]), "generic_read_write", [
                    ("소액 채권을 만들어 노동자도 살 수 있게 한다.", {"stability_factor": 0.03}),
                    ("시장에 맡긴다. 돈을 내는 사람이 전쟁을 산다.", {"political_power_gain": 0.03, "industrial_capacity_factory": 0.02}),
                ]),
        chapter("ruhr_contracts", "construct_civ_factory", "루르의 계약서", "프로이센이 무너지자 프랑스 기업들이 루르로 몰려갑니다.", {"industrial_capacity_factory": 0.02},
                "에센의 경매", P.join([
                    "에센의 호텔 연회장. 군정청이 압류한 루르의 탄광과 제철소를 경매에 부칩니다. 슈나이더, 드방델, 리옹 신용은행의 대리인들이 번호판을 들고 앉았습니다.",
                    "경매가 끝나 갈 무렵, 독일 광부 대표들이 연회장 문을 밀고 들어옵니다. 우리의 일자리를 팔지 말라고.",
                    "군정 장관이 파리의 지시를 기다립니다. 지롱드 내각이 믿는 것은 시장입니다. 그러나 시장은 총을 든 광부를 계산하지 않습니다."]), "generic_factory", [
                    ("경매를 계속하되 광부의 고용을 조건으로 건다.", {"stability_factor": 0.03, "industrial_capacity_factory": 0.02}),
                    ("경매를 계속한다. 계약은 계약이다.", {"political_power_gain": 0.04}),
                ]),
        chapter("common_market", "positive_trade_relations", "대륙의 시장", "관세가 사라진 유럽을 상인들이 꿈꿉니다.", {"political_power_gain": 0.03},
                "관세 없는 유럽", P.join([
                    "보르도 상공회의소. 지롱드파의 오랜 꿈이 처음으로 손에 닿습니다. 프랑스와 자매 공화국들, 라인 연방 사이의 관세를 모두 없애는 조약 초안입니다.",
                    "선주들과 은행가들은 환호합니다. 그러나 북부의 농민들은 독일의 싼 밀이 들어오면 망한다며 트랙터로 도로를 막았습니다.",
                    "총리가 초안에 서명하기 전에 망설입니다. 나폴레옹의 대륙봉쇄는 칼로 유럽을 묶었습니다. 지롱드는 계산서로 묶으려 합니다."]), "generic_sign_treaty1", [
                    ("조약에 서명한다. 상품이 국경을 넘으면 군대는 넘지 않는다.", {"political_power_gain": 0.05, "industrial_capacity_factory": 0.03}),
                    ("농산물은 빼고 서명한다.", {"stability_factor": 0.05}),
                ]),
    ],
    # ===== Feuillants =====
    "LR_MAR_cabinet": [
        chapter("kings_call", "military_sphere", "입헌 군주의 소집령", "헌법 아래의 왕이 처음으로 군대를 부릅니다.", {"war_support_factor": 0.02},
                "왕의 서명, 의회의 서명", P.join([
                    "튈르리 궁 집무실. 동원령 문서에는 서명란이 둘 있습니다. 하나는 왕의 것, 하나는 의회 의장의 것입니다. 1791년 헌법이 정한 그대로입니다.",
                    "왕이 먼저 서명하려 하자 의장이 손을 들어 막습니다. 헌법에 따르면 의회의 표결이 먼저라고.",
                    "궁정 대신들이 얼굴을 붉힙니다. 국민방위대 사령관이 조용히 말합니다. " + say("순서가 바뀌면, 그것은 더 이상 입헌 군주정이 아닙니다.")]), "generic_parliament", [
                    ("의회가 먼저 표결하고 왕이 서명한다.", {"stability_factor": 0.04, "democratic_drift": 0.02}),
                    ("전시에는 왕이 먼저 서명한다. 헌법은 평시의 것이다.", {"war_support_factor": 0.04, "political_power_gain": 0.02}),
                ]),
        chapter("notables_peace", "dangerous_deal", "명사들의 강화", "프로이센이 무너지자 명사들이 서둘러 강화를 원합니다.", {"stability_factor": 0.02},
                "살롱의 지도", P.join([
                    "생제르맹 거리의 어느 살롱. 은행가와 대지주와 대주교가 모여 지도를 펼쳤습니다. 프로이센은 무너졌고, 그들은 이제 전쟁을 끝내고 싶어 합니다.",
                    "전쟁이 길어질수록 세금이 오르고, 세금이 오를수록 거리의 급진파가 힘을 얻습니다. 푀양파가 가장 두려워하는 것은 적국의 군대가 아니라 파리의 바리케이드입니다.",
                    "총리가 살롱을 나서며 비서에게 말합니다. " + say("명사들은 평화를 원하고, 장군들은 승리를 원한다. 나는 둘 다 필요하다.")]), "generic_read_write", [
                    ("서둘러 강화를 모색한다. 혁명은 전쟁의 자식이다.", {"stability_factor": 0.05, "war_support_factor": -0.03}),
                    ("끝까지 싸운다. 어설픈 강화는 다음 전쟁을 부른다.", {"war_support_factor": 0.04}),
                ]),
        chapter("concert", "national_unity", "유럽 협조 체제", "입헌 프랑스가 왕들의 유럽과 공존할 질서를 제안합니다.", {"stability_factor": 0.03},
                "빈 회의의 그림자", P.join([
                    "빈의 회의장. 2차 대불전쟁 뒤 왕들이 혁명 프랑스를 묶었던 그 도시에서, 이번에는 입헌 프랑스가 회의를 주재합니다.",
                    "총리가 제안하는 것은 정복도 혁명도 아닌 균형입니다. 강대국들이 정기적으로 모여 분쟁을 조정하는 유럽 협조 체제. 그리고 모든 왕국에 최소한의 헌장을.",
                    "왕들의 대사들이 서로를 바라봅니다. 헌장이라는 말이 그들의 귀에는 아직 혁명처럼 들립니다."]), "generic_parliament", [
                    ("헌장을 조건으로 건다. 유럽은 법 위에 서야 한다.", {"democratic_drift": 0.03, "stability_factor": 0.04}),
                    ("헌장은 빼고 균형만 맺는다. 평화가 먼저다.", {"stability_factor": 0.05, "political_power_gain": 0.02}),
                ]),
    ],
    # ===== Empire =====
    "LR_NAP_coronation": [
        chapter("bulletin", "propaganda", "대육군 공보", "황제의 공보가 전선의 소식을 전합니다. 늘 승리뿐입니다.", {"war_support_factor": 0.02},
                "제1호 공보", P.join([
                    "파리의 모든 신문 1면에 같은 글이 실립니다. 대육군 제1호 공보. 황제가 직접 받아쓰게 한 전황 보고입니다.",
                    "공보에 따르면 적군은 도망치고 있고, 아군의 손실은 미미합니다. 대전쟁 때 참모본부의 공보도 늘 그랬습니다. 파리 사람들은 그때 이런 말을 만들어 냈습니다. 공보처럼 거짓말한다.",
                    "경찰장관이 보고합니다. 카페에서 공보를 비웃는 사람들이 늘고 있다고."]), "generic_read_write", [
                    ("공보에 손실도 적게 한다. 진실이 신뢰를 산다.", {"stability_factor": 0.03}),
                    ("공보를 비웃는 자를 잡아들인다.", {"war_support_factor": 0.04, "stability_factor": -0.01}),
                ]),
        chapter("berlin_decree", "forceful_treaty", "베를린 칙령", "베를린에서 황제가 대륙봉쇄를 다시 선포합니다.", {"political_power_gain": 0.02},
                "베를린 칙령", P.join([
                    "베를린 왕궁, 프리드리히 대왕의 옛 서재. 황제가 대륙봉쇄령에 서명합니다. 프로이센 왕들이 프랑스를 겨눈 동맹 조약에 서명하던 바로 그 책상입니다.",
                    "영국 상품은 대륙의 어느 항구에도 들어올 수 없습니다. 함부르크와 암스테르담의 상인들은 장부를 덮습니다. 밀수꾼들은 새 지도를 그립니다.",
                    "외무장관이 묻습니다. 이 칙령은 동맹국에도 적용됩니까?"]), "generic_sign_treaty1", [
                    ("모든 나라에 적용한다. 예외는 구멍이다.", {"war_support_factor": 0.03, "industrial_capacity_factory": 0.02}),
                    ("동맹국은 면제한다. 친구를 굶길 수는 없다.", {"stability_factor": 0.03, "political_power_gain": 0.02}),
                ]),
        chapter("grand_empire", "national_unity", "대제국", "황제의 제국이 샤를마뉴 이후 가장 넓은 국경을 그렸습니다.", {"stability_factor": 0.03},
                "130개의 도", P.join([
                    "튈르리 궁 지도실. 벽에 걸린 프랑스 제국 지도에는 130개의 도가 그려져 있습니다. 암스테르담에서 로마까지, 함부르크에서 바르셀로나까지. 샤를마뉴의 제국보다 넓습니다.",
                    "그 바깥에는 형제들과 원수들이 다스리는 위성 왕국들이 둘러싸고 있습니다. 바르샤바 대공국, 나폴리 왕국, 라인 연방.",
                    "황제가 지도 앞에서 오래 서 있다가 묻습니다. " + say("여기까지 온 자들은 그다음에 무엇을 했지?") + " 원수 하나가 대답합니다. " + say("스웨덴의 카를 12세는 러시아로 갔습니다, 폐하.")]), "france_parade", [
                    ("여기서 멈춘다. 제국은 넓혀서가 아니라 지켜서 위대해진다.", {"stability_factor": 0.06}),
                    ("멈추지 않는다. 그는 겨울을 몰랐고, 나는 안다.", {"war_support_factor": 0.05, "army_morale_factor": 0.03}),
                ]),
    ],
    # ===== Guardian =====
    "LR_NAP_guardian": [
        chapter("war_powers", "political_pressure", "전시 대권", "대통령에게 전시 대권을 주자는 법안이 올라옵니다.", {"war_support_factor": 0.02},
                "대통령의 망설임", P.join([
                    "부르봉 궁. 대통령 지지 의원들이 전시 대권법을 발의했습니다. 전쟁 동안 대통령이 의회 없이 칙령으로 다스릴 수 있게 하는 법입니다.",
                    "법안은 통과될 것이 확실합니다. 문제는 대통령 자신입니다. 그는 왕관을 거절한 사람입니다. 이 법안은 왕관보다 작지만, 왕관과 같은 쪽을 향합니다.",
                    "비서실장이 묻습니다. 법안에 서명하시겠습니까?"]), "generic_parliament", [
                    ("거부한다. 전쟁도 의회와 함께 치른다.", {"stability_factor": 0.04, "democratic_drift": 0.02, "seats": 3}),
                    ("서명하되 종전과 함께 효력이 끝나게 한다.", {"political_power_gain": 0.04, "war_support_factor": 0.03}),
                ]),
        chapter("general_president", "military_sphere", "전선의 대통령", "프로이센이 무너지자 대통령이 전선을 찾습니다.", {"army_morale_factor": 0.02},
                "막사의 대통령", P.join([
                    "라인강 건너의 전선 막사. 연미복 대신 낡은 야전 외투를 입은 대통령이 병사들 사이를 걷습니다. 알제리에서 그를 따랐던 고참병들이 그를 알아보고 경례합니다.",
                    "한 병사가 큰 소리로 외칩니다. 황제 만세! 막사가 순간 조용해집니다. 그 외침을 따라 하는 병사도 있고, 고개를 돌리는 병사도 있습니다.",
                    "대통령이 그 병사에게 다가갑니다."]), "soldiers_marching", [
                    (say("나는 황제가 아니다. 너희와 같은 시민이다."), {"stability_factor": 0.04, "democratic_drift": 0.02}),
                    ("아무 말 없이 병사의 어깨를 두드린다.", {"army_morale_factor": 0.04}),
                ]),
        chapter("republican_peace", "national_unity", "공화국의 평화", "대통령이 승전국으로서 강화의 원칙을 발표합니다.", {"stability_factor": 0.03},
                "열네 개의 원칙", P.join([
                    "베르사유 궁 거울의 방. 대통령이 강화 회의 개막 연설을 합니다. 1919년 이곳에서 프랑스를 무릎 꿇린 조약이 서명되었습니다. 이번에는 프랑스가 원칙을 말합니다.",
                    "민족 자결, 비밀 외교의 폐지, 군비 축소, 그리고 국가들의 연맹. 그는 왕관을 거절했듯이 복수도 거절하겠다고 말합니다.",
                    "회의장 뒤편의 장군들이 낮게 투덜거립니다. 1918년에 우리에게는 아무도 원칙을 말해 주지 않았다고."]), "generic_sign_treaty1", [
                    ("관대한 강화를 맺는다. 복수는 다음 전쟁을 낳는다.", {"stability_factor": 0.05, "democratic_drift": 0.03}),
                    ("원칙은 말하되 배상금은 받는다. 국민은 기억한다.", {"political_power_gain": 0.04, "war_support_factor": 0.02}),
                ]),
    ],
}
GATES = {}
for _head, _chapters in PART2.items():
    _prefix = _head[:7]  # "LR_XXX_"
    for _chapter, _gate in zip(_chapters, (AT_WAR, PRUSSIA, NEW_EUROPE)):
        GATES[_prefix + _chapter["key"]] = _gate
# The empire and the presidency share Napoleon's prefix.
GATES = {k.replace("LR_NAP_war_powers", "LR_GUA_war_powers").replace("LR_NAP_general_president", "LR_GUA_general_president")
         .replace("LR_NAP_republican_peace", "LR_GUA_republican_peace"): v for k, v in GATES.items()}
FOCUS_TEXT = {}
for _head, _chapters in PART2.items():
    _prefix = "LR_GUA_" if _head == "LR_NAP_guardian" else _head[:7]
    for _chapter in _chapters:
        _first = _chapter["text"].split(P)[0]
        FOCUS_TEXT[_prefix + _chapter["key"]] = _chapter["desc"] + " " + _first
