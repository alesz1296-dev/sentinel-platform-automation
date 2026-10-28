# SNTL CI/CD pipeline design

## Purpose

SNTL CI proves code, infrastructure definitions, delivery configuration, and documentation are safe to review. CD prepares and promotes immutable artifacts through local simulation environments. No workflow automatically creates AWS resources, applies Terraform, mutates Kubernetes, or deploys to cloud infrastructure.

The design reuses the Secure EKS Delivery baseline: pre-commit validation, Actionlint, TFLint, Checkov, Gitleaks, Terraform plan-only OIDC, hardened image scanning, SBOM evidence, and optional signed ECR publication.

## Pipeline principles

- Run fast checks locally and independently in GitHub Actions.
- Pin GitHub Actions by commit digest and grant each job the minimum permission required.
- Use GitHub OIDC for future AWS plan and ECR-publishing roles; never store long-lived AWS credentials in GitHub.
- Build one immutable image per accepted commit and promote its digest between environments.
- Retain quality and security evidence for a defined short period.
- Keep Terraform apply, Helm install/upgrade, mutating kubectl actions, and AWS resource creation manual-first behind explicit approval.

## Pre-commit hooks

`.pre-commit-config.yaml` is the fast local gate. Developers run `pre-commit run --all-files` before opening a pull request.

| Hook | Scope | Purpose |
| --- | --- | --- |
| Whitespace, EOF, YAML, JSON, merge-conflict checks | Changed files | Prevent malformed or accidental source changes |
| Ruff format and lint | Python app and tests | Style and static Python defects |
| Actionlint | `.github/workflows/` | GitHub Actions syntax and expression validation |
| Terraform format | Terraform files | Canonical HCL formatting |
| TFLint | Terraform root modules | Terraform and provider rule validation |
| Checkov | Terraform, Kubernetes, then Helm configuration | Infrastructure and configuration policy findings |
| Gitleaks | Working tree | Prevent secrets entering commits |

Hooks do not run Terraform apply, Kubernetes mutation, long load tests, network provisioning, or SonarQube analysis.

## Pull-request validation

`pr-validation.yml` runs when a pull request changes application code, tests, infrastructure, Kubernetes or Helm configuration, workflows, dependencies, or quality configuration.

| Job | Required checks | Notes |
| --- | --- | --- |
| Workflow and source hygiene | Actionlint, Gitleaks, structural checks | Gitleaks uses full history for the PR range |
| Python quality | Locked install, Ruff, pytest, mypy, pip-audit | Add Alembic validation once migrations exist |
| Infrastructure quality | Terraform fmt, `init -backend=false`, validate, TFLint, Checkov | Every Terraform root; no AWS credentials required |
| Kubernetes packaging | Helm lint/template and Kustomize build | Render only; never apply |
| Container verification | Docker build, Trivy, CycloneDX SBOM | Added when Dockerfile exists; upload evidence |
| SonarQube | Coverage report, analysis, Quality Gate | Trusted PRs and protected branch only |

These checks become protected-branch requirements after their implementations are stable and deterministic. A missing SonarQube credential is not a passing Quality Gate; it remains an explicitly pending integration.

## SonarQube analysis

SonarQube complements Ruff, mypy, pytest, and pip-audit. It supplies code-quality trends, coverage, duplication analysis, and a Quality Gate.

The first `sonar-project.properties` will define:

```text
sonar.sources=app
sonar.tests=tests
sonar.python.coverage.reportPaths=coverage.xml
sonar.sourceEncoding=UTF-8
sonar.exclusions=**/.git/**,**/.venv/**,**/.terraform/**,**/dist/**
```

The CI job runs tests with coverage, writes `coverage.xml`, and invokes the official scanner using `SONAR_TOKEN` and the SonarQube URL stored in GitHub configuration. It waits for the Quality Gate on trusted pull requests and `prod`. Fork pull requests use non-secret checks only.

## Delivery pipeline

`container-delivery.yml` runs after protected-branch validation and performs:

1. locked dependency installation, Ruff, pytest, mypy, and pip-audit;
2. Gitleaks scanning with repository history;
3. reproducible Linux image build;
4. Trivy scanning and CycloneDX SBOM generation;
5. upload of scan, SBOM, and later signature evidence;
6. optional ECR publication by digest through GitHub OIDC; and
7. keyless Cosign signing and SBOM attestation when ECR publication is enabled.

Kind development may use local images or a local registry. ECR publication is optional and does not imply EKS deployment. The delivery workflow never deploys AWS infrastructure.

## Local CD and promotion

Argo CD observes declarative local configuration. Promotion moves one previously built image digest from `dev` to `staging` to `production`; it does not rebuild the image. Argo Rollouts advances a canary only when Prometheus analysis meets documented success criteria. A failed analysis pauses or aborts the release and preserves evidence.

## Terraform pipeline

Terraform is designed and statically tested continuously but is unapplied by default.

| Trigger | Action | AWS access |
| --- | --- | --- |
| Pull request | Format, static init, validate, TFLint, Checkov | None |
| Manual workflow dispatch | Authenticated Terraform plan and plan artifact upload | OIDC plan-only role once AWS target exists |
| Explicitly approved future operation | Apply reviewed plan | Separate protected role and approval path |

The manual plan workflow uses a dedicated GitHub environment and a least-privilege OIDC role after the AWS target exists. It produces an artifact and never applies it. Costly resources remain disabled by default with a visible cost warning.

## Required repository configuration

| Configuration | Purpose |
| --- | --- |
| Protected `prod` branch | Require review and passing checks before merge |
| GitHub environments | Separate approval and variables for publication, planning, and promotion |
| SonarQube token and URL | Authenticated scan and Quality Gate |
| OIDC trust policies | Scoped access to future ECR and Terraform plan roles |
| Dependabot or equivalent | Visibility into action and Python dependency updates |
| Artifact retention policy | Preserve evidence without retaining it indefinitely |

## Implementation order

1. Add Python project metadata, pytest, Ruff, mypy, and coverage.
2. Add pre-commit hygiene, Ruff, Actionlint, Terraform, TFLint, Checkov, and Gitleaks hooks.
3. Add PR validation for source hygiene, Python quality, and static infrastructure/package checks.
4. Configure SonarQube and make its trusted-PR Quality Gate required.
5. Add image build, Trivy, SBOM, and evidence retention.
6. Add Helm/Kustomize rendering and local Argo CD/Rollouts release checks.
7. Add Terraform plan-only OIDC after the AWS design is ready.
8. Add optional ECR publication, signing, and attestation after protected environments are reviewed.

## Evidence

Each accepted change retains its workflow result, lint/test reports, coverage, SonarQube Quality Gate, Terraform static-validation result, rendered Kubernetes configuration, image scan/SBOM evidence when applicable, and release or rollback evidence when applicable.
