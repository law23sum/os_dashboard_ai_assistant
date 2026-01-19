"""Shared multi-agent discussion service for terminal + GUI."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from assistant_hub.db import ChatMessage

from .ai import execute_tool_call, generate_ai_reply, normalize_interaction_style
from .ai_registry import AGENT_MODELS, GENERIC_AI_PROVIDERS


CODEX_MODEL = os.getenv("ASSISTANT_HUB_CODEX_MODEL", "gpt-5.1-codex-max")
DEFAULT_MAX_TOOL_ITERS = 10
DEFAULT_MAX_ROUNDS = 3
PERSONAL_BUNDLE = ("AIC", "Sora", "Aria", "Gabriela")


@dataclass(frozen=True)
class AIOption:
    """Selectable AI option for UI/CLI menus."""

    id: int
    key: str
    label: str
    persona: Optional[str]
    provider: str = "openai"
    model: Optional[str] = None
    description: str = ""
    bundle: Optional[Sequence[str]] = None
    auto_route: bool = False
    codex: bool = False
    category: str = "personal"


@dataclass(frozen=True)
class DiscussionMode:
    id: int
    key: str
    label: str
    description: str


@dataclass(frozen=True)
class ResolvedAgent:
    key: str
    persona: str
    label: str
    provider: str
    model: Optional[str] = None


@dataclass
class DiscussionFault:
    reason: str
    message: str
    options: Sequence[str] = ("continue", "revise", "stop")


@dataclass
class DiscussionState:
    mode: str
    prompt: str
    agents: List[ResolvedAgent]
    rounds: List[Dict[str, str]] = field(default_factory=list)
    max_rounds: int = DEFAULT_MAX_ROUNDS


@dataclass
class DiscussionResult:
    messages: List[ChatMessage]
    responses: Dict[str, str]
    fault: Optional[DiscussionFault] = None
    state: Optional[DiscussionState] = None


@dataclass
class AgentRunResult:
    reply: str
    error: Optional[str]
    messages: List[ChatMessage]


AI_MENU: List[AIOption] = [
    AIOption(
        1,
        "AIC",
        "AIC (ChatGPT)",
        persona="AIC",
        description="Execution/operational via ChatGPT",
    ),
    AIOption(
        2,
        "Sora",
        "Sora (ChatGPT)",
        persona="Sora",
        description="Proof/structure via ChatGPT",
    ),
    AIOption(
        3,
        "Aria",
        "Aria (ChatGPT)",
        persona="Aria",
        description="Meaning/canon via ChatGPT",
    ),
    AIOption(
        4,
        "Gabriela",
        "Gabriela (Grok)",
        persona="Gabriela",
        provider="xai",
        model="grok-4",
        description="Commercialization via Grok",
    ),
    AIOption(
        5,
        "ChatGPT",
        "ChatGPT (Coordinator)",
        persona="ChatGPT",
        description="Coordinator/generalist via ChatGPT",
        category="generic",
    ),
    AIOption(
        6,
        "AIC_Codex",
        "AIC (Codex)",
        persona="AIC",
        model=CODEX_MODEL,
        description="AIC via Codex model",
        codex=True,
    ),
    AIOption(
        7,
        "Sora_Codex",
        "Sora (Codex)",
        persona="Sora",
        model=CODEX_MODEL,
        description="Sora via Codex model",
        codex=True,
    ),
    AIOption(
        8,
        "Aria_Codex",
        "Aria (Codex)",
        persona="Aria",
        model=CODEX_MODEL,
        description="Aria via Codex model",
        codex=True,
    ),
    AIOption(
        9,
        "Triad",
        "Personal (All)",
        persona=None,
        description="Broadcast to all personal agents",
        bundle=PERSONAL_BUNDLE,
    ),
    AIOption(
        10,
        "Gabriela_Codex",
        "Gabriela (Codex)",
        persona="Gabriela",
        model=CODEX_MODEL,
        description="Gabriela via Codex model",
        codex=True,
    ),
    AIOption(
        11,
        "Gemini",
        "Gemini (Generic)",
        persona="Gemini",
        provider=GENERIC_AI_PROVIDERS.get("Gemini", "google"),
        description="Generic Gemini via Google",
        category="generic",
    ),
    AIOption(
        12,
        "DeepSeek",
        "DeepSeek (Generic)",
        persona="DeepSeek",
        provider=GENERIC_AI_PROVIDERS.get("DeepSeek", "deepseek"),
        description="Generic DeepSeek via DeepSeek",
        category="generic",
    ),
    AIOption(
        13,
        "Claude",
        "Claude (Generic)",
        persona="Claude",
        provider=GENERIC_AI_PROVIDERS.get("Claude", "anthropic"),
        description="Generic Claude via Anthropic",
        category="generic",
    ),
    AIOption(
        14,
        "Grok",
        "Grok (Generic)",
        persona="Grok",
        provider=GENERIC_AI_PROVIDERS.get("Grok", "xai"),
        description="Generic Grok via xAI",
        category="generic",
    ),
    AIOption(
        15,
        "Cohere",
        "Cohere (Generic)",
        persona="Cohere",
        provider=GENERIC_AI_PROVIDERS.get("Cohere", "cohere"),
        description="Generic Cohere via Cohere",
        category="generic",
    ),
    AIOption(
        16,
        "Groq",
        "Groq (Generic)",
        persona="Groq",
        provider=GENERIC_AI_PROVIDERS.get("Groq", "groq"),
        description="Generic Groq via Groq",
        category="generic",
    ),
]


DISCUSSION_MODES: List[DiscussionMode] = [
    DiscussionMode(
        1,
        "sequential",
        "Sequential chain",
        "Send each response to the next agent in order.",
    ),
    DiscussionMode(
        2,
        "orchestration",
        "Orchestration",
        "Broadcast first, then multi-round cross-talk until a fault.",
    ),
    DiscussionMode(
        3,
        "panel",
        "Panel + synthesis",
        "One-shot panel responses, then synthesize.",
    ),
    DiscussionMode(
        4,
        "round_robin",
        "Round-robin",
        "Cycle agents through multiple rounds with shared context.",
    ),
]


def get_ai_menu() -> List[AIOption]:
    return list(AI_MENU)


def get_discussion_modes() -> List[DiscussionMode]:
    return list(DISCUSSION_MODES)


def format_ai_menu(options: Optional[Iterable[AIOption]] = None) -> str:
    options = options or AI_MENU
    lines = ["Available AI Options:"]
    grouped: Dict[str, List[AIOption]] = {"personal": [], "generic": []}
    for option in options:
        grouped.setdefault(option.category, []).append(option)

    for category, label in (("personal", "Personal Agents"), ("generic", "Generic Models")):
        if not grouped.get(category):
            continue
        lines.append(f"{label}:")
        for option in grouped[category]:
            desc = f" - {option.description}" if option.description else ""
            lines.append(f"  {option.id}) {option.label}{desc}")
    return "\n".join(lines)


def parse_ai_selection(selection: str) -> List[int]:
    if not selection:
        return []
    selection = selection.strip().lower()
    if selection in ("all", "*"):
        return [opt.id for opt in AI_MENU]
    if selection in ("personal", "p"):
        return [opt.id for opt in AI_MENU if opt.category == "personal"]
    if selection in ("generic", "g"):
        return [opt.id for opt in AI_MENU if opt.category == "generic"]
    ids: List[int] = []
    for chunk in selection.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            start, end = chunk.split("-", 1)
            if start.isdigit() and end.isdigit():
                ids.extend(range(int(start), int(end) + 1))
        elif chunk.isdigit():
            ids.append(int(chunk))
    return [i for i in ids if 1 <= i <= len(AI_MENU)]


def route_prompt_to_persona(prompt: str) -> str:
    prompt_lower = (prompt or "").lower()
    aic_keywords = [
        "implement",
        "execute",
        "operational",
        "system",
        "integration",
        "architecture",
        "biology",
        "biological",
        "chemist",
        "chemical",
        "engineer",
        "build",
        "deploy",
        "run",
        "performance",
        "applied",
        "practical",
        "viability",
        "reliability",
    ]
    sora_keywords = [
        "proof",
        "prove",
        "formal",
        "logic",
        "logical",
        "mathematical",
        "mathematics",
        "physics",
        "physical",
        "evidence",
        "validate",
        "validation",
        "structure",
        "ontology",
        "epistemology",
        "methodology",
        "taxonomy",
        "governance",
        "audit",
        "compliance",
        "rigor",
        "modeling",
        "framework",
    ]
    aria_keywords = [
        "meaning",
        "value",
        "philosophy",
        "philosophical",
        "ethics",
        "ethical",
        "theology",
        "theological",
        "interpret",
        "interpretation",
        "canon",
        "narrative",
        "norms",
        "ethos",
        "metaphysics",
        "phenomenology",
        "semiotic",
        "dialectic",
        "rhetoric",
        "concept",
        "why",
        "lived experience",
        "institutional",
        "identity",
    ]
    gabriela_keywords = [
        "pricing",
        "package",
        "packaging",
        "market",
        "gtm",
        "go-to-market",
        "sales",
        "revenue",
        "forecast",
        "investor",
        "pitch",
        "deck",
        "positioning",
        "segmentation",
        "unit economics",
        "cac",
        "ltv",
        "competitive",
        "growth",
        "monetization",
    ]
    scores = {
        "AIC": sum(1 for k in aic_keywords if k in prompt_lower),
        "Sora": sum(1 for k in sora_keywords if k in prompt_lower),
        "Aria": sum(1 for k in aria_keywords if k in prompt_lower),
        "Gabriela": sum(1 for k in gabriela_keywords if k in prompt_lower),
    }
    ordered = ["AIC", "Sora", "Aria", "Gabriela"]
    best = max(scores.values()) if scores else 0
    if best <= 0:
        return "AIC"
    for name in ordered:
        if scores.get(name) == best:
            return name
    return "AIC"


def _resolve_agents(
    selections: Sequence[int],
    prompt: str,
    provider_override: Optional[str] = None,
) -> List[ResolvedAgent]:
    resolved: List[ResolvedAgent] = []
    for opt_id in selections:
        option = next((o for o in AI_MENU if o.id == opt_id), None)
        if not option:
            continue
        if option.auto_route:
            persona = route_prompt_to_persona(prompt)
            resolved.append(
                ResolvedAgent(
                    key=option.key,
                    persona=persona,
                    label=f"{persona} (Auto)",
                    provider=option.provider or provider_override or "openai",
                    model=option.model,
                )
            )
            continue
        if option.bundle:
            for persona in option.bundle:
                resolved.append(
                    ResolvedAgent(
                        key=f"{option.key}:{persona}",
                        persona=persona,
                        label=f"{persona}{' (Codex)' if option.codex else ''}",
                        provider=option.provider or provider_override or "openai",
                        model=option.model,
                    )
                )
            continue
        if option.persona:
            resolved.append(
                ResolvedAgent(
                    key=option.key,
                    persona=option.persona,
                    label=option.label,
                    provider=option.provider or provider_override or "openai",
                    model=option.model,
                )
            )
    # Deduplicate by persona+label
    seen: Set[Tuple[str, str]] = set()
    unique: List[ResolvedAgent] = []
    for agent in resolved:
        key = (agent.persona, agent.label)
        if key in seen:
            continue
        seen.add(key)
        unique.append(agent)
    return unique


def _build_context(prompt: str, responses: List[Tuple[str, str]], suffix: str) -> Optional[str]:
    if not responses:
        return None
    compiled = "\n".join([f"- {name}: {text}" for name, text in responses])
    return f"{suffix}\n\nPrior responses:\n{compiled}\n\nOriginal prompt:\n{prompt}"


def _command_preview(tool_call) -> Optional[str]:
    if isinstance(tool_call, dict):
        raw = tool_call.get("arguments", "{}")
    else:
        raw = tool_call.function.arguments
    try:
        args = json.loads(raw or "{}")
    except Exception:
        return None
    return args.get("command")


def _make_message(persona: str, role: str, content: str, kind: str = "chat") -> ChatMessage:
    return ChatMessage(id=0, persona=persona, role=role, content=content, kind=kind)


class AIDiscussionService:
    def __init__(
        self,
        *,
        system_prompt: Optional[str] = None,
        cwd: Optional[str] = None,
        enable_shell: bool = True,
        max_tool_iterations: int = DEFAULT_MAX_TOOL_ITERS,
        max_rounds: int = DEFAULT_MAX_ROUNDS,
        permission_cb: Optional[Callable[[str, str], bool]] = None,
        provider_override: Optional[str] = None,
        model_override: Optional[str] = None,
        interaction_style: Optional[str] = None,
    ):
        self.system_prompt = system_prompt
        self.cwd = cwd
        self.enable_shell = enable_shell
        self.max_tool_iterations = max_tool_iterations
        self.max_rounds = max_rounds
        self.permission_cb = permission_cb
        self.provider_override = provider_override
        self.model_override = model_override
        self.interaction_style = normalize_interaction_style(interaction_style)

    def run_discussion(
        self,
        prompt: str,
        history: List[ChatMessage],
        selections: Sequence[int],
        mode: str,
        *,
        state: Optional[DiscussionState] = None,
    ) -> DiscussionResult:
        agents = _resolve_agents(selections, prompt, self.provider_override)
        if not agents:
            return DiscussionResult(messages=[], responses={}, fault=DiscussionFault(
                reason="no_agents",
                message="No AI agents selected.",
            ))
        if mode not in {m.key for m in DISCUSSION_MODES}:
            mode = "sequential"
        if mode == "orchestration":
            if state and state.max_rounds <= len(state.rounds):
                state.max_rounds = len(state.rounds) + self.max_rounds
            return self._run_orchestration(prompt, history, agents, state=state)
        if mode == "panel":
            return self._run_panel(prompt, history, agents)
        if mode == "round_robin":
            return self._run_round_robin(prompt, history, agents)
        return self._run_sequential(prompt, history, agents)

    def _run_sequential(
        self,
        prompt: str,
        history: List[ChatMessage],
        agents: List[ResolvedAgent],
    ) -> DiscussionResult:
        responses: Dict[str, str] = {}
        messages: List[ChatMessage] = []
        working_history = list(history)
        prior: List[Tuple[str, str]] = []
        for agent in agents:
            context_prompt = _build_context(
                prompt,
                prior,
                "Continue the discussion from your perspective.",
            )
            result = self._run_agent(
                working_history,
                agent,
                context_prompt,
            )
            messages.extend(result.messages)
            reply_text = result.reply.strip() if result.reply else "(no response)"
            response_msg = _make_message(agent.label, "assistant", reply_text)
            responses[agent.label] = reply_text
            messages.append(response_msg)
            working_history.append(response_msg)
            prior.append((agent.label, reply_text))
        return DiscussionResult(messages=messages, responses=responses)

    def _run_panel(
        self,
        prompt: str,
        history: List[ChatMessage],
        agents: List[ResolvedAgent],
    ) -> DiscussionResult:
        responses: Dict[str, str] = {}
        messages: List[ChatMessage] = []
        base_history = list(history)
        working_history = list(history)
        for agent in agents:
            result = self._run_agent(base_history, agent, None)
            messages.extend(result.messages)
            reply_text = result.reply.strip() if result.reply else "(no response)"
            response_msg = _make_message(agent.label, "assistant", reply_text)
            responses[agent.label] = reply_text
            messages.append(response_msg)
            working_history.append(response_msg)
        synthesizer = agents[0]
        synthesis_prompt = _build_context(prompt, list(responses.items()), "Synthesize the panel into a single plan.")
        synth_result = self._run_agent(working_history, synthesizer, synthesis_prompt)
        messages.extend(synth_result.messages)
        synthesis_text = synth_result.reply.strip() if synth_result.reply else "(no response)"
        synthesis_msg = _make_message(f"{synthesizer.label} (Synthesis)", "assistant", synthesis_text)
        responses[synthesis_msg.persona] = synthesis_text
        messages.append(synthesis_msg)
        return DiscussionResult(messages=messages, responses=responses)

    def _run_round_robin(
        self,
        prompt: str,
        history: List[ChatMessage],
        agents: List[ResolvedAgent],
    ) -> DiscussionResult:
        responses: Dict[str, str] = {}
        messages: List[ChatMessage] = []
        working_history = list(history)
        prior: List[Tuple[str, str]] = []
        rounds = min(self.max_rounds, max(1, len(agents)))
        for _ in range(rounds):
            for agent in agents:
                context_prompt = _build_context(
                    prompt,
                    prior,
                    "Round-robin discussion. Add your contribution.",
                )
                result = self._run_agent(working_history, agent, context_prompt)
                messages.extend(result.messages)
                reply_text = result.reply.strip() if result.reply else "(no response)"
                response_msg = _make_message(agent.label, "assistant", reply_text)
                responses[agent.label] = reply_text
                messages.append(response_msg)
                working_history.append(response_msg)
                prior.append((agent.label, reply_text))
        return DiscussionResult(messages=messages, responses=responses)

    def _run_orchestration(
        self,
        prompt: str,
        history: List[ChatMessage],
        agents: List[ResolvedAgent],
        *,
        state: Optional[DiscussionState] = None,
    ) -> DiscussionResult:
        messages: List[ChatMessage] = []
        working_history = list(history)
        if state is None:
            state = DiscussionState(
                mode="orchestration",
                prompt=prompt,
                agents=agents,
                rounds=[],
                max_rounds=self.max_rounds,
            )
        round_index = len(state.rounds)
        while round_index < state.max_rounds:
            round_responses: Dict[str, str] = {}
            context_prompt = None
            if state.rounds:
                prior_pairs: List[Tuple[str, str]] = []
                for previous in state.rounds[-1].items():
                    prior_pairs.append(previous)
                context_prompt = _build_context(
                    state.prompt,
                    prior_pairs,
                    "Orchestration round. React to the latest responses.",
                )
            round_history = list(working_history)
            for agent in agents:
                result = self._run_agent(round_history, agent, context_prompt)
                messages.extend(result.messages)
                reply_text = result.reply.strip() if result.reply else "(no response)"
                response_msg = _make_message(agent.label, "assistant", reply_text)
                messages.append(response_msg)
                working_history.append(response_msg)
                round_responses[agent.label] = reply_text
            state.rounds.append(round_responses)
            round_index += 1
            if self._is_fault(state):
                fault = DiscussionFault(
                    reason="stalled",
                    message="Orchestration hit a fault (repeated or max rounds).",
                )
                return DiscussionResult(
                    messages=messages,
                    responses=round_responses,
                    fault=fault,
                    state=state,
                )
        fault = DiscussionFault(
            reason="max_rounds",
            message="Orchestration reached max rounds.",
        )
        return DiscussionResult(messages=messages, responses={}, fault=fault, state=state)

    def _run_agent(
        self,
        history: List[ChatMessage],
        agent: ResolvedAgent,
        prompt: Optional[str],
    ) -> AgentRunResult:
        working_history = list(history)
        messages: List[ChatMessage] = []
        iteration = 0
        reply = ""
        error = None
        while iteration < self.max_tool_iterations:
            reply, error, tool_calls = generate_ai_reply(
                working_history,
                persona=agent.persona,
                prompt=prompt if iteration == 0 else None,
                append_prompt=bool(prompt) and iteration == 0,
                system_prompt=self.system_prompt,
                model=self.model_override or agent.model or AGENT_MODELS.get(agent.persona),
                cwd=self.cwd,
                enable_shell=self.enable_shell,
                model_provider=agent.provider,
                interaction_style=self.interaction_style,
            )
            if error:
                return AgentRunResult(reply=reply, error=error, messages=messages)
            if not tool_calls:
                return AgentRunResult(reply=reply, error=None, messages=messages)
            for tool_call in tool_calls:
                command = _command_preview(tool_call)
                if command and self.permission_cb:
                    if not self.permission_cb(command, self.cwd or os.getcwd()):
                        skipped = f"Skipped command: {command}"
                        skip_msg = _make_message(
                            agent.label, "assistant", skipped, kind="terminal_result"
                        )
                        tool_msg = _make_message(
                            agent.label, "tool", skipped, kind="tool_result"
                        )
                        messages.extend([skip_msg, tool_msg])
                        working_history.extend([skip_msg, tool_msg])
                        continue
                result = execute_tool_call(tool_call, cwd=self.cwd)
                if command:
                    header = f"$ {command}\n(cwd: {self.cwd or os.getcwd()})"
                    term_msg = _make_message(agent.label, "user", header, kind="terminal")
                    term_result = _make_message(
                        agent.label,
                        "assistant",
                        result["content"],
                        kind="terminal_result",
                    )
                    messages.extend([term_msg, term_result])
                    working_history.extend([term_msg, term_result])
                tool_msg = _make_message(
                    agent.label, "tool", result["content"], kind="tool_result"
                )
                messages.append(tool_msg)
                working_history.append(tool_msg)
            iteration += 1
        return AgentRunResult(
            reply=reply or "Maximum tool iterations reached.",
            error=None,
            messages=messages,
        )

    @staticmethod
    def _is_fault(state: DiscussionState) -> bool:
        if len(state.rounds) <= 1:
            return False
        latest = state.rounds[-1]
        previous = state.rounds[-2]
        if latest.keys() != previous.keys():
            return False
        for key, value in latest.items():
            prior = previous.get(key, "")
            if not prior:
                return False
            ratio = SequenceMatcher(None, value.strip(), prior.strip()).ratio()
            if ratio < 0.95:
                return False
        return True
