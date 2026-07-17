"""CLI entry point for the continuity tool.

Only --help and --version are implemented in this skeleton.
No business sub-commands are included.
"""

import argparse
import sys

import continuity


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="continuity",
        description="AI context continuity tool.",
        add_help=True,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=continuity.__version__,
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    """Entry point for both `continuity` and `python -m continuity`."""
    parser = _build_parser()
    try:
        parser.parse_args(argv)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
