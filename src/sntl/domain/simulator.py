"""Deterministic, fenced lifecycle simulator."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping
from uuid import UUID

from .errors import InvalidTransitionError, StaleFencingTokenError
from .models import AttemptOutcome, Platform, PlatformLifecycleState


class SimulatorOperation(StrEnum):
    INITIALIZE = "initialize"
    CONFIGURE_BIOS = "configure_bios"
    POWER_ON = "power_on"
    DISCOVER_DEVICES = "discover_devices"
    REACH_EFI = "reach_efi"
    EFI_SMOKE = "efi_smoke"
    BOOT_LINUX = "boot_linux"
    LINUX_READINESS = "linux_readiness"
    LINUX_SMOKE = "linux_smoke"


class FaultKind(StrEnum):
    RETRYABLE_FAILURE = "retryable_failure"
    ASSERTION_FAILED = "assertion_failed"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class OperationResult:
    operation_id: UUID
    operation: SimulatorOperation
    outcome: AttemptOutcome
    lifecycle_state: PlatformLifecycleState
    evidence: tuple[str, ...]


_TRANSITIONS: dict[SimulatorOperation, tuple[PlatformLifecycleState, PlatformLifecycleState]] = {
    SimulatorOperation.INITIALIZE: (PlatformLifecycleState.OFF, PlatformLifecycleState.INITIALIZED),
    SimulatorOperation.CONFIGURE_BIOS: (PlatformLifecycleState.INITIALIZED, PlatformLifecycleState.BIOS_CONFIGURED),
    SimulatorOperation.POWER_ON: (PlatformLifecycleState.BIOS_CONFIGURED, PlatformLifecycleState.POWERED_ON),
    SimulatorOperation.DISCOVER_DEVICES: (PlatformLifecycleState.POWERED_ON, PlatformLifecycleState.DEVICES_DISCOVERED),
    SimulatorOperation.REACH_EFI: (PlatformLifecycleState.DEVICES_DISCOVERED, PlatformLifecycleState.EFI_READY),
    SimulatorOperation.EFI_SMOKE: (PlatformLifecycleState.EFI_READY, PlatformLifecycleState.EFI_READY),
    SimulatorOperation.BOOT_LINUX: (PlatformLifecycleState.EFI_READY, PlatformLifecycleState.OS_BOOTING),
    SimulatorOperation.LINUX_READINESS: (PlatformLifecycleState.OS_BOOTING, PlatformLifecycleState.OS_READY),
    SimulatorOperation.LINUX_SMOKE: (PlatformLifecycleState.OS_READY, PlatformLifecycleState.OS_READY),
}


class DeterministicSimulator:
    def __init__(self, platform: Platform, fault_plan: Mapping[SimulatorOperation, tuple[FaultKind, ...]] | None = None) -> None:
        self.platform = platform
        self._faults = {operation: list(faults) for operation, faults in (fault_plan or {}).items()}
        self._completed: dict[UUID, OperationResult] = {}

    def set_active_fencing_token(self, token: int) -> None:
        if token <= self.platform.active_fencing_token:
            raise StaleFencingTokenError("fencing token must increase")
        self.platform.active_fencing_token = token

    def execute(self, operation: SimulatorOperation, operation_id: UUID, fencing_token: int) -> OperationResult:
        if fencing_token != self.platform.active_fencing_token:
            raise StaleFencingTokenError("operation was submitted by an obsolete owner")
        if operation_id in self._completed:
            return self._completed[operation_id]
        required, target = _TRANSITIONS[operation]
        if self.platform.lifecycle_state is not required:
            raise InvalidTransitionError(f"{operation} requires {required}, found {self.platform.lifecycle_state}")
        fault = self._next_fault(operation)
        if fault:
            outcome = {
                FaultKind.RETRYABLE_FAILURE: AttemptOutcome.RETRYABLE_FAILURE,
                FaultKind.ASSERTION_FAILED: AttemptOutcome.ASSERTION_FAILED,
                FaultKind.UNKNOWN: AttemptOutcome.UNKNOWN,
            }[fault]
            return OperationResult(operation_id, operation, outcome, self.platform.lifecycle_state, (f"simulator:{operation}:{fault}",))
        self.platform.lifecycle_state = target
        if target is PlatformLifecycleState.POWERED_ON:
            self.platform.boot_session += 1
        if target is PlatformLifecycleState.OS_READY:
            self.platform.observed_os = "linux"
        result = OperationResult(operation_id, operation, AttemptOutcome.SUCCEEDED, target, (f"simulator:{operation}:succeeded",))
        self.platform.operation_history.append(operation_id)
        self._completed[operation_id] = result
        return result

    def _next_fault(self, operation: SimulatorOperation) -> FaultKind | None:
        faults = self._faults.get(operation)
        return faults.pop(0) if faults else None
