"""
Project entrypoint: fetch → preprocess → save reusable datasets.

How to get preprocessed data (run once, then reuse)
----------------------------------------------------
From the project root (folder that contains ``run_backtest.py`` and ``config/``)::

    python run_backtest.py

This will:
1. Read ``config/config.yaml`` (symbols, date range, interval).
2. Download/cache raw Yahoo data under ``data/raw/`` (Parquet).
3. Run ``process_data`` on each symbol.
4. Save the cleaned table for reuse:
   - ``data/processed/{SYMBOL}_{interval}_clean.csv``  ← use this in notebooks, training, backtests
   - ``data/processed/{SYMBOL}_{interval}_clean.parquet`` ← optional fast pandas reload

Later, load the CSV without fetching or preprocessing::

    from src.utils.io import load_processed_csv
    df = load_processed_csv("data/processed/SPY_1d_clean.csv")

Or in a notebook with project root on ``sys.path``::

    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))  # if needed
    from src.utils.io import load_processed_csv
    df = load_processed_csv("data/processed/SPY_1d_clean.csv")
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

import yaml

from src.data.fetch_data import download_yahoo_ohlcv, load_raw_parquet
from src.data.preprocess import process_data, split_data
from src.utils.io import save_processed_csv, save_processed_parquet


def load_config():
    """
    Load YAML configuration from `config/config.yaml`.

    How to use:
    - Normally called from `main()`.
    - You can also import and call directly in notebooks to reuse the same config.
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
    3) Cleans data via `process_data`.
    4) Splits train/test (for reporting only; full series is saved).
    5) Saves CSV + Parquet under `data/processed/`.
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
            f"run_backtest.py currently implements provider='yahoo' only; got {provider!r}. "
            "Set data.provider to yahoo or extend this script for Traydner history parsing."
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
        print(f"Processed CSV: {csv_path}   ← load this for training / backtests / forecasting")
        print(f"Parquet:       {parquet_path}")
        print(f"Rows (clean):  {len(clean_df)}")
        print(f"Train / test:  {len(train_df)} / {len(test_df)} (split_ratio={split_ratio})")


if __name__ == "__main__":
    main()
