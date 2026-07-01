#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import shutil


RESOLVE_APP = Path("/Applications/DaVinci Resolve/DaVinci Resolve.app")
API_ROOT = Path(
    "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
)
API_README = API_ROOT / "README.txt"
API_MODULE = API_ROOT / "Modules" / "DaVinciResolveScript.py"
FALLBACK_TOOL_DIRS = (Path("/opt/homebrew/bin"), Path("/usr/local/bin"))


def find_tool(name: str):
    discovered = shutil.which(name)
    if discovered:
        return Path(discovered)
    for directory in FALLBACK_TOOL_DIRS:
        candidate = directory / name
        if candidate.is_file():
            return candidate
    return None


def check_environment(target=None):
    target_path = Path(target).expanduser().resolve() if target is not None else None
    ffmpeg = find_tool("ffmpeg")
    ffprobe = find_tool("ffprobe")
    return {
        "target": str(target_path) if target_path else None,
        "target_exists": target_path.is_file() if target_path else None,
        "resolve_app": RESOLVE_APP.is_dir(),
        "resolve_api_readme": API_README.is_file(),
        "resolve_api_module": API_MODULE.is_file(),
        "ffmpeg": str(ffmpeg) if ffmpeg else None,
        "ffprobe": str(ffprobe) if ffprobe else None,
        "connection_mode": "embedded Py3 Console",
    }


def main():
    parser = argparse.ArgumentParser(description="Check local DaVinci prerequisites")
    parser.add_argument("target", nargs="?", type=Path)
    args = parser.parse_args()
    report = check_environment(args.target)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    required = (
        report["resolve_app"],
        report["resolve_api_readme"],
        report["resolve_api_module"],
        report["ffmpeg"],
        report["ffprobe"],
    )
    if args.target is not None:
        required += (report["target_exists"],)
    return 0 if all(required) else 1


if __name__ == "__main__":
    raise SystemExit(main())
