"""After the second defeat: occupied France, between collaboration and resistance.

When France capitulates (lr_france_defeated) every route closes and the occupation route opens. A shared trunk
of survival, then a choice: cooperate with the victor for autonomy, or build the resistance until Paris rises.
Each road ends in a long scene. The resistance is a variable, LR_resist (0-100): resistance focuses raise it,
collaboration lowers it, and the rising needs 60.

new_routes.py calls define(), arrange(), weave_routes() and spirits() and merges the tables.
"""
from france_story import chapter

P = "\\n\\n"
Q = '\\"'


def say(line):
    return f"{Q}{line}{Q}"


DEF, DEF_ROUTE = "LR_DEF_", "LR_route_vanquished"
RESIST = "add_to_variable = {{ LR_resist = {} }}\nclamp_variable = {{ var = LR_resist min = 0 max = 100 }}".format

IDEAS = [
    ("LR_idea_def_rations", "배급표", "빵과 석탄과 신발에 배급표가 붙었습니다.", "generic_central_management", {"stability_factor": 0.05, "consumer_goods_factor": -0.02}),
    ("LR_idea_def_collab", "협력 행정부", "승전국의 감독관이 각 부처에 앉아 있습니다. 대신 행정은 굴러갑니다.", "generic_disjointed_gov", {"political_power_gain": 0.1, "stability_factor": 0.05, "war_support_factor": -0.05}),
    ("LR_idea_def_maquis", "마키", "알프스와 마시프상트랄의 숲에 숨어든 청년들이 총을 듭니다.", "generic_reserve_divisions", {"war_support_factor": 0.08, "stability_factor": -0.03}),
    ("LR_idea_def_secret_army", "비밀군", "옛 장교들이 지하에서 연대를 다시 짭니다.", "generic_army_war_college", {"army_org_factor": 0.03, "experience_gain_army_factor": 0.05}),
]
REGIMES = {"vanquished": ("점령된 프랑스", {"stability_factor": -0.1, "war_support_factor": -0.1})}


