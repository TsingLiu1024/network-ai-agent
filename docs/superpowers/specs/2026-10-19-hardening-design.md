# Network diagnosis hardening

User request: fix all findings from the preceding review and related latent defects.
This is a repair of the existing API and local diagnostic service, not authorization
to execute repairs on the host or publish changes upstream.

## Design

Keep the existing agent/result boundaries. Use one validated Settings instance for
providers, paths, deadlines, resource limits and authentication. Maintain the
documented MODEL_PROVIDER name and accept LLM_PROVIDER as a compatibility alias.
Providers return nonempty strings or raise sanitized typed failures. Real read-only
collectors feed network/log agents; no collector error may be reported as evidence.

The manager is a synchronous bounded pipeline run by FastAPI in a worker thread.
It collects independent evidence concurrently with fixed timeouts, retrieves
source-bearing knowledge, and makes at most two bounded model calls (repair then
summary). An overall monotonic budget prevents starting work after expiry. HTTP
client and subprocess deadlines bound in-flight work. Limit simultaneous API work
and input/output sizes. Distinguish success, partial, failure; preserve per-stage
errors without exposing credentials or internal exception details.

Repair output must validate against a typed schema. Commands remain suggestions;
generic shell execution is disabled. Explicit local repair tools accept only named
allowlisted actions with explicit confirmation. Old reset scripts require explicit
confirmation. Local evidence is opt-in for cloud providers and identifies the host
as the API server/container, never the remote caller. Deployment binds localhost
by default; optional API key supports deliberate exposure.

RAG uses normalized multilingual embeddings, validated JSON vector/document
snapshots and in-memory FAISS indices (no native index/pickle deserialization),
provenance and relevance filtering.
Lazy imports avoid model downloads during API import/testing. Complete-file and
content fingerprint checks trigger rebuilds. File locking plus atomic generation
publication prevent readers seeing partial writes. Models are configurable and
can be preloaded; RAG may be explicitly disabled. Failed optional RAG degrades
diagnosis visibly rather than aborting all startup.

## Acceptance

Offline pytest tests cover provider errors/configuration, route contracts,
structured repair rejection, failed/partial pipelines, evidence provenance,
subprocess errors/timeouts, concurrent API responsiveness, resource limits,
empty/corrupt/stale indices and concurrent builds. Use deterministic test
embeddings, never external models or actual repair/network commands. Include
Chinese retrieval fixtures and a runnable evaluation command. CI runs tests and
lint on Windows and Linux; dependencies have bounded versions and Docker has a
build check and smoke route. Document platform/container limits and all settings.

No claim of eliminating unknown vulnerabilities or validating paid live models.
