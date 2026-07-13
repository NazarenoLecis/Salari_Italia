from __future__ import annotations

import csv
import io
import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from salari_italia.schema import ensure_standard_schema

ISTAT_BASE_URL = "https://esploradati.istat.it/SDMXWS/rest"
DBNOMICS_BASE_URL = "https://api.db.nomics.world/v22"
USER_AGENT = "Salari_Italia/0.1 (+https://github.com/NazarenoLecis/Salari_Italia)"

DIMENSION_CODELISTS = {
    "REF_AREA": "CL_ITTER107",
    "DATA_TYPE": "CL_TIPO_DATO7",
    "SEX": "CL_SEXISTAT1",
    "AGE": "CL_ETA1",
    "EDU_LEV_HIGHEST": "CL_TITOLO_STUDIO",
    "COUNTRY_BIRTH": "CL_ISO",
    "CITIZENSHIP": "CL_ISO",
    "TYPE_OF_CONTRACT": "CL_CARATT_OCC",
    "FULL_PART_TIME": "CL_REGIME_ORARIO",
    "CONTARCTUAL_OCCUPATION": "CL_PROFILO_PROF",
    "EMPLOYEE_TENURE": "CL_ETA1",
    "PAID_DAYS": "CL_DURATA",
    "ECON_ACTIVITY_NACE_2007": "CL_ATECO_2007",
    "EMPLOYESS_CLASS": "CL_CLLVT",
}

SEX_MAP = {"1": "M", "M": "M", "2": "F", "F": "F", "9": "T", "T": "T"}

LOCAL_LABELS_IT = {
    "DATA_TYPE": {
        "HOUWAG_ENTEMP_AV_MI": "Retribuzione oraria lorda media",
        "HOUWAG_ENTEMP_FIRD_MI": "Primo decile della retribuzione oraria lorda",
        "HOUWAG_ENTEMP_MED_MI": "Retribuzione oraria lorda mediana",
        "HOUWAG_ENTEMP_NIND_MI": "Nono decile della retribuzione oraria lorda",
    },
    "SEX": {"1": "Maschi", "M": "Maschi", "2": "Femmine", "F": "Femmine", "9": "Totale", "T": "Totale"},
    "AGE": {
        "TOTAL": "Totale",
        "Y15-24": "15-24 anni",
        "Y25-34": "25-34 anni",
        "Y35-44": "35-44 anni",
        "Y45-54": "45-54 anni",
        "Y55-64": "55-64 anni",
        "Y_GE65": "65 anni e oltre",
    },
    "EDU_LEV_HIGHEST": {
        "7": "Diploma di istruzione secondaria superiore",
        "11": "Laurea o titolo terziario",
        "13": "Nessun titolo, licenza elementare o media",
        "99": "Totale",
        "TOTAL": "Totale",
    },
    "COUNTRY_BIRTH": {"WORLD": "Totale", "IT": "Italia", "WRL_X_ITA": "Estero"},
    "CITIZENSHIP": {"WORLD": "Totale", "IT": "Italia", "WRL_X_ITA": "Estero"},
    "TYPE_OF_CONTRACT": {
        "1": "Tempo determinato",
        "2": "Tempo indeterminato",
        "3": "Stagionale",
        "9": "Totale",
    },
    "FULL_PART_TIME": {
        "1": "Tempo pieno",
        "2": "Tempo parziale",
        "3": "Part-time orizzontale",
        "4": "Part-time verticale",
        "5": "Part-time misto",
        "6": "Part-time fino al 50%",
        "7": "Part-time oltre il 50%",
        "8": "Senza preferenze",
        "9": "Totale",
    },
    "CONTARCTUAL_OCCUPATION": {
        "1": "Dirigenti e impiegati",
        "2": "Dirigenti",
        "3": "Quadri",
        "4": "Impiegati",
        "5": "Operai e apprendisti",
        "6": "Operai",
        "7": "Apprendisti",
        "10": "Dipendenti esclusi dirigenti",
        "23": "Quadri e impiegati",
        "35": "Dirigenti e quadri",
        "99": "Totale",
    },
    "EMPLOYEE_TENURE": {"TOTAL": "Totale"},
    "PAID_DAYS": {
        "TOTAL": "Totale",
        "D0-364": "0-364 giorni",
        "D_UN90": "Fino a 90 giornate retribuite",
        "D_GE91": "91 giornate retribuite e oltre",
        "D1-3": "1-3 giorni",
        "D4-30": "4-30 giorni",
        "D31-60": "31-60 giorni",
        "D61-90": "61-90 giorni",
        "D91-180": "91-180 giorni",
        "D181-270": "181-270 giorni",
        "D271-364": "271-364 giorni",
    },
    "ECON_ACTIVITY_NACE_2007": {
        "0010": "Totale",
        "0011": "Totale industria",
        "0012": "Totale servizi",
        "B": "Estrazione di minerali",
        "C": "Attivita' manifatturiere",
        "D": "Fornitura di energia elettrica, gas, vapore e aria condizionata",
        "E": "Fornitura di acqua; reti fognarie, gestione rifiuti e risanamento",
        "F": "Costruzioni",
        "G": "Commercio all'ingrosso e al dettaglio; riparazione di autoveicoli e motocicli",
        "H": "Trasporto e magazzinaggio",
        "I": "Attivita' dei servizi di alloggio e ristorazione",
        "J": "Servizi di informazione e comunicazione",
        "K": "Attivita' finanziarie e assicurative",
        "L": "Attivita' immobiliari",
        "M": "Attivita' professionali, scientifiche e tecniche",
        "N": "Noleggio, agenzie di viaggio, servizi di supporto alle imprese",
        "O": "Amministrazione pubblica e difesa; assicurazione sociale obbligatoria",
        "P": "Istruzione",
        "Q": "Sanita' e assistenza sociale",
        "R": "Attivita' artistiche, sportive, di intrattenimento e divertimento",
        "S": "Altre attivita' di servizi",
        "T": "Attivita' di famiglie e convivenze come datori di lavoro",
        "U": "Organizzazioni e organismi extraterritoriali",
    },
    "EMPLOYESS_CLASS": {
        "TOTAL": "Totale",
        "W0_9": "0-9 addetti",
        "W10_49": "10-49 addetti",
        "W50_249": "50-249 addetti",
        "W_GE250": "250 addetti e oltre",
        "W250_499": "250-499 addetti",
        "W500_999": "500-999 addetti",
        "W_GE1000": "1.000 addetti e oltre",
    },
}

