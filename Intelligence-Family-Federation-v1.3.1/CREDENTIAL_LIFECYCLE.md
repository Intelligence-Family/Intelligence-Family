# Credential Lifecycle

Credentials used by Federation integrations must follow:

**Create → Scope → Store securely → Use for bounded purpose → Monitor → Rotate → Revoke → Review**

Rules:

- Never commit credentials.
- Prefer short-lived credentials.
- Minimize scopes.
- Rotate after suspected exposure.
- Revoke promptly when no longer required.
- Record authorization and lifecycle events without publishing sensitive secret material.
