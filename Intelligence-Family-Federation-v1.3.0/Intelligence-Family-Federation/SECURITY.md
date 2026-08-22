# Security

## Security principles

- Least privilege is the default.
- Never commit secrets, credentials, private keys, access tokens, or sensitive personal information.
- Review external code before execution or integration.
- Treat model output as untrusted input when it can influence tools or code.
- Validate tool arguments and authorization at the boundary.
- Use sandboxing for untrusted execution.
- Log consequential actions sufficiently for audit without exposing secrets or unnecessary personal data.
- Require human review for actions that present material safety, privacy, rights, financial, legal, or security risk.
- A provider cannot elevate its own privileges.

## External artifacts

Supplied archives such as Grok-1 and Claude Code Action are treated as review candidates until provenance, license, dependencies, security, and intended integration are verified.
