# Feature 001 research decisions

## Selected patterns

- PostgreSQL remains the initial durable coordination authority. It provides transactional run creation, short task claims, leases, and fencing without adding a broker before measured need.
- Workers execute outside transactions. Long-running platform operations never hold database locks; the Orchestrator atomically accepts resulting facts.
- Idempotency is request-level, scoped to caller and `Idempotency-Key`, with a canonical fingerprint. This yields at-least-once request delivery with one logical submission, not impossible end-to-end exactly-once platform operations.
- Fencing tokens protect takeover. A lease expiry permits a new owner, while monotonically increasing fencing rejects obsolete mutation and result attempts.
- Explicit retry delays make the initial policy easy to explain and test. Backoff algorithms can be introduced later if operational data justifies them.
- A development bearer token gives the MVP an authorization boundary. It is intentionally replaced during the security-hardening phase, rather than presented as a deployable identity system.

## Deferred dependency decisions

Select exact Python, FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL-driver, test, lint, and type-check versions in P2 after the project package metadata is created. Keep all dependencies pinned and record material compatibility findings in the implementation change.
