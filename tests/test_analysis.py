from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from channel_income_os.analysis import analyze
from channel_income_os.ingest import apply_rights_registry, load_summary, load_videos


ROOT = Path(__file__).resolve().parents[1]


class AnalysisTests(unittest.TestCase):
    def setUp(self) -> None:
        self.videos = load_videos(ROOT / "sample_data" / "videos.csv")
        apply_rights_registry(self.videos, ROOT / "sample_data" / "rights_registry.csv")
        self.summary, self.warnings = load_summary(
            ROOT / "sample_data" / "channel_summary.csv",
            self.videos,
            "USD",
        )
        self.report = analyze(self.videos, self.summary, 10000.0, 25)

    def test_loads_synthetic_catalogue(self) -> None:
        self.assertEqual(len(self.videos), 12)
        self.assertEqual(self.summary.views, 14500)
        self.assertAlmostEqual(self.summary.estimated_revenue, 17.90)

    def test_target_math_is_explicit(self) -> None:
        expected_rpm = 17.90 / 14500 * 1000
        self.assertAlmostEqual(self.report["effective_rpm"], expected_rpm)
        self.assertAlmostEqual(
            self.report["views_required_at_current_rpm"],
            10000 / expected_rpm * 1000,
        )

    def test_rights_hold_has_highest_control_priority(self) -> None:
        item = next(x for x in self.report["action_queue"] if x["video_id"] == "vid004")
        self.assertEqual(item["code"], "RIGHTS_HOLD")
        self.assertEqual(item["priority"], 100.0)

    def test_low_sample_rpm_outlier_is_audited(self) -> None:
        item = next(x for x in self.report["action_queue"] if x["video_id"] == "vid008")
        self.assertEqual(item["code"], "REVENUE_AUDIT")

    def test_learning_retention_signal_is_preserved(self) -> None:
        self.assertGreater(
            self.report["learning"]["retention_ratio"],
            self.report["other"]["retention_ratio"],
        )


if __name__ == "__main__":
    unittest.main()
