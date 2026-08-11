import csv
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class RepositoryAssetTests(unittest.TestCase):
    def test_offline_guide_contains_expected_cards(self) -> None:
        guide = (REPOSITORY_ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertEqual(guide.count('cat:"'), 21)
        self.assertIn("2026 AI", guide)

    def test_source_catalog_is_substantive(self) -> None:
        with (REPOSITORY_ROOT / "docs" / "sources.csv").open(
            encoding="utf-8", newline=""
        ) as source_file:
            rows = list(csv.DictReader(source_file))
        self.assertGreaterEqual(len(rows), 30)
        required = {"title", "organization", "url", "accessed_at", "license_notes"}
        self.assertTrue(required.issubset(rows[0]))
        self.assertTrue(all(row["url"].startswith("https://") for row in rows))


if __name__ == "__main__":
    unittest.main()

