import pandas as pd

from salari_italia.harmonise import harmonise_eurostat


def test_harmonise_ses_median() -> None:
    raw = pd.DataFrame(
        [
            {
                "geo": "IT",
                "geo_label": "Italy",
                "time": "2022",
                "sex": "T",
                "sex_label": "Total",
                "age": "TOTAL",
                "age_label": "Total",
                "isco08": "TOTAL",
                "isco08_label": "All occupations",
                "nace_r2": "B-S_X_O",
                "nace_r2_label": "Business economy",
                "indic_se": "MED_E_EUR",
                "unit": "EUR",
                "value": 15.5,
            }
        ]
    )
    result = harmonise_eurostat(raw, "earn_ses_hourly", "test", "https://example.test")
    assert result.loc[0, "year"] == 2022
    assert result.loc[0, "pay_concept"] == "gross_earnings"
    assert result.loc[0, "statistic"] == "median"
    assert result.loc[0, "percentile"] == 50.0
    assert result.loc[0, "value"] == 15.5
