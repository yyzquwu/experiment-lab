import pandas as pd

from exp.data import preprocess_hillstrom


def test_preprocess_hillstrom_matches_repo_contract() -> None:
    raw = pd.DataFrame(
        {
            "recency": [10, 6],
            "history_segment": ["2) $100 - $200", "3) $200 - $350"],
            "history": [142.44, 329.08],
            "mens": [1, 1],
            "womens": [0, 1],
            "zip_code": ["Surburban", "Rural"],
            "newbie": [0, 1],
            "channel": ["Phone", "Web"],
            "segment": ["No E-Mail", "Womens E-Mail"],
            "visit": [0, 1],
            "conversion": [0, 1],
            "spend": [0.0, 25.0],
        }
    )

    processed = preprocess_hillstrom(raw)
    assert {"user_id", "variant", "timestamp", "pre_metric", "segment", "outcome_conversion", "outcome_spend"}.issubset(processed.columns)
    assert processed["variant"].tolist() == ["control", "treatment"]
    assert processed["outcome_conversion"].tolist() == [0, 1]