def define(g):
    focus, extras, ROOT = g["focus"], g["extras"], g["ROOT"]
    stab, war, pp, xp, civ, pop = (g[n] for n in ("stab", "war", "pp", "xp", "civ", "pop"))
    g["IDEAS"].extend(IDEAS)
    idea = "add_ideas = {}".format
    focus(DEF + "occupation", "national_unity", 16, 1, "점령의 겨울", "두 번째 패전. 파리의 관공서마다 승전국의 깃발이 걸렸습니다.", stab(0.05), pre=[ROOT], route=DEF_ROUTE, cost=5)
    extras(DEF, DEF_ROUTE, [
        # 내정: survival
        ("rations", "trade", 0, 0, "배급표", "빵과 석탄과 신발에 배급표를 붙입니다.", ["occupation"], [idea("LR_idea_def_rations")]),
        ("prisoners", "improve_relations", 0, 0, "포로 귀환 협상", "수용소의 병사 수십만 명을 돌려 달라고 청합니다.", ["occupation"], ["add_manpower = 60000"]),
        ("black_market", "intelligence_exchange", 0, 0, "암시장", "레알 시장 뒷골목의 암시장을 단속할지 눈감을지 정합니다.", ["rations"], [pp(50), stab(0.02)]),
        ("ruins", "construct_civilian", 0, 0, "폐허의 재건", "포격으로 무너진 북부의 도시를 다시 짓습니다.", ["prisoners"], [civ(2)]),
        ("winter_relief", "propaganda", 0, 0, "겨울 구호", "교회와 적십자가 겨울 외투와 수프를 나눕니다.", ["black_market", "ruins"], [stab(0.05)]),
        # 정치: the choice
        ("two_roads", "political_pressure", 0, 0, "두 갈래 길", "승전국과 손을 잡을 것인가, 숲으로 들어갈 것인가.", ["occupation"], [pp(25)]),
        ("cooperate", "dangerous_deal", 0, 0, "승전국과의 협력", "점령군 사령관과 같은 식탁에 앉습니다.", ["two_roads"], [pp(75), RESIST(-20)]),
        ("collab_admin", "political_pressure", 0, 0, "협력 행정부", "승전국의 감독관과 함께 각 부처를 운영합니다.", ["cooperate"], [idea("LR_idea_def_collab"), RESIST(-10)]),
        ("reparations_paid", "trade", 0, 0, "배상금 완납", "마지막 배상금 수표에 서명합니다.", ["collab_admin"], [pp(50), RESIST(-10)]),
        ("autonomy", "national_unity", 0, 0, "자치 회복", "승전국이 프랑스의 자치를 넓혀 주겠다고 합니다.", ["reparations_paid"], ["country_event = { id = lr_novel.1201 }"]),
        ("resist", "special_forces", 0, 0, "숲으로", "젊은이들이 징용 명단을 피해 숲으로 들어갑니다.", ["two_roads"], [RESIST(20), war(0.05)]),
        ("maquis", "allies_build_infantry", 0, 0, "마키", "알프스와 마시프상트랄의 숲에 저항 거점을 세웁니다.", ["resist"], [idea("LR_idea_def_maquis"), RESIST(15)]),
        ("sabotage", "forceful_treaty", 0, 0, "철도 사보타주", "점령군의 보급 열차가 다리 위에서 멈춥니다.", ["maquis"], [RESIST(15)]),
        ("secret_army", "army_doctrines", 0, 0, "비밀군", "옛 장교들이 지하에서 연대를 다시 짭니다.", ["maquis"], [idea("LR_idea_def_secret_army"), RESIST(10)]),
        ("rising", "propaganda", 0, 0, "8월의 봉기", "파리의 바리케이드가 다시 올라갑니다.", ["sabotage", "secret_army"], ["country_event = { id = lr_novel.1301 }"]),
        # 외교
        ("exile_committee", "alliance", 0, 0, "제네바의 망명 위원회", "국경 너머의 망명자들이 자유 프랑스 위원회를 세웁니다.", ["occupation"], [pp(50), RESIST(5)]),
        ("world_opinion", "improve_relations", 0, 0, "세계 여론", "중립국 신문에 점령의 실상을 알립니다.", ["exile_committee"], [stab(0.02), RESIST(5)]),
        # 안정도
        ("curfew", "fortify_city", 0, 0, "통행금지", "밤 열 시 이후 파리의 거리는 텅 빕니다.", ["occupation"], ["lr_fra_op_reduce = yes"]),
    ])
    for item in g["FOCUSES"]:
        if item["id"] == DEF + "cooperate":
            item["me"] = [DEF + "resist"]
        elif item["id"] == DEF + "resist":
            item["me"] = [DEF + "cooperate"]
        elif item["id"] == DEF + "rising":
            item["available"] = "custom_trigger_tooltip = {\n\ttooltip = LR_tt_resist_60\n\tcheck_variable = { LR_resist > 59 }\n}"
        elif item["id"] == DEF + "autonomy":
            item["available"] = "custom_trigger_tooltip = {\n\ttooltip = LR_tt_resist_low\n\tcheck_variable = { LR_resist < 30 }\n}\nhas_stability > 0.5"


def arrange(g):
    plan, BY_ID, FILTERS = g["plan"], g["BY_ID"], g["FILTERS"]
    plan(DEF, "occupation", [
        ("내정", ["rations", "black_market", "prisoners", "ruins", "winter_relief"]),
        ("정치", ["two_roads", ("cooperate", "resist")]),
        ("외교", ["exile_committee", "world_opinion"]),
        ("안정도", ["curfew"]),
    ])
    BY_ID[DEF + "occupation"]["filter"] = FILTERS["정치"]
    for key in ("collab_admin", "reparations_paid", "autonomy"):
        BY_ID[DEF + key]["filter"] = FILTERS["정치"]
    for key in ("maquis", "sabotage", "secret_army", "rising"):
        BY_ID[DEF + key]["filter"] = FILTERS["영토확장"]


