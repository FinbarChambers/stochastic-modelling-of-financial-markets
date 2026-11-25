# Stochastische Modellierung von Finanzmärkten

Brownsche Bewegung, SDEs und Monte Carlo, **getestet an historischen Marktdaten**; später Märkte als zelluläre
Automaten (Ising/Bornholdt) und formale Beweise zentraler Aussagen in Lean.

> **Urheberschaft:** Code, Herleitungen und Texte wurden von **Claude** (Anthropic) geschrieben, unter Leitung von
> **Finbar Chambers** (Themen, Anspruch, Entscheidungen, Prüfung). Wie wir zusammengearbeitet haben und was geprüft
> ist: [`ARBEITSWEISE.md`](ARBEITSWEISE.md).

> **Ehrlichkeit vorweg:** Aktienkurse sind mit diesen Modellen *nicht* in dem Sinne vorhersagbar, dass man die Richtung
> kennt. Projekt 1 zeigt mathematisch, warum (Standardfehler der Drift $=\sigma/\sqrt T$). Was man modellieren und
> testen kann, ist die **Verteilung** möglicher Kurse. Das Ziel hier ist saubere Modellierung und ehrliche Validierung.

## Projekte

| # | Thema | Status |
|---|---|---|
| 1 | [GBM: MLE, Monte Carlo, Out-of-sample-Bänder, Euler-Maruyama vs. Milstein](projekte/01_gbm/) | ✅ |
| 2–9 | Heston, Merton-Sprünge, OU, Zinsen, Fokker-Planck/Black-Scholes, Prognosemärkte, Ising-Markt, Lean | 📋 [Roadmap](docs/roadmap.md) |

## Aufbau

```
ARBEITSWEISE.md          Zusammenarbeit Finbar ↔ Claude, Prüfstatus, Prompt-Protokoll
docs/konventionen.md     Notation, Markierungen für Vorwissen (📘), ausgelassene Algebra (✂️), Heuristik (💡)
docs/entscheidungen/     Entscheidungslog (ADRs): warum wir was wie gemacht haben
docs/roadmap.md          Geplante Projekte und ihre Motivation
src/stochmarkt/          Gemeinsamer, getesteter Code
projekte/NN_name/        Je Projekt: herleitung.md, run.py, ergebnisse.md, abbildungen/
tests/                   Tests gegen bekannte Antworten
data/                    Daten-Snapshot und Herkunft
```

## Schnellstart

```bash
pip install -e ".[dev,daten]"
pytest                                  # 7 Tests, ~2 s
python projekte/01_gbm/run.py           # reproduziert ergebnisse.md und alle Abbildungen
python projekte/01_gbm/run.py --source auto   # mit aktuellen yfinance-Daten (Netz nötig)
```

Python ≥ 3.10, numpy, scipy, pandas, matplotlib.
