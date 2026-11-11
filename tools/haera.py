"""Turn narration from 합쇼체 ("~합니다") into 해라체 ("~한다"), leaving quoted speech alone.

Used once on war_close.py; kept for the next batch of plain texts. Past and future forms convert safely; for
present-tense verbs a list of adjective stems keeps "많습니다" as "많다" rather than "많는다". Check the result by eye.
"""
import re

ADJECTIVE_STEMS = ("같", "많", "적", "좋", "싫", "높", "낮", "길", "짧", "깊", "넓", "좁", "늦", "작", "괜찮", "옳", "젊",
                   "크", "비싸", "싸", "다르", "어렵", "쉽", "멀", "가깝", "이르", "아프", "바쁘", "기쁘", "슬프", "예쁘", "나쁘", "무겁", "가볍", "춥", "덥")
HA_ADJECTIVES = ("중요", "필요", "분명", "확실", "충분", "유명", "조용", "이상", "가능", "위험", "행복", "친절", "정확", "비슷",
                 "깨끗", "편안", "불편", "피곤", "간단", "복잡", "충실", "단단", "강", "약", "평온", "평화", "솔직", "당연")
VERB_I_STEMS = ("보", "펄럭", "붙", "먹", "속", "죽", "끓", "녹", "움직", "기울", "쌓", "반짝", "끄덕", "출렁", "깜빡", "놓", "쓰",
                "모", "숙", "덮", "섞", "끼", "줄어들", "번쩍", "흔들", "꺾", "높", "낮", "받아들", "기울")
BASE = 0xAC00


def split(ch):
    code = ord(ch) - BASE
    return code // 588, (code % 588) // 28, code % 28


def join(lead, vowel, tail):
    return chr(BASE + lead * 588 + vowel * 28 + tail)


def convert_word(word):
    """One sentence-final word ending in 니다."""
    if word.endswith("아닙니다"):
        return word[:-4] + "아니다"
    if word.endswith("입니다"):
        stem = word[:-3]
        if stem.endswith(VERB_I_STEMS):  # 보입니다 -> 보인다, 펄럭입니다 -> 펄럭인다
            return stem + "인다"
        # 편지입니다 -> 편지다, 사람입니다 -> 사람이다
        return stem + ("다" if stem and "가" <= stem[-1] <= "힣" and split(stem[-1])[2] == 0 else "이다")
    if word.endswith("합니다") and word[:-3].endswith(HA_ADJECTIVES):
        return word[:-3] + "하다"
    if word.endswith("습니다"):
        stem = word[:-3]
        last_tail = split(stem[-1])[2] if stem and "가" <= stem[-1] <= "힣" else 0
        if last_tail == 20 or stem.endswith(("있", "없")):  # ㅆ: past or future (했, 보냈, 겠)
            return stem + "다"
        if stem.endswith(ADJECTIVE_STEMS):
            return stem + "다"
        return stem + "는다"
    if word.endswith("니다") and len(word) >= 3:
        stem, last = word[:-2], word[-3]
        lead, vowel, tail = split(last)
        if tail == 17:  # ㅂ final: 갑 -> 가
            plain = stem[:-1] + join(lead, vowel, 0)
            if plain.endswith(ADJECTIVE_STEMS):
                return plain + "다"
            # verbs take ㄴ: 가 -> 간다; a stem already ending in ㄹ drops it: 만듭 -> 만든다
            return stem[:-1] + join(lead, vowel, 4) + "다"
    return word


def convert(text):
    parts = re.split(r'(\\".*?\\")', text)
    out = []
    for part in parts:
        if part.startswith('\\"'):
            out.append(part)
            continue
        out.append(re.sub(r"([가-힣]+니다)(?=[.?!,]|$)", lambda m: convert_word(m.group(1)), part))
    return "".join(out)
