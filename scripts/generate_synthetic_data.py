from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def _base_table(n_users: int, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    user_id = np.arange(1, n_users + 1)
    variant = rng.choice(["control", "treatment"], size=n_users, p=[0.5, 0.5])
    timestamp = pd.date_range("2025-01-01", periods=n_users, freq="min")
    return user_id, variant, timestamp


def build_signup_experiment(path: Path) -> None:
    user_id, variant, timestamp = _base_table(n_users=12000, seed=7)
    rng = np.random.default_rng(11)

    pre_metric = rng.normal(0.0, 1.0, size=user_id.size)
    base = 0.13 + 0.02 * (pre_metric > 0)
    lift = np.where(variant == "treatment", 0.015, 0.0)
    prob = np.clip(base + lift, 0.01, 0.99)
    outcome = rng.binomial(1, prob)

    df = pd.DataFrame(
        {
            "user_id": user_id,
            "variant": variant,
            "timestamp": timestamp,
            "pre_metric": pre_metric,
            "outcome": outcome,
        }
    )
    df.to_csv(path / "signup_experiment.csv", index=False)


def build_checkout_value_experiment(path: Path) -> None:
    user_id, variant, timestamp = _base_table(n_users=9000, seed=18)
    rng = np.random.default_rng(22)

    pre_metric = rng.normal(50.0, 10.0, size=user_id.size)
    noise = rng.normal(0.0, 15.0, size=user_id.size)
    outcome = pre_metric + noise + np.where(variant == "treatment", 2.5, 0.0)

    df = pd.DataFrame(
        {
            "user_id": user_id,
            "variant": variant,
            "timestamp": timestamp,
            "pre_metric": pre_metric,
            "outcome": outcome,
        }
    )
    df.to_csv(path / "checkout_value_experiment.csv", index=False)


def build_sequential_peeking_experiment(path: Path) -> None:
    user_id, variant, timestamp = _base_table(n_users=10000, seed=27)
    rng = np.random.default_rng(30)

    pre_metric = rng.normal(0.0, 1.0, size=user_id.size)
    prob = np.where(variant == "treatment", 0.105, 0.095)
    outcome = rng.binomial(1, np.clip(prob + 0.01 * (pre_metric > 1.0), 0.01, 0.99))

    df = pd.DataFrame(
        {
            "user_id": user_id,
            "variant": variant,
            "timestamp": timestamp,
            "pre_metric": pre_metric,
            "outcome": outcome,
        }
    )
    df.to_csv(path / "sequential_peeking_experiment.csv", index=False)


def main() -> None:
    output_dir = Path("data/synthetic")
    output_dir.mkdir(parents=True, exist_ok=True)

    build_signup_experiment(output_dir)
    build_checkout_value_experiment(output_dir)
    build_sequential_peeking_experiment(output_dir)


if __name__ == "__main__":
    main()
