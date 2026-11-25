# Arbeitsweise: Wer hat was gemacht?

> **Kurz:** Der gesamte Code, die Herleitungen und die Dokumentation in diesem Repository wurden von **Claude**
> (KI-Assistent von Anthropic) geschrieben. **Finbar** hat Ziel, Themen, Prioritäten und Qualitätsanspruch vorgegeben,
> Entscheidungen getroffen oder bestätigt und prüft die Ergebnisse. Dieses Dokument macht die Zusammenarbeit transparent.

## Rollen

| | Finbar | Claude |
|---|---|---|
| Themenwahl, Reihenfolge, Umfang | ✔ entscheidet | schlägt vor |
| Anspruch (mathematische Korrektheit, Offenlegung, Begründungen) | ✔ gibt vor | setzt um |
| Modellwahl und Methodik im Detail | bestätigt / verwirft | ✔ schlägt mit Abwägung vor (ADRs) |
| Code, Tests, Abbildungen | – | ✔ schreibt und führt aus |
| Herleitungen | prüft | ✔ schreibt |
| Schlussfolgerungen | ✔ letzte Instanz | formuliert, mit Belegen aus `ergebnisse.md` |

## Ablauf

1. Finbar formuliert ein Ziel im Chat (Auszüge unten im Prompt-Protokoll).
2. Claude plant, wägt Optionen ab und dokumentiert jede nicht-offensichtliche Wahl als ADR in
   [`docs/entscheidungen/`](docs/entscheidungen/). Die Spalte „Wer“ zeigt, wer entschieden hat.
3. Claude schreibt Herleitung, Code und Tests, führt alles aus und legt die Ergebnisse ab.
4. Die Arbeit kommt als Pull Request; Finbar liest, fragt nach, fordert Änderungen an und merged.

## Was Claude selbst geprüft hat (und was nicht)

- ✔ Jede zentrale Formel hat einen Test gegen synthetische Daten mit bekannter Antwort (`tests/`), alle bestehen.
- ✔ Monte Carlo und analytische Formeln stimmen überein (Abweichung < 1 %, reines MC-Rauschen).
- ✔ Gemessene Konvergenzordnungen stimmen mit der Theorie überein.
- ✘ Ein KI-Modell kann sich in Herleitungen irren. Was Finbar Zeile für Zeile nachgerechnet hat, steht im Prüfstatus.

## Prüfstatus durch Finbar

| Dokument | Status |
|---|---|
| `projekte/01_gbm/herleitung.md` §1–§2 | ⏳ offen |
| `projekte/01_gbm/herleitung.md` §3–§4 | ⏳ offen |
| `projekte/01_gbm/herleitung.md` §5–§6 | ⏳ offen |
| ADRs 0002–0006 | ⏳ offen |

## Prompt-Protokoll (Finbars Vorgaben, wörtlich bzw. sinngemäß)

**2026-11-25, Projektstart**
> „Wichtig ist mir hier die mathematische Kohärenz. Das heißt, wenn jemand das liest, kann er wissen, dass die Codes etc.
> von dir sind und wie ich mit dir gearbeitet habe. Lass uns das also dokumentieren. Wichtig ist die mathematische
> Richtigkeit, die Abwägung der Modelle und die Entscheidungsfindung, wieso wir etwas gemacht haben, wie wir es gemacht haben.“

Gewünschter Inhalt Projekt 1: μ, σ per MLE aus historischen Daten, Monte-Carlo-Pfade, Konfidenzbänder gegen reale
Out-of-sample-Kurse, Vergleich Euler-Maruyama vs. Milstein. Ehrlichkeit darüber, dass Kurse kaum vorhersagbar sind.

**Ständige Vorgabe:** „Immer sichtbar machen, wenn Vorwissen ausgelassen oder extrem viel Algebra übersprungen wird.“
→ umgesetzt als Markierungen 📘 ✂️ 💡 ([`docs/konventionen.md`](docs/konventionen.md)).

**2026-11-25, Reihenfolge**
> „Wir behandeln erst etwas Verdaubares, damit es auch für einen Leser verständlicher ist.“ → ADR 0007.
Prognosemärkte (Polymarket) und Zinsmodelle als spätere Projekte vorgemerkt → ADR 0008, Roadmap.
