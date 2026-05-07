#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
BEGIN_AVAILABLE = "<!-- BEGIN GENERATED AVAILABLE SKILLS -->"
END_AVAILABLE = "<!-- END GENERATED AVAILABLE SKILLS -->"
GROUP_ORDER = ["user-facing", "admin"]
GROUP_LABELS = {
    "user-facing": "User-Facing Skills",
    "admin": "Admin / Package Skills",
}


class CatalogError(RuntimeError):
    pass


@dataclass(frozen=True)
class SkillEntry:
    name: str
    group: str
    order: int
    slash_command: str
    aliases: list[str]
    description: str
    use_when: str
    expected_output: str
    examples: list[str]
    output: str
    readme_include: bool
    readme_description: str

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "group": self.group,
            "order": self.order,
            "slash_command": self.slash_command,
            "aliases": self.aliases,
            "description": self.description,
            "use_when": self.use_when,
            "expected_output": self.expected_output,
            "examples": self.examples,
            "output": self.output,
            "readme_include": self.readme_include,
            "readme_description": self.readme_description,
        }


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def split_frontmatter(text: str, path: Path) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise CatalogError(f"{path}: missing YAML frontmatter")
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[1:index])
    raise CatalogError(f"{path}: unterminated YAML frontmatter")


def indentation(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def parse_scalar(raw: str, path: Path, line_no: int) -> Any:
    value = raw.strip()
    if not value:
        return ""
    if value.startswith("&") or value.startswith("*") or " &" in value:
        raise CatalogError(f"{path}:{line_no}: YAML anchors and aliases are not supported")
    if value.startswith(("[", "{")):
        raise CatalogError(f"{path}:{line_no}: inline YAML collections are not supported")
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "none", "~"}:
        return None
    if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
        return int(value)
    return value


def normalized_lines(frontmatter: str, path: Path) -> list[tuple[int, str, int]]:
    result: list[tuple[int, str, int]] = []
    for line_no, raw in enumerate(frontmatter.splitlines(), start=1):
        if "\t" in raw:
            raise CatalogError(f"{path}:{line_no}: tabs are not supported in frontmatter")
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        result.append((indentation(raw), stripped, line_no))
    return result


def collect_folded_value(lines: list[tuple[int, str, int]], start: int, parent_indent: int) -> tuple[str, int]:
    parts: list[str] = []
    index = start
    while index < len(lines):
        indent, content, _line_no = lines[index]
        if indent <= parent_indent:
            break
        parts.append(content)
        index += 1
    return " ".join(parts).strip(), index


def parse_list(lines: list[tuple[int, str, int]], start: int, list_indent: int, path: Path) -> tuple[list[Any], int]:
    values: list[Any] = []
    index = start
    while index < len(lines):
        indent, content, line_no = lines[index]
        if indent < list_indent:
            break
        if indent > list_indent:
            raise CatalogError(f"{path}:{line_no}: nested list values are not supported")
        if not content.startswith("- "):
            break
        item = content[2:].strip()
        if not item:
            raise CatalogError(f"{path}:{line_no}: empty list items are not supported")
        values.append(parse_scalar(item, path, line_no))
        index += 1
    return values, index


def parse_mapping(lines: list[tuple[int, str, int]], start: int, map_indent: int, path: Path) -> tuple[dict[str, Any], int]:
    data: dict[str, Any] = {}
    index = start
    while index < len(lines):
        indent, content, line_no = lines[index]
        if indent < map_indent:
            break
        if indent > map_indent:
            raise CatalogError(f"{path}:{line_no}: unexpected indentation")
        if content.startswith("- "):
            raise CatalogError(f"{path}:{line_no}: top-level lists are not supported here")
        key, separator, raw_value = content.partition(":")
        if not separator or not key.strip():
            raise CatalogError(f"{path}:{line_no}: expected key: value")
        key = key.strip()
        raw_value = raw_value.strip()
        if raw_value in {">", ">-"}:
            value, index = collect_folded_value(lines, index + 1, indent)
            data[key] = value
            continue
        if raw_value:
            data[key] = parse_scalar(raw_value, path, line_no)
            index += 1
            continue
        next_index = index + 1
        if next_index >= len(lines) or lines[next_index][0] <= indent:
            data[key] = {}
            index += 1
            continue
        child_indent, child_content, _child_line = lines[next_index]
        if child_content.startswith("- "):
            value, index = parse_list(lines, next_index, child_indent, path)
        else:
            value, index = parse_mapping(lines, next_index, child_indent, path)
        data[key] = value
    return data, index


def parse_simple_yaml(frontmatter: str, path: Path) -> dict[str, Any]:
    lines = normalized_lines(frontmatter, path)
    data, index = parse_mapping(lines, 0, 0, path)
    if index != len(lines):
        raise CatalogError(f"{path}: could not parse all frontmatter")
    return data


def parse_skill_markdown(text: str, path: Path) -> dict[str, Any]:
    return parse_simple_yaml(split_frontmatter(text, path), path)


