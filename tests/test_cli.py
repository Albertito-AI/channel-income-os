from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def test_demo_generates_all_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "demo"
            env = dict(__import__("os").environ)
            env["PYTHONPATH"] = str(ROOT / "src")
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "channel_income_os",
                    "demo",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            for name in ["report.md", "dashboard.html", "action_queue.csv", "scorecard.json"]:
                path = output / name
                self.assertTrue(path.exists(), name)
                self.assertGreater(path.stat().st_size, 50, name)

    def test_missing_file_fails_cleanly(self) -> None:
        env = dict(__import__("os").environ)
        env["PYTHONPATH"] = str(ROOT / "src")
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "channel_income_os",
                "analyze",
                "--videos",
                "does-not-exist.csv",
            ],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("error:", completed.stderr)


if __name__ == "__main__":
    unittest.main()
