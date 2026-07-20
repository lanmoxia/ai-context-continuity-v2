"""Schema registry: offline fixed-whitelist loader, self-check, and instance validation.

All schemas are loaded exclusively via importlib.resources from the installed package.
No network access, no arbitrary file-system paths, no dynamic $ref resolution.

F01 compliance: $ref resolution uses the ``referencing`` library with a sealed
Registry containing only whitelisted URN-based schemas.  Any $ref pointing outside
this fixed set is rejected *before* any network or filesystem I/O.  Validation
errors (including $ref resolution failures) are always returned as structured
error dicts — never as tracebacks.

F02 compliance: RFC 3339 timestamps are validated in two layers — JSON Schema
``format: "date-time"`` with ``jsonschema[format]`` enabled, AND a strict
regex that rejects impossible calendar dates, hours, minutes and seconds.
"""

from __future__ import annotations

import importlib.resources
import json
import re
from typing import Any

import jsonschema
import jsonschema.validators

try:
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012
    _HAS_REFERENCING = True
except ImportError:  # pragma: no cover — referencing is a hard dep of jsonschema ≥ 4.18
    _HAS_REFERENCING = False

# ---------------------------------------------------------------------------
# Fixed whitelist of schema names available in this package.
# Adding a new schema requires updating this tuple and shipping the .schema.json
# file as package data.  Unknown names are rejected before any I/O.
# ---------------------------------------------------------------------------
_SCHEMA_NAMES: tuple[str, ...] = (
    "project",
    "config",
    "current",
    "task",
    "stage",
    "work-order",
    "checkpoint",
    "handoff",
    "evidence",
    "context-pack",
    "review-pack",
    "review-decision",
)

# The common definitions schema is internal; it is loaded into the registry
# store but not exposed through schema_names().
_INTERNAL_SCHEMA_NAMES: tuple[str, ...] = ("common",)

# All whitelisted URN prefixes.  Any $ref whose URI does not start with one
# of these is rejected before any resolution is attempted.
_URN_PREFIX = "urn:continuity:schema:"

# Build the complete set of allowed URN bases for pre-scan.
_ALL_NAMES = _INTERNAL_SCHEMA_NAMES + _SCHEMA_NAMES
_ALLOWED_URNS = frozenset(f"{_URN_PREFIX}{name}:1" for name in _ALL_NAMES)

# Strict RFC 3339 regex with calendar/time range guards:
#   YYYY: 0001-9999
#   MM:   01-12
#   DD:   01-31 (schema-level; semantic check below)
#   HH:   00-23
#   mm:   00-59
#   ss:   00-60 (60 = leap second per RFC 3339)
#   tz:   Z | ±HH:MM with HH 00-23, MM 00-59
_RFC3339_STRICT_RE = re.compile(
    r"^(?P<year>\d{4})-(?P<month>0[1-9]|1[0-2])-(?P<day>0[1-9]|[12]\d|3[01])"
    r"T(?P<hour>[01]\d|2[0-3]):(?P<minute>[0-5]\d):(?P<second>[0-5]\d|60)"
    r"(\.\d+)?"
    r"(Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)$"
)

# Days per month (non-leap).  February handled separately.
_DAYS_IN_MONTH = {
    1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
    7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31,
}


def _is_valid_rfc3339(value: str) -> bool:
    """Return True only if *value* is a syntactically and semantically valid
    RFC 3339 timestamp with a mandatory timezone offset or Z.
    """
    m = _RFC3339_STRICT_RE.match(value)
    if m is None:
        return False
    year, month, day = int(m.group("year")), int(m.group("month")), int(m.group("day"))
    max_day = _DAYS_IN_MONTH[month]
    if month == 2:
        is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
        if is_leap:
            max_day = 29
    return day <= max_day


def schema_names() -> list[str]:
    """Return the stable, sorted list of public schema names."""
    return sorted(_SCHEMA_NAMES)


def _schema_filename(name: str) -> str:
    return f"{name}.schema.json"


