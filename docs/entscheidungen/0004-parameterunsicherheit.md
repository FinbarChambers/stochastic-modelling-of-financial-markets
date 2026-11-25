# 0004 – Konfidenzbänder mit Parameterunsicherheit (t-Prädiktive)

**Status:** akzeptiert (2026-11-25) · **Wer:** Claude

## Kontext
Ein „Konfidenzband“ für zukünftige Kurse muss zwei Unsicherheiten enthalten: die Zufälligkeit der Zukunft
(Diffusion) und dass wir μ, σ nur geschätzt haben. Besonders μ ist sehr ungenau (`herleitung.md` §3).

## Optionen
| Option | Beschreibung | Bewertung |
|---|---|---|
| A: Plug-in | $X_h \sim N(\hat\nu h, \hat\sigma^2 h)$ | zu schmal, ignoriert SE(ν̂) |
| B: Parametrischer Bootstrap | Parameter neu schätzen auf simulierten Daten | korrekt, aber langsam und nur approximativ |
| C: exakte t-Prädiktive | $t_{n-1}$ mit Skala $\sqrt{(s_u^2/\Delta)(h + h^2/T)}$ | exakt unter GBM, geschlossen, schnell |

## Entscheidung
**C**, für Monte Carlo umgesetzt als Ziehung eines Parameterpaares pro Pfad aus der Normal-Inverse-χ²-Posterior.
C hat zwei Interpretationen mit demselben Ergebnis: frequentistisch (exakte Überdeckung, wenn GBM stimmt) und
bayesianisch (Prior ∝ 1/σ²). Herleitung in `herleitung.md` §4.2. Der Plug-in-Score wird im Backtest zum Vergleich
mitgeführt.

## Konsequenzen
+ Abweichungen im Backtest sind eindeutig *Modellfehler* (nicht Schätzfehler), weil die Bänder unter dem Modell exakt sind.
− Im Snapshot-Backtest ist C teils minimal schlechter als A, weil die Bänder dort ohnehin zu breit sind
  (siehe `ergebnisse.md` §4). Wir behalten C, weil es das korrekte Verfahren ist und das Problem woanders liegt.
