# Intelligence Family Federation v1.3.0

## Federation Integrity & Authorization Gate

This release makes security governance an operational repository layer.

### Added

- Agent authorization policy
- Agent registry
- Credential lifecycle policy
- Agent authorization JSON schema
- Defense-in-depth security controls
- Audit artifact handling policy
- ADR 0003 documenting agent authorization boundaries

### CI

The repository now validates governance files and JSON contracts, detects common credential-bearing artifacts, rejects nested release ZIPs, and uses `contents: read` permissions.

### Security posture

Read-only access is the default. Consequential actions require human approval. Missing or ambiguous authorization fails closed. Credentials are never intended to be stored in source control.

### Important

This release provides governance and validation scaffolding. It does not create credentials, grant external agents access, or claim that an agent integration is trusted merely because it is listed in the registry.
