"""Command-line entry point for quick environment checks and smoke demos."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import sys
from pathlib import Path

import numpy as np

from .evaluation import entropy_topsis
from .sensitivity import one_at_a_time_sensitivity


OPTIONAL_PACKAGES = (
    "matplotlib",
    "networkx",
    "openpyxl",
    "scikit-learn",
    "scipy",
    "statsmodels",
)


def package_version(distribution: str) -> str:
    """Return an installed distribution version or a readable marker."""
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return "not installed"


def environment_report() -> dict[str, object]:
    """Build a non-sensitive report of the current modeling environment."""
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "executable": sys.executable,
        "required": {
            "numpy": package_version("numpy"),
            "pandas": package_version("pandas"),
        },
        "optional": {package: package_version(package) for package in OPTIONAL_PACKAGES},
    }


def run_demo(output_dir: Path) -> dict[str, object]:
    """Run dependency-light TOPSIS and sensitivity smoke examples."""
    output_dir.mkdir(parents=True, exist_ok=True)
    alternatives = np.array(
        [
            [82.0, 12.0, 0.91, 6.0],
            [76.0, 9.0, 0.95, 7.5],
            [88.0, 15.0, 0.87, 5.0],
            [79.0, 10.0, 0.93, 6.8],
        ]
    )
    weights, scores = entropy_topsis(
        alternatives,
        benefit_flags=[True, False, True, False],
    )

    def response(parameters: dict[str, float]) -> float:
        return parameters["a"] * 2.0**2 + parameters["b"] * 2.0 + parameters["c"]

    sensitivity = one_at_a_time_sensitivity(
        response,
        {"a": 2.0, "b": 1.5, "c": 5.0},
    )
    sensitivity.to_csv(output_dir / "sensitivity.csv", index=False, encoding="utf-8-sig")
    result = {
        "topsis": {
            "weights": weights.tolist(),
            "scores": scores.tolist(),
            "ranking_best_to_worst": (np.argsort(-scores) + 1).tolist(),
        },
        "sensitivity_rows": len(sensitivity),
    }
    (output_dir / "metrics.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cumcm-starter")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("check-env", help="Print installed package versions.")
    demo = subparsers.add_parser("demo", help="Run dependency-light smoke examples.")
    demo.add_argument("--out", type=Path, default=Path("demo_output"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "check-env":
        print(json.dumps(environment_report(), ensure_ascii=False, indent=2))
        return 0
    if args.command == "demo":
        result = run_demo(args.out)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    raise AssertionError("unreachable command")


if __name__ == "__main__":
    raise SystemExit(main())
