# Entscheidungslog (Architecture Decision Records)

Jede nicht-offensichtliche Entscheidung bekommt ein kurzes Dokument: **Kontext → Optionen → Entscheidung → Konsequenzen**.
Entscheidungen werden nicht gelöscht, sondern bei Bedarf durch ein neues ADR *ersetzt* (Status „ersetzt durch 00xx“).
So bleibt nachvollziehbar, warum etwas zu einem Zeitpunkt so gemacht wurde.

Spalte „Wer“: **F** = von Finbar vorgegeben, **C** = von Claude vorgeschlagen und umgesetzt, **F+C** = gemeinsam abgewogen.

| Nr. | Titel | Status | Wer |
|---|---|---|---|
| [0001](0001-arbeitsweise-und-dokumentation.md) | Arbeitsweise, Urheberschaft, Dokumentationsformat | akzeptiert | F |
| [0002](0002-datenquelle.md) | Datenquelle: eingecheckter Snapshot statt Live-Download | akzeptiert | C |
| [0003](0003-zeitachse-handelstage.md) | Zeitachse: Handelstage, Δ = 1/252 | akzeptiert | C |
| [0004](0004-parameterunsicherheit.md) | Bänder mit Parameterunsicherheit (t-Prädiktive) | akzeptiert | C |
| [0005](0005-exakte-simulation-vs-schemata.md) | Exakte Simulation für Prognosen, EM/Milstein nur zur Verifikation | akzeptiert | C |
| [0006](0006-validierung.md) | Validierung: Rolling-Origin, PIT, Log-Score statt Punktprognose-Fehler | akzeptiert | C |
| [0007](0007-reihenfolge-gbm-zuerst.md) | Reihenfolge: Aktien/GBM als verdaulicher Einstieg | akzeptiert | F |
| [0008](0008-prognosemaerkte-kein-gbm.md) | Prognosemärkte (Polymarket): warum GBM dort nicht passt | vorgemerkt | F+C |
