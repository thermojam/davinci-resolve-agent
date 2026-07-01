from pathlib import Path
import shutil
import sys


def tool_path(name: str) -> Path:
    discovered = shutil.which(name)
    if discovered:
        return Path(discovered)
    for directory in (Path("/opt/homebrew/bin"), Path("/usr/local/bin")):
        candidate = directory / name
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"required tool is not installed: {name}")


def connect_resolve():
    embedded_resolve = globals().get("resolve")
    if embedded_resolve is None:
        raise RuntimeError(
            "Run this task from DaVinci Resolve Workspace > Console > embedded Py3 Console"
        )
    return embedded_resolve


def run(resolve):
    del resolve
    raise NotImplementedError("Implement only after the production plan is approved")


def main() -> int:
    try:
        return int(run(connect_resolve()) or 0)
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
