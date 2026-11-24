"""Economy, army, navy and air branches for every American tree (2026-11-25): america_focus.py calls development()
once per tree, to the right of its story branches. The four roots carry each regime's own name and story; the focuses
under them are shared, written so they fit any of the five Americas.
"""

# tree prefix -> {branch: (name, description)} for the four roots.
ROOTS = {
    "LR_USA_": {
        "economy": ("식민지 전시 경제",
                    "런던은 식민지 공장이 늘어나는 것을 늘 꺼려 왔지만, 다음 전쟁에서 본토 공장만으로 버틸 수 없다는 계산이 마침내 그 두려움을 눌렀습니다. "
                    "총독부 안에 전시 산업국이 생기고, 국장 자리에는 디트로이트의 자동차 회사 사장이 앉습니다."),
        "army": ("왕립 식민지군",
                 "대전쟁에서 돌아온 식민지 연대들은 영국군 장교 밑에서 싸웠고, 그 장교들 밑에서 승진이 막혔습니다. "
                 "총독부는 처음으로 식민지 출신에게 대령 계급장을 달아 주고, 그들의 연대를 따로 묶어 왕립 식민지군이라 부르기로 합니다."),
        "navy": ("북대서양 분함대",
                 "본국 함대가 대서양을 건너오는 데는 열흘이 걸립니다. 해군성은 그 열흘을 메울 함대를 식민지 항구에 두기로 했고, "
                 "노퍽과 보스턴의 선거에 해군성 감독관들이 짐을 풉니다."),
        "air": ("식민지 항공대",
                "영국 공군은 식민지에 비행장을 내주면서도 조종사는 본토에서 데려왔습니다. 오하이오의 비행 학교를 졸업한 청년들이 "
                "정비병으로만 일한다는 불만이 신문에 실린 뒤에야 총독부는 식민지 항공대 창설안을 런던에 올립니다."),
    },
    "LR_CNA_": {
        "economy": ("연방 전시 경제",
                    "독립은 선언으로 끝나지 않았습니다. 영국의 금수 조치가 대서양 항로를 막자 공화국은 지금껏 리버풀에서 사 오던 물건을 스스로 만들어야 했고, "
                    "재무부는 공장주들을 필라델피아로 불러 전시 생산 계약서를 내밉니다."),
        "army": ("대륙군 재건",
                 "1776년의 대륙군은 농부와 사냥꾼으로 영국 정규군을 이겼다고 교과서는 가르칩니다. 지금의 참모들은 그 교과서를 덮어 두고, "
                 "철도와 무전기로 움직이는 군대의 편제표를 새로 그립니다."),
        "navy": ("연방 해군 위원회",
                 "영국 해군이 마음만 먹으면 공화국의 항구는 한 주 안에 모두 막힙니다. 의회는 그 사실을 알고도 오랫동안 해군 예산을 깎았지만, "
                 "금수 조치가 시작된 뒤로는 해군 위원회 청문회가 가장 붐비는 자리가 되었습니다."),
        "air": ("대륙 항공대",
                "데이턴의 자전거 가게에서 비행기가 처음 떴다는 것은 이 나라 사람들이 자랑으로 여기는 일입니다. 그러나 그 비행기를 군대로 만드는 일에는 "
                "아직 아무도 손을 대지 않았고, 육군 항공과의 젊은 장교들이 의회 복도에서 의원들을 붙잡습니다."),
    },
    "LR_AMC_": {
        "economy": ("인민 경제 위원회",
                    "공장을 노동자의 손에 넘기는 일은 혁명의 첫날에 끝났지만, 그 공장을 다시 돌리는 일은 그렇게 빨리 끝나지 않습니다. "
                    "평의회는 공장 위원회 대표들을 디트로이트에 모아 전쟁에 필요한 물자의 목록과 계획을 함께 짭니다."),
        "army": ("적군 참모부",
                 "적위대는 파업 현장에서는 강했지만 들판에서 정규군을 만나면 흩어졌습니다. 평의회는 옛 군대의 장교들 가운데 혁명 편에 선 사람들을 불러 모으고, "
                 "그들 곁에 정치 위원을 하나씩 붙여 참모부를 세웁니다."),
        "navy": ("적색 함대",
                 "오대호의 화물선 선원들과 대서양 항구의 부두 노동자들은 혁명에 가장 먼저 가담한 사람들이었습니다. 평의회는 그들이 지킨 배들을 모아 "
                 "함대라 부르기로 했지만, 그 배들 가운데 포를 단 것은 아직 몇 척 되지 않습니다."),
        "air": ("인민 항공대",
                "비행기 공장의 노동자들은 자기들이 만든 비행기를 몰고 싶어 했고, 평의회는 그 바람을 막을 이유를 찾지 못했습니다. "
                "공장마다 비행 동호회가 생기고, 그 동호회가 인민 항공대의 첫 비행 대대가 됩니다."),
    },
    "LR_LNG_": {
        "economy": ("부의 공유 경제",
                    "롱은 연설할 때마다 모든 사람이 왕이 될 수 있다고 외쳤고, 사람들은 그 말을 믿고 그를 따랐습니다. "
                    "이제 그 약속을 지킬 차례가 왔는데, 나누어 줄 부를 만들려면 먼저 공장이 돌아가야 합니다."),
        "army": ("프레리 방위군",
                 "중서부의 주 방위군은 롱이 주지사들과 손잡던 날부터 그의 군대가 되었습니다. 트럭에 기관총을 얹고 평원을 달리던 그 부대들에 "
                 "제대로 된 편제와 계급을 주는 일이 남아 있습니다."),
        "navy": ("미시시피 함대",
                 "중서부에는 바다가 없지만 강은 있습니다. 미시시피와 오하이오를 오르내리는 바지선과 증기선에 포를 달면 강 연안의 도시들을 지킬 수 있고, "
                 "멕시코만으로 나가는 길도 열 수 있습니다."),
        "air": ("킹피시 항공대",
                "롱은 비행기를 타고 유세를 다니길 즐겼습니다. 유세용 비행기를 몰던 조종사들이 이제 군복을 입고, 롱의 별명을 딴 항공대가 "
                "캔자스의 밀밭 한가운데에 비행장을 닦습니다."),
    },
    "LR_DXE_": {
        "economy": ("목화 전시 경제",
                    "남부의 부는 늘 목화에서 나왔고, 목화는 늘 바다 건너로 팔려 나갔습니다. 전쟁으로 그 길이 막히자 농장주 의회는 처음으로 "
                    "목화밭 옆에 공장을 세우는 법안을 통과시킵니다."),
        "army": ("남부 회색군",
                 "남부의 청년들은 할아버지들이 입었던 회색 군복을 다시 꺼내 입었습니다. 그러나 할아버지들의 전쟁은 머스킷 총으로 치렀고, "
                 "이번 전쟁에서 이기려면 그 군복 아래의 모든 것을 바꿔야 합니다."),
        "navy": ("만 연안 함대",
                 "모빌과 뉴올리언스, 갤버스턴의 항구는 남부가 바다로 나가는 문입니다. 의회는 그 문을 지킬 함대를 꾸리기로 하고, "
                 "멕시코만의 어선과 화물선을 징발해 첫 전대를 만듭니다."),
        "air": ("남부 항공대",
                "앨라배마와 조지아의 넓은 들판은 비행장을 닦기에 좋은 땅입니다. 대전쟁에서 프랑스 하늘을 날았던 남부 출신 조종사들이 "
                "고향으로 돌아와 후배들을 가르치기 시작합니다."),
    },
}

