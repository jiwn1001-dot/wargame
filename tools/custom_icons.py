"""Drop-in pictures for focus icons and national spirits: python tools/custom_icons.py

Put a picture in docs/art and build; nobody has to edit a table.

Focus icons (docs/art/goals), most specific first:
    goals/LR_NAP_eagles.png                     that one focus
    goals/NAP/goal_generic_major_war.png        every Napoleon focus that now shows that vanilla icon
    goals/all/goal_generic_major_war.png        every French focus that now shows that vanilla icon
National spirits (docs/art/ideas):
    ideas/LR_dyn_ruler_emperor.png              a dynamic modifier or an idea, by its name

Pictures may be .png, .jpg or .webp of any size; they are trimmed, fitted and saved as .dds. Focus icons get the
same shine vanilla icons get. Run it after every tool that writes the focus tree, ideas or dynamic modifiers
(tools/build_all.py does). It also writes docs/art/icon_worklist.csv: every focus and spirit, what it shows now,
and the file names that would replace it.
"""
import csv
import re
import shutil

from PIL import Image

import build_world as world

MOD = world.MOD
ART = world.PROJECT / "docs" / "art"
FOCUS_FILE = MOD / "common" / "national_focus" / "france.txt"
SPIRIT_FILES = sorted((MOD / "common" / "dynamic_modifiers").glob("lr_*.txt")) + sorted((MOD / "common" / "ideas").glob("lr_*.txt"))
EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
GOAL_SIZE = (95, 95)  # the size of the mod's other focus icons
IDEA_SIZE = (60, 68)  # vanilla national spirit pictures
CUSTOM = "LRc"  # marks a sprite made here; the original vanilla icon follows "__" in its name

ROUTES = {"FRA": "공통", "ORL": "오를레앙", "BOU": "부르봉 왕정", "PET": "페탱", "NAP": "나폴레옹", "GUA": "공화국의 수호자",
          "RED": "붉은 나폴레옹", "JAC": "산악파", "GIR": "지롱드", "MAR": "푀양파", "COM": "코뮌", "ANA": "자유 코뮌 연합",
          "DEF": "패전"}
THEMES = {
    "goal_generic_major_war": "전쟁·진격", "goal_generic_national_unity": "국민 통합", "goal_generic_political_pressure": "정치 압박·탄압",
    "goal_generic_propaganda": "선전·연설", "goal_generic_improve_relations": "외교·우호", "goal_generic_major_alliance": "동맹",
    "goal_generic_demand_territory": "영토 요구·편입", "goal_generic_construct_civilian": "민간 건설", "goal_generic_army_doctrines": "육군 교리",
    "goal_generic_occupy_start_war": "점령·출병", "goal_generic_military_sphere": "군사 영향권", "goal_generic_allies_build_infantry": "보병·민병대",
    "goal_generic_positive_trade_relations": "무역 협정", "goal_generic_navy_doctrines_tactics": "해군 교리", "goal_generic_trade": "교역·금융",
    "goal_generic_special_forces": "특수 부대·근위대", "goal_generic_scientific_exchange": "학문·연구", "goal_generic_construct_civ_factory": "민간 공장",
    "goal_generic_fortify_city": "요새·방어", "goal_generic_forceful_treaty": "강압 조약", "goal_generic_construct_mil_factory": "군수 공장",
    "goal_generic_alliance": "협약", "goal_generic_production": "생산", "goal_generic_military_deal": "군사 협정",
    "goal_generic_intelligence_exchange": "정보·첩보", "goal_generic_dangerous_deal": "위험한 거래", "goal_generic_construct_naval_dockyard": "조선소",
    "goal_generic_army_artillery": "포병", "goal_generic_small_arms": "소총", "goal_generic_army_motorized": "차량화", "goal_generic_air_bomber": "폭격기",
    "goal_generic_radar": "레이더", "goal_generic_navy_submarine": "잠수함", "goal_generic_construction": "건설", "goal_generic_construct_infrastructure": "철도·도로",
    "goal_generic_build_tank": "전차 생산", "goal_generic_army_tanks": "기갑", "goal_generic_air_fighter": "전투기", "goal_generic_air_doctrine": "공군 교리",
}


