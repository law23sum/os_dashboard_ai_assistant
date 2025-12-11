from assistant_hub.research_workspace import ResearchWorkspaceState


def test_start_simulation_tracks_new_experiment():
    state = ResearchWorkspaceState()
    baseline = len(state.snapshot()["experiments"])
    result = state.start_simulation("monte_carlo", "financial_risk", 250)

    assert result["simulation_type"] == "monte_carlo"
    snapshot = state.snapshot()
    assert len(snapshot["experiments"]) == baseline + 1
    assert snapshot["experiments"][0]["total"] == 250


def test_design_experiment_updates_workspace():
    state = ResearchWorkspaceState()
    design = state.design_experiment("parameter_sweep", ["volatility", "drift_rate"])

    assert design["type"] == "parameter_sweep"
    workspace = state.snapshot()
    assert workspace["last_design"]["id"] == design["id"]
    assert workspace["last_design"]["variables"] == ["volatility", "drift_rate"]
