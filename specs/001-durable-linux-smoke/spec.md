# Feature 001: durable simulated Linux smoke workflow

Status: Draft / Specify and Clarify. Not approved for implementation.
Date: 2026-10-31.
Product owner and phase acceptance: alesz1296-dev.
Implementation owner: coding assistant, under user direction.
Reviewer and phase acceptance: alesz1296-dev. Shared-contract review is deferred for this English-only MVP.

## Purpose and governing requirements

Deliver the first SNTL workflow that can be submitted, executed against a simulated target, inspected, and recovered after Worker loss. Use this feature to learn domain modeling, transactions, concurrency, API boundaries, and recovery through reproducible evidence.

Sources: [system behavior](../../docs/SYSTEM-BEHAVIOR.md), [architecture](../../docs/ARCHITECTURE-AND-ROADMAP.md), [golden path](../../docs/GOLDEN-PATH.md), and [working standard](../../docs/working-standard.md).

Existing product requirements remain authoritative. Proposed decisions below are not silently accepted changes to those requirements. This feature follows Specify -> Clarify -> Plan -> Tasks -> Analyze -> Implement -> Review. Before code, complete plan.md, data-model.md, contracts/, docs/tasks.md, quickstart.md, and research.md where required by the standard.

## Phase control

Each implementation packet ends with assistant verification, user-run checks, and explicit user acceptance. A passing automated check does not authorize starting the next packet. The current packet is P1. Numbering here is feature-local; it does not replace the broader golden-path phases.

| Packet | Deliverable | User validation gate |
| --- | --- | --- |
| P1: specification | Resolve decisions, formalize contracts, transitions, schema, plan, and test cases. | Review examples and failure outcomes; approve the specification. |
| P2: domain and simulator | Python package, state rules, deterministic simulator, unit tests, basic local quality checks. | Run valid/invalid lifecycle cases and inspect events. |
| P3: persistence | PostgreSQL migrations, repositories, transaction boundaries, lease and idempotency constraints. | Run integration tests, restart persistence, and inspect stored history. |
| P4: local execution | API, Orchestrator, Worker and simulator connected for one complete workflow. | Submit, poll, cancel, and inspect evidence locally. |
| P5: recovery | Worker-loss and unknown-outcome reconciliation, fencing and bounded retries. | Reproduce failures and verify no duplicate accepted results or unsafe re-execution. |

Kind, broader telemetry dashboards, deployment promotion, and AWS follow subsequent reviewed feature packets. Basic structured logs and correlation begin with the implementation, and relevant CI checks grow with the code.

## First user story

As an engineer, I submit an approved immutable Linux smoke workflow to a compatible simulated target, inspect its progress and evidence, and receive an unambiguous outcome even if a Worker fails.

Lifecycle: initialize -> configure BIOS -> power on/device discovery -> EFI readiness -> EFI smoke -> Linux handoff -> Linux readiness -> one Linux smoke test -> completion.

Initialization remains a symbolic operation. Do not invent proprietary Init SV behavior. Linux and EFI execution are explicitly simulated.

## Requirements

- R01: Pin every run to an approved workflow version and content digest; allow only registered symbolic operations and validated inputs.
- R02: Support explicit target selection and capability-based target selection. In either mode, reject a workflow before dispatch when no nominated or eligible platform satisfies every declared requirement: product, capabilities, minimum memory, minimum CPU cores, thermal-control need, supported OS, required devices, health, and availability.
- R03: Keep desired state, observed state, execution stage, boot-session identity, and health separate.
- R04: Permit one active mutating workflow per platform. This feature executes tests serially; the data model must not imply that future OS-test concurrency is impossible.
- R05: Persist workflow progress, attempts, partial results, transitions, and evidence metadata. A process restart must not erase them.
- R06: Deduplicate concurrent submission of the same request under one caller/key scope. Reuse of a key with different inputs must fail explicitly.
- R07: Record work durably before dispatch. Execute platform operations outside database transactions.
- R08: Fence obsolete Workers at both the result-acceptance boundary and simulator mutation boundary. Lease expiry alone is insufficient protection.
- R09: Distinguish assertion failure from execution timeout, Worker loss, target failure, and unknown outcome.
- R10: Reconcile uncertain operations by stable operation identity and observed state before replay. Do not claim exactly-once execution across the database and simulator.
- R11: Cancellation stops new dispatch, permits bounded cleanup, and preserves partial evidence. Unsafe targets remain unavailable until reconciliation or quarantine.
- R12: Expose submission/status/cancellation and evidence inspection through a contract reviewed before implementation. Validate caller identity, role and ownership; local identity mechanism remains to be selected.
- R13: Emit structured, redacted events with existing SNTL correlation identifiers. Resolve aliases before adding new identifier names.
- R14: Apply the existing one-day test-environment artifact/telemetry retention requirement. Decide durable run/audit and idempotency retention separately.
- R15: Bound retries and deadlines through explicit policy; terminal failure cannot silently return an unsafe target to service.

