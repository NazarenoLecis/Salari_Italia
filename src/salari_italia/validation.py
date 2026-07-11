from __future__ import annotations

from typing import Any

import pandas as pd

from salari_italia.schema import STANDARD_COLUMNS


def validate_dataset(df: pd.DataFrame) -> dict[str, Any]:
    missing_columns = [column for column in STANDARD_COLUMNS if column not in df.columns]
    numeric_values = pd.to_numeric(df.get("value", pd.Series(dtype=float)), errors="coerce")
    invalid_value_count = int(numeric_values.isna().sum()) if len(df) else 0
    duplicate_columns = [
        column
        for column in ("source", "dataset", "source_request", "year", "dimensions_json", "statistic", "percentile")
        if column in df.columns
    ]
    duplicate_count = int(df.duplicated(subset=duplicate_columns).sum()) if duplicate_columns and len(df) else 0
    year_values = pd.to_numeric(df.get("year", pd.Series(dtype=float)), errors="coerce").dropna()
    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "missing_required_columns": missing_columns,
        "invalid_value_count": invalid_value_count,
        "duplicate_count": duplicate_count,
        "year_min": int(year_values.min()) if not year_values.empty else None,
        "year_max": int(year_values.max()) if not year_values.empty else None,
        "datasets": sorted(df["dataset"].dropna().astype(str).unique().tolist()) if "dataset" in df else [],
        "geographies": sorted(df["geography_code"].dropna().astype(str).unique().tolist()) if "geography_code" in df else [],
        "valid": not missing_columns and invalid_value_count == 0,
    }
