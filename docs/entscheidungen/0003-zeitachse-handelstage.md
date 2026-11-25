# 0003 – Zeitachse: Handelstage, Δ = 1/252

**Status:** akzeptiert (2026-11-25) · **Wer:** Claude

## Kontext
Die MLE in `herleitung.md` §2 setzt äquidistante Beobachtungen voraus. Kurse gibt es nur an Handelstagen; zwischen
Freitag und Montag liegen 3 Kalendertage.

## Optionen
- **A: Handelstag-Zeit.** Jeder Handelstag ist ein Schritt Δ = 1/252 Jahr. Annahme: Am Wochenende vergeht keine
  „Marktzeit“.
- **B: Kalenderzeit.** Δ_i = tatsächlicher Abstand; Likelihood mit ungleichen Varianzen σ²Δ_i.

## Entscheidung
**A.** Empirisch ist die Varianz von Freitag→Montag-Renditen deutlich kleiner als das Dreifache einer normalen
Tagesrendite (French & Roll 1986, *J. Financial Economics* 17), Information kommt vor allem bei offenem Markt.
A ist also näher an den Daten und hält die Mathematik einfach (iid).

## Konsequenzen
+ Geschlossene MLE-Formeln, exakte Verteilungsresultate (Student/Cochran) gelten.
− Feiertage und Wochenenden werden ignoriert; σ ist „pro Handelsjahr“. Für Vergleich mit Optionsmärkten (Kalenderzeit)
  muss man umrechnen.
