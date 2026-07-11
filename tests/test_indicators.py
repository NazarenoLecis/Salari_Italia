import numpy as np
import pandas as pd

from salari_italia.indicators import build_percentile_ratios, weighted_quantile


def test_weighted_quantile() -> None:
    result = weighted_quantile([10, 20, 30], [1, 1, 1], [0.5])
    assert np.isclose(result[0], 20)


def test_build_percentile_ratios() -> None:
    rows = []
    for percentile, value in ((10.0, 10.0), (50.0, 20.0), (90.0, 40.0)):
        rows.append(
            {
                "source": "Eurostat",
                "dataset": "earn_ses_hourly",
                "source_request": "total",
                "year": 2022,
                "geography_type": "country",
                "geography_code": "IT",
                "geography_name": "Italy",
                "geography_basis": "reporting_country",
                "pay_concept": "gross_earnings",
                "pay_period": "hourly",
                "statistic": "percentile",
                "percentile": percentile,
                "value": value,
                "unit": "EUR",
            }
        )
    result = build_percentile_ratios(pd.DataFrame(rows))
    ratios = dict(zip(result["statistic"], result["value"], strict=True))
    assert ratios["d9_d1"] == 4.0
    assert ratios["d9_median"] == 2.0
    assert ratios["median_d1"] == 2.0
