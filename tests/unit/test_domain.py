"""Tests for continuity.domain — state transitions and cross-entity invariants.

Covers:
  - All legal and illegal state transition edges for task, stage, work_order.
  - Unknown entity type fail-closed behaviour.
  - Unknown source/target status fail-closed behaviour.
  - Self-loop transitions.
  - Cross-entity invariant checks:
      - Pointer existence (dangling pointers).
      - Single-active constraint.
      - Parent-child ownership.
      - Handoff ownership.
      - Evidence ↔ Review Pack fingerprint consistency.
      - Stale evidence in fresh pack.
      - Review Decision binding (pack existence, manifest match).
      - Duplicate decision per gate per pack.
      - Stage approval precondition.
      - Task final-review precondition.
  - Stable (path, code) sorting of violations.
  - Dict insertion-order independence for identical violation sequences.
  - Input deep-equality immutability.
"""

from __future__ import annotations

import copy
import unittest

from continuity.domain import (
    DomainViolation,
    can_transition,
    validate_invariants,
    validate_transition,
)
from continuity.domain.transitions import (
    _ENTITY_REGISTRY,
    _STAGE_TRANSITIONS,
    _TASK_TRANSITIONS,
    _WORK_ORDER_TRANSITIONS,
    valid_statuses,
    valid_transitions,
)


# ── Helpers ──────────────────────────────────────────────────────────────


def _violation_codes(violations: list[DomainViolation]) -> list[str]:
    """Extract just the codes from a violation list."""
    return [v.code for v in violations]


def _violation_tuples(
    violations: list[DomainViolation],
) -> list[tuple[str, str]]:
    """Extract (path, code) pairs."""
    return [(v.path, v.code) for v in violations]


# ── Explicit expected transition sets (F-55-KF-004) ──────────────────────

EXPECTED_TASK_TRANSITIONS = frozenset({
    ("draft", "ready"),
    ("ready", "active"),
    ("active", "ready_for_final_review"),
    ("active", "blocked"),
    ("active", "cancelled"),
    ("blocked", "active"),
    ("ready_for_final_review", "approved_for_merge"),
    ("approved_for_merge", "completed"),
})

EXPECTED_STAGE_TRANSITIONS = frozenset({
    ("planned", "active"),
    ("active", "ready_for_review"),
    ("active", "blocked"),
    ("blocked", "active"),
    ("ready_for_review", "approved"),
    ("ready_for_review", "changes_requested"),
    ("ready_for_review", "active"),
    ("changes_requested", "active"),
    ("approved", "completed"),
})

EXPECTED_WORK_ORDER_TRANSITIONS = frozenset({
    ("draft", "approved"),
    ("approved", "active"),
    ("approved", "superseded"),
    ("active", "superseded"),
    ("active", "completed"),
})


# ── Transition tests ─────────────────────────────────────────────────────


class TestCanTransition(unittest.TestCase):
    """Test can_transition for all entity types against hardcoded expected transitions."""

    def test_all_legal_task_edges(self) -> None:
        for from_s, to_s in EXPECTED_TASK_TRANSITIONS:
            with self.subTest(edge=f"{from_s}→{to_s}"):
                self.assertTrue(can_transition("task", from_s, to_s))

    def test_all_legal_stage_edges(self) -> None:
        for from_s, to_s in EXPECTED_STAGE_TRANSITIONS:
            with self.subTest(edge=f"{from_s}→{to_s}"):
                self.assertTrue(can_transition("stage", from_s, to_s))

    def test_all_legal_work_order_edges(self) -> None:
        for from_s, to_s in EXPECTED_WORK_ORDER_TRANSITIONS:
            with self.subTest(edge=f"{from_s}→{to_s}"):
                self.assertTrue(can_transition("work_order", from_s, to_s))

    def test_illegal_task_skip(self) -> None:
        """draft → completed skips intermediates."""
        self.assertFalse(can_transition("task", "draft", "completed"))

    def test_illegal_task_reverse(self) -> None:
        """active → ready reverses direction."""
        self.assertFalse(can_transition("task", "active", "ready"))

    def test_illegal_stage_reverse(self) -> None:
        """approved → active reverses direction."""
        self.assertFalse(can_transition("stage", "approved", "active"))

    def test_illegal_work_order_reverse(self) -> None:
        """completed → active reverses direction."""
        self.assertFalse(can_transition("work_order", "completed", "active"))

    def test_self_loop_task(self) -> None:
        """active → active is not a declared edge."""
        self.assertFalse(can_transition("task", "active", "active"))

    def test_self_loop_stage(self) -> None:
        self.assertFalse(can_transition("stage", "active", "active"))

    def test_self_loop_work_order(self) -> None:
        self.assertFalse(can_transition("work_order", "active", "active"))

    def test_unknown_entity_returns_false(self) -> None:
        """Fail-closed: unknown entity → False."""
        self.assertFalse(can_transition("unknown", "a", "b"))

    def test_unknown_entity_various(self) -> None:
        self.assertFalse(can_transition("widget", "draft", "ready"))
        self.assertFalse(can_transition("", "draft", "ready"))


