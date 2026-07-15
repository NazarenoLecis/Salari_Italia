from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERMEDIATE_DIR = DATA_DIR / "intermediate"
PROCESSED_DIR = DATA_DIR / "processed"
VALIDATION_DIR = DATA_DIR / "validation"

DEFAULT_GEOGRAPHIES = (
    "EU27_2020",
    "AT",
    "BE",
    "BG",
    "CH",
    "CY",
    "CZ",
    "DE",
    "DK",
    "EE",
    "EL",
    "ES",
    "FI",
    "FR",
    "HR",
    "HU",
    "IE",
    "IS",
    "IT",
    "LT",
    "LU",
    "LV",
    "MT",
    "NL",
    "NO",
    "PL",
    "PT",
    "RO",
    "SE",
    "SI",
    "SK",
    "UK",
)

EUROSTAT_BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
OECD_BASE_URL = "https://sdmx.oecd.org/public/rest/data"

OECD_REQUESTS = (
    {
        "name": "oecd_average_annual_wages",
        "dataset_id": "OECD.ELS.SAE,DSD_EARNINGS@AV_AN_WAGE",
        "description": "Salario medio annuo per dipendente equivalente full-time nell'economia totale, dollari PPP.",
        "filters": {
            "MEASURE": "WG",
            "UNIT_MEASURE": "USD_PPP",
            "PAY_PERIOD": "A",
            "PRICE_BASE": "Q",
            "AGGREGATION_OPERATION": "MEAN",
            "SEX": "_Z",
        },
        "start_period": "2000",
    },
)

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
        "description": (
            "Media, decile 1, mediana e decile 9 delle retribuzioni mensili lorde "
            "per sesso e regime di orario."
        ),
        "filters": {
            "nace_r2": "B-S_X_O",
            "isco08": "TOTAL",
            "worktime": ("TOTAL", "TOT_FTE", "FT", "PT", "PT_FTE"),
            "age": "TOTAL",
            "sex": ("T", "M", "F"),
            "indic_se": ("D1_E_EUR", "MED_E_EUR", "D9_E_EUR", "MEAN_E_EUR"),
        },
    },
    {
        "name": "ses_annual_distribution",
        "dataset_id": "earn_ses_annual",
        "description": (
            "Media, decile 1, mediana e decile 9 delle retribuzioni annuali lorde "
            "per sesso e regime di orario."
        ),
        "filters": {
            "nace_r2": "B-S_X_O",
            "isco08": "TOTAL",
            "worktime": ("TOTAL", "TOT_FTE", "FT", "PT", "PT_FTE"),
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

ISTAT_STRUCTURE_FLOW_ID = "533_957_DF_DCSC_RACLI_23"
ISTAT_WAGE_DATA_TYPES = (
    "HOUWAG_ENTEMP_AV_MI",
    "HOUWAG_ENTEMP_FIRD_MI",
    "HOUWAG_ENTEMP_MED_MI",
    "HOUWAG_ENTEMP_NIND_MI",
)

ISTAT_REQUESTS = (
    {
        "name": "istat_racli_sector_gender",
        "flow_id": "533_957_DF_DCSC_RACLI_17",
        "description": "Retribuzione oraria dei dipendenti privati per sesso e settore Ateco a due cifre.",
        "dimensions": {"DATA_TYPE": ISTAT_WAGE_DATA_TYPES, "REF_AREA": ("IT",)},
        "start_period": "2014",
    },
    {
        "name": "istat_racli_sector_age",
        "flow_id": "533_957_DF_DCSC_RACLI_18",
        "description": "Retribuzione oraria dei dipendenti privati per eta' e settore Ateco a due cifre.",
        "dimensions": {"DATA_TYPE": ISTAT_WAGE_DATA_TYPES, "REF_AREA": ("IT",)},
        "start_period": "2014",
    },
    {
        "name": "istat_racli_sector_country_birth",
        "flow_id": "533_957_DF_DCSC_RACLI_19",
        "description": "Retribuzione oraria dei dipendenti privati per paese di nascita e settore Ateco a due cifre.",
        "dimensions": {"DATA_TYPE": ISTAT_WAGE_DATA_TYPES, "REF_AREA": ("IT",)},
        "start_period": "2014",
    },
    {
        "name": "istat_racli_sector_education",
        "flow_id": "533_957_DF_DCSC_RACLI_20",
        "description": "Retribuzione oraria dei dipendenti privati per titolo di studio e settore Ateco a due cifre.",
        "dimensions": {"DATA_TYPE": ISTAT_WAGE_DATA_TYPES, "REF_AREA": ("IT",)},
        "start_period": "2014",
    },
    {
        "name": "istat_racli_sector_contract",
        "flow_id": "533_957_DF_DCSC_RACLI_21",
        "description": "Retribuzione oraria dei dipendenti privati per contratto e settore Ateco a due cifre.",
        "dimensions": {"DATA_TYPE": ISTAT_WAGE_DATA_TYPES, "REF_AREA": ("IT",)},
        "start_period": "2014",
    },
    {
        "name": "istat_racli_sector_working_time",
        "flow_id": "533_957_DF_DCSC_RACLI_22",
        "description": "Retribuzione oraria dei dipendenti privati per regime orario e settore Ateco a due cifre.",
        "dimensions": {"DATA_TYPE": ISTAT_WAGE_DATA_TYPES, "REF_AREA": ("IT",)},
        "start_period": "2014",
    },
    {
        "name": "istat_racli_sector_firm_size",
        "flow_id": "533_957_DF_DCSC_RACLI_23",
        "description": "Retribuzione oraria dei dipendenti privati per dimensione d'impresa e settore Ateco a due cifre.",
        "dimensions": {"DATA_TYPE": ISTAT_WAGE_DATA_TYPES, "REF_AREA": ("IT",)},
        "start_period": "2014",
    },
    {
        "name": "istat_racli_sector_qualification",
        "flow_id": "533_957_DF_DCSC_RACLI_24",
        "description": "Retribuzione oraria dei dipendenti privati per qualifica contrattuale e settore Ateco a due cifre.",
        "dimensions": {"DATA_TYPE": ISTAT_WAGE_DATA_TYPES, "REF_AREA": ("IT",)},
        "start_period": "2014",
    },
    {
        "name": "istat_racli_sector_paid_days",
        "flow_id": "533_957_DF_DCSC_RACLI_25",
        "description": "Retribuzione oraria dei dipendenti privati per giornate retribuite e settore Ateco a due cifre.",
        "dimensions": {"DATA_TYPE": ISTAT_WAGE_DATA_TYPES, "REF_AREA": ("IT",)},
        "start_period": "2014",
    },
    {
        "name": "istat_racli_province_gender",
        "flow_id": "533_957_DF_DCSC_RACLI_8",
        "description": "Retribuzione oraria dei dipendenti privati per sesso e territorio provinciale.",
        "dimensions": {"DATA_TYPE": ISTAT_WAGE_DATA_TYPES},
        "start_period": "2014",
    },
    {
        "name": "istat_racli_province_age",
        "flow_id": "533_957_DF_DCSC_RACLI_9",
        "description": "Retribuzione oraria dei dipendenti privati per eta' e territorio provinciale.",
        "dimensions": {"DATA_TYPE": ISTAT_WAGE_DATA_TYPES},
        "start_period": "2014",
    },
    {
        "name": "istat_racli_province_country_birth",
        "flow_id": "533_957_DF_DCSC_RACLI_10",
        "description": "Retribuzione oraria dei dipendenti privati per paese di nascita e territorio provinciale.",
        "dimensions": {"DATA_TYPE": ISTAT_WAGE_DATA_TYPES},
        "start_period": "2014",
    },
    {
        "name": "istat_racli_province_education",
        "flow_id": "533_957_DF_DCSC_RACLI_11",
        "description": "Retribuzione oraria dei dipendenti privati per titolo di studio e territorio provinciale.",
        "dimensions": {"DATA_TYPE": ISTAT_WAGE_DATA_TYPES},
        "start_period": "2014",
    },
    {
        "name": "istat_racli_province_contract",
        "flow_id": "533_957_DF_DCSC_RACLI_12",
        "description": "Retribuzione oraria dei dipendenti privati per contratto e territorio provinciale.",
        "dimensions": {"DATA_TYPE": ISTAT_WAGE_DATA_TYPES},
        "start_period": "2014",
    },
    {
        "name": "istat_racli_province_working_time",
        "flow_id": "533_957_DF_DCSC_RACLI_13",
        "description": "Retribuzione oraria dei dipendenti privati per regime orario e territorio provinciale.",
        "dimensions": {"DATA_TYPE": ISTAT_WAGE_DATA_TYPES},
        "start_period": "2014",
    },
    {
        "name": "istat_racli_province_firm_size",
        "flow_id": "533_957_DF_DCSC_RACLI_14",
        "description": "Retribuzione oraria dei dipendenti privati per dimensione d'impresa e territorio provinciale.",
        "dimensions": {"DATA_TYPE": ISTAT_WAGE_DATA_TYPES},
        "start_period": "2014",
    },
    {
        "name": "istat_racli_province_qualification",
        "flow_id": "533_957_DF_DCSC_RACLI_15",
        "description": "Retribuzione oraria dei dipendenti privati per qualifica contrattuale e territorio provinciale.",
        "dimensions": {"DATA_TYPE": ISTAT_WAGE_DATA_TYPES},
        "start_period": "2014",
    },
    {
        "name": "istat_racli_province_paid_days",
        "flow_id": "533_957_DF_DCSC_RACLI_16",
        "description": "Retribuzione oraria dei dipendenti privati per giornate retribuite e territorio provinciale.",
        "dimensions": {"DATA_TYPE": ISTAT_WAGE_DATA_TYPES},
        "start_period": "2014",
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
