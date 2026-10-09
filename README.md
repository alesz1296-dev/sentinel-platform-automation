# SNTL Automation Platform

SNTL Automation Platform is a Python/FastAPI platform automation and validation system. It orchestrates versioned test workflows across simulated bare-metal platforms, records platform state and test results, and recovers from expected and unexpected reboots, freezes, and state mismatches.

The hardware-facing tools are deliberate black boxes. SNTL models their contracts and lifecycle evidence while concentrating implementation effort on cloud architecture, Kubernetes operations, observability, security, reliability, and software delivery.

## Portfolio goals

- Build a real Python/FastAPI control plane and CLI.
- Practice Kubernetes, Terraform, AWS, CI/CD, and DevSecOps practices.
- Use Prometheus, Grafana, and OpenTelemetry for correlated logs, metrics, and traces.
- Implement durable job execution, recovery policies, RBAC, audit trails, and artifact retention.
- Start locally; deploy AWS only through reviewed, manual-first steps.

## Platform lifecycle

Workflows may combine pre-EFI/BIOS preparation, EFI tasks, OS boot and stabilization, OS-specific tests, and reboot cycles. A workflow can omit configuration phases, execute tasks in EFI, move between Windows, Linux, and Solaris, or apply a configuration after a reboot.

```text
BIOS image/configuration → power on → device discovery → EFI stabilization
→ EFI tasks/configuration → OS boot → OS health checks → test execution
→ optional reboot and next lifecycle stage
```

Platforms run transitions serially. Multiple platforms can execute concurrently. Once an OS is stable, a workflow may allow compatible OS tests to execute in parallel.

## Current scope

The first implementation will use simulated platforms with labels for EFI/bare-metal, Linux, Windows, Solaris, and thermal-control support. Workflow executions collect representative BIOS/EFI logs, test stdout/stderr, telemetry, hardware/register evidence, MCAs, traces, metrics, and artifacts.

The project retains observability data for one day in its initial test environment.

## Documentation

- [Working standard](docs/working-standard.md)
- [Session log](docs/logs.md)
- [Change ledger](docs/changes.md)

Every feature follows Spec Kit gates. Specifications are the source of truth; code serves the specification.

## Status

Repository bootstrap and project standards are in progress. No application, infrastructure, or cloud resources have been implemented or deployed.