def weave_routes(g):
    weave = g["weave"]
    weave(DEF, "occupation", "내정", [["rations", "prisoners"], ["black_market<rations", "ruins<prisoners"], ["winter_relief<black_market+ruins"]])
    weave(DEF, "occupation", "정치", [["two_roads"], [("cooperate", "resist")], ["collab_admin<cooperate", "maquis<resist"],
                                       ["reparations_paid<collab_admin", "sabotage<maquis", "secret_army<maquis"], ["autonomy<reparations_paid", "rising<sabotage+secret_army"]])
    for key in ("maquis", "sabotage", "secret_army", "rising"):
        g["BY_ID"][DEF + key]["filter"] = g["FILTERS"]["영토확장"]


def spirits(g):
    g["spirit"](DEF + "occupation", "점령의 겨울", "파리의 관공서마다 승전국의 깃발이 걸렸습니다. 프랑스는 다시 일어설 수 있을까요.", "generic_disjointed_gov",
                {"stability_factor": 0.03})


STORY = [
    ("LR_DEF_occupation", DEF, DEF_ROUTE, 1700, [
        chapter("commandant", "dangerous_deal", "사령관의 만찬", "점령군 사령관이 파리의 명사들을 만찬에 부릅니다.", {"political_power_gain": 0.02},
                "리츠 호텔의 만찬", P.join([
                    "방돔 광장의 리츠 호텔. 점령군 사령관이 파리의 명사 마흔 명을 만찬에 초대했습니다. 은행가, 극장 주인, 주교, 그리고 옛 정부의 장관 몇 명.",
                    "초대장에는 거절할 경우에 대한 말이 없습니다. 그러나 모두가 그 뜻을 압니다.",
                    "총리 비서실장이 묻습니다. " + say("정부 대표로 누가 가야 할까요? 아니면 아무도 보내지 않을까요?")]), "generic_sign_treaty1", [
                    ("총리가 직접 간다. 식탁에서 얻을 수 있는 것은 얻는다.", {"political_power_gain": 0.03, "flag": "LR_st_def_dinner"}),
                    ("아무도 보내지 않는다. 빈 의자가 대답이다.", {"war_support_factor": 0.03}),
                ]),
        chapter("first_execution", "special_forces", "첫 처형", "점령군 장교 한 명이 지하철역에서 총에 맞았습니다.", {"war_support_factor": 0.02},
                "바르베스역의 총성", P.join([
                    "바르베스 로슈슈아르 지하철역. 점령군 해군 사관후보생 한 명이 플랫폼에서 등 뒤로 총을 맞고 쓰러졌습니다. 범인은 군중 속으로 사라졌습니다.",
                    "다음 날 아침, 점령군 사령부의 포고문이 파리의 벽마다 붙었습니다. 범인이 잡히지 않으면 인질 50명을 총살한다.",
                    "점령군 사령관이 프랑스 정부에 명단을 요구합니다. 누구를 내줄 것인지 프랑스가 정하라고."]), "generic_riot", [
                    ("명단을 거부한다. 프랑스는 자기 시민을 넘기지 않는다.", {"war_support_factor": 0.04, "stability_factor": -0.03}),
                    ("이미 감옥에 있는 공산주의자들의 이름을 적는다.", {"political_power_gain": 0.03, "communism_drift": -0.02, "stability_factor": 0.02}),
                ]),
        chapter("second_winter", "national_unity", "두 번째 겨울", "점령 아래 두 번째 겨울이 옵니다.", {"stability_factor": 0.03},
                "센강이 얼다", P.join([
                    "1월, 센강이 얼었습니다. 파리의 아파트에는 석탄이 없고, 아이들은 외투를 입은 채 잠듭니다. 공원의 나무들이 하룻밤 사이에 사라집니다.",
                    "빵집 앞 줄에서 사람들이 소곤거립니다. 숲에 들어간 젊은이들이 늘었다고. 지방의 철로가 또 끊겼다고.",
                    "라디오에서는 정부의 신년사가 흘러나옵니다. 듣는 사람은 많지 않습니다."]), "generic_read_write", [
                    ("점령군에게 석탄을 더 달라고 청한다.", {"stability_factor": 0.04, "need": "LR_st_def_dinner"}),
                    ("교회와 노조에 구호를 맡긴다.", {"stability_factor": 0.03, "war_support_factor": 0.01}),
                    ("숲의 젊은이들에게 몰래 보급을 보낸다.", {"war_support_factor": 0.05, "avoid": "LR_st_def_dinner"}),
                ]),
    ]),
]

