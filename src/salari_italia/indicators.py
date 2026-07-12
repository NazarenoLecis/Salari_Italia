from __future__ import annotations

import numpy as np
import pandas as pd

from salari_italia.schema import ensure_standard_schema


def weighted_quantile(
    values: pd.Series | np.ndarray,
    weights: pd.Series | np.ndarray,
    quantiles: list[float] | np.ndarray,
) -> np.ndarray:
    values_array = np.asarray(values, dtype=float)
    weights_array = np.asarray(weights, dtype=float)
    quantiles_array = np.asarray(quantiles, dtype=float)
    valid = np.isfinite(values_array) & np.isfinite(weights_array) & (weights_array >= 0)
    values_array = values_array[valid]
    weights_array = weights_array[valid]
    if values_array.size == 0 or weights_array.sum() <= 0:
        return np.full(quantiles_array.shape, np.nan)
    if np.any((quantiles_array < 0) | (quantiles_array > 1)):
        raise ValueError("I quantili devono essere compresi tra 0 e 1.")
    order = np.argsort(values_array)
    sorted_values = values_array[order]
    sorted_weights = weights_array[order]
    cumulative = np.cumsum(sorted_weights) - 0.5 * sorted_weights
    cumulative /= sorted_weights.sum()
    return np.interp(quantiles_array, cumulative, sorted_values)


def build_percentile_ratios(df: pd.DataFrame) -> pd.DataFrame:
    standard = ensure_standard_schema(df)
    subset = standard[
        standard["pay_concept"].eq("gross_earnings")
        & standard["pay_period"].eq("hourly")
        & standard["percentile"].isin([10.0, 50.0, 90.0])
    ].copy()
    if subset.empty:
        return ensure_standard_schema(pd.DataFrame())

    group_columns = [
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
        "contractual_occupation",
        "contractual_occupation_label",
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
        "country_birth",
        "country_birth_label",
        "unit",
        "unit_label",
    ]
    sentinel = "__ALL__"
    subset[group_columns] = subset[group_columns].fillna(sentinel)
    pivot = subset.pivot_table(index=group_columns, columns="percentile", values="value", aggfunc="first").reset_index()
    rows = []
    for _, row in pivot.iterrows():
        for ratio_name, numerator, denominator in (
            ("d9_d1", 90.0, 10.0),
            ("d9_median", 90.0, 50.0),
            ("median_d1", 50.0, 10.0),
        ):
            numerator_value = row.get(numerator)
            denominator_value = row.get(denominator)
            if pd.isna(numerator_value) or pd.isna(denominator_value) or denominator_value == 0:
                continue
            output = {column: (None if row[column] == sentinel else row[column]) for column in group_columns}
            output.update(
                {
                    "pay_concept": "gross_earnings_ratio",
                    "pay_period": "hourly",
                    "statistic": ratio_name,
                    "percentile": None,
                    "measure_code": ratio_name.upper(),
                    "value": float(numerator_value) / float(denominator_value),
                    "unit": "ratio",
                    "unit_label": "Ratio",
                    "population": None,
                    "sample_size": None,
                    "quality_flag": None,
                    "source_url": None,
                    "download_timestamp": None,
                    "dimensions_json": None,
                }
            )
            rows.append(output)
    return ensure_standard_schema(pd.DataFrame(rows))
