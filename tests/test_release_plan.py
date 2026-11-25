"""Exercise the release planner against a real repository and Actions outputs."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PLANNER = Path(__file__).resolve().parents[1] / ".github/scripts/release_plan.py"


class ReleasePlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.git("init", "-q")

    def git(self, *args):
        return subprocess.check_output(
            ["git", "-c", "user.name=CI", "-c", "user.email=ci@example.invalid", *args],
            cwd=self.repo, text=True,
        ).strip()

    def manifest(self, version, description="sample"):
        (self.repo / "pyproject.toml").write_text(
            f'[project]\nversion = "{version}"\ndescription = "{description}"\n',
            encoding="utf-8",
        )

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-qm", "fixture", "--allow-empty")
        return self.git("rev-parse", "HEAD")

    def plan(self, *, event="push", before="", publish=False, ref="refs/heads/main"):
        output = self.repo / ".git/step-output"
        output.write_text("", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(PLANNER)], cwd=self.repo, capture_output=True, text=True,
            env=dict(os.environ, GITHUB_EVENT_NAME=event, GITHUB_REF=ref,
                     BEFORE_SHA=before, REQUEST_PUBLICATION=str(publish).lower(),
                     GITHUB_OUTPUT=str(output)),
        )
        return result.returncode, output.read_text(encoding="utf-8")

    def test_unchanged_version_verifies_and_new_version_publishes(self):
        self.manifest("0.1.0")
        old = self.commit()
        self.manifest("0.1.0", "edited description")
        self.commit()
        self.assertEqual(self.plan(before=old), (0, "tag=v0.1.0\npublish=false\n"))
        self.manifest("0.1.1")
        self.assertEqual(self.plan(before=old), (0, "tag=v0.1.1\npublish=true\n"))

    def test_new_branch_and_first_manifest(self):
        empty = self.commit()
        self.manifest("0.1.0")
        for base in ("0" * 40, empty):
            with self.subTest(base=base):
                self.assertEqual(self.plan(before=base), (0, "tag=v0.1.0\npublish=true\n"))

    def test_unknown_push_base_fails_closed(self):
        self.manifest("0.1.0")
        for base in ("", "f" * 40):
            with self.subTest(base=base):
                status, outputs = self.plan(before=base)
                self.assertNotEqual(status, 0)
                self.assertEqual(outputs, "")

    def test_manual_publication_requires_explicit_intent_and_main(self):
        self.manifest("0.1.0")
        self.assertEqual(self.plan(event="workflow_dispatch"), (0, "tag=v0.1.0\npublish=false\n"))
        self.assertEqual(self.plan(event="workflow_dispatch", publish=True),
                         (0, "tag=v0.1.0\npublish=true\n"))
        status, outputs = self.plan(event="workflow_dispatch", publish=True, ref="refs/heads/topic")
        self.assertNotEqual(status, 0)
        self.assertEqual(outputs, "")
