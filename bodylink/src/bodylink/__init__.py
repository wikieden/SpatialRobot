"""bodylink — the execution-adapter layer for Chronotope (D5, the 4th member).

The brain (`mindloop`) ships the `ExecutorAdapter` *protocol*; bodylink ships the
reference *fill*: `MockBody` (a no-hardware body for L3 dev/tests) and the G1-D
reference manifest. Each real robot is a separate, out-of-tree device package
implementing the same protocol — differentiated only by its Body Profile + verb
set ("swap the body, keep the mind", D3). Genesis/Isaac sim lives behind the
`[sim]` extra; no heavy deps in the core.
"""

from __future__ import annotations

from .mock import MockBody, UnsupportedVerbError, g1d_manifest

__version__ = "0.1.0a0"

__all__ = [
    "MockBody",
    "UnsupportedVerbError",
    "g1d_manifest",
]
