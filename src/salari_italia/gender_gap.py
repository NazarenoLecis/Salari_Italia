from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from salari_italia.schema import ensure_standard_schema

GPG_DECOMPOSITION_DATASET = "eurostat_gpg_decomposition_ses2022"
GPG_DECOMPOSITION_REQUEST = "gender_pay_gap_decomposition_ses2022"
GPG_DECOMPOSITION_SOURCE_URL = (
    "https://ec.europa.eu/eurostat/documents/3888793/22251197/"
    "KS-01-25-035-EN-N.pdf/ebeddabe-578a-e620-3c61-122891de2b94"
    "?download=true&t=1758787175828&version=1.0"
)
GPG_DECOMPOSITION_PRODUCT_URL = "https://ec.europa.eu/eurostat/web/products-statistical-working-papers/w/ks-01-25-035"
GPG_DECOMPOSITION_RESOURCE = Path(__file__).resolve().parent / "resources" / "gender_pay_gap_decomposition_ses2022.csv"

GPG_COMPONENTS = {
    "unadjusted_gpg": ("gender_pay_gap_decomposition", "unadjusted", "GPG_UNADJUSTED_SES2022"),
    "overall_explained_gap": ("gender_pay_gap_decomposition", "explained_overall", "GPG_EXPLAINED_OVERALL"),
    "residual": ("gender_pay_gap_decomposition", "residual", "GPG_RESIDUAL"),
    "age": ("gender_pay_gap_decomposition", "age", "GPG_EXPLAINED_AGE"),
    "education": ("gender_pay_gap_decomposition", "education", "GPG_EXPLAINED_EDUCATION"),
    "occupation": ("gender_pay_gap_decomposition", "occupation", "GPG_EXPLAINED_OCCUPATION"),
    "job_experience": ("gender_pay_gap_decomposition", "job_experience", "GPG_EXPLAINED_JOB_EXPERIENCE"),
    "employment_contract": ("gender_pay_gap_decomposition", "employment_contract", "GPG_EXPLAINED_EMPLOYMENT_CONTRACT"),
    "working_time": ("gender_pay_gap_decomposition", "working_time", "GPG_EXPLAINED_WORKING_TIME"),
    "economic_activity": ("gender_pay_gap_decomposition", "economic_activity", "GPG_EXPLAINED_ECONOMIC_ACTIVITY"),
    "enterprise_size": ("gender_pay_gap_decomposition", "enterprise_size", "GPG_EXPLAINED_ENTERPRISE_SIZE"),
    "enterprise_control": ("gender_pay_gap_decomposition", "enterprise_control", "GPG_EXPLAINED_ENTERPRISE_CONTROL"),
    "geographical_location": (
        "gender_pay_gap_decomposition",
        "geographical_location",
        "GPG_EXPLAINED_GEOGRAPHICAL_LOCATION",
    ),
    "adjusted_unexplained_gpg": (
        "gender_pay_gap_decomposition",
        "adjusted_unexplained",
        "GPG_ADJUSTED_UNEXPLAINED",
    ),
}


def decomposition_dimensions(component: str) -> str:
    return json.dumps(
        {
            "source_table": "Eurostat KS-01-25-035 Table 2",
            "reference_survey": "Structure of Earnings Survey 2022",
            "method": "Blinder-Oaxaca decomposition",
            "component": component,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def base_row(source_row: pd.Series, timestamp: str, component: str) -> dict[str, Any]:
    return {
        "source": "Eurostat",
        "dataset": GPG_DECOMPOSITION_DATASET,
        "source_request": GPG_DECOMPOSITION_REQUEST,
        "year": 2022,
        "geography_type": "country_or_european_aggregate",
        "geography_code": source_row["geography_code"],
        "geography_name": source_row["geography_name"],
        "geography_basis": "reporting_country",
        "sex": "F_M",
        "sex_label": "Donne rispetto agli uomini",
        "sector": "B-S_X_O",
        "sector_label": "Industria, costruzioni e servizi esclusa pubblica amministrazione",
        "firm_size": "GE10",
        "firm_size_label": "10 addetti e oltre",
        "pay_period": "hourly",
        "unit": "PC",
        "unit_label": "Percentuale della retribuzione oraria lorda media maschile",
        "population": None,
        "sample_size": None,
        "quality_flag": None,
        "source_url": GPG_DECOMPOSITION_SOURCE_URL,
        "download_timestamp": timestamp,
        "dimensions_json": decomposition_dimensions(component),
    }


def load_gender_pay_gap_decomposition(
    source_path: Path | None = None,
    download_timestamp: str | None = None,
) -> pd.DataFrame:
    path = source_path or GPG_DECOMPOSITION_RESOURCE
    timestamp = download_timestamp or datetime.now(UTC).isoformat()
    raw = pd.read_csv(path)
    rows: list[dict[str, Any]] = []
    for _, source_row in raw.iterrows():
        for column, (pay_concept, statistic, measure_code) in GPG_COMPONENTS.items():
            row = base_row(source_row, timestamp, statistic)
            row.update(
                {
                    "pay_concept": pay_concept,
                    "statistic": statistic,
                    "percentile": None,
                    "measure_code": measure_code,
                    "value": pd.to_numeric(source_row[column], errors="coerce"),
                }
            )
            rows.append(row)
        adjusted_row = base_row(source_row, timestamp, "adjusted_unexplained")
        adjusted_row.update(
            {
                "pay_concept": "gender_pay_gap_adjusted",
                "statistic": "mean_gap",
                "percentile": None,
                "measure_code": "GPG_ADJUSTED_UNEXPLAINED",
                "value": pd.to_numeric(source_row["adjusted_unexplained_gpg"], errors="coerce"),
            }
        )
        rows.append(adjusted_row)
    return ensure_standard_schema(pd.DataFrame(rows))
