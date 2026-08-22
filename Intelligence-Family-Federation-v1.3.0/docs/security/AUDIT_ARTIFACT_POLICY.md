# Audit Artifact Policy

Raw provider, OAuth, GitHub, or agent audit exports are treated as sensitive operational evidence.

Do not commit raw exports to the public repository. If an audit artifact is needed for reproducibility, create a sanitized derivative that removes tokens, token hashes, actor identifiers, request identifiers, private repository metadata, and other unnecessary identifiers.

Preserve chain-of-custody and the original artifact in an appropriately protected location.
