#!/usr/bin/env python3
"""Build and validate the mise-en-place Cowork plugin bundle."""

from __future__ import annotations

import argparse
import pathlib
import sys
import zipfile

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
INCLUDE_PATHS = (
    pathlib.Path(".claude-plugin"),
    pathlib.Path("skills"),
    pathlib.Path("commands"),
    pathlib.Path("README.md"),
    pathlib.Path("LICENSE"),
)
REQUIRED_MEMBERS = {
    ".claude-plugin/marketplace.json",
    ".claude-plugin/plugin.json",
    "commands/mise-en-place.md",
    "skills/mise-en-place/SKILL.md",
    "skills/mise-en-place/references/contract.md",
    "README.md",
    "LICENSE",
}


def bundle_files(repo_root: pathlib.Path) -> list[pathlib.Path]:
    """Return the sorted files that make up the Cowork bundle."""
    files: list[pathlib.Path] = []
    for relative in INCLUDE_PATHS:
        source = repo_root / relative
        if source.is_dir():
            files.extend(path for path in source.rglob("*") if path.is_file())
        elif source.is_file():
            files.append(source)
        else:
            raise FileNotFoundError(f"required bundle input not found: {relative}")
    return sorted(files, key=lambda path: path.relative_to(repo_root).as_posix())


def validate_bundle(bundle: pathlib.Path) -> list[str]:
    """Return errors for missing canonical plugin surfaces in a bundle."""
    if not bundle.is_file():
        return [f"bundle not found: {bundle}"]
    try:
        with zipfile.ZipFile(bundle) as archive:
            members = set(archive.namelist())
            bad_members = archive.testzip()
    except (OSError, zipfile.BadZipFile) as exc:
        return [f"invalid plugin archive: {exc}"]

    errors = [f"bundle missing required member: {name}" for name in sorted(REQUIRED_MEMBERS - members)]
    if bad_members is not None:
        errors.append(f"bundle member failed CRC check: {bad_members}")
    return errors


def build_bundle(repo_root: pathlib.Path, output: pathlib.Path) -> None:
    """Write a reproducible Cowork-compatible .plugin archive."""
    files = bundle_files(repo_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for source in files:
            relative = source.relative_to(repo_root).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes())

    errors = validate_bundle(output)
    if errors:
        raise ValueError("; ".join(errors))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=pathlib.Path,
        default=REPO_ROOT,
        help="repository root (defaults to the parent of this script)",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("dist/mise-en-place.plugin"),
        help="output .plugin path, relative to the repository root by default",
    )
    parser.add_argument(
        "--check",
        type=pathlib.Path,
        help="validate an existing archive instead of building one",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    repo_root = args.repo_root.resolve()

    if args.check is not None:
        bundle = args.check if args.check.is_absolute() else repo_root / args.check
        errors = validate_bundle(bundle)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        print(f"Cowork bundle valid: {bundle}")
        return 0

    output = args.output if args.output.is_absolute() else repo_root / args.output
    try:
        build_bundle(repo_root, output)
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"Cowork bundle build failed: {exc}", file=sys.stderr)
        return 1
    print(f"Cowork bundle built: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
