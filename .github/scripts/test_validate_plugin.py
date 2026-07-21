"""Tests for validate_plugin.py.

Stdlib unittest only. Each test builds its own fixture tree inside a
TemporaryDirectory; tests never read or mutate the real repo.
"""

from __future__ import annotations

import io
import json
import pathlib
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

# Make sibling validate_plugin.py importable regardless of how unittest
# discovers this file.
_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import validate_plugin as vp  # noqa: E402


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _write(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _valid_plugin_json() -> dict:
    return {
        "name": "mise-en-place",
        "version": "0.1.0",
        "description": "Test plugin description.",
    }


def _valid_marketplace_json() -> dict:
    return {
        "name": "mirepoix",
        "description": "Test marketplace description.",
        "owner": {"name": "John Edge", "email": "john.edge@kavara.ai"},
        "plugins": [
            {
                "name": "mise-en-place",
                "source": "./",
                "description": "Test plugin description.",
                "version": "0.1.0",
            }
        ],
    }


# ---------------------------------------------------------------------------
# Test base
# ---------------------------------------------------------------------------


class _TempRootTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name).resolve()

    def tearDown(self) -> None:
        self._tmp.cleanup()


# ---------------------------------------------------------------------------
# 1–3: plugin.json tests
# ---------------------------------------------------------------------------


class TestPluginJson(_TempRootTest):
    def test_valid_plugin_json_passes(self) -> None:
        path = self.root / ".claude-plugin" / "plugin.json"
        _write(path, json.dumps(_valid_plugin_json()))
        self.assertEqual(vp.validate_plugin_json(path, self.root), [])

    def test_invalid_json_returns_error(self) -> None:
        path = self.root / ".claude-plugin" / "plugin.json"
        _write(path, "{not json")
        errors = vp.validate_plugin_json(path, self.root)
        self.assertTrue(errors, "expected at least one error")
        self.assertTrue(
            any("invalid JSON" in e for e in errors),
            f"expected 'invalid JSON' in errors, got: {errors}",
        )

    def test_missing_required_field(self) -> None:
        path = self.root / ".claude-plugin" / "plugin.json"
        data = _valid_plugin_json()
        del data["version"]
        _write(path, json.dumps(data))
        errors = vp.validate_plugin_json(path, self.root)
        self.assertTrue(
            any("missing required field 'version'" in e for e in errors),
            f"expected missing 'version' error, got: {errors}",
        )


# ---------------------------------------------------------------------------
# 4–5: marketplace.json tests
# ---------------------------------------------------------------------------


class TestMarketplaceJson(_TempRootTest):
    def test_valid_and_kebab_case_enforced(self) -> None:
        path = self.root / ".claude-plugin" / "marketplace.json"
        _write(path, json.dumps(_valid_marketplace_json()))
        self.assertEqual(vp.validate_marketplace_json(path, self.root), [])

        bad = _valid_marketplace_json()
        bad["name"] = "Bad_Name"
        _write(path, json.dumps(bad))
        errors = vp.validate_marketplace_json(path, self.root)
        self.assertTrue(
            any("not kebab-case" in e for e in errors),
            f"expected 'not kebab-case' in errors, got: {errors}",
        )

    def test_plugins_array_must_be_nonempty(self) -> None:
        path = self.root / ".claude-plugin" / "marketplace.json"
        data = _valid_marketplace_json()
        data["plugins"] = []
        _write(path, json.dumps(data))
        errors = vp.validate_marketplace_json(path, self.root)
        self.assertTrue(
            any("non-empty" in e for e in errors),
            f"expected 'non-empty' error for empty plugins array, got: {errors}",
        )

    def test_marketplace_description_is_required(self) -> None:
        path = self.root / ".claude-plugin" / "marketplace.json"
        data = _valid_marketplace_json()
        del data["description"]
        _write(path, json.dumps(data))
        errors = vp.validate_marketplace_json(path, self.root)
        self.assertIn(
            ".claude-plugin/marketplace.json: missing required field 'description'",
            errors,
        )