def require_type(value: Any, expected_type: type, field: str, path: Path) -> Any:
    if not isinstance(value, expected_type):
        raise CatalogError(f"{path}: {field} must be {expected_type.__name__}")
    return value


def require_nonempty_string(value: Any, field: str, path: Path) -> str:
    value = require_type(value, str, field, path)
    if not value.strip():
        raise CatalogError(f"{path}: {field} must not be empty")
    return value.strip()


def require_string_list(value: Any, field: str, path: Path) -> list[str]:
    value = require_type(value, list, field, path)
    if not value:
        raise CatalogError(f"{path}: {field} must not be empty")
    strings: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise CatalogError(f"{path}: {field} must contain non-empty strings")
        strings.append(item.strip())
    return strings


def build_entry(skill_dir: Path) -> SkillEntry:
    skill_path = skill_dir / "SKILL.md"
    parsed = parse_skill_markdown(skill_path.read_text(encoding="utf-8"), skill_path)
    name = require_nonempty_string(parsed.get("name"), "name", skill_path)
    if name != skill_dir.name:
        raise CatalogError(f"{skill_path}: name {name!r} must match directory {skill_dir.name!r}")
    description = require_nonempty_string(parsed.get("description"), "description", skill_path)
    metadata = require_type(parsed.get("metadata"), dict, "metadata", skill_path)
    slash_command = require_nonempty_string(metadata.get("slash-command"), "metadata.slash-command", skill_path)
    output = require_nonempty_string(metadata.get("output", "skill-output"), "metadata.output", skill_path)
    catalog = require_type(metadata.get("catalog"), dict, "metadata.catalog", skill_path)
    group = require_nonempty_string(catalog.get("group"), "metadata.catalog.group", skill_path)
    if group not in GROUP_LABELS:
        raise CatalogError(f"{skill_path}: metadata.catalog.group must be one of {', '.join(GROUP_ORDER)}")
    order = require_type(catalog.get("order"), int, "metadata.catalog.order", skill_path)
    aliases = require_string_list(catalog.get("aliases"), "metadata.catalog.aliases", skill_path)
    use_when = require_nonempty_string(catalog.get("use_when"), "metadata.catalog.use_when", skill_path)
    expected_output = require_nonempty_string(catalog.get("expected_output"), "metadata.catalog.expected_output", skill_path)
    examples = require_string_list(catalog.get("examples"), "metadata.catalog.examples", skill_path)
    readme_include = require_type(catalog.get("readme_include"), bool, "metadata.catalog.readme_include", skill_path)
    readme_description = require_nonempty_string(
        catalog.get("readme_description"),
        "metadata.catalog.readme_description",
        skill_path,
    )
    return SkillEntry(
        name=name,
        group=group,
        order=order,
        slash_command=slash_command,
        aliases=aliases,
        description=description,
        use_when=use_when,
        expected_output=expected_output,
        examples=examples,
        output=output,
        readme_include=readme_include,
        readme_description=readme_description,
    )


