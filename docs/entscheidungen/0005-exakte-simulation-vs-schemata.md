# 0005 – Exakte Simulation für Prognosen, EM/Milstein nur zur Verifikation

**Status:** akzeptiert (2026-11-25) · **Wer:** Claude

## Kontext
Für GBM gibt es eine exakte Lösung, Diskretisierungsverfahren sind also eigentlich unnötig. Finbar wollte trotzdem
den Vergleich Euler-Maruyama vs. Milstein.

## Entscheidung
- **Prognosen und Bänder** nutzen `exact_paths` (Fehler null durch Diskretisierung).
- **EM und Milstein** werden *allgemein* für $dX = a(X)dt + b(X)dW$ implementiert (`sde.py`) und an GBM gegen die
  exakte Lösung verifiziert, mit gemessenen Konvergenzordnungen als Test.

## Begründung
GBM ist der seltene Fall mit bekannter Antwort, also der ideale Prüfstand. Ab Projekt 2 (Heston) gibt es keine
exakte Lösung mehr; dann wird derselbe, hier geprüfte Code verwendet.

## Konsequenzen
+ Verfahren mit Test, bevor sie gebraucht werden.
+ Messbar: stark EM ≈ 0,49, Milstein ≈ 0,99, schwach beide ≈ 1,00 (`ergebnisse.md` §5).
− Die Python-Schleife über Zeitschritte ist langsam; für Projekt 2 ggf. vektorisieren oder `numba`.
