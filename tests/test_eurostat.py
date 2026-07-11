from salari_italia.eurostat import jsonstat_to_frame


def test_jsonstat_decoder_sparse_values() -> None:
    payload = {
        "id": ["sex", "time"],
        "size": [2, 2],
        "dimension": {
            "sex": {"category": {"index": {"M": 0, "F": 1}, "label": {"M": "Male", "F": "Female"}}},
            "time": {
                "category": {"index": {"2020": 0, "2021": 1}, "label": {"2020": "2020", "2021": "2021"}}
            },
        },
        "value": {"0": 10.0, "3": 20.0},
        "status": {"3": "p"},
    }
    result = jsonstat_to_frame(payload)
    assert len(result) == 2
    assert result.loc[0, "sex"] == "M"
    assert result.loc[0, "time"] == "2020"
    assert result.loc[1, "sex"] == "F"
    assert result.loc[1, "time"] == "2021"
    assert result.loc[1, "status"] == "p"
