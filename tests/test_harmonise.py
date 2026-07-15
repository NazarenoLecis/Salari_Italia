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


def test_harmonise_lfs_employment_rate() -> None:
    raw = pd.DataFrame(
        [
            {
                "geo": "DE",
                "geo_label": "Germany",
                "time": "2025",
                "sex": "F",
                "sex_label": "Females",
                "age": "Y20-64",
                "age_label": "From 20 to 64 years",
                "citizen": "TOTAL",
                "citizen_label": "Total",
                "unit": "PC",
                "value": 77.8,
            }
        ]
    )
    result = harmonise_eurostat(raw, "lfsa_ergan", "lfs_employment_rate", "https://example.test")
    assert result.loc[0, "year"] == 2025
    assert result.loc[0, "pay_concept"] == "labour_market_context"
    assert result.loc[0, "pay_period"] == "annual"
    assert result.loc[0, "statistic"] == "employment_rate"
    assert result.loc[0, "sex"] == "F"
    assert result.loc[0, "citizenship"] == "TOTAL"
    assert result.loc[0, "value"] == 77.8
