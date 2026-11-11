"""Events rewritten to docs/STYLE_GUIDE.md: scenes in 해라체 from one person's view, news as plain reports,
options as the decider's own short line.

polish_text.apply() writes STYLED last, so these win over epic_text, polish_text and the builders.
Report events show up to about 950 characters on one page (build_eventwindow.py); news events still stop at
about 450.
"""
P = "\\n\\n"
Q = '\\"'


def say(line):
    return f"{Q}{line}{Q}"


def j(*parts):
    return P.join(parts)


STYLED = {
    # ----- 장면: 왕정의 독일 선전포고
    "lr_story.1202.d_king": j(
        "앙리 르클레르 중위는 새벽 네 시부터 샹드마르스에 서 있었다. 말이 자꾸 고개를 흔들었고, 장갑 속 손가락은 이미 감각이 없었다. 연대장은 일곱 시라고 했지만 왕의 차는 여덟 시 반이 되어서야 사열대 뒤에 멈췄다.",
        "왕은 생각보다 작았다. 르클레르는 왕을 가까이서 본 적이 없었다. 신문 사진 속의 왕은 늘 말 위에 있었는데, 오늘 사열대에 올라선 노인은 계단을 오르다 한 번 멈춰서 숨을 골랐다. 시종이 종이 한 장을 건넸다. 확성기가 두 번 끽 소리를 냈다.",
        say("...1918년 조약을 근거로 북독일 연방이 요구해 온 모든 것을, 짐은 오늘부로 거부한다. 그 조약에 서명한 자들의 군대가 우리의 거부를 받아들이지 않는다면, 짐의 군대가 그것을 받아들이게 할 것이다."),
        "그게 다였다. 옆에 선 기수 뒤부아가 작게 물었다. " + say("끝이야? 저게 선전포고야?") + " 르클레르는 대답하지 않았다.",
        "그의 아버지는 1918년 아르덴에서 돌아오지 않았다. 어머니는 그해 받은 전사 통지서를 지금도 성경책 사이에 끼워 두고 있었다. 르클레르는 그 종이를 딱 한 번 몰래 꺼내 읽어 본 적이 있었다. 날짜와 이름, 그리고 \\\"조국을 위해\\\"라는 인쇄된 글자가 전부였다.",
        "대열 뒤쪽 어딘가에서 누가 먼저 국왕 만세를 외쳤다. 처음에는 몇 명이었고, 곧 연병장 전체가 따라 외쳤다. 르클레르도 외쳤다. 생각보다 목소리가 컸다. 뒤부아가 그를 쳐다보며 웃었다.",
        "정오에 연대는 동역으로 행군했다. 플랫폼에는 어머니들이 나와 있었다. 르클레르는 자기 어머니를 찾지 않았다. 오지 않을 거라는 걸 알고 있었다."),
    "lr_story.1202.a": "베를린에서 보자.",
    "lr_story.1202.b": "알자스부터다. 서두를 것 없다.",
    # ----- 장면: 산악파 정부의 공장 점거
    "lr_story.1017.d": j(
        "내무부 차관 피에르 랑글루아는 비양쿠르 공장 정문 건너편 카페에서 세 번째 커피를 시켰다. 철문 위에는 점거 중이라고 페인트로 쓴 침대 시트가 걸려 있었다. 안에 3만 명이 있다고 했다. 랑글루아는 그 숫자를 믿지 않았지만, 정문 앞을 오가는 사람들을 보고 있으니 아주 틀린 말 같지도 않았다.",
        "이상한 점거였다. 기계는 멀쩡했다. 노동자들은 아침마다 선반에 기름칠을 했고, 점심때가 되면 지붕 위에서 누가 아코디언을 켰다. 담장 너머로 아내들이 바게트와 포도주를 넘겨주었다. 경비원 두 명은 정문 옆에 의자를 내놓고 앉아 담배를 피우고 있었다. 회사가 고용한 경비원들이었다.",
        "랑글루아는 커피를 다 마시고 정문으로 걸어갔다. 철문 사이로 작업복 차림의 젊은 남자가 그를 내다보았다. " + say("정부에서 왔소?") + " 랑글루아가 고개를 끄덕이자 남자가 물었다. " + say("경찰은 언제 오오?"),
        say("아무도 안 와요. 아직은."),
        say("아직은, 이라."),
        "남자는 웃더니 철문 틈으로 쪽지 한 장을 내밀었다. 노조 위원회 도장이 찍혀 있었다. 공안위원회는 누구 편이오. 그 한 줄뿐이었다.",
        "카페로 돌아오니 주인이 전화가 왔었다고 했다. 사장단 대표였다. 오늘만 세 번째였다. 랑글루아는 쪽지를 접어 주머니에 넣고 커피값을 치렀다. 총리에게 뭐라고 보고할지는 아직 정하지 못했다."),
    "lr_story.1017.a": "그들도 시민이다. 경찰은 보내지 마.",
    "lr_story.1017.b": "공장 문을 열게 해. 오늘 안으로.",
    # ----- 뉴스: 프랑스, 북독일에 선전포고 (뉴스 창은 약 450자까지)
    "lr_gnews.7.d": j(
        "프랑스가 북독일 연방에 선전포고했습니다. 파리 주재 북독일 대사는 오늘 오전 외무부에서 선전포고문을 전달받은 뒤 곧바로 동역으로 향한 것으로 알려졌습니다.",
        "프랑스 정부는 1918년 강화 조약의 군비 제한 조항을 더는 인정하지 않는다고 밝혔습니다. 알자스 국경 지대에서는 프랑스군의 대규모 이동이 목격되고 있으며, 스트라스부르 시청은 민간인 대피 계획을 발표했습니다. 라인강 다리 세 곳은 이미 통행이 막혔습니다.",
        "베를린은 제국연맹 회원국들에 조약 이행을 요구했습니다. 빈은 긴급 각료 회의를 소집했고, 런던은 아직 공식 입장을 내놓지 않았습니다."),
    "lr_gnews.7.a": "또 라인강인가.",
}


from styled_war import WAR  # noqa: E402
STYLED.update(WAR)

from styled_scenes import LAST  # noqa: E402
STYLED.update(LAST)

from styled_story_a import STORY as _STORY_A  # noqa: E402
STYLED.update(_STORY_A)

from styled_story_b import STORY as _STORY_B  # noqa: E402
STYLED.update(_STORY_B)

from styled_story_c import STORY as _STORY_C  # noqa: E402
STYLED.update(_STORY_C)

from styled_story_d import STORY as _STORY_D  # noqa: E402
STYLED.update(_STORY_D)

from styled_story_e import STORY as _STORY_E  # noqa: E402
STYLED.update(_STORY_E)
