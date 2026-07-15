from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from salari_italia.schema import ensure_standard_schema

UTC = timezone.utc

SES_INDICATORS = {
    "D1_E_EUR": ("gross_earnings", "hourly", "percentile", 10.0),
    "MED_E_EUR": ("gross_earnings", "hourly", "median", 50.0),
    "D9_E_EUR": ("gross_earnings", "hourly", "percentile", 90.0),
    "MEAN_E_EUR": ("gross_earnings", "hourly", "mean", None),
}

SES_PERIOD_BY_DATASET = {
    "earn_ses_hourly": "hourly",
    "earn_ses_monthly": "monthly",
    "earn_ses_annual": "annual",
    "earn_ses22_15": "hourly",
    "earn_ses22_16": "hourly",
    "earn_ses22_17": "hourly",
    "earn_ses22_18": "hourly",
    "earn_ses22_22": "monthly",
    "earn_ses22_23": "monthly",
    "earn_ses22_28": "annual",
    "earn_ses22_29": "annual",
    "earn_ses22_30": "annual",
    "earn_ses22_31": "annual",
}

SES2022_MEASURES = {
    "ERN": ("gross_earnings", "mean", None),
    "BNS": ("annual_bonuses", "mean", None),
    "OPAY": ("overtime_pay", "mean", None),
    "SPAY": ("special_payments", "mean", None),
    "OP_E_PC": ("overtime_pay_share", "share", None),
    "SP_E_PC": ("special_payments_share", "share", None),
}


def row_value(row: pd.Series, column: str, default: Any = None) -> Any:
    value = row.get(column, default)
    return default if pd.isna(value) else value


def dimension_payload(row: pd.Series) -> str:
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


def measure_definition(dataset_id: str, row: pd.Series) -> tuple[str, str, str, float | None, str]:
    if dataset_id in {"earn_ses_hourly", "earn_ses_monthly", "earn_ses_annual"}:
        code = str(row_value(row, "indic_se", "unknown"))
        indicator_definition = SES_INDICATORS.get(
            code, ("gross_earnings", SES_PERIOD_BY_DATASET[dataset_id], "other", None)
        )
        pay_concept = indicator_definition[0]
        statistic = indicator_definition[2]
        percentile = indicator_definition[3]
        pay_period = SES_PERIOD_BY_DATASET[dataset_id]
        return pay_concept, pay_period, statistic, percentile, code
    if dataset_id in {
        "earn_ses22_15",
        "earn_ses22_16",
        "earn_ses22_17",
        "earn_ses22_18",
        "earn_ses22_22",
        "earn_ses22_23",
        "earn_ses22_28",
        "earn_ses22_29",
        "earn_ses22_30",
        "earn_ses22_31",
    }:
        code = str(row_value(row, "indic_se", "unknown"))
        pay_concept, statistic, percentile = SES2022_MEASURES.get(code, ("gross_earnings", "other", None))
        return pay_concept, SES_PERIOD_BY_DATASET[dataset_id], statistic, percentile, code
    if dataset_id in {"earn_ses_pub1s", "earn_ses_pub1a", "earn_ses_pub1i"}:
        return "low_wage_earners", "hourly", "share_below_two_thirds_median", None, "LOW_WAGE_SHARE"
    if dataset_id == "earn_gr_gpgr2":
        return "gender_pay_gap_unadjusted", "hourly", "mean_gap", None, "GPG_UNADJUSTED"
    if dataset_id == "lc_lci_lev":
        return "labour_cost", "hourly", "mean", None, str(row_value(row, "lcstruct", "TOTAL_LABOUR_COST"))
    if dataset_id == "lfsa_ergan":
        return "labour_market_context", "annual", "employment_rate", None, "EMPLOYMENT_RATE"
    if dataset_id == "lfsa_argan":
        return "labour_market_context", "annual", "activity_rate", None, "ACTIVITY_RATE"
    if dataset_id == "une_rt_a":
        return "labour_market_context", "annual", "unemployment_rate", None, "UNEMPLOYMENT_RATE"
    if dataset_id == "lfsa_eppga":
        return "labour_market_context", "annual", "part_time_share", None, "PART_TIME_SHARE"
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
        pay_concept, pay_period, statistic, percentile, measure_code = measure_definition(dataset_id, row)
        year_raw = row_value(row, "time")
        year = int(year_raw) if year_raw is not None and str(year_raw).isdigit() else year_raw
        rows.append(
            {
                "source": "Eurostat",
                "dataset": dataset_id,
                "source_request": request_name,
                "year": year,
                "geography_type": "country_or_european_aggregate",
                "geography_code": row_value(row, "geo"),
                "geography_name": row_value(row, "geo_label"),
                "geography_basis": "reporting_country",
                "sex": row_value(row, "sex"),
                "sex_label": row_value(row, "sex_label"),
                "age_class": row_value(row, "age"),
                "age_label": row_value(row, "age_label"),
                "education": row_value(row, "isced11"),
                "education_label": row_value(row, "isced11_label"),
                "occupation": row_value(row, "isco08"),
                "occupation_label": row_value(row, "isco08_label"),
                "employment_status": row_value(row, "wstatus"),
                "contract_type": row_value(row, "emp_cont"),
                "contract_type_label": row_value(row, "emp_cont_label"),
                "collective_pay_agreement": row_value(row, "cpayagr"),
                "collective_pay_agreement_label": row_value(row, "cpayagr_label"),
                "working_time": row_value(row, "worktime"),
                "working_time_label": row_value(row, "worktime_label"),
                "seniority": row_value(row, "l_serv"),
                "seniority_label": row_value(row, "l_serv_label"),
                "sector": row_value(row, "nace_r2", row_value(row, "nace_r1")),
                "sector_label": row_value(row, "nace_r2_label", row_value(row, "nace_r1_label")),
                "firm_size": row_value(row, "sizeclas"),
                "firm_size_label": row_value(row, "sizeclas_label"),
                "public_private": None,
                "citizenship": row_value(row, "citizen"),
                "citizenship_label": row_value(row, "citizen_label"),
                "pay_concept": pay_concept,
                "pay_period": pay_period,
                "statistic": statistic,
                "percentile": percentile,
                "measure_code": measure_code,
                "value": pd.to_numeric(row_value(row, "value"), errors="coerce"),
                "unit": row_value(row, "unit", row_value(row, "currency")),
                "unit_label": row_value(row, "unit_label", row_value(row, "currency_label")),
                "population": None,
                "sample_size": None,
                "quality_flag": row_value(row, "status"),
                "source_url": source_url,
                "download_timestamp": timestamp,
                "dimensions_json": dimension_payload(row),
            }
        )

    return ensure_standard_schema(pd.DataFrame(rows))
