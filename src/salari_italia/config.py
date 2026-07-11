from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERMEDIATE_DIR = DATA_DIR / "intermediate"
PROCESSED_DIR = DATA_DIR / "processed"
VALIDATION_DIR = DATA_DIR / "validation"

DEFAULT_GEOGRAPHIES = ("IT", "DE", "FR", "ES", "NL", "EU27_2020")

EUROSTAT_BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

EUROSTAT_REQUESTS = (
    {
        "name": "ses_total_distribution",
        "dataset_id": "earn_ses_hourly",
        "description": "Decile 1, mediana e decile 9 delle retribuzioni orarie lorde.",
        "filters": {
            "nace_r2": "B-S_X_O",
            "isco08": "TOTAL",
            "worktime": "TOTAL",
            "age": "TOTAL",
            "sex": "T",
            "indic_se": ("D1_E_EUR", "MED_E_EUR", "D9_E_EUR"),
        },
    },
    {
        "name": "ses_by_sex",
        "dataset_id": "earn_ses_hourly",
        "description": "Retribuzione oraria mediana per sesso.",
        "filters": {
            "nace_r2": "B-S_X_O",
            "isco08": "TOTAL",
            "worktime": "TOTAL",
            "age": "TOTAL",
            "sex": ("M", "F"),
            "indic_se": "MED_E_EUR",
        },
    },
    {
        "name": "ses_by_age",
        "dataset_id": "earn_ses_hourly",
        "description": "Retribuzione oraria mediana per classe di età.",
        "filters": {
            "nace_r2": "B-S_X_O",
            "isco08": "TOTAL",
            "worktime": "TOTAL",
            "sex": "T",
            "indic_se": "MED_E_EUR",
        },
    },
    {
        "name": "ses_by_occupation",
        "dataset_id": "earn_ses_hourly",
        "description": "Retribuzione oraria mediana per professione ISCO-08.",
        "filters": {
            "nace_r2": "B-S_X_O",
            "worktime": "TOTAL",
            "age": "TOTAL",
            "sex": "T",
            "indic_se": "MED_E_EUR",
        },
    },
    {
        "name": "ses_by_sector",
        "dataset_id": "earn_ses_hourly",
        "description": "Retribuzione oraria mediana per settore NACE Rev. 2.",
        "filters": {
            "isco08": "TOTAL",
            "worktime": "TOTAL",
            "age": "TOTAL",
            "sex": "T",
            "indic_se": "MED_E_EUR",
        },
    },
    {
        "name": "ses_by_working_time",
        "dataset_id": "earn_ses_hourly",
        "description": "Retribuzione oraria mediana per regime di orario.",
        "filters": {
            "nace_r2": "B-S_X_O",
            "isco08": "TOTAL",
            "age": "TOTAL",
            "sex": "T",
            "indic_se": "MED_E_EUR",
        },
    },
    {
        "name": "low_wage_share",
        "dataset_id": "earn_ses_pub1s",
        "description": "Quota di dipendenti sotto due terzi della mediana nazionale.",
        "filters": {"sex": ("T", "M", "F"), "sizeclas": "GE10"},
    },
    {
        "name": "gender_pay_gap",
        "dataset_id": "earn_gr_gpgr2",
        "description": "Divario retributivo di genere non corretto.",
        "filters": {"nace_r2": "B-S_X_O", "unit": "PC"},
    },
    {
        "name": "labour_cost_levels",
        "dataset_id": "lc_lci_lev",
        "description": "Costo orario del lavoro per settore.",
        "filters": {
            "currency": "EUR",
            "lcstruct": "D1_D4_MD5",
            "nace_r2": ("B-S_X_O", "C", "F", "G-J", "K-N"),
        },
    },
)


def requested_geographies() -> tuple[str, ...]:
    raw = os.getenv("SALARI_GEOGRAPHIES", "")
    if not raw.strip():
        return DEFAULT_GEOGRAPHIES
    values = tuple(value.strip() for value in raw.split(",") if value.strip())
    return values or DEFAULT_GEOGRAPHIES


def ensure_data_directories() -> None:
    for path in (RAW_DIR, INTERMEDIATE_DIR, PROCESSED_DIR, VALIDATION_DIR):
        path.mkdir(parents=True, exist_ok=True)
