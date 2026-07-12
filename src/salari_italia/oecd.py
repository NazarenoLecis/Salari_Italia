from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import pandas as pd
import requests

from salari_italia.config import OECD_BASE_URL
from salari_italia.schema import ensure_standard_schema

OECD_AREA_LABELS = {
    "AUS": "Australia",
    "AUT": "Austria",
    "BEL": "Belgio",
    "BGR": "Bulgaria",
    "CAN": "Canada",
    "CHE": "Svizzera",
    "CHL": "Cile",
    "COL": "Colombia",
    "CRI": "Costa Rica",
    "CZE": "Cechia",
    "DEU": "Germania",
    "DNK": "Danimarca",
    "ESP": "Spagna",
    "EST": "Estonia",
    "FIN": "Finlandia",
    "FRA": "Francia",
    "GBR": "Regno Unito",
    "GRC": "Grecia",
    "HRV": "Croazia",
    "HUN": "Ungheria",
    "IRL": "Irlanda",
    "ISL": "Islanda",
    "ISR": "Israele",
    "ITA": "Italia",
    "JPN": "Giappone",
    "KOR": "Corea del Sud",
    "LTU": "Lituania",
    "LUX": "Lussemburgo",
    "LVA": "Lettonia",
    "MEX": "Messico",
    "NLD": "Paesi Bassi",
    "NOR": "Norvegia",
    "NZL": "Nuova Zelanda",
    "OECD": "Media OCSE",
    "POL": "Polonia",
    "PRT": "Portogallo",
    "ROU": "Romania",
    "SVK": "Slovacchia",
    "SVN": "Slovenia",
    "SWE": "Svezia",
    "TUR": "Turchia",
    "USA": "Stati Uniti",
}


def read_oecd_csv(text: str) -> pd.DataFrame:
    return pd.DataFrame(list(csv.DictReader(io.StringIO(text))))


def download_oecd_dataset(
    dataset_id: str,
    start_period: str | None = None,
    raw_output_path: Path | None = None,
    timeout: int = 120,
) -> tuple[pd.DataFrame, str]:
    params = {}
    if start_period:
        params["startPeriod"] = start_period
    query = f"?{urlencode(params)}" if params else ""
    url = f"{OECD_BASE_URL}/{dataset_id}/.{query}"
    response = requests.get(url, headers={"Accept": "text/csv"}, timeout=timeout)
    response.raise_for_status()
    text = response.text
    if raw_output_path is not None:
        raw_output_path.parent.mkdir(parents=True, exist_ok=True)
        raw_output_path.write_text(text, encoding="utf-8")
    return read_oecd_csv(text), response.url


def row_value(row: dict[str, Any], key: str) -> Any:
    value = row.get(key)
    if value is None or value == "":
        return None
    return value


def harmonise_oecd_average_wages(raw: pd.DataFrame, request_name: str, source_url: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in raw.to_dict(orient="records"):
        if row_value(row, "MEASURE") != "WG":
            continue
        if row_value(row, "UNIT_MEASURE") != "USD_PPP":
            continue
        if row_value(row, "PAY_PERIOD") != "A":
            continue
        if row_value(row, "AGGREGATION_OPERATION") != "MEAN":
            continue
        if row_value(row, "SEX") not in {"_Z", "T", None}:
            continue
        try:
            value = float(row.get("OBS_VALUE"))
        except (TypeError, ValueError):
            continue
        year_raw = row_value(row, "TIME_PERIOD")
        year = int(year_raw) if str(year_raw).isdigit() else year_raw
        area = row_value(row, "REF_AREA")
        rows.append(
            {
                "source": "OECD",
                "dataset": "DSD_EARNINGS@AV_AN_WAGE",
                "source_request": request_name,
                "year": year,
                "geography_type": "country_or_oecd_aggregate",
                "geography_code": area,
                "geography_name": OECD_AREA_LABELS.get(str(area), area),
                "geography_basis": "oecd_reporting_country",
                "sex": "T",
                "sex_label": "Totale",
                "employment_status": "employee_fte",
                "pay_concept": "average_annual_wage_oecd",
                "pay_period": "annual",
                "statistic": "mean",
                "percentile": None,
                "measure_code": row_value(row, "MEASURE"),
                "value": value,
                "unit": "USD_PPP",
                "unit_label": "Dollari USA PPP 2025",
                "quality_flag": row_value(row, "OBS_STATUS"),
                "source_url": source_url,
            }
        )
    return ensure_standard_schema(pd.DataFrame(rows))
