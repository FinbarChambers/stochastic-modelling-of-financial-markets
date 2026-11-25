# Projekt 1 – Mathematische Herleitungen

Dieses Dokument begründet jede Formel, die in `src/stochmarkt/gbm.py`, `sde.py` und `validation.py`
benutzt wird. Konventionen (siehe [`docs/konventionen.md`](../../docs/konventionen.md)):

> 📘 **Vorwissen:** markiert Resultate, die wir *ohne Beweis* benutzen, mit Quelle.
>
> ✂️ **Algebra übersprungen:** markiert Rechenschritte, die ausgelassen wurden, mit einer Anleitung, wie man sie nachrechnet.
>
> 💡 **Heuristik:** markiert Argumente, die die Idee zeigen, aber kein Beweis sind.

Zeit wird in Jahren gemessen, ein Handelstag ist $\Delta = 1/252$ (ADR 0003).

---

## 1. Das Modell und seine exakte Lösung

**Modell.** Der Kurs $S_t > 0$ folgt der Itô-SDE

$$
dS_t = \mu S_t\,dt + \sigma S_t\,dW_t, \qquad S_0 > 0,
$$

mit Brownscher Bewegung $W$, Drift $\mu \in \mathbb{R}$ und Volatilität $\sigma > 0$.
Interpretation: Die *relative* Änderung $dS/S$ hat konstanten Erwartungswert $\mu\,dt$ und konstante Varianz $\sigma^2 dt$.

> 📘 **Vorwissen (Itô-Lemma, eindimensional).** Ist $dX_t = a_t\,dt + b_t\,dW_t$ und $f \in C^2$, dann gilt
> $$df(X_t) = f'(X_t)\,dX_t + \tfrac12 f''(X_t)\,b_t^2\,dt.$$
> Der Zusatzterm gegenüber der gewöhnlichen Kettenregel kommt von der quadratischen Variation $(dW_t)^2 = dt$.
> Quelle: Øksendal, *Stochastic Differential Equations*, 6. Aufl., Thm. 4.1.2.

**Lösung.** Wende das Itô-Lemma auf $f(x) = \ln x$ an, mit $f'(x) = 1/x$, $f''(x) = -1/x^2$, $a_t = \mu S_t$, $b_t = \sigma S_t$:

$$
d\ln S_t = \frac{1}{S_t}\left(\mu S_t\,dt + \sigma S_t\,dW_t\right) - \frac12\,\frac{1}{S_t^2}\,\sigma^2 S_t^2\,dt
= \left(\mu - \tfrac12\sigma^2\right)dt + \sigma\,dW_t .
$$

Die rechte Seite hängt nicht mehr von $S$ ab, also kann man direkt integrieren:

$$
\ln S_t = \ln S_0 + \nu t + \sigma W_t, \qquad \boxed{\nu := \mu - \tfrac12\sigma^2}, \qquad
\boxed{S_t = S_0 \exp\!\left(\nu t + \sigma W_t\right)}.
$$

> ✂️ **Algebra übersprungen:** Dass dieses $S_t$ die SDE tatsächlich löst, prüft man durch Rückwärtsanwendung des Itô-Lemmas auf $g(t,w) = S_0 e^{\nu t + \sigma w}$ (zweidimensionale Version mit $\partial_t g = \nu g$, $\partial_w g = \sigma g$, $\partial_w^2 g = \sigma^2 g$). Eindeutigkeit folgt aus der Lipschitz-Stetigkeit der Koeffizienten (Øksendal Thm. 5.2.1).

**Erwartungswert und Median.**

> 📘 **Vorwissen:** Für $Z \sim N(0,1)$ ist $\mathbb{E}\,e^{aZ} = e^{a^2/2}$ (momenterzeugende Funktion der Normalverteilung).

