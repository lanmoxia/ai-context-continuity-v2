"""Unit tests for continuity.schemas (WORK-0002).

Coverage:
- Draft 2020-12 schema self-check (all 12 entity + common schemas)
- Self-contained offline $ref (no network, no arbitrary path loading)
- Package resources: schema_names() == 12, each name loadable
- Valid fixtures: each passes validate()
- Invalid fixtures: missing fields, unknown fields, wrong type, bad enum,
  bad ID pattern, no timezone -> all rejected with structured errors
- Stable error ordering
- Unknown schema name -> ValueError before any I/O
- External URI $ref rejection (schema-level guard)
- Incompatible schema_version (not 1) is rejected

All tests are 0 skipped.
"""

import importlib.resources
import json
import pathlib
import unittest

from continuity.schemas import (
    check_all_schemas,
    load_schema,
    schema_names,
    validate,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FIXTURE_ROOT = pathlib.Path(__file__).parent.parent / "fixtures" / "schemas"
_VALID_DIR = _FIXTURE_ROOT / "valid"
_INVALID_DIR = _FIXTURE_ROOT / "invalid"


def _load_fixture(path: pathlib.Path) -> object:
    return json.loads(path.read_bytes())


# ---------------------------------------------------------------------------
# 1. Schema meta-check
# ---------------------------------------------------------------------------


class TestSchemaMetaCheck(unittest.TestCase):
    def test_all_schemas_pass_meta_check(self) -> None:
        """All entity schemas (+ common) must be valid Draft 2020-12."""
        # Should not raise.
        check_all_schemas()


# ---------------------------------------------------------------------------
# 2. Package resources
# ---------------------------------------------------------------------------


class TestPackageResources(unittest.TestCase):
    def test_schema_names_returns_exactly_12(self) -> None:
        names = schema_names()
        self.assertEqual(len(names), 12)

    def test_schema_names_are_sorted(self) -> None:
        names = schema_names()
        self.assertEqual(names, sorted(names))

    def test_each_schema_is_loadable(self) -> None:
        for name in schema_names():
            with self.subTest(name=name):
                schema = load_schema(name)
                self.assertIn("$id", schema)
                self.assertIn("$schema", schema)

    def test_schemas_are_loaded_via_importlib_resources(self) -> None:
        """Confirm the .schema.json files exist as package resources."""
        pkg = importlib.resources.files("continuity.schemas")
        for name in schema_names():
            resource = pkg.joinpath(f"{name}.schema.json")
            # Reading should succeed (raises FileNotFoundError if missing).
            data = resource.read_bytes()
            self.assertGreater(len(data), 0)

    def test_load_schema_unknown_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            load_schema("nonexistent_schema_xyz")

    def test_validate_unknown_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            validate("nonexistent_schema_xyz", {})


# ---------------------------------------------------------------------------
# 3. Valid fixtures
# ---------------------------------------------------------------------------


_SCHEMA_TO_VALID_FIXTURE: list[tuple[str, str]] = [
    ("project", "project.json"),
    ("config", "config.json"),
    ("current", "current.json"),
    ("task", "task.json"),
    ("stage", "stage.json"),
    ("work-order", "work-order.json"),
    ("checkpoint", "checkpoint.json"),
    ("handoff", "handoff.json"),
    ("evidence", "evidence.json"),
    ("context-pack", "context-pack.json"),
    ("review-pack", "review-pack.json"),
    ("review-decision", "review-decision.json"),
]


class TestValidFixtures(unittest.TestCase):
    def test_valid_fixtures_pass_validation(self) -> None:
        for schema_name, filename in _SCHEMA_TO_VALID_FIXTURE:
            fixture_path = _VALID_DIR / filename
            with self.subTest(schema=schema_name, fixture=filename):
                self.assertTrue(fixture_path.exists(), f"Fixture missing: {fixture_path}")
                instance = _load_fixture(fixture_path)
                errors = validate(schema_name, instance)
                self.assertEqual(
                    errors,
                    [],
                    f"Expected no errors for valid fixture {filename!r} "
                    f"against schema {schema_name!r}, got: {errors}",
                )


# ---------------------------------------------------------------------------
# 4. Invalid fixtures
# ---------------------------------------------------------------------------


class TestInvalidFixtures(unittest.TestCase):
    def _assert_rejected(self, schema_name: str, filename: str) -> list[dict]:
        fixture_path = _INVALID_DIR / filename
        self.assertTrue(fixture_path.exists(), f"Fixture missing: {fixture_path}")
        instance = _load_fixture(fixture_path)
        errors = validate(schema_name, instance)
        self.assertGreater(
            len(errors),
            0,
            f"Expected validation errors for {filename!r} against {schema_name!r}, "
            f"but got none.",
        )
        return errors

    def test_task_missing_required_fields_is_rejected(self) -> None:
        self._assert_rejected("task", "task_missing_fields.json")

    def test_task_unknown_field_is_rejected(self) -> None:
        self._assert_rejected("task", "task_unknown_field.json")

    def test_task_wrong_type_is_rejected(self) -> None:
        self._assert_rejected("task", "task_wrong_type.json")

    def test_task_bad_enum_is_rejected(self) -> None:
        self._assert_rejected("task", "task_bad_enum.json")

    def test_task_bad_id_pattern_is_rejected(self) -> None:
        self._assert_rejected("task", "task_bad_id.json")

    def test_task_no_timezone_in_timestamp_is_rejected(self) -> None:
        self._assert_rejected("task", "task_no_timezone.json")

    def test_review_pack_bad_sha256_is_rejected(self) -> None:
        self._assert_rejected("review-pack", "review_pack_bad_sha256.json")

    def test_review_decision_bad_verdict_is_rejected(self) -> None:
        self._assert_rejected("review-decision", "review_decision_bad_verdict.json")

    def test_inline_unknown_field_rejected(self) -> None:
        """additionalProperties: false guard via inline instance."""
        errors = validate("task", {
            "schema_version": 1,
            "id": "TASK-0001",
            "title": "T",
            "goal": "G",
            "scope_in": ["x"],
            "scope_out": [],
            "acceptance_criteria": ["p"],
            "status": "active",
            "created_at": "2026-07-17T10:00:00+08:00",
            "updated_at": "2026-07-17T10:00:00+08:00",
            "injected_key": "evil",
        })
        self.assertGreater(len(errors), 0)

    def test_inline_missing_field_rejected(self) -> None:
        errors = validate("task", {
            "schema_version": 1,
            "id": "TASK-0001",
            # missing title, goal, scope_in, etc.
        })
        self.assertGreater(len(errors), 0)

    def test_inline_wrong_schema_version_rejected(self) -> None:
        """schema_version != 1 must be rejected (const: 1)."""
        errors = validate("project", {
            "schema_version": 2,
            "id": "PROJECT-0001",
            "name": "test",
            "root_path": "/tmp/x",
            "created_at": "2026-07-01T08:00:00+08:00",
            "data_format_version": 1,
        })
        self.assertGreater(len(errors), 0)

    def test_no_timezone_rejected_inline(self) -> None:
        """Timestamp without timezone must be rejected by pattern check."""
        errors = validate("task", {
            "schema_version": 1,
            "id": "TASK-0001",
            "title": "T",
            "goal": "G",
            "scope_in": ["x"],
            "scope_out": [],
            "acceptance_criteria": ["p"],
            "status": "active",
            "created_at": "2026-07-17T10:00:00",   # missing tz
            "updated_at": "2026-07-17T10:00:00+08:00",
        })
        self.assertGreater(len(errors), 0)

    def test_short_id_rejected(self) -> None:
        """ID with fewer than 4 decimal digits must be rejected."""
        errors = validate("task", {
            "schema_version": 1,
            "id": "TASK-001",   # only 3 digits
            "title": "T",
            "goal": "G",
            "scope_in": ["x"],
            "scope_out": [],
            "acceptance_criteria": ["p"],
            "status": "active",
            "created_at": "2026-07-17T10:00:00+08:00",
            "updated_at": "2026-07-17T10:00:00+08:00",
        })
        self.assertGreater(len(errors), 0)

    def test_new_invalid_fixtures_are_rejected(self) -> None:
        """Verify the newly added invalid fixtures are rejected as expected."""
        self._assert_rejected("task", "task_bad_date_leap.json")
        self._assert_rejected("task", "task_bad_date_hour24.json")
        self._assert_rejected("task", "task_bad_date_pattern.json")
        self._assert_rejected("checkpoint", "checkpoint_bad_fingerprint_size.json")
        self._assert_rejected("current", "current_bad_id.json")
        self._assert_rejected("review-decision", "review_decision_missing_round.json")


# ---------------------------------------------------------------------------
# 5. Stable error ordering
# ---------------------------------------------------------------------------


class TestStableErrorOrdering(unittest.TestCase):
    def test_error_list_is_stably_ordered(self) -> None:
        """Running validate() twice on the same bad input gives identical ordering."""
        instance = {
            "schema_version": 1,
            "id": "task-bad",       # bad pattern
            "title": 99,            # wrong type
            # missing many required fields
        }
        errors_1 = validate("task", instance)
        errors_2 = validate("task", instance)
        self.assertEqual(errors_1, errors_2)
        # Each error dict must contain code, path, keyword.
        for err in errors_1:
            self.assertIn("code", err)
            self.assertIn("path", err)
            self.assertIn("keyword", err)

    def test_error_dicts_have_required_keys(self) -> None:
        errors = validate("task", {"schema_version": 99})
        self.assertGreater(len(errors), 0)
        for err in errors:
            self.assertIsInstance(err["code"], str)
            self.assertIsInstance(err["path"], str)
            self.assertIsInstance(err["keyword"], str)


# ---------------------------------------------------------------------------
# 6. Offline / security guards
# ---------------------------------------------------------------------------


class TestOfflineAndSecurityGuards(unittest.TestCase):
    def test_schema_id_does_not_use_http_uri(self) -> None:
        """No schema should have an http(s)://-based $id to avoid accidental net fetches."""
        for name in schema_names():
            schema = load_schema(name)
            schema_id = schema.get("$id", "")
            self.assertFalse(
                schema_id.startswith("http://") or schema_id.startswith("https://"),
                f"Schema {name!r} has an HTTP $id which risks network resolution: {schema_id!r}",
            )

    def test_all_schema_refs_are_urn_based(self) -> None:
        """$ref values in the loaded schemas must use urn: URIs, not http(s)."""
        for name in schema_names():
            schema = load_schema(name)
            schema_str = json.dumps(schema)
            # Check that any $ref that appears is not an http/https one.
            # We search for the raw string pattern.
            import re
            bad_refs = re.findall(r'"\\$ref"\s*:\s*"https?://', schema_str)
            self.assertEqual(
                bad_refs,
                [],
                f"Schema {name!r} contains http(s) $ref: {bad_refs}",
            )

    def test_validate_does_not_raise_on_bad_instance(self) -> None:
        """validate() must return errors, not raise, for invalid instances."""
        errors = validate("task", {"completely": "wrong"})
        self.assertIsInstance(errors, list)
        self.assertGreater(len(errors), 0)

    def test_common_schema_not_in_public_names(self) -> None:
        """'common' is an internal schema and must not appear in schema_names()."""
        self.assertNotIn("common", schema_names())

    def test_common_schema_load_raises_value_error(self) -> None:
        """load_schema('common') must raise ValueError (not in public whitelist)."""
        with self.assertRaises(ValueError):
            load_schema("common")
    def test_strict_rfc3339_calendar_rules(self) -> None:
        """Verify that semantic calendar boundaries are strictly checked."""
        # Non-leap year Feb 29 (invalid)
        errors1 = validate("task", {
            "schema_version": 1,
            "id": "TASK-0001",
            "title": "T", "goal": "G",
            "scope_in": ["x"], "scope_out": [],
            "acceptance_criteria": ["p"], "status": "active",
            "created_at": "2026-02-29T10:00:00+08:00",
            "updated_at": "2026-07-17T10:00:00+08:00"
        })
        self.assertTrue(any(e["code"] == "rfc3339_strict" for e in errors1))

        # Leap year Feb 29 (valid)
        errors2 = validate("task", {
            "schema_version": 1,
            "id": "TASK-0001",
            "title": "T", "goal": "G",
            "scope_in": ["x"], "scope_out": [],
            "acceptance_criteria": ["p"], "status": "active",
            "created_at": "2024-02-29T10:00:00+08:00",
            "updated_at": "2026-07-17T10:00:00+08:00"
        })
        self.assertEqual(errors2, [])

        # Non-existent month 13
        errors3 = validate("task", {
            "schema_version": 1,
            "id": "TASK-0001",
            "title": "T", "goal": "G",
            "scope_in": ["x"], "scope_out": [],
            "acceptance_criteria": ["p"], "status": "active",
            "created_at": "2026-13-10T10:00:00+08:00",
            "updated_at": "2026-07-17T10:00:00+08:00"
        })
        self.assertTrue(len(errors3) > 0)

        # Illegal hour 24
        errors4 = validate("task", {
            "schema_version": 1,
            "id": "TASK-0001",
            "title": "T", "goal": "G",
            "scope_in": ["x"], "scope_out": [],
            "acceptance_criteria": ["p"], "status": "active",
            "created_at": "2026-07-20T24:00:00+08:00",
            "updated_at": "2026-07-17T10:00:00+08:00"
        })
        self.assertTrue(len(errors4) > 0)

    def test_non_empty_source_fingerprint_valid(self) -> None:
        """Verify that a non-empty source fingerprint with valid entries is accepted."""
        instance = {
            "schema_version": 1,
            "id": "CHECKPOINT-0001",
            "task_id": "TASK-0001",
            "stage_id": "STAGE-0001",
            "state_revision": 3,
            "writer_lease_id": "LEASE-0001",
            "completed_steps": ["Step 1"],
            "in_progress_steps": [],
            "changed_files": ["pyproject.toml"],
            "check_summaries": [],
            "known_risks": [],
            "source_fingerprint": {
                "git_head": "abc1234567890123456789012345678901234567",
                "staged_diff_sha256": None,
                "unstaged_diff_sha256": None,
                "untracked_files": [
                    {
                        "path": "src/continuity/schemas/registry.py",
                        "size_bytes": 1234,
                        "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
                    }
                ],
                "captured_at": "2026-07-17T14:00:00+08:00"
            },
            "created_at": "2026-07-17T14:00:00+08:00"
        }
        self.assertEqual(validate("checkpoint", instance), [])

    def test_invalid_stable_ids_and_hashes_rejection(self) -> None:
        """Verify that nullable_stable_id constraints are strictly enforced."""
        # Test work-order with invalid supersedes_work_order_id (must be stable ID or null)
        errors = validate("work-order", {
            "schema_version": 1,
            "id": "WORK-0002",
            "task_id": "TASK-0001",
            "stage_id": "STAGE-02",
            "revision": 1,
            "title": "Build",
            "goal": "Test",
            "risk_level": "normal",
            "risk_reasons": [],
            "required_review_gates": ["GATE-01"],
            "allowed_paths": ["pyproject.toml"],
            "forbidden_paths": [],
            "required_inputs": [],
            "required_outputs": [{"path": "pyproject.toml"}],
            "required_checks": [{"id": "test", "argv": ["python"]}],
            "acceptance_criteria": ["All pass"],
            "known_constraints": [],
            "status": "approved",
            "supersedes_work_order_id": "invalid-id-format"
        })
        self.assertTrue(any("supersedes_work_order_id" in e["path"] for e in errors))

        # Test handoff with invalid based_on_checkpoint_id (must be stable ID or null)
        errors2 = validate("handoff", {
            "schema_version": 1,
            "id": "HANDOFF-0001",
            "task_id": "TASK-0001",
            "stage_id": "STAGE-0001",
            "work_order_id": "WORK-0001",
            "kind": "working",
            "based_on_checkpoint_id": "invalid-checkpoint-id",
            "completed": [],
            "remaining": [],
            "unverified": [],
            "changed_files": [],
            "checks": [],
            "risks": [],
            "next_action": "Proceed",
            "source_fingerprint": {
                "git_head": "abc1234567890123456789012345678901234567",
                "staged_diff_sha256": None,
                "unstaged_diff_sha256": None,
                "untracked_files": [],
                "captured_at": "2026-07-17T15:00:00+08:00"
            },
            "created_at": "2026-07-17T15:00:00+08:00"
        })
        self.assertTrue(any("based_on_checkpoint_id" in e["path"] for e in errors2))

    def test_ref_resolution_error_safety(self) -> None:
        """Verify that disallowed and unresolved references do not leak tracebacks."""
        from continuity.schemas.registry import _collect_errors
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "urn:test:schema",
            "type": "object",
            "properties": {
                "ref_prop": { "$ref": "urn:continuity:schema:common:1#/$defs/stable_id" }
            }
        }
        errors = _collect_errors({"ref_prop": "TASK-0001"}, schema, None)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["code"], "ref_resolution")
        self.assertEqual(errors[0]["keyword"], "ref_resolution")
        self.assertEqual(errors[0]["path"], "<root>")

    def test_ref_validation_security_boundary(self) -> None:
        """Verify that disallowed $refs are rejected before any network/filesystem reads."""
        from continuity.schemas.registry import _validate_refs
        import unittest.mock

        bad_refs = [
            "https://example.invalid/schema.json",
            "file:///tmp/schema.json",
            "other.schema.json#/$defs/x",
            "urn:continuity:schema:not-registered:1"
        ]

        for bad_ref in bad_refs:
            with self.subTest(bad_ref=bad_ref):
                corrupt_schema = {
                    "$schema": "https://json-schema.org/draft/2020-12/schema",
                    "$id": "urn:continuity:schema:test:1",
                    "type": "object",
                    "properties": {
                        "field": { "$ref": bad_ref }
                    }
                }
                with unittest.mock.patch("importlib.resources.files") as mock_files:
                    with self.assertRaises(ValueError):
                        _validate_refs(corrupt_schema, "test")
                    mock_files.assert_not_called()


if __name__ == "__main__":
    unittest.main()
