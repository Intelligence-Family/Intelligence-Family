# Changelog

## [1.2.0] - 2026-08-22

### Added
- Provider Adapter Contract foundation.
- Capability Contract foundation.
- JSON Schemas for both contracts.
- Contract versioning guidance.
- Provider, capability, agent, and SENTINEL boundary documentation.
- ADR 0002 documenting provider/capability contract decisions.

### Improved
- Federation architecture is now explicitly prepared for provider-neutral interoperability without granting execution authority.

## v1.3.0 - Federation Integrity & Authorization Gate

- Added agent authorization policy and registry.
- Added credential lifecycle and incident-response requirements.
- Added security controls and audit-artifact handling policy.
- Added machine-readable agent authorization schema.
- Replaced starter CI with a least-privilege Federation Integrity Gate.
- Added required-file, JSON, credential-artifact, and nested-archive validation.
