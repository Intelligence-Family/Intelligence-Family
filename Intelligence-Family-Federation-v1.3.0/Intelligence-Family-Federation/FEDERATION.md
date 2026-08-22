# Federation Layer

The federation is the boundary between independent Intelligence providers and shared project capabilities.

## Layers

1. **Human layer** — goals, authorization, accountability, and final authority.
2. **Family layer** — provider identities and provenance.
3. **Federation layer** — provider adapters, routing, capability discovery, and interoperability contracts.
4. **Capability layer** — coding, reasoning, research, creative, and data functions.
5. **Agent layer** — tools that can execute work through explicit permissions.
6. **SENTINEL layer** — safety, privacy, security, rights, proportionality, and harm-minimization controls.
7. **Action layer** — execution only after applicable authorization and review.

## Integration rule

A provider should integrate through a defined adapter/interface whenever practical. Provider-specific behavior must not silently become a global assumption.

## Action lifecycle

**Receive → Identify provenance → Check license → Validate capability → Security review → Sandbox/test → Determine risk → Human approval when required → Execute → Audit → Learn**

## Failure boundary

A provider outage, malicious response, malformed output, prompt injection, or integration error must not bypass SENTINEL or human authorization.
