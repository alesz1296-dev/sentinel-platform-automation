from uuid import uuid4

import pytest

from sntl.domain.eligibility import evaluate_eligibility
from sntl.domain.errors import DomainValidationError, InvalidTransitionError, StaleFencingTokenError
from sntl.domain.models import AttemptOutcome, PlatformLifecycleState, PlatformRequirements, ProductCode, RetryPolicy
from sntl.domain.simulator import DeterministicSimulator, FaultKind, SimulatorOperation
from sntl.domain.workflow import parse_linux_smoke_workflow


def test_matching_platform_is_eligible(compatible_platform):
    requirements = PlatformRequirements(product=ProductCode.SPR, supported_os="linux", required_capabilities=frozenset({"efi"}), minimum_memory_mib=65_536, minimum_cpu_cores=16, required_devices=frozenset({"network"}), thermal_control_required=True)
    assert evaluate_eligibility(compatible_platform, requirements).eligible


def test_product_resource_and_thermal_mismatch_are_reported(compatible_platform):
    compatible_platform.memory_mib = 8_192
    compatible_platform.capabilities = frozenset({"efi"})
    result = evaluate_eligibility(compatible_platform, PlatformRequirements(product=ProductCode.ICX, supported_os="linux", minimum_memory_mib=16_384, thermal_control_required=True))
    assert not result.eligible
    assert "product requires ICX, found SPR" in result.reasons
    assert "minimum memory is 16384 MiB, found 8192 MiB" in result.reasons
    assert "missing capabilities: thermal-control" in result.reasons


def test_retry_policy_contract():
    assert RetryPolicy().delays_seconds == (30, 60, 120)
    with pytest.raises(DomainValidationError):
        RetryPolicy(max_retries=6, delays_seconds=(1, 2, 3, 4, 5, 6))
    with pytest.raises(DomainValidationError):
        RetryPolicy(max_retries=2, delays_seconds=(30,))
    with pytest.raises(DomainValidationError):
        RetryPolicy(max_retries=0, delays_seconds=(), attempt_timeout_seconds=601)


def test_lifecycle_and_replayed_operation_are_deterministic(compatible_platform):
    simulator = DeterministicSimulator(compatible_platform)
    simulator.set_active_fencing_token(1)
    operations = (SimulatorOperation.INITIALIZE, SimulatorOperation.CONFIGURE_BIOS, SimulatorOperation.POWER_ON, SimulatorOperation.DISCOVER_DEVICES, SimulatorOperation.REACH_EFI, SimulatorOperation.EFI_SMOKE, SimulatorOperation.BOOT_LINUX, SimulatorOperation.LINUX_READINESS, SimulatorOperation.LINUX_SMOKE)
    results = [simulator.execute(operation, uuid4(), 1) for operation in operations]
    assert all(result.outcome is AttemptOutcome.SUCCEEDED for result in results)
    assert compatible_platform.lifecycle_state is PlatformLifecycleState.OS_READY
    assert compatible_platform.observed_os == "linux"
    operation_id = uuid4()
    first = simulator.execute(SimulatorOperation.LINUX_SMOKE, operation_id, 1)
    assert simulator.execute(SimulatorOperation.LINUX_SMOKE, operation_id, 1) == first


def test_out_of_order_and_stale_workers_are_rejected(compatible_platform):
    simulator = DeterministicSimulator(compatible_platform)
    simulator.set_active_fencing_token(1)
    with pytest.raises(InvalidTransitionError):
        simulator.execute(SimulatorOperation.LINUX_SMOKE, uuid4(), 1)
    simulator.set_active_fencing_token(2)
    with pytest.raises(StaleFencingTokenError):
        simulator.execute(SimulatorOperation.INITIALIZE, uuid4(), 1)


def test_retryable_fault_does_not_advance_state(compatible_platform):
    simulator = DeterministicSimulator(compatible_platform, {SimulatorOperation.INITIALIZE: (FaultKind.RETRYABLE_FAILURE,)})
    simulator.set_active_fencing_token(1)
    failed = simulator.execute(SimulatorOperation.INITIALIZE, uuid4(), 1)
    assert failed.outcome is AttemptOutcome.RETRYABLE_FAILURE
    assert compatible_platform.lifecycle_state is PlatformLifecycleState.OFF
    assert simulator.execute(SimulatorOperation.INITIALIZE, uuid4(), 1).outcome is AttemptOutcome.SUCCEEDED


def test_workflow_parser_allows_only_the_reviewed_linux_sequence():
    document = {
        "name": "linux-smoke", "version": "1", "target": {"product": "SPR", "supported_os": "linux", "minimum_memory_mib": 65536},
        "steps": [operation.value for operation in (SimulatorOperation.INITIALIZE, SimulatorOperation.CONFIGURE_BIOS, SimulatorOperation.POWER_ON, SimulatorOperation.DISCOVER_DEVICES, SimulatorOperation.REACH_EFI, SimulatorOperation.EFI_SMOKE, SimulatorOperation.BOOT_LINUX, SimulatorOperation.LINUX_READINESS, SimulatorOperation.LINUX_SMOKE)],
    }
    assert parse_linux_smoke_workflow(document).requirements.product is ProductCode.SPR
    document["steps"] = document["steps"][:-1]
    with pytest.raises(DomainValidationError):
        parse_linux_smoke_workflow(document)