def collect_catalog(skills_dir: Path) -> dict[str, Any]:
    if not skills_dir.is_dir():
        raise CatalogError(f"skills directory not found: {skills_dir}")
    entries = [
        build_entry(candidate)
        for candidate in sorted(skills_dir.iterdir())
        if candidate.is_dir() and not candidate.name.startswith(".") and (candidate / "SKILL.md").is_file()
    ]
    entries.sort(key=lambda entry: (GROUP_ORDER.index(entry.group), entry.order, entry.name))
    skills = [entry.to_json() for entry in entries]
    digest = hashlib.sha256(json.dumps(skills, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return {"schema_version": SCHEMA_VERSION, "source_hash": digest, "skills": skills}


def render_skill_markdown(skill: dict[str, Any]) -> str:
    examples = "\n".join(f"  - `{example}`" for example in skill["examples"])
    return "\n".join(
        [
            f"### {skill['name']}",
            "",
            f"- Slash command: `{skill['slash_command']}`",
            f"- What it does: {skill['readme_description']}",
            f"- Use when: {skill['use_when']}",
            f"- Output: {skill['expected_output']}",
            "- Curated examples:",
            examples,
        ]
    )


def render_catalog_markdown(catalog: dict[str, Any]) -> str:
    lines = [
        "# NanoSkills Catalog",
        "",
        "This file is generated from `skills/*/SKILL.md` frontmatter. Do not edit it by hand.",
        "",
        "Only list skills from this generated catalog. Do not merge global runtime skills, external skills, or inferred capabilities.",
        "",
        "Answer in the language of the current conversation. Keep skill names and slash commands literal.",
        "",
    ]
    by_group: dict[str, list[dict[str, Any]]] = {group: [] for group in GROUP_ORDER}
    for skill in catalog["skills"]:
        by_group[skill["group"]].append(skill)
    for group in GROUP_ORDER:
        if not by_group[group]:
            continue
        lines.extend([f"## {GROUP_LABELS[group]}", ""])
        for skill in by_group[group]:
            lines.extend([render_skill_markdown(skill), ""])
    lines.extend(["## Catalog Grouping", ""])
    for group in GROUP_ORDER:
        if not by_group[group]:
            continue
        lines.extend([f"Show these skills under `{GROUP_LABELS[group]}`:", ""])
        lines.extend(f"- {skill['name']}" for skill in by_group[group])
        lines.append("")
    lines.extend(
        [
            "If this file is missing or stale in a NanoClaw container, `/nanoskills` should fail closed and ask for the package catalog to be updated or reinstalled.",
            "",
        ]
    )
    return "\n".join(lines)


def render_catalog_json(catalog: dict[str, Any]) -> str:
    return json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_readme_table(catalog: dict[str, Any]) -> str:
    lines: list[str] = []
    by_group: dict[str, list[dict[str, Any]]] = {group: [] for group in GROUP_ORDER}
    for skill in catalog["skills"]:
        if skill["readme_include"]:
            by_group[skill["group"]].append(skill)
    for group in GROUP_ORDER:
        if not by_group[group]:
            continue
        if lines:
            lines.append("")
        lines.extend([f"### {GROUP_LABELS[group]}", "", "| Skill | Description |", "| --- | --- |"])
        for skill in by_group[group]:
            lines.append(f"| [{skill['name']}](skills/{skill['name']}) | {skill['readme_description']} |")
    return "\n".join(lines)


def update_readme_available_skills(content: str, table: str) -> str:
    block = f"{BEGIN_AVAILABLE}\n{table}\n{END_AVAILABLE}"
    if BEGIN_AVAILABLE in content and END_AVAILABLE in content:
        before, rest = content.split(BEGIN_AVAILABLE, 1)
        _old, after = rest.split(END_AVAILABLE, 1)
        return before + block + after
    heading = "## Available Skills"
    if heading not in content:
        raise CatalogError("README.md: missing ## Available Skills section")
    before, rest = content.split(heading, 1)
    next_heading = rest.find("\n## ")
    if next_heading == -1:
        return before + heading + "\n\n" + block + "\n"
    return before + heading + "\n\n" + block + "\n" + rest[next_heading:]


def paths_for(repo_root: Path) -> dict[str, Path]:
    return {
        "catalog_md": repo_root / "skills/nanoskills/references/catalog.md",
        "catalog_json": repo_root / "skills/nanoskills/references/catalog.json",
        "readme": repo_root / "README.md",
    }


def expected_outputs(repo_root: Path, skills_dir: Path) -> dict[str, str]:
    catalog = collect_catalog(skills_dir)
    paths = paths_for(repo_root)
    readme_content = paths["readme"].read_text(encoding="utf-8") if paths["readme"].exists() else "## Available Skills\n"
    return {
        "catalog_md": render_catalog_markdown(catalog),
        "catalog_json": render_catalog_json(catalog),
        "readme": update_readme_available_skills(readme_content, render_readme_table(catalog)),
    }


def write_outputs(repo_root: Path, skills_dir: Path) -> None:
    outputs = expected_outputs(repo_root, skills_dir)
    paths = paths_for(repo_root)
    paths["catalog_md"].parent.mkdir(parents=True, exist_ok=True)
    paths["catalog_md"].write_text(outputs["catalog_md"], encoding="utf-8")
    paths["catalog_json"].write_text(outputs["catalog_json"], encoding="utf-8")
    paths["readme"].write_text(outputs["readme"], encoding="utf-8")


def check_outputs(repo_root: Path, skills_dir: Path) -> list[str]:
    outputs = expected_outputs(repo_root, skills_dir)
    paths = paths_for(repo_root)
    stale: list[str] = []
    for key, expected in outputs.items():
        path = paths[key]
        actual = path.read_text(encoding="utf-8") if path.exists() else None
        if actual != expected:
            stale.append(str(path))
    return stale


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate the NanoSkills catalog from SKILL.md frontmatter.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="Write catalog.md, catalog.json, and README generated block.")
    mode.add_argument("--check", action="store_true", help="Fail if generated outputs are stale.")
    mode.add_argument("--stdout", action="store_true", help="Print generated Markdown catalog without writing files.")
    parser.add_argument("--repo-root", default=str(default_repo_root()))
    parser.add_argument("--skills-dir", help="Directory containing skill folders. Defaults to <repo-root>/skills.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    skills_dir = Path(args.skills_dir).resolve() if args.skills_dir else repo_root / "skills"
    try:
        if args.stdout:
            print(render_catalog_markdown(collect_catalog(skills_dir)), end="")
            return 0
        if args.write:
            write_outputs(repo_root, skills_dir)
            return 0
        stale = check_outputs(repo_root, skills_dir)
    except CatalogError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if stale:
        print("FAIL: generated catalog outputs are stale:", file=sys.stderr)
        for path in stale:
            print(f"  {path}", file=sys.stderr)
        print("Run: python3 skills/nanoskills/scripts/generate_catalog.py --write", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
