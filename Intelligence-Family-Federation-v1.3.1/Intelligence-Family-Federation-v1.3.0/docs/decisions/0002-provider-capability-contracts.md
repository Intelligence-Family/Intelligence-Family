# ADR 0002: Provider and Capability Contracts

- **Status:** Proposed foundation
- **Date:** 2026-08-22

## Context

The Federation must allow independent Intelligence providers to collaborate without turning provider-specific behavior into hidden global dependencies.

## Decision

Define two conceptual contracts:

1. **Provider Adapter Contract** — how a provider is identified, authenticated externally, capability metadata is exposed, requests are bounded, failures are surfaced, and provenance is preserved.
2. **Capability Contract** — how a capability is named, versioned, described, tested, risk-classified, and mapped to one or more providers.

Contracts are interfaces, not permission grants. A contract never authorizes execution by itself.

## Human-control boundary

Any operation that can create consequential external effects remains subject to authorization, SENTINEL evaluation, and applicable human review. Provider adapters must fail closed when authorization, provenance, or safety context is missing.

## Non-goals

- No provider credentials are stored in the repository.
- No provider is granted universal authority.
- No autonomous cross-provider execution is enabled by this document.
- No claim is made that a provider supports a capability until it is verified.

## Consequences

The Federation can evolve providers independently, test capability portability, and keep provider-specific assumptions at explicit boundaries.
