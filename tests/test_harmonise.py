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


def test_harmonise_ses2018_annual_education() -> None:
    raw = pd.DataFrame(
        [
            {
                "geo": "IT",
                "geo_label": "Italy",
                "time": "2018",
                "sex": "F",
                "sex_label": "Females",
                "isced11": "ED5-8",
                "isced11_label": "Tertiary education",
                "nace_r2": "B-S_X_O",
                "nace_r2_label": "Business economy",
                "sizeclas": "GE10",
                "sizeclas_label": "10 employees or more",
                "indic_se": "ERN",
                "unit": "EUR",
                "value": 34123,
            }
        ]
    )
    result = harmonise_eurostat(raw, "earn_ses18_30", "ses2018_annual_by_education", "https://example.test")
    assert result.loc[0, "year"] == 2018
    assert result.loc[0, "pay_concept"] == "gross_earnings"
    assert result.loc[0, "pay_period"] == "annual"
    assert result.loc[0, "statistic"] == "mean"
    assert result.loc[0, "sex"] == "F"
    assert result.loc[0, "education"] == "ED5-8"
    assert result.loc[0, "firm_size"] == "GE10"
    assert result.loc[0, "value"] == 34123


def test_harmonise_ses2010_education_uses_isced97() -> None:
    raw = pd.DataFrame(
        [
            {
                "geo": "IT",
                "geo_label": "Italy",
                "time": "2010",
                "sex": "T",
                "sex_label": "Total",
                "isced97": "ED5_6",
                "isced97_label": "Tertiary education",
                "nace_r2": "B-S_X_O",
                "nace_r2_label": "Business economy",
                "sizeclas": "GE10",
                "sizeclas_label": "10 employees or more",
                "indic_se": "ERN",
                "currency": "EUR",
                "value": 29500,
            }
        ]
    )
    result = harmonise_eurostat(raw, "earn_ses10_30", "ses2010_annual_by_education", "https://example.test")
    assert result.loc[0, "year"] == 2010
    assert result.loc[0, "pay_period"] == "annual"
    assert result.loc[0, "education"] == "ED5_6"
    assert result.loc[0, "unit"] == "EUR"