BRANCH = [
    ("LR_DEF_black_market", "generic_read_write", "레알의 뒷골목", "암시장의 가격이 배급 가격의 열 배가 되었습니다.", [
        ("단속한다. 배급은 모두에게 같아야 한다.", {"stability_factor": 0.02, "raw": ["add_political_power = -25"]}),
        ("눈감는다. 암시장이 없으면 파리는 굶는다.", {"political_power_gain": 0.02}),
    ]),
    ("LR_DEF_maquis", "soldiers_marching", "숲의 청년들", "징용 명단에 오른 청년 수천 명이 사라졌습니다.", [
        ("옛 장교를 보내 훈련시킨다.", {"army_org_factor": 0.02, "raw": ["add_to_variable = { LR_resist = 5 }"]}),
        ("총보다 먼저 빵을 보낸다.", {"stability_factor": 0.02}),
    ]),
]
BRANCH_TEXT = {
    "LR_DEF_black_market": P.join([
        "레알 시장 뒷골목. 배급표로는 일주일에 버터 50그램이 나오는데, 이곳에서는 돈만 있으면 버터도 커피도 고기도 삽니다. 가격은 배급 가격의 열 배입니다.",
        "경찰은 이 골목을 압니다. 장관 부인들이 이 골목에서 장을 본다는 것도 압니다.",
        "경시총감이 묻습니다. " + say("단속할까요? 단속하면 시장 사람들이 굶고, 안 하면 노동자들이 분노합니다.")]),
    "LR_DEF_maquis": P.join([
        "징용 명단이 붙은 다음 날, 리옹과 그르노블의 청년 수천 명이 사라졌습니다. 그들은 알프스와 마시프상트랄의 숲으로 들어갔습니다. 농부들은 그들을 마키라고 부릅니다. 덤불이라는 뜻입니다.",
        "그들에게는 총도 군화도 없습니다. 있는 것은 분노와 젊음뿐입니다.",
        say("무엇을 먼저 보낼까요?")]),
}

