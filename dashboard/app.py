from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PARQUET = PROJECT_ROOT / "data" / "processed" / "salari_eurostat.parquet"
DEFAULT_CSV = PROJECT_ROOT / "data" / "processed" / "salari_eurostat.csv"

st.set_page_config(page_title="Salari Italia", layout="wide")
st.title("Salari Italia")
st.caption("Distribuzione delle retribuzioni, differenze tra gruppi e copertura delle fonti.")


def load_data() -> pd.DataFrame:
    custom_path = os.getenv("SALARI_DATA_PATH")
    if custom_path:
        path = Path(custom_path)
        return pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)
    if DEFAULT_PARQUET.exists():
        return pd.read_parquet(DEFAULT_PARQUET)
    if DEFAULT_CSV.exists():
        return pd.read_csv(DEFAULT_CSV)
    return pd.DataFrame()


def apply_multiselect(df: pd.DataFrame, column: str, label: str) -> pd.DataFrame:
    if column not in df or df[column].dropna().empty:
        return df
    options = sorted(df[column].dropna().astype(str).unique().tolist())
    selected = st.sidebar.multiselect(label, options)
    return df[df[column].astype(str).isin(selected)] if selected else df


data = load_data()
if data.empty:
    st.error("Dati non trovati. Eseguire `python scripts/run_pipeline.py` prima di avviare la dashboard.")
    st.stop()

data["value"] = pd.to_numeric(data["value"], errors="coerce")
data["year"] = pd.to_numeric(data["year"], errors="coerce")

st.sidebar.header("Filtri")
filtered = data.copy()
filtered = apply_multiselect(filtered, "geography_code", "Territorio")
filtered = apply_multiselect(filtered, "pay_concept", "Concetto retributivo")
filtered = apply_multiselect(filtered, "sex_label", "Sesso")
filtered = apply_multiselect(filtered, "age_label", "Età")
filtered = apply_multiselect(filtered, "occupation_label", "Professione")
filtered = apply_multiselect(filtered, "sector_label", "Settore")
filtered = apply_multiselect(filtered, "working_time_label", "Orario")

if filtered.empty:
    st.warning("Nessuna osservazione corrisponde ai filtri selezionati.")
    st.stop()

latest_year = int(filtered["year"].dropna().max()) if filtered["year"].notna().any() else None
latest = filtered[filtered["year"].eq(latest_year)] if latest_year is not None else filtered

col1, col2, col3, col4 = st.columns(4)
col1.metric("Ultimo anno", latest_year if latest_year is not None else "n.d.")
col2.metric("Osservazioni", f"{len(filtered):,}".replace(",", "."))
col3.metric("Territori", filtered["geography_code"].nunique())
col4.metric("Fonti/dataset", filtered["dataset"].nunique())

st.subheader("Distribuzione oraria lorda")
distribution = filtered[
    filtered["pay_concept"].eq("gross_earnings") & filtered["percentile"].isin([10.0, 50.0, 90.0])
].copy()
if not distribution.empty:
    distribution["quantile"] = distribution["percentile"].map({10.0: "D1", 50.0: "Mediana", 90.0: "D9"})
    fig = px.line(
        distribution.sort_values("year"),
        x="year",
        y="value",
        color="quantile",
        line_dash="geography_code",
        markers=True,
        hover_data=["geography_name", "sex_label", "age_label", "occupation_label", "sector_label"],
        labels={"value": "Euro per ora", "year": "Anno", "quantile": "Statistica"},
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("I filtri selezionati non contengono D1, mediana o D9.")

st.subheader("Confronto nell'ultimo anno")
labels = {
    "occupation_label": "Professione",
    "sector_label": "Settore",
    "sex_label": "Sesso",
    "age_label": "Età",
    "working_time_label": "Orario",
    "geography_code": "Territorio",
}
comparison_dimension = st.selectbox("Dimensione", list(labels), format_func=labels.get)
comparison = latest[
    latest[comparison_dimension].notna()
    & ~latest[comparison_dimension].astype(str).isin(["Total", "TOTAL", "All activities", "All occupations"])
    & latest["statistic"].isin(["median", "mean", "share_below_two_thirds_median", "mean_gap"])
].copy()
if not comparison.empty:
    comparison = comparison.sort_values("value", ascending=False).head(40)
    fig_bar = px.bar(
        comparison,
        x="value",
        y=comparison_dimension,
        color="geography_code",
        orientation="h",
        hover_data=["dataset", "unit", "statistic"],
        labels={"value": "Valore", comparison_dimension: "Categoria"},
    )
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("La dimensione scelta non è disponibile con i filtri correnti.")

st.subheader("Copertura dei dati")
coverage = (
    filtered.groupby(["dataset", "source_request"], dropna=False)
    .agg(
        osservazioni=("value", "size"),
        primo_anno=("year", "min"),
        ultimo_anno=("year", "max"),
        territori=("geography_code", "nunique"),
    )
    .reset_index()
)
st.dataframe(coverage, use_container_width=True, hide_index=True)

with st.expander("Dati filtrati"):
    st.dataframe(filtered, use_container_width=True, hide_index=True)
