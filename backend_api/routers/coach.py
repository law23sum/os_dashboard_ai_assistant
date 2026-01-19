"""AI page coach + tutorial surface (Spec §1.7, §4.5, §5.12)."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()


class QuickAction(BaseModel):
    label: str
    description: str
    prompt: str


class CoachProfile(BaseModel):
    route: str
    title: str
    summary: str
    persona: str
    spec_refs: List[str]
    tutorial: List[str]
    recommendations: List[str]
    quick_actions: List[QuickAction]
    signals: List[str] = Field(default_factory=list)


class CoachAskRequest(BaseModel):
    route: str
    question: str


class CoachAskResponse(BaseModel):
    route: str
    persona: str
    response: str
    follow_up: List[str]
    timestamp: str


_COACH_LIBRARY: Dict[str, Dict[str, object]] = {
    "/": {
        "title": "Global Orchestrator Coach",
        "summary": "Preview high-impact automations before you dive in. This coach keeps the AIC persona aligned with mission goals.",
        "persona": "AIC · Control Plane Lead",
        "spec_refs": ["Spec §1.1", "Spec §1.7.4"],
        "tutorial": [
            "Review intent backlog and approve queued plans.",
            "Trigger capsule bundles matching today's objectives.",
            "Log any manual overrides so the ledger stays authoritative.",
        ],
        "recommendations": [
            "Scan ledger deltas before switching workspaces.",
            "Keep the driver fabric hydrated with recent health pings.",
            "Escalate risky intents to Governance plane immediately.",
        ],
        "quick_actions": [
            {
                "label": "Summarize current runbook",
                "description": "Produce a one-liner status for stakeholders.",
                "prompt": "Summarize the current AI OS runbook with major risks.",
            },
            {
                "label": "Highlight stuck tasks",
                "description": "Call out what needs a driver re-route.",
                "prompt": "List the stuck intents that block the mission right now.",
            },
        ],
        "signals": ["Control plane standing orders synced", "Ledger hash verified"],
    },
    "/dashboard": {
        "title": "Mission Dashboard Guide",
        "summary": "Balance persona workload, driver budgets, and audit compliance from a single cockpit.",
        "persona": "Echo · Mission Controller",
        "spec_refs": ["Spec §1.1", "Spec §2.2", "Spec §11.1"],
        "tutorial": [
            "Inspect persona load vs. driver utilization.",
            "Review latest audit evidence and project risk color.",
            "Kick off pre-approved capsules for upcoming shifts.",
        ],
        "recommendations": [
            "Keep CPU/network metrics under thresholds before enabling heavy capsules.",
            "Use search to surface CIR snippets when triaging alerts.",
            "Pin the most volatile personas for closer monitoring.",
        ],
        "quick_actions": [
            {
                "label": "Prep daily briefing",
                "description": "Summarize KPIs + alerts from this dashboard.",
                "prompt": "Draft a briefing using today's dashboard telemetry and alerts.",
            },
            {
                "label": "Suggest persona routing",
                "description": "Optimize persona assignment based on current load.",
                "prompt": "Recommend persona routing adjustments for load balance.",
            },
        ],
        "signals": ["Telemetry feed stable", "Projects sync in progress"],
    },
    "/projects": {
        "title": "Project Intelligence Guide",
        "summary": "Tie CIR, ledger, and TRF reasoning together so projects never drift from the canon.",
        "persona": "Sora · Structure Architect",
        "spec_refs": ["Spec §3.5", "Spec §4.5–§4.8"],
        "tutorial": [
            "Open the ledger stream and confirm new events are hash-linked.",
            "Use TRF insights to update project risk posture.",
            "Push new capsule templates to the shared library when a pattern emerges.",
        ],
        "recommendations": [
            "Promote healthy tasks into capsule drafts once success criteria repeat.",
            "Pair ledger events with Evidence Pack exports weekly.",
            "Invite additional personas when AIC confidence falls below guardrails.",
        ],
        "quick_actions": [
            {
                "label": "Assess project risk",
                "description": "Speed check on overdue tasks + ledger gaps.",
                "prompt": "Assess the highest risk projects and suggest mitigations.",
            },
            {
                "label": "Plan capsule rollout",
                "description": "Draft next capsule release from current data.",
                "prompt": "Propose the next capsule rollout plan using ledger insights.",
            },
        ],
        "signals": ["Ledger hash intact", "TRF heuristics synced"],
    },
    "/ai/autofix": {
        "title": "Auto-Fix Mentor",
        "summary": "Instrument remediation loops so self-healing drivers repair regressions before humans notice.",
        "persona": "Critic · Self-Healing Overseer",
        "spec_refs": ["Spec §5.12", "Spec §8.13", "Spec §11.8"],
        "tutorial": [
            "Check queue depth and prioritize critical severity first.",
            "Adjust confidence threshold if pipelines are noisy.",
            "Log manual approvals to the governance plane.",
        ],
        "recommendations": [
            "Couple every applied fix with a regression test rerun.",
            "Refresh scan targets weekly to cover new directories.",
            "Correlate diagnostic feed with Auto-Fix reports to detect drift.",
        ],
        "quick_actions": [
            {
                "label": "Calibrate threshold",
                "description": "Quick audit of auto-apply accuracy.",
                "prompt": "Review recent auto-fix accuracy and suggest a new threshold if needed.",
            },
            {
                "label": "Draft remediation summary",
                "description": "Generate a status blurb for stakeholders.",
                "prompt": "Summarize today's auto-fix activity with notable wins and remaining work.",
            },
        ],
        "signals": ["Self-healing active", "Governance approvals current"],
    },
    "/ai/capsules": {
        "title": "Capsule Marketplace Guide",
        "summary": "Curate capsule packs, validate manifests, and align installs with governance policy.",
        "persona": "Archivist · Capsule Steward",
        "spec_refs": ["Spec §8.1–§8.7", "Spec §8.20"],
        "tutorial": [
            "Review blueprint coverage vs. workspace demand.",
            "Run validation hooks before deploying a pack.",
            "Publish install/update notices to the ledger.",
        ],
        "recommendations": [
            "Bundle capsules into policy-tiered blueprints for faster onboarding.",
            "Watch driver manifests for deprecations and push updates proactively.",
            "Tag capsules with residency metadata for regulator queries.",
        ],
        "quick_actions": [
            {
                "label": "Score blueprint fit",
                "description": "Match a blueprint to current workspace goals.",
                "prompt": "Evaluate which blueprint best accelerates the current workspace focus.",
            },
            {
                "label": "Outline validation steps",
                "description": "Checklist for deploying a capsule safely.",
                "prompt": "List validation steps before deploying the selected capsule pack.",
            },
        ],
        "signals": ["Marketplace synced", "Policy tiers enforced"],
    },
    "/work/writer": {
        "title": "Writer Workspace Coach",
        "summary": "Pair lore canon with AI drafting so narratives stay on mission and consistent across teams.",
        "persona": "Aria · Narrative Strategist",
        "spec_refs": ["Spec §7.5", "Spec §7.12.4"],
        "tutorial": [
            "Select the doc template that matches the narrative arc.",
            "Co-edit with AI suggestions and capture final prompts in the ledger.",
            "Publish drafts to the canonical canon store with metadata tags.",
        ],
        "recommendations": [
            "Leverage persona voice switching for multi POV documents.",
            "Monitor word count vs. spec-defined guidance for deliverable types.",
            "Link drafts to Evidence Packs when work feeds regulated releases.",
        ],
        "quick_actions": [
            {
                "label": "Improve tone",
                "description": "Align writing voice with the reader persona.",
                "prompt": "Suggest tone adjustments for the active writer document.",
            },
            {
                "label": "Outline next section",
                "description": "Keep drafts flowing with clear headings.",
                "prompt": "Propose the next section outline for the current writer draft.",
            },
        ],
        "signals": ["Canon sync enabled", "Persona tone locked"],
    },
    "default": {
        "title": "Workspace Guide",
        "summary": "AI copilots stay on standby with quick tutorials and relevant recommendations for every workspace.",
        "persona": "AIC · Default Copilot",
        "spec_refs": ["Spec §1.7.2", "Spec §7.1"],
        "tutorial": [
            "Glance at the spec references for this surface.",
            "Check recommended actions and align with mission goals.",
            "Use quick actions to run automation-ready prompts.",
        ],
        "recommendations": [
            "Keep personas in sync with workspace mode switches.",
            "Let the AI capture context snippets for Evidence Packs.",
            "Escalate to governance if operations touch regulated assets.",
        ],
        "quick_actions": [
            {
                "label": "Share quick summary",
                "description": "High-level status note for your teammates.",
                "prompt": "Summarize what this workspace enables and current focus areas.",
            }
        ],
        "signals": ["Spec references loaded"],
    },
}


def _normalize_route(route: Optional[str]) -> str:
    if not route:
        return "/"
    path = route.strip() or "/"
    if not path.startswith("/"):
        path = f"/{path}"
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")
    return path or "/"


def _resolve_profile(route: str) -> Dict[str, object]:
    normalized = _normalize_route(route).lower()
    if normalized in _COACH_LIBRARY:
        return _COACH_LIBRARY[normalized]
    parts = [segment for segment in normalized.split("/") if segment]
    candidates: List[str] = []
    for length in range(len(parts), 0, -1):
        candidate = "/" + "/".join(parts[:length])
        candidates.append(candidate)
    candidates.append("/")
    candidates.append("default")
    for candidate in candidates:
        if candidate in _COACH_LIBRARY:
            return _COACH_LIBRARY[candidate]
    return _COACH_LIBRARY["default"]


@router.get("/coach", response_model=CoachProfile)
async def get_page_coach(route: str = Query("/", description="Current SPA route")) -> CoachProfile:
    profile_data = _resolve_profile(route)
    return CoachProfile(
        route=_normalize_route(route),
        title=profile_data["title"],
        summary=profile_data["summary"],
        persona=profile_data["persona"],
        spec_refs=list(profile_data["spec_refs"]),
        tutorial=list(profile_data["tutorial"]),
        recommendations=list(profile_data["recommendations"]),
        quick_actions=[QuickAction(**item) for item in profile_data["quick_actions"]],
        signals=list(profile_data.get("signals", [])),
    )


@router.post("/coach/ask", response_model=CoachAskResponse)
async def ask_page_coach(payload: CoachAskRequest) -> CoachAskResponse:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    profile_data = _resolve_profile(payload.route)
    persona = profile_data["persona"]
    recommendations = list(profile_data["recommendations"])
    spec_refs = ", ".join(profile_data["spec_refs"])
    response = (
        f"{persona} reviewed your request: “{question}”. "
        f"Focus on spec anchors {spec_refs} and pair the next action with a ledger note. "
        f"Suggested next move: {recommendations[0] if recommendations else 'continue monitoring telemetry'}."
    )
    follow_up = recommendations[1:3] if len(recommendations) > 1 else ["Capture outcome in Evidence Pack before proceeding."]
    return CoachAskResponse(
        route=_normalize_route(payload.route),
        persona=persona,
        response=response,
        follow_up=follow_up,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )
