"""France's wars on the rest of Europe, region by region. Every route gets these after its Rhine focus.

A plan focus fires a speech and opens a declaration of war, as a decision, on each country in the region.
"""

# Focus prefix, route flag, the focus the plans hang from.
WAR_PREFIXES = [
    ("LR_ORL_", "LR_route_orleans", "LR_ORL_rhine"),
    ("LR_BOU_", "LR_route_bourbon", "LR_BOU_rhine"),
    ("LR_COM_", "LR_route_communist", "LR_COM_rhine"),
    ("LR_JAC_", "LR_route_jacobin", "LR_JAC_rhine"),
    ("LR_GIR_", "LR_route_girondin", "LR_GIR_rhine"),
    ("LR_MAR_", "LR_route_marais", "LR_MAR_rhine"),
    ("LR_NAP_", "LR_route_empire", "LR_NAP_rhine"),
    ("LR_GUA_", "LR_route_guardian", "LR_GUA_rhine"),
    ("LR_PET_", "LR_route_petain", "LR_PET_rhine"),
    ("LR_ANA_", "LR_route_anarchist", "LR_ANA_rhine"),
    ("LR_RED_", "LR_route_red", "LR_RED_rhine"),
]
ROUTE_FAMILY_FLAGS = {
    "king": ("LR_route_orleans", "LR_route_bourbon"),
    "commune": ("LR_route_communist",),
    "republic": ("LR_route_jacobin", "LR_route_girondin", "LR_route_marais"),
    "emperor": ("LR_route_empire",),
    "guardian": ("LR_route_guardian",),
    "petain": ("LR_route_petain",),
    "anarchist": ("LR_route_anarchist",),
    "red": ("LR_route_red",),
}
# The last words of every war speech, in the voice of whoever rules France.
FAMILY_CLOSE = {
    "king": "왕이 칼을 뽑아 지도 위에 올려놓습니다. 프랑스 왕의 영광은 국경선에서 멈춘 적이 없습니다. 몽주아 생드니!",
    "commune": "위원회의 결의는 한 줄입니다. 왕궁에는 전쟁을, 오두막에는 평화를! 인터내셔널을 부르며 붉은 연대가 행진합니다.",
    "republic": "의회가 일어서서 라 마르세예즈를 부릅니다. 무기를 들어라, 시민들이여! 이번에는 그 노래가 국경 너머까지 들릴 것입니다.",
    "emperor": "황제가 지도에서 눈을 들고 짧게 말합니다. 진군. 그 한 마디에 유럽의 지도가 또 한 번 바뀝니다. 황제 만세!",
    "guardian": "대통령은 군복 깃을 여미고 의회에 승인을 청합니다. 공화국이 칼을 드는 것은 다시는 칼을 들지 않기 위해서입니다. 공화국 만세!",
}
# Countries France takes outright when they give up; the rest become puppets.
ANNEXED = ["BEL", "LUX", "HOL"]