### Platform requirement model

Each platform has exactly one immutable `product` identity. Initial product values include `ICX`, `SPR`, `DMR`, `EMR`, and `SRF`; the complete controlled vocabulary is extended through reviewed inventory/configuration changes. A platform cannot advertise multiple products. A workflow declares exactly one required product for this initial slice, and SNTL rejects any platform whose product does not match.

The initial workflow requirement schema includes:

- `product` (required): one supported product identity.
- `supported_os` (required for OS workflow steps): for this slice, `linux`.
- `required_capabilities`: e.g. `efi`, `thermal-control`.
- `minimum_memory_mib` and `minimum_cpu_cores`.
- `required_devices`: e.g. `network`, `storage`.
- `thermal_control_required`: explicit boolean for clear user intent, normalized with required capabilities during validation.

The request may name a target with `platform_id`, define requirements for SNTL to select an eligible target, or supply both. Supplying both means the named platform must satisfy all requirements; SNTL does not silently choose another target.

### Default retry policy

The Linux-readiness operation receives a workflow-configurable retry policy. The default is three retries after the initial attempt, with delays of 30 seconds, 1 minute, and 2 minutes. A workflow can select zero retries or another bounded retry count and delay schedule, subject to server-side maximums defined in the final contract. Each attempt has its own timeout. The first contract must make the requested timeout and retry schedule explicit; it must distinguish a retry delay from an attempt timeout.

## Acceptance scenarios

| ID | Scenario | Required observable result |
| --- | --- | --- |
| A01 | Submit approved Linux workflow to compatible target. | Ordered stages complete, run succeeds, evidence and attempt history are readable. |
| A02 | Submit unknown workflow/version or incompatible target. | Clear rejection; no platform operation dispatched. |
| A03 | Request a Linux operation before Linux readiness. | Guard rejects it; platform is not mutated by that operation. |
| A04 | Submit identical requests concurrently with the same caller/key. | One accepted logical submission; callers can resolve the same run. |
| A05 | Reuse that key with different inputs. | Explicit conflict; original submission is unchanged. |
| A06 | Two Workers contend for the same platform. | Only current ownership can authorize mutation and accepted results. |
| A07 | Simulator assertion fails after earlier successful steps. | Run fails according to policy; earlier results and assertion evidence remain. |
| A08 | Kill Worker before operation completion. | Expiry triggers bounded reconciliation and an eligible retry or recorded terminal outcome. |
| A09 | Operation completes but acknowledgement is lost. | Reconciliation detects completion; the side effect is not blindly repeated. |
| A10 | Obsolete Worker returns after takeover. | Its mutations and result writes are rejected by fencing. |
| A11 | Cancel queued and running work. | No new dispatch after cancellation acceptance; running outcome follows the reviewed cancellation contract. |
| A12 | Restart API/Orchestrator with durable work pending. | State/history survive and eligible work is reconstructed. |
| A13 | Caller lacks role or ownership. | Access is rejected and no protected mutation occurs. |
| A14 | Simulator operation outcome cannot be established. | Bounded policy stops unsafe reuse; evidence states the uncertainty. |
| A15 | Submit an `SPR` workflow against an otherwise healthy `ICX` platform. | Admission fails before dispatch and identifies product mismatch. |
| A16 | Submit a thermal-control workflow to an `SPR` platform without thermal control. | Admission fails before dispatch and identifies the unmet requirement. |
| A17 | Inject three retryable Linux-readiness failures. | Attempts are recorded with the configured 30s, 1m, and 2m delays; terminal result follows policy after retry budget exhaustion. |
| A18 | Submit a workflow with retry overrides. | The validated override is persisted with the run and governs that run only. |

