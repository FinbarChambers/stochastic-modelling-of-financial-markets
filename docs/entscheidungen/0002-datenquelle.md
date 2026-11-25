# 0002 – Datenquelle: eingecheckter Snapshot statt Live-Download

**Status:** akzeptiert (2026-11-25) · **Wer:** Claude

## Kontext
Geplant war `yfinance`. In der Cloud-Umgebung, in der Claude den Code ausgeführt hat, war Yahoo Finance durch die
Netzwerkrichtlinie gesperrt. Unabhängig davon revidiert Yahoo historische Daten (Dividendenanpassung), d. h. ein
Live-Download liefert in einem Jahr leicht andere Zahlen.

## Optionen
| Option | + | − |
|---|---|---|
| A: nur yfinance | aktuell, beliebige Ticker | nicht reproduzierbar, braucht Netz |
| B: eingecheckter Snapshot | exakt reproduzierbar, offline | alter Zeitraum (2007–2016), 5 Titel |
| C: B als Standard, A optional | beides | etwas mehr Code |

## Entscheidung
**C.** `load_prices(..., source="snapshot")` ist Standard; `--source auto` versucht yfinance (Cache in `data/cache/`,
nicht versioniert) und fällt sonst auf den Snapshot zurück. Herkunft des Snapshots: `data/README.md`.

## Konsequenzen
+ Alle Zahlen in `ergebnisse.md` sind bit-genau reproduzierbar (fester Seed).
+ Der Zeitraum enthält die Finanzkrise 2008, ein lehrreicher Stresstest für GBM.
− Die Anpassungsmethode des Snapshots ist nicht dokumentiert (geprüft: keine Split-Sprünge, max. |r| liegt auf
  Krisentagen). `^GSPC` ist ein Preisindex ohne Dividenden, also ist $\hat\mu$ dort die Kursdrift, nicht die Gesamtrendite.
− **Offen:** Finbar kann lokal `python projekte/01_gbm/run.py --source auto` laufen lassen und aktuelle Daten vergleichen.
