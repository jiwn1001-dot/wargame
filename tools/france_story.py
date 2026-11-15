"""The spine of each French route: one focus per chapter, and the event it fires.

Chapter: key, icon, focus name, focus text, focus reward, event title, event text, picture, options, optional alternative text.
Option: text, effects. Effects are modifier tokens from LABELS in build_france.py, plus:
seats, op (all regional opposition -15), dev (economic reconstruction), relief (disarmament steps), heal (defeat),
civ, mil, friend (a country tag), flag (remembered choice), need / avoid (shows the option only with or without a flag).
Alternative text: (flag, text), used instead of the event text when the flag is set.
"""


def chapter(key, icon, name, desc, reward, title, text, picture, options, alt=None):
    return {"key": key, "icon": icon, "name": name, "desc": desc, "reward": reward, "title": title, "text": text,
            "picture": picture, "options": options, "alt": alt}


# head focus id, focus id prefix, route flag, first event number, chapters.
STORY = [
    ("LR_ORL_duke", "LR_ORL_", "LR_route_orleans", 100, [
        chapter("cross_of_fire", "propaganda", "불의 십자단", "재향군인들이 왕의 깃발 아래 줄을 섭니다. 그들은 대가를 바라고 왔습니다.", {"war_support_factor": 0.02},
                "샹젤리제의 재향군인들", "라 로크 대령이 불의 십자단 대원 수만 명을 이끌고 샹젤리제를 행진합니다. 훈장을 단 노병들이 왕에게 경례하고, 대령은 궁으로 청구서를 보냅니다. 내각의 자리 셋입니다.", "fascist_gathering", [
                    ("자리를 내주어라. 그들은 왕의 주먹이다.", {"fascism_drift": 0.03, "political_power_gain": 0.03}),
                    ("대원은 군으로 받고, 대령은 훈장으로 돌려보내라.", {"army_org_factor": 0.02}),
                ]),
        chapter("generals_cabinet", "army_doctrines", "장군들의 내각", "재무부의 장부를 군인들이 읽기 시작합니다.", {"political_power_gain": 0.02},
                "베강과 재무장관", "베강 장군이 내년 군사 예산을 두 배로 요구했습니다. 재무장관은 그 숫자라면 프랑화가 겨울을 못 넘긴다며 사표를 내밀었습니다. 두 사람 모두 왕의 답을 기다립니다.", "military_planning", [
                    ("대포가 먼저다. 사표를 수리하라.", {"war_support_factor": 0.03, "stability_factor": -0.02}),
                    ("장군은 돈을 기다릴 줄도 알아야 한다.", {"political_power_gain": 0.03, "dev": 1}),
                ]),
        chapter("inspectors_out", "forceful_treaty", "감독관들과의 숨바꼭질", "배상 위원회의 감독관들이 왕의 창고 문을 두드립니다.", {"experience_gain_army_factor": 0.02},
                "창고 앞의 영국 소령", "르크뢰조의 창고 앞에 배상 위원회의 영국인 감독관이 서 있습니다. 문 안에는 배상 위원회 장부에 없는 야포 200문이 있습니다. 공장장은 어떻게 할지 묻는 전보를 보냈습니다.", "french_british_officers", [
                    ("감독관들을 국경 밖으로 내쫓아라. 이제 숨길 것도 없다.", {"war_support_factor": 0.03, "flag": "LR_st_orl_defiance"}),
                    ("차와 빈 창고를 내주어라. 대포는 더 깊이 숨겨라.", {"political_power_gain": 0.02}),
                ]),
        chapter("king_at_front", "military_sphere", "국경의 왕", "왕이 파리를 비우고 빼앗긴 땅이 보이는 언덕으로 갑니다.", {"army_morale_factor": 0.02},
                "벨포르의 연설", "왕이 벨포르 요새 위에서 라인강 쪽을 가리켰습니다. 지금 그는 어디로 가야 할지 고민하고 있습니다. 병사들의 막사인지, 아니면 파업 직전인 릴의 공장인지.", "king_speech", [
                    ("병사들과 같은 솥의 수프를 먹는다.", {"army_morale_factor": 0.03}),
                    ("릴의 용광로 앞에 선다. 전쟁은 공장에서 시작된다.", {"dev": 2, "industrial_capacity_factory": 0.02}),
                ]),
        chapter("colonels_plot", "intelligence_exchange", "대령들의 음모", "왕이 너무 느리다고 생각하는 젊은 장교들이 있습니다.", {"stability_factor": 0.02},
                "대령들의 음모", "왕실 보안 담당자가 명단을 가져왔습니다. 대령 열두 명이 왕이 전쟁을 미룬다며, 왕을 끌어내리지는 않되 왕의 손을 대신 움직이겠다고 모의했습니다. 명단에는 왕이 아끼는 이름도 있습니다.", "generic_read_write", [
                    ("모두 군법회의에 넘겨라. 왕의 군대에 주인은 하나다.", {"stability_factor": 0.04, "army_org_factor": -0.02}),
                    ("장군으로 진급시켜 전선으로 보내라. 그 열정을 쓰겠다.", {"army_morale_factor": 0.03, "stability_factor": -0.02, "war_support_factor": 0.02}),
                ]),
        chapter("day_of_revenge", "major_war", "복수의 날", "1918년에 멈춘 시계를 다시 돌립니다.", {"war_support_factor": 0.03},
                "복수의 날", "동원령 초안이 왕의 책상에 올라왔습니다. 조약은 아직 살아 있는 척하고, 유럽은 프랑스가 얌전히 무릎 꿇고 있다고 믿습니다. 오를레앙 왕조는 한 번의 기습에 모든 것을 걸게 될 것입니다.", "france_parade", [
                    ("숨긴 칼로 찌른다. 첫 달에 모든 것을 끝낸다.", {"planning_speed": 0.1, "war_support_factor": 0.05, "avoid": "LR_st_orl_defiance"}),
                    ("유럽은 이미 우리를 안다. 정면으로 행진하라.", {"war_support_factor": 0.08, "army_morale_factor": 0.03, "need": "LR_st_orl_defiance"}),
                ], ("LR_st_orl_defiance", "동원령 초안이 왕의 책상에 올라왔습니다. 감독관들을 내쫓은 날부터 유럽은 프랑스가 다시 올 것을 알고 있습니다. 기습은 없습니다. 런던과 빈의 신문은 벌써 전쟁을 말합니다.")),
    ]),
    ("LR_BOU_restored", "LR_BOU_", "LR_route_bourbon", 200, [
        chapter("lit_de_justice", "political_pressure", "친림 법정", "왕이 직접 법정에 앉아 칙령을 등록합니다. 앙시앵 레짐은 끝난 적이 없습니다.", {"political_power_gain": 0.02},
                "고등법원의 항명", "되살아난 파리 고등법원이 왕의 첫 칙령 등록을 거부했습니다. 법관들은 조상들처럼 왕에게 간언할 권리를 내세웁니다. 루이 20세는 전통을 지켰더니 전통이 물어뜯는 꼴이라며 웃지 않았습니다.", "generic_parliament", [
                    ("왕이 직접 법정에 앉는다. 등록하라.", {"political_power_gain": 0.03, "stability_factor": -0.01}),
                    ("법관들에게 작위와 연금을 약속한다.", {"stability_factor": 0.03}),
                ]),
        chapter("versailles_return", "national_unity", "베르사유 귀환", "왕궁의 창문을 다시 엽니다. 임대 중이던 박물관은 짐을 쌉니다.", {"stability_factor": 0.02},
                "거울의 방의 청구서", "베르사유 복원 예산이 올라왔습니다. 궁정 대신은 유럽의 왕들이 볼 왕궁을 말하고, 재무장관은 지붕이 새는 병원 수를 말합니다.", "king_speech", [
                    ("왕권은 보여야 존재한다. 궁을 빛내라.", {"political_power_gain": 0.03, "consumer_goods_factor": 0.01}),
                    ("왕궁은 절반만 쓴다. 나머지는 병원에 준다.", {"stability_factor": 0.03, "op": 1}),
                ]),
        chapter("jesuits_return", "improve_relations", "예수회의 귀환", "두 세기 전에 쫓겨난 신부들이 학교로 돌아오겠다고 청합니다.", {"stability_factor": 0.02},
                "왕관과 교실", "예수회가 프랑스의 중등 교육을 맡겠다고 청원했습니다. 받아들이면 시골의 충성은 한 세대 동안 보장됩니다. 그러나 왕립과학원 원장은 라틴어로 강철을 만들 수는 없다는 편지를 보내왔습니다.", "generic_read_write", [
                    ("왕관과 제단은 하나다. 학교를 맡겨라.", {"stability_factor": 0.04, "research_speed_factor": -0.01, "flag": "LR_st_bou_altar"}),
                    ("신부는 교회로, 교실은 왕립과학원으로.", {"research_speed_factor": 0.03}),
                ]),
        chapter("kings_bread", "construct_civilian", "왕의 빵", "빵값이 오르면 왕이 위험하다는 것을 부르봉 가문만큼 잘 아는 집안은 없습니다.", {"stability_factor": 0.02},
                "포부르 생탕투안의 겨울", "파리 동쪽 구역의 빵값이 두 배가 됐습니다. 여자들이 시청 앞에 모였습니다. 늙은 장관 하나가 왕에게 조용히 말합니다. 전하, 1789년도 빵으로 시작했습니다.", "generic_riot", [
                    ("왕실 곡물 창고를 열어라.", {"op": 1, "political_power_gain": -0.01, "stability_factor": 0.02}),
                    ("기병대를 보내라. 이번에는 진압에 성공한다.", {"war_support_factor": 0.02, "stability_factor": -0.02}),
                ]),
        chapter("madrid_letter", "major_alliance", "마드리드에서 온 편지", "스페인의 사촌이 왕실 혼인을 제안합니다.", {"political_power_gain": 0.02},
                "마드리드에서 온 편지", "스페인 왕가가 왕세자의 혼담을 보내왔습니다. 두 부르봉 왕가가 다시 합치면 피레네는 없는 산이 됩니다. 하지만 런던은 위트레흐트 조약을 기억하고 있습니다.", "generic_sign_treaty1", [
                    ("혼인을 받는다. 피레네는 이제 없다.", {"friend": "SPR", "war_support_factor": 0.02}),
                    ("정중히 사양한다. 프랑스의 왕은 프랑스만 다스린다.", {"stability_factor": 0.03, "friend": "ENG"}),
                ]),
        chapter("sun_king", "military_sphere", "태양왕의 후계", "루이 14세의 나라가 돌아왔는지, 왕 자신이 답합니다.", {"stability_factor": 0.03},
                "태양왕의 후계", "즉위 기념식에서 루이 20세가 어떤 왕으로 기억될지 선언합니다. 계몽 군주들의 편지를 읽은 왕은 신민보다 먼저 과학과 공장을 말합니다.", "france_parade", [
                    ("왕은 신의 뜻 아래 있다. 그리고 프랑스는 왕 아래 있다.", {"stability_factor": 0.06, "political_power_gain": 0.05, "need": "LR_st_bou_altar"}),
                    ("계몽 군주의 길을 간다. 짐은 국가의 첫째 공복이다.", {"research_speed_factor": 0.03, "industrial_capacity_factory": 0.03, "avoid": "LR_st_bou_altar"}),
                ], ("LR_st_bou_altar", "랭스의 성유가 왕의 이마에 다시 묻습니다. 예수회가 가르친 아이들이 거리에서 찬가를 부릅니다. 프랑스는 150년 전의 나라로, 그러나 더 견고하게 돌아왔습니다.")),
    ]),
    ("LR_COM_commune", "LR_COM_", "LR_route_communist", 300, [
        chapter("sections_congress", "propaganda", "48구역 대회", "1793년의 파리 48구역이 대표를 다시 보냅니다.", {"communism_drift": 0.02},
                "48구역 대회", "파리 48구역 대표들이 시청에 모였습니다. 공장 평의회가 모든 권력을 가져야 한다는 쪽과, 전쟁 앞에서는 중앙위원회가 필요하다는 쪽이 나흘째 싸웁니다. 의장의 종이 부서졌습니다.", "generic_communist_congress", [
                    ("모든 권력을 평의회로.", {"stability_factor": 0.03, "dev": 1}),
                    ("중앙위원회가 혁명을 지휘한다.", {"political_power_gain": 0.04}),
                ]),
        chapter("elected_officers", "army_doctrines", "장교 문제", "왕의 장교들을 어떻게 할지 정합니다.", {"army_morale_factor": 0.02},
                "견장을 떼어낸 대위", "한 연대가 병사 투표로 연대장을 뽑았습니다. 뽑힌 사람은 어제까지 취사병이었습니다. 옛 왕군 장교 수천 명은 집에서 소집장을 기다립니다. 전쟁을 아는 사람은 그들뿐입니다.", "generic_communist_militia", [
                    ("옛 장교를 쓰되, 곁에 정치위원을 붙여라.", {"army_org_factor": 0.03}),
                    ("모든 장교는 병사가 뽑는다.", {"army_morale_factor": 0.04}),
                ]),
        chapter("tribunal", "political_pressure", "혁명 재판소", "1793년에 끝내지 못한 재판을 다시 엽니다.", {"political_power_gain": 0.02},
                "혁명 재판소", "체포된 왕당파 귀족과 장군 400명이 콩시에르주리에 있습니다. 구역 대표들은 그들의 목을 요구합니다. 재판소장은 단두대가 아직 창고에 있다고 보고합니다. 150년 묵은 기름을 닦으면 쓸 수 있다고 합니다.", "generic_read_write", [
                    ("혁명은 두 번 실패하지 않는다. 단두대를 꺼내라.", {"op": 1, "stability_factor": -0.03, "political_power_gain": 0.03, "flag": "LR_st_com_terror"}),
                    ("추방하라. 코뮌은 그들과 다르다는 것을 보여라.", {"stability_factor": 0.04}),
                ]),
        chapter("bread_and_coal", "construct_mil_factory", "빵과 석탄", "왕들의 유럽이 코뮌을 봉쇄합니다.", {"industrial_capacity_factory": 0.02},
                "봉쇄의 겨울", "유럽의 왕국들이 금수를 선언했습니다. 공장은 석탄이 없어 멈추고, 도시는 빵이 없어 줄을 섭니다. 농민은 곡물을 내놓지 않습니다. 코뮌에게 땅을 받은 바로 그 농민들입니다.", "generic_strike", [
                    ("곡물을 징발한다. 공장이 먼저다.", {"mil": 2, "dev": 2, "stability_factor": -0.03}),
                    ("농민과의 약속이 혁명의 뿌리다. 시장을 허용한다.", {"stability_factor": 0.03, "communism_drift": -0.01}),
                ]),
        chapter("toulon_sailors", "navy_doctrines_tactics", "툴롱의 수병들", "혁명을 시작한 사람들이 혁명에게 묻습니다.", {"stability_factor": 0.02},
                "툴롱의 수병들", "툴롱의 수병들이 붉은 깃발을 든 채 코뮌에 요구안을 보냈습니다. 자유 선거, 언론 자유, 정치위원 폐지. 그들은 지난봄 가장 먼저 왕의 장교들을 바다에 던진 사람들입니다.", "sailors_in_working_rig", [
                    ("반혁명이다. 포를 돌려라.", {"war_support_factor": 0.03, "stability_factor": -0.02, "political_power_gain": 0.03}),
                    ("요구의 절반을 받는다. 동지들에게 총을 겨누지 않는다.", {"stability_factor": 0.04, "political_power_gain": -0.01}),
                ]),
        chapter("year_one", "national_unity", "혁명력 원년", "새 달력이 시청 벽에 걸립니다. 다시, 원년입니다.", {"communism_drift": 0.02},
                "혁명력 원년", "코뮌이 새 헌법과 새 달력을 선포합니다. 시청 앞 광장이 붉은 깃발로 찼습니다. 망명 귀족의 이름은 지워졌고, 사람들은 박수를 칩니다. 아무도 먼저 멈추려 하지 않습니다.", "french_liberation", [
                    ("공포는 정의의 다른 이름이다.", {"war_support_factor": 0.06, "political_power_gain": 0.05, "stability_factor": -0.02, "need": "LR_st_com_terror"}),
                    ("피 대신 학교로 세운 공화국이다.", {"stability_factor": 0.05, "research_speed_factor": 0.03, "avoid": "LR_st_com_terror"}),
                ], ("LR_st_com_terror", "코뮌이 새 헌법과 새 달력을 선포합니다. 콩코르드 광장의 단두대는 치워지지 않았습니다. 사람들은 박수를 치고, 옆사람이 얼마나 오래 치는지 곁눈질합니다.")),
    ]),
    ("LR_JAC_committee", "LR_JAC_", "LR_route_jacobin", 400, [
        chapter("matignon", "trade", "마티뇽 협상", "노조와 사장들이 총리 관저에서 마주 앉습니다.", {"stability_factor": 0.02},
                "마티뇽의 밤", "블룸 총리의 관저에서 노동총동맹과 사용자 단체가 밤새 협상합니다. 공장은 점거됐고 파업은 200만 명으로 불었습니다. 사장들은 임금 7%면 끝내자고 합니다. 노조는 15%를 말합니다.", "generic_strike", [
                    ("15%. 공화국은 어느 편인지 숨기지 않는다.", {"seats": 3, "stability_factor": 0.02}),
                    ("12%로 끝낸다. 공장이 다시 돌아야 한다.", {"dev": 2, "industrial_capacity_factory": 0.02}),
                ]),
        chapter("two_hundred", "political_pressure", "200가문", "중앙은행의 주주 200명이 국가를 가졌다고 사람들은 말합니다.", {"political_power_gain": 0.02},
                "금이 빠져나간다", "프랑스은행 금고에서 금이 빠져나가 제네바로 갑니다. 200가문의 답장입니다. 재무장관이 환율표를 들고 뛰어왔습니다. 자본 통제냐, 저 사람들과의 저녁 식사냐를 정해야 합니다.", "generic_stock_traders", [
                    ("국경에서 금 가방을 열어라.", {"political_power_gain": 0.03, "stability_factor": 0.01, "seats": 2}),
                    ("저녁을 먹는다. 공화국은 아직 돈이 필요하다.", {"consumer_goods_factor": -0.02}),
                ]),
        chapter("robespierre_portrait", "national_unity", "로베스피에르의 초상", "공안위원회의 이름을 쓴 이상, 그 이름의 무게도 물려받습니다.", {"stability_factor": 0.02},
                "로베스피에르의 초상", "의회 급진파가 공안위원회에 비상 권한을 달라는 법안을 냈습니다. 왕당파의 음모 앞에서 절차는 사치라고 합니다. 의사당 복도에 누군가 로베스피에르의 초상을 걸어 놓았습니다. 블룸은 그것을 오래 쳐다봅니다.", "generic_parliament", [
                    ("덕이 없는 공포는 재앙이고, 공포가 없는 덕은 무력하다.", {"political_power_gain": 0.04, "stability_factor": -0.02, "flag": "LR_st_jac_virtue"}),
                    ("초상을 내려라. 공화국은 법으로 싸운다.", {"seats": 4, "stability_factor": 0.03}),
                ]),
        chapter("pyrenees_refugees", "improve_relations", "피레네의 망명자들", "스페인 왕의 경찰을 피해 공화주의자들이 산을 넘어옵니다.", {"democratic_drift": 0.02},
                "피레네의 눈길", "페르피냥 국경 초소에 스페인 공화주의자 3천 명이 도착했습니다. 대부분 맨발입니다. 마드리드 대사는 범죄자 인도를 요구합니다. 프랑스 민중은 그들에게 빵을 건네고 있습니다.", "generic_read_write", [
                    ("모두 받는다. 공화국은 망명자의 조국이다.", {"war_support_factor": 0.03, "stability_factor": -0.01}),
                    ("수용소에 두고 마드리드와 협상한다.", {"stability_factor": 0.02, "friend": "SPR"}),
                ]),
        chapter("cagoule", "intelligence_exchange", "두건단", "왕당파 장교들의 비밀 결사가 공장을 폭파합니다.", {"stability_factor": 0.02},
                "두건단의 명단", "경찰이 무기고 다섯 곳과 명단 하나를 찾았습니다. 카굴, 두건단입니다. 파리 주둔 장교 40명의 이름이 있습니다. 전쟁부 장관은 이 사람들을 모두 자르면 군이 무너진다고 합니다.", "generic_read_write", [
                    ("전부 체포한다. 공화국의 군대에 왕당파는 없다.", {"op": 1, "army_org_factor": -0.02, "seats": 3}),
                    ("조용히 식민지로 전출시킨다.", {"army_org_factor": 0.02, "stability_factor": -0.01}),
                ]),
        chapter("fourteenth_july", "major_alliance", "7월 14일", "한 번도 공휴일이었던 적 없는 날이 국경일이 됩니다.", {"stability_factor": 0.03},
                "7월 14일", "1789년에 진압당한 바스티유의 봉기가 147년 만에 국경일이 됐습니다. 군악대는 처음으로 합법적으로 라 마르세예즈를 연주합니다. 총리가 연단에 올라 이 공화국이 무엇인지 말합니다.", "france_parade", [
                    ("덕의 공화국은 적을 용서하지 않는다.", {"war_support_factor": 0.06, "political_power_gain": 0.05, "need": "LR_st_jac_virtue"}),
                    ("이 공화국은 누구의 머리도 자르지 않고 여기까지 왔다.", {"stability_factor": 0.05, "seats": 5, "avoid": "LR_st_jac_virtue"}),
                ], ("LR_st_jac_virtue", "1789년에 진압당한 바스티유의 봉기가 147년 만에 국경일이 됐습니다. 비상 권한은 아직 끝나지 않았습니다. 연단 뒤에 로베스피에르의 초상이 걸려 있고, 이제 아무도 그것을 이상하게 여기지 않습니다.")),
    ]),
    ("LR_GIR_cabinet", "LR_GIR_", "LR_route_girondin", 500, [
        chapter("bordeaux_congress", "positive_trade_relations", "보르도 대회", "지롱드의 고향에서 상공인들이 내각에 조건을 내겁니다.", {"political_power_gain": 0.02},
                "보르도 대회", "보르도 상공회의소에 전국의 선주와 공장주가 모였습니다. 그들이 선거 자금을 댔고, 이제 대가를 말합니다. 법인세 인하 아니면 지방 의회 권한 확대입니다. 둘 다는 안 된다고 재무장관이 잘랐습니다.", "generic_conference", [
                    ("세금을 내린다. 돈은 공장으로 돌아올 것이다.", {"dev": 2, "industrial_capacity_factory": 0.02}),
                    ("지방 의회에 권한을 준다. 표는 고향에서 나온다.", {"seats": 4, "stability_factor": 0.01}),
                ]),
        chapter("paris_question", "political_pressure", "파리 문제", "파리는 혁명을 세 번 망쳤다고 지롱드는 믿습니다.", {"stability_factor": 0.02},
                "파리 문제", "1793년 지롱드파를 단두대로 보낸 것은 파리 민중이었습니다. 내각 안에서 파리의 자치권을 지방 수준으로 깎자는 안이 나왔습니다. 파리 시장은 시청 발코니에서 해볼 테면 해보라고 외쳤습니다.", "gathering_protest", [
                    ("파리도 83개 데파르트망 가운데 하나일 뿐이다.", {"political_power_gain": 0.03, "stability_factor": -0.02}),
                    ("수도에 특별 예산을 준다. 복수는 정책이 아니다.", {"op": 1, "stability_factor": 0.02}),
                ]),
        chapter("atlantic_company", "trade", "대서양 회사", "선주들이 칙허 회사를 세우자고 합니다. 이름은 네덜란드에서 빌렸습니다.", {"consumer_goods_factor": -0.01},
                "대서양 회사", "보르도와 낭트의 선주들이 식민지 무역 독점권을 가진 대서양 회사를 제안합니다. 네덜란드 공화국이 그렇게 부자가 됐습니다. 대신 회사의 이사가 각료 회의에 앉겠다고 합니다.", "generic_stock_traders", [
                    ("이사회에 의자를 내준다. 상인이 곧 공화국이다.", {"political_power_gain": 0.03, "industrial_capacity_factory": 0.03, "stability_factor": -0.02, "flag": "LR_st_gir_company"}),
                    ("돈은 환영이지만 의자는 없다.", {"stability_factor": 0.03}),
                ]),
        chapter("bourse_panic", "construct_civ_factory", "증권가의 공황", "자유 시장에도 겨울은 옵니다.", {"industrial_capacity_factory": 0.02},
                "브롱니아르 궁의 비명", "파리 증권거래소의 철강주가 하루에 40% 빠졌습니다. 은행 두 곳이 문을 닫았습니다. 내각의 경제학자는 시장이 스스로 고칠 것이라 하고, 문 앞의 예금자들은 그의 집 주소를 묻습니다.", "generic_stock_traders", [
                    ("은행을 구한다. 이번 한 번뿐이다.", {"stability_factor": 0.04, "political_power_gain": -0.01}),
                    ("시장에 맡긴다. 살아남은 회사가 더 강해진다.", {"dev": 2, "stability_factor": -0.03, "industrial_capacity_factory": 0.02}),
                ]),
        chapter("federal_draft", "national_unity", "연방 헌법 초안", "1793년에 쓰다 만 지롱드 헌법을 금고에서 꺼냅니다.", {"stability_factor": 0.02},
                "콩도르세의 금고", "콩도르세의 지롱드 헌법 초안이 국립문서고에서 나왔습니다. 데파르트망마다 자기 의회와 자기 예산을 갖는 연방입니다. 지방 의원들은 환호하고, 참모본부는 전시에 누가 명령하느냐고 묻습니다.", "generic_read_write", [
                    ("채택한다. 143년 늦은 약속이다.", {"seats": 5, "stability_factor": 0.02, "war_support_factor": -0.02}),
                    ("전쟁이 끝날 때까지 금고에 둔다.", {"war_support_factor": 0.02, "political_power_gain": 0.02}),
                ]),
        chapter("merchant_republic", "major_alliance", "상인들의 공화국", "프랑스의 다음 세기를 누가 쓸지 답합니다.", {"political_power_gain": 0.03},
                "상인들의 공화국", "대서양 항구들이 다시 붐빕니다. 총리는 보르도 부두에서 연설합니다. 왕이 없는 프랑스가 전쟁 없이도 부유할 수 있음을 보여 주겠다고 합니다. 부두 노동자들은 조용히 듣습니다.", "generic_conference", [
                    ("이 나라는 이제 하나의 큰 회사다.", {"political_power_gain": 0.06, "consumer_goods_factor": -0.03, "need": "LR_st_gir_company"}),
                    ("상인의 자유와 시민의 권리는 함께 간다.", {"stability_factor": 0.05, "democratic_drift": 0.03, "avoid": "LR_st_gir_company"}),
                ], ("LR_st_gir_company", "대서양 회사의 깃발이 공화국의 깃발보다 높이 걸린 항구가 늘었습니다. 총리는 보르도 부두에서 연설하고, 연설문은 회사 이사회가 먼저 읽었습니다. 배당금은 사상 최고입니다.")),
    ]),
    ("LR_MAR_cabinet", "LR_MAR_", "LR_route_marais", 600, [
        chapter("notables", "political_pressure", "명사 회의", "재산과 이름이 있는 사람들이 나라의 앞날을 논합니다.", {"stability_factor": 0.02},
                "명사 회의", "푀양파 내각이 전국의 명사를 파리로 불렀습니다. 지방 지주와 옛 귀족은 선거구 조정을, 도시 은행가들은 공업 차관을 원합니다. 내각에게는 줄 것이 하나뿐입니다.", "generic_conference", [
                    ("지방 명사를 택한다. 프랑스는 아직 시골이다.", {"seats": 4}),
                    ("은행가를 택한다. 내일의 프랑스는 도시다.", {"dev": 2, "industrial_capacity_factory": 0.02}),
                ]),
        chapter("lafayette_heir", "military_sphere", "라파예트의 후계자", "국민방위대가 다시 제복을 맞춥니다. 사령관이 누구냐가 문제입니다.", {"stability_factor": 0.02},
                "흰 깃털의 사령관", "국민방위대 사령관 후보로 라파예트의 후손이 나섰습니다. 시민들은 흰 깃털을 좋아합니다. 그러나 전쟁부는 정규군 밖에 무장 세력이 생기는 것을 싫어하고, 왕당파는 그 이름 자체를 싫어합니다.", "soldiers_marching", [
                    ("방위대는 시민의 것이다. 임명한다.", {"stability_factor": 0.03, "conscription_factor": 0.01}),
                    ("전쟁부 아래 둔다.", {"army_org_factor": 0.02}),
                ]),
        chapter("empty_throne", "national_unity", "빈 왕좌", "헌법은 왕을 요구하는데 왕좌는 비어 있습니다. 후보를 고릅니다.", {"political_power_gain": 0.02},
                "빈 왕좌", "헌법은 완성됐고 왕좌는 비어 있습니다. 파리 백작은 프랑스어로 연설할 줄 알지만 그의 가문은 믿을 수 없습니다. 스페인에서 온 부르봉의 작은 왕자는 믿을 만하지만 프랑스어 연설을 연습 중입니다.", "king_speech", [
                    ("파리 백작을 부른다. 프랑스의 왕은 프랑스인이어야 한다.", {"stability_factor": 0.03, "flag": "LR_st_mar_paris"}),
                    ("부르봉 왕자를 부른다. 유럽의 왕실이 우리를 인정할 것이다.", {"friend": "SPR", "political_power_gain": 0.03}),
                ]),
        chapter("civil_list", "trade", "왕실비 논쟁", "왕에게 얼마를 줄지 의회가 정합니다. 그 사실 자체가 혁명입니다.", {"political_power_gain": 0.02},
                "왕실비 논쟁", "의회가 왕실 예산안을 심의합니다. 야당은 왕 한 명의 연봉이 초등학교 400곳이라고 계산했습니다. 궁정은 영국 왕보다 적게 받을 수 없다고 합니다. 왕이 의회의 예산안을 기다린다는 점만은 모두 동의합니다.", "generic_parliament", [
                    ("왕의 위엄에 값을 매길 수 없다. 넉넉히 준다.", {"political_power_gain": 0.03, "seats": -2}),
                    ("왕이 스스로 삭감을 제안하게 한다.", {"stability_factor": 0.03, "seats": 3}),
                ]),
        chapter("lyon_strike", "construct_civilian", "리옹의 견직공", "1831년의 깃발이 리옹에 다시 걸립니다.", {"stability_factor": 0.02},
                "리옹의 견직공", "리옹 견직공들이 다시 검은 깃발을 들었습니다. 일하며 살거나 싸우며 죽겠다는 100년 전의 구호입니다. 지방 지사는 군대를 요청하고, 산악파 의원들은 의사당에서 이름을 부릅니다.", "generic_strike", [
                    ("법은 법이다. 방위대를 보낸다.", {"op": 1, "seats": -2}),
                    ("최저 공임법을 낸다. 왕당파가 뭐라 하든.", {"seats": 3, "stability_factor": 0.02, "dev": 1}),
                ]),
        chapter("charter", "major_alliance", "1791년의 약속", "한 번 찢어졌던 헌법 위에 왕이 손을 얹습니다.", {"stability_factor": 0.03},
                "1791년의 약속", "145년 전 찢어진 헌법 초안이 다시 낭독됩니다. 왕은 의사당에 들어와 의장보다 낮은 자리에 앉습니다. 이것이 영국인이 말하는 그 정치인지, 프랑스식 무언가인지 아직 아무도 모릅니다.", "generic_parliament", [
                    ("왕은 프랑스 사람이고, 헌법은 왕보다 위에 있다.", {"stability_factor": 0.07, "democratic_drift": 0.02, "need": "LR_st_mar_paris"}),
                    ("부르봉의 피와 공화국의 법. 유럽이 처음 보는 왕국이다.", {"political_power_gain": 0.06, "stability_factor": 0.03, "avoid": "LR_st_mar_paris"}),
                ], ("LR_st_mar_paris", "145년 전 찢어진 헌법 초안이 다시 낭독됩니다. 파리 백작은 의사당에 들어와 의장보다 낮은 자리에 앉습니다. 그의 프랑스어 연설은 완벽했고, 빈정거리던 의원들도 박수를 칩니다.")),
    ]),
    ("LR_NAP_first_consul", "LR_NAP_", "LR_route_napoleon", 700, [
        chapter("algiers_return", "military_sphere", "알제에서 돌아온 사람", "아무나 보내라던 그 아무나가 파리에 도착합니다.", {"war_support_factor": 0.02},
                "오랑주리의 군화", "보나파르트 장군이 척탄병을 이끌고 의회가 피신한 오랑주리에 들어왔습니다. 코르시카 억양으로 몇 마디 하다 말을 더듬었고, 의원들은 야유했습니다. 그의 동생이 그를 구했습니다. 지금 의원들은 창밖으로 뛰어내리는 중입니다.", "soldiers_marching", [
                    ("의원들을 체포한다.", {"political_power_gain": 0.04, "stability_factor": -0.02}),
                    ("남은 의원들에게 헌법 초안을 맡긴다. 쓰는 사람은 내가 고른다.", {"stability_factor": 0.03}),
                ]),
        chapter("plebiscite", "propaganda", "국민투표", "통령 정부에 찬성하느냐고 나라에 묻습니다.", {"political_power_gain": 0.02},
                "개표소의 동생", "국민투표 결과가 내무부에 도착했습니다. 찬성 150만 표입니다. 내무장관인 동생이 숫자를 들여다보더니 군인들 표가 빠졌다며 펜을 들었습니다. 그가 쓰려는 숫자는 300만입니다.", "election_vote", [
                    ("쓰게 둔다. 대승이어야 유럽이 믿는다.", {"political_power_gain": 0.04, "war_support_factor": 0.02}),
                    ("펜을 빼앗는다. 150만은 정직한 숫자다.", {"stability_factor": 0.04, "democratic_drift": 0.02}),
                ]),
        chapter("before_the_crown", "national_unity", "왕관 앞에서", "법전과 정교 협약이 끝나면 원로원이 물을 것입니다. 그다음은 무엇이냐고.", {"stability_factor": 0.02},
                "왕관 앞에서", "원로원 대표단이 말메종을 찾아왔습니다. 공화국을 지키려면 세습이 필요하다고, 그들은 왕관이라는 단어만 빼고 말합니다. 통령은 대답하지 않고 대서양 지도를 봅니다. 이제 곧 대답해야 합니다.", "generic_conference", [
                    ("근위대 장교들과 저녁을 먹는다.", {"army_morale_factor": 0.03, "war_support_factor": 0.02}),
                    ("법률가들과 저녁을 먹는다.", {"stability_factor": 0.03, "political_power_gain": 0.02}),
                ]),
    ]),
    ("LR_NAP_coronation", "LR_NAP_", "LR_route_empire", 800, [
        chapter("eagles", "military_sphere", "독수리 군기", "로마의 독수리가 프랑스 연대 앞에 섭니다.", {"army_morale_factor": 0.02},
                "독수리 군기", "샹드마르스에서 황제가 연대에 금빛 독수리를 나눠 줍니다. 전쟁부는 이 금으로 전차 몇 대를 살 수 있는지 계산한 메모를 보내왔습니다. 황제는 그 메모를 읽었습니다.", "france_parade", [
                    ("병사는 금속이 아니라 깃발을 위해 죽는다.", {"army_morale_factor": 0.03, "war_support_factor": 0.02}),
                    ("독수리는 나무로 깎고, 금은 공장으로 보내라.", {"dev": 2, "mil": 1}),
                ]),
        chapter("new_nobles", "political_pressure", "오랜 이름, 새 이름", "제국 궁정에 누구를 앉힐지 정합니다.", {"political_power_gain": 0.02},
                "황제의 응접실", "튈르리 응접실에 생제르맹의 옛 귀족 후작 부인이 들어옵니다. 그 옆에는 어제 공작이 된 포병 장군의 아내가 있습니다. 후작 부인은 공작 부인에게 인사하지 않습니다. 궁정 대신이 황제의 지시를 기다립니다.", "generic_read_write", [
                    ("옛 가문을 부른다. 그들의 인사가 곧 유럽의 인정이다.", {"stability_factor": 0.03, "army_morale_factor": -0.01}),
                    ("내 공작들이 프랑스의 귀족이다. 후작 부인은 나가시오.", {"army_morale_factor": 0.03}),
                ]),
        chapter("empress", "major_alliance", "황후 문제", "제국에는 후계자가 필요합니다. 황제의 침실은 외교 문제가 됩니다.", {"stability_factor": 0.02},
                "황후 문제", "빈에서 조용한 제안이 왔습니다. 합스부르크의 대공녀입니다. 받아들이면 황제는 유럽 왕실의 사위가 됩니다. 원수들은 굴욕이라 하고, 튈르리에는 그와 알제 시절부터 함께한 부인이 아직 살고 있습니다.", "king_speech", [
                    ("합스부르크의 사위가 된다.", {"political_power_gain": 0.04, "friend": "AUS", "stability_factor": -0.01, "flag": "LR_st_emp_habsburg"}),
                    ("내 황후는 이미 여기 있다.", {"stability_factor": 0.03, "war_support_factor": 0.02}),
                ]),
        chapter("spanish_ulcer", "forceful_treaty", "스페인의 궤양", "황제의 형은 왕이 되고 싶어 합니다. 마드리드는 벌써 불길합니다.", {"war_support_factor": 0.02},
                "마드리드의 빈자리", "스페인 왕위 계승 분쟁이 터졌습니다. 황제의 형이 마드리드를 원합니다. 탈레랑의 후계자를 자처하는 외무장관이 이렇게 씁니다. 전하, 스페인은 들어가기는 쉬워도 나오기는 어려운 나라입니다.", "generic_sign_treaty1", [
                    ("형을 왕으로 앉힌다.", {"war_support_factor": 0.03, "stability_factor": -0.02, "political_power_gain": 0.02}),
                    ("외무장관 말을 듣는다. 이번만이다.", {"stability_factor": 0.03}),
                ]),
        chapter("emperor_of_europe", "major_war", "유럽의 황제", "모든 왕이 황제의 전갈을 기다리는 날을 꿈꿉니다.", {"war_support_factor": 0.03},
                "유럽의 황제", "제국 궁정에 유럽 지도가 펼쳐졌습니다. 황제가 말합니다. 빈과 런던과 상트페테르부르크, 누구든 이 지도를 함께 그릴 수 있다고. 거부하는 자는 그 지도 위에서 지워진다고.", "france_parade", [
                    ("왕들의 사위로서, 왕들을 다스린다.", {"political_power_gain": 0.08, "stability_factor": 0.03, "need": "LR_st_emp_habsburg"}),
                    ("코르시카 포병 장교가 왕들의 유럽을 끝낸다.", {"war_support_factor": 0.08, "army_morale_factor": 0.03, "avoid": "LR_st_emp_habsburg"}),
                ], ("LR_st_emp_habsburg", "새 황후가 쓴 프랑스어 편지가 빈으로 갑니다. 왕실 연감에 황제의 이름이 처음으로 실렸습니다. 원수들의 얼굴은 어둡고, 왕들은 그의 잔을 받습니다. 유럽 지도가 궁정에 펼쳐졌습니다.")),
    ]),
    ("LR_NAP_guardian", "LR_GUA_", "LR_route_guardian", 900, [
        chapter("first_address", "propaganda", "첫 국정 연설", "대통령이 의회에 처음으로 군복을 입지 않고 들어갑니다.", {"stability_factor": 0.02},
                "연미복의 장군", "대통령이 처음으로 연미복을 입고 연단에 섭니다. 옷이 어색합니다. 의원들은 그가 헌법을 말할지 군대를 말할지 기다립니다. 초고는 두 개입니다.", "generic_parliament", [
                    ("헌법을 말한다.", {"seats": 3, "democratic_drift": 0.02}),
                    ("군대 개혁을 말한다. 공화국은 무장해야 산다.", {"war_support_factor": 0.02}),
                ]),
        chapter("marshals_protest", "army_doctrines", "장군들의 항의", "왕관을 거절한 황제를 군은 이해하지 못합니다.", {"army_org_factor": 0.02},
                "그가 왜 거절했는가", "알제부터 함께 온 장군들이 관저로 찾아왔습니다. 저희가 왜 피를 흘렸습니까. 그들은 민간인 전쟁부 장관 앞에서 경례하기 싫다고 합니다. 대통령은 그들의 이름을 모두 외우고 있습니다.", "military_planning", [
                    ("옛 동료를 해임한다. 문민 통제는 나부터다.", {"stability_factor": 0.04, "army_morale_factor": -0.01}),
                    ("술을 마시며 설득한다. 그들이 없으면 군도 없다.", {"army_morale_factor": 0.03}),
                ]),
        chapter("life_presidency", "political_pressure", "종신 대통령 청원", "지지자들이 임기를 없애자는 청원서를 가져옵니다.", {"political_power_gain": 0.02},
                "400만 명의 서명", "시민 400만 명이 종신 대통령을 청원했습니다. 서명 일부는 진짜입니다. 대통령은 왕관을 거절했지만, 지금 이것은 왕관이 아니라고 측근들이 말합니다. 공화국의 이름 그대로입니다.", "election_vote", [
                    ("청원서를 불태운다. 임기는 헌법에 적혀 있다.", {"stability_factor": 0.04, "democratic_drift": 0.03, "flag": "LR_st_gua_term"}),
                    ("대답하지 않는다. 언제가 될지는 내가 정한다.", {"political_power_gain": 0.05}),
                ]),
        chapter("exiles_return", "improve_relations", "망명 왕족의 귀환", "대통령이 왕족의 귀국을 허락할지 정합니다.", {"stability_factor": 0.02},
                "런던에서 온 편지", "런던의 부르봉 왕족과 오를레앙 왕족이 시민으로 돌아가고 싶다고 편지를 보냈습니다. 코뮌파는 그 편지를 태우라 하고, 왕당파는 왕의 귀환으로 환영합니다. 대통령은 그 왕족의 이름들을 소리 내어 읽어 봅니다.", "generic_read_write", [
                    ("시민 자격으로 돌아오게 한다.", {"op": 1, "seats": 2}),
                    ("국경은 닫혀 있다. 공화국은 아직 어리다.", {"war_support_factor": 0.02, "stability_factor": 0.01}),
                ]),
        chapter("farewell", "national_unity", "대통령의 약속", "언젠가 이 사람도 관저를 나와야 합니다. 그 날의 약속을 합니다.", {"stability_factor": 0.03},
                "대통령의 약속", "대통령이 앵발리드 앞에서 연설합니다. 왕관을 쓰지 않았다는 것이 그의 가장 큰 승리인지, 가장 큰 실수인지 역사가 말할 것입니다. 병사와 의원들이 함께 듣고 있습니다.", "france_parade", [
                    ("임기가 끝나면 나는 코르시카로 간다.", {"stability_factor": 0.08, "seats": 5, "need": "LR_st_gua_term"}),
                    ("공화국이 나를 필요로 하는 한 나는 여기 있다.", {"political_power_gain": 0.08, "war_support_factor": 0.03, "avoid": "LR_st_gua_term"}),
                ], ("LR_st_gua_term", "청원서가 타버린 재 위에서 대통령이 앵발리드 앞에 섭니다. 다음 선거일이 달력에 적혀 있습니다. 장군 출신 대통령이 스스로 물러나겠다는 약속을 유럽의 왕들은 믿지 않습니다.")),
    ]),
]
