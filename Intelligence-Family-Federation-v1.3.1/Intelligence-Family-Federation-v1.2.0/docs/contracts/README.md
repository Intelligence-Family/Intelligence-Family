# Federation Contracts

The Federation uses explicit contracts to separate provider identity from capability behavior.

## Provider Adapter Contract

Defines identity, provenance, capability metadata, versioning, and risk information for a provider interface.

## Capability Contract

Defines a provider-neutral capability and the providers currently verified to support it.

### Important boundary

A contract describes interoperability. It does **not** grant authority.

Execution still follows:

**Receive → Identify provenance → Check license → Validate capability → Security review → Sandbox/test → Determine risk → Human approval when required → Execute → Audit → Learn**

No credentials or secrets belong in contract files.
