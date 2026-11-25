"""Datenbeschaffung.

Reihenfolge (ADR 0002):
1. lokaler Cache  data/cache/<TICKER>.csv  (von einem früheren yfinance-Download)
2. yfinance (adjustierte Schlusskurse), Ergebnis wird gecacht
3. eingechecktes Snapshot  data/snapshot/plotly_stockdata_2007_2016.csv
   (AAPL, MSFT, IBM, SBUX, ^GSPC; 2007-01-03 bis 2016-03-01; Quelle siehe data/README.md)

Die Ergebnisse in projekte/01_gbm wurden mit dem Snapshot erzeugt, damit sie exakt
reproduzierbar sind (yfinance-Daten werden nachträglich revidiert).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "data" / "snapshot" / "plotly_stockdata_2007_2016.csv"
CACHE = ROOT / "data" / "cache"
_SNAPSHOT_ALIAS = {"^GSPC": "GSPC", "GSPC": "GSPC"}


def load_snapshot() -> pd.DataFrame:
    df = pd.read_csv(SNAPSHOT, parse_dates=["Date"]).set_index("Date").sort_index()
    return df


def load_prices(ticker: str, start: str | None = None, end: str | None = None,
                source: str = "snapshot") -> pd.Series:
    """Tägliche (split-/dividendenbereinigte) Schlusskurse als pd.Series.

    source: "snapshot" (Standard, reproduzierbar), "yfinance" oder "auto"
    (Cache -> yfinance -> Snapshot).
    """
    if source in ("yfinance", "auto"):
        try:
            return _load_yfinance(ticker, start, end)
        except Exception as exc:  # Netz weg, Ticker unbekannt, ...
            if source == "yfinance":
                raise
            print(f"[data] yfinance nicht verfügbar ({exc!r}); nutze Snapshot.")
    col = _SNAPSHOT_ALIAS.get(ticker, ticker)
    s = load_snapshot()[col].rename(ticker)
    return s.loc[start:end]


def _load_yfinance(ticker: str, start: str | None, end: str | None) -> pd.Series:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{ticker.replace('^', '')}.csv"
    if path.exists():
        s = pd.read_csv(path, parse_dates=["Date"]).set_index("Date")[ticker]
    else:
        import yfinance as yf  # optional dependency
        df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
        if df.empty:
            raise RuntimeError("leerer Download")
        s = df["Close"].squeeze().rename(ticker)
        s.index.name = "Date"
        s.to_frame().to_csv(path)
    return s.loc[start:end]
