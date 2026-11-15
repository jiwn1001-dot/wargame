"""Capitulation news for France's great enemies. Since 2026-11-13 the terms are written at the peace conference and
settled by region decisions, so the news reports the fall and the coming conference, not fixed terms.
Broadcast style (docs/STYLE_GUIDE.md, section 3). styled_text.py merges NEWS into STYLED.
"""
P = "\\n\\n"

NEWS = {
    "lr_news.10.t": "프로이센 항복",
    "lr_news.10.d": P.join([
        "북독일 연방이 프랑스에 항복했습니다. 베를린 주재 외교관들에 따르면 연방 정부는 오늘 오전 휴전 문서에 서명했으며, 프로이센군은 각 전선에서 사격을 멈췄습니다.",
        "강화 회의는 곧 열릴 예정입니다. 라인강 서안과 한자 도시들, 동부 영토의 장래가 그 자리에서 정해질 것으로 보입니다. 바르샤바와 뮌헨은 벌써 대표단을 꾸리기 시작한 것으로 알려졌습니다."]),
    "lr_news.11.t": "합스부르크 항복",
    "lr_news.11.d": P.join([
        "오스트리아 제국이 프랑스에 항복했습니다. 빈의 외무부는 황제의 재가를 받아 휴전에 동의했다고 발표했습니다.",
        "제국의 여러 민족 지도자들은 강화 회의에 자기 대표를 보내겠다고 밝혔습니다. 갈리치아와 보헤미아, 이탈리아 영토의 운명을 두고 각국 외교관들의 움직임이 바빠지고 있습니다."]),
    "lr_news.12.t": "런던 함락",
    "lr_news.12.d": P.join([
        "영국이 프랑스에 항복했습니다. 런던 시내에서는 프랑스군의 행진이 목격되었고, 정부 청사에는 휴전을 알리는 포고문이 붙었습니다.",
        "왕실의 행방은 아직 확인되지 않았습니다. 해군 일부가 대서양으로 빠져나갔다는 보도가 있습니다. 해외 영토의 장래는 곧 열릴 강화 회의에서 다뤄질 것으로 보입니다."]),
    "lr_news.13.t": "캐나다 항복",
    "lr_news.13.d": P.join([
        "캐나다가 프랑스에 항복했습니다. 오타와 정부는 더는 저항할 수 없다고 발표했습니다.",
        "대서양 건너에서 영국 왕관이 설 자리는 이제 거의 남지 않았습니다. 북아메리카의 장래를 정할 강화 회의가 곧 열릴 예정입니다."]),
}
