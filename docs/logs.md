# Session log

## 2026-10-31 - Feature 001 Phase 2 implementation

- User: alesz1296-dev; branch not inspected; no Git commands.
- Objective: begin the pure-Python domain and deterministic simulator after Phase 1 approval.
- Work/areas: added project packaging, domain states/value objects, admission rules, retry validation, fenced deterministic simulator, and initial unit tests.
- Decisions: Phase 2 has no persistence, API, containers, Kubernetes, or cloud operations.
- Checks: `python -m pytest -q` passed (7 tests); `python -m ruff check . --no-cache` passed. Installed mypy 2.1.0 terminated with an internal error before analysis; cache-disabled retry behaved the same. `compileall` could not create bytecode caches because this workspace path denies that write, while pytest itself passed.
- Blockers: none.
- Next: user validates P2 with the quickstart command. Do not begin P3 persistence work until accepted.

## 2026-10-31 - First feature specification

- User: alesz1296-dev; branch not inspected; no Git commands.
- Objective: begin spec-driven delivery with user validation between phases.
- Work/areas: drafted specs/001-durable-linux-smoke/spec.md and linked it from README.
- Decisions: P1 is Specify/Clarify; local target is Windows PowerShell with Docker Desktop; the MVP is English-only and reviewed by alesz1296-dev; runs support explicit and requirement-based platform selection with pre-dispatch eligibility validation.
- Follow-up decisions: each platform represents one product family; initial examples are ICX, SPR, DMR, EMR and SRF. Workflow admission validates product, hardware/resource requirements, capabilities and OS. Linux readiness defaults to three configurable retries with 30-second, one-minute and two-minute delays.
- Work completed: finalized the Phase 1 design artifacts for feature 001: plan, data model, OpenAPI draft, task list, validation guide and research decisions. Application implementation remains pending Phase 1 acceptance.
- Checks: draft reviewed against system behavior and working standard; relative document links checked.
- Blockers: platform-selection, local runtime, language/reviewer answers pending; detailed P1 contracts and plan remain to be completed.
- Next: resolve clarifications, complete the feature design packet, and obtain user review before P2.

## 2026-10-31 - Golden path and design-gap review

- Objective: make the proposed SNTL architecture executable as a local-first implementation sequence and expose material design gaps before coding.
- Work: added `GOLDEN-PATH.md` with the first vertical slice, acceptance gates, durable-state design, observability criteria, intentional deferrals, and decisions required before local, Kind, and AWS phases.
- Checks: documentation links reviewed; no Git commands run.
- Next: choose the first feature specification and resolve its Phase 1 decisions before implementing it.

## 2026-10-31 - Standalone SNTL scope

- User: alesz1296-dev; branch not inspected; no Git commands.
- Objective: remove the external experiment-project integration requirement from SNTL.
- Work: updated README, context, simulation/implementation guides and architecture views; added PROJECT-BOUNDARIES.md; archived the superseded integration proposal. Clarified the no-Git rule in the working standard.
- Decisions: SNTL owns domain simulation, recovery, operational telemetry and its own acceptance tests; generic chaos and incident-training products are out of scope.
- Checks: active-reference and Markdown link validation.
- Blockers: none.
- Next: specify SNTL's first durable workflow slice independently.

Earlier entries below record historical decisions, including the now-superseded external integration proposal.

## 2026-10-31 - Separate Alpha Legion experiment project

- User: alesz1296-dev.
- Branch: not inspected; no Git commands run.
- Objective: extract generic chaos, traffic, and incident-training framework requirements into the sibling Alpha Legion project.
- Work: added explicit ownership and cross-project links to the README, context, simulation guide, implementation plan, both architecture views, and architecture roadmap; added ALPHA-LEGION-INTEGRATION.md.
- Decisions: SNTL keeps domain recovery and operational evidence; Alpha Legion independently owns experiments, cleanup, training and verification. Existing SNTL exercises are integration criteria.
- Checks: documentation link and content review; no deployment or experiments.
- Blockers: none.
- Next: specify the first Alpha Legion vertical slice and SNTL attachment profile.

## 2026-10-28 — Architecture views recorded separately