Mit $W_t = \sqrt t\,Z$ folgt $\mathbb{E}[S_t] = S_0 e^{\nu t} e^{\sigma^2 t/2} = S_0 e^{\mu t}$.
Der **Median** ist dagegen $S_0 e^{\nu t}$, weil $\exp$ monoton ist und $\sigma W_t$ den Median 0 hat.
Der Unterschied $\mu$ vs. $\nu$ ist also *keine* Spitzfindigkeit: ein typischer Pfad wächst mit Rate $\nu$, der Mittelwert über Pfade mit $\mu$. Das ist der Grund, warum wir intern fast immer mit $\nu$ rechnen.

---

## 2. Maximum-Likelihood-Schätzung

**Daten.** Preise $S_{t_0}, \dots, S_{t_n}$ an äquidistanten Zeiten $t_i = t_0 + i\Delta$. Log-Renditen

$$ r_i := \ln S_{t_i} - \ln S_{t_{i-1}} = \nu\Delta + \sigma\left(W_{t_i} - W_{t_{i-1}}\right), \qquad i = 1,\dots,n .$$

Weil Brownsche Inkremente unabhängig und $N(0,\Delta)$-verteilt sind, gilt

$$ r_1, \dots, r_n \overset{\text{iid}}{\sim} N(m, v), \qquad m = \nu\Delta,\quad v = \sigma^2\Delta. $$

Das ist der zentrale Punkt: **GBM wird durch den Logarithmus auf das einfachste statistische Modell überhaupt zurückgeführt.**

*Warum reicht es, die Log-Renditen statt der Preise zu betrachten?* Gegeben $S_{t_0}$ ist $(S_{t_1},\dots,S_{t_n}) \mapsto (r_1,\dots,r_n)$ eine Bijektion, deren Jacobi-Determinante $\prod_i S_{t_i}^{-1}$ nicht von $(\mu,\sigma)$ abhängt. Die Likelihoods unterscheiden sich also nur um einen parameterfreien Faktor und haben dasselbe Maximum.

**Log-Likelihood.**

$$
\ell(m, v) = -\frac n2 \ln(2\pi v) - \frac{1}{2v}\sum_{i=1}^n (r_i - m)^2 .
$$

Ableitungen null setzen:

$$
\partial_m \ell = \frac1v \sum_i (r_i - m) = 0 \;\Rightarrow\; \hat m = \bar r := \frac1n\sum_i r_i,
\qquad
\partial_v \ell = -\frac{n}{2v} + \frac{1}{2v^2}\sum_i (r_i - m)^2 = 0 \;\Rightarrow\; \hat v = \frac1n \sum_i (r_i - \bar r)^2 .
$$

(Dass es ein Maximum ist: $\ell \to -\infty$ für $v \to 0$ und $v \to \infty$, und es gibt nur einen kritischen Punkt.)

**Zurück zu den Modellparametern.** Die MLE ist invariant unter Reparametrisierung (ist $\hat\theta$ MLE von $\theta$, dann ist $g(\hat\theta)$ MLE von $g(\theta)$ für bijektives $g$). Also

$$
\hat\sigma^2 = \hat v/\Delta, \qquad \hat\nu = \hat m/\Delta, \qquad \hat\mu = \hat\nu + \tfrac12\hat\sigma^2 .
$$

Code: `fit_mle` in `gbm.py`. Beachte: $\hat v$ hat Nenner $n$ (MLE, leicht verzerrt: $\mathbb E\hat v = \tfrac{n-1}{n}v$). Für die Vorhersagebänder (§4) brauchen wir die erwartungstreue Version $s_u^2 = \tfrac{n}{n-1}\hat v$; bei $n \approx 750$ ist der Unterschied 0,13 %.

---

## 3. Wie genau sind die Schätzer? (Das wichtigste Ergebnis des Projekts)

> 📘 **Vorwissen (Satz von Student/Cochran).** Für $r_i \overset{\text{iid}}{\sim} N(m,v)$ gilt exakt: $\bar r \sim N(m, v/n)$, $\; n\hat v / v \sim \chi^2_{n-1}$, und $\bar r$, $\hat v$ sind unabhängig. Quelle: z. B. Casella & Berger, *Statistical Inference*, Thm. 5.3.1.

**Drift.** Aus $\bar r \sim N(\nu\Delta, \sigma^2\Delta/n)$ folgt exakt

