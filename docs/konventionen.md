# Konventionen

## Markierungen in Herleitungen

Finbars feste Vorgabe: Es muss immer sichtbar sein, wo Wissen vorausgesetzt oder Rechnung ausgelassen wird.

| Symbol | Bedeutung | Pflichtangabe |
|---|---|---|
| 📘 **Vorwissen** | Resultat wird ohne Beweis benutzt | Quelle mit Satznummer |
| ✂️ **Algebra übersprungen** | Rechenschritt ausgelassen | Anleitung zum Nachrechnen |
| 💡 **Heuristik** | zeigt die Idee, ist kein Beweis | Verweis auf rigorosen Beweis |

Alles, was nicht markiert ist, soll mit Schulwissen + Analysis I/II + Grundlagen W-Theorie direkt nachvollziehbar sein.

## Notation

| Symbol | Bedeutung |
|---|---|
| $S_t$ | Kurs zur Zeit $t$ (Jahre) |
| $W_t$ | Standard-Brownsche Bewegung |
| $\mu$ | Drift von $S$: $\mathbb E S_t = S_0 e^{\mu t}$ |
| $\sigma$ | Volatilität pro $\sqrt{\text{Jahr}}$ |
| $\nu = \mu - \sigma^2/2$ | Log-Drift, Wachstumsrate des Medians |
| $\Delta$ | Beobachtungsabstand, ein Handelstag $= 1/252$ |
| $r_i$ | Log-Rendite $\ln(S_{t_i}/S_{t_{i-1}})$ |
| $n$, $T = n\Delta$ | Anzahl Renditen, Fensterlänge in Jahren |
| $h$ | Prognosehorizont in Jahren |
| $X_h$ | $\ln(S_{t+h}/S_t)$ |
| $\hat\cdot$ | MLE; $s_u^2$ erwartungstreue Varianz (Nenner $n-1$) |

## Code

- Bezeichner Englisch, Kommentare und Docstrings Deutsch, Verweise auf `herleitung.md §x`.
- Zufallszahlen nur über `np.random.Generator` mit festem Seed.
- Jede Formel aus einer Herleitung hat einen Test gegen eine bekannte Antwort (synthetische Daten).
- Ergebniszahlen nur aus `run.py` → `ergebnisse.md`.
