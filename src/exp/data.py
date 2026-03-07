"""Public dataset preprocessing helpers."""

from __future__ import annotations

import hashlib
import io
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd


HILLSTROM_URLS = (
    "http://www.minethatdata.com/Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv",
    "https://www.minethatdata.com/Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv",
)
HILLSTROM_SHA256 = "0e5893329d8b93cefecc571777672028290ab69865718020c78c7284f291aece"
HILLSTROM_RAW_COLUMNS = (
    "recency",
    "history_segment",
    "history",
    "mens",
    "womens",
    "zip_code",
    "newbie",
    "channel",
    "segment",
    "visit",
    "conversion",
    "spend",
)


def preprocess_hillstrom(raw_frame: pd.DataFrame) -> pd.DataFrame:
    missing = [column for column in HILLSTROM_RAW_COLUMNS if column not in raw_frame.columns]
    if missing:
        raise ValueError(f"Hillstrom raw frame is missing columns: {missing}")

    prepared = raw_frame.copy().reset_index(drop=True)
    prepared["user_id"] = np.arange(1, len(prepared) + 1)
    prepared["variant"] = np.where(prepared["segment"] == "No E-Mail", "control", "treatment")
    prepared["timestamp"] = pd.date_range("2008-03-20", periods=len(prepared), freq="min")
    prepared["pre_metric"] = prepared["history"].astype(float)
    prepared["segment_label"] = prepared["history_segment"]
    prepared["outcome_conversion"] = prepared["conversion"].astype(int)
    prepared["outcome_spend"] = prepared["spend"].astype(float)

    output = pd.DataFrame(
        {
            "user_id": prepared["user_id"],
            "variant": prepared["variant"],
            "timestamp": prepared["timestamp"],
            "pre_metric": prepared["pre_metric"],
            "segment": prepared["segment_label"],
            "channel": prepared["channel"],
            "history": prepared["history"].astype(float),
            "recency": prepared["recency"].astype(float),
            "mens": prepared["mens"].astype(int),
            "womens": prepared["womens"].astype(int),
            "newbie": prepared["newbie"].astype(int),
            "outcome_conversion": prepared["outcome_conversion"],
            "outcome_spend": prepared["outcome_spend"],
        }
    )
    return output


def download_hillstrom_bytes() -> bytes:
    errors: list[str] = []
    for url in HILLSTROM_URLS:
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                payload = response.read()
            digest = hashlib.sha256(payload).hexdigest()
            if digest != HILLSTROM_SHA256:
                raise ValueError(f"Unexpected SHA256 for {url}: {digest}")
            return payload
        except Exception as exc:
            errors.append(f"{url}: {exc}")
    raise RuntimeError("Unable to download Hillstrom dataset:\n" + "\n".join(errors))


def prepare_hillstrom_dataset(raw_output_path: Path, processed_output_path: Path) -> Path:
    payload = download_hillstrom_bytes()
    raw_output_path.parent.mkdir(parents=True, exist_ok=True)
    raw_output_path.write_bytes(payload)
    raw_frame = pd.read_csv(io.BytesIO(payload))
    processed = preprocess_hillstrom(raw_frame)
    processed.to_csv(processed_output_path, index=False)
    return processed_output_path
