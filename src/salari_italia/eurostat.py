from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlencode

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from salari_italia.config import EUROSTAT_BASE_URL

USER_AGENT = "Salari_Italia/0.1 (+https://github.com/NazarenoLecis/Salari_Italia)"


def _ordered_codes(dimension: dict[str, Any]) -> list[str]:
    category = dimension.get("category", {})
    index = category.get("index", {})
    if isinstance(index, list):
        return [str(value) for value in index]
    return [str(code) for code, _ in sorted(index.items(), key=lambda item: item[1])]


def _labels(dimension: dict[str, Any]) -> dict[str, str]:
    labels = dimension.get("category", {}).get("label", {})
    return {str(code): str(label) for code, label in labels.items()}


def _coordinates(position: int, sizes: list[int]) -> list[int]:
    result = [0] * len(sizes)
    remainder = position
    for index in range(len(sizes) - 1, -1, -1):
        size = sizes[index]
        if size <= 0:
            return result
        result[index] = remainder % size
        remainder //= size
    return result


def jsonstat_to_frame(payload: dict[str, Any]) -> pd.DataFrame:
    dimension_ids = [str(value) for value in payload.get("id", [])]
    sizes = [int(value) for value in payload.get("size", [])]
    dimensions = payload.get("dimension", {})
    if not dimension_ids or len(dimension_ids) != len(sizes) or any(size <= 0 for size in sizes):
        return pd.DataFrame()

    codes = {dimension_id: _ordered_codes(dimensions.get(dimension_id, {})) for dimension_id in dimension_ids}
    labels = {dimension_id: _labels(dimensions.get(dimension_id, {})) for dimension_id in dimension_ids}
    raw_values = payload.get("value", {})
    raw_status = payload.get("status", {})

    if isinstance(raw_values, list):
        observations: Iterable[tuple[int, Any]] = enumerate(raw_values)
    else:
        observations = ((int(position), value) for position, value in raw_values.items())

    rows: list[dict[str, Any]] = []
    for position, value in observations:
        if value is None:
            continue
        coordinate = _coordinates(position, sizes)
        row: dict[str, Any] = {"value": value}
        for dimension_id, dimension_position in zip(dimension_ids, coordinate, strict=True):
            dimension_codes = codes[dimension_id]
            if dimension_position >= len(dimension_codes):
                continue
            code = dimension_codes[dimension_position]
            row[dimension_id] = code
            row[f"{dimension_id}_label"] = labels[dimension_id].get(code, code)
        if isinstance(raw_status, list) and position < len(raw_status):
            row["status"] = raw_status[position]
        elif isinstance(raw_status, dict):
            row["status"] = raw_status.get(str(position))
        rows.append(row)

    return pd.DataFrame(rows)


def _session() -> requests.Session:
    retry = Retry(
        total=4,
        connect=4,
        read=4,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def build_query_parameters(filters: dict[str, Any], geographies: tuple[str, ...]) -> list[tuple[str, str]]:
    params: list[tuple[str, str]] = [("format", "JSON"), ("lang", "en")]
    combined = dict(filters)
    combined["geo"] = geographies
    for key, value in combined.items():
        values = value if isinstance(value, (list, tuple, set)) else (value,)
        for item in values:
            params.append((key, str(item)))
    return params


def download_dataset(
    dataset_id: str,
    filters: dict[str, Any],
    geographies: tuple[str, ...],
    raw_output_path: Path | None = None,
    timeout: int = 120,
) -> tuple[dict[str, Any], str]:
    params = build_query_parameters(filters, geographies)
    url = f"{EUROSTAT_BASE_URL}/{dataset_id}"
    response = _session().get(url, params=params, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    if "error" in payload:
        raise RuntimeError(f"Eurostat ha restituito un errore per {dataset_id}: {payload['error']}")
    if raw_output_path is not None:
        raw_output_path.parent.mkdir(parents=True, exist_ok=True)
        raw_output_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return payload, response.url


def readable_request_url(dataset_id: str, filters: dict[str, Any], geographies: tuple[str, ...]) -> str:
    params = build_query_parameters(filters, geographies)
    return f"{EUROSTAT_BASE_URL}/{dataset_id}?{urlencode(params)}"
