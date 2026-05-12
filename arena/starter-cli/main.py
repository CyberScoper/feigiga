#!/usr/bin/env python3
"""CLI стартер. Для задач "обработай файл / поток / API → выведи результат"."""

import argparse
import json
import sys
from pathlib import Path


def process(text: str) -> dict:
    """Замени на логику задачи."""
    return {
        "length": len(text),
        "lines": text.count("\n") + 1,
        "preview": text[:80],
    }


def main():
    p = argparse.ArgumentParser(description="Vibe Arena CLI")
    p.add_argument("input", nargs="?", help="файл или '-' для stdin")
    p.add_argument("-o", "--output", help="куда писать (по умолчанию stdout)")
    p.add_argument("--json", action="store_true", help="вывод как JSON")
    args = p.parse_args()

    if not args.input or args.input == "-":
        text = sys.stdin.read()
    else:
        text = Path(args.input).read_text(encoding="utf-8", errors="replace")

    result = process(text)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) if args.json else str(result)

    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
