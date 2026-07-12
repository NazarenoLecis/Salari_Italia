from __future__ import annotations

import math
from numbers import Integral, Real
from datetime import UTC, datetime
from typing import Any, Iterable

import pandas as pd

from salari_italia.config import EUROSTAT_REQUESTS
from salari_italia.eurostat import readable_request_url
from salari_italia.schema import ensure_standard_schema

DASHBOARD_FIELDS = [
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
    "contract_type_label",
    "collective_pay_agreement",
    "collective_pay_agreement_label",
    "working_time",
    "working_time_label",
    "seniority",
    "seniority_label",
    "sector",
    "sector_label",
    "firm_size",
    "firm_size_label",
    "public_private",
    "citizenship",
    "citizenship_label",
    "pay_concept",
    "pay_period",
    "statistic",
    "percentile",
    "measure_code",
    "value",
    "unit",
    "unit_label",
    "quality_flag",
    "source_url",
]

FILTER_DIMENSIONS = [
    {"id": "year", "field": "year", "label": "Anno"},
    {"id": "geography", "field": "geography_code", "label": "Territorio", "label_field": "geography_name"},
    {"id": "sex", "field": "sex", "label": "Sesso", "label_field": "sex_label"},
    {"id": "age", "field": "age_class", "label": "Eta'", "label_field": "age_label"},
    {"id": "education", "field": "education", "label": "Titolo di studio", "label_field": "education_label"},
    {"id": "occupation", "field": "occupation", "label": "Professione", "label_field": "occupation_label"},
    {"id": "sector", "field": "sector", "label": "Settore", "label_field": "sector_label"},
    {"id": "working_time", "field": "working_time", "label": "Orario", "label_field": "working_time_label"},
    {"id": "firm_size", "field": "firm_size", "label": "Dimensione impresa", "label_field": "firm_size_label"},
    {"id": "seniority", "field": "seniority", "label": "Anzianita'", "label_field": "seniority_label"},
    {"id": "contract_type", "field": "contract_type", "label": "Contratto", "label_field": "contract_type_label"},
    {"id": "public_private", "field": "public_private", "label": "Pubblico/privato"},
    {"id": "citizenship", "field": "citizenship", "label": "Cittadinanza", "label_field": "citizenship_label"},
    {"id": "pay_period", "field": "pay_period", "label": "Periodo retributivo"},
    {"id": "statistic", "field": "statistic", "label": "Statistica"},
]

COVERAGE_ITEMS = [
    {
        "dimension": "Media, mediana, D1, D9 e rapporti D9/D1",
        "status": "available",
        "source": "Eurostat earn_ses_hourly, earn_ses_monthly, earn_ses_annual",
        "note": "Disponibili per retribuzioni lorde orarie, mensili e annuali nel perimetro SES.",
    },
    {
        "dimension": "Distribuzione complessiva dei salari",
        "status": "partial",
        "source": "Eurostat Structure of Earnings Survey",
        "note": "Il payload espone punti della distribuzione pubblicati da Eurostat, non microdati o istogrammi completi.",
    },
    {
        "dimension": "Sesso, eta', professione, settore, orario",
        "status": "available",
        "source": "Eurostat earn_ses_hourly",
        "note": "Serie storiche quadriennali o celle pubblicate secondo disponibilita' Eurostat.",
    },
    {
        "dimension": "Titolo di studio, contratto, anzianita', dimensione impresa",
        "status": "available_2022",
        "source": "Eurostat Structure of Earnings Survey 2022",
        "note": "Disponibili come tavole 2022 specifiche, da non leggere come serie storica continua.",
    },
    {
        "dimension": "Regione, provincia, citta' o comune",
        "status": "not_available",
        "source": "Non integrato",
        "note": "Non pubblicato in queste tavole Eurostat armonizzate; non viene stimato artificialmente.",
    },
    {
        "dimension": "Pubblico/privato, dipendenti/autonomi, cittadinanza o nazionalita'",
        "status": "not_available",
        "source": "Non integrato",
        "note": "Le tavole Eurostat pubbliche integrate non contengono questa dimensione; la dashboard non la sostituisce con stime.",
    },
    {
        "dimension": "Retribuzione netta",
        "status": "not_available",
        "source": "Non integrato",
        "note": "Il netto non viene simulato: le tavole salariali pubblicate qui sono lorde.",
    },
    {
        "dimension": "Costo del lavoro",
        "status": "available_separate",
        "source": "Eurostat lc_lci_lev",
        "note": "Mantenuto separato dalla retribuzione ricevuta dal lavoratore.",
    },
]


