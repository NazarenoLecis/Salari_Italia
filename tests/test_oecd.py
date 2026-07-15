import pandas as pd

from salari_italia.oecd import harmonise_oecd_average_wages


def test_harmonise_oecd_average_wages_uses_euro_constant_prices() -> None:
    raw = pd.DataFrame(
        [
            {
                "REF_AREA": "DEU",
                "MEASURE": "WG",
                "UNIT_MEASURE": "EUR",
                "PAY_PERIOD": "A",
                "PRICE_BASE": "Q",
                "AGGREGATION_OPERATION": "MEAN",
                "SEX": "_Z",
                "TIME_PERIOD": "2025",
                "OBS_VALUE": "54839.643",
                "BASE_PER": "2025",
                "OBS_STATUS": "A",
            },
            {
                "REF_AREA": "DEU",
                "MEASURE": "WG",
                "UNIT_MEASURE": "USD_PPP",
                "PAY_PERIOD": "A",
                "PRICE_BASE": "Q",
                "AGGREGATION_OPERATION": "MEAN",
                "SEX": "_Z",
                "TIME_PERIOD": "2025",
                "OBS_VALUE": "76284.517",
                "BASE_PER": "2025",
                "OBS_STATUS": "A",
            },
        ]
    )
    result = harmonise_oecd_average_wages(raw, "oecd_average_annual_wages", "https://example.test")
    assert len(result) == 1
    assert result.loc[0, "geography_code"] == "DEU"
    assert result.loc[0, "unit"] == "EUR"
    assert result.loc[0, "unit_label"] == "Euro a prezzi 2025"
    assert result.loc[0, "value"] == 54839.643
