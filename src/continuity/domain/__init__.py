"""Domain models and state transitions.

Public API
----------
.. autoclass:: DomainViolation
.. autofunction:: can_transition
.. autofunction:: validate_transition
.. autofunction:: validate_invariants
"""

from continuity.domain.errors import DomainViolation
from continuity.domain.invariants import validate_invariants
from continuity.domain.transitions import (
    can_transition,
    validate_transition,
)

__all__ = [
    "DomainViolation",
    "can_transition",
    "validate_invariants",
    "validate_transition",
]