def find(stem):
    for ext in EXTENSIONS:
        path = ART / f"{stem}{ext}"
        if path.exists():
            return path
    # An icon tools/icon_pictures.py made from a public-domain photograph (auto/goals/<id>, auto/ideas/<id>): asked
    # for last, after every picture drawn by hand, so hand-made art always wins.
    if stem.startswith("auto/"):
        auto = ART / f"{stem}.png"
        if auto.exists():
            return auto
    return None


def drop_background(picture):
    """Cut out a flat background (Gemini's green screen) from a picture that has no transparency."""
    if picture.getextrema()[3][0] < 255:
        return picture
    import numpy as np
    pixels = np.array(picture).astype(np.int16)
    h, w = pixels.shape[:2]
    border = np.concatenate([pixels[0], pixels[-1], pixels[:, 0], pixels[:, -1]])[:, :3]
    key = np.median(border, axis=0)
    close = np.abs(pixels[:, :, :3] - key).max(axis=2) < 70
    # only background reachable from the edges, so the same colour inside the icon survives
    seen = np.zeros_like(close)
    seen[0], seen[-1], seen[:, 0], seen[:, -1] = close[0], close[-1], close[:, 0], close[:, -1]
    while True:
        grown = seen.copy()
        grown[1:] |= seen[:-1]
        grown[:-1] |= seen[1:]
        grown[:, 1:] |= seen[:, :-1]
        grown[:, :-1] |= seen[:, 1:]
        grown &= close
        if (grown == seen).all():
            break
        seen = grown
    pixels[seen, 3] = 0
    # take the green cast off the edge pixels left next to the cut
    near = np.zeros_like(seen)
    for dy in (-2, -1, 0, 1, 2):
        for dx in (-2, -1, 0, 1, 2):
            near |= np.roll(np.roll(seen, dy, 0), dx, 1)
    edge = near & ~seen
    if key[1] > key[0] + 60 and key[1] > key[2] + 60:
        r, g, b = pixels[:, :, 0], pixels[:, :, 1], pixels[:, :, 2]
        g[edge] = np.minimum(g[edge], np.maximum(r[edge], b[edge]))
    return Image.fromarray(pixels.astype(np.uint8), "RGBA")


