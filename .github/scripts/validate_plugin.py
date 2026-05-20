#!/usr/bin/env python3
"""Validator for the mise-en-place Claude plugin marketplace repo.

Three checks (per specs/validate-ci.md):
  1. JSON manifest validity for .claude-plugin/plugin.json and
     .claude-plugin/marketplace.json (required fields + kebab-case names).
  2. SKILL.md frontmatter integrity for every skills/*/SKILL.md
     (name + description present; description has no XML-like tags).
  3. Relative-reference integrity: every backtick-quoted .md path in a
     SKILL.md body must resolve to an existing file on disk.

Exit codes:
  0 — no errors.
  1 — one or more validation failures (full list printed to stderr).
  2 — uncaught internal exception in main().

Stdlib only: no third-party deps, no install step in CI.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Default repo root: two levels up from .github/scripts/ → repo root.
DEFAULT_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
XML_TAG_RE = re.compile(r"<[a-zA-Z][a-zA-Z0-9_-]*>")
MD_REFERENCE_RE = re.compile(r"`([^`\n]+?\.md)`")
# Per ADR-016, contract.md must contain "## 5. Justified Action" exactly
# (case-sensitive, whitespace-strict). Changes to the heading text require
# their own ADR.
PRINCIPLE_5_HEADING_RE = re.compile(r"^## 5\. Justified Action\s*$", re.MULTILINE)
# Triple-backtick fenced code blocks. We strip these before MD reference
# extraction so that nested inline `something.md` spans inside fenced blocks
# do not produce false positives. Tilde-fenced blocks (~~~) are not stripped;
# the repo does not currently use them.
FENCED_BLOCK_RE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)
# A URL scheme like http:// or file://. Used to filter inline references.
URL_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://")
# Frontmatter key syntactic check.
FRONTMATTER_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------


def _rel(path: pathlib.Path, repo_root: pathlib.Path) -> str:
    """Return the path relative to repo_root, in posix form.

    Falls back to str(path) if path is not under repo_root (e.g. when tests
    pass in a path under a temp dir that is also the repo_root — that case
    works fine; this guard handles only truly out-of-tree paths).
    """
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


# ---------------------------------------------------------------------------
# JSON manifest checks
# ---------------------------------------------------------------------------


def _load_json(path: pathlib.Path, repo_root: pathlib.Path) -> tuple[Optional[dict], list[str]]:
    """Load and parse a JSON file. Returns (data, errors)."""
    rel = _rel(path, repo_root)
    if not path.is_file():
        return None, [f"{rel}: file not found"]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, [f"{rel}: cannot read file: {exc}"]
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, [f"{rel}: invalid JSON: {exc.msg} (line {exc.lineno} column {exc.colno})"]
    if not isinstance(data, dict):
        return None, [f"{rel}: invalid JSON: top-level value is not an object"]
    return data, []


def validate_plugin_json(path: pathlib.Path, repo_root: Optional[pathlib.Path] = None) -> list[str]:
    """Check 1a. plugin.json must have name, version, description; name kebab-case."""
    repo_root = repo_root if repo_root is not None else DEFAULT_REPO_ROOT
    rel = _rel(path, repo_root)
    data, errors = _load_json(path, repo_root)
    if data is None:
        return errors

    for field in ("name", "version", "description"):
        if field not in data:
            errors.append(f"{rel}: missing required field '{field}'")

    name = data.get("name")
    if isinstance(name, str) and not KEBAB_RE.match(name):
        errors.append(f"{rel}: name '{name}' is not kebab-case")

    return errors


def validate_marketplace_json(
    path: pathlib.Path, repo_root: Optional[pathlib.Path] = None
) -> list[str]:
    """Check 1b. marketplace.json: name, owner, plugins (non-empty list);
    each plugin entry has name, source, description; names kebab-case."""
    repo_root = repo_root if repo_root is not None else DEFAULT_REPO_ROOT
    rel = _rel(path, repo_root)
    data, errors = _load_json(path, repo_root)
    if data is None:
        return errors

    for field in ("name", "owner", "plugins"):
        if field not in data:
            errors.append(f"{rel}: missing required field '{field}'")

    name = data.get("name")
    if isinstance(name, str) and not KEBAB_RE.match(name):
        errors.append(f"{rel}: name '{name}' is not kebab-case")

    plugins = data.get("plugins")
    if "plugins" in data:
        if not isinstance(plugins, list):
            errors.append(f"{rel}: 'plugins' must be a list")
        elif len(plugins) == 0:
            errors.append(f"{rel}: 'plugins' must be a non-empty array")
        else:
            for idx, entry in enumerate(plugins):
                prefix = f"{rel}: plugins[{idx}]"
                if not isinstance(entry, dict):
                    errors.append(f"{prefix}: entry is not an object")
                    continue
                for field in ("name", "source", "description"):
                    if field not in entry:
                        errors.append(f"{prefix}: missing required field '{field}'")
                entry_name = entry.get("name")
                if isinstance(entry_name, str) and not KEBAB_RE.match(entry_name):
                    errors.append(f"{prefix}: name '{entry_name}' is not kebab-case")

    return errors


# ---------------------------------------------------------------------------
# Frontmatter parser (intentionally minimal: single-line key: value only)
# ---------------------------------------------------------------------------


def parse_frontmatter(text: str) -> tuple[Optional[dict[str, str]], list[str]]:
    """Parse the leading --- ... --- block of a SKILL.md.

    Returns (parsed_dict, errors).
      - (dict, [])         clean parse.
      - (partial, [errs])  partial parse + errors for individual lines.
      - (None, [errs])     frontmatter missing entirely or never closed.

    Supported subset: a flat block of single-line `key: value` pairs.
    Lines that are blank or YAML-style comments (`# ...`) are skipped.
    Anything richer (nested keys, lists, multi-line scalars) is flagged
    as malformed — the spec calls for swapping to pyyaml if/when that's
    needed.
    """
    if not text:
        return None, ["frontmatter missing (file is empty)"]

    # Strip an optional UTF-8 BOM at the start of the file.
    if text.startswith("﻿"):
        text = text.lstrip("﻿")

    lines = text.split("\n")
    if not lines or lines[0].rstrip("\r") != "---":
        return None, ["frontmatter missing (no leading '---' delimiter)"]

    parsed: dict[str, str] = {}
    errors: list[str] = []
    closed = False

    for raw in lines[1:]:
        line = raw.rstrip("\r")
        if line == "---":
            closed = True
            break

        stripped = line.strip()
        if stripped == "":
            continue
        if stripped.startswith("#"):
            continue

        if ":" not in line:
            errors.append(f"malformed frontmatter line: '{line}'")
            continue

        # Reject obviously non-flat constructs.
        if line.lstrip().startswith(("-", "[", "{")):
            errors.append(f"malformed frontmatter line: '{line}'")
            continue
        # Reject continuation/indented lines (we don't parse multi-line scalars).
        if line[:1] in (" ", "\t"):
            errors.append(f"malformed frontmatter line: '{line}'")
            continue

        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        if not FRONTMATTER_KEY_RE.match(key):
            errors.append(f"malformed frontmatter line: '{line}'")
            continue

        # Strip exactly one matching pair of single or double quotes around value.
        if len(value) >= 2 and (
            (value[0] == '"' and value[-1] == '"') or (value[0] == "'" and value[-1] == "'")
        ):
            value = value[1:-1]

        if key in parsed:
            errors.append(f"duplicate frontmatter key '{key}'")
            continue

        parsed[key] = value

    if not closed:
        errors.append("frontmatter not terminated (no closing '---')")
        return None, errors

    return parsed, errors


# ---------------------------------------------------------------------------
# SKILL.md frontmatter check
# ---------------------------------------------------------------------------


def validate_skill_frontmatter(
    skill_md: pathlib.Path, repo_root: Optional[pathlib.Path] = None
) -> list[str]:
    """Check 2. Frontmatter present, parses, has name+description, no XML-like tag."""
    repo_root = repo_root if repo_root is not None else DEFAULT_REPO_ROOT
    rel = _rel(skill_md, repo_root)
    if not skill_md.is_file():
        return [f"{rel}: file not found"]

    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{rel}: cannot read file: {exc}"]

    parsed, parse_errors = parse_frontmatter(text)
    errors = [f"{rel}: {msg}" for msg in parse_errors]

    if parsed is None:
        return errors

    for field in ("name", "description"):
        if field not in parsed:
            errors.append(f"{rel}: missing required frontmatter key '{field}'")

    description = parsed.get("description")
    if isinstance(description, str):
        for tag in XML_TAG_RE.findall(description):
            errors.append(f"{rel}: description contains XML-like tag {tag}")

    return errors


# ---------------------------------------------------------------------------
# Reference extraction + check
# ---------------------------------------------------------------------------


def extract_md_references(body: str) -> list[str]:
    """Return inline-backtick-quoted relative .md paths from body.

    Filters out URLs, absolute paths, and paths containing whitespace.
    Strips fenced (```) code blocks before matching to avoid false positives
    from inline spans nested inside fenced blocks.
    """
    if not body:
        return []
    body_for_refs = FENCED_BLOCK_RE.sub("", body)
    matches = MD_REFERENCE_RE.findall(body_for_refs)

    out: list[str] = []
    for match in matches:
        candidate = match.strip()
        if candidate != match:
            # whitespace inside the span — defensive skip
            continue
        if not candidate:
            continue
        if candidate.startswith("/"):
            continue
        if URL_SCHEME_RE.match(candidate):
            continue
        if any(ch.isspace() for ch in candidate):
            continue
        out.append(candidate)
    return out


def _split_frontmatter_and_body(text: str) -> str:
    """Return the body (everything after the closing --- delimiter).

    If the frontmatter is missing or unterminated, returns the original text;
    extract_md_references will simply scan the whole file in that case, which
    is a benign fallback because frontmatter is a flat key:value block and
    won't contain inline `.md` backtick spans.
    """
    if not text.startswith("---") and not text.startswith("﻿---"):
        return text
    # Strip optional BOM.
    if text.startswith("﻿"):
        text = text.lstrip("﻿")
    lines = text.split("\n")
    if not lines or lines[0].rstrip("\r") != "---":
        return text
    for idx in range(1, len(lines)):
        if lines[idx].rstrip("\r") == "---":
            return "\n".join(lines[idx + 1 :])
    return text


def _looks_like_local_reference(ref: str, skill_dir: pathlib.Path) -> bool:
    """Heuristic: does this backtick-quoted .md path look like a local file ref?

    Yes if any of:
      - the path is single-segment (e.g. `notes.md`),
      - it starts with `./` or `../` (explicit relative),
      - its first path segment exists as a sibling of skill_dir.

    No otherwise — e.g. `forrestchang/andrej-karpathy-skills/CLAUDE.md` looks
    like an external repo citation rather than a local file reference, because
    no `forrestchang/` directory sits next to the SKILL.md. This filter exists
    so that lineage / citation strings in skill bodies aren't flagged as
    broken references.
    """
    if ref.startswith("./") or ref.startswith("../"):
        return True
    if "/" not in ref:
        return True
    first_segment = ref.split("/", 1)[0]
    if first_segment in ("", ".", ".."):
        return True
    sibling = skill_dir / first_segment
    return sibling.exists()


def validate_skill_references(
    skill_md: pathlib.Path, repo_root: Optional[pathlib.Path] = None
) -> list[str]:
    """Check 3. Every inline-backtick-quoted relative .md reference exists."""
    repo_root = repo_root if repo_root is not None else DEFAULT_REPO_ROOT
    rel = _rel(skill_md, repo_root)
    if not skill_md.is_file():
        return [f"{rel}: file not found"]

    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{rel}: cannot read file: {exc}"]

    body = _split_frontmatter_and_body(text)
    refs = extract_md_references(body)

    errors: list[str] = []
    for ref in refs:
        if not _looks_like_local_reference(ref, skill_md.parent):
            # Treat as external citation (e.g. `user/repo/FILE.md`), not a local ref.
            continue
        resolved = (skill_md.parent / ref).resolve()
        if not resolved.is_file():
            errors.append(
                f"{rel}: broken reference '{ref}' (resolves to {resolved}, not found)"
            )
    return errors


# ---------------------------------------------------------------------------
# Contract Principle 5 invariant (ADR-016)
# ---------------------------------------------------------------------------


def validate_contract_principle_5(
    path: pathlib.Path, repo_root: Optional[pathlib.Path] = None
) -> list[str]:
    """Check 4. contract.md must contain the canonical Principle 5 heading.

    Per ADR-016, mise-en-place v0.5.0 onward commits to five foundational
    principles. The fifth (Justified Action / Five Whys) must appear as the
    heading "## 5. Justified Action" in the canonical contract. Future
    versions that drop, rename, or relocate the principle require their
    own ADR.
    """
    repo_root = repo_root if repo_root is not None else DEFAULT_REPO_ROOT
    rel = _rel(path, repo_root)

    if not path.is_file():
        return [f"{rel}: contract.md not found (required for Principle 5 invariant)"]

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{rel}: cannot read contract.md: {exc}"]

    if not PRINCIPLE_5_HEADING_RE.search(text):
        return [
            f"{rel}: missing canonical heading '## 5. Justified Action' "
            f"(required by ADR-016; changes to the heading text require their own ADR)"
        ]

    return []


# ---------------------------------------------------------------------------
# Skill discovery
# ---------------------------------------------------------------------------


def find_skill_files(skills_dir: pathlib.Path) -> list[pathlib.Path]:
    """Return sorted skills/*/SKILL.md paths. Returns [] if skills_dir missing.

    Globs only one level deep on purpose: the repo root contains a symlink
    `mise-en-place.md` -> `skills/mise-en-place/references/contract.md`
    that should NOT be treated as a SKILL.md, and the validator must not
    follow it. Scoping to skills/*/SKILL.md keeps that out by construction.
    """
    if not skills_dir.is_dir():
        return []
    return sorted(skills_dir.glob("*/SKILL.md"))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate mise-en-place plugin manifests and skill files."
    )
    parser.add_argument(
        "--repo-root",
        type=pathlib.Path,
        default=None,
        help="Path to repo root. Defaults to two levels above this script.",
    )
    return parser


def _run_checks(repo_root: pathlib.Path) -> tuple[list[str], int]:
    """Run all checks against repo_root. Returns (errors, n_skills)."""
    plugin_json = repo_root / ".claude-plugin" / "plugin.json"
    marketplace_json = repo_root / ".claude-plugin" / "marketplace.json"
    skills_dir = repo_root / "skills"
    contract_md = repo_root / "skills" / "mise-en-place" / "references" / "contract.md"

    errors: list[str] = []
    errors.extend(validate_plugin_json(plugin_json, repo_root))
    errors.extend(validate_marketplace_json(marketplace_json, repo_root))
    errors.extend(validate_contract_principle_5(contract_md, repo_root))

    skill_files = find_skill_files(skills_dir)
    for skill_md in skill_files:
        errors.extend(validate_skill_frontmatter(skill_md, repo_root))
        errors.extend(validate_skill_references(skill_md, repo_root))

    return errors, len(skill_files)


def main(argv: Optional[list[str]] = None) -> int:
    """Entry point. Returns 0 on success, 1 on validation errors, 2 on internal error."""
    try:
        parser = _build_arg_parser()
        args = parser.parse_args(argv)
        repo_root = (
            args.repo_root.resolve() if args.repo_root is not None else DEFAULT_REPO_ROOT
        )

        errors, n_skills = _run_checks(repo_root)

        print(f"[validate_plugin] checking 2 manifests, {n_skills} skills")
        for line in errors:
            print(line, file=sys.stderr)

        if errors:
            print(f"[validate_plugin] FAIL: {len(errors)} error(s)")
            return 1
        print("[validate_plugin] PASS")
        return 0
    except SystemExit:
        # argparse calls sys.exit on -h/--help; let that propagate.
        raise
    except Exception as exc:  # noqa: BLE001 — we want a single top-level safety net
        print(f"[validate_plugin] internal error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
