# Credential Lifecycle Policy

Credentials are security boundaries, not configuration conveniences.

## Lifecycle

**Request → Approve → Issue minimum scope → Use for bounded task → Audit → Rotate/Expire → Revoke**

### Requirements

- Store secrets only in approved secret stores or GitHub encrypted secrets.
- Never commit plaintext tokens, private keys, certificates, `.env` files, or credential exports.
- Prefer short-lived credentials and workload identity where supported.
- Record owner, purpose, scope, creation time, expiration/rotation target, and revocation procedure.
- Revoke credentials immediately when exposure is suspected.
- Credential rotation does not prove that authorization is appropriate.
- Raw audit exports containing operational identifiers remain outside the public repository unless sanitized.

## Incident response

If a credential may be exposed: stop use, revoke/rotate it, preserve relevant audit evidence safely, assess scope, and document the incident before restoring access.