- **GitHub user:** alesz1296-dev
- **Branch:** Not inspected by request.
- **Objective:** Record the local and AWS architecture views in focused Markdown documents.
- **Work completed:** Added separate local Kind and optional AWS architecture documents with Mermaid diagrams and a local-to-AWS mapping. Linked both from the README and project context.
- **Files or areas changed:** `README.md`, `docs/PROJECT-CONTEXT.md`, `docs/ARCHITECTURE-LOCAL.md`, `docs/ARCHITECTURE-AWS.md`, `docs/logs.md`, `docs/changes.md`.
- **Tests and checks run:** Documentation paths and Mermaid source reviewed; no Git commands run by request.
- **Decisions made:** The roadmap remains the reconciliation document; focused architecture files provide stable views for local operation and AWS validation.
- **Blockers:** None.
- **Next steps:** Keep the two views synchronized through the shared logical boundary table.

## 2026-10-28 — Architecture views reconciled

- **GitHub user:** alesz1296-dev
- **Branch:** Not inspected by request.
- **Objective:** Reconcile the local simulation diagram with the AWS target architecture.
- **Work completed:** Added a logical-to-deployment mapping, clarified the initial API/orchestrator/workers deployment boundary, and added a consistent AWS target Mermaid view using RDS, S3, IAM, and observability equivalents.
- **Files or areas changed:** `docs/ARCHITECTURE-AND-ROADMAP.md`, `docs/logs.md`, `docs/changes.md`.
- **Tests and checks run:** Mermaid source and documentation references reviewed; no Git commands run by request.
- **Decisions made:** The diagrams are compatible views of one architecture. Logical modules are not required to become separate deployments until scale, ownership, or failure isolation justifies the split.
- **Blockers:** None.
- **Next steps:** Keep local and AWS environment overlays mapped to the same service contracts.

## 2026-10-28 — Local-first architecture diagram

- **GitHub user:** alesz1296-dev
- **Branch:** Not inspected by request.
- **Objective:** Make the SNTL control plane, simulated target, observability, delivery, and optional AWS boundaries visible in the architecture roadmap.
- **Work completed:** Replaced the minimal architecture diagram with a Mermaid diagram showing the two Kind failure domains, workflow services, telemetry backends, k6, Argo delivery, GitHub Actions, Terraform, and optional AWS services.
- **Files or areas changed:** `docs/ARCHITECTURE-AND-ROADMAP.md`, `docs/logs.md`, `docs/changes.md`.
- **Tests and checks run:** Mermaid source and documentation references reviewed; no Git commands run by request.
- **Decisions made:** The control cluster is the durable operations boundary; the target cluster is deliberately allowed to fail; AWS integrations remain optional and visually separated.
- **Blockers:** None.
- **Next steps:** Implement the first durable workflow slice and its local telemetry.

## 2026-10-28 — CI/CD pipeline design

- **GitHub user:** alesz1296-dev
- **Branch:** Not inspected by request.
- **Objective:** Document the SNTL CI/CD design using the established Secure EKS Delivery quality and infrastructure checks.
- **Work completed:** Added the CI/CD pipeline design covering pre-commit hooks, Actionlint, TFLint, Checkov, SonarQube, Gitleaks, container/SBOM evidence, local Argo promotion, and Terraform plan-only OIDC. Aligned the architecture roadmap's delivery, Terraform, acceptance, and operational-evidence phases with that design. Linked the pipeline design from the README, project context, and working standard.
- **Files or areas changed:** `README.md`, `docs/ARCHITECTURE-AND-ROADMAP.md`, `docs/CI-CD-PIPELINE.md`, `docs/PROJECT-CONTEXT.md`, `docs/working-standard.md`, `docs/logs.md`, `docs/changes.md`.
- **Tests and checks run:** Documentation paths and links will be verified; no Git commands are run by request.
- **Decisions made:** CI validates all code and configuration independently of local hooks; SonarQube Quality Gate is required only after trusted credentials and a stable project gate are configured; cloud mutation remains manual-first.
- **Blockers:** None.
- **Next steps:** Implement Phase 0 Python tooling and the pre-commit configuration from the documented order.

## 2026-10-28 — Simulation environment model