FOCUS_TEXT = {
    "LR_DEF_occupation": "두 번째 패전입니다. 콩피에뉴 숲의 객차에서 다시 항복 문서에 서명했습니다. 파리의 관공서마다 승전국의 깃발이 걸렸고, 새 정부는 승전국의 뜻에 따라 구성되었습니다. 이제 프랑스는 살아남는 법부터 다시 배워야 합니다.",
    "LR_DEF_rations": "빵과 석탄과 신발에 배급표가 붙습니다. 주부들은 새벽부터 빵집 앞에 줄을 서고, 배급표 위조범이 경찰의 새 골칫거리가 됩니다.",
    "LR_DEF_prisoners": "전쟁 포로 수십만 명이 승전국의 수용소에 있습니다. 그들을 돌려받는 것이 새 정부의 첫 외교 과제입니다. 값은 비쌉니다.",
    "LR_DEF_black_market": "레알 시장 뒷골목에서는 돈만 있으면 무엇이든 삽니다. 암시장을 단속할 것인가, 눈감을 것인가.",
    "LR_DEF_ruins": "포격으로 무너진 북부의 도시들. 아라스와 릴의 시민들이 맨손으로 벽돌을 줍기 시작합니다.",
    "LR_DEF_winter_relief": "교회와 적십자와 노조가 처음으로 같은 줄에 서서 겨울 외투와 수프를 나눕니다.",
    "LR_DEF_two_roads": "승전국과 손을 잡을 것인가, 숲으로 들어갈 것인가. 프랑스는 둘로 갈라집니다. 이 결정은 되돌릴 수 없습니다.",
    "LR_DEF_cooperate": "점령군 사령관과 같은 식탁에 앉습니다. 협력하면 배급은 늘고 포로는 돌아옵니다. 그 대가를 사람들은 오래 기억할 것입니다.",
    "LR_DEF_collab_admin": "승전국의 감독관이 각 부처에 앉고, 프랑스 공무원들이 그들의 지시를 받아 적습니다. 행정은 굴러가고, 기차는 제시간에 달립니다.",
    "LR_DEF_reparations_paid": "마지막 배상금 수표에 서명합니다. 금고는 비었지만, 승전국은 이제 프랑스에 요구할 것이 없습니다.",
    "LR_DEF_autonomy": "충실한 협력의 대가로 승전국이 프랑스의 자치를 넓혀 주겠다고 합니다. 감독관들이 짐을 쌉니다. 그러나 프랑스는 정말 자유로워졌을까요.",
    "LR_DEF_resist": "징용 명단이 붙자 젊은이들이 숲으로 들어갑니다. 정부는 공식적으로 그들을 모른다고 말합니다. 비공식적으로는 다릅니다.",
    "LR_DEF_maquis": "알프스와 마시프상트랄의 숲에 저항 거점이 생깁니다. 농부들은 그들에게 빵을 주고, 헌병들은 못 본 척합니다.",
    "LR_DEF_sabotage": "점령군의 보급 열차가 다리 위에서 멈춥니다. 철도원 노조가 레지스탕스의 가장 큰 무기가 됩니다.",
    "LR_DEF_secret_army": "옛 장교들이 지하에서 연대를 다시 짭니다. 무기는 산속 동굴에, 명부는 수녀원 지하실에 숨겨집니다.",
    "LR_DEF_rising": "파리의 바리케이드가 다시 올라갑니다. 1830년에도, 1848년에도, 1871년에도 그랬습니다. 이번에는 점령군을 몰아내기 위해서입니다.",
    "LR_DEF_exile_committee": "국경 너머 제네바에서 망명자들이 자유 프랑스 위원회를 세웁니다. 그들의 방송은 밤마다 프랑스의 라디오에서 몰래 흘러나옵니다.",
    "LR_DEF_world_opinion": "중립국 신문에 점령의 실상을 알립니다. 스웨덴과 스위스의 기자들이 파리의 배급 줄을 사진으로 찍어 갑니다.",
    "LR_DEF_curfew": "밤 열 시 이후 파리의 거리는 텅 빕니다. 순찰대의 군화 소리만 울립니다.",
    "LR_DEF_commandant": "점령군 사령관이 파리의 명사들을 리츠 호텔 만찬에 부릅니다.",
    "LR_DEF_first_execution": "점령군 장교 한 명이 지하철역에서 총에 맞았습니다. 점령군은 인질 명단을 요구합니다.",
    "LR_DEF_second_winter": "점령 아래 두 번째 겨울. 센강이 얼고, 공원의 나무들이 하룻밤 사이에 사라집니다.",
}

