import asyncio
from typing import Any, Dict, List

import pytest

from assistant_core.driver_architecture import (
    CapabilityDispatchDriver,
    DriverCapability,
    DriverCategory,
    DriverExecutionRequest,
    DriverManifest,
    DriverScheduler,
    ExecutionPriority,
)


class _DummyDriver(CapabilityDispatchDriver):
    def __init__(self) -> None:
        manifest = DriverManifest(
            name="dummy",
            version="0.0.1",
            category=DriverCategory.SOFTWARE_SAAS,
            description="test driver",
            capabilities=[
                DriverCapability("add", "add numbers"),
                DriverCapability("echo", "echo value"),
            ],
        )
        super().__init__(manifest)

    async def initialize(self) -> bool:
        return True

    async def cleanup(self) -> None:
        return None

    def _capability_handlers(self):
        return {
            "add": self._handle_add,
            "echo": self._handle_echo,
        }

    def _handle_add(self, params: Dict[str, Any], _: Dict[str, Any]) -> int:
        return sum(params.get("values", []))

    async def _handle_echo(self, params: Dict[str, Any], _: Dict[str, Any]) -> Any:
        await asyncio.sleep(0)
        return params.get("value")


class _RecordingDriver(CapabilityDispatchDriver):
    def __init__(self, sink: List[Any]) -> None:
        self.sink = sink
        manifest = DriverManifest(
            name="recorder",
            version="0.0.1",
            category=DriverCategory.SOFTWARE_SAAS,
            description="records calls",
            capabilities=[DriverCapability("record", "record values")],
        )
        super().__init__(manifest)

    async def initialize(self) -> bool:
        return True

    async def cleanup(self) -> None:
        return None

    def _capability_handlers(self):
        return {"record": self._handle_record}

    async def _handle_record(self, params: Dict[str, Any], _: Dict[str, Any]) -> Dict[str, Any]:
        self.sink.append(params.get("value"))
        return {"recorded": params.get("value")}


@pytest.mark.asyncio
async def test_capability_dispatch_driver_routes_sync_and_async_handlers():
    driver = _DummyDriver()
    await driver.start()

    add_result = await driver.execute("add", {"values": [1, 2, 3]})
    echo_result = await driver.execute("echo", {"value": "hi"})

    assert add_result == 6
    assert echo_result == "hi"
    assert driver.last_execution is not None


@pytest.mark.asyncio
async def test_driver_scheduler_respects_priority_ordering():
    sink: List[Any] = []
    driver = _RecordingDriver(sink)
    await driver.start()

    scheduler = DriverScheduler(max_concurrent_executions=1)
    scheduler.register_driver(driver)
    await scheduler.start_scheduler()

    high_req = DriverExecutionRequest(
        driver_id=driver.id, capability="record", parameters={"value": "high"}, priority=ExecutionPriority.HIGH
    )
    low_req = DriverExecutionRequest(
        driver_id=driver.id, capability="record", parameters={"value": "low"}, priority=ExecutionPriority.LOW
    )

    await scheduler.submit_request(high_req)
    await scheduler.submit_request(low_req)

    for _ in range(20):
        if len(sink) >= 2:
            break
        await asyncio.sleep(0.05)
    await scheduler.stop_scheduler()

    assert sink[0] == "high"
    assert sink[1] == "low"


@pytest.mark.asyncio
async def test_driver_scheduler_is_stable_with_same_priority():
    sink: List[Any] = []
    driver = _RecordingDriver(sink)
    await driver.start()

    scheduler = DriverScheduler(max_concurrent_executions=1)
    scheduler.register_driver(driver)
    await scheduler.start_scheduler()

    first = DriverExecutionRequest(
        driver_id=driver.id, capability="record", parameters={"value": "first"}, priority=ExecutionPriority.NORMAL
    )
    second = DriverExecutionRequest(
        driver_id=driver.id, capability="record", parameters={"value": "second"}, priority=ExecutionPriority.NORMAL
    )

    await scheduler.submit_request(first)
    await scheduler.submit_request(second)

    for _ in range(20):
        if len(sink) >= 2:
            break
        await asyncio.sleep(0.05)
    await scheduler.stop_scheduler()

    assert sink == ["first", "second"]
