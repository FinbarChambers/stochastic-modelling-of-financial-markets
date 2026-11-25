# 0006 – Validierung: Rolling-Origin, PIT, Log-Score statt Punktprognose-Fehler

**Status:** akzeptiert (2026-11-25) · **Wer:** Claude

## Kontext
GBM liefert keine Punktprognose, sondern eine Verteilung. Ein RMSE zwischen Median und realem Kurs würde
bewerten, was das Modell gar nicht behauptet, und sagt nichts darüber, ob die *Breite* der Bänder stimmt.

## Entscheidung
1. **Rolling-Origin:** Ursprünge alle 21 Handelstage, Schätzfenster die letzten 3 Jahre, Horizonte 1/5/21/63 Tage.
   Nur Vergangenheitsdaten fließen in jede Prognose (kein Look-ahead).
2. **PIT-Histogramme und Überdeckung** für 50/80/95 %: prüfen Kalibrierung.
3. **Log-Score** gegen einen Benchmark: GBM mit μ = 0 (Kurs ist Martingal) und gleichem σ. Frage: Hilft die
   geschätzte Drift überhaupt?
4. **Diagnostik der Annahmen** (Schiefe, Kurtosis, Autokorrelation von r und |r|) vor der Prognose.

## Begründete Parameterwahl
- 3 Jahre: Kompromiss zwischen SE(σ̂) (braucht viele Punkte) und Anpassung an Regimewechsel (braucht kurze Fenster).
  **Nicht optimiert**, um Overfitting der Validierung zu vermeiden. Eine Sensitivitätsanalyse ist offen.
- 21 Tage Abstand: für h ≤ 21 nicht überlappend.

## Konsequenzen
+ Ehrliche, modellgerechte Bewertung; die Schwächen von GBM werden sichtbar statt versteckt.
− Nur ~71 Ursprünge pro Titel; Überlappung bei h = 63 macht Tests optimistisch (n_eff in Tabelle angegeben).
