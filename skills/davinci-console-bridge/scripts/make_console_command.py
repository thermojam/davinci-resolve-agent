#!/usr/bin/env python3
import argparse
from pathlib import Path


def make_command(target: Path) -> str:
    resolved = Path(target).expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"Resolve task script does not exist: {resolved}")
    path_literal = repr(str(resolved))
    return (
        f"p={path_literal}; "
        'g={"__file__":p,"__name__":"resolve_console_task","resolve":resolve}; '
        'exec(__import__("pathlib").Path(p).read_text(encoding="utf-8"),g); '
        'result=g["main"]()'
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a command for DaVinci Resolve Workspace > Console > Py3"
    )
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    print(make_command(args.target))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
