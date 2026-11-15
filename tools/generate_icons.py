"""Draw every French focus icon with an image API, one picture per focus: python tools/generate_icons.py

    python tools/generate_icons.py --dry-run                      how many are left and roughly what they cost
    python tools/generate_icons.py --limit 10                     the first ten (try the style first)
    python tools/generate_icons.py --route NAP                    one route (FRA ORL BOU PET NAP GUA RED JAC GIR MAR COM ANA DEF)
    python tools/generate_icons.py --reference docs/art/goals/LR_NAP_eagles.png
                                                                  match the style of a picture you liked
    python tools/generate_icons.py --redo LR_NAP_eagles LR_NAP_rhine
                                                                  draw these again, over the old pictures

The key comes from the environment, never from a file: GEMINI_API_KEY (--provider gemini, the default) or
OPENAI_API_KEY (--provider openai). Pictures go to docs/art/goals/<focus id>.png; a focus that already has one
is skipped, so a run can be stopped and started again. Then build (custom_icons) as usual: the green background
is cut out and the picture is fitted to the icon.
"""
import argparse
import base64
import csv
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import requests

import custom_icons as icons
import gemini_prompts

GOALS = icons.ART / "goals"
CODES = {name: code for code, name in icons.ROUTES.items()}
# rough dollars per picture, only for the --dry-run estimate; check the provider's price page
PRICES = {"gemini": 0.04, "openai": 0.04}
DEFAULT_MODELS = {"gemini": "gemini-2.5-flash-image", "openai": "gpt-image-1.5"}

SETTING = """National focus icon for a Hearts of Iron IV mod set in an alternate 1936: France lost the Great War in 1918,
and a beaten, half-ruined France now chooses between a restored king, a new Napoleon, a republic or a commune."""

STYLE = """Style: exactly like the vanilla Hearts of Iron IV national focus icons.
- One clear object or emblem, centred, filling about 80% of the square, seen slightly from three-quarters above.
- Painted, semi-realistic, crisp dark outlines, soft light from the top left, a small drop shadow under the object.
- Muted, slightly desaturated 1930s colours (brass, steel, olive, navy, parchment, dark red).
- Readable at 95 x 95 pixels: big simple shapes, no fine detail, no crowds or tiny figures.
- No text, letters, numbers, captions or signatures. No border, frame, round badge or vignette.
- Square image."""

BACKGROUND = {
    "gemini": "- Background: one flat pure green (#00FF00) and nothing else, so it can be cut out. Never use that green in the object.",
    "openai": "- Transparent background, nothing behind the object.",
}

SYMBOLS = {
    "ORL": "the tricolour with a royal crown (the Orléans July Monarchy)",
    "BOU": "the white Bourbon flag with golden fleurs-de-lis",
    "PET": "the francisque double axe and the tricolour (Pétain's État français)",
    "NAP": "the golden imperial eagle, bees and the tricolour",
    "GUA": "the tricolour and the imperial eagle under a republican laurel",
    "RED": "the red flag together with the Napoleonic eagle",
    "JAC": "the Phrygian cap, pikes and the tricolour (radical Jacobin republic)",
    "GIR": "Marianne and the tricolour (moderate republic)",
    "MAR": "Marianne and the tricolour (liberal constitutional republic)",
    "COM": "the red flag (the Paris Commune, communist)",
    "ANA": "the black-and-red flag (anarchist commune)",
    "DEF": "the tricolour, worn and torn (a beaten France)",
    "FRA": "the tricolour",
}


def pending(route=None, redo=()):
    loc = icons.names()
    with open(icons.ART / "icon_worklist.csv", encoding="utf-8-sig") as source:
        rows = [row for row in csv.DictReader(source) if row["종류"] == "중점"]
    out = []
    for row in rows:
        code = CODES.get(row["루트"], "FRA")
        if redo:
            if row["ID"] not in redo:
                continue
        elif any((GOALS / f"{row['ID']}{ext}").exists() for ext in icons.EXTENSIONS):
            continue
        if route and code != route:
            continue
        out.append({"id": row["ID"], "code": code, "route": row["루트"], "name": row["이름"],
                    "desc": gemini_prompts.short(loc.get(f"{row['ID']}_desc", ""), 400)})
    return out


