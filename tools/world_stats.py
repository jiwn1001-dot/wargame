"""Factories, dockyards and manpower per country at the 1936 start, after build_world's transfers.
python tools/world_stats.py [TAG ...]
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_world as world  # noqa: E402

KEYS = ("industrial_complex", "arms_factory", "dockyard")


def state_data():
    """state id -> (vanilla owner, buildings, manpower)."""
    data = {}
    for path in (world.VANILLA / "history" / "states").glob("*.txt"):
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        sid = int(re.search(r"\bid\s*=\s*(\d+)", text).group(1))
        head = re.split(r"\n\s*\d{4}\.\d+\.\d+\s*=", text)[0]  # ignore dated blocks
        owner = re.search(r"\bowner\s*=\s*(\w+)", head)
        manpower = re.search(r"\bmanpower\s*=\s*(\d+)", text)
        buildings = {k: int(m.group(1)) for k in KEYS if (m := re.search(rf"\b{k}\s*=\s*(\d+)", head))}
        data[sid] = (owner.group(1) if owner else None, buildings, int(manpower.group(1)) if manpower else 0)
    return data


def owners(data):
    owner = {sid: d[0] for sid, d in data.items()}
    for tag, states in world.TRANSFERS.items():
        for sid in states:
            owner[sid] = tag
    return owner


def totals():
    data = state_data()
    owner = owners(data)
    out = defaultdict(lambda: defaultdict(int))
    for sid, (_, buildings, manpower) in data.items():
        tag = owner.get(sid)
        if not tag:
            continue
        for k, v in buildings.items():
            out[tag][k] += v
        out[tag]["manpower"] += manpower
        out[tag]["states"] += 1
    return out, owner, data


if __name__ == "__main__":
    out, _, _ = totals()
    tags = sys.argv[1:] or sorted(out, key=lambda t: -(out[t]["industrial_complex"] + out[t]["arms_factory"]))[:30]
    print(f"{'tag':5}{'civ':>6}{'mil':>6}{'dock':>6}{'manpower(M)':>13}{'states':>8}")
    for t in tags:
        d = out[t]
        print(f"{t:5}{d['industrial_complex']:>6}{d['arms_factory']:>6}{d['dockyard']:>6}{d['manpower'] / 1e6:>13.1f}{d['states']:>8}")
