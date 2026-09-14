"""Canonical exact-identifier keys shared by identity-grade consumers."""

from __future__ import annotations

import unicodedata
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

from spicysearch.canonical import IntegrityError, sha256_digest

IDENTIFIER_NORMALIZATION_POLICY_ID = "spicysearch-exact-identifier-v1"
IDENTIFIER_NORMALIZATION_POLICY_VERSION = "1"
FEDERAL_REGISTER_DOCUMENT_NUMBER_ROLE = "federal-register-document-number"
_DASHES = str.maketrans(dict.fromkeys("\u2010\u2011\u2012\u2013\u2014\u2015\u2212", "-"))
IDENTIFIER_NORMALIZATION_POLICY: Mapping[str, Any] = MappingProxyType(
    {
        "policyId": IDENTIFIER_NORMALIZATION_POLICY_ID,
        "policyVersion": IDENTIFIER_NORMALIZATION_POLICY_VERSION,
        "steps": (
            "trim-unicode-whitespace",
            "unicode-nfkc",
            "unicode-casefold",
            "recognized-dashes-to-ascii-hyphen",
            "collapse-unicode-whitespace-to-ascii-space",
        ),
        "unicodeDataVersion": unicodedata.unidata_version,
    }
)
IDENTIFIER_NORMALIZATION_POLICY_DIGEST = sha256_digest(dict(IDENTIFIER_NORMALIZATION_POLICY))


def normalize_identifier(value: str) -> str | None:
    """Return one complete identifier key without parsing or dropping punctuation."""

    if not isinstance(value, str):
        raise IntegrityError("identifier normalization requires a string")
    folded = unicodedata.normalize("NFKC", value.strip()).casefold().translate(_DASHES)
    normalized = " ".join(folded.split())
    return normalized or None


__all__ = [
    "FEDERAL_REGISTER_DOCUMENT_NUMBER_ROLE",
    "IDENTIFIER_NORMALIZATION_POLICY",
    "IDENTIFIER_NORMALIZATION_POLICY_DIGEST",
    "IDENTIFIER_NORMALIZATION_POLICY_ID",
    "IDENTIFIER_NORMALIZATION_POLICY_VERSION",
    "normalize_identifier",
]
