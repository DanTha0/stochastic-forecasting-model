# Traydner API (outline)

Market data and simulated trading use **Traydner** (`TraydnerAPI` in `src/data/fetch_data.py`).

## Credentials

- Bearer token: set `TRAYDNER_API_KEY` in `.env` (see `.env.example`).
- Base URL is defined on the client class (remote API host).

## Endpoints used in code

| Method | HTTP | Purpose |
|--------|------|---------|
| `get_price` | GET `price` | Latest price for a symbol |
| `get_history` | GET `history` | Historical candles (`resolution`, `limit`, optional `start_ts` / `end_ts`) |
| `trade` | POST `trade` | Simulated buy/sell |
| `get_balance` | GET `balance` | Simulated account balance |
| `market_status` | GET `market_status` | Market/symbol open status |

## Next steps for the data layer

- Parse `get_history` JSON into a **pandas** OHLCV `DataFrame` with a datetime index.
- Save to `data/raw/` (parquet) for reproducible backtests.
- Map Traydner `resolution` strings to your `config.yaml` timeframe field.

Alpaca (or another broker) can be added later as an alternate `provider` behind the same save/load interface.