# branch -> [(suffix, icon, name, description, effects-key)]: the four focuses under each root, shared by every tree.
SHARED = {
    "economy": [
        ("machine_tools", "production", "공작기계 표준화",
         "공장마다 다른 규격의 나사와 볼트를 쓰는 바람에, 한 공장에서 만든 부품이 다른 공장의 기계에 맞지 않는 일이 흔합니다. "
         "규격을 하나로 맞추는 데는 여섯 달이 걸리지만, 그 뒤로는 어느 공장에서 만든 부품이든 전선의 어느 기계에나 들어갑니다."),
        ("power_grid", "construct_infrastructure", "전국 송전망",
         "강가의 수력 발전소에서 만든 전기가 도시 하나를 넘어가지 못하고 버려지고 있습니다. 송전탑을 이어 발전소와 공업 지대를 하나의 망으로 묶으면, "
         "밤에도 불을 끄지 않는 공장을 세울 수 있습니다."),
        ("synthetic_fuel", "oil_refinery", "합성 연료 공장",
         "석유는 남쪽 유전에서 나오고, 그 유전으로 가는 철도는 전쟁이 나면 가장 먼저 끊깁니다. 화학자들은 석탄에서 휘발유를 뽑아내는 공정을 보여 주며, "
         "값은 비싸도 적이 끊을 수 없는 연료라는 점을 강조합니다."),
        ("war_production", "construct_mil_factory", "민수에서 군수로",
         "자동차 공장의 조립 라인은 하루면 트럭 공장이 되고, 한 달이면 전차 공장이 됩니다. 정부는 공장주들에게 전쟁이 끝나면 라인을 돌려주겠다고 약속하고, "
         "그 약속을 문서로 남겨 달라는 요구에 순순히 서명합니다."),
    ],
    "army": [
        ("rifles", "small_arms", "보병 화기 개량",
         "병사들이 들고 있는 소총은 대전쟁 때 만든 것이고, 그 가운데 상당수는 그때 쓰던 것을 그대로 물려받은 것입니다. "
         "병기국은 반자동 소총과 경기관총의 시험 사격을 끝내고 생산 계약을 맺습니다."),
        ("artillery", "army_artillery", "야포 표준화",
         "포병대가 쓰는 대포의 구경만 일곱 가지라 탄약 보급이 늘 엉킵니다. 참모부는 구경을 세 가지로 줄이고, 그 세 가지를 트럭으로 끌 수 있는 포가로 바꾸기로 합니다."),
        ("tanks", "build_tank", "기갑 부대",
         "대전쟁의 전차는 참호를 넘는 기계였지만, 지금 유럽에서 만드는 전차는 참호 뒤까지 달려가는 기계입니다. 기병 장교 몇이 말을 내리고 "
         "시험용 전차 중대를 맡겠다고 자원합니다."),
        ("mobile_doctrine", "army_motorized", "기동전 교리",
         "이 대륙은 유럽보다 훨씬 넓고, 넓은 땅에서는 먼저 도착하는 쪽이 이깁니다. 참모 대학의 교관들은 보병을 트럭에 태우고 전차와 함께 움직이는 훈련을 "
         "교과 과정에 넣습니다."),
    ],
    "navy": [
        ("destroyers", "navy_anti_submarine", "구축함 계획",
         "상선을 지키는 데는 전함보다 구축함이 쓸모 있습니다. 해군은 같은 설계로 구축함을 여러 척 한꺼번에 찍어 내는 계획을 세우고, "
         "조선소마다 같은 도면을 보냅니다."),
        ("submarines", "navy_submarine", "잠수함대",
         "적의 함대가 더 크다면 그 함대가 지키는 상선을 노리면 됩니다. 잠수함 승조원 학교가 문을 열고, 첫 기수의 절반은 상선 선원 출신으로 채워집니다."),
        ("capital_ships", "navy_battleship", "주력함 건조",
         "바다를 지배하는 것은 여전히 큰 함포를 단 배라고 제독들은 믿습니다. 의회는 오랜 논쟁 끝에 주력함 건조 예산을 통과시키고, "
         "가장 큰 선거에서 용골을 놓는 기공식이 열립니다."),
        ("fleet_doctrine", "navy_doctrines_tactics", "해군 교리",
         "배를 만드는 것보다 그 배들을 함께 움직이는 법을 익히는 데 더 오래 걸립니다. 해군 대학은 해마다 대규모 기동 연습을 열고, "
         "그 결과를 바탕으로 함대 교범을 새로 씁니다."),
    ],
    "air": [
        ("fighters", "air_fighter", "전투기 개발",
         "복엽기의 시대는 끝났습니다. 설계국은 금속 동체에 접이식 바퀴를 단 단엽 전투기의 시제기를 내놓고, 시험 비행에서 시속 사백 킬로미터를 넘깁니다."),
        ("bombers", "air_bomber", "폭격기 개발",
         "전선 너머의 철도와 다리를 부술 수 있다면 적의 군대는 굶습니다. 항공대는 쌍발 폭격기의 설계 공모를 열고, 세 회사가 시제기를 내놓습니다."),
        ("aircraft_plants", "air_production", "항공기 공장",
         "비행기 한 대를 만드는 데 걸리는 시간을 줄이려면 자동차처럼 조립 라인에서 만들어야 합니다. 정부는 자동차 회사들에 항공기 생산을 맡기고, "
         "공장 옆에 비행장을 붙여 짓게 합니다."),
        ("air_doctrine", "air_doctrine", "공군 교리",
         "비행기를 육군과 해군의 보조로 둘 것인지, 따로 싸우는 군대로 만들 것인지를 두고 오랜 논쟁이 이어졌습니다. 항공대 장교들은 마침내 "
         "자기들만의 교범을 손에 넣고, 그 교범의 첫 장은 제공권을 다룹니다."),
    ],
}

