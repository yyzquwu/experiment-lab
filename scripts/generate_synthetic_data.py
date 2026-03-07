from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def _base_table(n_users: int, seed: int, treatment_ratio: float = 0.5) -> tuple[np.ndarray, np.ndarray, pd.DatetimeIndex, np.random.Generator]:
    rng = np.random.default_rng(seed)
    user_id = np.arange(1, n_users + 1)
    variant = rng.choice(["control", "treatment"], size=n_users, p=[1.0 - treatment_ratio, treatment_ratio])
    timestamp = pd.date_range("2025-01-01", periods=n_users, freq="min")
    return user_id, variant, timestamp, rng


def build_signup_experiment(path: Path) -> None:
    user_id, variant, timestamp, rng = _base_table(n_users=14000, seed=7)

    pre_metric = rng.normal(0.0, 1.0, size=user_id.size)
    baseline_sessions = rng.poisson(3.6, size=user_id.size)
    segment = np.where(pre_metric > 0.8, "high_intent", np.where(pre_metric < -0.5, "casual", "exploring"))

    base = 0.12 + 0.018 * (pre_metric > 0.0) + 0.010 * (baseline_sessions >= 4)
    treatment_lift = np.select(
        [segment == "high_intent", segment == "exploring", segment == "casual"],
        [0.026, 0.014, 0.003],
        default=0.010,
    )
    prob = np.clip(base + np.where(variant == "treatment", treatment_lift, 0.0), 0.01, 0.99)
    outcome = rng.binomial(1, prob)

    support_ticket_prob = np.clip(
        0.018 + 0.006 * (segment == "casual") + np.where(variant == "treatment", 0.004, 0.0),
        0.001,
        0.25,
    )
    support_tickets = rng.binomial(1, support_ticket_prob)

    df = pd.DataFrame(
        {
            "user_id": user_id,
            "variant": variant,
            "timestamp": timestamp,
            "pre_metric": pre_metric,
            "baseline_sessions": baseline_sessions,
            "segment": segment,
            "outcome": outcome,
            "support_tickets": support_tickets,
        }
    )
    df.to_csv(path / "signup_experiment.csv", index=False)


def build_checkout_value_experiment(path: Path) -> None:
    user_id, variant, timestamp, rng = _base_table(n_users=9500, seed=18)

    pre_metric = rng.normal(52.0, 10.0, size=user_id.size)
    prior_value = rng.normal(48.0, 9.5, size=user_id.size)
    segment = np.where(prior_value > 56, "repeat_buyers", np.where(prior_value < 42, "price_sensitive", "mixed"))

    noise = rng.normal(0.0, 15.0, size=user_id.size)
    lift = np.select(
        [segment == "repeat_buyers", segment == "mixed", segment == "price_sensitive"],
        [3.4, 2.2, 0.8],
        default=2.0,
    )
    outcome = pre_metric + noise + np.where(variant == "treatment", lift, 0.0)

    refund_rate = np.clip(
        0.032 + 0.012 * (segment == "price_sensitive") + np.where(variant == "treatment", 0.005, 0.0),
        0.001,
        0.40,
    )
    refund_flag = rng.binomial(1, refund_rate)

    df = pd.DataFrame(
        {
            "user_id": user_id,
            "variant": variant,
            "timestamp": timestamp,
            "pre_metric": pre_metric,
            "prior_value": prior_value,
            "segment": segment,
            "outcome": outcome,
            "refund_flag": refund_flag,
        }
    )
    df.to_csv(path / "checkout_value_experiment.csv", index=False)


def build_sequential_peeking_experiment(path: Path) -> None:
    user_id, variant, timestamp, rng = _base_table(n_users=12000, seed=27)

    pre_metric = rng.normal(0.0, 1.0, size=user_id.size)
    device_score = rng.normal(0.0, 1.0, size=user_id.size)
    segment = np.where(device_score > 0.7, "mobile_heavy", np.where(device_score < -0.6, "desktop_heavy", "mixed"))

    progress = np.linspace(0.0, 1.0, num=user_id.size)
    novelty_effect = 0.018 * np.exp(-4.0 * progress)
    steady_effect = 0.004
    base_prob = 0.093 + 0.012 * (pre_metric > 1.0)
    treatment_prob = np.clip(base_prob + novelty_effect + steady_effect * (segment != "mobile_heavy"), 0.01, 0.99)
    control_prob = np.clip(base_prob, 0.01, 0.99)
    prob = np.where(variant == "treatment", treatment_prob, control_prob)
    outcome = rng.binomial(1, prob)

    delay_prob = np.clip(0.020 + 0.010 * (segment == "mobile_heavy") + np.where(variant == "treatment", 0.003, 0.0), 0.001, 0.25)
    latency_alert = rng.binomial(1, delay_prob)

    df = pd.DataFrame(
        {
            "user_id": user_id,
            "variant": variant,
            "timestamp": timestamp,
            "pre_metric": pre_metric,
            "device_score": device_score,
            "segment": segment,
            "outcome": outcome,
            "latency_alert": latency_alert,
        }
    )
    df.to_csv(path / "sequential_peeking_experiment.csv", index=False)


def build_search_ctr_experiment(path: Path) -> None:
    user_id, variant, timestamp, rng = _base_table(n_users=11000, seed=39)

    baseline_sessions = rng.poisson(5.0, size=user_id.size) + 1
    segment = np.where(baseline_sessions >= 7, "power_searchers", np.where(baseline_sessions <= 3, "light_searchers", "typical"))
    impressions = rng.poisson(18 + 4 * (segment == "power_searchers"), size=user_id.size) + 1

    base_ctr = 0.086 + 0.012 * (segment == "power_searchers") - 0.005 * (segment == "light_searchers")
    ctr_lift = np.select(
        [segment == "power_searchers", segment == "typical", segment == "light_searchers"],
        [0.012, 0.008, 0.002],
        default=0.006,
    )
    click_prob = np.clip(base_ctr + np.where(variant == "treatment", ctr_lift, 0.0), 0.01, 0.95)
    clicks = rng.binomial(impressions, click_prob)

    bounce_prob = np.clip(0.110 + 0.020 * (segment == "light_searchers") + np.where(variant == "treatment", 0.007, 0.0), 0.01, 0.95)
    bounce_rate = rng.binomial(1, bounce_prob)

    df = pd.DataFrame(
        {
            "user_id": user_id,
            "variant": variant,
            "timestamp": timestamp,
            "baseline_sessions": baseline_sessions,
            "segment": segment,
            "clicks": clicks,
            "impressions": impressions,
            "bounce_rate": bounce_rate,
        }
    )
    df.to_csv(path / "search_ctr_experiment.csv", index=False)


def main() -> None:
    output_dir = Path("data/synthetic")
    output_dir.mkdir(parents=True, exist_ok=True)

    build_signup_experiment(output_dir)
    build_checkout_value_experiment(output_dir)
    build_sequential_peeking_experiment(output_dir)
    build_search_ctr_experiment(output_dir)


if __name__ == "__main__":
    main()
