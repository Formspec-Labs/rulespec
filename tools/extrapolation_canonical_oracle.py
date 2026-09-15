"""Test-only canonical helpers copied from Rulespec 8ec1417.

Source: tools/extrapolation_release_v2.py. The function block below is exact;
production code must use rulespec_artifacts instead.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import rfc8785

MAX_SAFE_INTEGER = (1 << 53) - 1


def canonical_json_bytes(value: Any) -> bytes:
    """Encode one identity-bearing value under ``spicy-canonical-json-v1``."""

    _validate_canonical_domain(value)
    return rfc8785.dumps(value)


def canonical_sha256(value: Any) -> str:
    """Return an unqualified digest over canonical JSON bytes."""

    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _validate_canonical_domain(value: Any, path: str = "$") -> None:
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, int):
        if isinstance(value, bool) or abs(value) > MAX_SAFE_INTEGER:
            raise ValueError(f"{path} integer is outside the JSON safe range")
        return
    if isinstance(value, float):
        raise ValueError(f"{path} floating-point values are forbidden")
    if isinstance(value, list):
        for index, member in enumerate(value):
            _validate_canonical_domain(member, f"{path}/{index}")
        return
    if isinstance(value, dict):
        for key, member in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{path} object key is not a string")
            _validate_canonical_domain(member, f"{path}/{key}")
        return
    raise ValueError(f"{path} contains unsupported JSON value {type(value).__name__}")


def _reject_constant(value: str) -> None:
    raise ValueError(f"JSON constant {value!r} is forbidden")


def _reject_float(value: str) -> None:
    raise ValueError(f"JSON floating-point value {value!r} is forbidden")


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def load_strict_canonical_json(path: Path) -> Any:
    """Load a canonical manifest and reject noncanonical source bytes."""

    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError("a UTF-8 byte order mark is forbidden")
    value = json.loads(
        raw.decode("utf-8"),
        parse_constant=_reject_constant,
        parse_float=_reject_float,
        object_pairs_hook=_reject_duplicate_keys,
    )
    _validate_canonical_domain(value)
    if canonical_json_bytes(value) != raw:
        raise ValueError("JSON bytes are not canonical")
    return value


