"""How many lines each scene page takes in the event window (about 38 characters a line, 30 lines a page)."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
LINE, LIMIT = 38, 30


def lines(text):
    paras = text.replace('\\"', '"').split("\\n\\n")
    return sum(max(1, math.ceil(len(p) / LINE)) for p in paras) + len(paras) - 1


def report(name, text, limit=LIMIT):
    n = lines(text)
    flag = "  <-- too long" if n > limit else ""
    print(f"{name}: {len(text)} chars, {n} lines{flag}")
    return n <= limit


if __name__ == "__main__":
    import novel_text
    ok = True
    for event, scene in novel_text.NOVEL.items():
        for i, page in enumerate(scene["pages"], 1):
            ok &= report(f"{event} p{i}", page)
        ok &= report(f"{event} last", scene["last"])
    print("OK" if ok else "SOME PAGES TOO LONG")
