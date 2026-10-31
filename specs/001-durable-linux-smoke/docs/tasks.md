# Feature 001 tasks

Status: P2 implementation complete; user validation required before P3 begins.

| ID | Packet | Task | Owner | Reviewer | Required validation | Documentation impact |
| --- | --- | --- | --- | --- | --- | --- |
| T01 | P2 | Scaffold Python packaging, lint/test/type-check configuration, and source layout. | Coding assistant | alesz1296-dev | local quality commands | quickstart | Implemented; pending user validation |
| T02 | P2 | Implement typed canonical states, transition guards, requirement matching, retry-policy validation, and workflow schema parsing. | Coding assistant | alesz1296-dev | domain unit tests | contracts and data model cross-check | Implemented; pending user validation |
| T03 | P2 | Implement deterministic in-process simulator with operation IDs, fencing validation, and fault fixtures. | Coding assistant | alesz1296-dev | simulator unit tests | quickstart scenarios | Implemented; pending user validation |
| T04 | P3 | Add PostgreSQL compose profile, SQLAlchemy mappings, Alembic initialization, and core migrations. | Coding assistant | alesz1296-dev | clean migration integration test | data model |
| T05 | P3 | Implement repositories for submission/idempotency, platform selection, task claims, leases, attempts, events, and artifacts. | Coding assistant | alesz1296-dev | PostgreSQL integration tests | data model |
| T06 | P4 | Implement development-token authentication, API endpoints, OpenAPI validation, and CLI flows. | Coding assistant | alesz1296-dev | API/contract tests | quickstart |
| T07 | P4 | Implement local Orchestrator/Worker loop and complete successful Linux smoke run. | Coding assistant | alesz1296-dev | end-to-end local test | demo/runbook |
| T08 | P5 | Implement heartbeat expiry, delayed retry scheduler, unknown-outcome reconciliation, and cancellation race handling. | Coding assistant | alesz1296-dev | recovery integration tests | recovery runbook |
| T09 | P5 | Prove stale Worker fencing, three default retries, override validation, and no duplicate accepted outcome. | Coding assistant | alesz1296-dev | deterministic fault suite | test evidence |

No AWS, Kind, GitHub mutation, Terraform apply, Helm deployment, or Git operations are in this work packet.
