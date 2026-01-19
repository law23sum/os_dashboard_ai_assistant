"""API smoke tests for Intelligence Project Management routes."""


def test_ipm_projects_list(sync_client):
    response = sync_client.get("/api/ipm/projects", params={"scope": "personal"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_pms_projects_deprecated(sync_client):
    response = sync_client.get("/api/pms/projects", params={"scope": "personal"})
    assert response.status_code == 200
    assert response.headers.get("Deprecation") == "true"
    warning = response.headers.get("Warning", "")
    assert "Deprecated API" in warning