class TestManifestParity(_TempRootTest):
    def test_matching_versions_pass(self) -> None:
        plugin = self.root / ".claude-plugin" / "plugin.json"
        marketplace = self.root / ".claude-plugin" / "marketplace.json"
        _write(plugin, json.dumps(_valid_plugin_json()))
        _write(marketplace, json.dumps(_valid_marketplace_json()))
        self.assertEqual(vp.validate_manifest_parity(plugin, marketplace, self.root), [])

    def test_version_drift_fails(self) -> None:
        plugin = self.root / ".claude-plugin" / "plugin.json"
        marketplace = self.root / ".claude-plugin" / "marketplace.json"
        _write(plugin, json.dumps(_valid_plugin_json()))
        data = _valid_marketplace_json()
        data["plugins"][0]["version"] = "0.0.9"
        _write(marketplace, json.dumps(data))
        errors = vp.validate_manifest_parity(plugin, marketplace, self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("does not match plugin.json version '0.1.0'", errors[0])


# ---------------------------------------------------------------------------
# Frontmatter parser tests
# ---------------------------------------------------------------------------


class TestFrontmatterParser(unittest.TestCase):
    def test_basic_kv_pairs(self) -> None:
        text = "---\nname: foo\ndescription: Bar baz.\n---\nbody\n"
        parsed, errors = vp.parse_frontmatter(text)
        self.assertEqual(errors, [])
        self.assertEqual(parsed, {"name": "foo", "description": "Bar baz."})

    def test_missing_closing_delim(self) -> None:
        text = "---\nname: foo\ndescription: Bar.\n"
        parsed, errors = vp.parse_frontmatter(text)
        self.assertIsNone(parsed)
        self.assertTrue(
            any("not terminated" in e for e in errors),
            f"expected not-terminated error, got: {errors}",
        )

    def test_crlf_and_blank_lines_tolerated(self) -> None:
        text = "---\r\nname: foo\r\n\r\ndescription: Bar baz.\r\n---\r\nbody\r\n"
        parsed, errors = vp.parse_frontmatter(text)
        self.assertEqual(errors, [])
        self.assertEqual(parsed, {"name": "foo", "description": "Bar baz."})


# ---------------------------------------------------------------------------
# 9–10: skill frontmatter tests
# ---------------------------------------------------------------------------


class TestSkillFrontmatter(_TempRootTest):
    def _make_skill(self, frontmatter_lines: list[str], body: str = "Body.") -> pathlib.Path:
        path = self.root / "skills" / "demo" / "SKILL.md"
        text = "---\n" + "\n".join(frontmatter_lines) + "\n---\n" + body + "\n"
        _write(path, text)
        return path

    def test_xml_tag_in_description_fails(self) -> None:
        path = self._make_skill(
            [
                "name: demo",
                "description: Greet <test> the operator.",
            ]
        )
        errors = vp.validate_skill_frontmatter(path, self.root)
        self.assertTrue(
            any("description contains XML-like tag <test>" in e for e in errors),
            f"expected XML-tag error, got: {errors}",
        )

    def test_missing_description_fails(self) -> None:
        path = self._make_skill(["name: demo"])
        errors = vp.validate_skill_frontmatter(path, self.root)
        self.assertTrue(
            any("missing required frontmatter key 'description'" in e for e in errors),
            f"expected missing description error, got: {errors}",
        )


# ---------------------------------------------------------------------------
# 11–15: reference extraction + validation tests
# ---------------------------------------------------------------------------


class TestReferences(_TempRootTest):
    def test_extract_finds_inline_md_paths(self) -> None:
        body = "See `references/contract.md` for details.\n"
        self.assertEqual(vp.extract_md_references(body), ["references/contract.md"])

    def test_extract_skips_fenced_block(self) -> None:
        body = (
            "Outside `references/contract.md` should match.\n"
            "```\n"
            "Inside `inside/file.md` should NOT match.\n"
            "```\n"
        )
        refs = vp.extract_md_references(body)
        self.assertIn("references/contract.md", refs)
        self.assertNotIn("inside/file.md", refs)

    def test_extract_filters_urls_and_absolute(self) -> None:
        body = (
            "Skip `https://example.com/page.md` and `/abs/foo.md` "
            "but keep `references/contract.md`.\n"
        )
        refs = vp.extract_md_references(body)
        self.assertEqual(refs, ["references/contract.md"])

    def test_broken_reference_fails(self) -> None:
        skill = self.root / "skills" / "demo" / "SKILL.md"
        # Create the references/ sibling directory so the heuristic recognizes
        # references/missing.md as a local reference (even though the .md is
        # absent, which is the broken-ref case under test).
        (skill.parent / "references").mkdir(parents=True, exist_ok=True)
        body = (
            "---\n"
            "name: demo\n"
            "description: Demo skill.\n"
            "---\n"
            "See `references/missing.md`.\n"
        )
        _write(skill, body)
        errors = vp.validate_skill_references(skill, self.root)
        self.assertTrue(
            any("broken reference 'references/missing.md'" in e for e in errors),
            f"expected broken reference error, got: {errors}",
        )

    def test_resolved_reference_passes(self) -> None:
        skill = self.root / "skills" / "demo" / "SKILL.md"
        ref_target = skill.parent / "references" / "contract.md"
        _write(ref_target, "# contract\n")
        body = (
            "---\n"
            "name: demo\n"
            "description: Demo skill.\n"
            "---\n"
            "See `references/contract.md`.\n"
        )
        _write(skill, body)
        self.assertEqual(vp.validate_skill_references(skill, self.root), [])


# ---------------------------------------------------------------------------
# 16: local-reference heuristic (_looks_like_local_reference) tests
# ---------------------------------------------------------------------------


class TestLooksLikeLocalReference(_TempRootTest):
    """Explicit coverage of the _looks_like_local_reference heuristic.

    This filter was added by the coding agent (deviation from blueprint §3)
    to avoid flagging external lineage citations such as
    `forrestchang/andrej-karpathy-skills/CLAUDE.md` as broken references.
    These tests verify the filter's boundaries, including one false-negative
    risk: a typo'd first segment (e.g. `Reference/contract.md` instead of
    `references/contract.md`) is silently treated as an external citation
    when no `Reference/` directory exists.
    """

    def setUp(self) -> None:
        super().setUp()
        # Create a skill directory with a real `references/` sibling.
        self.skill_dir = self.root / "skills" / "demo"
        self.skill_dir.mkdir(parents=True, exist_ok=True)
        (self.skill_dir / "references").mkdir(exist_ok=True)

    def test_single_segment_ref_is_local(self) -> None:
        # A bare filename with no directory component is always treated as local.
        self.assertTrue(vp._looks_like_local_reference("notes.md", self.skill_dir))

    def test_explicit_relative_prefix_is_local(self) -> None:
        # ./file.md and ../sibling/file.md are unambiguously local.
        self.assertTrue(vp._looks_like_local_reference("./notes.md", self.skill_dir))
        self.assertTrue(vp._looks_like_local_reference("../other/notes.md", self.skill_dir))

    def test_existing_first_segment_is_local(self) -> None:
        # references/ exists as a sibling of skill_dir, so this is local.
        self.assertTrue(
            vp._looks_like_local_reference("references/contract.md", self.skill_dir)
        )

    def test_three_segment_external_citation_is_not_local(self) -> None:
        # `forrestchang/andrej-karpathy-skills/CLAUDE.md` — first segment
        # `forrestchang` does NOT exist as a sibling of skill_dir, so the
        # filter correctly treats this as an external citation (not local).
        self.assertFalse(
            vp._looks_like_local_reference(
                "forrestchang/andrej-karpathy-skills/CLAUDE.md", self.skill_dir
            )
        )

    def test_capitalised_first_segment_is_not_local_false_negative_risk(self) -> None:
        # `Reference/contract.md` (capital R) — the directory `Reference/`
        # does NOT exist next to SKILL.md (only lowercase `references/` does).
        # The filter returns False, which means the validator silently skips
        # this reference instead of flagging it as broken.  This is a known
        # false-negative: a typo'd path segment that looks like an external
        # citation is not validated.  This test documents the behavior so that
        # operators are aware of the boundary.
        result = vp._looks_like_local_reference("Reference/contract.md", self.skill_dir)
        # The heuristic returns False — the typo'd ref is NOT treated as local.
        self.assertFalse(
            result,
            "Capital-R 'Reference/' is not a sibling dir, so filter returns False "
            "(false-negative risk: broken ref silently ignored).",
        )


# ---------------------------------------------------------------------------
# 17: main() integration test
# ---------------------------------------------------------------------------


class TestMain(_TempRootTest):
    def _build_minimal_repo(self, *, bad_description: bool = False) -> None:
        plugin = self.root / ".claude-plugin" / "plugin.json"
        marketplace = self.root / ".claude-plugin" / "marketplace.json"
        _write(plugin, json.dumps(_valid_plugin_json()))
        _write(marketplace, json.dumps(_valid_marketplace_json()))

        # Principle 5 invariant (ADR-016): the validator now also checks for
        # the canonical heading in the mise-en-place contract. The minimal
        # fixture must include it for the clean-repo path to return 0.
        mep_contract = (
            self.root / "skills" / "mise-en-place" / "references" / "contract.md"
        )
        _write(mep_contract, "# mise-en-place\n\n## 5. Justified Action\n")

        skill = self.root / "skills" / "demo" / "SKILL.md"
        ref_target = skill.parent / "references" / "contract.md"
        _write(ref_target, "# contract\n")
        description = (
            "Demo skill with <bad> tag." if bad_description else "Demo skill description."
        )
        _write(
            skill,
            "---\n"
            f"name: demo\n"
            f"description: {description}\n"
            "---\n"
            "See `references/contract.md`.\n",
        )

    def test_main_returns_1_on_any_error(self) -> None:
        self._build_minimal_repo(bad_description=True)
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = vp.main(["--repo-root", str(self.root)])
        self.assertEqual(rc, 1, f"expected rc=1, got {rc}; stderr={err.getvalue()!r}")
        self.assertIn("description contains XML-like tag <bad>", err.getvalue())

    def test_main_returns_0_on_clean_repo(self) -> None:
        # Sanity check that the harness produces a clean repo when asked.
        self._build_minimal_repo(bad_description=False)
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = vp.main(["--repo-root", str(self.root)])
        self.assertEqual(rc, 0, f"expected rc=0, got {rc}; stderr={err.getvalue()!r}")


# ---------------------------------------------------------------------------
# 18–23: Principle 5 invariant tests (ADR-016)
# ---------------------------------------------------------------------------


class TestPrinciple5Invariant(_TempRootTest):
    """Tests for the validate_contract_principle_5 invariant check (ADR-016)."""

    def _write_contract(self, body: str) -> pathlib.Path:
        contract = self.root / "contract.md"
        _write(contract, body)
        return contract

    def test_canonical_heading_passes(self) -> None:
        """A contract.md with the canonical Section 5 heading should validate."""
        contract = self._write_contract(
            "# mise-en-place\n\n"
            "## 1. Think Before Coding\n...\n"
            "## 5. Justified Action\n\n"
            "**Every action serves a why-chain...**\n"
        )
        self.assertEqual(vp.validate_contract_principle_5(contract, self.root), [])

    def test_missing_heading_fails(self) -> None:
        """A contract.md without Section 5 should produce an error."""
        contract = self._write_contract(
            "# mise-en-place\n\n## 1. Think Before Coding\n...\n"
        )
        errors = vp.validate_contract_principle_5(contract, self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("missing canonical heading", errors[0])
        self.assertIn("ADR-016", errors[0])

    def test_renamed_heading_fails(self) -> None:
        """A renamed Principle 5 (e.g., 'Justified Work' or 'Five Whys') should fail."""
        contract = self._write_contract("# mise-en-place\n\n## 5. Five Whys\n...\n")
        errors = vp.validate_contract_principle_5(contract, self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("Justified Action", errors[0])

    def test_lowercase_heading_fails(self) -> None:
        """Heading text is case-sensitive; lowercase 'justified action' should fail."""
        contract = self._write_contract(
            "# mise-en-place\n\n## 5. justified action\n...\n"
        )
        errors = vp.validate_contract_principle_5(contract, self.root)
        self.assertEqual(len(errors), 1)

    def test_missing_file_fails(self) -> None:
        """A non-existent contract.md should produce a clear error."""
        nonexistent = (
            self.root / "skills" / "mise-en-place" / "references" / "contract.md"
        )
        errors = vp.validate_contract_principle_5(nonexistent, self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("not found", errors[0])

    def test_heading_at_different_section_number_fails(self) -> None:
        """Section number must be 5 (Principle 5 is the fifth principle, not the eighth)."""
        contract = self._write_contract(
            "# mise-en-place\n\n## 8. Justified Action\n...\n"
        )
        errors = vp.validate_contract_principle_5(contract, self.root)
        self.assertEqual(len(errors), 1)


if __name__ == "__main__":
    unittest.main()
