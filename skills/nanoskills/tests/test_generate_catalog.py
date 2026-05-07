from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_catalog.py"
SPEC = importlib.util.spec_from_file_location("generate_catalog", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write_skill(skills_dir: Path, name: str, frontmatter: str) -> Path:
    skill_dir = skills_dir / name
    skill_dir.mkdir(parents=True)
    normalized_frontmatter = textwrap.dedent(frontmatter).strip()
    (skill_dir / "SKILL.md").write_text(
        f"---\n{normalized_frontmatter}\n---\n\n# {name}\n",
        encoding="utf-8",
    )
    return skill_dir


class GenerateCatalogTests(unittest.TestCase):
    def test_parse_frontmatter_supports_folded_description_and_nested_lists(self) -> None:
        raw = textwrap.dedent(
            """\
            ---
            name: sample-skill
            description: >-
              Use when the user asks to do
              a useful thing.
            user-invocable: true
            metadata:
              slash-command: /sample
              output: sample-output
              catalog:
                group: user-facing
                order: 20
                aliases:
                  - sample
                  - sample-alt
                examples:
                  - /sample Do this
            ---
            # Sample
            """
        )

        parsed = MODULE.parse_skill_markdown(raw, Path("skills/sample-skill/SKILL.md"))

        self.assertEqual(parsed["name"], "sample-skill")
        self.assertEqual(parsed["description"], "Use when the user asks to do a useful thing.")
        catalog = parsed["metadata"]["catalog"]
        self.assertEqual(catalog["group"], "user-facing")
        self.assertEqual(catalog["order"], 20)
        self.assertEqual(catalog["aliases"], ["sample", "sample-alt"])
        self.assertEqual(catalog["examples"], ["/sample Do this"])

    def test_collect_catalog_rejects_missing_required_catalog_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skills_dir = Path(tmp) / "skills"
            write_skill(
                skills_dir,
                "bad-skill",
                """
                name: bad-skill
                description: Broken catalog entry.
                user-invocable: true
                metadata:
                  slash-command: /bad
                """,
            )

            with self.assertRaisesRegex(MODULE.CatalogError, "metadata.catalog"):
                MODULE.collect_catalog(skills_dir)

    def test_collect_catalog_rejects_name_that_differs_from_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skills_dir = Path(tmp) / "skills"
            write_skill(
                skills_dir,
                "actual-name",
                """
                name: declared-name
                description: Name mismatch.
                user-invocable: true
                metadata:
                  slash-command: /declared
                  catalog:
                    group: user-facing
                    order: 10
                    aliases:
                      - declared
                    use_when: Use this.
                    expected_output: Output.
                    examples:
                      - /declared
                    readme_include: true
                    readme_description: Declared skill.
                """,
            )

            with self.assertRaisesRegex(MODULE.CatalogError, "must match directory"):
                MODULE.collect_catalog(skills_dir)

    def test_render_outputs_are_deterministic_and_grouped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skills_dir = Path(tmp) / "skills"
            write_skill(
                skills_dir,
                "admin-skill",
                """
                name: admin-skill
                description: Admin helper.
                user-invocable: true
                metadata:
                  slash-command: /admin
                  output: admin-output
                  catalog:
                    group: admin
                    order: 20
                    aliases:
                      - admin
                    use_when: Use for lifecycle work.
                    expected_output: Admin status.
                    examples:
                      - /admin
                    readme_include: false
                    readme_description: Admin helper.
                """,
            )
            write_skill(
                skills_dir,
                "user-skill",
                """
                name: user-skill
                description: User helper.
                user-invocable: true
                metadata:
                  slash-command: /user
                  output: user-output
                  catalog:
                    group: user-facing
                    order: 10
                    aliases:
                      - user
                    use_when: Use for user work.
                    expected_output: User result.
                    examples:
                      - /user
                    readme_include: true
                    readme_description: User-facing helper.
                """,
            )

            catalog = MODULE.collect_catalog(skills_dir)
            markdown = MODULE.render_catalog_markdown(catalog)
            json_text = MODULE.render_catalog_json(catalog)
            rendered = json.loads(json_text)

            self.assertLess(markdown.index("### user-skill"), markdown.index("### admin-skill"))
            self.assertIn("## User-Facing Skills", markdown)
            self.assertIn("## Admin / Package Skills", markdown)
            self.assertEqual(rendered["schema_version"], 1)
            self.assertEqual(len(rendered["source_hash"]), 64)
            self.assertEqual(json_text, MODULE.render_catalog_json(catalog))

    def test_update_readme_replaces_only_generated_block(self) -> None:
        readme = textwrap.dedent(
            """\
            # Title

            Before

            ## Available Skills

            <!-- BEGIN GENERATED AVAILABLE SKILLS -->
            old table
            <!-- END GENERATED AVAILABLE SKILLS -->

            After
            """
        )
        table = "### User-Facing Skills\n\n| Skill | Description |\n| --- | --- |\n| [demo](skills/demo) | Demo. |"

        updated = MODULE.update_readme_available_skills(readme, table)

        self.assertIn("Before", updated)
        self.assertIn("After", updated)
        self.assertNotIn("old table", updated)
        self.assertIn("### User-Facing Skills", updated)
        self.assertIn("| [demo](skills/demo) | Demo. |", updated)

    def test_stdout_mode_does_not_write_catalog_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            skills_dir = repo / "skills"
            write_skill(
                skills_dir,
                "demo",
                """
                name: demo
                description: Demo skill.
                user-invocable: true
                metadata:
                  slash-command: /demo
                  output: demo-output
                  catalog:
                    group: user-facing
                    order: 10
                    aliases:
                      - demo
                    use_when: Use demo.
                    expected_output: Demo output.
                    examples:
                      - /demo
                    readme_include: true
                    readme_description: Demo skill.
                """,
            )

            output = io.StringIO()
            with redirect_stdout(output):
                code = MODULE.main(["--stdout", "--repo-root", str(repo), "--skills-dir", str(skills_dir)])

            self.assertEqual(code, 0)
            self.assertIn("### demo", output.getvalue())
            self.assertFalse((repo / "skills/nanoskills/references/catalog.md").exists())
            self.assertFalse((repo / "skills/nanoskills/references/catalog.json").exists())

    def test_check_mode_fails_when_generated_files_are_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            skills_dir = repo / "skills"
            references = repo / "skills/nanoskills/references"
            references.mkdir(parents=True)
            (repo / "README.md").write_text(
                "## Available Skills\n\n<!-- BEGIN GENERATED AVAILABLE SKILLS -->\nstale\n<!-- END GENERATED AVAILABLE SKILLS -->\n",
                encoding="utf-8",
            )
            (references / "catalog.md").write_text("stale\n", encoding="utf-8")
            (references / "catalog.json").write_text("{}\n", encoding="utf-8")
            write_skill(
                skills_dir,
                "demo",
                """
                name: demo
                description: Demo skill.
                user-invocable: true
                metadata:
                  slash-command: /demo
                  output: demo-output
                  catalog:
                    group: user-facing
                    order: 10
                    aliases:
                      - demo
                    use_when: Use demo.
                    expected_output: Demo output.
                    examples:
                      - /demo
                    readme_include: true
                    readme_description: Demo skill.
                """,
            )

            error_output = io.StringIO()
            with redirect_stderr(error_output):
                code = MODULE.main(["--check", "--repo-root", str(repo), "--skills-dir", str(skills_dir)])

            self.assertEqual(code, 1)
            self.assertIn("generated catalog outputs are stale", error_output.getvalue())
            self.assertEqual((references / "catalog.md").read_text(encoding="utf-8"), "stale\n")


if __name__ == "__main__":
    unittest.main()