These are acceptance requirements, not executed test results. P1 assigns them to unit, integration, and end-to-end tests and supplies reproducible commands as implementation becomes available.

## Clarifications and design gaps

| ID | Gap | Proposal / required resolution | Status |
| --- | --- | --- | --- |
| D01 | How does the first job select a platform? | Support either an explicit platform ID or requirement-based selection. Admission validates all declared requirements before dispatch. Explicit selection fails if the named platform cannot satisfy them; automatic selection chooses an eligible platform or fails with reasons. | Resolved 2026-10-31 |
| D02 | Local test environment | Windows PowerShell with Docker Desktop. Quickstart and local commands target this environment first. | Resolved 2026-10-31 |
| D03 | Language and reviewers | English-only MVP; alesz1296-dev is the sole phase reviewer. Future localization and shared contract review remain roadmap work. | Resolved 2026-10-31 |
| D04 | State vocabulary | Resolved in [plan.md](plan.md): canonical lifecycle states are distinct from execution stage and OS identity; legacy YAML aliases map during validation only. | Resolved 2026-10-31 |
| D05 | Job versus workflow run | Resolved: one submission creates one run. Automatic retries create attempts; a manual rerun creates a new run that references its source. | Resolved 2026-10-31 |
| D06 | Transition ownership | Resolved in [plan.md](plan.md): the Orchestrator alone advances durable workflow state; Workers propose facts. | Resolved 2026-10-31 |
| D07 | Idempotency contract | Resolved in [contracts/openapi.yaml](contracts/openapi.yaml): caller plus key is unique, request fingerprint mismatch is a conflict, and replay returns the original run. | Resolved 2026-10-31 |
| D08 | Claims and leases | Resolved in [data-model.md](data-model.md): task claims and platform leases are separate, renewable, database-clock based, and fenced. | Resolved 2026-10-31 |
| D09 | Simulator continuity | Resolved: the simulator is an in-process typed adapter in P2, with operation records held by the durable repository interface in P3; HTTP transport is deferred. | Resolved 2026-10-31 |
| D10 | Cancel versus completion race | Resolved in [plan.md](plan.md): the first valid terminal compare-and-set wins; late results remain audit evidence and cannot overwrite the terminal run. | Resolved 2026-10-31 |
| D11 | Durable database design | Resolved in [data-model.md](data-model.md), including migrations, constraints, indexes, artifact protocol, and retention. | Resolved 2026-10-31 |
| D12 | Identity and API schema | Resolved: one configured development bearer token maps to identity `ale` with Engineer and Administrator roles; it is development-only and hardened identity is a later mandatory feature. | Resolved 2026-10-31 |
| D13 | Product taxonomy governance | Resolved: validated configuration list seeded with ICX, SPR, DMR, EMR, and SRF. Inventory can use only configured values; configuration changes do not require an application release. | Resolved 2026-10-31 |
| D14 | Retry-policy limits | Resolved: zero to five retries; each delay at most 10 minutes; per-attempt timeout at most 10 minutes; delays are an explicit validated schedule. | Resolved 2026-10-31 |

## Scope boundaries

Defer UI, Windows/Solaris scenarios, enforced-priority preemption, parallel same-platform tests, external brokers, new service splits, and generic chaos orchestration. These remain separate roadmap decisions, not removed product requirements.

## P1 exit criteria

- Clarifications D01-D14 are resolved and recorded in the linked design artifacts.
- Contracts, data model, transition table, implementation plan and scoped task list exist and agree with this spec.
- Every requirement has an acceptance scenario and an assigned test layer; cancellation, concurrency and crash boundaries are explicit.
- Technical research supports any newly selected dependencies or API behavior.
- User approves P1 before P2 begins. Current acceptance: pending.