class TestValidateTransition(unittest.TestCase):
    """Test validate_transition for structured error returns."""

    def test_legal_edge_returns_empty(self) -> None:
        result = validate_transition("task", "draft", "ready")
        self.assertEqual(result, [])

    def test_unknown_entity_returns_violation(self) -> None:
        result = validate_transition("unknown", "a", "b")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].code, "UNKNOWN_ENTITY")
        self.assertIn("unknown", result[0].path)

    def test_unknown_source_status(self) -> None:
        result = validate_transition("task", "nonexistent", "ready")
        codes = _violation_codes(result)
        self.assertIn("UNKNOWN_STATUS", codes)

    def test_unknown_target_status(self) -> None:
        result = validate_transition("task", "draft", "nonexistent")
        codes = _violation_codes(result)
        self.assertIn("UNKNOWN_STATUS", codes)

    def test_both_unknown_statuses(self) -> None:
        result = validate_transition("stage", "foo", "bar")
        codes = _violation_codes(result)
        self.assertEqual(codes.count("UNKNOWN_STATUS"), 2)

    def test_illegal_edge_returns_violation(self) -> None:
        result = validate_transition("task", "draft", "completed")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].code, "ILLEGAL_TRANSITION")

    def test_violations_sorted_by_path_code(self) -> None:
        result = validate_transition("stage", "foo", "bar")
        keys = [(v.path, v.code) for v in result]
        self.assertEqual(keys, sorted(keys))


class TestValidStatuses(unittest.TestCase):
    """Test the valid_statuses helper."""

    def test_task_statuses(self) -> None:
        s = valid_statuses("task")
        self.assertIsNotNone(s)
        self.assertIn("draft", s)
        self.assertIn("completed", s)
        self.assertIn("approved_for_merge", s)

    def test_unknown_entity_returns_none(self) -> None:
        self.assertIsNone(valid_statuses("bogus"))

    def test_stage_statuses(self) -> None:
        s = valid_statuses("stage")
        self.assertIsNotNone(s)
        self.assertIn("planned", s)
        self.assertIn("approved", s)

    def test_work_order_statuses(self) -> None:
        s = valid_statuses("work_order")
        self.assertIsNotNone(s)
        self.assertIn("draft", s)
        self.assertIn("superseded", s)


class TestValidTransitions(unittest.TestCase):
    """Test the valid_transitions helper."""

    def test_task_transitions(self) -> None:
        t = valid_transitions("task")
        self.assertIsNotNone(t)
        self.assertEqual(t, EXPECTED_TASK_TRANSITIONS)

    def test_stage_transitions(self) -> None:
        t = valid_transitions("stage")
        self.assertIsNotNone(t)
        self.assertEqual(t, EXPECTED_STAGE_TRANSITIONS)

    def test_work_order_transitions(self) -> None:
        t = valid_transitions("work_order")
        self.assertIsNotNone(t)
        self.assertEqual(t, EXPECTED_WORK_ORDER_TRANSITIONS)

    def test_unknown_entity_returns_none(self) -> None:
        self.assertIsNone(valid_transitions("bogus"))


# ── Invariant tests ──────────────────────────────────────────────────────


def _minimal_current(**overrides: object) -> dict:
    """Build a minimal current.json mapping."""
    base = {
        "schema_version": 1,
        "state_revision": 1,
        "active_task_id": None,
        "active_stage_id": None,
        "active_work_order_id": None,
        "latest_checkpoint_id": None,
        "latest_handoff_id": None,
        "latest_context_id": None,
        "active_review_pack_id": None,
        "latest_transfer_id": None,
        "task_final_review_pack_id": None,
        "active_task_branch": None,
        "updated_at": "2026-01-01T00:00:00+08:00",
    }
    base.update(overrides)
    return base


