import json
import tempfile
import unittest
from pathlib import Path

from cumcm_starter.cli import run_demo


class CliDemoTests(unittest.TestCase):
    def test_demo_writes_reproducible_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_dir = Path(temporary_directory)
            result = run_demo(output_dir)
            self.assertTrue((output_dir / "metrics.json").is_file())
            self.assertTrue((output_dir / "sensitivity.csv").is_file())
            parsed = json.loads((output_dir / "metrics.json").read_text(encoding="utf-8"))
            self.assertEqual(parsed, result)
            self.assertEqual(result["sensitivity_rows"], 6)


if __name__ == "__main__":
    unittest.main()