ITALIAN_TRANSLATIONS = {
    "average": "media",
    "females": "femmine",
    "full-time": "tempo pieno",
    "males": "maschi",
    "median": "mediana",
    "part-time": "tempo parziale",
    "permanent employees": "tempo indeterminato",
    "temporary employees": "tempo determinato",
    "total": "totale",
}


def istat_session() -> requests.Session:
    retry = Retry(
        total=4,
        connect=4,
        read=4,
        backoff_factor=1.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def read_istat_csv(text: str) -> pd.DataFrame:
    return pd.DataFrame(list(csv.DictReader(io.StringIO(text))))


def download_istat_csv(
    flow_id: str,
    key: str,
    start_period: str | None = None,
    raw_output_path: Path | None = None,
    timeout: int = 120,
) -> tuple[pd.DataFrame, str]:
    params = {}
    if start_period:
        params["startPeriod"] = start_period
    query = f"?{urlencode(params)}" if params else ""
    url = f"{ISTAT_BASE_URL}/data/{flow_id}/{key}{query}"
    response = istat_session().get(url, headers={"Accept": "text/csv"}, timeout=timeout)
    response.raise_for_status()
    text = response.text
    if raw_output_path is not None:
        raw_output_path.parent.mkdir(parents=True, exist_ok=True)
        raw_output_path.write_text(text, encoding="utf-8")
    return read_istat_csv(text), response.url


def download_istat_structure(
    flow_id: str,
    raw_output_path: Path | None = None,
    timeout: int = 180,
) -> tuple[dict[str, dict[str, str]], str]:
    url = f"{ISTAT_BASE_URL}/dataflow/IT1/{flow_id}/1.0/?detail=Full&references=Descendants"
    response = istat_session().get(url, timeout=timeout)
    response.raise_for_status()
    text = response.text
    if raw_output_path is not None:
        raw_output_path.parent.mkdir(parents=True, exist_ok=True)
        raw_output_path.write_text(text, encoding="utf-8")
    return parse_codelists(text), response.url


def dbnomics_dimensions(dimensions: dict[str, Any]) -> str:
    return json.dumps({key: list(value) if isinstance(value, tuple | list | set) else [value] for key, value in dimensions.items()})


def dbnomics_codelists(dataset: dict[str, Any]) -> dict[str, dict[str, str]]:
    labels = dataset.get("dimensions_values_labels") or {}
    output: dict[str, dict[str, str]] = {}
    for dimension, codelist_id in DIMENSION_CODELISTS.items():
        values = labels.get(dimension)
        if isinstance(values, dict):
            output[codelist_id] = {str(key): str(value) for key, value in values.items()}
    return output


def use_raw_cache() -> bool:
    return os.getenv("SALARI_USE_RAW_CACHE", "").strip().lower() in {"1", "true", "yes"}


def download_istat_series(
    flow_id: str,
    dimensions: dict[str, Any],
    start_period: str | None = None,
    raw_output_path: Path | None = None,
    timeout: int = 120,
) -> tuple[pd.DataFrame, str, dict[str, dict[str, str]]]:
    url = f"{DBNOMICS_BASE_URL}/series/ISTAT/{flow_id}"
    if raw_output_path is not None and raw_output_path.exists() and use_raw_cache():
        cached = json.loads(raw_output_path.read_text(encoding="utf-8"))
        dataset = cached.get("dataset") or {}
        docs = cached.get("series") or []
        source_url = f"{url}?cached=1"
        rows: list[dict[str, Any]] = []
        start_year = int(start_period) if start_period and str(start_period).isdigit() else None
        for series_doc in docs:
            series_dimensions = series_doc.get("dimensions") or {}
            periods = series_doc.get("period") or []
            values = series_doc.get("value") or []
            statuses = series_doc.get("status") or []
            for index, period in enumerate(periods):
                year = int(period) if str(period).isdigit() else None
                if start_year is not None and year is not None and year < start_year:
                    continue
                row = dict(series_dimensions)
                row["TIME_PERIOD"] = period
                row["OBS_VALUE"] = values[index] if index < len(values) else None
                row["OBS_STATUS"] = statuses[index] if index < len(statuses) else None
                row["UNIT_MEAS"] = "EUR"
                rows.append(row)
        return pd.DataFrame(rows), source_url, dbnomics_codelists(dataset)

    offset = 0
    limit = 250
    docs: list[dict[str, Any]] = []
    dataset: dict[str, Any] = {}
    source_url = url
    while True:
        params = {
            "dimensions": dbnomics_dimensions(dimensions),
            "observations": "1",
            "limit": str(limit),
            "offset": str(offset),
        }
        response = istat_session().get(url, params=params, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
        if not dataset:
            dataset = payload.get("dataset") or {}
            source_url = response.url
        series = payload.get("series") or {}
        batch = series.get("docs") or []
        docs.extend(batch)
        if offset + len(batch) >= int(series.get("num_found") or 0) or not batch:
            break
        offset += len(batch)

    if raw_output_path is not None:
        raw_output_path.parent.mkdir(parents=True, exist_ok=True)
        raw_output_path.write_text(
            json.dumps({"dataset": dataset, "series": docs}, ensure_ascii=False),
            encoding="utf-8",
        )

    rows: list[dict[str, Any]] = []
    start_year = int(start_period) if start_period and str(start_period).isdigit() else None
    for series_doc in docs:
        series_dimensions = series_doc.get("dimensions") or {}
        periods = series_doc.get("period") or []
        values = series_doc.get("value") or []
        statuses = series_doc.get("status") or []
        for index, period in enumerate(periods):
            year = int(period) if str(period).isdigit() else None
            if start_year is not None and year is not None and year < start_year:
                continue
            value = values[index] if index < len(values) else None
            row = dict(series_dimensions)
            row["TIME_PERIOD"] = period
            row["OBS_VALUE"] = value
            row["OBS_STATUS"] = statuses[index] if index < len(statuses) else None
            row["UNIT_MEAS"] = "EUR"
            rows.append(row)
    return pd.DataFrame(rows), source_url, dbnomics_codelists(dataset)


def parse_codelists(xml_text: str) -> dict[str, dict[str, str]]:
    namespace = {
        "structure": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure",
        "common": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common",
    }
    root = ET.fromstring(xml_text)
    output: dict[str, dict[str, str]] = {}
    for codelist in root.findall(".//structure:Codelist", namespace):
        codelist_id = str(codelist.attrib.get("id"))
        values: dict[str, str] = {}
        for code in codelist.findall("structure:Code", namespace):
            code_id = str(code.attrib.get("id"))
            label = code_id
            for name in code.findall("common:Name", namespace):
                language = name.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
                if language == "it" and name.text:
                    label = name.text
                    break
                if name.text:
                    label = name.text
            values[code_id] = label
        output[codelist_id] = values
    return output


def label_for(codelists: dict[str, dict[str, str]], dimension: str, code: Any) -> str | None:
    if code is None or pd.isna(code) or code == "":
        return None
    local_label = LOCAL_LABELS_IT.get(dimension, {}).get(str(code))
    if local_label:
        return local_label
    codelist_id = DIMENSION_CODELISTS.get(dimension)
    if not codelist_id:
        return str(code)
    label = codelists.get(codelist_id, {}).get(str(code), str(code))
    return ITALIAN_TRANSLATIONS.get(str(label).lower(), label)


def istat_measure(row: pd.Series | dict[str, Any], data_type_label: str | None) -> tuple[str, int | None]:
    data_type = str(row.get("DATA_TYPE") or "").lower()
    label = str(data_type_label or "").lower()
    if "first decile" in label or "primo decile" in label or "fird" in data_type or "1dec" in data_type:
        return "percentile", 10
    if "ninth decile" in label or "nono decile" in label or "nind" in data_type or "9dec" in data_type:
        return "percentile", 90
    if "mediana" in label or "median" in label or "_med_" in data_type:
        return "median", 50
    return "mean", None


def geography_type(code: Any) -> str:
    text = str(code or "")
    if text == "IT":
        return "country"
    if len(text) >= 5:
        return "province_or_metropolitan_city"
    if len(text) == 4:
        return "region_or_autonomous_province"
    return "istat_reference_area"


def harmonise_istat(
    raw: pd.DataFrame,
    flow_id: str,
    request_name: str,
    source_url: str,
    codelists: dict[str, dict[str, str]],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in raw.to_dict(orient="records"):
        try:
            value = float(row.get("OBS_VALUE"))
        except (TypeError, ValueError):
            continue
        if pd.isna(value):
            continue
        year_raw = row.get("TIME_PERIOD")
        year = int(year_raw) if str(year_raw).isdigit() else year_raw
        data_type_label = label_for(codelists, "DATA_TYPE", row.get("DATA_TYPE"))
        statistic, percentile = istat_measure(row, data_type_label)
        sex = SEX_MAP.get(str(row.get("SEX")), row.get("SEX"))
        sector = row.get("ECON_ACTIVITY_NACE_2007")
        rows.append(
            {
                "source": "ISTAT",
                "dataset": flow_id,
                "source_request": request_name,
                "year": year,
                "geography_type": geography_type(row.get("REF_AREA")),
                "geography_code": row.get("REF_AREA"),
                "geography_name": label_for(codelists, "REF_AREA", row.get("REF_AREA")),
                "geography_basis": "istat_racli_reference_area",
                "sex": sex,
                "sex_label": label_for(codelists, "SEX", row.get("SEX")),
                "age_class": row.get("AGE"),
                "age_label": label_for(codelists, "AGE", row.get("AGE")),
                "education": row.get("EDU_LEV_HIGHEST"),
                "education_label": label_for(codelists, "EDU_LEV_HIGHEST", row.get("EDU_LEV_HIGHEST")),
                "occupation": None,
                "occupation_label": None,
                "contractual_occupation": row.get("CONTARCTUAL_OCCUPATION"),
                "contractual_occupation_label": label_for(
                    codelists, "CONTARCTUAL_OCCUPATION", row.get("CONTARCTUAL_OCCUPATION")
                ),
                "employment_status": "employee_private_sector",
                "contract_type": row.get("TYPE_OF_CONTRACT"),
                "contract_type_label": label_for(codelists, "TYPE_OF_CONTRACT", row.get("TYPE_OF_CONTRACT")),
                "collective_pay_agreement": None,
                "collective_pay_agreement_label": None,
                "working_time": row.get("FULL_PART_TIME"),
                "working_time_label": label_for(codelists, "FULL_PART_TIME", row.get("FULL_PART_TIME")),
                "seniority": row.get("EMPLOYEE_TENURE"),
                "seniority_label": label_for(codelists, "EMPLOYEE_TENURE", row.get("EMPLOYEE_TENURE")),
                "paid_days": row.get("PAID_DAYS"),
                "paid_days_label": label_for(codelists, "PAID_DAYS", row.get("PAID_DAYS")),
                "sector": sector,
                "sector_label": label_for(codelists, "ECON_ACTIVITY_NACE_2007", sector),
                "firm_size": row.get("EMPLOYESS_CLASS"),
                "firm_size_label": label_for(codelists, "EMPLOYESS_CLASS", row.get("EMPLOYESS_CLASS")),
                "public_private": "private_sector",
                "citizenship": row.get("CITIZENSHIP"),
                "citizenship_label": label_for(codelists, "CITIZENSHIP", row.get("CITIZENSHIP")),
                "country_birth": row.get("COUNTRY_BIRTH"),
                "country_birth_label": label_for(codelists, "COUNTRY_BIRTH", row.get("COUNTRY_BIRTH")),
                "pay_concept": "gross_earnings",
                "pay_period": "hourly",
                "statistic": statistic,
                "percentile": percentile,
                "measure_code": row.get("DATA_TYPE"),
                "value": value,
                "unit": row.get("UNIT_MEAS") or "EUR",
                "unit_label": "Euro per ora",
                "population": None,
                "sample_size": None,
                "quality_flag": row.get("OBS_STATUS"),
                "source_url": source_url,
                "download_timestamp": None,
                "dimensions_json": json.dumps(row, ensure_ascii=False, sort_keys=True),
            }
        )
    return ensure_standard_schema(pd.DataFrame(rows))