def _minimal_task(
    task_id: str = "TASK-0001",
    status: str = "active",
) -> dict:
    return {
        "schema_version": 1,
        "id": task_id,
        "title": "Test task",
        "goal": "Test goal",
        "scope_in": ["src/"],
        "scope_out": [],
        "acceptance_criteria": ["Done"],
        "status": status,
        "created_at": "2026-01-01T00:00:00+08:00",
        "updated_at": "2026-01-01T00:00:00+08:00",
    }


def _minimal_stage(
    stage_id: str = "STAGE-01",
    task_id: str = "TASK-0001",
    status: str = "active",
    review_gates: list[str] | None = None,
) -> dict:
    return {
        "schema_version": 1,
        "id": stage_id,
        "task_id": task_id,
        "title": "Test stage",
        "goal": "Test goal",
        "acceptance_criteria": ["Done"],
        "dependencies": [],
        "allowed_paths": ["src/"],
        "required_checks": [],
        "review_gates": review_gates or ["GATE-01", "GATE-02"],
        "risk_level": "normal",
        "risk_reasons": [],
        "status": status,
        "created_at": "2026-01-01T00:00:00+08:00",
        "updated_at": "2026-01-01T00:00:00+08:00",
    }


def _minimal_work_order(
    wo_id: str = "WORK-0001",
    task_id: str = "TASK-0001",
    stage_id: str = "STAGE-01",
    status: str = "active",
) -> dict:
    return {
        "schema_version": 1,
        "id": wo_id,
        "task_id": task_id,
        "stage_id": stage_id,
        "status": status,
    }


def _minimal_handoff(
    handoff_id: str = "HANDOFF-0001",
    task_id: str = "TASK-0001",
    stage_id: str = "STAGE-01",
    work_order_id: str = "WORK-0001",
) -> dict:
    return {
        "id": handoff_id,
        "task_id": task_id,
        "stage_id": stage_id,
        "work_order_id": work_order_id,
        "kind": "working",
    }


def _minimal_evidence(
    ev_id: str = "EV-0001",
    task_id: str = "TASK-0001",
    stage_id: str = "STAGE-01",
    status: str = "fresh",
    source_fingerprint: dict | None = None,
) -> dict:
    return {
        "id": ev_id,
        "task_id": task_id,
        "stage_id": stage_id,
        "status": status,
        "capture_mode": "captured",
        "source_fingerprint": source_fingerprint or {"git_head": "abc123"},
    }


def _minimal_review_pack(
    pack_id: str = "PACK-0001",
    task_id: str = "TASK-0001",
    stage_id: str | None = "STAGE-01",
    scope: str = "stage",
    status: str = "fresh",
    manifest_sha256: str = "sha_aaa",
    source_fingerprint: dict | None = None,
    evidence_ids: list[str] | None = None,
) -> dict:
    return {
        "id": pack_id,
        "task_id": task_id,
        "stage_id": stage_id,
        "scope": scope,
        "status": status,
        "manifest_sha256": manifest_sha256,
        "source_fingerprint": source_fingerprint or {"git_head": "abc123"},
        "evidence_ids": evidence_ids or [],
    }


def _minimal_review_decision(
    decision_id: str = "RD-0001",
    pack_id: str = "PACK-0001",
    manifest_sha256: str = "sha_aaa",
    gate_id: str = "GATE-01",
    verdict: str = "approve",
    round: int | None = 1,
    created_at: str | None = "2026-01-01T00:00:00+08:00",
) -> dict:
    d = {
        "id": decision_id,
        "pack_id": pack_id,
        "manifest_sha256": manifest_sha256,
        "gate_id": gate_id,
        "verdict": verdict,
    }
    if round is not None:
        d["round"] = round
    if created_at is not None:
        d["created_at"] = created_at
    return d


def _make_entities(**overrides: object) -> dict:
    """Build minimal entities dict with optional overrides."""
    base: dict = {
        "tasks": [],
        "stages": [],
        "work_orders": [],
        "handoffs": [],
        "evidence_list": [],
        "review_packs": [],
        "review_decisions": [],
    }
    base.update(overrides)
    return base


