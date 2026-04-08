# Stochastic Forecasting Model

Quantitative research sandbox for equities: historical data, preprocessing, and (in progress) stochastic models (Markov chains, GARCH, Monte Carlo), ML, signals, and backtesting.

---

## Installation

From the project root:

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows PowerShell
pip install -r requirements.txt
```

**Parquet support:** Raw downloads and optional processed Parquet files use `pandas` + **pyarrow**. If Parquet writes fail, install with `pip install pyarrow` (listed in `requirements.txt`).

---

## Data pipeline (`src/data` and `data/`)

This section describes how market data is fetched, cleaned, stored, and reused.

### Overview

1. **Configure** symbols and date range in `config/config.yaml` under `data:`.
2. **Fetch** daily (or other interval) OHLCV from **Yahoo Finance** via `yfinance`, cached on disk.
3. **Preprocess** with a fixed functional pipeline (`process_data` in `preprocess.py`).
4. **Save** processed tables to **`data/processed/`** as **CSV** (primary artifact for reuse) and optionally **Parquet** (faster reload in Python).

**Optional:** `fetch_data.py` also defines a **Traydner** HTTP client for simulated trading, latest price, and history JSON. The main research path uses **Yahoo** for bulk history; Traydner is not required for the default pipeline.

---

### Directory layout

| Location | Role |
|----------|------|
| `config/config.yaml` | Symbols, `start` / `end` dates, `interval`, and preprocess-related keys used by scripts. |
| `data/raw/` | Cached **raw** downloads from Yahoo: one Parquet file per symbol/range/interval (gitignored by default). |
| `data/processed/` | **Cleaned** datasets ready for training, backtests, and notebooks (gitignored by default). |

---

### Files in `src/data/`

| File | Purpose |
|------|---------|
| `fetch_data.py` | **`PROJECT_ROOT`**, **`download_yahoo_ohlcv`**, **`load_raw_parquet`**: download/cache Yahoo OHLCV (+ Adj Close) as Parquet under `data/raw/`. Also **`TraydnerAPI`** for optional live/simulated endpoints. |
| `preprocess.py` | **`process_data`**: normalize columns → fix datetime index → drop invalid bars → log returns (`returns`) → winsorize → rolling annualized **`volatility`** → drop NaNs. **`split_data`**: chronological train/test split by row fraction. Uses **`toolz.pipe`** to chain steps. |
| `ml_data_process.py` | Rolling, walk-forward GARCH forecast builder for ML feature pipelines. Fits a sliding-window GARCH model and stores `garch_vol_forecast`; uses **`tqdm`** for progress tracking. |
| `__init__.py` | **`load_yaml()`**, **`build_clean_dataframe()`**, **`create_data()`** (small demo using first symbol from config). |
| `__main__.py` | Allows **`python -m src.data`** to run **`create_data()`**. |

Shared I/O helpers live in **`src/utils/io.py`**: **`save_processed_csv`**, **`load_processed_csv`**, **`save_processed_parquet`**.

---

### How to get data (recommended)

From the **project root** (the folder that contains `prepare_data.py` and `config/`):

```bash
python prepare_data.py
```

The implementation lives in **`src/cli/prepare_data.py`**; the root `prepare_data.py` is a thin launcher. You can also run:

```bash
python -m src.cli.prepare_data
```

This script:

1. Loads `config/config.yaml`.
2. For each symbol in `data.symbols`, downloads or reuses cached raw data (`download_yahoo_ohlcv` → `data/raw/`).
3. Loads that Parquet with `load_raw_parquet`, runs **`process_data`**, splits train/test for logging (`split_data`, ratio from `preprocess.train_frac` if present).
4. Saves processed output:
   - **`data/processed/{SYMBOL}_{interval}_clean.csv`** — **use this** for notebooks, model training, and backtests without refetching.
   - **`data/processed/{SYMBOL}_{interval}_clean.parquet`** — same data; faster to load in pandas if pyarrow is installed. If Parquet fails (missing engine), CSV is still written.

**Re-run** this when you change symbols, dates, interval, or preprocessing logic. For day-to-day modeling, **load the CSV** instead of running the full pipeline every time.

---

### Alternative: quick demo (no CSV export)

```bash
python -m src.data
```

Runs **`create_data()`**: uses the **first** symbol in `config/config.yaml`, fetches and preprocesses, prints head and train/test sizes. It does **not** mirror the full multi-symbol CSV export in `prepare_data.py`; use `prepare_data.py` for saved artifacts.

---

### Rolling ML feature generation

The new `src/data/ml_data_process.py` module supports a walk-forward GARCH forecast over a historical dataset.

- Use it to build a standalone `garch_vol_forecast` feature for model training or strategy signals.
- The routine is computationally expensive and intended for one-time dataset preparation, not for every live prediction step.
- Requires `tqdm` for the progress bar, which is now included in `requirements.txt`.

---

### Configuration (`config/config.yaml`)

Relevant keys for the data stage:

- **`data.provider`** — use `yahoo` for the implemented path.
- **`data.symbols`** — list of tickers, e.g. `[SPY, AAPL]`.
- **`data.start`**, **`data.end`** — date strings; `end: null` means through the latest available bar.
- **`data.interval`** — yfinance interval, e.g. `1d`, `1h`.
- **`preprocess.train_frac`** — fraction of rows used as the **train** portion in `prepare_data.py` when reporting train/test sizes (default `0.8` in code if omitted).

Other keys under `preprocess`, `features`, etc. are reserved for future or extended pipelines; the current **`process_data`** implementation uses fixed steps inside `preprocess.py` (not every YAML key is wired in yet).

---

### Format of the processed data

**Index**

- **Datetime index** (bar timestamp). In CSV, the index is written as the **first column** (often unnamed or `timestamp`); when loading with `load_processed_csv`, it becomes a **`DatetimeIndex`**.

**Columns** (after `process_data`)

Typical columns (exact names depend on Yahoo fields and pipeline):

| Column | Meaning |
|--------|---------|
| `open`, `high`, `low`, `close` | OHLC (lowercase after normalization). |
| `adj_close` | Adjusted close when provided by Yahoo (preferred for returns). |
| `volume` | Volume when present. |
| `returns` | Log return from `adj_close` or `close`; then **winsorized** at default quantiles. |
| `volatility` | Rolling standard deviation of `returns` × √252 (21-bar window by default), annualized. |

Rows with insufficient history for rolling statistics are dropped at the end of the pipeline.

**Raw Parquet (`data/raw/`)**

- Yahoo columns as returned by `yfinance` (after flattening MultiIndex), sorted by date, index name `timestamp`.

---

### Loading processed data in Python

```python
from pathlib import Path
import sys

