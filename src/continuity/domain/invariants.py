"""Cross-entity invariant validation for Continuity.

Every function in this module is a pure computation:

* No file I/O, network, Git, time, or environment-variable access.
* No mutation of arguments — all inputs are treated as read-only.
* Errors are returned as sorted lists of
  :class:`~continuity.domain.errors.DomainViolation`, never raised,
  printed, or expressed via ``assert`` / ``sys.exit``.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from continuity.domain.errors import DomainViolation

# ── Type aliases (documentation only; no runtime enforcement) ────────────

# A "mapping" is any dict-like object with string keys.
# An "entity list" is a sequence of such mappings.

# ── Internal helpers ─────────────────────────────────────────────────────


def _get(mapping: Mapping[str, Any], key: str, default: Any = None) -> Any:
    """Read-only accessor — never mutates *mapping*."""
    return mapping.get(key, default)


def _index_by(
    records: Sequence[Mapping[str, Any]],
    key: str,
) -> dict[str, Mapping[str, Any]]:
    """Build a lookup dict keyed by *key*.  Last-write-wins for duplicates."""
    return {r[key]: r for r in records if key in r}


# ── Pointer-existence checks ─────────────────────────────────────────────


def _check_pointer_existence(
    current: Mapping[str, Any],
    entities: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[DomainViolation]:
    """All non-null pointers in ``current`` must reference existing entities."""
    violations: list[DomainViolation] = []

    pointer_targets: list[tuple[str, str, str]] = [
        ("active_task_id", "tasks", "id"),
        ("active_stage_id", "stages", "id"),
        ("active_work_order_id", "work_orders", "id"),
        ("latest_checkpoint_id", "checkpoints", "id"),
        ("latest_handoff_id", "handoffs", "id"),
        ("latest_context_id", "context_packs", "id"),
        ("active_review_pack_id", "review_packs", "id"),
        ("latest_transfer_id", "transfers", "id"),
        ("task_final_review_pack_id", "review_packs", "id"),
    ]

    for pointer_key, collection_key, id_field in pointer_targets:
        pointer_value = _get(current, pointer_key)
        if pointer_value is None:
            continue  # null pointer is valid

        # If collection key is in entities mapping, verify existence.
        # If collection key is omitted in entities, skip (optional collection provided by caller).
        if collection_key in entities:
            collection = _get(entities, collection_key, ())
            ids = {_get(r, id_field) for r in collection}
            if pointer_value not in ids:
                violations.append(DomainViolation(
                    path=f"current.{pointer_key}",
                    code="DANGLING_POINTER",
                    message=(
                        f"current.{pointer_key} references "
                        f"{pointer_value!r} which does not exist "
                        f"in {collection_key}"
                    ),
                ))

    return violations


# ── Single-active checks ────────────────────────────────────────────────


def _check_single_active(
    entities: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[DomainViolation]:
    """At most one ``active`` entity of each primary kind."""
    violations: list[DomainViolation] = []

    checks: list[tuple[str, str]] = [
        ("tasks", "task"),
        ("stages", "stage"),
        ("work_orders", "work_order"),
    ]

    for collection_key, entity_label in checks:
        collection = _get(entities, collection_key, ())
        active_ids = [
            _get(r, "id", "<unknown>")
            for r in collection
            if _get(r, "status") == "active"
        ]
        if len(active_ids) > 1:
            violations.append(DomainViolation(
                path=f"{entity_label}.status",
                code="MULTIPLE_ACTIVE",
                message=(
                    f"Multiple active {entity_label}s found: "
                    f"{active_ids!r}"
                ),
            ))

    return violations


# ── Parent-child ownership ───────────────────────────────────────────────


def _check_parent_child(
    current: Mapping[str, Any],
    entities: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[DomainViolation]:
    """Active Stage belongs to active Task; active WO belongs to both."""
    violations: list[DomainViolation] = []

    active_task_id = _get(current, "active_task_id")
    active_stage_id = _get(current, "active_stage_id")
    active_wo_id = _get(current, "active_work_order_id")

    stages_index = _index_by(_get(entities, "stages", ()), "id")
    wo_index = _index_by(_get(entities, "work_orders", ()), "id")

    # Stage → Task
    if active_stage_id is not None and active_task_id is not None:
        stage = stages_index.get(active_stage_id)
        if stage is not None:
            if _get(stage, "task_id") != active_task_id:
                violations.append(DomainViolation(
                    path="stage.task_id",
                    code="PARENT_MISMATCH",
                    message=(
                        f"Active stage {active_stage_id!r} has "
                        f"task_id={_get(stage, 'task_id')!r} but "
                        f"active task is {active_task_id!r}"
                    ),
                ))

    # Work Order → Task + Stage
    if active_wo_id is not None:
        wo = wo_index.get(active_wo_id)
        if wo is not None:
            if active_task_id is not None and _get(wo, "task_id") != active_task_id:
                violations.append(DomainViolation(
                    path="work_order.task_id",
                    code="PARENT_MISMATCH",
                    message=(
                        f"Active work order {active_wo_id!r} has "
                        f"task_id={_get(wo, 'task_id')!r} but "
                        f"active task is {active_task_id!r}"
                    ),
                ))
            if active_stage_id is not None and _get(wo, "stage_id") != active_stage_id:
                violations.append(DomainViolation(
                    path="work_order.stage_id",
                    code="PARENT_MISMATCH",
                    message=(
                        f"Active work order {active_wo_id!r} has "
                        f"stage_id={_get(wo, 'stage_id')!r} but "
                        f"active stage is {active_stage_id!r}"
                    ),
                ))

    return violations


# ── Handoff ownership ────────────────────────────────────────────────────


def _check_handoff_ownership(
    current: Mapping[str, Any],
    entities: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[DomainViolation]:
    """Each Handoff's task_id, stage_id, work_order_id must exist, and
    if current.latest_handoff_id is set, the latest Handoff's ownership must
    match active task/stage/work_order pointers."""
    violations: list[DomainViolation] = []

    task_ids = {_get(r, "id") for r in _get(entities, "tasks", ())}
    stage_ids = {_get(r, "id") for r in _get(entities, "stages", ())}
    wo_ids = {_get(r, "id") for r in _get(entities, "work_orders", ())}

    handoffs_index = _index_by(_get(entities, "handoffs", ()), "id")

    for handoff in _get(entities, "handoffs", ()):
        h_id = _get(handoff, "id", "<unknown>")

        h_task = _get(handoff, "task_id")
        if h_task is not None and h_task not in task_ids:
            violations.append(DomainViolation(
                path=f"handoff[{h_id}].task_id",
                code="DANGLING_REFERENCE",
                message=(
                    f"Handoff {h_id!r} references non-existent "
                    f"task {h_task!r}"
                ),
            ))

        h_stage = _get(handoff, "stage_id")
        if h_stage is not None and h_stage not in stage_ids:
            violations.append(DomainViolation(
                path=f"handoff[{h_id}].stage_id",
                code="DANGLING_REFERENCE",
                message=(
                    f"Handoff {h_id!r} references non-existent "
                    f"stage {h_stage!r}"
                ),
            ))

        h_wo = _get(handoff, "work_order_id")
        if h_wo is not None and h_wo not in wo_ids:
            violations.append(DomainViolation(
                path=f"handoff[{h_id}].work_order_id",
                code="DANGLING_REFERENCE",
                message=(
                    f"Handoff {h_id!r} references non-existent "
                    f"work order {h_wo!r}"
                ),
            ))

    # Check active pointer consistency for latest_handoff_id
    latest_h_id = _get(current, "latest_handoff_id")
    if latest_h_id is not None:
        latest_h = handoffs_index.get(latest_h_id)
        if latest_h is not None:
            active_task_id = _get(current, "active_task_id")
            active_stage_id = _get(current, "active_stage_id")
            active_wo_id = _get(current, "active_work_order_id")

            if active_task_id is not None and _get(latest_h, "task_id") != active_task_id:
                violations.append(DomainViolation(
                    path="handoff.task_id",
                    code="HANDOFF_OWNERSHIP_MISMATCH",
                    message=(
                        f"Latest handoff {latest_h_id!r} has "
                        f"task_id={_get(latest_h, 'task_id')!r} but "
                        f"active task is {active_task_id!r}"
                    ),
                ))
            if active_stage_id is not None and _get(latest_h, "stage_id") != active_stage_id:
                violations.append(DomainViolation(
                    path="handoff.stage_id",
                    code="HANDOFF_OWNERSHIP_MISMATCH",
                    message=(
                        f"Latest handoff {latest_h_id!r} has "
                        f"stage_id={_get(latest_h, 'stage_id')!r} but "
                        f"active stage is {active_stage_id!r}"
                    ),
                ))
            if active_wo_id is not None and _get(latest_h, "work_order_id") != active_wo_id:
                violations.append(DomainViolation(
                    path="handoff.work_order_id",
                    code="HANDOFF_OWNERSHIP_MISMATCH",
                    message=(
                        f"Latest handoff {latest_h_id!r} has "
                        f"work_order_id={_get(latest_h, 'work_order_id')!r} but "
                        f"active work order is {active_wo_id!r}"
                    ),
                ))

    return violations


# ── Evidence ↔ Review Pack fingerprint consistency ───────────────────────


def _check_evidence_pack_consistency(
    entities: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[DomainViolation]:
    """Evidence referenced by a Review Pack must share task_id, stage_id,
    and source_fingerprint; stale Evidence cannot support a fresh Pack."""
    violations: list[DomainViolation] = []

    evidence_index = _index_by(_get(entities, "evidence_list", ()), "id")

    for pack in _get(entities, "review_packs", ()):
        pack_id = _get(pack, "id", "<unknown>")
        pack_task = _get(pack, "task_id")
        pack_stage = _get(pack, "stage_id")
        pack_fp = _get(pack, "source_fingerprint")
        pack_status = _get(pack, "status")
        pack_evidence_ids: Sequence[str] = _get(pack, "evidence_ids", ())

        for ev_id in pack_evidence_ids:
            ev = evidence_index.get(ev_id)
            if ev is None:
                violations.append(DomainViolation(
                    path=f"review_pack[{pack_id}].evidence_ids",
                    code="DANGLING_REFERENCE",
                    message=(
                        f"Review pack {pack_id!r} references "
                        f"non-existent evidence {ev_id!r}"
                    ),
                ))
                continue

            # task_id consistency
            if _get(ev, "task_id") != pack_task:
                violations.append(DomainViolation(
                    path=f"evidence[{ev_id}].task_id",
                    code="EVIDENCE_PACK_TASK_MISMATCH",
                    message=(
                        f"Evidence {ev_id!r} task_id "
                        f"{_get(ev, 'task_id')!r} does not match "
                        f"pack {pack_id!r} task_id {pack_task!r}"
                    ),
                ))

            # stage_id consistency
            if _get(ev, "stage_id") != pack_stage:
                violations.append(DomainViolation(
                    path=f"evidence[{ev_id}].stage_id",
                    code="EVIDENCE_PACK_STAGE_MISMATCH",
                    message=(
                        f"Evidence {ev_id!r} stage_id "
                        f"{_get(ev, 'stage_id')!r} does not match "
                        f"pack {pack_id!r} stage_id {pack_stage!r}"
                    ),
                ))

            # source_fingerprint consistency
            if pack_fp is not None and _get(ev, "source_fingerprint") != pack_fp:
                violations.append(DomainViolation(
                    path=f"evidence[{ev_id}].source_fingerprint",
                    code="FINGERPRINT_MISMATCH",
                    message=(
                        f"Evidence {ev_id!r} source_fingerprint "
                        f"does not match pack {pack_id!r}"
                    ),
                ))

            # Stale evidence cannot support a fresh pack
            if _get(ev, "status") == "stale" and pack_status == "fresh":
                violations.append(DomainViolation(
                    path=f"evidence[{ev_id}].status",
                    code="STALE_EVIDENCE_IN_FRESH_PACK",
                    message=(
                        f"Stale evidence {ev_id!r} cannot support "
                        f"fresh pack {pack_id!r}"
                    ),
                ))

    return violations


# ── Review Decision binding ──────────────────────────────────────────────


def _check_decision_binding(
    entities: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[DomainViolation]:
    """Each Decision must reference an existing Pack's pack_id and
    manifest_sha256; no two current decisions for the same gate on the
    same pack."""
    violations: list[DomainViolation] = []

    pack_index = _index_by(_get(entities, "review_packs", ()), "id")

    # Track (pack_id, gate_id) → decision_id for duplicate detection.
    seen: dict[tuple[str, str], str] = {}

    for decision in _get(entities, "review_decisions", ()):
        d_id = _get(decision, "id", "<unknown>")
        d_pack_id = _get(decision, "pack_id")
        d_manifest = _get(decision, "manifest_sha256")
        d_gate = _get(decision, "gate_id")

        # Pack existence
        if d_pack_id is not None:
            pack = pack_index.get(d_pack_id)
            if pack is None:
                violations.append(DomainViolation(
                    path=f"review_decision[{d_id}].pack_id",
                    code="DANGLING_REFERENCE",
                    message=(
                        f"Decision {d_id!r} references non-existent "
                        f"pack {d_pack_id!r}"
                    ),
                ))
            elif d_manifest is not None:
                # manifest_sha256 consistency
                if _get(pack, "manifest_sha256") != d_manifest:
                    violations.append(DomainViolation(
                        path=f"review_decision[{d_id}].manifest_sha256",
                        code="MANIFEST_MISMATCH",
                        message=(
                            f"Decision {d_id!r} manifest_sha256 "
                            f"does not match pack {d_pack_id!r}"
                        ),
                    ))

        # Duplicate gate per pack
        if d_pack_id is not None and d_gate is not None:
            dup_key = (d_pack_id, d_gate)
            if dup_key in seen:
                violations.append(DomainViolation(
                    path=f"review_decision[{d_id}].gate_id",
                    code="DUPLICATE_GATE_DECISION",
                    message=(
                        f"Duplicate decision for gate {d_gate!r} on "
                        f"pack {d_pack_id!r}: {seen[dup_key]!r} and "
                        f"{d_id!r}"
                    ),
                ))
            else:
                seen[dup_key] = d_id

    return violations


# ── Stage approval precondition ──────────────────────────────────────────


def _check_stage_approval(
    current: Mapping[str, Any],
    entities: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[DomainViolation]:
    """A stage with status ``approved`` must have ALL required review
    gates passing (verdict ``approve``) in strict sequential order on the
    SAME fresh pack with consistent ``manifest_sha256``.
    If current.active_review_pack_id is set, it must match the satisfying pack."""
    violations: list[DomainViolation] = []

    active_review_pack_id = _get(current, "active_review_pack_id")

    # Group decisions by pack_id preserving sequence
    decisions_by_pack: dict[str, list[Mapping[str, Any]]] = {}
    for d in _get(entities, "review_decisions", ()):
        p = _get(d, "pack_id")
        if p is not None:
            decisions_by_pack.setdefault(p, []).append(d)

    for stage in _get(entities, "stages", ()):
        if _get(stage, "status") != "approved":
            continue

        stage_id = _get(stage, "id", "<unknown>")
        required_gates: Sequence[str] = _get(stage, "review_gates", ())
        if not required_gates:
            continue  # nothing to check

        # Find the stage-scope review packs for this stage.
        stage_packs = [
            p for p in _get(entities, "review_packs", ())
            if _get(p, "stage_id") == stage_id
            and _get(p, "scope") == "stage"
        ]

        if not stage_packs:
            violations.append(DomainViolation(
                path=f"stage[{stage_id}].status",
                code="MISSING_REVIEW_PACK",
                message=(
                    f"Stage {stage_id!r} is approved but has no "
                    f"stage-scope review pack"
                ),
            ))
            continue

        # Check that at least one fresh pack satisfies approval.
        any_pack_satisfies = False

        for pack in stage_packs:
            pack_id = _get(pack, "id")
            pack_status = _get(pack, "status")
            pack_manifest = _get(pack, "manifest_sha256")

            if pack_status != "fresh":
                continue  # stale pack cannot satisfy approval

            # If current.active_review_pack_id is specified, the pack must match it
            if active_review_pack_id is not None and pack_id != active_review_pack_id:
                continue

            pack_decisions = decisions_by_pack.get(pack_id, [])

            # We must verify that decisions for required_gates appear in strict sequence.
            # Extract sequence of decisions matching required_gates.
            matching_decisions = [
                d for d in pack_decisions
                if _get(d, "gate_id") in required_gates
            ]

            # Check sequence matching required_gates length and order
            if len(matching_decisions) != len(required_gates):
                continue

            seq_valid = True
            for idx, expected_gate in enumerate(required_gates):
                d = matching_decisions[idx]
                if _get(d, "gate_id") != expected_gate:
                    seq_valid = False
                    break
                if _get(d, "verdict") != "approve":
                    seq_valid = False
                    break
                if (pack_manifest is not None
                        and _get(d, "manifest_sha256") is not None
                        and _get(d, "manifest_sha256") != pack_manifest):
                    seq_valid = False
                    break

                # Also verify round/created_at non-decreasing if present
                if idx > 0:
                    prev_d = matching_decisions[idx - 1]
                    prev_round = _get(prev_d, "round")
                    curr_round = _get(d, "round")
                    if prev_round is not None and curr_round is not None and curr_round < prev_round:
                        seq_valid = False
                        break
                    prev_created = _get(prev_d, "created_at")
                    curr_created = _get(d, "created_at")
                    if prev_created is not None and curr_created is not None and curr_created < prev_created:
                        seq_valid = False
                        break

            if seq_valid:
                any_pack_satisfies = True
                break

        if not any_pack_satisfies:
            violations.append(DomainViolation(
                path=f"stage[{stage_id}].status",
                code="STAGE_APPROVAL_PRECONDITION_UNMET",
                message=(
                    f"Stage {stage_id!r} is approved but no fresh "
                    f"pack has all required gates "
                    f"({list(required_gates)!r}) approved in correct sequence "
                    f"with consistent manifest"
                ),
            ))

    return violations


# ── Task final-review precondition ───────────────────────────────────────


def _check_task_final(
    entities: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[DomainViolation]:
    """A task with status ``approved_for_merge`` must have ALL stages
    ``approved`` or ``completed``, and a ``TASK-FINAL`` decision with
    verdict ``approve`` on a fresh task-scope pack."""
    violations: list[DomainViolation] = []

    for task in _get(entities, "tasks", ()):
        if _get(task, "status") != "approved_for_merge":
            continue

        task_id = _get(task, "id", "<unknown>")

        # All stages for this task must be approved or completed.
        task_stages = [
            s for s in _get(entities, "stages", ())
            if _get(s, "task_id") == task_id
        ]

        non_terminal_stages = [
            _get(s, "id", "<unknown>")
            for s in task_stages
            if _get(s, "status") not in ("approved", "completed")
        ]

        if non_terminal_stages:
            violations.append(DomainViolation(
                path=f"task[{task_id}].status",
                code="STAGES_NOT_COMPLETE",
                message=(
                    f"Task {task_id!r} is approved_for_merge but "
                    f"stages {non_terminal_stages!r} are not "
                    f"approved/completed"
                ),
            ))

        # Must have a TASK-FINAL approve on a fresh task-scope pack.
        task_packs = [
            p for p in _get(entities, "review_packs", ())
            if _get(p, "task_id") == task_id
            and _get(p, "scope") == "task"
            and _get(p, "status") == "fresh"
        ]

        has_final_approve = False
        for pack in task_packs:
            pack_id = _get(pack, "id")
            for d in _get(entities, "review_decisions", ()):
                if (_get(d, "pack_id") == pack_id
                        and _get(d, "gate_id") == "TASK-FINAL"
                        and _get(d, "verdict") == "approve"):
                    has_final_approve = True
                    break
            if has_final_approve:
                break

        if not has_final_approve:
            violations.append(DomainViolation(
                path=f"task[{task_id}].status",
                code="TASK_FINAL_PRECONDITION_UNMET",
                message=(
                    f"Task {task_id!r} is approved_for_merge but "
                    f"no TASK-FINAL approve exists on a fresh "
                    f"task-scope pack"
                ),
            ))

    return violations


# ── Public entry point ───────────────────────────────────────────────────


def validate_invariants(
    current: Mapping[str, Any],
    entities: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[DomainViolation]:
    """Validate cross-entity invariants.

    Parameters
    ----------
    current:
        A mapping representing ``current.json`` pointer fields
        (``active_task_id``, ``active_stage_id``, etc.).
    entities:
        A mapping of entity collection names to sequences of entity
        mappings.  Expected keys: ``tasks``, ``stages``,
        ``work_orders``, ``handoffs``, ``evidence_list``,
        ``review_packs``, ``review_decisions``.

    Returns
    -------
    list[DomainViolation]
        A list of violations, sorted by ``(path, code)``.  An empty
        list means all checked invariants hold.  The function never
        mutates *current* or *entities*.
    """
    violations: list[DomainViolation] = []

    violations.extend(_check_pointer_existence(current, entities))
    violations.extend(_check_single_active(entities))
    violations.extend(_check_parent_child(current, entities))
    violations.extend(_check_handoff_ownership(current, entities))
    violations.extend(_check_evidence_pack_consistency(entities))
    violations.extend(_check_decision_binding(entities))
    violations.extend(_check_stage_approval(current, entities))
    violations.extend(_check_task_final(entities))

    violations.sort(key=lambda v: v.sort_key())
    return violations
