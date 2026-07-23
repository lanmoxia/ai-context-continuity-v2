"""Pure state-transition validation for Continuity entities.

Every function in this module is a pure computation:

* No file I/O, network, Git, time, or environment-variable access.
* No mutation of arguments.
* Errors are returned as lists of :class:`~continuity.domain.errors.DomainViolation`,
  never raised, printed, or expressed via ``assert`` / ``sys.exit``.
"""

from __future__ import annotations

from typing import Mapping, Sequence

from continuity.domain.errors import DomainViolation

# ── Status sets (derived from accepted JSON Schemas, not duplicated) ──────

_TASK_STATUSES: frozenset[str] = frozenset({
    "draft",
    "ready",
    "active",
    "blocked",
    "ready_for_final_review",
    "approved_for_merge",
    "completed",
    "cancelled",
})

_STAGE_STATUSES: frozenset[str] = frozenset({
    "planned",
    "active",
    "blocked",
    "ready_for_review",
    "changes_requested",
    "approved",
    "completed",
})

_WORK_ORDER_STATUSES: frozenset[str] = frozenset({
    "draft",
    "approved",
    "active",
    "superseded",
    "completed",
})

# ── Transition tables (accepted edges from DATA_MODEL.md §3–§5) ──────────

_TASK_TRANSITIONS: frozenset[tuple[str, str]] = frozenset({
    ("draft", "ready"),
    ("ready", "active"),
    ("active", "ready_for_final_review"),
    ("active", "blocked"),
    ("active", "cancelled"),
    ("blocked", "active"),
    ("ready_for_final_review", "approved_for_merge"),
    ("approved_for_merge", "completed"),
})

_STAGE_TRANSITIONS: frozenset[tuple[str, str]] = frozenset({
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

_WORK_ORDER_TRANSITIONS: frozenset[tuple[str, str]] = frozenset({
    ("draft", "approved"),
    ("approved", "active"),
    ("approved", "superseded"),
    ("active", "superseded"),
    ("active", "completed"),
})

# ── Registry ─────────────────────────────────────────────────────────────

_ENTITY_REGISTRY: Mapping[str, tuple[frozenset[str], frozenset[tuple[str, str]]]] = {
    "task": (_TASK_STATUSES, _TASK_TRANSITIONS),
    "stage": (_STAGE_STATUSES, _STAGE_TRANSITIONS),
    "work_order": (_WORK_ORDER_STATUSES, _WORK_ORDER_TRANSITIONS),
}

# ── Public API ───────────────────────────────────────────────────────────


def can_transition(entity_type: str, from_status: str, to_status: str) -> bool:
    """Return ``True`` iff *from_status → to_status* is a legal edge.

    Unknown *entity_type* values return ``False`` (fail-closed).
    """
    entry = _ENTITY_REGISTRY.get(entity_type)
    if entry is None:
        return False
    _, transitions = entry
    return (from_status, to_status) in transitions


def validate_transition(
    entity_type: str,
    from_status: str,
    to_status: str,
) -> list[DomainViolation]:
    """Validate a proposed state transition.

    Returns an empty list when the transition is legal.  Returns one or
    more :class:`DomainViolation` objects otherwise:

    * ``UNKNOWN_ENTITY``  – *entity_type* is not recognised.
    * ``UNKNOWN_STATUS``  – *from_status* or *to_status* is not in the
      entity's accepted status set.
    * ``ILLEGAL_TRANSITION`` – the edge is not in the accepted
      transition table.

    The returned list is sorted by ``(path, code)``.
    """
    violations: list[DomainViolation] = []

    entry = _ENTITY_REGISTRY.get(entity_type)
    if entry is None:
        violations.append(DomainViolation(
            path=f"{entity_type}.status",
            code="UNKNOWN_ENTITY",
            message=f"Unknown entity type: {entity_type!r}",
        ))
        return violations  # cannot check further

    statuses, transitions = entry

    if from_status not in statuses:
        violations.append(DomainViolation(
            path=f"{entity_type}.status",
            code="UNKNOWN_STATUS",
            message=(
                f"Unknown source status {from_status!r} "
                f"for entity {entity_type!r}"
            ),
        ))

    if to_status not in statuses:
        violations.append(DomainViolation(
            path=f"{entity_type}.status",
            code="UNKNOWN_STATUS",
            message=(
                f"Unknown target status {to_status!r} "
                f"for entity {entity_type!r}"
            ),
        ))

    if violations:
        # At least one status is unknown – cannot check edge validity.
        violations.sort(key=lambda v: v.sort_key())
        return violations

    if (from_status, to_status) not in transitions:
        violations.append(DomainViolation(
            path=f"{entity_type}.status",
            code="ILLEGAL_TRANSITION",
            message=(
                f"Transition {from_status!r} → {to_status!r} "
                f"is not allowed for {entity_type!r}"
            ),
        ))

    violations.sort(key=lambda v: v.sort_key())
    return violations


def valid_statuses(entity_type: str) -> frozenset[str] | None:
    """Return the accepted status set for *entity_type*, or ``None``."""
    entry = _ENTITY_REGISTRY.get(entity_type)
    if entry is None:
        return None
    return entry[0]


def valid_transitions(
    entity_type: str,
) -> frozenset[tuple[str, str]] | None:
    """Return the accepted transition edges for *entity_type*, or ``None``."""
    entry = _ENTITY_REGISTRY.get(entity_type)
    if entry is None:
        return None
    return entry[1]