def prompt(focus, provider):
    return "\n\n".join([
        SETTING,
        f"Focus: \"{focus['name']}\" (route: {focus['route']}).\nWhat it is about (Korean): {focus['desc'] or focus['name']}",
        "Draw the single object or emblem that best stands for this focus. Pick something concrete and specific to it "
        "(a document, a weapon, a building, a tool, a uniform piece, a flag), not a generic soldier.",
        f"Use where it fits: {SYMBOLS[focus['code']]}.",
        STYLE + "\n" + BACKGROUND[provider],
    ])


def gemini(focus, key, model, reference):
    parts = [{"text": prompt(focus, "gemini")}]
    if reference:
        parts.append({"text": "Match the drawing style of this example icon exactly (not its subject):"})
        parts.append({"inline_data": {"mime_type": "image/png", "data": reference}})
    reply = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={"x-goog-api-key": key},
        json={"contents": [{"parts": parts}],
              "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "1:1"}}},
        timeout=180)
    reply.raise_for_status()
    for candidate in reply.json().get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            data = part.get("inlineData") or part.get("inline_data")
            if data:
                return base64.b64decode(data["data"])
    raise RuntimeError(f"no picture in the reply: {reply.text[:300]}")


def openai(focus, key, model, reference):
    headers = {"Authorization": f"Bearer {key}"}
    fields = {"model": model, "prompt": prompt(focus, "openai"), "size": "1024x1024", "quality": "medium",
              "background": "transparent", "output_format": "png"}
    if reference:
        fields["prompt"] += "\n\nMatch the drawing style of the attached example icon exactly (not its subject)."
        files = [("image[]", ("reference.png", base64.b64decode(reference), "image/png"))]
        reply = requests.post("https://api.openai.com/v1/images/edits", headers=headers, data=fields, files=files, timeout=300)
    else:
        reply = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=fields, timeout=300)
    reply.raise_for_status()
    return base64.b64decode(reply.json()["data"][0]["b64_json"])


def draw(focus, args, key, reference):
    call = gemini if args.provider == "gemini" else openai
    for attempt in range(5):
        try:
            picture = call(focus, key, args.model, reference)
            (GOALS / f"{focus['id']}.png").write_bytes(picture)
            return f"OK   {focus['id']} ({focus['name']})"
        except requests.HTTPError as error:
            status = error.response.status_code
            if status in (429, 500, 502, 503, 504) and attempt < 4:
                time.sleep(10 * 2 ** attempt)
                continue
            return f"FAIL {focus['id']}: HTTP {status} {error.response.text[:200]}"
        except Exception as error:  # a reply without a picture (refused, cut off): try again a couple of times
            if attempt < 2:
                continue
            return f"FAIL {focus['id']}: {error}"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--provider", choices=("gemini", "openai"), default="gemini")
    parser.add_argument("--model")
    parser.add_argument("--route", choices=sorted(icons.ROUTES))
    parser.add_argument("--limit", type=int)
    parser.add_argument("--redo", nargs="+", default=())
    parser.add_argument("--reference")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--show-prompt", action="store_true", help="print the first prompt and stop")
    args = parser.parse_args()
    args.model = args.model or DEFAULT_MODELS[args.provider]

    todo = pending(args.route, set(args.redo))
    if args.limit:
        todo = todo[:args.limit]
    if args.show_prompt:
        print(prompt(todo[0], args.provider) if todo else "nothing left")
        return
    cost = len(todo) * PRICES[args.provider]
    print(f"{len(todo)} focus icons to draw with {args.provider} ({args.model}), roughly ${cost:.0f}")
    if args.dry_run or not todo:
        return
    key = os.environ.get("GEMINI_API_KEY" if args.provider == "gemini" else "OPENAI_API_KEY")
    if not key:
        sys.exit(f"set {'GEMINI_API_KEY' if args.provider == 'gemini' else 'OPENAI_API_KEY'} first")
    reference = base64.b64encode(open(args.reference, "rb").read()).decode() if args.reference else None

    GOALS.mkdir(parents=True, exist_ok=True)
    failed = 0
    with ThreadPoolExecutor(args.workers) as pool:
        for done, line in enumerate(pool.map(lambda focus: draw(focus, args, key, reference), todo), 1):
            failed += line.startswith("FAIL")
            print(f"[{done}/{len(todo)}] {line}", flush=True)
    print(f"Done: {len(todo) - failed} drawn, {failed} failed. Build with: python tools/build_all.py --only custom_icons check_mod")


if __name__ == "__main__":
    main()
