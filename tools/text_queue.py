"""The next texts to rewrite for docs/STYLE_GUIDE.md section 9: python tools/text_queue.py [N] [OUT]

Lists the worst-scoring texts (text_lint.py's choppy-sentence checks) that prose_fr.py has not rewritten yet, with
their full current text, so a batch can be rewritten in one go. Writes to OUT (default: stdout).
"""
import io
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import text_lint  # noqa: E402
from prose_fr import PROSE_FR  # noqa: E402

MOD = Path(__file__).resolve().parent.parent / "mod"
CHOPPY = ("짧은 단정문", "부정 마무리", "문단 끝 한 줄 펀치", "경구 마무리")


def queue():
    items = []
    for path in sorted((MOD / "localisation" / "korean").glob("lr_*.yml")):
        if "usa" in path.name:
            continue
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            m = re.match(r'^\s*([\w.]+):\d*\s*"(.*)"\s*$', line)
            if not m or m.group(1) in PROSE_FR:
                continue
            found = [f for f in text_lint.score(m.group(1), m.group(2)) if f.startswith(CHOPPY)]
            counts = [re.search(r"(\d+)개", f) for f in found]
            weight = sum(int(c.group(1)) if c else 1 for c in counts)
            if weight >= 3:
                items.append((weight, path.name, m.group(1), m.group(2)))
    items.sort(key=lambda r: -r[0])
    return items


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    out = open(sys.argv[2], "w", encoding="utf-8") if len(sys.argv) > 2 else io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    items = queue()
    out.write(f"# {len(items)} texts left\n\n")
    for weight, name, key, text in items[:n]:
        out.write(f"=== {key}  [{weight}] {name}\n{text.replace(chr(92) + 'n' + chr(92) + 'n', chr(10) + chr(10)).replace(chr(92) + chr(34), chr(34))}\n\n")


if __name__ == "__main__":
    main()
