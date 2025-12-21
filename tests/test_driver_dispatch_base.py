import pytest
from datetime import timedelta

from assistant_core.driver_orchestrator_architecture import (
    ActionDispatchDriver,
    ActionSchema,
    DriverManifest,
    ExecutionPlanner,
    Intent,
    TaskDecomposition,
    TaskStep,
)


class _DummyDriver(ActionDispatchDriver):
    def __init__(self) -> None:
        manifest = DriverManifest(
            name="dummy",
            version="0.0.1",
            vendor="test",
            trust_level="test",
            actions={
                "ping": ActionSchema(
                    name="ping",
                    input_schema={},
                    output_schema={},
                    description="ping",
                ),
                "sum": ActionSchema(
                    name="sum",
                    input_schema={},
                    output_schema={},
                    description="sum",
                ),
            },
            side_effects=[],
            rate_limits={},
            cost_model={},
            latency_profile={},
            security_class="public",
            preconditions=[],
            postconditions=[],
        )
        super().__init__(manifest)

    def _action_handlers(self):
        return {
            "ping": self._ping,
            "sum": self._sum,
        }

    async def _ping(self, params):
        return {"ok": params.get("value", "pong")}

    def _sum(self, params):
        return sum(params.get("values", []))


class _StubRegistry:
    def __init__(self, names):
        self._names = names

    async def discover_drivers_for_task(self, *_args, **_kwargs):
        return list(self._names)


class _StubConstraintSolver:
    def __init__(self, scores):
        self._scores = scores

    async def score_driver_option(self, driver_name, *_args, **_kwargs):
        return self._scores[driver_name]


@pytest.mark.asyncio
async def test_action_dispatch_driver_routes_to_handlers():
    driver = _DummyDriver()
    ping_result = await driver.execute_action("ping", {"value": "hello"})
    sum_result = await driver.execute_action("sum", {"values": [1, 2, 3]})

    assert ping_result == {"ok": "hello"}
    assert sum_result == 6

    with pytest.raises(ValueError):
        await driver.execute_action("unknown", {})


@pytest.mark.asyncio
async def test_execution_planner_selects_best_scored_driver():
    registry = _StubRegistry(["fast", "slow"])
    planner = ExecutionPlanner(registry)
    planner.constraint_solver = _StubConstraintSolver({"fast": 10.0, "slow": 1.0})

    task_step = TaskStep(
        id="step1",
        description="do something",
        required_capabilities=[],
        input_requirements={},
        output_expectations={},
        risk_level="low",
    )
    decomposition = TaskDecomposition(
        intent_id="intent",
        steps=[task_step],
        dependencies={"step1": []},
        estimated_duration=timedelta(seconds=1),
        confidence_score=1.0,
    )
    intent = Intent(id="intent", source="test", content="demo", user_id="", tenant_id="")

    plan = await planner.create_execution_plan(decomposition, intent)

    assert plan.steps[0].driver_name == "fast"


@pytest.mark.asyncio
async def test_execution_planner_respects_dependencies_topology():
    registry = _StubRegistry(["driver"])
    planner = ExecutionPlanner(registry)
    planner.constraint_solver = _StubConstraintSolver({"driver": 1.0})

    step_a = TaskStep(
        id="A",
        description="first",
        required_capabilities=[],
        input_requirements={},
        output_expectations={},
        risk_level="low",
    )
    step_b = TaskStep(
        id="B",
        description="second",
        required_capabilities=[],
        input_requirements={},
        output_expectations={},
        risk_level="low",
    )
    decomposition = TaskDecomposition(
        intent_id="intent",
        steps=[step_a, step_b],
        dependencies={"A": [], "B": ["A"]},
        estimated_duration=timedelta(seconds=2),
        confidence_score=1.0,
    )
    intent = Intent(id="intent", source="test", content="demo", user_id="", tenant_id="")

    plan = await planner.create_execution_plan(decomposition, intent)

    assert [step.id for step in plan.steps] == ["exec_A", "exec_B"]


@pytest.mark.asyncio
async def test_execution_planner_raises_on_dependency_cycle():
    registry = _StubRegistry(["driver"])
    planner = ExecutionPlanner(registry)
    planner.constraint_solver = _StubConstraintSolver({"driver": 1.0})

    step_a = TaskStep(
        id="A",
        description="first",
        required_capabilities=[],
        input_requirements={},
        output_expectations={},
        risk_level="low",
    )
    step_b = TaskStep(
        id="B",
        description="second",
        required_capabilities=[],
        input_requirements={},
        output_expectations={},
        risk_level="low",
    )
    decomposition = TaskDecomposition(
        intent_id="intent",
        steps=[step_a, step_b],
        dependencies={"A": ["B"], "B": ["A"]},
        estimated_duration=timedelta(seconds=2),
        confidence_score=1.0,
    )
    intent = Intent(id="intent", source="test", content="demo", user_id="", tenant_id="")

    with pytest.raises(ValueError):
        await planner.create_execution_plan(decomposition, intent)
