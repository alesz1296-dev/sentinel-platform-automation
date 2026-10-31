# Feature 001 implementation plan

Status: Phase 1 design complete; implementation awaits user acceptance.

## Technical approach

Create one Python project with API, domain, Orchestrator, Worker, simulator and persistence packages. They share a domain contract but run as distinct roles once local execution begins. PostgreSQL is introduced in P3. The first simulator is a typed in-process adapter so P2 can test lifecycle correctness without network transport; P3 persists operation identity and evidence through repository interfaces, preserving the later option to extract it behind HTTP or gRPC.

Use PostgreSQL with SQLAlchemy and Alembic in P3. Use FastAPI and Pydantic for the P4 HTTP boundary. Exact dependency versions are selected in the implementation packet and locked in project metadata after compatibility research.

## Canonical state model

Never use one enum for all concepts:

| Concept | Canonical values for this feature |
| --- | --- |
| Workflow run status | `QUEUED`, `DISPATCHING`, `RUNNING`, `CANCEL_REQUESTED`, `SUCCEEDED`, `FAILED`, `CANCELED` |
| Task status | `PENDING`, `CLAIMED`, `RUNNING`, `RETRY_WAIT`, `SUCCEEDED`, `FAILED`, `CANCELED`, `BLOCKED` |
| Platform lifecycle state | `OFF`, `INITIALIZED`, `BIOS_CONFIGURED`, `POWERED_ON`, `DEVICES_DISCOVERED`, `EFI_READY`, `OS_BOOTING`, `OS_READY`, `RECOVERING`, `QUARANTINED` |
| Observed OS | `NONE`, `LINUX` |
| Platform health | `AVAILABLE`, `BUSY`, `DEGRADED`, `UNREACHABLE`, `FROZEN`, `RECOVERING`, `QUARANTINED` |
| Attempt outcome | `SUCCEEDED`, `ASSERTION_FAILED`, `RETRYABLE_FAILURE`, `TIMED_OUT`, `CANCELED`, `UNKNOWN`, `STALE_FENCED` |

Workflow schema aliases map only during validation: `INIT_SV -> INITIALIZED`, `BIOS_CONFIG -> BIOS_CONFIGURED`, `EFI -> EFI_READY`, and `LINUX -> OS_READY` plus `observed_os=LINUX`. Persist only canonical values.

## Transition and ownership rules

| Command | Owner | Guard | Durable outcome |
| --- | --- | --- | --- |
| Submit run | API | valid token/role, immutable workflow, idempotency key, valid requirements | run and tasks created in `QUEUED` |
| Select platform / acquire lease | Orchestrator | eligible product/resources/capabilities and no active lease | platform lease, fencing token, run moves to `DISPATCHING` |
| Claim task | Worker | runnable dependency, unexpired lease, no cancellation | task attempt and short task claim created |
| Execute operation | Worker + simulator | current fencing token, expected lifecycle/OS state, deadline | operation fact and evidence proposed; no direct run-state advance |
| Accept result / schedule retry | Orchestrator | current attempt and fencing token, valid source state | task/run progression or `RETRY_WAIT` |
| Request cancellation | API | caller owns run or has administrator role; run nonterminal | run becomes `CANCEL_REQUESTED`; no new claims |
| Commit terminal state | Orchestrator | compare-and-set from nonterminal state | first valid terminal result wins |

Allowed normal platform progression is `OFF -> INITIALIZED -> BIOS_CONFIGURED -> POWERED_ON -> DEVICES_DISCOVERED -> EFI_READY -> OS_BOOTING -> OS_READY`. Every adapter operation declares required and resulting canonical lifecycle/OS states. Recovery transitions are introduced in P5; until then, an unknown or unsafe operation result marks work failed and platform health degraded rather than replaying it.

Workers cannot mark a run successful or failed directly. They return a fact keyed by `operation_id`, `attempt_id`, and `fencing_token`. The Orchestrator performs an atomic acceptance update. If cancellation and completion race, the first committed valid terminal compare-and-set wins; later facts are retained as audit/attempt evidence but cannot overwrite a terminal run.

## Admission and retry policy

Every workflow declares one product, supported OS, capabilities, minimum memory, minimum CPU cores, device requirements and thermal-control requirement. A submission can supply `platform_id`, requirements, or both. With both, the named platform must pass every requirement. With requirements only, the Orchestrator chooses an eligible available platform deterministically by lowest active-run count and then platform ID. This rule is intentionally simple and testable.

Linux readiness defaults to three retries after an initial failed attempt with an explicit delay schedule `[30, 60, 120]` seconds. Overrides allow zero through five retries, a same-length delay schedule whose values are between 0 and 600 seconds, and an attempt timeout from 1 through 600 seconds. A workflow cannot set a retry policy for errors that are not classified retryable. Retry schedule and timeout are copied into the run/task record at submission, so later workflow edits cannot change an in-flight run.

## Security approach for the MVP

One configured local development bearer token authenticates identity `ale`, holding Engineer and Administrator roles. Store the token only in ignored local configuration. The API authenticates before mutation and includes actor identity in audit events. The token is sufficient only for local development. P8 must replace it with hardened identity, authorization policy management, secret rotation, least-privilege service identities, and the required RBAC implementation.

## Implementation sequence

1. P2: scaffold project tooling, typed domain model, workflow validation, state transition guards, deterministic simulator, and unit tests.
2. P3: add PostgreSQL, Alembic migrations, repositories, idempotency, task claims, leases/fencing, and integration tests.
3. P4: add API/CLI, local process roles, run submission/status/cancellation/evidence endpoints, and local quickstart.
4. P5: add heartbeat expiry, operation reconciliation, delayed retry scheduler, Worker-loss scenarios, stale-result rejection, and recovery-focused integration tests.

## Risks retained for later packets

- In-process simulator isolation does not model network failure; extract an adapter service before network fault exercises.
- Single development token does not demonstrate identity-provider integration; hardening remains mandatory before production-like operations.
- The first deterministic selection rule is not fairness, priority, or capacity scheduling. Those require measured workload behavior.
- Artifact bytes use a local adapter in P3/P4; MinIO/S3 compatibility is added behind the same interface later.