def fit(path, size, trim):
    picture = Image.open(path).convert("RGBA")
    picture.thumbnail((size[0] * 3, size[1] * 3), Image.LANCZOS)  # a Gemini picture is 1024 px; cut it out small
    picture = drop_background(picture)
    if trim and picture.getbbox():
        picture = picture.crop(picture.getbbox())
    picture.thumbnail(size, Image.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    canvas.paste(picture, ((size[0] - picture.width) // 2, (size[1] - picture.height) // 2), picture)
    return canvas


def original(sprite):
    """The vanilla icon behind a sprite, whether or not this tool already replaced it."""
    return sprite.split("__", 1)[1] if sprite.startswith(f"GFX_{CUSTOM}_") else sprite


def shine_template():
    shine = (world.VANILLA / "interface" / "goals_shine.gfx").read_text(encoding="utf-8-sig", errors="ignore")
    start = [m.start() for m in re.finditer(r"[sS]priteType\s*=\s*\{", shine[:shine.index('"GFX_goal_generic_national_unity_shine"')])][-1]
    end, depth = shine.index("{", start) + 1, 1
    while depth:
        depth += {"{": 1, "}": -1}.get(shine[end], 0)
        end += 1
    return shine[start:end]


def names():
    out = {}
    for path in (MOD / "localisation" / "korean").glob("*.yml"):
        out.update(re.findall(r'^\s*([\w.]+):\d* "(.*)"', path.read_text(encoding="utf-8-sig", errors="ignore"), re.M))
    return out


def focuses(rows, loc):
    text = FOCUS_FILE.read_text(encoding="utf-8")
    template = shine_template()
    folder = MOD / "gfx" / "interface" / "goals" / "custom"
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    made, plain, shining = {}, [], []

    def sprite_for(path, key, base):
        name = f"GFX_{CUSTOM}_{key}__{base}"
        if name not in made:
            dds = f"{key}__{base}.dds"
            fit(path, GOAL_SIZE, True).save(folder / dds)
            texture = f"gfx/interface/goals/custom/{dds}"
            plain.append(f'\tspriteType = {{\n\t\tname = "{name}"\n\t\ttexturefile = "{texture}"\n\t}}\n')
            shining.append("\t" + template.replace("GFX_goal_generic_national_unity_shine", f"{name}_shine")
                           .replace("gfx/interface/goals/goal_generic_national_unity.dds", texture) + "\n")
            made[name] = path
        return name

    def replace(match):
        fid, eol, sprite = match.group(1), match.group(2), match.group(3)
        base_sprite = original(sprite)
        base = base_sprite[4:]  # without GFX_
        prefix = fid[3:6]
        choices = [(f"goals/{fid}", fid), (f"goals/{prefix}/{base}", prefix), (f"goals/all/{base}", "all"), (f"auto/goals/{fid}", fid)]
        picked = next(((find(stem), key) for stem, key in choices if find(stem)), (None, None))
        new = sprite_for(picked[0], picked[1], base_sprite) if picked[0] else base_sprite
        rows.append(["중점", ROUTES.get(prefix, prefix), fid, loc.get(fid, ""), base, THEMES.get(base, ""),
                     f"goals/{fid}.png", f"goals/{prefix}/{base}.png", f"goals/all/{base}.png",
                     str(picked[0].relative_to(ART)).replace("\\", "/") if picked[0] else ""])
        return f"id = {fid}{eol}\t\ticon = {new}"

    text = re.sub(r"id = (LR_\w+)(\r?\n)\t\ticon = (GFX_\w+)", replace, text)
    FOCUS_FILE.write_text(text, encoding="utf-8")
    (MOD / "interface" / "lr_custom_goals.gfx").write_text("spriteTypes = {\n" + "".join(plain) + "}\n", encoding="utf-8")
    (MOD / "interface" / "lr_custom_goals_shine.gfx").write_text("spriteTypes = {\n" + "".join(shining) + "}\n", encoding="utf-8")
    return len(made)


def spirits(rows, loc):
    folder = MOD / "gfx" / "interface" / "ideas" / "custom"
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    sprites = []

    def make(name, base):
        """Write GFX_idea_LRc_<name>__<vanilla picture> when docs/art/ideas has a picture for it; return that path."""
        path = find(f"ideas/{name}") or find(f"auto/ideas/{name}")
        if path:
            fit(path, IDEA_SIZE, False).save(folder / f"{name}.dds")
            sprites.append(f'\tspriteType = {{\n\t\tname = "GFX_idea_{CUSTOM}_{name}__{base}"\n'
                           f'\t\ttexturefile = "gfx/interface/ideas/custom/{name}.dds"\n\t}}\n')
        rows.append(["국민정신", "", name, loc.get(name, ""), base, "", f"ideas/{name}.png", "", "",
                     str(path.relative_to(ART)).replace("\\", "/") if path else ""])
        return path

    def dynamic(match):
        # icon = GFX_idea_generic_x, or GFX_idea_LRc_<name>__GFX_idea_generic_x after an earlier run
        name, eol, icon = match.group(1), match.group(2), match.group(3)
        base = icon.split("__", 1)[1] if f"{CUSTOM}_" in icon else icon
        return f"{name} = {{{eol}\ticon = " + (f"GFX_idea_{CUSTOM}_{name}__{base}" if make(name, base) else base)

    def idea(match):
        # picture = generic_x (the game adds GFX_idea_), or LRc_<name>__generic_x after an earlier run
        name, body, picture = match.group(1), match.group(2), match.group(3)
        base = picture.split("__", 1)[1] if picture.startswith(f"{CUSTOM}_") else picture
        return f"\t\t{name} = {{{body}picture = " + (f"{CUSTOM}_{name}__{base}" if make(name, base) else base)

    for path in SPIRIT_FILES:
        raw = path.read_bytes()
        bom = raw.startswith(b"\xef\xbb\xbf")
        text = raw.decode("utf-8-sig")
        new = re.sub(r"^(\w+) = \{(\r?\n)\ticon = (GFX_\w+)", dynamic, text, flags=re.M)
        new = re.sub(r"^\t\t(\w+) = \{([^{}]*?)picture = (\w+)", idea, new, flags=re.M)
        if new != text:
            path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + new.encode("utf-8"))
    (MOD / "interface" / "lr_custom_ideas.gfx").write_text("spriteTypes = {\n" + "".join(sprites) + "}\n", encoding="utf-8")
    return len(sprites)


def write_guide(rows):
    """docs/art/ICONS.md: how to drop pictures in, and which pictures replace the most icons."""
    from collections import Counter, defaultdict
    focus = [r for r in rows if r[0] == "중점"]
    spirit = [r for r in rows if r[0] == "국민정신"]
    common = Counter(r[4] for r in focus)
    by_route = defaultdict(Counter)
    for r in focus:
        by_route[r[1]][r[4]] += 1
    done = sum(1 for r in rows if r[-1])
    out = [
        "# 중점 아이콘과 국민정신 그림",
        "",
        "`tools/custom_icons.py`가 만드는 문서입니다. 손으로 고치지 마세요.",
        "",
        "## 넣는 법",
        "",
        "그림을 아래 폴더에 이름만 맞춰 넣고 `python tools/build_all.py`(또는 `python tools/custom_icons.py`)를 돌립니다.",
        "크기는 상관없습니다. 여백은 잘라 내고 아이콘 크기에 맞춰 DDS로 바꿉니다. 배경이 투명한 PNG가 가장 깔끔합니다.",
        "",
        "| 넣을 곳 | 바뀌는 것 |",
        "|---|---|",
        "| `goals/중점ID.png` (예: `goals/LR_NAP_eagles.png`) | 그 중점 하나 |",
        "| `goals/루트/바닐라아이콘.png` (예: `goals/NAP/goal_generic_major_war.png`) | 그 루트에서 그 아이콘을 쓰는 중점 전부 |",
        "| `goals/all/바닐라아이콘.png` (예: `goals/all/goal_generic_major_war.png`) | 프랑스 중점 가운데 그 아이콘을 쓰는 것 전부 |",
        "| `ideas/정신ID.png` (예: `ideas/LR_dyn_ruler_emperor.png`) | 그 국민정신 하나 |",
        "",
        "위에 있는 것이 우선합니다. 그림을 지우고 다시 빌드하면 원래 아이콘으로 돌아갑니다.",
        "루트 폴더 이름: " + ", ".join(f"`{k}` {v}" for k, v in ROUTES.items()) + ".",
        "",
        f"지금 {len(rows)}개 가운데 {done}개가 바뀌어 있습니다. 하나하나의 목록은 `icon_worklist.csv`(엑셀로 열림)에 있습니다.",
        "",
        "## 가장 효과가 큰 그림 (공통 주제)",
        "",
        "한 장으로 많은 중점이 바뀝니다. 위에서부터 그리면 됩니다.",
        "",
        "| 중점 수 | 주제 | 넣을 파일 |",
        "|---|---|---|",
    ]
    out += [f"| {n} | {THEMES.get(icon, icon)} | `goals/all/{icon}.png` |" for icon, n in common.most_common() if n >= 3]
    out += ["", "## 루트별 주제", "", "루트마다 분위기를 다르게 하고 싶을 때 씁니다. 3개 이상 쓰는 것만 적었습니다.", ""]
    for route in ROUTES.values():
        icons = [(icon, n) for icon, n in by_route.get(route, Counter()).most_common() if n >= 3]
        if not icons:
            continue
        key = next(k for k, v in ROUTES.items() if v == route)
        out += [f"### {route} (`{key}`)", ""]
        out += [f"- {THEMES.get(icon, icon)} {n}개: `goals/{key}/{icon}.png`" for icon, n in icons]
        out.append("")
    out += ["## 국민정신", "", "| ID | 이름 |", "|---|---|"]
    out += [f"| `{r[2]}` | {r[3]} |" for r in spirit if r[3]]
    (ART / "ICONS.md").write_text("\n".join(out) + "\n", encoding="utf-8")


def main():
    for sub in ("goals", "goals/all", "ideas"):
        (ART / sub).mkdir(parents=True, exist_ok=True)
    loc = names()
    rows = []
    goal_count = focuses(rows, loc)
    idea_count = spirits(rows, loc)
    with open(ART / "icon_worklist.csv", "w", encoding="utf-8-sig", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["종류", "루트", "ID", "이름", "지금 아이콘", "주제", "개별 파일", "루트 주제 파일", "공통 주제 파일", "적용된 그림"])
        writer.writerows(rows)
    write_guide(rows)
    import gemini_prompts
    gemini_prompts.main()
    done = sum(1 for row in rows if row[-1])
    print(f"OK: {goal_count} focus pictures and {idea_count} spirit pictures; {done} of {len(rows)} icons replaced")


if __name__ == "__main__":
    main()
