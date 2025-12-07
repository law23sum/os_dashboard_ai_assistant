"""High-level Excel operations leveraging GPT."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from ...ai import get_openai_client, openai_available
from ...versioning.git_async import enqueue_commit
from ..msgraph.client import GraphClient
from .cloud_client import GraphExcelClient
from .local_client import load_sheet, write_sheet


DEFAULT_MODEL = "gpt-4o-mini"


def _prompt_for_transformation(sample: str, instruction: str) -> str:
    if not openai_available():
        raise RuntimeError("OpenAI API is not configured; cannot generate Excel transformations.")

    client = get_openai_client()
    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that writes concise Python pandas code to transform a DataFrame. "
                "Operate on a variable named df and assign the final result to result_df."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Sample data (first rows):\n{sample}\n\n"
                f"Instruction: {instruction}\n"
                "Return only the Python code."
            ),
        },
    ]
    response = client.chat.completions.create(model=DEFAULT_MODEL, messages=messages)
    return response.choices[0].message.content or ""


class ExcelService:
    """Coordinates local/cloud Excel operations and AI transformations."""

    def __init__(self, *, graph_client: Optional[GraphClient] = None):
        self.graph_client = graph_client or GraphClient()
        self.cloud = GraphExcelClient(self.graph_client)

    # --- local helpers ----------------------------------------------------
    def summarize_local_sheet(
        self,
        path: str | Path,
        sheet_name: str,
        *,
        instruction: str,
        actor: str = "AIC",
    ) -> Dict[str, Any]:
        """Use GPT to transform a local sheet and write a Summary sheet."""

        df = load_sheet(path, sheet_name=sheet_name)
        code = _prompt_for_transformation(df.head(20).to_markdown(index=False), instruction)

        local_vars: Dict[str, Any] = {"df": df.copy()}
        exec(code, {}, local_vars)
        result_df = local_vars.get("result_df", df)

        summary_sheet = "Summary"
        write_sheet(path, summary_sheet, result_df)
        enqueue_commit([str(path)], actor=actor, reason=f"Update Excel summary for {sheet_name}", tag="excel")
        return {"code": code, "output_rows": len(result_df)}

    # --- cloud helpers ----------------------------------------------------
    def list_cloud_workbooks(self) -> List[Dict[str, Any]]:
        return self.cloud.list_workbooks()

    def list_cloud_sheets(self, item_id: str) -> List[Dict[str, Any]]:
        return self.cloud.list_worksheets(item_id)

    def update_cloud_range(
        self,
        item_id: str,
        worksheet_id: str,
        address: str,
        values: List[List[Any]],
        *,
        actor: str = "AIC",
    ) -> Dict[str, Any]:
        result = self.cloud.update_range(item_id, worksheet_id, address, values)
        enqueue_commit([], actor=actor, reason=f"Updated cloud range {address}", tag="excel")
        return result