class TestPointerExistence(unittest.TestCase):
    """current.json pointer references must exist (F-55-KF-001)."""

    def test_null_pointers_are_clean(self) -> None:
        current = _minimal_current()
        entities = _make_entities()
        result = validate_invariants(current, entities)
        self.assertEqual(result, [])

    def test_dangling_task_pointer(self) -> None:
        current = _minimal_current(active_task_id="TASK-9999")
        entities = _make_entities()
        result = validate_invariants(current, entities)
        codes = _violation_codes(result)
        self.assertIn("DANGLING_POINTER", codes)

    def test_dangling_stage_pointer(self) -> None:
        current = _minimal_current(active_stage_id="STAGE-9999")
        entities = _make_entities()
        result = validate_invariants(current, entities)
        codes = _violation_codes(result)
        self.assertIn("DANGLING_POINTER", codes)

    def test_dangling_work_order_pointer(self) -> None:
        current = _minimal_current(active_work_order_id="WORK-9999")
        entities = _make_entities()
        result = validate_invariants(current, entities)
        codes = _violation_codes(result)
        self.assertIn("DANGLING_POINTER", codes)

    def test_dangling_latest_handoff_pointer(self) -> None:
        current = _minimal_current(latest_handoff_id="HANDOFF-MISSING")
        entities = _make_entities()
        result = validate_invariants(current, entities)
        codes = _violation_codes(result)
        self.assertIn("DANGLING_POINTER", codes)

    def test_dangling_active_review_pack_pointer(self) -> None:
        current = _minimal_current(active_review_pack_id="PACK-MISSING")
        entities = _make_entities()
        result = validate_invariants(current, entities)
        codes = _violation_codes(result)
        self.assertIn("DANGLING_POINTER", codes)

    def test_dangling_task_final_review_pack_pointer(self) -> None:
        current = _minimal_current(task_final_review_pack_id="PACK-MISSING")
        entities = _make_entities()
        result = validate_invariants(current, entities)
        codes = _violation_codes(result)
        self.assertIn("DANGLING_POINTER", codes)

    def test_valid_pointers_are_clean(self) -> None:
        current = _minimal_current(
            active_task_id="TASK-0001",
            active_stage_id="STAGE-01",
            active_work_order_id="WORK-0001",
            latest_handoff_id="HANDOFF-0001",
            active_review_pack_id="PACK-0001",
        )
        entities = _make_entities(
            tasks=[_minimal_task()],
            stages=[_minimal_stage()],
            work_orders=[_minimal_work_order()],
            handoffs=[_minimal_handoff()],
            review_packs=[_minimal_review_pack()],
        )
        result = validate_invariants(current, entities)
        self.assertEqual(result, [])


class TestSingleActive(unittest.TestCase):
    """At most one active entity of each primary kind."""

    def test_two_active_tasks(self) -> None:
        entities = _make_entities(tasks=[
            _minimal_task("TASK-0001", "active"),
            _minimal_task("TASK-0002", "active"),
        ])
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("MULTIPLE_ACTIVE", codes)

    def test_two_active_stages(self) -> None:
        entities = _make_entities(stages=[
            _minimal_stage("STAGE-01", status="active"),
            _minimal_stage("STAGE-02", status="active"),
        ])
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("MULTIPLE_ACTIVE", codes)

    def test_two_active_work_orders(self) -> None:
        entities = _make_entities(work_orders=[
            _minimal_work_order("WORK-0001", status="active"),
            _minimal_work_order("WORK-0002", status="active"),
        ])
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("MULTIPLE_ACTIVE", codes)

    def test_one_active_one_completed_is_clean(self) -> None:
        entities = _make_entities(tasks=[
            _minimal_task("TASK-0001", "active"),
            _minimal_task("TASK-0002", "completed"),
        ])
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertNotIn("MULTIPLE_ACTIVE", codes)


class TestParentChild(unittest.TestCase):
    """Active Stage → Task; active WO → Task + Stage."""

    def test_stage_task_mismatch(self) -> None:
        current = _minimal_current(
            active_task_id="TASK-0001",
            active_stage_id="STAGE-01",
        )
        entities = _make_entities(
            tasks=[_minimal_task("TASK-0001")],
            stages=[_minimal_stage("STAGE-01", task_id="TASK-9999")],
        )
        result = validate_invariants(current, entities)
        codes = _violation_codes(result)
        self.assertIn("PARENT_MISMATCH", codes)

    def test_wo_task_mismatch(self) -> None:
        current = _minimal_current(
            active_task_id="TASK-0001",
            active_stage_id="STAGE-01",
            active_work_order_id="WORK-0001",
        )
        entities = _make_entities(
            tasks=[_minimal_task("TASK-0001")],
            stages=[_minimal_stage("STAGE-01")],
            work_orders=[_minimal_work_order(
                "WORK-0001", task_id="TASK-9999",
            )],
        )
        result = validate_invariants(current, entities)
        codes = _violation_codes(result)
        self.assertIn("PARENT_MISMATCH", codes)

    def test_wo_stage_mismatch(self) -> None:
        current = _minimal_current(
            active_task_id="TASK-0001",
            active_stage_id="STAGE-01",
            active_work_order_id="WORK-0001",
        )
        entities = _make_entities(
            tasks=[_minimal_task("TASK-0001")],
            stages=[_minimal_stage("STAGE-01")],
            work_orders=[_minimal_work_order(
                "WORK-0001", stage_id="STAGE-99",
            )],
        )
        result = validate_invariants(current, entities)
        codes = _violation_codes(result)
        self.assertIn("PARENT_MISMATCH", codes)


