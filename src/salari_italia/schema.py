from __future__ import annotations

import pandas as pd

STANDARD_COLUMNS = [
    "source",
    "dataset",
    "source_request",
    "year",
    "geography_type",
    "geography_code",
    "geography_name",
    "geography_basis",
    "sex",
    "sex_label",
    "age_class",
    "age_label",
    "education",
    "education_label",
    "occupation",
    "occupation_label",
    "employment_status",
    "contract_type",
    "working_time",
    "working_time_label",
    "sector",
    "sector_label",
    "firm_size",
    "firm_size_label",
    "public_private",
    "pay_concept",
    "pay_period",
    "statistic",
    "percentile",
    "measure_code",
    "value",
    "unit",
    "unit_label",
    "population",
    "sample_size",
    "quality_flag",
    "source_url",
    "download_timestamp",
    "dimensions_json",
]


def empty_standard_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=STANDARD_COLUMNS)


def ensure_standard_schema(df: pd.DataFrame) -> pd.DataFrame:
    output = df.copy()
    for column in STANDARD_COLUMNS:
        if column not in output.columns:
            output[column] = None
    remaining = [column for column in output.columns if column not in STANDARD_COLUMNS]
    return output[STANDARD_COLUMNS + remaining]