ROOT_ICON = {"economy": "construct_civ_factory", "army": "army_doctrines", "navy": "build_navy", "air": "build_airforce"}
ORDER = ["economy", "army", "navy", "air"]


def development(af, tree, prefix, x0, y0=0, branch=None):
    """Four branches of five focuses, side by side from column x0: a root, two focuses under it, the one they lead to,
    and a last one."""
    effects = {
        "economy": [af.civ(2)],
        "machine_tools": [af.tech(prefix + "dev_machine_tools", "industry"), af.pp(25)],
        "power_grid": [af.infra(1), af.tech(prefix + "dev_power_grid", "construction_tech")],
        "synthetic_fuel": [af.build("synthetic_refinery", 1), af.tech(prefix + "dev_synthetic_fuel", "synth_resources")],
        "war_production": [af.mil(3)],
        "army": [af.xp("army", 25), af.manpower(10000)],
        "rifles": [af.tech(prefix + "dev_rifles", "infantry_weapons"), af.rifles(1000)],
        "artillery": [af.tech(prefix + "dev_artillery", "artillery")],
        "tanks": [af.tech(prefix + "dev_tanks", "armor")],
        "mobile_doctrine": [af.tech(prefix + "dev_mobile_doctrine", "land_doctrine"), af.tech(prefix + "dev_mobile_trucks", "motorized_equipment")],
        "navy": [af.xp("navy", 25), af.dock(1)],
        "destroyers": [af.tech(prefix + "dev_destroyers", "dd_tech")],
        "submarines": [af.tech(prefix + "dev_submarines", "ss_tech")],
        "capital_ships": [af.tech(prefix + "dev_capital_ships", "bb_tech"), af.dock(2)],
        "fleet_doctrine": [af.tech(prefix + "dev_fleet_doctrine", "naval_doctrine"), af.xp("navy", 25)],
        "air": [af.xp("air", 25), af.build("air_base", 2)],
        "fighters": [af.tech(prefix + "dev_fighters", "light_fighter")],
        "bombers": [af.tech(prefix + "dev_bombers", "tactical_bomber")],
        "aircraft_plants": [af.mil(2)],
        "air_doctrine": [af.tech(prefix + "dev_air_doctrine", "air_doctrine"), af.xp("air", 25)],
    }
    for i, kind in enumerate(ORDER):
        x = x0 + i * 4
        name, desc = ROOTS[prefix][kind]
        root = prefix + "dev_" + kind
        af.focus(tree, root, ROOT_ICON[kind], x + 1, y0, name, desc, *effects[kind], branch=branch)
        (a_id, a_icon, a_name, a_desc), (b_id, b_icon, b_name, b_desc), (c_id, c_icon, c_name, c_desc), (d_id, d_icon, d_name, d_desc) = SHARED[kind]
        af.focus(tree, prefix + "dev_" + a_id, a_icon, x, y0 + 1, a_name, a_desc, *effects[a_id], pre=[root], branch=branch)
        af.focus(tree, prefix + "dev_" + b_id, b_icon, x + 2, y0 + 1, b_name, b_desc, *effects[b_id], pre=[root], branch=branch)
        af.focus(tree, prefix + "dev_" + c_id, c_icon, x + 1, y0 + 2, c_name, c_desc, *effects[c_id],
                 pre=[prefix + "dev_" + a_id, prefix + "dev_" + b_id], branch=branch)
        af.focus(tree, prefix + "dev_" + d_id, d_icon, x + 1, y0 + 3, d_name, d_desc, *effects[d_id], pre=[prefix + "dev_" + c_id], branch=branch)