$$
\operatorname{Var}(\hat\nu) = \frac{1}{\Delta^2}\cdot\frac{\sigma^2\Delta}{n} = \frac{\sigma^2}{n\Delta} = \boxed{\frac{\sigma^2}{T}}, \qquad T := n\Delta .
$$

$\Delta$ ist herausgefallen. **Die Genauigkeit der Drift hängt nur von der Länge $T$ des Beobachtungszeitraums ab, nicht davon, wie oft man misst.** Intuition: $\hat\nu = (\ln S_{t_n} - \ln S_{t_0})/T$ ist eine Teleskopsumme, nur Anfangs- und Endpunkt zählen.

Zahlenbeispiel: $\sigma = 0{,}2$. Für $\operatorname{SE}(\hat\nu) = 1\,\%$ p. a. braucht man $T = (0{,}2/0{,}01)^2 = 400$ Jahre. Mit 9 Jahren Daten (unser Snapshot) ist $\operatorname{SE} \approx 7\,\%$ p. a., also so groß wie die Drift selbst. *Das ist der mathematische Kern der Aussage „Kursrichtungen sind kaum vorhersagbar“.* Getestet in `test_drift_se_depends_only_on_T_not_on_sampling`.

**Volatilität.** $\operatorname{Var}(\chi^2_{n-1}) = 2(n-1)$, also $\operatorname{Var}(\hat v) = 2(n-1)v^2/n^2 \approx 2v^2/n$ und $\operatorname{Var}(\hat\sigma^2) \approx 2\sigma^4/n$.

> 📘 **Vorwissen (Delta-Methode).** Ist $\hat\theta$ asymptotisch $N(\theta, \tau^2)$ und $g$ differenzierbar mit $g'(\theta)\neq0$, dann ist $g(\hat\theta)$ asymptotisch $N(g(\theta), g'(\theta)^2\tau^2)$.

Mit $g(x) = \sqrt x$, $g'(\sigma^2) = 1/(2\sigma)$:

$$ \operatorname{Var}(\hat\sigma) \approx \frac{1}{4\sigma^2}\cdot\frac{2\sigma^4}{n} = \frac{\sigma^2}{2n}. $$

Hier steht $n$, nicht $T$: **Volatilität wird durch häufigeres Messen beliebig genau** (im Modell; real begrenzt durch Mikrostruktur-Rauschen bei sehr hohen Frequenzen).

**Drift $\mu$.** $\hat\mu = \hat\nu + \hat\sigma^2/2$ mit unabhängigen Summanden, also

$$ \operatorname{Var}(\hat\mu) \approx \frac{\sigma^2}{T} + \frac14\cdot\frac{2\sigma^4}{n} = \frac{\sigma^2}{T} + \frac{\sigma^4}{2n}. $$

Der zweite Term ist bei Tagesdaten vernachlässigbar (S&P: $\approx 5\cdot10^{-7}$ vs. $5\cdot10^{-3}$). Ein Test (`test_mle_recovers_parameters_and_se_is_calibrated`) prüft an 400 synthetischen Datensätzen, dass $(\hat\theta-\theta)/\operatorname{SE}$ tatsächlich Mittel 0 und Streuung 1 hat.

---

## 4. Vorhersageverteilung und Konfidenzbänder

Gesucht: Verteilung von $X_h := \ln(S_{t+h}/S_t)$ für einen Horizont $h$ (Vielfaches von $\Delta$), gegeben die Daten bis $t$.

### 4.1 Plug-in (naiv)

Setze die Schätzer als wahr ein: $X_h \sim N(\hat\nu h, \hat\sigma^2 h)$. Das ignoriert, dass $\hat\nu$ selbst unsicher ist, und ist deshalb systematisch zu schmal.

### 4.2 Mit Parameterunsicherheit (verwendet; ADR 0004)

*Frequentistisch, exakt.* Unter dem Modell ist $X_h \sim N(\nu h, \sigma^2 h)$ unabhängig von den Daten der Vergangenheit (unabhängige Inkremente), und $\hat\nu \sim N(\nu, \sigma^2/T)$. Also