PLANS = [
    {
        "key": "low", "after": None, "event": 1301, "icon": "occupy_start_war", "picture": "soldiers_marching",
        "name": "저지대 계획", "desc": "브뤼셀과 룩셈부르크, 암스테르담, 그리고 알프스의 은행가들. 중립국들의 시대는 끝나 가고 있습니다.",
        "title": "슐리펜의 길을 거꾸로",
        "text": "참모본부의 지도에서 벨기에는 언제나 복도였습니다. 1914년에 프로이센은 그 복도로 들어왔습니다. 이번에는 프랑스가 반대 방향으로 지나갑니다. 왈론의 광부들은 벌써 프랑스어 전단을 받아 듭니다.",
        "targets": {"BEL": "벨기에", "LUX": "룩셈부르크", "HOL": "네덜란드 공화국", "SWI": "스위스"},
        "options": [("복도를 연다.", {"war_support_factor": 0.02}), ("안트베르펜 항구부터 친다.", {"raw": ["navy_experience = 25"]})],
    },
    {
        "key": "south_germany", "after": None, "event": 1302, "icon": "major_war", "picture": "france_parade",
        "name": "슈바르츠발트 너머", "desc": "뮌헨과 슈투트가르트의 왕들은 언제나 베를린보다 파리를 덜 무서워했습니다.",
        "title": "슈바르츠발트 너머",
        "text": "남독일 연방의 왕들은 프로이센의 패권을 싫어하면서도 대전쟁에서 함께 싸웠습니다. 프랑스의 사절은 이제 숲 너머로 마지막 질문을 보냅니다. 베를린과 함께 무너지겠습니까? 뮌헨의 답장은 없었습니다. 포병이 스트라스부르로 이동합니다.",
        "targets": {"BAY": "남독일 연방"},
        "options": [("라인강을 건너 뮌헨으로.", {"army_morale_factor": 0.02}), ("라인 연방을 약속한다.", {"political_power_gain": 0.02})],
    },
    {
        "key": "iberia", "after": None, "event": 1303, "icon": "demand_territory", "picture": "soldiers_marching",
        "name": "피레네 계획", "desc": "루이 14세는 피레네가 없어졌다고 말했습니다. 이제 그 말을 사실로 만들 때입니다.",
        "title": "피레네는 없다",
        "text": "태양왕은 손자를 마드리드로 보내며 이제 피레네는 없다고 했습니다. 두 세기 반이 지났지만 그 산맥은 여전히 그 자리에 있습니다. 어느 프랑스 왕도 그 말을 사실로 만들지 못했습니다. 이제 프랑스 군대가 합니다. 리스본의 금고와 지브롤터의 포대가 그 너머에서 기다립니다.",
        "targets": {"SPR": "스페인", "CRL": "카를로스파 스페인", "ESR": "스페인 공화파", "POR": "포르투갈"},
        "options": [("마드리드로 곧장 간다.", {"war_support_factor": 0.02}), ("카탈루냐부터 달랜다.", {"stability_factor": 0.01})],
    },
    {
        "key": "italy", "after": None, "event": 1304, "icon": "major_war", "picture": "france_parade",
        "name": "알프스 계획", "desc": "한니발도, 프랑수아 1세도 이 길을 넘었습니다. 토리노에서 나폴리까지 네 왕이 서로를 노려보고 있습니다.",
        "title": "알프스를 넘어",
        "text": "샤를 8세의 원정 이래 프랑스 왕들은 이탈리아라는 꿈을 끊지 못했습니다. 토리노, 로마, 피렌체, 나폴리의 네 나라는 지금도 서로를 더 미워합니다. 몽스니 고개의 눈이 녹았습니다. 포병대가 노새 위에 올라갑니다.",
        "targets": {"ITA": "사르데냐", "PAP": "교황령", "TOS": "토스카나", "TTS": "양시칠리아"},
        "options": [("고개를 넘어라.", {"army_morale_factor": 0.02}), ("교황께는 먼저 서한을 보낸다.", {"political_power_gain": 0.02})],
    },
    {
        "key": "north", "after": "low", "event": 1305, "icon": "navy_doctrines_tactics", "picture": "sailors_in_working_rig",
        "name": "북해 계획", "desc": "덴마크 해협을 쥐면 발트해가 닫힙니다. 스칸디나비아의 왕들은 중립이 오래가지 않음을 압니다.",
        "title": "얼음 바다로",
        "text": "프랑스 군함이 스카게라크에 들어간 것은 언제가 마지막이었을까요. 아무도 기억하지 못합니다. 그래서 더욱 놀라울 것입니다. 코펜하겐의 해협, 나르비크의 철광, 스웨덴의 베어링, 핀란드의 숲. 북유럽 왕국들의 중립은 그 값이 너무 비쌌습니다.",
        "targets": {"DEN": "덴마크", "NOR": "노르웨이", "SWE": "스웨덴", "FIN": "핀란드", "ICE": "아이슬란드"},
        "options": [("코펜하겐부터.", {"raw": ["navy_experience = 25"]}), ("나르비크의 철광부터.", {"industrial_capacity_factory": 0.01})],
    },
    {
        "key": "east", "after": "south_germany", "event": 1306, "icon": "major_war", "picture": "soldiers_marching",
        "name": "동유럽 계획", "desc": "바르샤바와 키예프, 리가. 대전쟁이 러시아에게서 떼어 낸 작은 왕국들이 이제 프랑스의 답을 기다립니다.",
        "title": "비스와강의 삼색기",
        "text": "폴란드 공국과 우크라이나 왕국, 벨라루스, 발트 공국들, 캅카스의 왕국들. 대전쟁의 승자들이 러시아에서 떼어 내 세운 나라들입니다. 지도 위에서는 나라이지만, 그 왕들 대부분은 왕이 된 지 스무 해도 안 됩니다. 프랑스의 깃발이 비스와강까지 가면 그들도 고를 수 있을 것입니다.",
        "targets": {"POL": "폴란드", "LIT": "리투아니아", "LAT": "라트비아", "EST": "에스토니아", "BLR": "벨라루스", "UKR": "우크라이나", "GEO": "조지아", "ARM": "아르메니아", "AZR": "아제르바이잔"},
        "options": [("폴란드를 해방한다.", {"political_power_gain": 0.02}), ("곡창 지대를 노린다.", {"raw": ["add_manpower = 30000"]})],
    },
    {
        "key": "balkans", "after": "italy", "event": 1307, "icon": "demand_territory", "picture": "soldiers_marching",
        "name": "발칸 계획", "desc": "유럽의 화약고. 소피아와 베오그라드, 아테네와 부쿠레슈티는 서로를 물어뜯느라 뒤를 보지 않습니다.",
        "title": "화약고로",
        "text": "대불가리아, 세르비아, 그리스, 루마니아. 스무 해 동안 서로의 지도를 고쳐 그려 온 나라들입니다. 지중해 함대가 살로니카로 향합니다. 어느 편을 들지는 중요하지 않습니다. 발칸의 왕들은 언제나 다음 전쟁의 동맹을 찾아왔고, 이제 프랑스가 그 답입니다.",
        "targets": {"BUL": "불가리아", "YUG": "세르비아", "GRE": "그리스", "ROM": "루마니아", "ALB": "알바니아", "MNT": "몬테네그로", "MOL": "몰다비아"},
        "options": [("살로니카에 상륙한다.", {"raw": ["navy_experience = 25"]}), ("약한 쪽에 소총을 보낸다.", {"political_power_gain": 0.02})],
    },
    {
        "key": "turkey", "after": "balkans", "event": 1308, "icon": "major_war", "picture": "generic_battle",
        "name": "동방 원정", "desc": "대전쟁의 승자, 도나우에서 페르시아만까지 뻗은 오스만 제국. 십자군 이래 가장 야심 찬 프랑스의 동방 원정입니다.",
        "title": "제9차 십자군",
        "text": "프랑스 왕들은 일곱 번을 넘게 레반트로 떠났습니다. 대전쟁 뒤 오스만의 깃발은 이제 트리폴리에서 바스라까지 펄럭입니다. 다르다넬스를 뚫으면 이스탄불이고, 시리아를 치면 석유입니다. 레바논의 마론파는 아직도 프랑스 왕의 이름으로 기도합니다.",
        "targets": {"TUR": "오스만 제국"},
        "options": [("다르다넬스로.", {"raw": ["navy_experience = 40"]}), ("레반트에 상륙한다.", {"raw": ["army_experience = 40"]})],
    },
]


from new_routes import FAMILY_CLOSE as _NEW_CLOSE  # noqa: E402
FAMILY_CLOSE.update(_NEW_CLOSE)
