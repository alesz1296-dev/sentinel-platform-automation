# Feature 001 data model

Status: proposed design pending user Phase 1 review. PostgreSQL implementation starts in P3.

All identifiers are UUIDs, timestamps are UTC `timestamptz`, and mutable records include `created_at`, `updated_at`, and a numeric optimistic `version` where API concurrency requires it. Enumerations are application-controlled strings checked by database constraints or PostgreSQL enum types selected in the migration design.

## Core tables

| Table | Key columns | Constraints and indexes |
| --- | --- | --- |
| `products` | `code`, `display_name`, `active` | `code` unique; seeded ICX, SPR, DMR, EMR, SRF; configuration controlled. |
| `platforms` | `id`, `product_code`, `memory_mib`, `cpu_cores`, `supported_os`, `lifecycle_state`, `observed_os`, `health`, `boot_session` | one product FK; positive resources; index eligibility fields; one product only by non-null single FK. |
| `platform_capabilities` | `platform_id`, `capability` | unique pair; controlled capability vocabulary. |
| `platform_devices` | `platform_id`, `device` | unique pair; controlled device vocabulary. |
| `workflow_versions` | `id`, `name`, `version`, `content_digest`, `definition_json`, `published_at` | unique `(name, version)` and unique digest; immutable after publish. |
| `workflow_runs` | `id`, `workflow_version_id`, `requested_platform_id`, `assigned_platform_id`, `actor_id`, `status`, `requirements_json`, `idempotency_key`, `request_fingerprint`, `source_run_id` | unique `(actor_id, idempotency_key)` while retained; index status/created time; assigned platform FK. |
| `task_instances` | `id`, `run_id`, `step_id`, `sequence`, `status`, `retry_policy_json`, `next_eligible_at` | unique `(run_id, step_id)`; index runnable task predicate. |
| `task_attempts` | `id`, `task_instance_id`, `number`, `worker_id`, `operation_id`, `fencing_token`, `status`, `outcome`, `started_at`, `finished_at`, `deadline_at`, `result_json` | unique `(task_instance_id, number)` and `operation_id`; index active attempts. |
| `platform_leases` | `platform_id`, `owner_run_id`, `fencing_token`, `expires_at`, `heartbeat_at` | one current lease per platform; fencing token increases on each acquisition. |
| `task_claims` | `task_instance_id`, `attempt_id`, `worker_id`, `expires_at` | one active claim per task; short-lived and separate from platform lease. |
| `transition_events` | `id`, `run_id`, `task_attempt_id`, `platform_id`, `from_state`, `to_state`, `reason`, `actor_type`, `occurred_at` | append-only; indexes by run, platform, and time. |
| `artifacts` | `id`, `task_attempt_id`, `storage_key`, `checksum_sha256`, `size_bytes`, `status`, `retention_until` | unique storage key; only `AVAILABLE` after upload and checksum verification. |
| `audit_events` | `id`, `actor_id`, `action`, `resource_type`, `resource_id`, `outcome`, `metadata_redacted`, `occurred_at` | append-only; index actor/time and resource/time. |

## Database transaction boundaries

- Submission transaction: authenticate/authorize, validate workflow and requirements, lock/check idempotency key, create run/tasks/audit event, then commit. The Orchestrator sees only committed work.
- Selection/lease transaction: query eligible platforms with row-level locking, verify health and requirements again, increment fencing token, create/renew lease, assign the run, emit event, commit.
- Claim transaction: claim one runnable task using `FOR UPDATE SKIP LOCKED`, create attempt and claim, commit. Never hold a transaction while executing a platform operation.
- Result-acceptance transaction: lock task/run/platform lease, reject obsolete fencing or terminal run, persist attempt outcome/evidence metadata, atomically advance task and run or calculate `next_eligible_at`, append events/audit data, commit.
- Artifact protocol: write bytes to an attempt-specific temporary key, calculate checksum, move/promote it, then create `AVAILABLE` metadata in the result transaction. Reconciliation cleans incomplete uploads by policy.

Database `CURRENT_TIMESTAMP` determines lease expiry comparisons. Worker process clocks are never authoritative. Lease acquisition and result acceptance verify the fencing token. A restarted Worker may report an old fact, but it cannot mutate platform state or accept a stale result.

## Retention and migrations

Artifacts retain for one day in the initial environment. Metrics/logs/traces follow their own one-day operational retention. Run, transition, and audit history is retained until a later documented retention policy replaces the MVP default; idempotency keys retain for at least 24 hours to preserve replay behavior.

Use Alembic revisions. Each schema change has an upgrade path, a documented downgrade decision, and an integration test that runs migrations against an empty PostgreSQL database. Reverting application code never automatically reverses data migrations.
