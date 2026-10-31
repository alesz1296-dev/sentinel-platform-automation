"""Stable value objects for the first SNTL workflow slice."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import FrozenSet
from uuid import UUID

from .errors import DomainValidationError


class ProductCode(StrEnum):
    ICX = "ICX"
    SPR = "SPR"
    DMR = "DMR"
    EMR = "EMR"
    SRF = "SRF"


class PlatformLifecycleState(StrEnum):
    OFF = "OFF"
    INITIALIZED = "INITIALIZED"
    BIOS_CONFIGURED = "BIOS_CONFIGURED"
    POWERED_ON = "POWERED_ON"
    DEVICES_DISCOVERED = "DEVICES_DISCOVERED"
    EFI_READY = "EFI_READY"
    OS_BOOTING = "OS_BOOTING"
    OS_READY = "OS_READY"
    RECOVERING = "RECOVERING"
    QUARANTINED = "QUARANTINED"


class PlatformHealth(StrEnum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    DEGRADED = "DEGRADED"
    UNREACHABLE = "UNREACHABLE"
    FROZEN = "FROZEN"
    RECOVERING = "RECOVERING"
    QUARANTINED = "QUARANTINED"


class AttemptOutcome(StrEnum):
    SUCCEEDED = "SUCCEEDED"
    ASSERTION_FAILED = "ASSERTION_FAILED"
    RETRYABLE_FAILURE = "RETRYABLE_FAILURE"
    TIMED_OUT = "TIMED_OUT"
    CANCELED = "CANCELED"
    UNKNOWN = "UNKNOWN"
    STALE_FENCED = "STALE_FENCED"


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_retries: int = 3
    delays_seconds: tuple[int, ...] = (30, 60, 120)
    attempt_timeout_seconds: int = 30

    def __post_init__(self) -> None:
        if not 0 <= self.max_retries <= 5:
            raise DomainValidationError("max_retries must be between 0 and 5")
        if len(self.delays_seconds) != self.max_retries:
            raise DomainValidationError("delays_seconds must contain one delay per retry")
        if any(delay < 0 or delay > 600 for delay in self.delays_seconds):
            raise DomainValidationError("each retry delay must be between 0 and 600 seconds")
        if not 1 <= self.attempt_timeout_seconds <= 600:
            raise DomainValidationError("attempt_timeout_seconds must be between 1 and 600")


@dataclass(frozen=True, slots=True)
class PlatformRequirements:
    product: ProductCode
    supported_os: str
    required_capabilities: FrozenSet[str] = frozenset()
    minimum_memory_mib: int = 1
    minimum_cpu_cores: int = 1
    required_devices: FrozenSet[str] = frozenset()
    thermal_control_required: bool = False

    def __post_init__(self) -> None:
        if self.supported_os != "linux":
            raise DomainValidationError("Feature 001 supports only linux")
        if self.minimum_memory_mib < 1 or self.minimum_cpu_cores < 1:
            raise DomainValidationError("minimum resources must be positive")

    @property
    def normalized_capabilities(self) -> FrozenSet[str]:
        return self.required_capabilities | (
            frozenset({"thermal-control"}) if self.thermal_control_required else frozenset()
        )


@dataclass(slots=True)
class Platform:
    id: UUID
    product: ProductCode
    memory_mib: int
    cpu_cores: int
    supported_os: FrozenSet[str]
    capabilities: FrozenSet[str]
    devices: FrozenSet[str]
    lifecycle_state: PlatformLifecycleState = PlatformLifecycleState.OFF
    observed_os: str | None = None
    health: PlatformHealth = PlatformHealth.AVAILABLE
    boot_session: int = 0
    active_fencing_token: int = 0
    operation_history: list[UUID] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.memory_mib < 1 or self.cpu_cores < 1:
            raise DomainValidationError("platform resources must be positive")
