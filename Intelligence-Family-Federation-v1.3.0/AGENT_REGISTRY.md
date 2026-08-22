# Agent Registry

The registry records integrations without granting them authority.

Each entry should identify:

- provider
- agent/integration name
- purpose
- risk tier
- requested capabilities
- repository/system scope
- credential owner
- approval authority
- creation/rotation/expiration metadata
- audit source
- revocation procedure
- status

Use `docs/registry/agent-authorization.schema.json` for structured records.

## Initial registry

| Agent / integration | Classification | Default access | Status |
|---|---|---|---|
| Copilot Chat App | Agent/tool | Read-only unless explicitly approved | Review |
| Copilot SWE Agent | Agent/tool | Read-only unless explicitly approved | Review |
| Claude Code | Agent/tool | Bounded repository scope | Review |
| Codex | Agent/tool | Bounded repository scope | Review |

Registry entries are governance records; they do not create credentials or permissions.
