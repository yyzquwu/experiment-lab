from __future__ import annotations

from pathlib import Path

from exp.data import prepare_hillstrom_dataset


RAW_PATH = Path("data/raw/hillstrom_raw.csv")
PROCESSED_PATH = Path("data/raw/hillstrom_experiment.csv")


def main() -> None:
    if PROCESSED_PATH.exists():
        print(f"Found processed Hillstrom dataset at {PROCESSED_PATH}")
        return

    prepare_hillstrom_dataset(RAW_PATH, PROCESSED_PATH)
    print(f"Downloaded and processed Hillstrom dataset to {PROCESSED_PATH}")


if __name__ == "__main__":
    main()
