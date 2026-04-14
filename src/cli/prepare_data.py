"""
Fetch market data, preprocess it, and save reusable datasets (CSV + optional Parquet).

Run via the repo launcher (project root)::

    python prepare_data.py

Or as a module (project root on ``sys.path``)::

    python -m src.cli.prepare_data

This does **not** run a trading backtest.

Implementation lives here; the file ``prepare_data.py`` at the repository root is only a thin launcher.
"""

from pathlib import Path

import yaml

from ..data.fetch_data import download_yahoo_ohlcv, load_raw_parquet
from ..data.preprocess import process_data, split_data
from ..utils.io import save_processed_csv, save_processed_parquet

# Repo root: .../project/src/cli/prepare_data.py -> parents[2]
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_config():
    """
    Load YAML configuration from ``config/config.yaml`` (relative to repo root).

    How to use:
    - Called from ``main()``.
    - Import in notebooks: ``from src.cli.prepare_data import load_config``.
    """
    cfg_path = PROJECT_ROOT / "config" / "config.yaml"
    with open(cfg_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    """
    Execute the data pipeline for each configured symbol.

    What it does:
    1) Reads config.
    2) Downloads/caches raw Yahoo data.
    3) Cleans data via ``process_data``.
    4) Splits train/test (for reporting only; full series is saved).
    5) Saves CSV + Parquet under ``data/processed/``.
    """
    cfg = load_config()
    data_cfg = cfg.get("data", {})
    prep_cfg = cfg.get("preprocess", {})

    provider = (data_cfg.get("provider") or "yahoo").lower()
    symbols = data_cfg.get("symbols") or ["SPY"]
    start = data_cfg.get("start", "2018-01-01")
    end = data_cfg.get("end")
    interval = data_cfg.get("interval", "1d")
    split_ratio = float(prep_cfg.get("train_frac", 0.8))

    processed_dir = PROJECT_ROOT / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    if provider != "yahoo":
        raise SystemExit(
            f"prepare_data pipeline currently implements provider='yahoo' only; got {provider!r}. "
            "Set data.provider to yahoo or extend this module for Traydner history parsing."
        )

    for symbol in symbols:
        raw_path = download_yahoo_ohlcv(symbol, start=start, end=end, interval=interval)
        raw_df = load_raw_parquet(raw_path)
        clean_df = process_data(raw_df)
        train_df, test_df = split_data(clean_df, ratio=split_ratio)

        base = f"{symbol}_{interval}_clean"
        csv_path = processed_dir / f"{base}.csv"
        parquet_path = processed_dir / f"{base}.parquet"

        save_processed_csv(clean_df, csv_path)
        try:
            save_processed_parquet(clean_df, parquet_path)
        except ImportError as e:
            print(f"Note: skipped Parquet ({e}). CSV saved at {csv_path}")

        print(f"\n=== {symbol} ===")
        print(f"Raw cache:     {raw_path}")
        print(f"Processed CSV: {csv_path}   ← load this for training / later backtests / forecasting")
        print(f"Parquet:       {parquet_path}")
        print(f"Rows (clean):  {len(clean_df)}")
        print(f"Train / test:  {len(train_df)} / {len(test_df)} (split_ratio={split_ratio})")


if __name__ == "__main__":
    main()
