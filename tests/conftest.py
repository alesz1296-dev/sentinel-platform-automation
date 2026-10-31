from uuid import uuid4

import pytest

from sntl.domain.models import Platform, ProductCode


@pytest.fixture
def compatible_platform() -> Platform:
    return Platform(
        id=uuid4(), product=ProductCode.SPR, memory_mib=131_072, cpu_cores=32,
        supported_os=frozenset({"linux"}), capabilities=frozenset({"efi", "thermal-control"}),
        devices=frozenset({"network", "storage"}),
    )
