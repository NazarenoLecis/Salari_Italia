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
        "name": "ses_hourly_distribution",
        "dataset_id": "earn_ses_hourly",
        "description": "Media, decile 1, mediana e decile 9 delle retribuzioni orarie lorde per sesso.",
        "filters": {
            "nace_r2": "B-S_X_O",
            "isco08": "TOTAL",
            "worktime": "TOTAL",
            "age": "TOTAL",
            "sex": ("T", "M", "F"),
            "indic_se": ("D1_E_EUR", "MED_E_EUR", "D9_E_EUR", "MEAN_E_EUR"),
        },
    },
    {
        "name": "ses_monthly_distribution",
        "dataset_id": "earn_ses_monthly",
        "description": "Media, decile 1, mediana e decile 9 delle retribuzioni mensili lorde per sesso.",
        "filters": {
            "nace_r2": "B-S_X_O",
            "isco08": "TOTAL",
            "worktime": "TOTAL",
            "age": "TOTAL",
            "sex": ("T", "M", "F"),
            "indic_se": ("D1_E_EUR", "MED_E_EUR", "D9_E_EUR", "MEAN_E_EUR"),
        },
    },
    {
        "name": "ses_annual_distribution",
        "dataset_id": "earn_ses_annual",
        "description": "Media, decile 1, mediana e decile 9 delle retribuzioni annuali lorde per sesso.",
        "filters": {
            "nace_r2": "B-S_X_O",
            "isco08": "TOTAL",
            "worktime": "TOTAL",
            "age": "TOTAL",
            "sex": ("T", "M", "F"),
            "indic_se": ("D1_E_EUR", "MED_E_EUR", "D9_E_EUR", "MEAN_E_EUR"),
        },
    },
    {
        "name": "ses_by_age",
        "dataset_id": "earn_ses_hourly",
        "description": "Retribuzione oraria media e mediana per classe di eta' e sesso.",
        "filters": {
            "nace_r2": "B-S_X_O",
            "isco08": "TOTAL",
            "worktime": "TOTAL",
            "sex": ("T", "M", "F"),
            "indic_se": ("MED_E_EUR", "MEAN_E_EUR"),
        },
    },
    {
        "name": "ses_by_occupation",
        "dataset_id": "earn_ses_hourly",
        "description": "Retribuzione oraria media e mediana per professione ISCO-08 e sesso.",
        "filters": {
            "nace_r2": "B-S_X_O",
            "worktime": "TOTAL",
            "age": "TOTAL",
            "sex": ("T", "M", "F"),
            "indic_se": ("MED_E_EUR", "MEAN_E_EUR"),
        },
    },
    {
        "name": "ses_by_sector",
        "dataset_id": "earn_ses_hourly",
        "description": "Retribuzione oraria media e mediana per settore NACE Rev. 2 e sesso.",
        "filters": {
            "isco08": "TOTAL",
            "worktime": "TOTAL",
            "age": "TOTAL",
            "sex": ("T", "M", "F"),
            "indic_se": ("D1_E_EUR", "MED_E_EUR", "D9_E_EUR", "MEAN_E_EUR"),
        },
    },
    {
        "name": "ses_by_working_time",
        "dataset_id": "earn_ses_hourly",
        "description": "Retribuzione oraria media e mediana per regime di orario e sesso.",
        "filters": {
            "nace_r2": "B-S_X_O",
            "isco08": "TOTAL",
            "age": "TOTAL",
            "sex": ("T", "M", "F"),
            "indic_se": ("MED_E_EUR", "MEAN_E_EUR"),
        },
    },
    {
        "name": "ses2022_hourly_by_education",
        "dataset_id": "earn_ses22_16",
        "description": "Retribuzione oraria lorda media per titolo di studio nella SES 2022.",
        "filters": {"sex": ("T", "M", "F"), "indic_se": "ERN", "sizeclas": "GE10", "nace_r2": "B-S_X_O", "unit": "EUR"},
    },
    {
        "name": "ses2022_hourly_by_contract",
        "dataset_id": "earn_ses22_15",
        "description": "Retribuzione oraria lorda media per tipo di contratto nella SES 2022.",
        "filters": {"sex": ("T", "M", "F"), "indic_se": "ERN", "sizeclas": "GE10", "nace_r2": "B-S_X_O", "unit": "EUR"},
    },
    {
        "name": "ses2022_hourly_by_seniority",
        "dataset_id": "earn_ses22_17",
        "description": "Retribuzione oraria lorda media per anzianita' lavorativa nella SES 2022.",
        "filters": {"sex": ("T", "M", "F"), "indic_se": "ERN", "sizeclas": "GE10", "nace_r2": "B-S_X_O", "unit": "EUR"},
    },
    {
        "name": "ses2022_hourly_by_firm_size_occupation",
        "dataset_id": "earn_ses22_18",
        "description": "Retribuzione oraria lorda media per professione e dimensione d'impresa nella SES 2022.",
        "filters": {"sex": ("T", "M", "F"), "indic_se": "ERN", "unit": "EUR"},
    },
    {
        "name": "ses2022_monthly_by_education",
        "dataset_id": "earn_ses22_23",
        "description": "Retribuzione mensile lorda media per titolo di studio nella SES 2022.",
        "filters": {"sex": ("T", "M", "F"), "indic_se": "ERN", "sizeclas": "GE10", "nace_r2": "B-S_X_O", "unit": "EUR"},
    },
    {
        "name": "ses2022_monthly_by_contract",
        "dataset_id": "earn_ses22_22",
        "description": "Retribuzione mensile lorda media per tipo di contratto nella SES 2022.",
        "filters": {"sex": ("T", "M", "F"), "indic_se": "ERN", "sizeclas": "GE10", "nace_r2": "B-S_X_O", "unit": "EUR"},
    },
    {
        "name": "ses2022_annual_by_age_occupation",
        "dataset_id": "earn_ses22_28",
        "description": "Retribuzione annuale lorda media per eta' e professione nella SES 2022.",
        "filters": {"sex": ("T", "M", "F"), "indic_se": "ERN", "sizeclas": "GE10", "unit": "EUR"},
    },
    {
        "name": "ses2022_annual_by_education",
        "dataset_id": "earn_ses22_30",
        "description": "Retribuzione annuale lorda media per titolo di studio nella SES 2022.",
        "filters": {"sex": ("T", "M", "F"), "indic_se": "ERN", "sizeclas": "GE10", "nace_r2": "B-S_X_O", "unit": "EUR"},
    },
    {
        "name": "ses2022_annual_by_contract",
        "dataset_id": "earn_ses22_29",
        "description": "Retribuzione annuale lorda media per tipo di contratto nella SES 2022.",
        "filters": {"sex": ("T", "M", "F"), "indic_se": "ERN", "sizeclas": "GE10", "nace_r2": "B-S_X_O", "unit": "EUR"},
    },
    {
        "name": "low_wage_share",
        "dataset_id": "earn_ses_pub1s",
        "description": "Quota di dipendenti sotto due terzi della mediana nazionale.",
        "filters": {"unit": "PC", "sex": ("T", "M", "F"), "sizeclas": "GE10"},
    },
    {
        "name": "low_wage_share_by_age",
        "dataset_id": "earn_ses_pub1a",
        "description": "Quota di dipendenti a bassa retribuzione per classe di eta'.",
        "filters": {"unit": "PC", "sizeclas": "GE10"},
    },
    {
        "name": "low_wage_share_by_education",
        "dataset_id": "earn_ses_pub1i",
        "description": "Quota di dipendenti a bassa retribuzione per titolo di studio.",
        "filters": {"unit": "PC", "sizeclas": "GE10"},
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
            "unit": "EUR",
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
