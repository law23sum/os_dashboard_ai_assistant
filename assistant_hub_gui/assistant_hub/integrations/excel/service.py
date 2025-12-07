"""Excel service orchestrating local/cloud operations with AI."""

from __future__ import annotations

import pandas as pd
from typing import List

from ...ai_layer.tools import excel_generate_pandas_code
from ...versioning.git_async import enqueue_commit
from .cloud_client import ExcelCloudClient
from .local_client import load_sheet, save_sheet


class ExcelService:
    """Provide higher-level Excel actions for the assistant hub."""

    def __init__(self, cloud: ExcelCloudClient | None = None):
        self.cloud = cloud or ExcelCloudClient()

    def summarize_sheet(self, workbook_path: str, sheet_name: str, instruction: str, actor: str = "AIC") -> List[str]:
        df = load_sheet(workbook_path, sheet_name)
        code = excel_generate_pandas_code(df.head(20).to_markdown(index=False), instruction)
        local_vars: dict = {"df": df.copy()}
        exec(code, {}, local_vars)
        result_df: pd.DataFrame = local_vars.get("result_df", df)
        save_sheet(workbook_path, "Summary", result_df)
        return [workbook_path]
