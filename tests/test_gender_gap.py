from salari_italia.gender_gap import load_gender_pay_gap_decomposition


def value_for(rows, pay_concept: str, statistic: str) -> float:
    selected = rows[
        rows["geography_code"].eq("IT")
        & rows["pay_concept"].eq(pay_concept)
        & rows["statistic"].eq(statistic)
    ]
    assert len(selected) == 1
    return float(selected.iloc[0]["value"])


def test_load_gender_pay_gap_decomposition_for_italy() -> None:
    rows = load_gender_pay_gap_decomposition(download_timestamp="2026-07-13T00:00:00+00:00")

    assert value_for(rows, "gender_pay_gap_adjusted", "mean_gap") == 10.9
    assert value_for(rows, "gender_pay_gap_decomposition", "unadjusted") == 3.8
    assert value_for(rows, "gender_pay_gap_decomposition", "explained_overall") == -7.1
    assert value_for(rows, "gender_pay_gap_decomposition", "working_time") == 1.7
    assert value_for(rows, "gender_pay_gap_decomposition", "economic_activity") == 4.9
    assert rows["source_url"].str.contains("KS-01-25-035").all()
