"""Rebuild the whole mod in the right order: python tools/build_all.py

    python tools/build_all.py              everything
    python tools/build_all.py --from build_france
                                           start at one step (the steps before it are already up to date)
    python tools/build_all.py --only custom_icons check_mod
                                           just those steps

Each step is a tool in this folder. A step that fails because Windows briefly locked a file it writes (OSError 22,
usually an editor or the game holding it) is tried again; any other failure stops the build.
"""
import subprocess
import sys
import time
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
STEPS = [
    "build_world",        # states, owners and the selection map
    "build_economy",
    "build_france",       # France's focus tree, events, decisions, endings
    "build_events",       # world events, new countries, world characters
    "build_systems",
    "build_advisors",
    "build_debug",
    "build_portraits",    # pictures in docs/art -> leader portraits
    "leader_traits",      # route leaders' traits
    "build_diplomacy",    # recruits characters, clears vanilla diplomacy
    "build_bookmark",
    "power_struggle",
    "build_ai",           # an AI France's strategy (replaces vanilla's 1939 one)
    "build_super",        # super events, their pictures and songs
    "build_eventwindow",
    "icon_pictures",      # public-domain photographs -> icons for what has no picture yet (fetch with --fetch)
    "custom_icons",       # pictures in docs/art/goals and docs/art/ideas -> icons
    "news_pictures",      # docs/art/news candidates -> news event pictures (fetch with --fetch)
    "polish_text",        # house style over all localisation; keep it last among the writers
    "kr_provinces",       # cuts vanilla provinces along Kaiserreich's Ottoman borders (the mod's map files)
    "kr_layout",          # regroups the provinces into Kaiserreich's states and renumbers every state in the mod
    "check_layout",       # what in the map crashes a campaign at its start
    "check_mod",
    "check_gui",
]
RETRIES = 4


def run(step):
    for attempt in range(1, RETRIES + 1):
        result = subprocess.run([sys.executable, str(TOOLS / f"{step}.py")], cwd=TOOLS, capture_output=True,
                                text=True, encoding="utf-8", errors="replace", env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
        output = (result.stdout + result.stderr).strip()
        last = output.splitlines()[-1] if output else ""
        if result.returncode == 0:
            print(f"{step}: {last}")
            return True
        if ("Errno 22" in output or "4294967274" in output) and attempt < RETRIES:  # a file locked for a moment (ffmpeg says -22 too)
            print(f"{step}: a file was locked, trying again ({attempt})")
            time.sleep(2)
            continue
        print(f"{step}: FAILED\n{output[-2000:]}")
        return False
    return False


def game_running():
    """A game reading the mod while the build rewrites it can load half-written files and crash."""
    try:
        listing = subprocess.run(["tasklist", "/FI", "IMAGENAME eq hoi4.exe"], capture_output=True, text=True, errors="replace").stdout
    except OSError:
        return False
    return "hoi4.exe" in listing.lower()


def main():
    args = sys.argv[1:]
    if game_running() and "--force" not in args:
        raise SystemExit("Hearts of Iron IV is running: close it first (a game loading during the build can crash), "
                         "or add --force.")
    args = [a for a in args if a != "--force"]
    steps = STEPS
    if args[:1] == ["--from"]:
        steps = STEPS[STEPS.index(args[1]):]
    elif args[:1] == ["--only"]:
        steps = [s for s in STEPS if s in args[1:]]
    # The steps before kr_layout write on vanilla's state numbers, which only build_world restores, and kr_layout
    # must then renumber what they wrote: a partial build of writers takes both along.
    writers = STEPS[1:STEPS.index("kr_provinces")]
    if any(s in writers for s in steps):
        steps = [s for s in STEPS if s in steps or s in ("build_world", "kr_provinces", "kr_layout")]
    for step in steps:
        if not run(step):
            raise SystemExit(1)
    if game_running():
        print("WARNING: Hearts of Iron IV was started during the build and may have read half-written files. "
              "Close it and start it again.")
    else:
        print("Build finished: the game can be started now.")


if __name__ == "__main__":
    main()
