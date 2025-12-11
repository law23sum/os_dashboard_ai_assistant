"""Research workspace API router."""
from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict
from typing import List

from assistant_hub.research_workspace import ResearchWorkspaceState

router = APIRouter()

_STATE = ResearchWorkspaceState()


class ResearchBase(BaseModel):
    """Allow fields like model_id without protected namespace warnings."""

    model_config = ConfigDict(protected_namespaces=())


class RunSimulationRequest(ResearchBase):
    sim_type: str = "monte_carlo"
    model_id: str = "financial_risk"
    iterations: int = 1000


class DesignExperimentRequest(ResearchBase):
    design_type: str = "parameter_sweep"
    variables: List[str]


@router.get("/snapshot")
async def get_research_snapshot():
    """Return the latest research workspace snapshot."""
    return _STATE.snapshot()


@router.post("/run")
async def run_simulation(request: RunSimulationRequest):
    """Start a new simulation run."""
    return _STATE.start_simulation(request.sim_type, request.model_id, request.iterations)


@router.post("/design")
async def design_experiment(request: DesignExperimentRequest):
    """Create a parameter sweep / experiment design record."""
    return _STATE.design_experiment(request.design_type, request.variables)
