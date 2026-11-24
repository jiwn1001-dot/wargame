"""Find the AI habits of docs/STYLE_GUIDE.md (section 5) in the mod's Korean text: python tools/text_lint.py [--top N] [--file NAME]

Looks at every lr_*.yml under mod/localisation/korean (the built text, after polish_text). Each text gets a score:
an epigram for a last line, stock phrases, lists of three, and scenes told in 합쇼체 where 해라체 belongs. The report
lists the worst texts first so they can be rewritten (in the styled_*.py tables, or america_*.py for America).
"""
import re
import sys
from collections import Counter
from pathlib import Path

MOD = Path(__file__).resolve().parent.parent / "mod"

# A last sentence that closes on a maxim rather than a fact.
EPIGRAM_END = [
    r"아무도 .{0,20}(않았|몰랐|없었|묻지)",
    r"^그것(이|은|만이|이야말로) .{0,30}(였다|이었다|입니다|였습니다|이다)",
    r"(뿐이었다|뿐이었습니다|뿐이다)$",
    r"(전부였다|전부입니다|전부였습니다)$",
    r"이름이 곧",
    r"(시작이었다|시작이었습니다|시작일 뿐)",
    r"(끝나지 않았다|끝나지 않았습니다)$",
    r"(알지 못했다|알지 못했습니다)$",
]
STOCK = ["그날 밤", "한참을 말없이", "아무도 묻지 않았", "가슴이 벅", "역사의 수레바퀴", "운명의 날", "새로운 시대가",
         "그 누구도", "침묵이 흘렀", "숨을 죽였", "역사는 기억", "결코 잊지", "모든 것이 바뀌었", "피할 수 없는"]
TRIPLET = re.compile(r"(?:^|[ \"])([가-힣]{1,6}), ([가-힣]{1,6}), (?:그리고 )?([가-힣]{1,6})(?:[와과이가을를의에도은는]|$|[ .])")
SCENE_KEYS = re.compile(r"^(lr_story|lr_novel|lr_usa|lr_france|lr_integration|lr_ending|lr_algeria|lr_peace|lr_world)\.\d+\.d")
NEWS_HINT = re.compile(r"(했습니다|밝혔습니다|알려졌습니다|보입니다|전했습니다)")


def sentences(text):
    flat = text.replace("\\n", " ").replace('\\"', '"')
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", flat) if s.strip()]


def score(key, text):
    found = []
    parts = sentences(text)
    if parts:
        last = parts[-1].rstrip(".!?\" ")
        for pattern in EPIGRAM_END:
            if re.search(pattern, last):
                found.append(f"경구 마무리: {last[-40:]}")
                break
    for phrase in STOCK:
        if phrase in text:
            found.append(f"상투구: {phrase}")
    for m in TRIPLET.finditer(text):
        found.append(f"셋씩 나열: {m.group(1)}, {m.group(2)}, {m.group(3)}")
    # The user's complaint (2026-11-24): "@@였다. @@는 없었다." Short flat assertions and negative closers, again
    # and again, read as machine prose.
    if len(text) > 200:
        flat = [s for s in parts if re.search(r"(였다|이었다|었다|았다|했다|였습니다|이었습니다)[.\"]?$", s) and len(s) <= 16]
        negative = [s for s in parts if re.search(r"(없었다|않았다|못했다|몰랐다|아니었다|없었습니다|않았습니다|못했습니다|아니었습니다)[.\"]?$", s)]
        paragraphs = [p for p in text.split("\\n\\n") if p.strip()]
        punch = [p for p in paragraphs if (ss := sentences(p)) and len(ss) > 1 and len(ss[-1]) <= 16]
        if len(flat) >= 2:
            found.append(f"짧은 단정문 {len(flat)}개: " + " / ".join(flat[:3]))
        if len(negative) >= 2:
            found.append(f"부정 마무리 {len(negative)}개: " + " / ".join(n[-18:] for n in negative[:3]))
        if len(punch) >= 2:
            found.append(f"문단 끝 한 줄 펀치 {len(punch)}개")
    if SCENE_KEYS.match(key) and len(text) > 300:
        formal = len(re.findall(r"습니다[.\"]", text))
        plain = len(re.findall(r"[었았였했]다[.\"]|[이]다[.\"]", text))
        if formal > plain and not NEWS_HINT.search(text[:120]):
            found.append(f"장면이 합쇼체: 습니다 {formal}, 다 {plain}")
    return found


def main():
    top = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 30
    only = sys.argv[sys.argv.index("--file") + 1] if "--file" in sys.argv else None
    results, per_file, kinds = [], Counter(), Counter()
    for path in sorted((MOD / "localisation" / "korean").glob("lr_*.yml")):
        if only and only not in path.name:
            continue
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            m = re.match(r'^\s*([\w.]+):\d*\s*"(.*)"\s*$', line)
            if not m:
                continue
            found = score(m.group(1), m.group(2))
            if found:
                results.append((len(found), path.name, m.group(1), found))
                per_file[path.name] += len(found)
                kinds.update(f.split(":")[0] for f in found)
    results.sort(key=lambda r: -r[0])
    print("== 파일별 ==")
    for name, n in per_file.most_common():
        print(f"{n:5d}  {name}")
    print("\n== 종류별 ==")
    for kind, n in kinds.most_common():
        print(f"{n:5d}  {kind}")
    print(f"\n== 가장 많이 걸린 {top}개 ==")
    for n, name, key, found in results[:top]:
        print(f"[{n}] {name} {key}")
        for f in found:
            print(f"      {f}")
    print(f"\n총 {sum(per_file.values())}건, {len(results)}개 텍스트")


if __name__ == "__main__":
    main()