# If running from elsewhere, add project root to path:
# sys.path.insert(0, r"path\to\Stochastic Forecasting Model")

from src.utils.io import load_processed_csv

root = Path(__file__).resolve().parent  # adjust to project root
df = load_processed_csv(root / "data" / "processed" / "SPY_1d_clean.csv")
```

Or with a string path relative to the current working directory:

```python
from src.utils.io import load_processed_csv

df = load_processed_csv("data/processed/SPY_1d_clean.csv")
```

---

### Importing the package

Run scripts from the project root, or add the root to `sys.path` so `import src.data` and `import src.utils.io` resolve. **`python -m src.data`** must be run from the directory that contains the `src` folder (project root).

---

## Features engineering (`src/features`)

This section describes feature extraction and stochastic modeling for forecasting and signals.

### Overview

Features are built from processed data (from `src/data`) to create inputs for models and signals. Includes time-series features, volatility models, and stochastic processes.

### Files in `src/features/`

| File | Purpose |
|------|---------|
| `time_series_features.py` | Lag features, rolling statistics, technical indicators (SMA, EMA, RSI, MACD, Bollinger bands). |
| `volatility_models.py` | Realized volatility estimators, GARCH models (GARCH(1,1), EGARCH), forecasting modes. |
| `garch_volatility.py` | Script to fit GARCH model and forecast next-day volatility from processed data. |
| `markov_chains.py` | Markov chain models for regime detection. |
| `monte_carlo.py` | Monte Carlo simulations for path generation. |
| `stochastic_processes.py` | General stochastic process implementations. |
| `get_indicators.py` | Technical indicators (RSI, MACD) using pandas-ta. |

### Running volatility forecast

From the project root:

```bash
python src/features/garch_volatility.py
```

This loads processed data, fits a GARCH(1,1) model, and prints the next-day annualized volatility forecast and model parameters.

### Importing features

```python
from src.features.garch_volatility import forecast_garch_volatility
from src.features.get_indicators import add_indicators
```

Ensure the project root is in `sys.path` or run from root.

---

---

## Roadmap

- Wire stochastic models and signals into the processed datasets.
- Full backtest and reporting from saved CSV/Parquet.
- Optional: Traydner or other providers as alternate `fetch` backends with the same processed column schema.
