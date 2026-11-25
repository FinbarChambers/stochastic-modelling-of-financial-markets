# 0001 – Arbeitsweise, Urheberschaft, Dokumentationsformat

**Status:** akzeptiert (2026-11-25) · **Wer:** Finbar (Vorgabe), Claude (Umsetzung)

## Kontext
Das Repository ist ein Lern- und Bewerbungsportfolio. Der Code wird von Claude (Anthropic) geschrieben. Finbar
möchte, dass jede Leserin und jeder Leser erkennen kann, *was* von Claude stammt, *wie* die Zusammenarbeit lief und
*warum* Entscheidungen so getroffen wurden. Mathematische Korrektheit hat Vorrang vor Umfang.

## Entscheidung
1. **Offenlegung:** `ARBEITSWEISE.md` beschreibt Rollen, Ablauf und Prüfstatus. Jedes Modul nennt Claude als Autor.
   Commits tragen einen `Co-Authored-By: Claude`-Trailer.
2. **Herleitungen getrennt vom Code:** pro Projekt eine `herleitung.md`; der Code verweist mit Abschnittsnummern darauf.
3. **Sichtbare Lücken:** Vorwissen (📘), übersprungene Algebra (✂️) und Heuristiken (💡) werden markiert
   (Finbars ständige Vorgabe, siehe `docs/konventionen.md`).
4. **Entscheidungen als ADRs** in diesem Ordner.
5. **Zahlen nur aus Code:** Ergebnistabellen werden von `run.py` in `ergebnisse.md` geschrieben, nie von Hand.
6. **Sprache:** Dokumentation und Kommentare Deutsch, Bezeichner im Code Englisch (übliche Fachbegriffe, bessere
   Lesbarkeit für internationale Leser des Codes).

## Konsequenzen
+ Nachvollziehbar und ehrlich; Fehler in Herleitungen sind leicht zu finden und einem Abschnitt zuzuordnen.
− Mehr Text als Code. Das ist für ein Lernportfolio gewollt.
