"""Immutable domain violation structure."""

from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True, slots=True)
class DomainViolation:
    """A single domain-rule violation.

    Attributes:
        path:    Logical project-relative path identifying the violating
                 location (e.g. ``"task.status"`` or ``"current.active_task_id"``).
        code:    Stable machine-readable error code (e.g.
                 ``"UNKNOWN_ENTITY"``).
        message: Short human-readable explanation.  Never ``None``.
    """

    path: str
    code: str
    message: str

    # --- sorting helpers -------------------------------------------------- #
    def sort_key(self) -> tuple[str, str]:
        """Return the canonical ``(path, code)`` sort key."""
        return (self.path, self.code)
