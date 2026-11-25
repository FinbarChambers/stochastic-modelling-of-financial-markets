# Daten

## `snapshot/plotly_stockdata_2007_2016.csv`

- **Inhalt:** tägliche Schlusskurse von MSFT, IBM, SBUX, AAPL und S&P 500 (`GSPC`), 2007-01-03 bis 2016-03-01, 2306 Handelstage, keine Lücken.
- **Quelle:** öffentlicher Beispieldatensatz `stockdata.csv` aus dem Repository `plotly/datasets` auf GitHub
  (`https://raw.githubusercontent.com/plotly/datasets/master/stockdata.csv`), heruntergeladen am 2026-11-25. Ursprünglich Yahoo Finance.
- **Bereinigung:** nicht dokumentiert. Geprüft (Claude): keine Split-Sprünge (AAPL-Split 7:1 im Juni 2014 wäre
  ein Log-Sprung von −1,95; größter Tageswert ist 0,197 am 2008-09-29). Die AAPL-Werte (11,09 am 2007-01-03) passen zu
  split- und dividendenbereinigten Kursen. `GSPC` ist ein reiner Kursindex (ohne Dividenden).
- **Warum ein Snapshot:** ADR 0002.

## `cache/` (nicht versioniert)

Von `--source auto`/`yfinance` angelegte Downloads.
