"""JSON Schema definitions for Continuity entities.

Public API
----------
schema_names()       – sorted list of the 12 entity schema names.
load_schema(name)    – load and return a single schema dict by name.
check_all_schemas()  – validate all schemas against the Draft 2020-12 meta-schema.
validate(name, obj)  – validate *obj* against the named schema; returns a list of
                       structured error dicts (empty on success).

All operations are offline; no network access is performed by this module.
"""

from continuity.schemas.registry import (
    check_all_schemas,
    load_schema,
    schema_names,
    validate,
)

__all__ = [
    "check_all_schemas",
    "load_schema",
    "schema_names",
    "validate",
]
