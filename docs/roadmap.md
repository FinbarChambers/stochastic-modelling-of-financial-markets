# Roadmap

Jedes Projekt beantwortet eine Schwäche, die im vorherigen **gemessen** wurde (ADR 0007).
Status: ✅ fertig · 🔨 in Arbeit · 📋 geplant

| # | Projekt | Motivation aus Vorgänger | Kernmathematik | Status |
|---|---|---|---|---|
| 1 | **GBM: Schätzung, Monte Carlo, Validierung** | Einstieg | Itô-Lemma, MLE, Fisher-Information, t-Prädiktive, EM/Milstein | ✅ |
| 2 | **Heston: stochastische Volatilität** | P1: ρ₁(\|r\|) ≈ 0,2–0,26 → Vol-Clustering; σ̂ hinkt Regimen hinterher | 2D-SDE, CIR-Prozess, Feller-Bedingung, Full-Truncation-Euler, Schätzung (z. B. über Realized Vol / Partikelfilter) | 📋 |
| 3 | **Merton: Sprungdiffusion** | P1: Exzess-Kurtosis 5–9, 4σ-Tage ~100× häufiger als normal | Poisson-Prozess, Itô-Formel mit Sprüngen, Mischungs-Likelihood | 📋 |
| 4 | **Ornstein-Uhlenbeck / Mean Reversion** | Gegenmodell zu „Kurs = Irrfahrt“, Pairs/Spreads | exakte Gauß-Übergänge, AR(1)-Äquivalenz, Halbwertszeit | 📋 |
| 5 | **Zinsen: Vasicek / CIR** | OU in der Anwendung, Daten von FRED/EZB | affine Modelle, Anleihepreise in geschlossener Form | 📋 (Option) |
| 6 | **Fokker-Planck & Black-Scholes ↔ Wärmeleitung** | Von Pfaden zu Dichten (Physik-Brücke) | Kolmogorov-Vorwärts/-Rückwärts, Feynman-Kac, Variablentransformation auf $u_t = u_{xx}$, Finite Differenzen vs. MC | 📋 |
| 7 | **Prognosemärkte (Polymarket)** | Beschränkte Martingale, siehe ADR 0008 | Logit-BM, Jacobi-Diffusion, Brier-Score | 📋 |
| 8 | **Agentenbasiert: Ising/Bornholdt-Markt** | Woher kommen fette Ränder und Clustering *mikroskopisch*? | Ising-Modell, Metropolis/Heat-Bath, Bornholdt-Spin-Modell, Zellularautomaten (Game-of-Life-Bezug) | 📋 |
| 9 | **Lean 4: formale Beweise** | Die wichtigsten diskreten Aussagen maschinell prüfen | Irrfahrt ist Martingal; Binomialmodell: No-Arbitrage ⇔ $d < 1+r < u$ | 📋 |

## Geplante Ordnerstruktur

```
projekte/
  01_gbm/            herleitung.md, run.py, ergebnisse.md, abbildungen/
  02_heston/
  03_merton/
  04_ou/
  05_zinsen/
  06_fokker_planck/
  07_prognosemaerkte/
  08_ising_markt/
src/stochmarkt/      gemeinsamer, getesteter Code (sde.py wird ab P2 wiederverwendet)
lean/                Lean-4-Projekt (lakefile), eigenes README
docs/entscheidungen/ ADRs über alle Projekte
```

Ordner werden erst angelegt, wenn das Projekt beginnt (keine leeren Platzhalter).
