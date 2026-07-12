from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from salari_italia.config import (
    EUROSTAT_REQUESTS,
    PROCESSED_DIR,
    RAW_DIR,
    VALIDATION_DIR,
    ensure_data_directories,
    requested_geographies,
)
from salari_italia.dashboard import build_dashboard_payload, validate_dashboard_payload
from salari_italia.eurostat import download_dataset, jsonstat_to_frame
from salari_italia.harmonise import harmonise_eurostat
from salari_italia.indicators import build_percentile_ratios
from salari_italia.schema import empty_standard_frame, ensure_standard_schema
from salari_italia.validation import validate_dataset


def json_payload_text(payload: dict[str, Any], pretty: bool = True) -> str:
    if pretty:
        return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(path.name + ".tmp")
    temp_path.write_text(text, encoding="utf-8")
    temp_path.replace(path)


def write_json_atomic(path: Path, payload: dict[str, Any], pretty: bool = True) -> None:
    write_text_atomic(path, json_payload_text(payload, pretty=pretty))


def write_dataframe_outputs(output: pd.DataFrame, csv_path: Path, json_path: Path, parquet_path: Path) -> None:
    for path in (csv_path, json_path, parquet_path):
        path.parent.mkdir(parents=True, exist_ok=True)
    csv_temp = csv_path.with_name(csv_path.name + ".tmp")
    json_temp = json_path.with_name(json_path.name + ".tmp")
    parquet_temp = parquet_path.with_name(parquet_path.name + ".tmp")
    output.to_csv(csv_temp, index=False)
    output.to_json(json_temp, orient="records", force_ascii=False)
    output.to_parquet(parquet_temp, index=False)
    csv_temp.replace(csv_path)
    json_temp.replace(json_path)
    parquet_temp.replace(parquet_path)


def run_pipeline(
    geographies: tuple[str, ...] | None = None,
    requests_config: Iterable[dict[str, Any]] = EUROSTAT_REQUESTS,
    fail_on_errors: bool = True,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    ensure_data_directories()
    selected_geographies = geographies or requested_geographies()
    frames: list[pd.DataFrame] = []
    errors: list[dict[str, str]] = []
    started_at = datetime.now(UTC).isoformat()

    for request_config in requests_config:
        name = str(request_config["name"])
        dataset_id = str(request_config["dataset_id"])
        raw_path = RAW_DIR / f"{name}.json"
        try:
            payload, source_url = download_dataset(
                dataset_id=dataset_id,
                filters=dict(request_config.get("filters", {})),
                geographies=selected_geographies,
                raw_output_path=raw_path,
            )
            raw = jsonstat_to_frame(payload)
            if raw.empty:
                raise RuntimeError("La risposta non contiene osservazioni.")
            frame = harmonise_eurostat(
                raw=raw,
                dataset_id=dataset_id,
                request_name=name,
                source_url=source_url,
                download_timestamp=payload.get("updated"),
            )
            frames.append(frame)
        except Exception as exc:
            errors.append({"request": name, "dataset": dataset_id, "error": str(exc)})

    observed = ensure_standard_schema(pd.concat(frames, ignore_index=True)) if frames else empty_standard_frame()
    derived = build_percentile_ratios(observed)
    output = ensure_standard_schema(pd.concat([observed, derived], ignore_index=True))

    csv_path = PROCESSED_DIR / "salari_eurostat.csv"
    json_path = PROCESSED_DIR / "salari_eurostat.json"
    parquet_path = PROCESSED_DIR / "salari_eurostat.parquet"
    dashboard_path = PROCESSED_DIR / "salari_dashboard.json"

    validation = validate_dataset(output)
    report = {
        "started_at": started_at,
        "completed_at": datetime.now(UTC).isoformat(),
        "geographies": list(selected_geographies),
        "successful_requests": len(frames),
        "failed_requests": len(errors),
        "errors": errors,
        "validation": validation,
        "outputs": {
            "csv": str(csv_path),
            "json": str(json_path),
            "parquet": str(parquet_path),
            "dashboard_json": str(dashboard_path),
        },
    }
    report_path = VALIDATION_DIR / "pipeline_report.json"

    if not frames:
        write_json_atomic(report_path, report)
        raise RuntimeError(f"Nessuna fonte ha restituito dati. Dettagli in {report_path}.")
    if not validation.get("valid"):
        write_json_atomic(report_path, report)
        raise RuntimeError(f"La validazione dei dati salariali non e' riuscita. Dettagli in {report_path}.")
    if errors and fail_on_errors:
        write_json_atomic(report_path, report)
        raise RuntimeError(f"{len(errors)} richieste Eurostat non sono riuscite. Dettagli in {report_path}.")

    dashboard_payload = build_dashboard_payload(output, report, selected_geographies)
    report["dashboard_validation"] = validate_dashboard_payload(dashboard_payload)
    dashboard_text = json_payload_text(dashboard_payload, pretty=False)
    report_text = json_payload_text(report)

    write_dataframe_outputs(output, csv_path, json_path, parquet_path)
    write_text_atomic(dashboard_path, dashboard_text)
    write_text_atomic(report_path, report_text)
    return output, report
