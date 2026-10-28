# SNTL optional AWS architecture

This is the cloud-validation target. It reuses the same SNTL service contracts
as the local platform while replacing local data and artifact adapters with
managed AWS services. It is designed in Terraform and remains unapplied during
normal local development.

```mermaid
flowchart TB
    Users[CLI, API clients, operators] --> API[FastAPI API]
    IAM[AWS IAM and workload identity] -. authorizes .-> API

    subgraph EKS[Optional AWS validation: EKS workload cluster]
        API --> Inventory[Platform inventory module]
        API --> Jobs[Job and workflow module]
        Jobs --> Orchestrator[Scheduler and orchestrator]
        Orchestrator --> Recovery[Recovery controller module]
        Orchestrator --> Workers[Test and transition workers]
        Workers --> Adapters[Simulated platform adapters]
        API --> OTel[OpenTelemetry Collector]
        Orchestrator --> OTel
        Workers --> OTel
    end

    DB[(RDS PostgreSQL)]
    S3[S3 artifacts]
    Observability[Prometheus, Grafana, Loki, Tempo]
    Alerts[Alertmanager to email or webhook]

    API --> DB
    Inventory --> DB
    Jobs --> DB
    Orchestrator --> DB
    Workers --> DB
    Workers --> S3
    OTel --> Observability
    Observability --> Alerts
```

The initial AWS deployment can use three workloads—API, orchestrator, and
workers—with inventory, job management, and recovery kept as modules. Those
modules may split into services later when independent scaling or failure
isolation justifies it. EKS is the workload platform; the managed EKS control
plane is not where application services execute.

## Local-to-AWS mapping

| Local | AWS target |
| --- | --- |
| Kind control cluster | EKS workload cluster |
| Kind simulated target cluster | Worker-side adapters and selected target environment |
| PostgreSQL | Private RDS PostgreSQL |
| Local filesystem or MinIO | Private S3 bucket |
| Local images or registry | ECR image digests |
| Kubernetes Secrets | Secrets Manager and workload identity where required |
| OTel, Prometheus, Grafana, Loki, Tempo, Alertmanager | Same in-cluster stack or selected AWS integrations |

See [architecture and roadmap](ARCHITECTURE-AND-ROADMAP.md) for the shared
logical boundaries and deployment reconciliation.
