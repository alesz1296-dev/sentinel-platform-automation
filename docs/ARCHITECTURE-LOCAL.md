# SNTL local simulation architecture

This is the daily development and operations environment. Kind hosts the SNTL
control plane and a separate Kind cluster hosts simulated targets once failure
isolation exercises begin.

```mermaid
flowchart TB
    Operator[Operator CLI or API client]
    Load[k6 traffic and incident tests]
    GitHub[GitHub Actions]
    GitOps[Git-tracked desired state]

    subgraph Local[Local simulation environment]
        subgraph Control[Kind control cluster]
            API[FastAPI API]
            Orchestrator[Scheduler and recovery controller]
            Workers[Execution workers]
            DB[(PostgreSQL)]
            Artifacts[Local artifact store]
            Argo[Argo CD and Argo Rollouts]
            OTel[OpenTelemetry Collector]
            Prometheus[Prometheus]
            Grafana[Grafana]
            Alertmanager[Alertmanager]
            Loki[Loki]
            Tempo[Tempo]
        end

        subgraph Target[Kind simulated target cluster]
            Simulator[Platform simulator]
            TargetState[Heartbeat, boot session, and lifecycle evidence]
        end
    end

    Operator --> API
    Load --> API
    API --> DB
    API --> Orchestrator
    Orchestrator --> DB
    Orchestrator --> Workers
    Workers --> DB
    Workers --> Artifacts
    Workers --> Simulator
    Simulator --> TargetState
    TargetState --> Workers
    API --> OTel
    Orchestrator --> OTel
    Workers --> OTel
    OTel --> Loki
    OTel --> Tempo
    API --> Prometheus
    Orchestrator --> Prometheus
    Workers --> Prometheus
    Prometheus --> Grafana
    Prometheus --> Alertmanager
    GitHub --> GitOps
    GitOps --> Argo
    Argo --> API
    Argo --> Orchestrator
    Argo --> Workers
```

The target cluster may experience freezes, reboots, network failures, or node
loss while the control cluster remains available for scheduling, recovery, and
investigation.
