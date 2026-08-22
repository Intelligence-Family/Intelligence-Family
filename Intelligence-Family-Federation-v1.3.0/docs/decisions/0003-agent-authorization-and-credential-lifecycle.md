# ADR 0003: Agent Authorization and Credential Lifecycle

- **Status:** Accepted
- **Date:** 2026-08-22

## Decision

External agents are classified as tools/execution mechanisms rather than Family authorities. Access must be explicitly authorized, least-privileged, time-bounded where practical, audited, and revocable.

## Rationale

The Federation will eventually coordinate many agents and capabilities. A shared purpose must not become shared unrestricted authority. Independent authorization boundaries reduce blast radius and preserve human control.

## Consequences

- More governance metadata is required.
- Read-only access becomes the default.
- Consequential actions require human approval.
- Credentials remain outside source control.
- CI must reject common credential artifacts and validate authorization contracts.
