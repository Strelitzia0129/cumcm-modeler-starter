"""Offline repository audit used locally and in CI."""

from __future__ import annotations

import ast
import csv
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "CITATION.cff",
    "pyproject.toml",
    "docs/index.html",
    "docs/sources.csv",
    ".github/workflows/ci.yml",
    ".github/workflows/pages.yml",
)
MARKDOWN_FILES = (
    "README.md",
    "README.en.md",
    "CONTRIBUTING.md",
    "SUPPORT.md",
    "THIRD_PARTY_NOTICES.md",
)


def fail(message: str) -> None:
    print(f"[FAIL] {message}")


def main() -> int:
    failures = 0
    for relative_path in REQUIRED_FILES:
        if not (ROOT / relative_path).is_file():
            fail(f"missing required file: {relative_path}")
            failures += 1

    guide_path = ROOT / "docs" / "index.html"
    if guide_path.is_file():
        guide = guide_path.read_text(encoding="utf-8")
        card_count = guide.count('cat:"')
        if card_count != 21:
            fail(f"expected 21 algorithm cards, found {card_count}")
            failures += 1
        for link in re.findall(r'href="([^"]+)"', guide):
            if link.startswith(("http://", "https://", "#")) or "${" in link:
                continue
            target = (guide_path.parent / link).resolve()
            if not target.is_file():
                fail(f"broken local guide link: {link}")
                failures += 1

    sources_path = ROOT / "docs" / "sources.csv"
    if sources_path.is_file():
        with sources_path.open(encoding="utf-8", newline="") as source_file:
            source_rows = list(csv.DictReader(source_file))
        if len(source_rows) < 30:
            fail(f"source catalog is too small: {len(source_rows)} rows")
            failures += 1
        for row_number, row in enumerate(source_rows, start=2):
            if not row.get("url", "").startswith("https://"):
                fail(f"source row {row_number} does not use HTTPS")
                failures += 1

    for relative_path in MARKDOWN_FILES:
        markdown_path = ROOT / relative_path
        if not markdown_path.is_file():
            fail(f"missing Markdown file: {relative_path}")
            failures += 1
            continue
        markdown = markdown_path.read_text(encoding="utf-8")
        for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", markdown):
            link = link.strip("<>").split("#", maxsplit=1)[0]
            if not link or link.startswith(("http://", "https://", "mailto:")):
                continue
            target = (markdown_path.parent / link).resolve()
            if not target.exists():
                fail(f"broken local Markdown link in {relative_path}: {link}")
                failures += 1

    for python_path in list((ROOT / "src").rglob("*.py")) + list(
        (ROOT / "examples").rglob("*.py")
    ):
        try:
            ast.parse(python_path.read_text(encoding="utf-8"), filename=str(python_path))
        except SyntaxError as error:
            fail(f"Python syntax error in {python_path.relative_to(ROOT)}: {error}")
            failures += 1

    if failures:
        print(f"Repository audit finished with {failures} failure(s).")
        return 1
    print("Repository audit passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
