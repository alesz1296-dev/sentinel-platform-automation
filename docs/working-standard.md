# SNTL Automation Platform working standard

This standard applies to every SNTL Automation Platform contributor and session. It adapts the supplied Spec Kit, collaboration, CI, security, and manual-first infrastructure requirements to this project.

Before implementation begins, use the [Golden path and design review](GOLDEN-PATH.md) to select the current phase and record resolved decisions from its gap register.

## Spec-driven development

Every feature follows this sequence:

```text
Constitution → Specify → Clarify → Plan → Tasks → Analyze → Implement → Review
```

Required artifacts are created under `specs/<feature>/` before implementation:

- `spec.md`
- `plan.md`
- `docs/tasks.md`
- `research.md` for provider, API, legal, or AI decisions
- `data-model.md` for persistence changes
- `contracts/` for API changes
- `quickstart.md` for validation scenarios

Specifications are the source of truth. Code must serve the specification. Do not invent API schemas, credentials, provider choices, or business decisions. Verify that `specs/<feature>/spec.md` exists before implementing.

## Git rules

Assistants must never execute Git commands, including read-only commands. The user performs repository operations. The workflow below is guidance for human contributors; assistants supply commands only when requested.

Never work directly on `main`. Before starting work, run `git pull`, review the repository status, then create a dedicated branch using one of:

```text
feat/  fix/  refactor/  docs/  chore/
```

Inspect changes before staging. Stage explicit files only; do not use `git add .` unless every change has been reviewed and intentionally included. Verify staged changes with `git status` and `git diff --staged`.

The following actions require an explanation and explicit user approval immediately before execution:

- `git commit`
- `git push`
- `git merge`
- `git rebase`
- `git reset`
- `git branch -d`
- `git tag`

Use Conventional Commits: `feat:`, `fix:`, `refactor:`, `docs:`, or `chore:`. Do not add AI attribution, co-author trailers, or tool-generated signatures to commits or pull requests.

All changes reach `main` through a pull request. Do not merge directly into `main`.

## Documentation and collaboration

Before proposing a commit, update `docs/logs.md` and `docs/changes.md` on the same branch and in the same commit. Never defer documentation synchronization to a follow-up pull request.

Each session entry in `docs/logs.md` includes:

1. Date
2. GitHub user
3. Branch
4. Objective
5. Work completed
6. Files or areas changed
7. Tests and checks run
8. Decisions made
9. Blockers (`None` when applicable)
10. Next steps

Each commit row in `docs/changes.md` includes date, user, branch, hash, message, summary, tests/checks, and PR link when available.

Every task needs a primary owner, reviewer, phase, Spec Kit reference, required tests, and documentation impact. A reviewer must approve a work packet before it becomes Complete. For the English-only MVP, alesz1296-dev is the sole reviewer; shared-contract review is added when collaboration scope requires it.

## Quality and CI

The [CI/CD pipeline design](CI-CD-PIPELINE.md) is the authoritative implementation plan for local hooks, pull-request validation, SonarQube, container evidence, release promotion, and Terraform plan-only automation.

CI begins in Phase 0 and runs:

- `pytest`
- `ruff check .`
- `mypy app tests`
- Actionlint for GitHub Actions workflows
- Terraform formatting, validation, TFLint, and Checkov for infrastructure changes
- Gitleaks for secret detection
- SonarQube analysis and Quality Gate after trusted-project credentials are configured

As relevant code is introduced, add Alembic migration validation, Docker build validation, `terraform validate`, and Helm template validation. Required checks must pass before a pull request can merge.

English is the MVP language. User-facing language behavior requires tests; Spanish and future locales use locale codes when localization becomes a planned feature.

## Security and access

Never commit secrets, credentials, certificates, private configuration, `.env`, or `.env.local` files. Verify that sensitive files are not staged.

Sentinel uses application RBAC for viewer, engineer, platform operator, and administrator responsibilities. AWS IAM and Kubernetes RBAC govern infrastructure access separately. User records enforce ownership in API handlers and tests. Auth, OAuth, session, token, and user-data export/deletion changes require explicit tests.

## Manual-first infrastructure

Kubernetes and AWS work is manual-first. Humans review and run all mutating infrastructure commands.

- No automatic `terraform apply`, Helm deployment, mutating `kubectl`, or AWS resource creation.
- Every mutating infrastructure or deployment action requires an explanation and explicit approval.
- Docker Compose and local Kubernetes remain the default low-cost path.
- Validate local Kubernetes with Helm, kind or k3d, port-forwarding, local secrets, and PostgreSQL before AWS.
- AWS planning supports low-cost development, EKS, ECS/Fargate, and a production-like reference. Expensive resources are disabled by default or protected by explicit variables and cost warnings.
- Secrets use AWS Secrets Manager; non-secret configuration may use SSM Parameter Store or Terraform variables.

## SNTL-specific design boundaries

SNTL must build, run, test and deploy independently of sibling projects. Generic chaos orchestration, hidden-root-cause training and scoring are outside scope. See [project boundaries](PROJECT-BOUNDARIES.md).

The enterprise hardware adapters are black boxes. SNTL owns job sequencing, platform leases, observed state, recovery, observability, RBAC, audit trails, and deployment. It does not reproduce proprietary BIOS, EFI, register, or IPS implementations.

Tests may destabilize a target. Recovery is stage-aware, bounded, and automated: probe, soft reboot, hard power cycle, reset known configuration, cooldown, retry, fail, or quarantine with alerts. One-day retention applies to the initial test environment's logs, traces, metrics, and artifacts.
