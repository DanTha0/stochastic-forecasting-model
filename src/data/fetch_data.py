"""
Market data: Yahoo Finance (research-grade historical OHLCV) and Traydner (simulated trading).

Typical research flow
---------------------
1. ``download_yahoo_ohlcv("SPY", start="2020-01-01", end=None, interval="1d")`` — caches under ``data/raw/``.
2. ``load_raw_parquet(path)`` — load into pandas for ``preprocess.clean_ohlcv``.

Traydner is optional: instantiate ``TraydnerAPI(api_key)`` for live price, paper trades, or history
if you parse JSON into a DataFrame yourself later.
"""

from pathlib import Path

import pandas as pd
import requests
import yfinance as yf

# Repo root (two levels up from this file: src/data → project root)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def ensure_raw_dir():
    """
    Create ``data/raw`` if missing so Parquet downloads do not fail.

    What it does: Makes ``RAW_DATA_DIR`` with parents.

    How to use: Called automatically by ``download_yahoo_ohlcv``. Call manually if you save raw
    files through custom code.
    """
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def _flatten_yfinance_columns(df):
    """
    Flatten yfinance MultiIndex columns when downloading a single ticker.

    What it does: yfinance sometimes returns columns like ("Close", "SPY"); this reduces them
    to "Close" so the same code works for one or many tickers.

    How to use: Internal only; applied inside ``download_yahoo_ohlcv`` after ``yf.download``.
    """
    if df.empty:
        return df
    if isinstance(df.columns, pd.MultiIndex):
        out = df.copy()
        out.columns = out.columns.get_level_values(0)
        return out
    return df


def download_yahoo_ohlcv(
    symbol,
    start,
    end=None,
    interval="1d",
    *,
    auto_adjust=False,
    force=False,
):
    """
    Download OHLCV plus Adj Close from Yahoo Finance and save as Parquet (with caching).

    What it does: Calls ``yfinance.download``, normalizes columns, sorts by date, writes
    ``data/raw/{SYMBOL}_yahoo_{interval}_{start}_{end_or_latest}.parquet``. If the file already
    exists and ``force`` is False, skips the network call and returns the existing path.

    How to use:
      ``path = download_yahoo_ohlcv("AAPL", "2019-01-01", end="2024-01-01", interval="1d")``
      ``df = load_raw_parquet(path)``
    Use ``force=True`` to refresh after a corporate action or bad cache.
    Use ``end=None`` to fetch through the latest available bar.

    Arguments:
      symbol — Ticker string (e.g. "SPY").
      start — Start date "YYYY-MM-DD".
      end — End date or None for latest.
      interval — yfinance bar size: "1d", "1h", "1wk", etc.
      auto_adjust — If True, Yahoo adjusts OHLC internally; default False keeps raw OHLC + Adj Close.
      force — If True, re-download even when cache file exists.
    """
    ensure_raw_dir()
    safe_sym = symbol.replace("/", "-")
    end_tag = end or "latest"
    filename = f"{safe_sym}_yahoo_{interval}_{start}_{end_tag}.parquet"
    out_path = RAW_DATA_DIR / filename

    if out_path.exists() and not force:
        return out_path

    df = yf.download(
        symbol,
        start=start,
        end=end,
        interval=interval,
        auto_adjust=auto_adjust,
        progress=False,
        threads=False,
    )
    df = _flatten_yfinance_columns(df)
    if df.empty:
        raise ValueError(f"No Yahoo Finance data for {symbol!r} (interval={interval}, start={start}, end={end}).")

    df = df.sort_index()
    df.index.name = "timestamp"
    df.to_parquet(out_path)
    return out_path


def load_raw_parquet(path):
    """
    Load a Parquet file from disk into a DataFrame with a sorted DatetimeIndex.

    What it does: ``read_parquet``, coerces index to datetime if needed, sorts ascending.

    How to use: After ``download_yahoo_ohlcv``, pass the returned Path or any compatible Parquet:
      ``raw = load_raw_parquet(path)``
      ``clean = clean_ohlcv(raw, preprocess_cfg)``

    Argument ``path``: String or Path to ``.parquet`` file.
    """
    df = pd.read_parquet(path)
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    if not df.index.is_monotonic_increasing:
        df = df.sort_index()
    return df


class TraydnerAPI:
    """
    HTTP client for the Traydner remote API (simulated balance, trades, candles, market status).

    What it does: Sends Bearer-authenticated GET/POST requests to the configured BASE_URL.

    How to use:
      ``import os``
      ``api = TraydnerAPI(os.environ["TRAYDNER_API_KEY"])``
      ``api.get_price("AAPL")``
      ``api.get_history("SPY", "1d", limit=500)``
    Parse JSON responses into DataFrames in your own module when you wire Traydner into the pipeline.
    """

    BASE_URL = "https://traydner-186649552655.us-central1.run.app/api/remote"

    def __init__(self, api_key, timeout=15):
        """
        Store API key and build Authorization headers.

        Arguments:
          api_key — Bearer token string from Traydner.
          timeout — Seconds for each HTTP request.
        """
        self.api_key = api_key
        self.timeout = timeout
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def _get(self, endpoint, params=None):
        """Internal GET to ``BASE_URL/endpoint`` with optional query params."""
        url = f"{self.BASE_URL}/{endpoint}"
        r = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def _post(self, endpoint, params=None):
        """Internal POST to ``BASE_URL/endpoint`` with optional query/body params."""
        url = f"{self.BASE_URL}/{endpoint}"
        r = requests.post(url, headers=self.headers, params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def get_price(self, symbol):
        """
        Latest price snapshot for a symbol.

        How to use: ``api.get_price("BTC")`` — response shape depends on Traydner API.
        """
        return self._get("price", {"symbol": symbol})

    def trade(self, symbol, side, quantity):
        """
        Submit a simulated buy or sell.

        Arguments:
          symbol — Ticker.
          side — "buy" or "sell".
          quantity — Share count (int) or crypto/forex size (float) per Traydner rules.
        """
        params = {"symbol": symbol, "side": side, "quantity": quantity}
        return self._post("trade", params)

    def get_balance(self):
        """Fetch simulated account balance JSON."""
        return self._get("balance")

    def get_history(self, symbol, resolution, limit=500, start_ts=None, end_ts=None):
        """
        Historical OHLCV-style candles from Traydner.

        Arguments:
          symbol — Ticker.
          resolution — Bar size string, e.g. "1m", "5m", "1h", "1d".
          limit — Max bars (API typically caps, e.g. 5000).
          start_ts, end_ts — Optional Unix timestamps to bound the window.

        How to use: You still need to map the JSON list into a pandas DataFrame for ``clean_ohlcv``.
        """
        params = {
            "symbol": symbol,
            "resolution": resolution,
            "limit": limit,
        }
        if start_ts is not None:
            params["start_ts"] = start_ts
        if end_ts is not None:
            params["end_ts"] = end_ts

        return self._get("history", params)

    def market_status(self, symbol=None, market=None):
        """
        Whether a symbol or whole market class is open.

        Arguments:
          symbol — If set, query this symbol.
          market — Else one of "stock", "crypto", "forex" when symbol is omitted.

        How to use: ``api.market_status(symbol="SPY")`` or ``api.market_status(market="stock")``.
        """
        params = {}
        if symbol:
            params["symbol"] = symbol
        if market:
            params["market"] = market

        return self._get("market_status", params)