- **GitHub user:** alesz1296-dev
- **Branch:** Not inspected by request.
- **Objective:** Capture the detailed local DevOps/SRE simulation-environment model for SNTL.
- **Work completed:** Added the simulation environment guide covering Kind topology, environment promotion, k6 traffic profiles, service objectives, Alertmanager, observability, incident drills, troubleshooting, postmortem evidence, and the AWS validation boundary. Linked it from the README and project context.
- **Files or areas changed:** `README.md`, `docs/PROJECT-CONTEXT.md`, `docs/SIMULATION-ENVIRONMENT.md`, `docs/logs.md`, `docs/changes.md`.
- **Tests and checks run:** Not run by request; no Git commands were executed.
- **Decisions made:** Daily operations and failure practice occur locally on Kind; the target-cluster fault domain is separate from the control plane before isolation scenarios are tested.
- **Blockers:** None.
- **Next steps:** Review the guide, then use the repository workflow to stage and commit the explicit documentation files.

## 2026-10-28 — Local-first implementation context

- **GitHub user:** alesz1296-dev
- **Branch:** `docs/local-first-implementation-context`
- **Objective:** Record SNTL's local Kind-first operating model, enduring requirements, and optional AWS implementation path.
- **Work completed:** Added a concise project context and requirements brief plus a phased local-first plan covering the two-cluster topology, observability, traffic, fault injection, recovery evidence, and later Terraform/AWS mapping. Linked both documents from the README.
- **Files or areas changed:** `README.md`, `docs/PROJECT-CONTEXT.md`, `docs/LOCAL-FIRST-IMPLEMENTATION.md`, `docs/logs.md`, `docs/changes.md`.
- **Tests and checks run:** `git diff --check`; verified all README and intra-document links target existing files; reviewed the documentation diff.
- **Decisions made:** Kind is the primary SNTL delivery and operations environment; AWS is a Terraform-defined, optional and manual-first validation target. The control and simulated target workloads use separate Kind clusters once failure-isolation testing begins.
- **Blockers:** None.
- **Next steps:** Review the documentation diff, then stage the explicit files and request approval before committing.

## 2026-10-09 — Architecture documentation migration

- **GitHub user:** alesz1296-dev
- **Branch:** `chore/bootstrap-documentation`
- **Objective:** Bring the SNTL architecture and system-behavior documents into the canonical repository and align their branding.
- **Work completed:** Migrated the architecture roadmap and system-behavior specification into `docs/`; renamed their visible project references to SNTL; retained the AWS, Kubernetes, DevOps, DevSecOps, workflow, recovery, RBAC, and observability decisions.
- **Files or areas changed:** `docs/ARCHITECTURE-AND-ROADMAP.md`, `docs/SYSTEM-BEHAVIOR.md`, `docs/logs.md`, `docs/changes.md`.
- **Tests and checks run:** Documentation-only change; structural review and diff whitespace review pending before staging.
- **Decisions made:** Architecture documents belong in the canonical SNTL repository under `docs/`; this remains a documentation-only change.
- **Blockers:** None.
- **Next steps:** Review the focused diff, stage explicit documentation files, and request approval before committing.

## 2026-10-07 — Repository bootstrap

- **GitHub user:** alesz1296-dev
- **Branch:** `chore/bootstrap-documentation`
- **Objective:** Initialize Sentinel project documentation and establish the working standard.
- **Work completed:** Cloned the empty Sentinel repository; created the dedicated documentation branch; added the project README, working standard, session log, and change ledger.
- **Files or areas changed:** `README.md`, `docs/working-standard.md`, `docs/logs.md`, `docs/changes.md`.
- **Tests and checks run:** Verified the remote repository exists with `git ls-remote`; checked initial repository status. `git pull` was attempted but network access to GitHub was unavailable after cloning.
- **Decisions made:** Sentinel is the project name; Spec Kit is mandatory; FastAPI plus CLI are the first application interfaces; infrastructure is manual-first; no commit or push occurs without explicit approval.
- **Blockers:** GitHub network connection was unavailable for the required `git pull`; the repository was confirmed empty at clone time.
- **Next steps:** Review bootstrap files, update the change ledger before the first commit, request explicit approval to stage and commit, then begin the constitution/specification phase.
