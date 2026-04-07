"""
Data-related utilities: fetching and preprocessing.

Import as: ``from src.data import ...`` or ``from src.data.fetch_data import ...``.

To run ``create_data()`` from the project root::

    python -m src.data

Do not run ``python src/data/__init__.py`` directly; if you must, imports fall back to absolute paths.
"""

import sys
from pathlib import Path

from .fetch_data import PROJECT_ROOT, download_yahoo_ohlcv, load_raw_parquet
from .preprocess import process_data, split_data

import yaml


def load_yaml():
    """Load ``config/config.yaml`` into a nested dict (same idea as ``src.cli.prepare_data.load_config``)."""
    with open(PROJECT_ROOT / "config" / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_clean_dataframe(symbol, start, end=None, interval="1d", force=False):
    """
    End-to-end: Yahoo cache path -> raw parquet -> processed dataframe.
    """
    raw_path = download_yahoo_ohlcv(symbol, start, end=end, interval=interval, force=force)
    raw_df = load_raw_parquet(raw_path)
    clean_df = process_data(raw_df)
    return clean_df, raw_path


def create_data():
    """Fetch + preprocess first symbol from config; print sample rows and train/test sizes."""
    cfg = load_yaml()
    data_cfg = cfg.get("data", {})
    symbols = data_cfg.get("symbols") or ["SPY"]
    symbol = symbols[0]
    start = data_cfg.get("start", "2017-01-01")
    end = data_cfg.get("end")
    interval = data_cfg.get("interval", "1d")

    df, path = build_clean_dataframe(symbol, start, end=end, interval=interval)

    print("Rows:", len(df), "columns:", list(df.columns))
    print(df.head())

    train, test = split_data(df, ratio=0.8)
    print("Train:", len(train), "Test:", len(test))


if __name__ == "__main__":
    create_data()
