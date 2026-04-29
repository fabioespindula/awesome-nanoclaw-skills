from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "awesome_skills.py"
SPEC = importlib.util.spec_from_file_location("awesome_skills", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AwesomeSkillsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.repo = self.base / "repo"
        self.skills_dir = self.base / "runtime" / "skills"
        (self.repo / "skills" / "demo").mkdir(parents=True)
        (self.repo / "skills" / "demo" / "SKILL.md").write_text("# Demo\nold\n")
        subprocess.run(["git", "init", "-b", "main"], cwd=self.repo, check=True, stdout=subprocess.PIPE)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.repo, check=True)
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=self.repo, check=True, stdout=subprocess.PIPE)
        self.first_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo, check=True, text=True, stdout=subprocess.PIPE).stdout.strip()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_cli(self, *args: str) -> dict[str, object]:
        code = MODULE.main(list(args))
        self.assertEqual(code, 0)
        # Direct unit tests call functions for result-sensitive checks.
        return {}

    def install_demo(self) -> dict[str, object]:
        args = type("Args", (), {
            "skill": "demo",
            "source_dir": str(self.repo),
            "skills_dir": str(self.skills_dir),
            "repo": str(self.repo),
            "branch": "main",
            "force": False,
        })()
        return MODULE.install_skill(args)

    def test_install_writes_default_auto_upgrade_metadata(self) -> None:
        result = self.install_demo()
        self.assertEqual(result["status"], "installed")
        metadata = json.loads((self.skills_dir / "demo" / ".awesome-skill.json").read_text())
        self.assertTrue(metadata["auto_upgrade"])
        self.assertTrue(metadata["update_check"])
        self.assertEqual(metadata["installed_commit"], self.first_commit)

    def test_check_reports_up_to_date_when_commit_matches(self) -> None:
        self.install_demo()
        args = type("Args", (), {
            "skill": "demo",
            "skills_dir": str(self.skills_dir),
            "source_dir": str(self.repo),
            "repo": None,
            "branch": None,
            "auto": True,
            "force": True,
        })()
        result = MODULE.check_skill(args)
        self.assertEqual(result["status"], "up_to_date")

    def test_check_auto_upgrades_and_creates_backup(self) -> None:
        self.install_demo()
        (self.repo / "skills" / "demo" / "SKILL.md").write_text("# Demo\nnew\n")
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-m", "update"], cwd=self.repo, check=True, stdout=subprocess.PIPE)
        latest = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo, check=True, text=True, stdout=subprocess.PIPE).stdout.strip()
        args = type("Args", (), {
            "skill": "demo",
            "skills_dir": str(self.skills_dir),
            "source_dir": str(self.repo),
            "repo": None,
            "branch": None,
            "auto": False,
            "force": True,
        })()
        result = MODULE.check_skill(args)
        self.assertEqual(result["status"], "upgraded")
        self.assertEqual((self.skills_dir / "demo" / "SKILL.md").read_text(), "# Demo\nnew\n")
        metadata = json.loads((self.skills_dir / "demo" / ".awesome-skill.json").read_text())
        self.assertEqual(metadata["installed_commit"], latest)
        backups = list((self.skills_dir / ".awesome-backups").glob("demo-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / "SKILL.md").read_text(), "# Demo\nold\n")

    def test_check_is_throttled_without_force(self) -> None:
        self.install_demo()
        args = type("Args", (), {
            "skill": "demo",
            "skills_dir": str(self.skills_dir),
            "source_dir": str(self.repo),
            "repo": None,
            "branch": None,
            "auto": True,
            "force": False,
        })()
        result = MODULE.check_skill(args)
        self.assertEqual(result["status"], "throttled")

    def test_validate_source_rejects_symlink(self) -> None:
        source = self.repo / "skills" / "bad"
        source.mkdir()
        (source / "SKILL.md").write_text("# Bad\n")
        (source / "link").symlink_to(self.repo / "skills" / "demo" / "SKILL.md")
        with self.assertRaisesRegex(MODULE.UpdaterError, "symlink"):
            MODULE.validate_source_skill(source)

    def test_config_can_disable_auto_upgrade(self) -> None:
        self.install_demo()
        args = type("Args", (), {
            "skill": "demo",
            "skills_dir": str(self.skills_dir),
            "set_values": ["auto_upgrade=false"],
        })()
        result = MODULE.config_skill(args)
        self.assertEqual(result["status"], "configured")
        metadata = json.loads((self.skills_dir / "demo" / ".awesome-skill.json").read_text())
        self.assertFalse(metadata["auto_upgrade"])


if __name__ == "__main__":
    unittest.main()