# ===== The two endings, told over several pages =====
NOVEL = {
    "lr_france.53": {"pages": [
        P.join([
            "봄, 파리 외무부 시계의 방.",
            "점령군 사령관이 마지막 서류에 서명합니다. 감독관들은 이번 주 안에 각 부처에서 철수하고, 점령군은 라인강 너머의 몇몇 요새로 물러납니다. 프랑스는 다시 스스로 다스리게 됩니다. 몇 가지 조건만 지킨다면.",
            "사령관이 만년필 뚜껑을 닫으며 웃습니다. " + say("귀국은 모범적인 동반자였습니다."),
        ]),
        P.join([
            "총리는 그 말에 대답하지 않습니다. 창밖의 오르세 강변에는 점령군 트럭들이 짐을 싣고 있습니다.",
            "포로들은 돌아왔고, 배급은 늘었으며, 기차는 제시간에 달립니다. 그 대가로 프랑스는 2년 동안 승전국이 시키는 대로 했습니다. 명단을 넘겼고, 공장을 내주었고, 숲의 젊은이들을 쫓았습니다.",
            "비서가 신문을 가져옵니다. 1면에는 해방이 아니라 정상화라는 단어가 실렸습니다.",
        ]),
        P.join([
            "그날 밤, 총리가 퇴근길에 생제르맹 거리의 카페 앞을 지납니다. 테라스의 사람들이 그를 알아보고 말을 멈춥니다. 누구도 인사하지 않습니다.",
            "어느 노인이 신문을 접으며 낮게 말합니다. " + say("살아남았지. 그건 맞아."),
            "총리는 걸음을 멈추지 않습니다. 그는 프랑스를 구했다고 믿습니다. 역사가 그렇게 기록할지는 알 수 없습니다.",
        ]),
        P.join([
            "몇 년 뒤, 리옹의 어느 고등학교 역사 시간. 교과서에는 점령기가 두 쪽에 걸쳐 실렸습니다. 협력이라는 단어는 한 번도 나오지 않습니다.",
            "맨 뒷자리의 학생 하나가 손을 듭니다. 할아버지가 그 시절 숲에 있었다고, 그런데 교과서에는 숲 이야기가 없다고.",
            "선생님은 잠깐 창밖을 보다가 대답합니다. 그 이야기는 아직 쓰이지 않았다고. 그리고 너희가 쓰게 될 거라고.",
        ]),
    ]},
    "lr_france.54": {"pages": [
        P.join([
            "8월 19일 새벽, 파리 경시청.",
            "경찰관 3천 명이 경시청 안마당에 모였습니다. 2년 동안 점령군의 명령을 받아 시민을 체포하던 사람들입니다. 누군가 지붕 위로 올라가 삼색기를 겁니다.",
            "같은 시각, 벨빌과 생앙투안과 라틴 지구의 거리마다 포석이 뜯겨 나갑니다. 1830년에도, 1848년에도, 1871년에도 그랬던 것처럼, 파리가 바리케이드를 쌓습니다.",
        ]),
        P.join([
            "엿새 동안 파리가 싸웁니다. 숲에서 내려온 마키들이 교외 역을 점거하고, 철도원들이 점령군의 증원 열차를 멈춥니다. 노트르담의 종이 울리기 시작합니다.",
            "8월 25일, 점령군 사령관이 몽파르나스역의 당구장에서 항복 문서에 서명합니다. 그는 파리를 불태우라는 명령을 받았지만, 끝내 따르지 않았다고 말합니다.",
            "승전국은 더 이상 프랑스를 붙잡아 둘 수 없다는 것을 압니다.",
        ]),
        P.join([
            "8월 26일, 샹젤리제. 숲에서 내려온 청년들과 경찰관과 철도원과 수녀들이 한 줄로 개선문에서 노트르담까지 걷습니다. 지붕 위에서는 아직 총성이 들립니다.",
            "제네바에서 돌아온 망명 위원회 의장이 시청 발코니에 섭니다.",
            say("파리! 짓밟힌 파리! 그러나 해방된 파리! 스스로의 힘으로, 인민의 손으로 해방된 파리!"),
        ]),
        P.join([
            "그날 밤, 파리의 모든 창문에 불이 켜졌습니다. 2년 만에 등화관제가 풀린 밤입니다. 사람들은 커튼을 걷고 창문을 활짝 열었습니다.",
            "몽마르트르 언덕에서 내려다보면 도시 전체가 빛납니다. 어느 노인이 손자의 어깨를 잡고 말합니다. 잘 봐 두어라. 이 불빛을 다시 끄려는 사람이 오면, 오늘 밤을 기억해라.",
            "멀리 동쪽 하늘이 붉습니다. 해가 뜨는 것이 아닙니다. 아직 전쟁은 끝나지 않았습니다.",
        ]),
    ]},
}
NOVEL_BASE = {"lr_france.53": 1200, "lr_france.54": 1300}
EVENTS = '''
# 53. The collaboration ending: autonomy, and a long silence.
country_event = {
	id = lr_france.53
	title = lr_france.53.t
	desc = lr_france.53.d
	picture = GFX_report_event_generic_sign_treaty1

	is_triggered_only = yes

	option = {
		name = lr_france.53.a
		OVERLORD = {
			set_autonomy = {
				target = ROOT
				autonomous_state = autonomy_dominion
			}
		}
		add_stability = 0.1
		set_country_flag = LR_ending_collaboration
	}
}

# 54. The liberation ending: Paris frees itself.
country_event = {
	id = lr_france.54
	title = lr_france.54.t
	desc = lr_france.54.d
	picture = GFX_report_event_france_parade

	is_triggered_only = yes

	option = {
		name = lr_france.54.a
		OVERLORD = { end_puppet = ROOT }
		set_politics = {
			ruling_party = democratic
			elections_allowed = yes
		}
		drop_cosmetic_tag = yes
		add_stability = 0.15
		add_war_support = 0.2
		set_country_flag = LR_ending_liberation
		news_event = { id = lr_gnews.21 days = 1 }
	}
}
'''
LOC = {
    "LR_tt_resist_60": "저항 세력이 §Y60§! 이상이어야 합니다. 지금 [?LR_resist|0]입니다.",
    "LR_tt_resist_low": "저항 세력이 §Y30§! 미만이어야 합니다. 지금 [?LR_resist|0]입니다.",
    "LR_tt_vanquished": "§R패전§!: 모든 루트가 닫히고 점령기 중점이 열립니다.",
    "lr_france.53.t": "모범적인 동반자",
    "lr_france.53.d": "몇 주 뒤, 마지막 감독관이 리옹역에서 기차에 오릅니다. 플랫폼에는 프랑스 장관 둘과 군악대가 나와 있습니다. 군악대는 승전국의 국가를 연주합니다." + P
                      + "프랑스는 다시 스스로 다스립니다. 국경과 군대와 외교에는 여전히 승전국의 승인이 필요합니다. 그래도 지난 2년보다는 훨씬 많은 것을 스스로 정합니다." + P
                      + "역 밖의 담벼락에는 누군가 분필로 한 단어를 적어 두었습니다. 기억하라. 청소부가 그것을 지우기까지 사흘이 걸렸습니다.",
    "lr_france.53.a": "살아남은 것이 이긴 것이다.",
    "lr_france.54.t": "해방된 파리",
    "lr_france.54.d": "시청 광장의 군중이 라 마르세예즈를 부릅니다. 1792년에 의용병들이 처음 부르며 파리로 걸어 들어왔던 노래입니다. 이번에는 파리가 스스로를 위해 부릅니다." + P
                      + "승전국은 점령군을 철수시키고 프랑스의 독립을 인정했습니다. 두 번 진 나라가 세 번째로 일어섰습니다." + P
                      + "봉기의 첫날 경시청 지붕에 삼색기를 걸었던 젊은 경찰관은 이제 그 깃발을 접어 아이에게 건넵니다. " + say("잊지 마라. 우리 손으로 되찾았다."),
    "lr_france.54.a": "프랑스는 다시 자유다.",
}
NEWS = ("파리 해방", "점령 2년 만에 파리가 일어섰습니다. 엿새 동안의 시가전 끝에 점령군 사령관이 항복했고, 승전국은 프랑스의 독립을 인정했습니다.\\n\\n두 번의 패전을 겪은 나라가 스스로의 힘으로 다시 일어섰다는 소식에, 유럽 각지의 점령지와 괴뢰국에서 같은 꿈을 꾸는 사람들이 늘고 있습니다.", "파리는 스스로 해방되었다.")