def _schema_urn(name: str) -> str:
    return f"{_URN_PREFIX}{name}:1"


def _load_raw(name: str) -> dict[str, Any]:
    """Load a single schema by name from package resources (offline, no network)."""
    package = importlib.resources.files("continuity.schemas")
    resource = package.joinpath(_schema_filename(name))
    content = resource.read_bytes()
    return json.loads(content)  # type: ignore[no-any-return]


# ---------------------------------------------------------------------------
# $ref pre-scan (F01): reject any $ref that escapes the fixed whitelist
# ---------------------------------------------------------------------------

def _scan_refs(obj: Any, path: str = "") -> list[str]:
    """Recursively collect all $ref values from a JSON-like object."""
    refs: list[str] = []
    if isinstance(obj, dict):
        if "$ref" in obj:
            refs.append(obj["$ref"])
        for key, val in obj.items():
            _sub = f"{path}.{key}" if path else key
            refs.extend(_scan_refs(val, _sub))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            refs.extend(_scan_refs(item, f"{path}[{i}]"))
    return refs


def _validate_refs(schema: dict[str, Any], schema_name: str) -> None:
    """Raise ValueError if any $ref in *schema* escapes the fixed whitelist.

    Allowed patterns:
      - ``#/$defs/...`` (internal fragment within the same schema)
      - ``urn:continuity:schema:<name>:1`` (exact match to a whitelisted schema)
      - ``urn:continuity:schema:<name>:1#/$defs/...`` (whitelisted schema + fragment)

    Anything else (http, https, file, relative path, unknown URN) is rejected
    *before* any I/O or network access.
    """
    refs = _scan_refs(schema)
    for ref in refs:
        if ref.startswith("#/"):
            continue  # internal fragment
        base = ref.split("#")[0]
        if base in _ALLOWED_URNS:
            continue  # known schema (with or without fragment)
        raise ValueError(
            f"Schema {schema_name!r} contains disallowed $ref {ref!r}. "
            f"Only internal fragments (#/...) and whitelisted URN schemas are permitted."
        )


# ---------------------------------------------------------------------------
# Registry builder (F01): use the ``referencing`` library for safe resolution
# ---------------------------------------------------------------------------

def _build_registry() -> tuple[dict[str, Any], Any]:
    """Build the URN → schema mapping and a referencing.Registry.

    Returns (store_dict, registry) where store_dict maps URN → raw schema dict,
    and registry is a referencing.Registry suitable for jsonschema validators.
    """
    store: dict[str, Any] = {}
    resources: list[tuple[str, Any]] = []

    for name in _ALL_NAMES:
        schema = _load_raw(name)
        _validate_refs(schema, name)
        urn = _schema_urn(name)
        store[urn] = schema
        if _HAS_REFERENCING:
            resource = Resource.from_contents(schema, default_specification=DRAFT202012)
            resources.append((urn, resource))

    if _HAS_REFERENCING:
        registry = Registry().with_resources(resources)
    else:
        registry = None  # pragma: no cover

    return store, registry


def _make_validator(
    schema: dict[str, Any],
    registry: Any,
) -> jsonschema.Validator:
    """Create a Draft 2020-12 validator with format checking and sealed registry."""
    cls = jsonschema.validators.validator_for(schema)

    if _HAS_REFERENCING and registry is not None:
        return cls(
            schema,
            registry=registry,
            format_checker=jsonschema.FormatChecker(),
        )
    else:  # pragma: no cover
        return cls(schema, format_checker=jsonschema.FormatChecker())


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_schema(name: str) -> dict[str, Any]:
    """Load and return the raw schema dict for *name*.

    Raises ValueError for unknown names (before any I/O).
    Raises json.JSONDecodeError or FileNotFoundError if the package is corrupt.
    """
    if name not in _SCHEMA_NAMES:
        raise ValueError(
            f"Unknown schema name {name!r}. "
            f"Allowed names: {sorted(_SCHEMA_NAMES)}"
        )
    return _load_raw(name)


