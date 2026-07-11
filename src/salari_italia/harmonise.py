from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import pandas as pd

from salari_italia.schema import ensure_standard_schema

SES_INDICATORS = {
    "D1_E_EUR": ("gross_earnings", "hourly", "percentile", 10.0),
    "MED_E_EUR": ("gross_earnings", "hourly", "median", 50.0),
    "D9_E_EUR": ("gross_earnings", "hourly", "percentile", 90.0),
    "MEAN_E_EUR": ("gross_earnings", "hourly", "mean", None),
}


def _value(row: pd.Series, column: str, default: Any = None) -> Any:
    value = row.get(column, default)
    return default if pd.isna(value) else value


def _dimension_payload(row: pd.Series) -> str:
    dimensions = {}
    for column in row.index:
        if column in {"value", "status", "source_url", "download_timestamp", "source_request"}:
            continue
        if column.endswith("_label"):
            continue
        value = row[column]
        if not pd.isna(value):
            dimensions[column] = value
    return json.dumps(dimensions, ensure_ascii=False, sort_keys=True)


def _measure_definition(dataset_id: str, row: pd.Series) -> tuple[str, str, str, float | None, str]:
    if dataset_id == "earn_ses_hourly":
        code = str(_value(row, "indic_se", "unknown"))
        pay_concept, pay_period, statistic, percentile = SES_INDICATORS.get(
            code, ("gross_earnings", "hourly", "other", None)
        )
        return pay_concept, pay_period, statistic, percentile, code
    if dataset_id == "earn_ses_pub1s":
        return "low_wage_earners", "hourly", "share_below_two_thirds_median", None, "LOW_WAGE_SHARE"
    if dataset_id == "earn_gr_gpgr2":
        return "gender_pay_gap_unadjusted", "hourly", "mean_gap", None, "GPG_UNADJUSTED"
    if dataset_id == "lc_lci_lev":
        return "labour_cost", "hourly", "mean", None, str(_value(row, "lcstruct", "TOTAL_LABOUR_COST"))
    return "unknown", "unknown", "other", None, "unknown"


def harmonise_eurostat(
    raw: pd.DataFrame,
    dataset_id: str,
    request_name: str,
    source_url: str,
    download_timestamp: str | None = None,
) -> pd.DataFrame:
    timestamp = download_timestamp or datetime.now(UTC).isoformat()
    rows: list[dict[str, Any]] = []

    for _, row in raw.iterrows():
        pay_concept, pay_period, statistic, percentile, measure_code = _measure_definition(dataset_id, row)
        year_raw = _value(row, "time")
        year = int(year_raw) if year_raw is not None and str(year_raw).isdigit() else year_raw
        rows.append(
            {
                "source": "Eurostat",
                "dataset": dataset_id,
                "source_request": request_name,
                "year": year,
                "geography_type": "country_or_european_aggregate",
                "geography_code": _value(row, "geo"),
                "geography_name": _value(row, "geo_label"),
                "geography_basis": "reporting_country",
                "sex": _value(row, "sex"),
                "sex_label": _value(row, "sex_label"),
                "age_class": _value(row, "age"),
                "age_label": _value(row, "age_label"),
                "education": _value(row, "isced11"),
                "education_label": _value(row, "isced11_label"),
                "occupation": _value(row, "isco08"),
                "occupation_label": _value(row, "isco08_label"),
                "employment_status": _value(row, "wstatus"),
                "contract_type": _value(row, "emp_cont"),
                "working_time": _value(row, "worktime"),
                "working_time_label": _value(row, "worktime_label"),
                "sector": _value(row, "nace_r2", _value(row, "nace_r1")),
                "sector_label": _value(row, "nace_r2_label", _value(row, "nace_r1_label")),
                "firm_size": _value(row, "sizeclas"),
                "firm_size_label": _value(row, "sizeclas_label"),
                "public_private": None,
                "pay_concept": pay_concept,
                "pay_period": pay_period,
                "statistic": statistic,
                "percentile": percentile,
                "measure_code": measure_code,
                "value": pd.to_numeric(_value(row, "value"), errors="coerce"),
                "unit": _value(row, "unit", _value(row, "currency")),
                "unit_label": _value(row, "unit_label", _value(row, "currency_label")),
                "population": None,
                "sample_size": None,
                "quality_flag": _value(row, "status"),
                "source_url": source_url,
                "download_timestamp": timestamp,
                "dimensions_json": _dimension_payload(row),
            }
        )

    return ensure_standard_schema(pd.DataFrame(rows))
