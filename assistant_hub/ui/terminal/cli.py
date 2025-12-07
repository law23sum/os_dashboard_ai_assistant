"""Entry point for the osdash CLI."""
from __future__ import annotations

import json
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table

from assistant_hub.config import AppConfig
from assistant_hub.core.models import AssistantState, Project, Task
from assistant_hub.core.routing.router import AgentRouter
from assistant_hub.core.state.json_store import JSONStateStore
from assistant_hub.ai.openai_client import OpenAIClient
from assistant_hub.ai.agents.aic import AICAgent
from assistant_hub.ai.agents.aria import AriaAgent
from assistant_hub.ai.agents.sora import SoraAgent
from assistant_hub.integrations.msgraph.auth import GraphAuthenticator
from assistant_hub.integrations.msgraph.client import GraphClient
from assistant_hub.integrations.onenote.service import OneNoteService
from assistant_hub.integrations.onenote.client import OneNoteClient
from assistant_hub.integrations.excel.service import ExcelService
from assistant_hub.integrations.excel.cloud_client import ExcelCloudClient
from assistant_hub.integrations.word.service import WordService
from assistant_hub.integrations.software_locator import SoftwareLocator
from assistant_hub.ai.workflows import clean_notebook_workflow

console = Console()


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    cfg = AppConfig.from_env()
    store = JSONStateStore(cfg.state_file)
    state = store.load()
    router = AgentRouter()
    client = OpenAIClient(cfg.openai)
    router.register(AICAgent(client))
    router.register(AriaAgent(client))
    router.register(SoraAgent(client))

    auth = GraphAuthenticator(cfg.graph.tenant_id, cfg.graph.client_id, cfg.graph.client_secret)
    graph_client = GraphClient(auth)
    onenote = OneNoteService(OneNoteClient(graph_client))
    excel = ExcelService(ExcelCloudClient(graph_client))
    word = WordService()
    locator = SoftwareLocator()

    ctx.obj = {
        "cfg": cfg,
        "store": store,
        "state": state,
        "router": router,
        "onenote": onenote,
        "excel": excel,
        "word": word,
        "locator": locator,
    }


@cli.group()
@click.pass_context
def projects(ctx: click.Context) -> None:
    """Manage projects."""


@projects.command("list")
@click.pass_context
def projects_list(ctx: click.Context) -> None:
    state: AssistantState = ctx.obj["state"]
    table = Table(title="Projects")
    table.add_column("Name")
    table.add_column("Description")
    if not state.projects:
        console.print("No projects yet. Use 'osdash projects add' to create one.")
        return
    for project in state.projects:
        table.add_row(project.name, project.description)
    console.print(table)


@projects.command("add")
@click.argument("name")
@click.option("--description", default="", help="Project description")
@click.pass_context
def projects_add(ctx: click.Context, name: str, description: str) -> None:
    state: AssistantState = ctx.obj["state"]
    state.projects.append(Project(name=name, description=description))
    ctx.obj["store"].save(state)
    console.print(f"Added project '{name}'")


@cli.group()
@click.pass_context
def onenote(ctx: click.Context) -> None:
    """Interact with OneNote."""


@onenote.command("notebooks")
@click.pass_context
def onenote_notebooks(ctx: click.Context) -> None:
    service: OneNoteService = ctx.obj["onenote"]
    data = service.notebooks()
    console.print_json(json.dumps(data))


@cli.group()
@click.pass_context
def excel(ctx: click.Context) -> None:
    """Excel helpers."""


@excel.command("workbooks")
@click.pass_context
def excel_workbooks(ctx: click.Context) -> None:
    service: ExcelService = ctx.obj["excel"]
    console.print_json(json.dumps(service.workbooks()))


@excel.command("summarize-local")
@click.argument("path")
@click.pass_context
def excel_summarize(ctx: click.Context, path: str) -> None:
    service: ExcelService = ctx.obj["excel"]
    console.print(service.summarize_local(path))


@cli.group()
@click.pass_context
def word(ctx: click.Context) -> None:
    """Word helpers."""


@word.command("summarize-local")
@click.argument("path")
@click.pass_context
def word_summarize(ctx: click.Context, path: str) -> None:
    service: WordService = ctx.obj["word"]
    console.print(service.summarize_local(path))


@cli.group()
@click.pass_context
def software(ctx: click.Context) -> None:  # noqa: ARG001
    """Locate installed software such as git, Word, Excel, or a PDF viewer."""


@software.command("locate")
@click.argument("name")
@click.option(
    "--alias",
    multiple=True,
    help="Additional executable names to try (e.g. --alias winword --alias soffice)",
)
@click.pass_context
def software_locate(ctx: click.Context, name: str, alias: tuple[str, ...]) -> None:
    locator: SoftwareLocator = ctx.obj["locator"]
    result = locator.locate(name, aliases=alias)
    if result.found:
        console.print(f"[green]{result.name}[/] found at {result.path}")
    else:
        console.print(
            f"[red]{result.name}[/] not found. Tried: {result.tried}"
            "\nTip: pass --alias to search alternate executable names."
        )


@software.command("defaults")
@click.pass_context
def software_defaults(ctx: click.Context) -> None:
    """Check all default targets (git, word, excel, pdf)."""

    locator: SoftwareLocator = ctx.obj["locator"]
    table = Table(title="Default software locations")
    table.add_column("Target")
    table.add_column("Status")
    table.add_column("Details")
    for result in locator.scan_defaults():
        status = "Found" if result.found else "Not found"
        detail = result.path or f"Tried: {result.tried}"
        style = "green" if result.found else "yellow"
        table.add_row(result.name, f"[{style}]{status}[/]", detail)
    console.print(table)


@cli.command()
@click.argument("agent")
@click.argument("message")
@click.pass_context
def chat(ctx: click.Context, agent: str, message: str) -> None:
    router: AgentRouter = ctx.obj["router"]
    console.print(router.route(agent, message))


@cli.command("workflow-clean-notebook")
@click.argument("path")
@click.pass_context
def workflow_clean_notebook(ctx: click.Context, path: str) -> None:  # noqa: ARG001
    console.print(clean_notebook_workflow(path))


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