$$ X_h - \hat\nu h \sim N\!\left(0,\; \sigma^2 h + h^2\frac{\sigma^2}{T}\right) = N\!\left(0,\; \sigma^2 h\left(1 + \frac hT\right)\right). $$

Ersetzt man das unbekannte $\sigma^2$ durch $s_u^2/\Delta$ (unabhängig von $\hat\nu$ nach Student/Cochran, $\chi^2_{n-1}$-verteilt), entsteht genau wie beim klassischen $t$-Test eine Studentsche $t$-Verteilung:

$$
\boxed{\;\frac{X_h - \hat\nu h}{\sqrt{(s_u^2/\Delta)\,(h + h^2/T)}} \sim t_{n-1}\;}
$$

> ✂️ **Algebra übersprungen:** Der Schritt zur $t$-Verteilung ist die Definition $t_k = Z/\sqrt{Q/k}$ mit $Z\sim N(0,1)$, $Q\sim\chi^2_k$ unabhängig. Hier $Z = (X_h - \hat\nu h)/\sqrt{\sigma^2(h+h^2/T)}$ und $Q = (n-1)s_u^2/(\sigma^2\Delta)$; $\sigma$ kürzt sich heraus.

Diese Bänder haben also **exakte** Überdeckung, *falls GBM stimmt*. Abweichungen im Backtest (§6) sind damit eindeutig Modellfehler, nicht Schätzfehler.

*Bayesianisch, dasselbe Ergebnis.* Mit der Prior $p(\nu,\sigma^2) \propto 1/\sigma^2$ ist die Posterior

$$ \sigma^2\Delta \mid \text{Daten} \sim \text{Scaled-Inv-}\chi^2(n-1, s_u^2), \qquad \nu \mid \sigma^2, \text{Daten} \sim N(\hat\nu, \sigma^2/T), $$

> ✂️ **Algebra übersprungen / 📘 Vorwissen:** Herleitung durch Ausmultiplizieren von Likelihood × Prior, quadratische Ergänzung in $\nu$ und Ausintegrieren; Standardergebnis in Gelman et al., *Bayesian Data Analysis*, 3. Aufl., §3.2.

und die posterior-prädiktive Verteilung von $X_h$ ist dieselbe $t_{n-1}$ wie oben. `sample_posterior` zieht $(\mu,\sigma)$ aus dieser Posterior, damit der Monte Carlo (ein Parameterpaar pro Pfad) die Parameterunsicherheit enthält. `test_posterior_matches_predictive_t` prüft, dass MC und analytische Formel übereinstimmen.

**Größenordnung:** Für $h = 63$ Tage $= 0{,}25$ J und $T = 3$ J ist $1 + h/T = 1{,}083$, das Band wird um $\sqrt{1{,}083}-1 \approx 4\,\%$ breiter. Für $h = T$ wäre es $\sqrt2$-mal so breit. Die Drift-Unsicherheit wächst mit $h^2$, die Diffusion nur mit $h$.

### 4.3 Von Log-Renditen zu Preisbändern

$\exp$ ist streng monoton, also ist das $q$-Quantil von $S_{t+h}$ gleich $S_t \exp(q\text{-Quantil von }X_h)$ (`price_quantiles`). Die Bänder sind deshalb asymmetrisch um den Median und es gibt keine negativen Preise.

---

## 5. Numerische Verfahren: Euler-Maruyama vs. Milstein

### 5.1 Verfahren

Für $dX = a(X)\,dt + b(X)\,dW$ und Schritt $\Delta t$, $\Delta W_k \sim N(0,\Delta t)$:

$$
\text{EM:}\quad X_{k+1} = X_k + a(X_k)\Delta t + b(X_k)\Delta W_k,
$$
$$
\text{Milstein:}\quad X_{k+1} = X_k + a(X_k)\Delta t + b(X_k)\Delta W_k + \tfrac12 b(X_k)b'(X_k)\left(\Delta W_k^2 - \Delta t\right).
$$

