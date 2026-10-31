"""Validation for the first immutable Linux smoke workflow definition."""

from dataclasses import dataclass
from typing import Any, Mapping

from .errors import DomainValidationError
from .models import PlatformRequirements, ProductCode, RetryPolicy
from .simulator import SimulatorOperation


@dataclass(frozen=True, slots=True)
class WorkflowDefinition:
    name: str
    version: str
    requirements: PlatformRequirements
    retry_policy: RetryPolicy
    steps: tuple[SimulatorOperation, ...]


_LINUX_SMOKE_STEPS = (
    SimulatorOperation.INITIALIZE,
    SimulatorOperation.CONFIGURE_BIOS,
    SimulatorOperation.POWER_ON,
    SimulatorOperation.DISCOVER_DEVICES,
    SimulatorOperation.REACH_EFI,
    SimulatorOperation.EFI_SMOKE,
    SimulatorOperation.BOOT_LINUX,
    SimulatorOperation.LINUX_READINESS,
    SimulatorOperation.LINUX_SMOKE,
)


def parse_linux_smoke_workflow(document: Mapping[str, Any]) -> WorkflowDefinition:
    """Validate the small, allowlisted P2 workflow schema from a parsed YAML/JSON document."""
    try:
        target = document["target"]
        retry = document.get("retry_policy", {})
        product = ProductCode(target["product"])
        requirements = PlatformRequirements(
            product=product,
            supported_os=target["supported_os"],
            required_capabilities=frozenset(target.get("required_capabilities", [])),
            minimum_memory_mib=target.get("minimum_memory_mib", 1),
            minimum_cpu_cores=target.get("minimum_cpu_cores", 1),
            required_devices=frozenset(target.get("required_devices", [])),
            thermal_control_required=target.get("thermal_control_required", False),
        )
        policy = RetryPolicy(
            max_retries=retry.get("max_retries", 3),
            delays_seconds=tuple(retry.get("delays_seconds", (30, 60, 120))),
            attempt_timeout_seconds=retry.get("attempt_timeout_seconds", 30),
        )
        steps = tuple(SimulatorOperation(step) for step in document["steps"])
    except (KeyError, TypeError, ValueError) as error:
        raise DomainValidationError(f"invalid Linux smoke workflow: {error}") from error
    if not document.get("name") or not document.get("version"):
        raise DomainValidationError("workflow name and version are required")
    if steps != _LINUX_SMOKE_STEPS:
        raise DomainValidationError("Feature 001 permits only the canonical Linux smoke step sequence")
    return WorkflowDefinition(document["name"], document["version"], requirements, policy, steps)