def clean_scalar(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if pd.isna(value):
        return None
    if isinstance(value, Integral) and not isinstance(value, bool):
        return int(value)
    if isinstance(value, Real) and not isinstance(value, bool):
        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return None
        return int(number) if number.is_integer() else number
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def ordered_unique(values: Iterable[Any]) -> list[Any]:
    seen: set[Any] = set()
    output: list[Any] = []
    for value in values:
        cleaned = clean_scalar(value)
        if cleaned is None or cleaned in seen:
            continue
        seen.add(cleaned)
        output.append(cleaned)
    return sorted(output)


def option_sort_key(option: dict[str, Any]) -> tuple[int, str]:
    value = option.get("value")
    if isinstance(value, int | float):
        return (0, f"{value:020.6f}")
    return (1, str(option.get("label") or value))


def dimension_options(df: pd.DataFrame, field: str, label_field: str | None = None) -> list[dict[str, Any]]:
    if field not in df.columns:
        return []
    rows = df[[field] + ([label_field] if label_field and label_field in df.columns else [])].dropna(subset=[field])
    options: dict[Any, str] = {}
    for _, row in rows.iterrows():
        value = clean_scalar(row[field])
        if value is None:
            continue
        label = clean_scalar(row[label_field]) if label_field and label_field in rows.columns else value
        options[value] = str(label if label is not None else value)
    return sorted(
        [{"value": value, "label": label} for value, label in options.items()],
        key=option_sort_key,
    )


def build_filter_options(df: pd.DataFrame) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = {}
    for dimension in FILTER_DIMENSIONS:
        options = dimension_options(df, str(dimension["field"]), dimension.get("label_field"))
        if options:
            output[str(dimension["id"])] = options
    return output


def record_payload(df: pd.DataFrame) -> list[dict[str, Any]]:
    present_fields = [field for field in DASHBOARD_FIELDS if field in df.columns]
    selected = df[present_fields].copy()
    selected = selected.sort_values(
        [field for field in ["dataset", "source_request", "geography_code", "year", "pay_period", "statistic"] if field in selected.columns]
    )
    records = []
    for row in selected.to_dict(orient="records"):
        cleaned = {key: clean_scalar(value) for key, value in row.items()}
        records.append({key: value for key, value in cleaned.items() if value is not None})
    return records


def source_catalog(geographies: tuple[str, ...]) -> list[dict[str, Any]]:
    catalog = []
    for request_config in EUROSTAT_REQUESTS:
        catalog.append(
            {
                "name": request_config["name"],
                "dataset_id": request_config["dataset_id"],
                "description": request_config.get("description"),
                "url": readable_request_url(
                    str(request_config["dataset_id"]),
                    dict(request_config.get("filters", {})),
                    geographies,
                ),
            }
        )
    return catalog


def available_ranges(df: pd.DataFrame) -> dict[str, Any]:
    years = pd.to_numeric(df.get("year", pd.Series(dtype=float)), errors="coerce").dropna()
    return {
        "year_min": int(years.min()) if not years.empty else None,
        "year_max": int(years.max()) if not years.empty else None,
        "datasets": ordered_unique(df.get("dataset", pd.Series(dtype=object))),
        "geographies": ordered_unique(df.get("geography_code", pd.Series(dtype=object))),
        "pay_periods": ordered_unique(df.get("pay_period", pd.Series(dtype=object))),
        "pay_concepts": ordered_unique(df.get("pay_concept", pd.Series(dtype=object))),
    }


def build_dashboard_payload(
    df: pd.DataFrame,
    report: dict[str, Any] | None = None,
    geographies: tuple[str, ...] = (),
) -> dict[str, Any]:
    standard = ensure_standard_schema(df)
    generated_at = datetime.now(UTC).isoformat()
    payload = {
        "meta": {
            "generated_by": "Salari_Italia",
            "prepared_at": generated_at,
            "updated_at": generated_at,
            "source_repo": "Salari_Italia",
            "source_command": "python scripts/run_pipeline.py",
            "public_url": "https://data.nazarenolecis.com/salari-italia/dashboard.json",
            "description": "Payload pubblico per la dashboard sui salari italiani.",
            "methodology": (
                "Dati ufficiali Eurostat armonizzati senza stime artificiali. Retribuzioni lorde, "
                "redditi dichiarati, imponibili contributivi, netti e costo del lavoro restano concetti separati."
            ),
            "pipeline_report": report or {},
        },
        "ranges": available_ranges(standard),
        "filters": build_filter_options(standard),
        "coverage": COVERAGE_ITEMS,
        "sources": source_catalog(geographies),
        "records": record_payload(standard),
    }
    validate_dashboard_payload(payload)
    return payload


def validate_dashboard_payload(payload: dict[str, Any]) -> dict[str, Any]:
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("Il payload dashboard non contiene record.")
    invalid_records = [
        index
        for index, record in enumerate(records)
        if not isinstance(record, dict)
        or "value" not in record
        or "year" not in record
        or "dataset" not in record
    ]
    if invalid_records:
        raise ValueError(f"Record dashboard non validi: {invalid_records[:5]}")
    filters = payload.get("filters")
    if not isinstance(filters, dict) or not filters:
        raise ValueError("Il payload dashboard non contiene filtri.")
    coverage = payload.get("coverage")
    if not isinstance(coverage, list) or not coverage:
        raise ValueError("Il payload dashboard non contiene la matrice di copertura.")
    return {
        "records": len(records),
        "filters": sorted(filters),
        "coverage_items": len(coverage),
        "valid": True,
    }
