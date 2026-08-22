# ADR 0004: Activate the Federation Integrity Gate

- Status: Accepted
- Date: 2026-08-22

## Context

The repository contained a starter GitHub Actions workflow that did not validate Federation governance or security controls.

## Decision

Replace the starter workflow with `federation-integrity.yml`.

The gate validates governance documents, JSON contracts, credential-bearing files,
nested release archives, and explicit workflow permissions.

## Boundary

The workflow validates repository state. It does not grant repository authority,
store credentials, or authorize consequential actions.

## Human control

A passing CI result is evidence for review, not permission to perform consequential actions.
