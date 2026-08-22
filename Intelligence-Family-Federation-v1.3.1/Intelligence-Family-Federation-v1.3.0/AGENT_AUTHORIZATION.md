# Agent Authorization Policy

## Purpose

External agents are execution mechanisms, not Family authorities. Every agent must receive only the minimum permission required for a bounded task.

## Non-negotiable controls

- Human approval is required for consequential actions.
- Authorization is explicit, scoped, time-bounded, auditable, and revocable.
- Credentials never belong in source control.
- An agent's provider identity does not grant repository authority.
- Missing or ambiguous authorization fails closed.
- Agents may not self-escalate privileges or approve their own actions.
- Read-only access is the default.

## Risk tiers

| Tier | Example | Default approval |
|---|---|---|
| 0 | Documentation/read-only analysis | Pre-authorized within scope |
| 1 | Local/test changes | Human review before merge |
| 2 | Repository writes or releases | Explicit human approval |
| 3 | External systems, credentials, production-impacting actions | Explicit human approval + additional security review |

See `docs/registry/agent-authorization.schema.json` for the machine-readable contract.
