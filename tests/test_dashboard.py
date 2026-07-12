import pandas as pd

from salari_italia.dashboard import build_dashboard_payload


def test_build_dashboard_payload() -> None:
    data = pd.DataFrame(
        [
            {
                "source": "Eurostat",
                "dataset": "earn_ses_hourly",
                "source_request": "ses_hourly_distribution",
                "year": 2022,
                "geography_type": "country_or_european_aggregate",
                "geography_code": "IT",
                "geography_name": "Italy",
                "geography_basis": "reporting_country",
                "sex": "T",
                "sex_label": "Total",
                "pay_concept": "gross_earnings",
                "pay_period": "hourly",
                "statistic": "median",
                "percentile": 50.0,
                "measure_code": "MED_E_EUR",
                "value": 15.4,
                "unit": "EUR",
            }
        ]
    )
    payload = build_dashboard_payload(data, {"successful_requests": 1}, ("IT",))
    value_index = payload["record_schema"].index("value")
    assert payload["records"][0][value_index] == 15.4
    assert payload["filters"]["year"][0]["value"] == 2022
    assert payload["coverage"]
