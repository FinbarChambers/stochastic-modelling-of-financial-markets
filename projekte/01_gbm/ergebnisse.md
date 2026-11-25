# Ergebnisse Projekt 1 (automatisch erzeugt von run.py, nicht von Hand editieren)

Datenquelle: `snapshot`, Seed 20261125.

## 1. MLE auf dem gesamten Datensatz (2007-01-03 bis 2016-03-01)

| Ticker | n | T [J] | μ̂ ± SE | σ̂ ± SE | ν̂ = μ̂−σ̂²/2 ± SE | 95%-KI für μ |
|---|---|---|---|---|---|---|
| ^GSPC | 2305 | 9.15 | 0.060 ± 0.072 | 0.216 ± 0.0032 | 0.037 ± 0.072 | [-0.080, 0.200] |
| AAPL | 2305 | 9.15 | 0.299 ± 0.112 | 0.339 ± 0.0050 | 0.241 ± 0.112 | [0.079, 0.518] |
| MSFT | 2305 | 9.15 | 0.128 ± 0.095 | 0.289 ± 0.0043 | 0.086 ± 0.095 | [-0.059, 0.315] |
| IBM | 2305 | 9.15 | 0.082 ± 0.076 | 0.229 ± 0.0034 | 0.056 ± 0.076 | [-0.066, 0.231] |
| SBUX | 2305 | 9.15 | 0.200 ± 0.111 | 0.336 ± 0.0050 | 0.144 ± 0.111 | [-0.018, 0.418] |

Lesart: σ ist auf wenige Promille genau bestimmt, μ dagegen kaum. Das ist kein Datenproblem, sondern Mathematik: SE(ν̂) = σ/√T hängt nur von der Gesamtdauer ab (herleitung.md §3).

## 2. Prüfung der Modellannahme „Log-Renditen iid normal“

| Ticker | Schiefe | Exzess-Kurtosis | Jarque-Bera p | ρ₁(r) | ρ₁(\|r\|) | Anteil \|r\|>4sd (normal: 6.3e-05) |
|---|---|---|---|---|---|---|
| ^GSPC | -0.31 | 9.3 | 0.0e+00 | -0.105 | 0.258 | 6.9e-03 |
| AAPL | -0.45 | 6.6 | 0.0e+00 | -0.003 | 0.230 | 4.3e-03 |
| MSFT | 0.21 | 9.2 | 0.0e+00 | -0.057 | 0.230 | 6.5e-03 |
| IBM | -0.14 | 5.2 | 0.0e+00 | -0.014 | 0.218 | 5.6e-03 |
| SBUX | 0.28 | 5.8 | 0.0e+00 | -0.030 | 0.209 | 6.5e-03 |

Lesart: Normalität wird für alle Titel klar verworfen (fette Ränder). |ρ₁(r)| ist klein (≤ 0.1, also kaum lineare Vorhersagbarkeit), ρ₁(|r|) ≈ 0.2–0.26 dagegen deutlich (Standardfehler ≈ 1/√n ≈ 0.02): Volatilität ist *nicht* konstant, sondern clustert. Genau das motiviert Heston (Projekt 2) und Sprünge (Projekt 3).

## 3. Fächerdiagramme: Monte Carlo vs. realisierter Kurs

Bänder: 50/80/95 % zentral, Posterior-prädiktiv (inkl. Parameterunsicherheit), 20 000 Pfade. Maximale relative Abweichung MC-Quantil vs. analytisches Quantil: 0.43% bzw. 0.89% (reines MC-Rauschen, Konsistenzcheck).

Anteil Handelstage, an denen der reale Kurs im 95 %-Band lag: ruhige Phase 100%, Krise 42%. Achtung: Das ist *ein* Pfad, die Tage sind stark korreliert; aussagekräftig ist erst Abschnitt 4.

## 4. Rolling-Origin-Backtest (Fenster 3 Jahre, neuer Ursprung alle 21 Handelstage)

Soll-Überdeckung: 50 / 80 / 95 %. KS-p: Kolmogorov-Smirnov-Test der PIT-Werte auf Gleichverteilung (bei Überlappung h>21 zu optimistisch). Log-Score: mittlere Log-Dichte des realisierten Werts, höher = besser.

