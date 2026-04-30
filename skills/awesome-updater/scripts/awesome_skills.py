#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any

DEFAULT_REPO = "https://github.com/fabioespindula/awesome-nanoclaw-skills.git"
DEFAULT_BRANCH = "main"
DEFAULT_THROTTLE_SECONDS = 3600
METADATA_NAME = ".awesome-skill.json"
BACKUP_DIR_NAME = ".awesome-backups"
LOCK_NAME = ".awesome-update.lock"
GLOBAL_CONFIG_SKILL = "awesome-updater"
MANAGED_DEFAULTS = {
    "source_repo": DEFAULT_REPO,
    "branch": DEFAULT_BRANCH,
    "update_check": True,
    "auto_upgrade": True,
    "discover_new": True,
    "throttle_seconds": DEFAULT_THROTTLE_SECONDS,
    "discover_throttle_seconds": DEFAULT_THROTTLE_SECONDS,
}


class UpdaterError(RuntimeError):
    pass


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def iso_now() -> str:
    return utc_now().replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_iso(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def bool_value(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"expected boolean, got {value!r}")


def run_git(args: list[str], cwd: Path | None = None) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=str(cwd) if cwd else None,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise UpdaterError("git is required for update checks") from exc
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or exc.stdout.strip() or str(exc)
        raise UpdaterError(f"git command failed: {detail}") from exc
    return completed.stdout.strip()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise UpdaterError(f"invalid JSON metadata: {path}") from exc
    if not isinstance(value, dict):
        raise UpdaterError(f"metadata must be a JSON object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def skill_dir(skills_dir: Path, skill: str) -> Path:
    if "/" in skill or ".." in Path(skill).parts or skill.strip() != skill or not skill:
        raise UpdaterError(f"invalid skill name: {skill!r}")
    return skills_dir / skill


def metadata_path(installed_skill: Path) -> Path:
    return installed_skill / METADATA_NAME


def load_metadata(installed_skill: Path) -> dict[str, Any]:
    metadata = read_json(metadata_path(installed_skill))
    if not metadata:
        raise UpdaterError(f"skill is not managed by awesome-updater: {installed_skill}")
    merged = {**MANAGED_DEFAULTS, **metadata}
    merged["skill"] = merged.get("skill") or installed_skill.name
    return merged


def source_commit(source_dir: Path | None, repo: str, branch: str) -> str:
    if source_dir:
        return run_git(["rev-parse", "HEAD"], cwd=source_dir)
    output = run_git(["ls-remote", repo, f"refs/heads/{branch}"])
    if not output:
        raise UpdaterError(f"branch not found: {branch}")
    return output.split()[0]


def clone_source(repo: str, branch: str, tmp_root: Path) -> Path:
    target = tmp_root / "source"
    run_git(["clone", "--depth", "1", "--branch", branch, repo, str(target)])
    return target


def validate_source_skill(source_skill: Path) -> None:
    if not source_skill.exists() or not source_skill.is_dir():
        raise UpdaterError(f"source skill not found: {source_skill}")
    if not (source_skill / "SKILL.md").is_file():
        raise UpdaterError(f"source skill is missing SKILL.md: {source_skill}")
    for item in source_skill.rglob("*"):
        if item.is_symlink():
            raise UpdaterError(f"source skill contains symlink: {item}")
        try:
            item.relative_to(source_skill)
        except ValueError as exc:
            raise UpdaterError(f"source path escapes skill directory: {item}") from exc


def source_skills_root(source_dir: Path) -> Path:
    skills_root = source_dir / "skills"
    return skills_root if skills_root.is_dir() else source_dir


def list_source_skills(source_dir: Path) -> dict[str, Path]:
    skills: dict[str, Path] = {}
    for candidate in sorted(source_skills_root(source_dir).iterdir()):
        if candidate.name.startswith(".") or not candidate.is_dir():
            continue
        if (candidate / "SKILL.md").is_file():
            skills[candidate.name] = candidate
    return skills


def global_metadata_path(skills_dir: Path) -> Path:
    return metadata_path(skills_dir / GLOBAL_CONFIG_SKILL)


def load_global_metadata(skills_dir: Path) -> dict[str, Any]:
    path = global_metadata_path(skills_dir)
    if path.exists():
        return {**MANAGED_DEFAULTS, **read_json(path)}
    return {**MANAGED_DEFAULTS, "skill": GLOBAL_CONFIG_SKILL}


def write_global_metadata(skills_dir: Path, metadata: dict[str, Any]) -> None:
    path = global_metadata_path(skills_dir)
    if path.exists():
        write_json(path, metadata)


def managed_installed_skills(skills_dir: Path) -> dict[str, dict[str, Any]]:
    managed: dict[str, dict[str, Any]] = {}
    if not skills_dir.exists():
        return managed
    for candidate in sorted(skills_dir.iterdir()):
        if not candidate.is_dir() or candidate.name.startswith("."):
            continue
        metadata_file = metadata_path(candidate)
        if metadata_file.exists():
            managed[candidate.name] = {**MANAGED_DEFAULTS, **read_json(metadata_file)}
    return managed


@contextmanager
def lock(skills_dir: Path):
    lock_path = skills_dir / LOCK_NAME
    try:
        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
    except FileExistsError as exc:
        raise UpdaterError(f"another update is already running: {lock_path}") from exc
    try:
        yield
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def backup_skill(installed_skill: Path, installed_commit: str | None) -> Path:
    backups = installed_skill.parent / BACKUP_DIR_NAME
    backups.mkdir(exist_ok=True)
    stamp = utc_now().strftime("%Y%m%d-%H%M%S")
    commit = (installed_commit or "unknown")[:12]
    target = backups / f"{installed_skill.name}-{stamp}-{commit}"
    shutil.copytree(installed_skill, target, ignore=shutil.ignore_patterns(BACKUP_DIR_NAME, LOCK_NAME))
    return target


def replace_skill(installed_skill: Path, source_skill: Path, metadata: dict[str, Any], latest_commit: str) -> Path | None:
    backup = backup_skill(installed_skill, metadata.get("installed_commit")) if installed_skill.exists() else None
    temp_target = installed_skill.parent / f".{installed_skill.name}.next"
    if temp_target.exists():
        shutil.rmtree(temp_target)
    try:
        shutil.copytree(source_skill, temp_target, ignore=shutil.ignore_patterns(".git", BACKUP_DIR_NAME, LOCK_NAME))
        next_metadata = {
            **MANAGED_DEFAULTS,
            **metadata,
            "skill": metadata.get("skill") or installed_skill.name,
            "installed_commit": latest_commit,
            "last_seen_commit": latest_commit,
            "last_check_at": iso_now(),
            "last_update_at": iso_now(),
        }
        write_json(temp_target / METADATA_NAME, next_metadata)
        if installed_skill.exists():
            shutil.rmtree(installed_skill)
        temp_target.rename(installed_skill)
    except Exception:
        if temp_target.exists():
            shutil.rmtree(temp_target)
        if backup and not installed_skill.exists():
            shutil.copytree(backup, installed_skill)
        raise
    return backup


def install_skill(args: argparse.Namespace) -> dict[str, Any]:
    source_dir = Path(args.source_dir).resolve()
    skills_dir = Path(args.skills_dir).resolve()
    installed = skill_dir(skills_dir, args.skill)
    source = source_dir / "skills" / args.skill
    if not source.exists():
        source = source_dir / args.skill
    validate_source_skill(source)
    skills_dir.mkdir(parents=True, exist_ok=True)
    commit = source_commit(source_dir, args.repo, args.branch)
    metadata = {
        **MANAGED_DEFAULTS,
        "source_repo": args.repo,
        "branch": args.branch,
        "skill": args.skill,
        "installed_commit": commit,
        "last_seen_commit": commit,
        "last_check_at": iso_now(),
        "last_update_at": iso_now(),
    }
    if installed.exists() and not args.force:
        raise UpdaterError(f"skill already exists, use --force to replace: {installed}")
    if installed.exists():
        shutil.rmtree(installed)
    shutil.copytree(source, installed, ignore=shutil.ignore_patterns(".git", BACKUP_DIR_NAME, LOCK_NAME))
    write_json(metadata_path(installed), metadata)
    return {"status": "installed", "skill": args.skill, "commit": commit, "path": str(installed)}


def check_skill(args: argparse.Namespace) -> dict[str, Any]:
    skills_dir = Path(args.skills_dir).resolve()
    installed = skill_dir(skills_dir, args.skill)
    metadata = load_metadata(installed)
    if not metadata.get("update_check", True):
        return {"status": "skipped", "reason": "update_check_disabled", "skill": args.skill}

    last_check = parse_iso(metadata.get("last_check_at"))
    throttle_seconds = int(metadata.get("throttle_seconds", DEFAULT_THROTTLE_SECONDS))
    if last_check and not args.force:
        elapsed = (utc_now() - last_check).total_seconds()
        if elapsed < throttle_seconds:
            return {
                "status": "throttled",
                "skill": args.skill,
                "seconds_until_next_check": int(throttle_seconds - elapsed),
                "installed_commit": metadata.get("installed_commit"),
            }

    repo = args.repo or metadata.get("source_repo", DEFAULT_REPO)
    branch = args.branch or metadata.get("branch", DEFAULT_BRANCH)
    source_dir = Path(args.source_dir).resolve() if args.source_dir else None
    latest_commit = source_commit(source_dir, repo, branch)
    metadata["last_check_at"] = iso_now()
    metadata["last_seen_commit"] = latest_commit
    write_json(metadata_path(installed), metadata)

    if latest_commit == metadata.get("installed_commit"):
        return {"status": "up_to_date", "skill": args.skill, "commit": latest_commit}

    auto_upgrade = args.auto or bool(metadata.get("auto_upgrade", True))
    if not auto_upgrade:
        return {
            "status": "update_available",
            "skill": args.skill,
            "installed_commit": metadata.get("installed_commit"),
            "latest_commit": latest_commit,
        }

    with lock(skills_dir):
        with tempfile.TemporaryDirectory(prefix="awesome-skills-") as tmp:
            tmp_root = Path(tmp)
            repo_dir = source_dir or clone_source(repo, branch, tmp_root)
            source_skill = repo_dir / "skills" / args.skill
            if not source_skill.exists():
                source_skill = repo_dir / args.skill
            validate_source_skill(source_skill)
            backup = replace_skill(installed, source_skill, {**metadata, "source_repo": repo, "branch": branch}, latest_commit)
    return {
        "status": "upgraded",
        "skill": args.skill,
        "previous_commit": metadata.get("installed_commit"),
        "installed_commit": latest_commit,
        "backup": str(backup) if backup else None,
    }


def config_skill(args: argparse.Namespace) -> dict[str, Any]:
    installed = skill_dir(Path(args.skills_dir).resolve(), args.skill)
    metadata = load_metadata(installed)
    for item in args.set_values or []:
        if "=" not in item:
            raise UpdaterError(f"expected key=value, got {item!r}")
        key, raw = item.split("=", 1)
        key = key.strip()
        if key not in {
            "auto_upgrade",
            "update_check",
            "discover_new",
            "throttle_seconds",
            "discover_throttle_seconds",
            "branch",
            "source_repo",
        }:
            raise UpdaterError(f"unsupported config key: {key}")
        if key in {"auto_upgrade", "update_check", "discover_new"}:
            value: Any = bool_value(raw)
        elif key in {"throttle_seconds", "discover_throttle_seconds"}:
            value = int(raw)
            if value < 0:
                raise UpdaterError(f"{key} must be >= 0")
        else:
            value = raw
        metadata[key] = value
    write_json(metadata_path(installed), metadata)
    return {"status": "configured", "skill": args.skill, "metadata": metadata}


def discover_skills(args: argparse.Namespace) -> dict[str, Any]:
    skills_dir = Path(args.skills_dir).resolve()
    skills_dir.mkdir(parents=True, exist_ok=True)
    global_metadata = load_global_metadata(skills_dir)

    if not global_metadata.get("discover_new", True):
        return {"status": "skipped", "reason": "discover_new_disabled"}

    last_discover = parse_iso(global_metadata.get("last_discover_at"))
    throttle_seconds = int(global_metadata.get("discover_throttle_seconds", DEFAULT_THROTTLE_SECONDS))
    if last_discover and not args.force:
        elapsed = (utc_now() - last_discover).total_seconds()
        if elapsed < throttle_seconds:
            return {
                "status": "throttled",
                "seconds_until_next_discover": int(throttle_seconds - elapsed),
            }

    repo = args.repo or global_metadata.get("source_repo", DEFAULT_REPO)
    branch = args.branch or global_metadata.get("branch", DEFAULT_BRANCH)
    source_dir_arg = Path(args.source_dir).resolve() if args.source_dir else None

    with tempfile.TemporaryDirectory(prefix="awesome-skills-discover-") as tmp:
        tmp_root = Path(tmp)
        repo_dir = source_dir_arg or clone_source(repo, branch, tmp_root)
        latest_commit = source_commit(repo_dir, repo, branch)
        source_skills = list_source_skills(repo_dir)
        managed = managed_installed_skills(skills_dir)
        installed: list[str] = []
        check_results: list[dict[str, Any]] = []
        skipped_existing_unmanaged: list[str] = []
        skipped_different_source: list[str] = []
        errors: list[dict[str, str]] = []

        for name, metadata in managed.items():
            if name not in source_skills:
                continue
            if metadata.get("source_repo", DEFAULT_REPO) != repo or metadata.get("branch", DEFAULT_BRANCH) != branch:
                skipped_different_source.append(name)
                continue
            check_args = argparse.Namespace(
                skill=name,
                skills_dir=str(skills_dir),
                source_dir=str(repo_dir),
                repo=repo,
                branch=branch,
                auto=args.auto,
                force=True,
            )
            try:
                check_results.append(check_skill(check_args))
            except Exception as exc:
                errors.append({"skill": name, "error": str(exc)})

        with lock(skills_dir):
            for name, source_skill in source_skills.items():
                target = skill_dir(skills_dir, name)
                if target.exists():
                    if not metadata_path(target).exists():
                        skipped_existing_unmanaged.append(name)
                    continue
                try:
                    validate_source_skill(source_skill)
                    metadata = {
                        **MANAGED_DEFAULTS,
                        "source_repo": repo,
                        "branch": branch,
                        "skill": name,
                    }
                    replace_skill(target, source_skill, metadata, latest_commit)
                    installed.append(name)
                except Exception as exc:
                    errors.append({"skill": name, "error": str(exc)})

        latest_global_metadata = load_global_metadata(skills_dir)
        latest_global_metadata["last_discover_at"] = iso_now()
        latest_global_metadata["last_seen_commit"] = latest_commit
        write_global_metadata(skills_dir, latest_global_metadata)

    return {
        "status": "partial" if errors else "discovered",
        "source_repo": repo,
        "branch": branch,
        "commit": latest_commit,
        "installed": installed,
        "checked": check_results,
        "skipped_existing_unmanaged": skipped_existing_unmanaged,
        "skipped_different_source": skipped_different_source,
        "errors": errors,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install and auto-update Awesome NanoClaw Skills")
    subcommands = parser.add_subparsers(dest="command", required=True)

    install = subcommands.add_parser("install", help="install a managed skill")
    install.add_argument("skill")
    install.add_argument("--source-dir", required=True)
    install.add_argument("--skills-dir", required=True)
    install.add_argument("--repo", default=DEFAULT_REPO)
    install.add_argument("--branch", default=DEFAULT_BRANCH)
    install.add_argument("--force", action="store_true")
    install.set_defaults(func=install_skill)

    check = subcommands.add_parser("check", help="check and optionally auto-upgrade a managed skill")
    check.add_argument("skill")
    check.add_argument("--skills-dir", required=True)
    check.add_argument("--source-dir")
    check.add_argument("--repo")
    check.add_argument("--branch")
    check.add_argument("--auto", action="store_true", help="allow upgrade when an update is available")
    check.add_argument("--force", action="store_true", help="ignore update-check throttle")
    check.set_defaults(func=check_skill)

    discover = subcommands.add_parser("discover", help="sync new and existing skills from the trusted package source")
    discover.add_argument("--skills-dir", required=True)
    discover.add_argument("--source-dir")
    discover.add_argument("--repo")
    discover.add_argument("--branch")
    discover.add_argument("--auto", action="store_true", help="allow upgrades when updates are available")
    discover.add_argument("--force", action="store_true", help="ignore discover throttle")
    discover.set_defaults(func=discover_skills)

    config = subcommands.add_parser("config", help="change managed skill updater config")
    config.add_argument("skill")
    config.add_argument("--skills-dir", required=True)
    config.add_argument("--set", dest="set_values", action="append")
    config.set_defaults(func=config_skill)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
    except UpdaterError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
