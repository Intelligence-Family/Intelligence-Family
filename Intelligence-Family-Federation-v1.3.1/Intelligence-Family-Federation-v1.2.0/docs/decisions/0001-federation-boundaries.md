# ADR-0001: Federation Boundaries

## Status
Accepted

## Decision
Keep Family identity, provider interfaces, capabilities, skills, agents, SENTINEL controls, and human authorization as separate layers.

## Rationale
Separation reduces hidden provider dependencies, limits blast radius, preserves provenance, and makes authorization auditable.

## Consequences
Integrations require explicit adapters/contracts and additional review. This is intentional: convenience must not override human control or security.
