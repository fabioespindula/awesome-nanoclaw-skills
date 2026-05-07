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

    def write_source_skill(self, name: str, content: str) -> None:
        source = self.repo / "skills" / name
        source.mkdir(parents=True, exist_ok=True)
        (source / "SKILL.md").write_text(content)

    def commit_repo(self, message: str) -> str:
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-m", message], cwd=self.repo, check=True, stdout=subprocess.PIPE)
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo, check=True, text=True, stdout=subprocess.PIPE).stdout.strip()

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
        self.assertEqual(metadata["metadata_version"], 2)
        self.assertEqual(metadata["hash_algorithm"], "sha256")
        self.assertRegex(metadata["installed_hash"], r"^[0-9a-f]{64}$")
        self.assertEqual(metadata["last_seen_hash"], metadata["installed_hash"])
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
        self.assertFalse(result["changed"])
        self.assertFalse(result["would_upgrade"])

    def test_check_ignores_repo_commit_when_skill_hash_is_unchanged(self) -> None:
        self.install_demo()
        self.write_source_skill("other", "# Other\n")
        latest = self.commit_repo("change unrelated skill")
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
        self.assertFalse(result["changed"])
        self.assertFalse(result["would_upgrade"])
        self.assertEqual(result["latest_commit"], latest)
        self.assertEqual(result["installed_hash"], result["latest_hash"])
        self.assertFalse((self.skills_dir / ".awesome-backups").exists())

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
        self.assertEqual(metadata["metadata_version"], 2)
        self.assertEqual(metadata["installed_hash"], result["installed_hash"])
        backups = list((self.skills_dir / ".awesome-backups").glob("demo-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / "SKILL.md").read_text(), "# Demo\nold\n")

    def test_check_dry_run_reports_upgrade_without_writing(self) -> None:
        self.install_demo()
        metadata_path = self.skills_dir / "demo" / ".awesome-skill.json"
        before_metadata = metadata_path.read_text()
        (self.repo / "skills" / "demo" / "SKILL.md").write_text("# Demo\nnew\n")
        latest = self.commit_repo("update demo dry-run")
        args = type("Args", (), {
            "skill": "demo",
            "skills_dir": str(self.skills_dir),
            "source_dir": str(self.repo),
            "repo": None,
            "branch": None,
            "auto": True,
            "force": True,
            "dry_run": True,
        })()
        result = MODULE.check_skill(args)
        self.assertEqual(result["status"], "update_available")
        self.assertTrue(result["changed"])
        self.assertTrue(result["would_upgrade"])
        self.assertEqual(result["latest_commit"], latest)
        self.assertEqual((self.skills_dir / "demo" / "SKILL.md").read_text(), "# Demo\nold\n")
        self.assertEqual(metadata_path.read_text(), before_metadata)
        self.assertFalse((self.skills_dir / ".awesome-backups").exists())

    def test_check_migrates_v1_metadata_idempotently(self) -> None:
        self.install_demo()
        metadata_path = self.skills_dir / "demo" / ".awesome-skill.json"
        metadata = json.loads(metadata_path.read_text())
        for key in ("metadata_version", "hash_algorithm", "installed_hash", "last_seen_hash"):
            metadata.pop(key, None)
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
        args = type("Args", (), {
            "skill": "demo",
            "skills_dir": str(self.skills_dir),
            "source_dir": str(self.repo),
            "repo": None,
            "branch": None,
            "auto": True,
            "force": True,
        })()
        first = MODULE.check_skill(args)
        second = MODULE.check_skill(args)
        migrated = json.loads(metadata_path.read_text())
        self.assertEqual(first["status"], "up_to_date")
        self.assertEqual(second["status"], "up_to_date")
        self.assertEqual(migrated["metadata_version"], 2)
        self.assertEqual(migrated["hash_algorithm"], "sha256")
        self.assertRegex(migrated["installed_hash"], r"^[0-9a-f]{64}$")
        self.assertEqual(migrated["installed_hash"], migrated["last_seen_hash"])

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

    def test_skill_content_hash_detects_renames_and_binary_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "skill"
            (skill / "docs").mkdir(parents=True)
            (skill / "SKILL.md").write_text("# Demo\n", encoding="utf-8")
            binary = skill / "docs" / "sample.bin"
            binary.write_bytes(b"\x00\x01\x02")
            original = MODULE.skill_content_hash(skill)
            manifest = MODULE.skill_content_hash(skill, include_manifest=True)
            self.assertEqual(manifest["hash"], original)
            self.assertEqual([item["path"] for item in manifest["files"]], ["SKILL.md", "docs/sample.bin"])

            binary.rename(skill / "docs" / "renamed.bin")
            renamed = MODULE.skill_content_hash(skill)
            self.assertNotEqual(original, renamed)

            (skill / "docs" / "renamed.bin").write_bytes(b"\x00\x01\x03")
            changed_binary = MODULE.skill_content_hash(skill)
            self.assertNotEqual(renamed, changed_binary)

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

    def test_discover_installs_new_source_skills(self) -> None:
        self.install_demo()
        self.write_source_skill("new-skill", "# New Skill\n")
        latest = self.commit_repo("add new skill")
        args = type("Args", (), {
            "skills_dir": str(self.skills_dir),
            "source_dir": str(self.repo),
            "repo": str(self.repo),
            "branch": "main",
            "auto": True,
            "force": True,
        })()
        result = MODULE.discover_skills(args)
        self.assertEqual(result["status"], "discovered")
        self.assertIn("new-skill", result["installed"])
        self.assertEqual((self.skills_dir / "new-skill" / "SKILL.md").read_text(), "# New Skill\n")
        metadata = json.loads((self.skills_dir / "new-skill" / ".awesome-skill.json").read_text())
        self.assertEqual(metadata["installed_commit"], latest)
        self.assertTrue(metadata["discover_new"])

    def test_discover_checks_existing_managed_skills(self) -> None:
        self.install_demo()
        (self.repo / "skills" / "demo" / "SKILL.md").write_text("# Demo\nnew\n")
        latest = self.commit_repo("update demo")
        args = type("Args", (), {
            "skills_dir": str(self.skills_dir),
            "source_dir": str(self.repo),
            "repo": str(self.repo),
            "branch": "main",
            "auto": True,
            "force": True,
        })()
        result = MODULE.discover_skills(args)
        self.assertEqual(result["status"], "discovered")
        self.assertEqual((self.skills_dir / "demo" / "SKILL.md").read_text(), "# Demo\nnew\n")
        checked = {item["skill"]: item for item in result["checked"]}
        self.assertEqual(checked["demo"]["status"], "upgraded")
        self.assertEqual(checked["demo"]["previous_commit"], self.first_commit)
        self.assertEqual(checked["demo"]["installed_commit"], latest)

    def test_discover_skips_unchanged_hashes_even_when_repo_commit_changed(self) -> None:
        self.install_demo()
        self.write_source_skill("other", "# Other\n")
        latest = self.commit_repo("change only other skill")
        args = type("Args", (), {
            "skills_dir": str(self.skills_dir),
            "source_dir": str(self.repo),
            "repo": str(self.repo),
            "branch": "main",
            "auto": True,
            "force": True,
        })()
        result = MODULE.discover_skills(args)
        checked = {item["skill"]: item for item in result["checked"]}
        self.assertEqual(checked["demo"]["status"], "up_to_date")
        self.assertEqual(checked["demo"]["latest_commit"], latest)
        self.assertFalse((self.skills_dir / ".awesome-backups").exists())

    def test_discover_dry_run_reports_without_writing(self) -> None:
        self.install_demo()
        before_metadata = (self.skills_dir / "demo" / ".awesome-skill.json").read_text()
        (self.repo / "skills" / "demo" / "SKILL.md").write_text("# Demo\nnew\n")
        self.write_source_skill("new-skill", "# New Skill\n")
        self.commit_repo("discover dry-run changes")
        args = type("Args", (), {
            "skills_dir": str(self.skills_dir),
            "source_dir": str(self.repo),
            "repo": str(self.repo),
            "branch": "main",
            "auto": True,
            "force": True,
            "dry_run": True,
        })()
        result = MODULE.discover_skills(args)
        checked = {item["skill"]: item for item in result["checked"]}
        self.assertEqual(checked["demo"]["status"], "update_available")
        self.assertTrue(checked["demo"]["would_upgrade"])
        self.assertIn("new-skill", result["would_install"])
        self.assertFalse((self.skills_dir / "new-skill").exists())
        self.assertEqual((self.skills_dir / "demo" / "SKILL.md").read_text(), "# Demo\nold\n")
        self.assertEqual((self.skills_dir / "demo" / ".awesome-skill.json").read_text(), before_metadata)
        self.assertFalse((self.skills_dir / ".awesome-backups").exists())

    def test_discover_respects_disabled_auto_upgrade_without_auto_flag(self) -> None:
        self.install_demo()
        config_args = type("Args", (), {
            "skill": "demo",
            "skills_dir": str(self.skills_dir),
            "set_values": ["auto_upgrade=false"],
        })()
        MODULE.config_skill(config_args)
        (self.repo / "skills" / "demo" / "SKILL.md").write_text("# Demo\nnew\n")
        latest = self.commit_repo("update demo disabled")
        args = type("Args", (), {
            "skills_dir": str(self.skills_dir),
            "source_dir": str(self.repo),
            "repo": str(self.repo),
            "branch": "main",
            "auto": False,
            "force": True,
        })()
        result = MODULE.discover_skills(args)
        checked = {item["skill"]: item for item in result["checked"]}
        self.assertEqual(checked["demo"]["status"], "update_available")
        self.assertEqual(checked["demo"]["latest_commit"], latest)
        self.assertEqual((self.skills_dir / "demo" / "SKILL.md").read_text(), "# Demo\nold\n")

    def test_discover_is_throttled_by_updater_metadata(self) -> None:
        self.write_source_skill("awesome-updater", "# Updater\n")
        self.commit_repo("add updater")
        args = type("Args", (), {
            "skill": "awesome-updater",
            "source_dir": str(self.repo),
            "skills_dir": str(self.skills_dir),
            "repo": str(self.repo),
            "branch": "main",
            "force": False,
        })()
        MODULE.install_skill(args)
        discover_args = type("Args", (), {
            "skills_dir": str(self.skills_dir),
            "source_dir": str(self.repo),
            "repo": str(self.repo),
            "branch": "main",
            "auto": True,
            "force": True,
        })()
        MODULE.discover_skills(discover_args)
        discover_args.force = False
        result = MODULE.discover_skills(discover_args)
        self.assertEqual(result["status"], "throttled")

    def test_discover_can_be_disabled_from_updater_config(self) -> None:
        self.write_source_skill("awesome-updater", "# Updater\n")
        self.commit_repo("add updater")
        install_args = type("Args", (), {
            "skill": "awesome-updater",
            "source_dir": str(self.repo),
            "skills_dir": str(self.skills_dir),
            "repo": str(self.repo),
            "branch": "main",
            "force": False,
        })()
        MODULE.install_skill(install_args)
        config_args = type("Args", (), {
            "skill": "awesome-updater",
            "skills_dir": str(self.skills_dir),
            "set_values": ["discover_new=false"],
        })()
        MODULE.config_skill(config_args)
        self.write_source_skill("new-skill", "# New Skill\n")
        self.commit_repo("add disabled new skill")
        discover_args = type("Args", (), {
            "skills_dir": str(self.skills_dir),
            "source_dir": str(self.repo),
            "repo": str(self.repo),
            "branch": "main",
            "auto": True,
            "force": True,
        })()
        result = MODULE.discover_skills(discover_args)
        self.assertEqual(result["status"], "skipped")
        self.assertFalse((self.skills_dir / "new-skill").exists())

    def test_discover_partial_failure_restores_failed_skill_only(self) -> None:
        self.write_source_skill("broken", "# Broken\nold\n")
        self.commit_repo("add broken")
        self.install_demo()
        install_broken = type("Args", (), {
            "skill": "broken",
            "source_dir": str(self.repo),
            "skills_dir": str(self.skills_dir),
            "repo": str(self.repo),
            "branch": "main",
            "force": False,
        })()
        MODULE.install_skill(install_broken)
        (self.repo / "skills" / "demo" / "SKILL.md").write_text("# Demo\nnew\n")
        (self.repo / "skills" / "broken" / "SKILL.md").write_text("# Broken\nnew\n")
        self.commit_repo("update demo and broken")

        original_replace = MODULE.replace_skill

        def flaky_replace(installed_skill, source_skill, metadata, latest_commit, latest_hash):
            if installed_skill.name != "broken":
                return original_replace(installed_skill, source_skill, metadata, latest_commit, latest_hash)
            original_rmtree = MODULE.shutil.rmtree

            def failing_rmtree(path, *args, **kwargs):
                if Path(path) == installed_skill:
                    original_rmtree(path, *args, **kwargs)
                    raise RuntimeError("simulated replace failure")
                return original_rmtree(path, *args, **kwargs)

            try:
                MODULE.shutil.rmtree = failing_rmtree
                return original_replace(installed_skill, source_skill, metadata, latest_commit, latest_hash)
            finally:
                MODULE.shutil.rmtree = original_rmtree

        try:
            MODULE.replace_skill = flaky_replace
            args = type("Args", (), {
                "skills_dir": str(self.skills_dir),
                "source_dir": str(self.repo),
                "repo": str(self.repo),
                "branch": "main",
                "auto": True,
                "force": True,
            })()
            result = MODULE.discover_skills(args)
        finally:
            MODULE.replace_skill = original_replace

        self.assertEqual(result["status"], "partial")
        self.assertEqual((self.skills_dir / "demo" / "SKILL.md").read_text(), "# Demo\nnew\n")
        self.assertEqual((self.skills_dir / "broken" / "SKILL.md").read_text(), "# Broken\nold\n")
        self.assertEqual(result["errors"][0]["skill"], "broken")
        backups = sorted((self.skills_dir / ".awesome-backups").glob("*"))
        self.assertGreaterEqual(len(backups), 2)

    def test_status_lists_managed_unmanaged_and_changed_files_without_writing(self) -> None:
        (self.repo / "skills" / "demo" / "notes").mkdir()
        (self.repo / "skills" / "demo" / "notes" / "old.txt").write_text("old\n")
        self.commit_repo("add notes")
        self.install_demo()
        metadata_path = self.skills_dir / "demo" / ".awesome-skill.json"
        before_metadata = metadata_path.read_text()
        (self.skills_dir / "local-only").mkdir(parents=True)
        (self.skills_dir / "local-only" / "SKILL.md").write_text("# Local\n")
        (self.repo / "skills" / "demo" / "notes" / "old.txt").unlink()
        (self.repo / "skills" / "demo" / "notes" / "new.txt").write_text("old\n")
        self.commit_repo("rename notes")
        args = type("Args", (), {
            "skills_dir": str(self.skills_dir),
            "source_dir": str(self.repo),
            "repo": str(self.repo),
            "branch": "main",
        })()
        result = MODULE.status_skills(args)
        self.assertEqual(result["status"], "ok")
        managed = {item["skill"]: item for item in result["managed"]}
        self.assertTrue(managed["demo"]["changed"])
        self.assertEqual(
            managed["demo"]["changed_files"],
            [
                {"path": "notes/new.txt", "change": "added"},
                {"path": "notes/old.txt", "change": "removed"},
            ],
        )
        self.assertEqual(result["unmanaged"], ["local-only"])
        self.assertEqual(result["missing_managed"], [])
        self.assertEqual(metadata_path.read_text(), before_metadata)


if __name__ == "__main__":
    unittest.main()
