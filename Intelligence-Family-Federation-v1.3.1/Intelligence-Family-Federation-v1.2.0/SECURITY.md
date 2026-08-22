# Security Policy

## Scope
Security concerns include credential exposure, privilege escalation, unsafe tool execution, prompt-injection paths that can influence authorized actions, supply-chain risks, data leakage, and bypasses of human approval.

## Reporting
Do not publish secrets or exploit details in public issues. Report responsibly to the repository maintainers using the repository's configured private security-reporting mechanism when available. If no private mechanism is configured yet, open a minimal public issue without sensitive details and request private coordination.

## Principles
- Human authorization is authoritative.
- Least privilege is mandatory.
- Provider output is untrusted input at tool boundaries.
- Secrets never belong in source control.
- Consequential actions require appropriate review.