| Ticker | h [Tage] | n (n_eff) | Cov50 | Cov80 | Cov95 | KS-p | LS prädiktiv | LS plug-in | LS Martingal (μ=0) |
|---|---|---|---|---|---|---|---|---|---|
| ^GSPC | 1 | 71 (71) | 0.66 | 0.83 | 0.96 | 0.24 | 3.032 | 3.032 | 3.030 |
| ^GSPC | 5 | 71 (71) | 0.69 | 0.92 | 0.96 | 0.16 | 2.322 | 2.323 | 2.321 |
| ^GSPC | 21 | 71 (71) | 0.75 | 0.94 | 0.99 | 0.024 | 1.692 | 1.699 | 1.696 |
| ^GSPC | 63 | 71 (24) | 0.77 | 0.96 | 0.99 | 0.035 | 1.165 | 1.190 | 1.194 |
| AAPL | 1 | 71 (71) | 0.70 | 0.87 | 0.99 | 0.16 | 2.661 | 2.661 | 2.666 |
| AAPL | 5 | 71 (71) | 0.72 | 0.90 | 1.00 | 0.17 | 1.936 | 1.939 | 1.933 |
| AAPL | 21 | 71 (71) | 0.59 | 0.87 | 0.97 | 0.44 | 1.154 | 1.160 | 1.134 |
| AAPL | 63 | 71 (24) | 0.66 | 0.86 | 0.92 | 0.093 | 0.487 | 0.493 | 0.448 |
| MSFT | 1 | 71 (71) | 0.59 | 0.83 | 0.99 | 0.64 | 2.785 | 2.785 | 2.785 |
| MSFT | 5 | 71 (71) | 0.62 | 0.85 | 0.99 | 0.19 | 2.015 | 2.016 | 2.012 |
| MSFT | 21 | 71 (71) | 0.56 | 0.85 | 0.99 | 0.41 | 1.264 | 1.268 | 1.257 |
| MSFT | 63 | 71 (24) | 0.65 | 0.87 | 0.99 | 0.55 | 0.706 | 0.717 | 0.691 |
| IBM | 1 | 71 (71) | 0.56 | 0.85 | 0.97 | 0.14 | 3.001 | 3.002 | 3.009 |
| IBM | 5 | 71 (71) | 0.63 | 0.87 | 0.97 | 0.32 | 2.241 | 2.242 | 2.245 |
| IBM | 21 | 71 (71) | 0.73 | 0.90 | 0.99 | 0.056 | 1.557 | 1.563 | 1.574 |
| IBM | 63 | 71 (24) | 0.65 | 0.93 | 0.99 | 0.0033 | 1.008 | 1.027 | 1.054 |
| SBUX | 1 | 71 (71) | 0.62 | 0.92 | 0.99 | 0.15 | 2.698 | 2.699 | 2.692 |
| SBUX | 5 | 71 (71) | 0.75 | 0.93 | 0.99 | 0.026 | 1.917 | 1.919 | 1.895 |
| SBUX | 21 | 71 (71) | 0.70 | 0.94 | 0.99 | 0.099 | 1.223 | 1.231 | 1.194 |
| SBUX | 63 | 71 (24) | 0.73 | 0.94 | 0.99 | 0.016 | 0.639 | 0.661 | 0.569 |

**Aggregiert über alle 5 Titel:**

| h [Tage] | Cov50 | Cov80 | Cov95 | ΔLS (GBM-Drift − Martingal) |
|---|---|---|---|---|
| 1 | 0.63 | 0.86 | 0.98 | -0.0010 |
| 5 | 0.68 | 0.89 | 0.98 | +0.0048 |
| 21 | 0.67 | 0.90 | 0.98 | +0.0068 |
| 63 | 0.69 | 0.91 | 0.97 | +0.0098 |

Lesart (Muster aus den Zahlen oben, für den Snapshot geprüft):
- Die Überdeckung ist auf *allen* Niveaus zu hoch, die Bänder sind also zu breit. Reine fette Ränder würden anders aussehen (50 % zu hoch, aber 95 % zu niedrig). Ursache ist hier vor allem Nicht-Stationarität: Die Testursprünge liegen in 2010–2015, die 3-Jahres-Fenster enthalten aber lange die Krisen-Volatilität 2008/09. σ̂ hinkt dem Regime hinterher: mittleres σ̂ = 0.271, realisierte Volatilität der jeweils folgenden 63 Tage = 0.214 (Mittel über Titel und Ursprünge).
- ΔLS (h=21) hat Mittel +0.0068 bei Standardabweichung 0.219 pro Ursprung, ist also weit innerhalb des Rauschens, und hat je nach Titel unterschiedliches Vorzeichen. Dass es im Mittel leicht positiv ist, passt zu einem Bullenmarkt im Testzeitraum und ist kein Beleg für Prognosefähigkeit der Drift.
- Der prädiktive Log-Score ist hier oft etwas *schlechter* als Plug-in: Die Parameterunsicherheit verbreitert Bänder, die ohnehin schon zu breit sind. Das Prinzip bleibt richtig; es zeigt nur, dass der dominante Fehler das Modell ist, nicht die Schätzung.
- Nur 71 Ursprünge pro Titel und Titel untereinander korreliert: Unterschiede in der zweiten Nachkommastelle der Überdeckung sind nicht signifikant.

## 5. Euler-Maruyama vs. Milstein

| Parameter | μ | σ | Ordnung stark EM | stark Milstein | schwach (analytisch) |
|---|---|---|---|---|---|
| S&P-Parameter | 0.060 | 0.216 | 0.494 | 0.990 | 0.999 |
| Stressparameter | 0.500 | 0.800 | 0.485 | 0.972 | 0.986 |

Starker Fehler: E|X_T − S_T| auf demselben Brownschen Pfad (20 000 Pfade, Δt = 2⁻² … 2⁻¹⁰). Schwacher Fehler für f(x)=x exakt: |e^{μT} − (1+μΔt)^N|. Die MC-Schätzung des Schwachfehlers wird bei kleinem Δt vom MC-Rauschen dominiert; deshalb die analytische Formel (herleitung.md §5.3).

