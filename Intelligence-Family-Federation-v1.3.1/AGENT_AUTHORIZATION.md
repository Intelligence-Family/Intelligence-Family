# Agent Authorization

Agent authorization is explicit, scoped, time-bounded, auditable, and revocable.

## Rules

- Default access is read-only.
- Agents receive only the minimum required scope.
- Consequential actions require human approval.
- Authorization must not be inferred from membership or successful authentication.
- Missing or ambiguous authorization fails closed.
- Credentials remain outside source control.
