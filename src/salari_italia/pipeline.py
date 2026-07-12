from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from salari_italia.config import (
    EUROSTAT_REQUESTS,
    ISTAT_REQUESTS,
    ISTAT_STRUCTURE_FLOW_ID,
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
from salari_italia.istat import download_istat_csv, download_istat_series, download_istat_structure, harmonise_istat, use_raw_cache
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


def write_dataframe_outputs(
    output: pd.DataFrame,
    csv_path: Path,
    json_path: Path,
    parquet_path: Path,
    parquet_output: pd.DataFrame | None = None,
) -> None:
    for path in (csv_path, json_path, parquet_path):
        path.parent.mkdir(parents=True, exist_ok=True)
    csv_temp = csv_path.with_name(csv_path.name + ".tmp")
    json_temp = json_path.with_name(json_path.name + ".tmp")
    parquet_temp = parquet_path.with_name(parquet_path.name + ".tmp")
    output.to_csv(csv_temp, index=False)
    output.to_json(json_temp, orient="records", force_ascii=False)
    (parquet_output if parquet_output is not None else output).to_parquet(parquet_temp, index=False)
    csv_temp.replace(csv_path)
    json_temp.replace(json_path)
    parquet_temp.replace(parquet_path)


def run_pipeline(
    geographies: tuple[str, ...] | None = None,
    requests_config: Iterable[dict[str, Any]] = EUROSTAT_REQUESTS,
    istat_requests_config: Iterable[dict[str, Any]] = ISTAT_REQUESTS,
    fail_on_errors: bool = True,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    ensure_data_directories()
    selected_geographies = geographies or requested_geographies()
    frames: list[pd.DataFrame] = []
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
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

    istat_frames: list[pd.DataFrame] = []
    codelists: dict[str, dict[str, str]] = {}
    structure_url = ""
    if use_raw_cache():
        warnings.append(
            {
                "request": "istat_structure",
                "dataset": ISTAT_STRUCTURE_FLOW_ID,
                "warning": "Struttura ISTAT ufficiale saltata per SALARI_USE_RAW_CACHE=1.",
            }
        )
    else:
        try:
            codelists, structure_url = download_istat_structure(
                flow_id=ISTAT_STRUCTURE_FLOW_ID,
                raw_output_path=RAW_DIR / "istat_racli_structure.xml",
                timeout=30,
            )
        except Exception as exc:
            warnings.append({"request": "istat_structure", "dataset": ISTAT_STRUCTURE_FLOW_ID, "warning": str(exc)})

    for request_config in istat_requests_config:
        name = str(request_config["name"])
        flow_id = str(request_config["flow_id"])
        raw_path = RAW_DIR / f"{name}.json" if request_config.get("dimensions") else RAW_DIR / f"{name}.csv"
        try:
            if request_config.get("dimensions"):
                raw, source_url, request_codelists = download_istat_series(
                    flow_id=flow_id,
                    dimensions=dict(request_config["dimensions"]),
                    start_period=str(request_config.get("start_period") or ""),
                    raw_output_path=raw_path,
                )
                merged_codelists = dict(request_codelists)
                merged_codelists.update(codelists)
                active_codelists = merged_codelists
            else:
                raw, source_url = download_istat_csv(
                    flow_id=flow_id,
                    key=str(request_config["key"]),
                    start_period=str(request_config.get("start_period") or ""),
                    raw_output_path=raw_path,
                )
                active_codelists = codelists
            if raw.empty:
                raise RuntimeError("La risposta ISTAT non contiene osservazioni.")
            frame = harmonise_istat(
                raw=raw,
                flow_id=flow_id,
                request_name=name,
                source_url=source_url or structure_url,
                codelists=active_codelists,
            )
            istat_frames.append(frame)
            frames.append(frame)
        except Exception as exc:
            errors.append({"request": name, "dataset": flow_id, "error": str(exc)})

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
        "successful_eurostat_requests": len(frames) - len(istat_frames),
        "successful_istat_requests": len(istat_frames),
        "errors": errors,
        "warnings": warnings,
        "validation": validation,
        "outputs": {
            "csv": str(csv_path),
            "json": str(json_path),
            "parquet": str(parquet_path),
            "dashboard_json": str(dashboard_path),
            "csv_json_scope": "Estratto Eurostat tracciabile; ISTAT RACLI completo nel payload dashboard compatto e nel Parquet locale.",
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

    csv_json_output = output[output["source"].eq("Eurostat")].copy()
    write_dataframe_outputs(csv_json_output, csv_path, json_path, parquet_path, parquet_output=output)
    write_text_atomic(dashboard_path, dashboard_text)
    write_text_atomic(report_path, report_text)
    return output, report
