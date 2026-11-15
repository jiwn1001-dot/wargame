"""Turn narration from 합쇼체 ("~합니다") into 해라체 ("~한다"), leaving quoted speech alone.

Used once on war_close.py; kept for the next batch of plain texts. Past and future forms convert safely; for
present-tense verbs a list of adjective stems keeps "많습니다" as "많다" rather than "많는다". Check the result by eye.
"""
import re

ADJECTIVE_STEMS = ("같", "많", "적", "좋", "싫", "높", "낮", "길", "짧", "깊", "넓", "좁", "늦", "작", "괜찮", "옳", "젊",
                   "크", "비싸", "싸", "다르", "어렵", "쉽", "멀", "가깝", "이르", "아프", "바쁘", "기쁘", "슬프", "예쁘", "나쁘", "무겁", "가볍", "춥", "덥")
HA_ADJECTIVES = ("중요", "필요", "분명", "확실", "충분", "유명", "조용", "이상", "가능", "위험", "행복", "친절", "정확", "비슷", "뻔", "빼곡", "가득", "선명", "희미", "엄격", "냉정", "막막", "캄캄", "축축", "멀쩡", "흔", "익숙", "수상", "초라", "화려", "요란", "한산",
                 "깨끗", "편안", "불편", "피곤", "간단", "복잡", "충실", "단단", "강", "약", "평온", "평화", "솔직", "당연")
VERB_I_STEMS = ("보", "펄럭", "붙", "먹", "속", "죽", "끓", "녹", "움직", "기울", "쌓", "반짝", "끄덕", "출렁", "깜빡", "놓", "쓰",
                "모", "숙", "덮", "섞", "끼", "줄어들", "번쩍", "흔들", "꺾", "높", "낮", "받아들", "기울", "망설", "번득", "글썽", "중얼", "머뭇", "꿈틀", "뒤척", "속삭", "헐떡", "두리번", "묶", "술렁", "들썩", "뒤섞", "웅성", "꿈틀")
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


# ===== The other way: 해라체 to 합쇼체, for focus descriptions (the user wants them polite) =====
SSANG_SIOT, NIEUN, RIEUL, BIEUP = 20, 4, 8, 17  # final-consonant indices
FORMAL_ADJECTIVES = ("크", "비싸", "싸", "다르", "이르", "아프", "바쁘", "기쁘", "슬프", "예쁘", "나쁘", "빠르", "느리", "흐리", "어리",
                     "아니", "고프", "그르", "바르", "푸르", "게으르", "서투르", "가쁘", "드세", "오래", "흔치")


def formal_word(word):
    """One sentence-final word in 해라체 ("한다", "했다", "크다", "땅이다") to 합쇼체 ("합니다", "했습니다", "큽니다", "땅입니다")."""
    if not word.endswith("다") or len(word) < 2:
        return word
    if word.endswith("니다") and len(word) >= 3 and "가" <= word[-3] <= "힣" and split(word[-3])[2] == BIEUP:
        return word  # already 합쇼체 (합니다, 습니다)
    stem = word[:-1]
    if stem.endswith("는") and len(stem) >= 2:          # 먹는다 -> 먹습니다
        return stem[:-1] + "습니다"
    last = stem[-1]
    if not "가" <= last <= "힣":
        return word
    lead, vowel, tail = split(last)
    if last == "이":                                    # 땅이다 -> 땅입니다, 아니다 handled below
        return stem[:-1] + "입니다"
    if tail == SSANG_SIOT:                              # 했다, 있다 -> 했습니다, 있습니다
        return stem + "습니다"
    if tail == NIEUN:                                   # 한다, 간다, 연다 -> 합니다, 갑니다, 엽니다
        return stem[:-1] + join(lead, vowel, BIEUP) + "니다"
    if tail == RIEUL:                                   # 길다, 멀다 -> 깁니다, 멉니다
        return stem[:-1] + join(lead, vowel, BIEUP) + "니다"
    if tail:                                            # 많다, 없다, 같다 -> 많습니다, 없습니다, 같습니다
        return stem + "습니다"
    # A bare vowel stem: in 해라체 a verb would read "-ㄴ다", so this is an adjective (크다 -> 큽니다) or a noun with the
    # copula shortened (이유다, 의회다 -> 이유입니다, 의회입니다).
    if last in "하되" and len(stem) >= 2:  # 필요하다, 위험하다 -> 필요합니다, 위험합니다
        return stem[:-1] + join(lead, vowel, BIEUP) + "니다"
    if stem in FORMAL_ADJECTIVES:  # the whole word, so 탱크다 stays a noun
        return stem[:-1] + join(lead, vowel, BIEUP) + "니다"
    return stem + "입니다"


def to_formal(text):
    """Every sentence that ends in "-다" becomes 합쇼체; fragments and quoted speech stay as they are."""
    import re
    out = []
    for part in re.split(r'(\\"[^"]*?\\")', text):
        if part.startswith('\\"'):
            out.append(part)
            continue
        out.append(re.sub(r"([가-힣]+다)(?=[.?!]|\s*$|\n)", lambda m: formal_word(m.group(1)), part))
    return "".join(out)