**Woher kommt der Milstein-Term?** Exakt gilt $X_{t+\Delta t} = X_t + \int_t^{t+\Delta t} a(X_s)\,ds + \int_t^{t+\Delta t} b(X_s)\,dW_s$. EM friert $a$ und $b$ am linken Rand ein. Milstein entwickelt $b$ eine Ordnung weiter: Nach Itô ist $b(X_s) \approx b(X_t) + b'(X_t)\,b(X_t)\,(W_s - W_t)$ (der dominante Teil von $dX$ ist $b\,dW$, Größe $\sqrt{\Delta t}$). Eingesetzt:

$$ \int_t^{t+\Delta t} b(X_s)\,dW_s \approx b\,\Delta W + b b' \int_t^{t+\Delta t} (W_s - W_t)\,dW_s . $$

> ✂️ **Algebra übersprungen:** $\int_t^{t+\Delta t}(W_s - W_t)\,dW_s = \tfrac12\left(\Delta W^2 - \Delta t\right)$. Nachrechnen: Itô-Lemma auf $f(w) = w^2/2$ für den Prozess $W_s - W_t$ gibt $d\tfrac12(W_s-W_t)^2 = (W_s - W_t)\,dW_s + \tfrac12 ds$, dann integrieren.

Für GBM: $a(x) = \mu x$, $b(x) = \sigma x$, $b'(x) = \sigma$, also $\tfrac12 bb' = \tfrac12\sigma^2 x$.

### 5.2 Warum Ordnung ½ bzw. 1? (lokaler Vergleich für GBM)

Exakter Schritt: $X_{k+1}/X_k = \exp(\nu\Delta t + \sigma\Delta W)$. Taylor bis Ordnung $\Delta t$ (beachte $\Delta W = O(\sqrt{\Delta t})$):

$$ e^{\nu\Delta t + \sigma\Delta W} = 1 + \nu\Delta t + \sigma\Delta W + \tfrac12\sigma^2\Delta W^2 + O(\Delta t^{3/2})
= 1 + \mu\Delta t + \sigma\Delta W + \tfrac12\sigma^2(\Delta W^2 - \Delta t) + O(\Delta t^{3/2}). $$

Die zweite Gleichung nutzt $\nu = \mu - \sigma^2/2$. **Milstein ist exakt die Taylor-Entwicklung bis $O(\Delta t)$; EM fehlt der Term $\tfrac12\sigma^2(\Delta W^2 - \Delta t)$.**

> 💡 **Heuristik (kein Beweis).** Der fehlende EM-Term hat Erwartungswert 0 und Standardabweichung $\propto \Delta t$. Über $N = T/\Delta t$ Schritte addieren sich solche unabhängigen Fehler wie eine Irrfahrt: Gesamtfehler $\propto \sqrt N\,\Delta t = \sqrt{T\Delta t}$, also **starke Ordnung ½**. Bei Milstein ist der lokale Fehler $O(\Delta t^{3/2})$, mit demselben Argument global $\sqrt N\,\Delta t^{3/2} \propto \Delta t$: **starke Ordnung 1**.
> Der rigorose Beweis (für allgemeine $a,b$ mit Lipschitz- und Wachstumsbedingungen): Kloeden & Platen, *Numerical Solution of SDEs*, Thm. 10.2.2 (EM) und 10.3.5 (Milstein).

### 5.3 Schwacher Fehler exakt ausgerechnet

Für $f(x) = x$: $\mathbb E[X_{k+1}\mid X_k] = X_k(1 + \mu\Delta t)$ bei beiden Verfahren (der Milstein-Term hat bedingten Erwartungswert 0). Induktiv $\mathbb E X_N = S_0(1+\mu\Delta t)^N$, während $\mathbb E S_T = S_0 e^{\mu T}$.

$$ N\ln(1+\mu\Delta t) = N\left(\mu\Delta t - \tfrac12\mu^2\Delta t^2 + O(\Delta t^3)\right) = \mu T - \tfrac12\mu^2 T\Delta t + O(\Delta t^2) $$

$$ \Rightarrow\quad \left|S_0 e^{\mu T} - S_0(1+\mu\Delta t)^N\right| = S_0 e^{\mu T}\cdot\tfrac12\mu^2 T\,\Delta t + O(\Delta t^2). $$

