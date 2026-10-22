# Security boundaries

Diagnosis endpoints never execute repair commands. Generated commands are untrusted
suggestions; JSON/schema validation does not make them safe for a particular host.
Do not wire model text to a shell. Local Python repair helpers accept named actions
and an explicit confirmation flag; they are not exposed through the API.

Local evidence collection is opt-in. Cloud use additionally requires explicit upload
permission. Evidence describes the API server/container, not the caller's computer.
Use only with trusted users. Pattern redaction is best effort; hostnames, event
messages and business data may remain sensitive.

Default deployment publishes localhost only. Set API_KEY, TLS, per-user rate limits
and a reverse proxy before remote exposure. API keys authenticate access but do not
provide user/tenant isolation. user_id is optional metadata, not an identity claim.
No diagnosis history is persisted by the service.

Knowledge, model caches and vector volumes must be writable only by trusted service
administrators. Checksums detect corruption, not malicious modifications by an
administrator. Model remote code is disabled; no pickle index loading is used.
Legacy index.pkl files are ignored. File sizes, counts and embedding dimensions are
bounded, and builds use locking/atomic publication.

Do not submit real secrets or host logs in public issues. Report a suspected defect
privately to the repository owner using an available private contact channel.
