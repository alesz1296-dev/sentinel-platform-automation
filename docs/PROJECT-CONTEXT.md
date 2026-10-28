# SNTL project context

## Purpose

SNTL is a platform automation and validation control plane. It accepts versioned hardware-validation workflows, selects a compatible simulated platform, drives its lifecycle through black-box adapters, records evidence, and applies bounded recovery when the target freezes, reboots unexpectedly, becomes unreachable, or enters an unexpected state.

The project deliberately simulates hardware-facing tools. The portfolio value is in the real implementation of durable orchestration, Kubernetes operations, observability, incident response, delivery practices, and infrastructure design. SNTL does not recreate proprietary BIOS, EFI, firmware, register, IPS, or hardware-driver implementations.

## Current delivery strategy

SNTL is local-first. The complete functional platform is developed and operated on Kind before any AWS deployment is considered.

The local platform has two independent Kubernetes failure domains:

```text
Control Kind cluster                         Target Kind cluster
--------------------                         -------------------
API, scheduler, workers                      simulated platform targets
PostgreSQL and artifact adapter              controlled reboot/freeze/failure modes
Prometheus, Grafana, Alertmanager            target health and lifecycle evidence
OpenTelemetry Collector, logs, traces
```

The control cluster schedules and observes target work. A simulated target may freeze, restart, or become isolated without taking down the control plane. A single-cluster setup is acceptable for early application development, but it is not sufficient evidence for control-plane survival during target-node failure.

AWS is a separately documented, Terraform-managed target architecture. The default is to write and validate the infrastructure without applying it. An AWS deployment is optional, manual-first, reviewable, short-lived, and justified by a specific cloud capability that cannot be validated locally.

## Product requirements

- Provide FastAPI and CLI interfaces for job submission, inspection, cancellation, platform operations, and evidence retrieval.
- Run only approved immutable workflow versions; every run records the workflow version and content digest used.
- Maintain separate desired state, observed state, execution stage, health, and boot-session identity for each platform.
- Enforce one active mutating workflow per platform through renewable leases and fencing tokens.
- Persist jobs, workflow runs, tasks, attempts, transitions, recovery decisions, incidents, audit events, and artifact metadata in PostgreSQL.
- Preserve partial evidence when a task, worker, or target fails.
- Detect and classify expected reboots, unexpected reboots, timeouts, freezes, lost connectivity, and state mismatches distinctly.
- Apply stage-specific, bounded recovery: re-probe, soft reboot, hard power cycle, reset a known configuration, cooldown, retry, fail, or quarantine.
- Expose correlated metrics, traces, logs, alerts, and artifacts for every run and incident.
- Retain test-environment telemetry and artifacts for one day, with explicit retention configuration.

## Operational requirements

- Use PostgreSQL as the initial durable source of truth and task-claiming mechanism. Do not add SQS, Redis, Kafka, or a workflow engine without a demonstrated limitation.
- Deploy three application roles: API, orchestrator, and workers. Keep job management, inventory, and recovery as modules until an independently deployable boundary is justified.
- Keep the simulator independent from the orchestrator. It owns target evidence; the orchestrator decides how to interpret and recover from it.
- Correlate telemetry with `job_id`, `workflow_run_id`, `platform_id`, `boot_session_id`, `stage_execution_id`, `test_id`, `attempt_id`, and `trace_id`. Keep unbounded identifiers in logs and traces, not Prometheus labels.
- Define SLOs and actionable alerts before conducting traffic or fault tests.
- Every deliberate incident produces a runbook entry or postmortem containing symptoms, evidence, diagnosis, mitigation, recovery outcome, and prevention.

## Local-to-AWS mapping

| Local implementation | Optional AWS implementation |
| --- | --- |
| Kind control and target clusters | EKS deployment topology chosen for the exercise |
| PostgreSQL container or StatefulSet | Private RDS PostgreSQL |
| Local filesystem or MinIO artifact adapter | Private S3 bucket with lifecycle policy |
| Local images loaded into Kind | Immutable images in ECR |
| Kubernetes Secrets for local development | Secrets Manager and workload identity where needed |
| Prometheus, Grafana, Alertmanager, OTel, Loki/Tempo | Same in-cluster stack or deliberately selected AWS integrations |
| Local port-forwarding | Restricted EKS/operator access and port-forwarding initially |

The Python domain model must remain portable. Cloud-specific behavior belongs in configuration and adapters, never in the workflow or recovery rules.

## Non-goals for the initial implementation

- Real hardware, BIOS images, EFI execution, Windows/Solaris hosts, or register access.
- Autonomous infrastructure deployment or automatic cloud spend.
- Public ingress, external DNS, and a public load balancer.
- Multi-region recovery, a service mesh, arbitrary user-supplied code, and multiple message brokers.
- Artificial microservice decomposition beyond API, orchestrator, worker, and simulator boundaries.

## Source documents

This document is a concise navigation aid. The authoritative behavioral and architecture specifications remain:

- [System behavior](SYSTEM-BEHAVIOR.md)
- [Architecture and roadmap](ARCHITECTURE-AND-ROADMAP.md)
- [Working standard](working-standard.md)
- [Local-first implementation plan](LOCAL-FIRST-IMPLEMENTATION.md)
- [Simulation environment guide](SIMULATION-ENVIRONMENT.md)
- [Local architecture view](ARCHITECTURE-LOCAL.md)
- [AWS architecture view](ARCHITECTURE-AWS.md)
- [CI/CD pipeline design](CI-CD-PIPELINE.md)