def check_all_schemas() -> None:
    """Validate every schema (including common) against the Draft 2020-12 meta-schema.

    Also validates that every $ref in every schema resolves to a whitelisted URN.
    Raises jsonschema.SchemaError on the first invalid schema.
    Does not access the network; uses the bundled meta-schema from jsonschema.
    """
    store, _reg = _build_registry()  # _validate_refs runs during build
    meta_cls = jsonschema.validators.validator_for(
        {"$schema": "https://json-schema.org/draft/2020-12/schema"}
    )
    meta_validator = meta_cls(meta_cls.META_SCHEMA)
    for name in _ALL_NAMES:
        schema = store[_schema_urn(name)]
        meta_validator.validate(schema)


def _collect_errors(
    instance: Any,
    schema: dict[str, Any],
    registry: Any,
) -> list[dict[str, Any]]:
    """Return a stably sorted list of structured validation errors.

    Each entry contains:
      - ``code``:    stable string key derived from the failing keyword
      - ``path``:    dot-separated JSON path to the failing location in *instance*
      - ``keyword``: the failing JSON Schema keyword

    F01 compliance: any $ref resolution error is caught and converted into a
    structured error dict with code='ref_resolution'.  No traceback is leaked.

    F02 compliance: after the jsonschema pass, every string field matching
    rfc3339_with_timezone is also checked with a strict calendar validator.
    """
    try:
        validator = _make_validator(schema, registry)
        raw_errors = list(validator.iter_errors(instance))

        def _sort_key(e: jsonschema.ValidationError) -> tuple[str, str]:
            path = ".".join(str(p) for p in e.absolute_path)
            return (path, e.validator or "")

        raw_errors.sort(key=_sort_key)
        errors = [
            {
                "code": e.validator or "unknown",
                "path": ".".join(str(p) for p in e.absolute_path) or "<root>",
                "keyword": e.validator or "unknown",
            }
            for e in raw_errors
        ]

        # F02: strict RFC 3339 post-validation for timestamp fields.
        _check_rfc3339_strict(instance, errors)

        # Sort the final merged list of structured errors stably by path and code.
        errors.sort(key=lambda x: (x["path"], x["code"]))

        return errors
    except Exception as exc:
        return [{
            "code": "ref_resolution",
            "path": "<root>",
            "keyword": "ref_resolution",
        }]


def _check_rfc3339_strict(
    obj: Any,
    errors: list[dict[str, Any]],
    path_prefix: str = "",
) -> None:
    """Recursively check all timestamp fields in *obj* (keys ending in _at or _time)
    for strict calendar validity. Appends to *errors* in-place.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            full_path = f"{path_prefix}{key}" if path_prefix else key
            if isinstance(value, str) and (key.endswith("_at") or key.endswith("_time")):
                if not _is_valid_rfc3339(value):
                    errors.append({
                        "code": "rfc3339_strict",
                        "path": full_path,
                        "keyword": "rfc3339_strict",
                    })
            elif isinstance(value, dict):
                _check_rfc3339_strict(value, errors, f"{full_path}.")
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    _check_rfc3339_strict(item, errors, f"{full_path}.{i}.")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _check_rfc3339_strict(item, errors, f"{path_prefix}{i}.")


def validate(name: str, instance: Any) -> list[dict[str, Any]]:
    """Validate *instance* against the named schema.

    Returns an empty list when validation passes.
    Returns a stably sorted list of structured error dicts on failure.

    Raises ValueError for unknown schema names (before any I/O or validation).
    Does not raise on validation errors—callers must check the returned list.
    Does not access the network, print tracebacks, or silently coerce values.
    """
    if name not in _SCHEMA_NAMES:
        raise ValueError(
            f"Unknown schema name {name!r}. "
            f"Allowed names: {sorted(_SCHEMA_NAMES)}"
        )
    try:
        store, registry = _build_registry()
        schema = store[_schema_urn(name)]
        return _collect_errors(instance, schema, registry)
    except Exception as exc:
        return [{
            "code": "ref_resolution",
            "path": "<root>",
            "keyword": "ref_resolution",
        }]
