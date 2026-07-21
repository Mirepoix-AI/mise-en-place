"""Regression tests for the documented Cowork .plugin bundle."""

from __future__ import annotations

import importlib.util
import pathlib
import tempfile
import unittest
import zipfile

_SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "build_cowork_bundle.py"
_SPEC = importlib.util.spec_from_file_location("build_cowork_bundle", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
builder = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(builder)


def _write(path: pathlib.Path, content: str = "fixture\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestCoworkBundle(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        for member in builder.REQUIRED_MEMBERS:
            _write(self.root / member)
        self.output = self.root / "dist" / "mise-en-place.plugin"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_bundle_contains_skill_and_slash_command_surfaces(self) -> None:
        builder.build_bundle(self.root, self.output)
        with zipfile.ZipFile(self.output) as archive:
            members = set(archive.namelist())
        self.assertIn("skills/mise-en-place/SKILL.md", members)
        self.assertIn("commands/mise-en-place.md", members)
        self.assertEqual(builder.validate_bundle(self.output), [])

    def test_validation_rejects_archive_without_slash_command(self) -> None:
        self.output.parent.mkdir(parents=True)
        with zipfile.ZipFile(self.output, "w") as archive:
            for member in builder.REQUIRED_MEMBERS - {"commands/mise-en-place.md"}:
                archive.writestr(member, "fixture\n")
        errors = builder.validate_bundle(self.output)
        self.assertIn(
            "bundle missing required member: commands/mise-en-place.md",
            errors,
        )


if __name__ == "__main__":
    unittest.main()
