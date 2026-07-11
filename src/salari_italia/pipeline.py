from __future__ import annotations

import json
from datetime import UTC, datetime
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
from salari_italia.eurostat import download_dataset, jsonstat_to_frame
from salari_italia.harmonise import harmonise_eurostat
from salari_italia.indicators import build_percentile_ratios
from salari_italia.schema import empty_standard_frame, ensure_standard_schema
from salari_italia.validation import validate_dataset


def run_pipeline(
    geographies: tuple[str, ...] | None = None,
    requests_config: Iterable[dict[str, Any]] = EUROSTAT_REQUESTS,
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
    output.to_csv(csv_path, index=False)
    output.to_json(json_path, orient="records", force_ascii=False)
    output.to_parquet(parquet_path, index=False)

    validation = validate_dataset(output)
    report = {
        "started_at": started_at,
        "completed_at": datetime.now(UTC).isoformat(),
        "geographies": list(selected_geographies),
        "successful_requests": len(frames),
        "failed_requests": len(errors),
        "errors": errors,
        "validation": validation,
        "outputs": {"csv": str(csv_path), "json": str(json_path), "parquet": str(parquet_path)},
    }
    report_path = VALIDATION_DIR / "pipeline_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if not frames:
        raise RuntimeError(f"Nessuna fonte ha restituito dati. Dettagli in {report_path}.")
    return output, report
