"""Credentials map rules: chat claim and analysis trigger (hub decisions 20, 29)."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping

from .errors import EmbassyError

MAX_ENTRIES = 8
MAX_BYTES = 8 * 1024
_KEY = re.compile(r"[A-Z][A-Z0-9_]{0,63}")
HINT = (
    "Use at most 8 string credentials (8 KiB total, no NUL) under keys matching "
    "^[A-Z][A-Z0-9_]{0,63}$ not starting with RC_."
)


def claim(credentials: Mapping[str, str] | None, code: str) -> dict[str, str] | None:
    """Validate like the host does; keys sorted (the goldens' order), None when absent or empty.

    Raises EmbassyError with `code` as error_class; the message never echoes a key or value.
    """
    if not credentials:
        return None
    if not isinstance(credentials, Mapping) or len(credentials) > MAX_ENTRIES:
        raise EmbassyError(0, code, HINT)
    sorted_claim: dict[str, str] = {}
    for key in sorted(credentials):
        value = credentials[key]
        # NUL: an env value cannot carry one; the host refuses it rather than fail the container.
        if (
            not isinstance(key, str)
            or not _KEY.fullmatch(key)
            or key.startswith("RC_")
            or not isinstance(value, str)
            or "\0" in value
        ):
            raise EmbassyError(0, code, HINT)
        sorted_claim[key] = value
    encoded = json.dumps(sorted_claim, separators=(",", ":"), ensure_ascii=False).encode()
    if len(encoded) > MAX_BYTES:
        raise EmbassyError(0, code, HINT)
    return sorted_claim