**Schwache Ordnung 1 für beide**, mit der Konstante $\tfrac12 S_0 e^{\mu T}\mu^2 T$. Kontrolle gegen `ergebnisse.md`: $\mu = 0{,}06$, $T = 1$, $\Delta t = 1/4$ ergibt $1{,}062\cdot 0{,}0018\cdot 0{,}25 \approx 4{,}8\cdot10^{-4}$, wie in der Abbildung. Vorteil dieser Formel: Sie hat kein Monte-Carlo-Rauschen, das bei kleinem $\Delta t$ den winzigen Fehler überdecken würde (sieht man an den grauen Kreuzen in `05_konvergenz.png`).

**Fazit für spätere Projekte:** Für *Verteilungen und Erwartungswerte* (Optionspreise, Bänder) ist schwache Ordnung entscheidend, und da sind EM und Milstein gleich. Milstein lohnt sich, wenn Pfade selbst zählen (pfadabhängige Größen, Multilevel-Monte-Carlo). Bei Heston ist $b(v) = \xi\sqrt v$ nicht Lipschitz bei 0, dann gelten die Sätze oben nicht direkt; das wird in Projekt 2 Thema.

---

## 6. Wie man testet, ob die Bänder stimmen

> 📘 **Vorwissen (Probability Integral Transform).** Hat $X$ eine stetige Verteilungsfunktion $F$, dann ist $F(X) \sim U(0,1)$. Quelle: Diebold, Gunther & Tay (1998), *Int. Economic Review* 39(4).

Ist die Vorhersageverteilung $F_{\text{pred}}$ korrekt, sind die PIT-Werte $u = F_{\text{pred}}(x_{\text{real}})$ gleichverteilt. Das zentrale $p$-Intervall entspricht $u \in [\tfrac{1-p}2, \tfrac{1+p}2]$, die empirische Überdeckung ist der Anteil der $u$ darin. Interpretation der Abweichungen:

| Befund | Bedeutung |
|---|---|
| Überdeckung auf allen Niveaus zu hoch | Bänder zu breit, $\sigma$ überschätzt |
| auf allen Niveaus zu niedrig | Bänder zu schmal |
| 50 % zu hoch, 95 % zu niedrig | wahre Verteilung spitzer mit fetteren Rändern |
| PIT-Histogramm schief | Drift systematisch falsch |

**Log-Score** $\log f_{\text{pred}}(x_{\text{real}})$: eine *strikt echte* Bewertungsregel (Gneiting & Raftery 2007, *JASA* 102), d. h. im Erwartungswert maximiert nur die wahre Verteilung den Score. Wir benutzen ihn nur zum Vergleich zweier Modelle auf denselben Daten: GBM mit geschätzter Drift gegen GBM mit $\mu = 0$ (Martingal-Kurs).

**Einschränkung:** Bei Horizont $h$ größer als der Abstand der Ursprünge (21 Tage) überlappen die Zielfenster, die $u$ sind korreliert. Der KS-Test setzt Unabhängigkeit voraus und ist dann zu optimistisch.

---

## Literatur

- B. Øksendal, *Stochastic Differential Equations*, 6. Aufl., Springer 2003.
- P. Kloeden, E. Platen, *Numerical Solution of Stochastic Differential Equations*, Springer 1992.
- D. Higham, „An Algorithmic Introduction to Numerical Simulation of SDEs“, *SIAM Review* 43(3), 2001. (sehr lesbar, empfohlener Einstieg)
- P. Glasserman, *Monte Carlo Methods in Financial Engineering*, Springer 2003, Kap. 3 und 6.
- G. Casella, R. Berger, *Statistical Inference*, 2. Aufl., 2002.
- A. Gelman et al., *Bayesian Data Analysis*, 3. Aufl., 2013.
- T. Gneiting, A. Raftery, „Strictly Proper Scoring Rules, Prediction, and Estimation“, *JASA* 102, 2007.
- R. Cont, „Empirical properties of asset returns: stylized facts and statistical issues“, *Quantitative Finance* 1, 2001.
