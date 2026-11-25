# 0008 – Prognosemärkte (Polymarket): warum GBM dort nicht passt

**Status:** vorgemerkt, noch nicht umgesetzt · **Wer:** Finbar (Idee), Claude (Analyse)

## Kontext
Kontrakte auf Polymarket zahlen 1 bei Eintreten eines Ereignisses, sonst 0. Der Preis $p_t \in [0,1]$ ist
(unter Risikoneutralität, ohne Gebühren/Zins) die Marktwahrscheinlichkeit und sollte ein **Martingal** sein:
$p_t = \mathbb E[\mathbf 1_A \mid \mathcal F_t]$.

## Warum GBM ungeeignet ist
1. GBM lebt auf $(0,\infty)$ und kann 1 überschreiten.
2. Der Endwert ist fast sicher 0 oder 1 (Auflösung); GBM hat eine lognormale, also nie degenerierte Verteilung.
3. Damit eine driftfreie Diffusion $dp = b(p)\,dW$ in $[0,1]$ bleibt, muss $b$ an *beiden* Rändern verschwinden. Bei GBM ist $b(p) = \sigma p$, das verschwindet nur bei 0.

## Kandidaten (für das spätere Projekt)
- **Logit-Brownsche Bewegung:** $Y = \operatorname{logit}(p)$, aber Martingal-Bedingung für $p$ erzwingt eine Drift in $Y$
  (Itô-Lemma auf $p = 1/(1+e^{-Y})$; Herleitung dann in der `herleitung.md` des Projekts).
- **Jacobi-/Wright-Fisher-Diffusion:** $dp = \sigma\sqrt{p(1-p)}\,dW$, driftfrei, Diffusion verschwindet am Rand.
- Validierung über **Brier-Score** und Kalibrierungsdiagramm, Daten über die öffentliche Gamma-/CLOB-API.

## Konsequenzen
Wird als eigenes Projekt nach den Aktienmodellen umgesetzt (siehe `docs/roadmap.md`).
