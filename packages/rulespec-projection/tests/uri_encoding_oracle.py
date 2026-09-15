"""Test-only URI encoder copied exactly from projection.py at 8ec1417."""

def encode_for_uri(value: str) -> str:
    """Percent-encode outside the RFC 3986 unreserved set, uppercase hex.

    This is SPARQL's ``ENCODE_FOR_URI``, which is the encoding Core §4.2 names
    for the artifact component and the encoding
    ``CarrierLocalFragmentUrnSourceAgreementShape`` compares against.
    """
    out: list[str] = []
    for character in value:
        if (character.isascii() and character.isalnum()) or character in "-._~":
            out.append(character)
        else:
            out.extend(f"%{byte:02X}" for byte in character.encode("utf-8"))
    return "".join(out)


