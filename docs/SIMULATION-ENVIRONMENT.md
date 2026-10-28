# SNTL simulation environment guide

## Purpose

SNTL is operated as a production-like local lab. The purpose is to run workflows under realistic traffic and controlled failure, detect degradation from telemetry, diagnose the cause, recover safely, and retain evidence of the outcome.

Daily work runs on Kind. AWS remains a Terraform-defined target architecture used only for intentionally scheduled cloud-validation exercises.

## Local platform

| Concern | Initial implementation | What it exercises |
| --- | --- | --- |
| Kubernetes | Kind | Repeatable clusters and Kubernetes operations |
| Control plane | FastAPI API, orchestrator, workers | Submission, scheduling, durable execution, recovery |
| Target plane | Separate Kind cluster with platform simulators | Failure isolation from control plane |
| Durable state | PostgreSQL | Jobs, leases, attempts, transitions, incidents, audit data |
| Metrics | Prometheus and Grafana | SLOs, resource pressure, queue state, diagnosis |
| Alerts | Alertmanager | Actionable notification and acknowledgement |
| Traces and logs | OpenTelemetry Collector, Tempo, Loki | End-to-end workflow investigation |
| Traffic | k6 | Repeatable API and workflow-submission load |
| Faults | Simulator scenarios, Kubernetes actions, NetworkPolicies | Outage and recovery validation |
| Delivery | GitHub Actions, Helm, Argo CD, Argo Rollouts | Reproducible delivery and rollback |

Start with one Kind cluster for the API and domain-model slice. Add the target cluster before testing node loss, partitions, and failures where SNTL must stay available while a simulated platform fails.

## Environments and promotion

| Environment | Purpose | Deployment rule |
| --- | --- | --- |
| `dev` | Rapid developer verification | Validated development build |
| `staging` | Integration, database, and load tests | Immutable image promoted after CI |
| `production` | Local production simulation | Same digest promoted after approval and acceptance criteria |

Use one Helm chart or Kustomize base with environment values. Promote image digests; do not rebuild images per environment. A production-simulation release needs probes, resource limits, telemetry, and rollback criteria before it receives traffic.

## Traffic model

k6 represents SNTL operators submitting and observing workflows. Use real SNTL API paths rather than generic product endpoints.

```text
authenticate or assume a test identity
  -> submit a Linux workflow
  -> poll the workflow run
  -> retrieve task and evidence summaries
```

| Profile | Shape | What it validates |
| --- | --- | --- |
| Baseline | Low, steady submissions | Normal latency, success rate, queue time |
| Ramp | Gradual virtual-user or arrival-rate increase | Capacity limit and scaling behavior |
| Burst | Brief submission spike | Backpressure, fairness, post-burst recovery |
| Soak | Sustained moderate traffic | Leaks, connection reuse, retention limits |
| Mixed priority | Queue and enforced-priority workflows | Lease transfer, cancellation, checkpoint, fairness |
| Dependency stress | Traffic while PostgreSQL is slow or unavailable | Safe timeout, retry, and user-visible failure behavior |

Each test uses thresholds for whole-test pass/fail conditions and checks for individual response observations. Establish thresholds from a measured baseline.

## Service objectives and alerts

| Signal | Alert condition | First investigation |
| --- | --- | --- |
| API availability | Sustained elevated 5xx/error rate | API dashboard, recent release, traces |
| API responsiveness | p95 latency exceeds its budget | CPU, throttling, database spans, traffic rate |
| Scheduling | Queue age or unclaimed work grows | Worker health, leases, DB connections |
| Platform availability | Heartbeat missing beyond policy | Target state, boot session, network evidence |
| Recovery | Recovery exhaustion or new quarantine | Incident timeline, evidence, recovery policy |
| Delivery | Canary analysis fails | Release metrics, logs, traces, configuration diff |

Every alert has an owner, severity, runbook link, notification route, and a tested firing scenario. Alertmanager sends notifications; SNTL remains the durable record of the incident, evidence, and recovery decision.

## Incident exercises

Document the hypothesis, blast radius, abort condition, expected signals, and cleanup action before starting an experiment.

| Exercise | Controlled cause | Expected evidence and behavior |
| --- | --- | --- |
| Pod crash | Delete API, worker, or simulator pod | Restarts, probes, controller recovery; no duplicate accepted result |
| Worker loss | Delete active worker during an operation | Lease expiry, fencing, and reconciliation |
| OOMKilled | Tighten memory limit while increasing allocation | Event, memory metric, restart, capacity assessment |
| CPU throttling | Tight CPU limit under k6 load | Throttling, higher p95, trace timing, mitigation comparison |
| Database outage | Stop or isolate PostgreSQL temporarily | Bounded retries; durable state intact after restoration |
| Slow database | Inject query delay or constrain connections | Trace identifies DB latency; queue/API impact measured |
| Network failure | Deny egress, add delay/loss, or break DNS | Target unreachable; unsafe dispatch stops; recovery follows policy |
| Target freeze | Simulator stops heartbeat | Evidence retained; bounded recovery or quarantine |
| Unexpected reboot | Simulator changes boot session mid-test | Separate reboot classification; stale readiness revoked |
| Node outage | Stop a target-cluster node | Target failure visible while control plane stays healthy |
| Bad release | Release broken configuration or behavior | Readiness/metrics fail; release halts or rolls back |
| Policy violation | Submit a noncompliant workload | Admission rejection and policy/audit evidence |

Use deterministic simulator scenarios first. Add a chaos framework only when scripts, Kubernetes actions, and NetworkPolicies cannot express a required test.

## Troubleshooting procedure

1. Confirm affected job, API request, environment, start time, and expected result.
2. Check alert state, SLO dashboard, release state, and traffic rate.
3. Follow the request or workflow trace to the slow or failed span.
4. Inspect API, orchestrator, and worker logs using `job_id`, `platform_id`, `attempt_id`, and `boot_session_id`.
5. Check pods, events, probes, limits, restarts, and node pressure.
6. Check PostgreSQL availability, connection saturation, slow operations, and migrations.
7. Check target heartbeats, observed state, lease/fencing state, boot session, and NetworkPolicy or DNS evidence.
8. Preserve evidence before recovery, then rerun the scenario to verify the fix.

CPU and latency alone do not establish a database root cause. Use traces, logs, metrics, and database evidence to distinguish saturation, throttling, backlog, target failure, and traffic-generator limits.

## Incident record

Every serious exercise records the scenario, hypothesis, impact, alert time, linked telemetry and artifacts, root cause, mitigation, recovery time, and preventive follow-up. Rerun the exact scenario after a fix and retain the comparison as portfolio evidence.

## AWS validation boundary

Terraform may model VPC networking, IAM/OIDC, ECR, S3, RDS, EKS, workload identity, logging, and budgets while daily operation remains local. Run formatting, validation, policy checks, and reviewed plans without provisioning.

When cloud validation is justified, scope it to one capability such as ECR access, RDS/S3 adapters, workload identity, private networking, or teardown verification. Provision only what is needed, collect evidence, destroy it, and verify retained cost-bearing resources.