class TestHandoffOwnership(unittest.TestCase):
    """Handoff references must be to existing entities and active pointers (F-55-KF-002)."""

    def test_handoff_with_nonexistent_task(self) -> None:
        entities = _make_entities(
            handoffs=[_minimal_handoff(task_id="TASK-GONE")],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("DANGLING_REFERENCE", codes)

    def test_handoff_with_nonexistent_stage(self) -> None:
        entities = _make_entities(
            tasks=[_minimal_task()],
            handoffs=[_minimal_handoff(stage_id="STAGE-GONE")],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("DANGLING_REFERENCE", codes)

    def test_handoff_with_nonexistent_wo(self) -> None:
        entities = _make_entities(
            tasks=[_minimal_task()],
            stages=[_minimal_stage()],
            handoffs=[_minimal_handoff(work_order_id="WORK-GONE")],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("DANGLING_REFERENCE", codes)

    def test_latest_handoff_ownership_mismatch(self) -> None:
        current = _minimal_current(
            active_task_id="TASK-0001",
            active_stage_id="STAGE-01",
            active_work_order_id="WORK-0001",
            latest_handoff_id="HANDOFF-0001",
        )
        entities = _make_entities(
            tasks=[_minimal_task("TASK-0001"), _minimal_task("TASK-0002")],
            stages=[_minimal_stage("STAGE-01"), _minimal_stage("STAGE-02")],
            work_orders=[_minimal_work_order("WORK-0001"), _minimal_work_order("WORK-0002")],
            handoffs=[_minimal_handoff(
                handoff_id="HANDOFF-0001",
                task_id="TASK-0002",
                stage_id="STAGE-02",
                work_order_id="WORK-0002",
            )],
        )
        result = validate_invariants(current, entities)
        codes = _violation_codes(result)
        self.assertIn("HANDOFF_OWNERSHIP_MISMATCH", codes)

    def test_valid_handoff_is_clean(self) -> None:
        current = _minimal_current(
            active_task_id="TASK-0001",
            active_stage_id="STAGE-01",
            active_work_order_id="WORK-0001",
            latest_handoff_id="HANDOFF-0001",
        )
        entities = _make_entities(
            tasks=[_minimal_task()],
            stages=[_minimal_stage()],
            work_orders=[_minimal_work_order()],
            handoffs=[_minimal_handoff()],
        )
        result = validate_invariants(current, entities)
        codes = _violation_codes(result)
        self.assertNotIn("DANGLING_REFERENCE", codes)
        self.assertNotIn("HANDOFF_OWNERSHIP_MISMATCH", codes)


class TestEvidencePackConsistency(unittest.TestCase):
    """Evidence ↔ Review Pack must share task, stage, fingerprint."""

    def test_task_id_mismatch(self) -> None:
        entities = _make_entities(
            evidence_list=[_minimal_evidence(task_id="TASK-OTHER")],
            review_packs=[_minimal_review_pack(evidence_ids=["EV-0001"])],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("EVIDENCE_PACK_TASK_MISMATCH", codes)

    def test_stage_id_mismatch(self) -> None:
        entities = _make_entities(
            evidence_list=[_minimal_evidence(stage_id="STAGE-OTHER")],
            review_packs=[_minimal_review_pack(evidence_ids=["EV-0001"])],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("EVIDENCE_PACK_STAGE_MISMATCH", codes)

    def test_fingerprint_mismatch(self) -> None:
        entities = _make_entities(
            evidence_list=[_minimal_evidence(
                source_fingerprint={"git_head": "different"},
            )],
            review_packs=[_minimal_review_pack(
                evidence_ids=["EV-0001"],
                source_fingerprint={"git_head": "abc123"},
            )],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("FINGERPRINT_MISMATCH", codes)

    def test_stale_evidence_in_fresh_pack(self) -> None:
        entities = _make_entities(
            evidence_list=[_minimal_evidence(status="stale")],
            review_packs=[_minimal_review_pack(
                status="fresh",
                evidence_ids=["EV-0001"],
            )],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("STALE_EVIDENCE_IN_FRESH_PACK", codes)

    def test_consistent_evidence_is_clean(self) -> None:
        fp = {"git_head": "abc123"}
        entities = _make_entities(
            evidence_list=[_minimal_evidence(source_fingerprint=fp)],
            review_packs=[_minimal_review_pack(
                evidence_ids=["EV-0001"],
                source_fingerprint=fp,
            )],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertNotIn("EVIDENCE_PACK_TASK_MISMATCH", codes)
        self.assertNotIn("FINGERPRINT_MISMATCH", codes)
        self.assertNotIn("STALE_EVIDENCE_IN_FRESH_PACK", codes)

    def test_nonexistent_evidence_in_pack(self) -> None:
        entities = _make_entities(
            evidence_list=[],
            review_packs=[_minimal_review_pack(
                evidence_ids=["EV-GONE"],
            )],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("DANGLING_REFERENCE", codes)


class TestDecisionBinding(unittest.TestCase):
    """Review Decision must bind to existing pack and consistent manifest."""

    def test_dangling_pack_reference(self) -> None:
        entities = _make_entities(
            review_decisions=[_minimal_review_decision(pack_id="PACK-GONE")],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("DANGLING_REFERENCE", codes)

    def test_manifest_mismatch(self) -> None:
        entities = _make_entities(
            review_packs=[_minimal_review_pack(manifest_sha256="sha_aaa")],
            review_decisions=[_minimal_review_decision(
                manifest_sha256="sha_bbb",
            )],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("MANIFEST_MISMATCH", codes)

    def test_duplicate_gate_decision(self) -> None:
        entities = _make_entities(
            review_packs=[_minimal_review_pack()],
            review_decisions=[
                _minimal_review_decision("RD-0001", gate_id="GATE-01"),
                _minimal_review_decision("RD-0002", gate_id="GATE-01"),
            ],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("DUPLICATE_GATE_DECISION", codes)

    def test_valid_decision_is_clean(self) -> None:
        entities = _make_entities(
            review_packs=[_minimal_review_pack()],
            review_decisions=[_minimal_review_decision()],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertNotIn("DANGLING_REFERENCE", codes)
        self.assertNotIn("MANIFEST_MISMATCH", codes)
        self.assertNotIn("DUPLICATE_GATE_DECISION", codes)


class TestStageApproval(unittest.TestCase):
    """Approved stage must have all required gates approved on same fresh pack (F-55-KF-003)."""

    def test_approved_without_pack(self) -> None:
        entities = _make_entities(
            stages=[_minimal_stage(status="approved")],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("MISSING_REVIEW_PACK", codes)

    def test_approved_with_stale_pack(self) -> None:
        entities = _make_entities(
            stages=[_minimal_stage(status="approved")],
            review_packs=[_minimal_review_pack(status="stale")],
            review_decisions=[
                _minimal_review_decision(gate_id="GATE-01"),
                _minimal_review_decision("RD-02", gate_id="GATE-02"),
            ],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("STAGE_APPROVAL_PRECONDITION_UNMET", codes)

    def test_approved_missing_gate(self) -> None:
        """Only GATE-01 approved, but GATE-02 also required."""
        entities = _make_entities(
            stages=[_minimal_stage(status="approved")],
            review_packs=[_minimal_review_pack(status="fresh")],
            review_decisions=[
                _minimal_review_decision(gate_id="GATE-01"),
            ],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("STAGE_APPROVAL_PRECONDITION_UNMET", codes)

    def test_approved_wrong_gate_order(self) -> None:
        """GATE-02 before GATE-01 must be rejected (F-55-KF-003)."""
        entities = _make_entities(
            stages=[_minimal_stage(status="approved", review_gates=["GATE-01", "GATE-02"])],
            review_packs=[_minimal_review_pack(status="fresh")],
            review_decisions=[
                _minimal_review_decision("RD-02", gate_id="GATE-02", round=1),
                _minimal_review_decision("RD-01", gate_id="GATE-01", round=2),
            ],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("STAGE_APPROVAL_PRECONDITION_UNMET", codes)

    def test_approved_active_review_pack_mismatch(self) -> None:
        """current.active_review_pack_id mismatch must be rejected (F-55-KF-003)."""
        current = _minimal_current(active_review_pack_id="PACK-0002")
        entities = _make_entities(
            stages=[_minimal_stage(status="approved")],
            review_packs=[
                _minimal_review_pack(pack_id="PACK-0001", status="fresh"),
                _minimal_review_pack(pack_id="PACK-0002", status="fresh"),
            ],
            review_decisions=[
                _minimal_review_decision(pack_id="PACK-0001", gate_id="GATE-01"),
                _minimal_review_decision("RD-02", pack_id="PACK-0001", gate_id="GATE-02"),
            ],
        )
        result = validate_invariants(current, entities)
        codes = _violation_codes(result)
        self.assertIn("STAGE_APPROVAL_PRECONDITION_UNMET", codes)

    def test_approved_with_changes_requested(self) -> None:
        """One gate approved, one changes_requested."""
        entities = _make_entities(
            stages=[_minimal_stage(status="approved")],
            review_packs=[_minimal_review_pack(status="fresh")],
            review_decisions=[
                _minimal_review_decision(gate_id="GATE-01"),
                _minimal_review_decision(
                    "RD-02", gate_id="GATE-02",
                    verdict="changes_requested",
                ),
            ],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("STAGE_APPROVAL_PRECONDITION_UNMET", codes)

    def test_approved_with_manifest_mismatch_on_gate(self) -> None:
        """Gate decision manifest doesn't match pack manifest."""
        entities = _make_entities(
            stages=[_minimal_stage(status="approved")],
            review_packs=[_minimal_review_pack(
                status="fresh",
                manifest_sha256="sha_aaa",
            )],
            review_decisions=[
                _minimal_review_decision(
                    gate_id="GATE-01", manifest_sha256="sha_aaa",
                ),
                _minimal_review_decision(
                    "RD-02", gate_id="GATE-02",
                    manifest_sha256="sha_wrong",
                ),
            ],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("STAGE_APPROVAL_PRECONDITION_UNMET", codes)

    def test_fully_approved_stage_is_clean(self) -> None:
        """All required gates approved on same fresh pack in sequence."""
        entities = _make_entities(
            stages=[_minimal_stage(status="approved")],
            review_packs=[_minimal_review_pack(status="fresh")],
            review_decisions=[
                _minimal_review_decision(gate_id="GATE-01", round=1),
                _minimal_review_decision("RD-02", gate_id="GATE-02", round=2),
            ],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertNotIn("STAGE_APPROVAL_PRECONDITION_UNMET", codes)
        self.assertNotIn("MISSING_REVIEW_PACK", codes)


    def test_high_risk_stage_requires_gate_03(self) -> None:
        """High-risk stage needs GATE-01, GATE-02, GATE-03."""
        entities = _make_entities(
            stages=[_minimal_stage(
                status="approved",
                review_gates=["GATE-01", "GATE-02", "GATE-03"],
            )],
            review_packs=[_minimal_review_pack(status="fresh")],
            review_decisions=[
                _minimal_review_decision(gate_id="GATE-01"),
                _minimal_review_decision("RD-02", gate_id="GATE-02"),
                # GATE-03 missing
            ],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("STAGE_APPROVAL_PRECONDITION_UNMET", codes)


class TestTaskFinal(unittest.TestCase):
    """Task approved_for_merge preconditions."""

    def test_approved_for_merge_without_stage_completion(self) -> None:
        entities = _make_entities(
            tasks=[_minimal_task(status="approved_for_merge")],
            stages=[_minimal_stage(status="active")],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("STAGES_NOT_COMPLETE", codes)

    def test_approved_for_merge_without_task_final(self) -> None:
        entities = _make_entities(
            tasks=[_minimal_task(status="approved_for_merge")],
            stages=[_minimal_stage(status="approved")],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("TASK_FINAL_PRECONDITION_UNMET", codes)

    def test_approved_for_merge_with_stale_task_pack(self) -> None:
        entities = _make_entities(
            tasks=[_minimal_task(status="approved_for_merge")],
            stages=[_minimal_stage(status="approved")],
            review_packs=[_minimal_review_pack(
                pack_id="TPACK-01",
                scope="task",
                stage_id=None,
                status="stale",
            )],
            review_decisions=[_minimal_review_decision(
                pack_id="TPACK-01",
                gate_id="TASK-FINAL",
            )],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertIn("TASK_FINAL_PRECONDITION_UNMET", codes)

    def test_fully_approved_task_is_clean(self) -> None:
        entities = _make_entities(
            tasks=[_minimal_task(status="approved_for_merge")],
            stages=[_minimal_stage(status="approved")],
            review_packs=[_minimal_review_pack(
                pack_id="TPACK-01",
                scope="task",
                stage_id=None,
                status="fresh",
            )],
            review_decisions=[_minimal_review_decision(
                pack_id="TPACK-01",
                gate_id="TASK-FINAL",
            )],
        )
        result = validate_invariants(_minimal_current(), entities)
        codes = _violation_codes(result)
        self.assertNotIn("STAGES_NOT_COMPLETE", codes)
        self.assertNotIn("TASK_FINAL_PRECONDITION_UNMET", codes)


# ── Stability and immutability tests ─────────────────────────────────────


class TestViolationSortingStability(unittest.TestCase):
    """All violations are sorted stably by (path, code)."""

    def test_violations_are_sorted(self) -> None:
        """Generate multiple violations and verify sort order."""
        current = _minimal_current(
            active_task_id="TASK-GONE",
            active_stage_id="STAGE-GONE",
            active_work_order_id="WORK-GONE",
        )
        entities = _make_entities()
        result = validate_invariants(current, entities)
        keys = _violation_tuples(result)
        self.assertEqual(keys, sorted(keys))
        # Should have at least 3 DANGLING_POINTER violations
        self.assertGreaterEqual(len(result), 3)

    def test_dict_insertion_order_independence(self) -> None:
        """Same data with reversed key order → identical violations."""
        # Forward order
        current1 = {
            "active_task_id": "TASK-GONE",
            "active_stage_id": "STAGE-GONE",
            "active_work_order_id": "WORK-GONE",
        }
        # Reverse order
        current2 = {
            "active_work_order_id": "WORK-GONE",
            "active_stage_id": "STAGE-GONE",
            "active_task_id": "TASK-GONE",
        }
        entities = _make_entities()

        r1 = validate_invariants(current1, entities)
        r2 = validate_invariants(current2, entities)
        self.assertEqual(r1, r2)

    def test_entity_list_order_independence(self) -> None:
        """Entities in different list order → identical violations."""
        ent1 = _make_entities(tasks=[
            _minimal_task("TASK-0001", "active"),
            _minimal_task("TASK-0002", "active"),
        ])
        ent2 = _make_entities(tasks=[
            _minimal_task("TASK-0002", "active"),
            _minimal_task("TASK-0001", "active"),
        ])
        r1 = validate_invariants(_minimal_current(), ent1)
        r2 = validate_invariants(_minimal_current(), ent2)
        self.assertEqual(
            _violation_tuples(r1),
            _violation_tuples(r2),
        )


class TestInputImmutability(unittest.TestCase):
    """validate_invariants must not mutate its inputs."""

    def test_current_not_mutated(self) -> None:
        current = _minimal_current(active_task_id="TASK-0001")
        current_copy = copy.deepcopy(current)
        entities = _make_entities(tasks=[_minimal_task()])
        validate_invariants(current, entities)
        self.assertEqual(current, current_copy)

    def test_entities_not_mutated(self) -> None:
        current = _minimal_current()
        entities = _make_entities(
            tasks=[_minimal_task()],
            stages=[_minimal_stage()],
            work_orders=[_minimal_work_order()],
            handoffs=[_minimal_handoff()],
        )
        entities_copy = copy.deepcopy(entities)
        validate_invariants(current, entities)
        self.assertEqual(entities, entities_copy)

    def test_transition_input_not_mutated(self) -> None:
        """validate_transition does not mutate anything (trivially true
        for str args, but verify no global-state side effects)."""
        result1 = validate_transition("task", "draft", "ready")
        result2 = validate_transition("task", "draft", "ready")
        self.assertEqual(result1, result2)


class TestDomainViolationStructure(unittest.TestCase):
    """DomainViolation is frozen, hashable, and has correct sort_key."""

    def test_frozen(self) -> None:
        v = DomainViolation(path="a", code="B", message="c")
        with self.assertRaises(AttributeError):
            v.path = "x"  # type: ignore[misc]

    def test_hashable(self) -> None:
        v = DomainViolation(path="a", code="B", message="c")
        # Should not raise
        hash(v)

    def test_sort_key(self) -> None:
        v = DomainViolation(path="x", code="Y", message="z")
        self.assertEqual(v.sort_key(), ("x", "Y"))

    def test_equality(self) -> None:
        v1 = DomainViolation(path="a", code="B", message="c")
        v2 = DomainViolation(path="a", code="B", message="c")
        self.assertEqual(v1, v2)

    def test_inequality(self) -> None:
        v1 = DomainViolation(path="a", code="B", message="c")
        v2 = DomainViolation(path="a", code="C", message="c")
        self.assertNotEqual(v1, v2)


if __name__ == "__main__":
    unittest.main()
