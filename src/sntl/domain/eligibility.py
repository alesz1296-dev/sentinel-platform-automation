"""Platform-admission rules."""

from dataclasses import dataclass

from .models import Platform, PlatformHealth, PlatformRequirements


@dataclass(frozen=True, slots=True)
class EligibilityResult:
    eligible: bool
    reasons: tuple[str, ...]


def evaluate_eligibility(platform: Platform, requirements: PlatformRequirements) -> EligibilityResult:
    reasons: list[str] = []
    if platform.product != requirements.product:
        reasons.append(f"product requires {requirements.product}, found {platform.product}")
    if requirements.supported_os not in platform.supported_os:
        reasons.append(f"platform does not support required OS {requirements.supported_os}")
    if platform.memory_mib < requirements.minimum_memory_mib:
        reasons.append(f"minimum memory is {requirements.minimum_memory_mib} MiB, found {platform.memory_mib} MiB")
    if platform.cpu_cores < requirements.minimum_cpu_cores:
        reasons.append(f"minimum CPU cores is {requirements.minimum_cpu_cores}, found {platform.cpu_cores}")
    missing_capabilities = requirements.normalized_capabilities - platform.capabilities
    if missing_capabilities:
        reasons.append(f"missing capabilities: {', '.join(sorted(missing_capabilities))}")
    missing_devices = requirements.required_devices - platform.devices
    if missing_devices:
        reasons.append(f"missing devices: {', '.join(sorted(missing_devices))}")
    if platform.health is not PlatformHealth.AVAILABLE:
        reasons.append(f"platform health is {platform.health}")
    return EligibilityResult(not reasons, tuple(reasons))
