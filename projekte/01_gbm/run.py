"""Projekt 1: GBM schätzen, simulieren, out-of-sample prüfen, Verfahren vergleichen.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python projekte/01_gbm/run.py                # reproduzierbar mit Snapshot-Daten
    python projekte/01_gbm/run.py --source auto  # versucht yfinance

Erzeugt abbildungen/*.png und ergebnisse.md (alle Zahlen im README stammen von dort).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from stochmarkt.data import load_prices  # noqa: E402
from stochmarkt.gbm import (TRADING_DAYS, exact_paths, fit_mle, sample_posterior,  # noqa: E402
                            plugin_logreturn_dist, predictive_logreturn_dist, price_quantiles)
from stochmarkt.sde import gbm_convergence_study, fitted_order  # noqa: E402
from stochmarkt.validation import rolling_backtest, summarize, return_diagnostics  # noqa: E402

FIG = HERE / "abbildungen"
TICKERS = ["^GSPC", "AAPL", "MSFT", "IBM", "SBUX"]
SEED = 20261125
plt.rcParams.update({"figure.dpi": 110, "savefig.dpi": 150, "axes.grid": True, "grid.alpha": 0.3,
                     "font.size": 9})
C_DATA, C_MODEL, C_ALT = "#1f2937", "#2563eb", "#d97706"


def fmt(x, d=3):
    return f"{x:.{d}f}"


def section_estimates(prices: dict[str, pd.Series], md: list[str]):
    md.append("## 1. MLE auf dem gesamten Datensatz (2007-01-03 bis 2016-03-01)\n")
    md.append("| Ticker | n | T [J] | μ̂ ± SE | σ̂ ± SE | ν̂ = μ̂−σ̂²/2 ± SE | 95%-KI für μ |")
    md.append("|---|---|---|---|---|---|---|")
    for tk, s in prices.items():
        f = fit_mle(s.to_numpy())
        lo, hi = f.mu - 1.96 * f.se_mu, f.mu + 1.96 * f.se_mu
        md.append(f"| {tk} | {f.n} | {fmt(f.T,2)} | {fmt(f.mu)} ± {fmt(f.se_mu)} | "
                  f"{fmt(f.sigma)} ± {fmt(f.se_sigma, 4)} | {fmt(f.nu)} ± {fmt(f.se_nu)} | "
                  f"[{fmt(lo)}, {fmt(hi)}] |")
    md.append("\nLesart: σ ist auf wenige Promille genau bestimmt, μ dagegen kaum. Das ist kein "
              "Datenproblem, sondern Mathematik: SE(ν̂) = σ/√T hängt nur von der Gesamtdauer ab "
              "(herleitung.md §3).\n")


def section_diagnostics(prices, md):
    md.append("## 2. Prüfung der Modellannahme „Log-Renditen iid normal“\n")
    md.append("| Ticker | Schiefe | Exzess-Kurtosis | Jarque-Bera p | ρ₁(r) | ρ₁(\\|r\\|) | Anteil \\|r\\|>4sd (normal: 6.3e-05) |")
    md.append("|---|---|---|---|---|---|---|")
    for tk, s in prices.items():
        d = return_diagnostics(s)
        md.append(f"| {tk} | {fmt(d['skew'],2)} | {fmt(d['excess_kurtosis'],1)} | "
                  f"{d['jarque_bera_p']:.1e} | {fmt(d['acf1_r'],3)} | {fmt(d['acf1_abs_r'],3)} | "
                  f"{d['frac_beyond_4sd']:.1e} |")
    md.append("\nLesart: Normalität wird für alle Titel klar verworfen (fette Ränder). "
              "|ρ₁(r)| ist klein (≤ 0.1, also kaum lineare Vorhersagbarkeit), ρ₁(|r|) ≈ 0.2–0.26 dagegen "
              "deutlich (Standardfehler ≈ 1/√n ≈ 0.02): "
              "Volatilität ist *nicht* konstant, sondern clustert. Genau das motiviert "
              "Heston (Projekt 2) und Sprünge (Projekt 3).\n")

    s = prices["^GSPC"]
    r = np.diff(np.log(s.to_numpy()))
    z = (r - r.mean()) / r.std()
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.2))
    xs = np.linspace(-8, 8, 400)
    ax[0].hist(z, bins=120, density=True, color=C_DATA, alpha=0.6, label="S&P 500, standardisiert")
    ax[0].plot(xs, stats.norm.pdf(xs), color=C_MODEL, label="N(0,1) (GBM)")
    ax[0].set_yscale("log"); ax[0].set_ylim(1e-4, 1); ax[0].set_xlim(-8, 8)
    ax[0].set_title("Dichte (log-Skala): fette Ränder"); ax[0].legend(fontsize=7)
    (osm, osr), _ = stats.probplot(z, dist="norm")
    ax[1].plot(osm, osr, ".", ms=2, color=C_DATA); ax[1].plot([-4, 4], [-4, 4], color=C_MODEL)
    ax[1].set_title("QQ-Plot gegen N(0,1)"); ax[1].set_xlabel("theoretisch"); ax[1].set_ylabel("empirisch")
    lags = np.arange(1, 41)
    def acf(x, k):
        x = x - x.mean(); return np.dot(x[:-k], x[k:]) / np.dot(x, x)
    ax[2].bar(lags - 0.2, [acf(r, k) for k in lags], width=0.4, color=C_DATA, label="r")
    ax[2].bar(lags + 0.2, [acf(np.abs(r), k) for k in lags], width=0.4, color=C_ALT, label="|r|")
    ax[2].axhline(1.96 / np.sqrt(r.size), color="gray", ls="--", lw=0.8)
    ax[2].axhline(-1.96 / np.sqrt(r.size), color="gray", ls="--", lw=0.8)
    ax[2].set_title("Autokorrelation: Vol-Clustering"); ax[2].set_xlabel("Lag [Tage]"); ax[2].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(FIG / "01_rendite_diagnostik.png"); plt.close(fig)


def fan_panel(ax, s: pd.Series, fit_start, fit_end, horizon_days, rng, title):
    fit_s = s.loc[fit_start:fit_end]
    f = fit_mle(fit_s.to_numpy())
    S0 = fit_s.iloc[-1]
    future = s.loc[fit_s.index[-1]:].iloc[: horizon_days + 1]
    H = len(future) - 1
    h = np.arange(1, H + 1) / TRADING_DAYS
    # Monte Carlo inkl. Parameterunsicherheit: pro Pfad ein Parameterpaar aus der Posterior
    n_paths = 20_000
    mu_s, sig_s = sample_posterior(f, n_paths, rng)
    paths = exact_paths(S0, mu_s, sig_s, T=H / TRADING_DAYS, n_steps=H, n_paths=n_paths, rng=rng)
    qs = [0.025, 0.1, 0.25, 0.5, 0.75, 0.9, 0.975]
    mcq = np.quantile(paths[:, 1:], qs, axis=0)
    anq = price_quantiles(S0, predictive_logreturn_dist(f, h), qs)
    x = future.index[1:]
    ax.plot(fit_s.index[-250:], fit_s.iloc[-250:], color=C_DATA, lw=1)
    for i, a in [(0, 0.15), (1, 0.2), (2, 0.25)]:
        ax.fill_between(x, mcq[i], mcq[-1 - i], color=C_MODEL, alpha=a, lw=0)
    ax.plot(x, mcq[3], color=C_MODEL, lw=1, label="Median (MC)")
    ax.plot(x, anq[0], color="k", ls=":", lw=0.8, label="2.5/97.5 % analytisch")
    ax.plot(x, anq[-1], color="k", ls=":", lw=0.8)
    for p in paths[:5]:
        ax.plot(x, p[1:], color=C_MODEL, lw=0.4, alpha=0.6)
    ax.plot(x, future.iloc[1:], color=C_ALT, lw=1.3, label="realisiert (out-of-sample)")
    ax.axvline(fit_s.index[-1], color="gray", lw=0.8)
    ax.set_title(f"{title}\nFit {fit_s.index[0]:%Y-%m}–{fit_s.index[-1]:%Y-%m}: "
                 f"μ̂={f.mu:.2f}±{f.se_mu:.2f}, σ̂={f.sigma:.2f}", fontsize=8)
    ax.legend(fontsize=6, loc="upper left")
    inside = np.mean((future.iloc[1:].to_numpy() >= anq[0]) & (future.iloc[1:].to_numpy() <= anq[-1]))
    maxdev = np.max(np.abs(mcq - anq) / anq)
    return f, inside, maxdev


def section_fan(prices, md, rng):
    md.append("## 3. Fächerdiagramme: Monte Carlo vs. realisierter Kurs\n")
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
    s = prices["^GSPC"]
    _, in1, d1 = fan_panel(ax[0], s, "2012-01-01", "2014-12-31", 252, rng, "S&P 500, ruhige Phase")
    _, in2, d2 = fan_panel(ax[1], s, "2005-01-01", "2008-08-29", 252, rng, "S&P 500, in die Finanzkrise")
    fig.tight_layout(); fig.savefig(FIG / "02_faecher_oos.png"); plt.close(fig)
    md.append(f"Bänder: 50/80/95 % zentral, Posterior-prädiktiv (inkl. Parameterunsicherheit), "
              f"20 000 Pfade. Maximale relative Abweichung MC-Quantil vs. analytisches Quantil: "
              f"{d1:.2%} bzw. {d2:.2%} (reines MC-Rauschen, Konsistenzcheck).\n")
    md.append(f"Anteil Handelstage, an denen der reale Kurs im 95 %-Band lag: ruhige Phase "
              f"{in1:.0%}, Krise {in2:.0%}. Achtung: Das ist *ein* Pfad, die Tage sind stark "
              f"korreliert; aussagekräftig ist erst Abschnitt 4.\n")


def realized_vol_after(prices, tab, days=63):
    vals = []
    for tk, g in tab[tab.h_days == tab.h_days.min()].groupby("ticker"):
        r = np.diff(np.log(prices[tk].to_numpy()))
        for o in g.origin:
            i = prices[tk].index.get_loc(o)
            vals.append(r[i:i + days].std(ddof=1) * np.sqrt(TRADING_DAYS))
    return float(np.mean(vals))


def section_backtest(prices, md):
    md.append("## 4. Rolling-Origin-Backtest (Fenster 3 Jahre, neuer Ursprung alle 21 Handelstage)\n")
    md.append("Soll-Überdeckung: 50 / 80 / 95 %. KS-p: Kolmogorov-Smirnov-Test der PIT-Werte auf "
              "Gleichverteilung (bei Überlappung h>21 zu optimistisch). Log-Score: mittlere "
              "Log-Dichte des realisierten Werts, höher = besser.\n")
    md.append("| Ticker | h [Tage] | n (n_eff) | Cov50 | Cov80 | Cov95 | KS-p | LS prädiktiv | LS plug-in | LS Martingal (μ=0) |")
    md.append("|---|---|---|---|---|---|---|---|---|---|")
    all_tabs = {}
    for tk, s in prices.items():
        bt = rolling_backtest(s)
        sm = summarize(bt)
        all_tabs[tk] = bt
        for _, r in sm.iterrows():
            md.append(f"| {tk} | {int(r.h_days)} | {int(r.n)} ({int(r.n_eff)}) | {r.cov50:.2f} | "
                      f"{r.cov80:.2f} | {r.cov95:.2f} | {r.ks_p:.2g} | {r.ls_pred:.3f} | "
                      f"{r.ls_plugin:.3f} | {r.ls_mart:.3f} |")
    # Aggregat über alle Ticker
    tab = pd.concat([b.table.assign(ticker=k) for k, b in all_tabs.items()])
    md.append("\n**Aggregiert über alle 5 Titel:**\n")
    md.append("| h [Tage] | Cov50 | Cov80 | Cov95 | ΔLS (GBM-Drift − Martingal) |")
    md.append("|---|---|---|---|---|")
    for hd, g in tab.groupby("h_days"):
        u = g.pit_pred.to_numpy()
        c = [np.mean((u >= (1 - p) / 2) & (u <= (1 + p) / 2)) for p in (0.5, 0.8, 0.95)]
        md.append(f"| {hd} | {c[0]:.2f} | {c[1]:.2f} | {c[2]:.2f} | {(g.ls_pred - g.ls_mart).mean():+.4f} |")
    agg = tab.groupby("h_days").apply(
        lambda g: pd.Series({p: np.mean((g.pit_pred >= (1 - p) / 2) & (g.pit_pred <= (1 + p) / 2))
                             for p in (0.5, 0.95)}), include_groups=False)
    too_wide = bool((agg[0.5] > 0.5).all() and (agg[0.95] > 0.95).all())
    md.append("\nLesart (Muster aus den Zahlen oben, für den Snapshot geprüft):")
    if too_wide:
        md.append("- Die Überdeckung ist auf *allen* Niveaus zu hoch, die Bänder sind also zu breit. "
                  "Reine fette Ränder würden anders aussehen (50 % zu hoch, aber 95 % zu niedrig). "
                  "Ursache ist hier vor allem Nicht-Stationarität: Die Testursprünge liegen in "
                  f"{tab.origin.min():%Y}–{tab.origin.max():%Y}, die 3-Jahres-Fenster enthalten "
                  "aber lange die Krisen-Volatilität 2008/09. σ̂ hinkt dem Regime hinterher: "
                  f"mittleres σ̂ = {tab.sigma.mean():.3f}, realisierte Volatilität der jeweils "
                  f"folgenden 63 Tage = {realized_vol_after(prices, tab):.3f} (Mittel über Titel und Ursprünge).")
    else:
        md.append("- Abweichungen der Überdeckung vom Soll: siehe Tabelle; Interpretation je Niveau.")
    d21 = (tab.ls_pred - tab.ls_mart)[tab.h_days == 21]
    md.append(f"- ΔLS (h=21) hat Mittel {d21.mean():+.4f} bei Standardabweichung {d21.std():.3f} pro Ursprung, "
              "ist also weit innerhalb des Rauschens, und hat je nach "
              "Titel unterschiedliches Vorzeichen. Dass es im Mittel leicht positiv ist, passt zu "
              "einem Bullenmarkt im Testzeitraum und ist kein Beleg für Prognosefähigkeit der Drift.")
    md.append("- Der prädiktive Log-Score ist hier oft etwas *schlechter* als Plug-in: Die "
              "Parameterunsicherheit verbreitert Bänder, die ohnehin schon zu breit sind. Das Prinzip "
              "bleibt richtig; es zeigt nur, dass der dominante Fehler das Modell ist, nicht die Schätzung.")
    md.append(f"- Nur {tab.origin.nunique()} Ursprünge pro Titel und Titel untereinander korreliert: "
              "Unterschiede in der zweiten Nachkommastelle der Überdeckung sind nicht signifikant.\n")

    fig, ax = plt.subplots(1, 4, figsize=(12, 2.8), sharey=True)
    for a, (hd, g) in zip(ax, tab.groupby("h_days")):
        a.hist(g.pit_pred, bins=20, range=(0, 1), density=True, color=C_MODEL, alpha=0.7)
        a.axhline(1, color="k", lw=0.8, ls="--")
        a.set_title(f"PIT, h = {hd} Tage (alle Titel)", fontsize=8)
        a.set_xlabel("u = F_pred(x_real)")
    ax[0].set_ylabel("Dichte (Soll: 1)")
    fig.tight_layout(); fig.savefig(FIG / "03_pit_histogramme.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(5, 3.4))
    nominal = np.linspace(0.05, 0.99, 30)
    for hd, g in tab.groupby("h_days"):
        u = g.pit_pred.to_numpy()
        emp = [np.mean((u >= (1 - p) / 2) & (u <= (1 + p) / 2)) for p in nominal]
        ax.plot(nominal, emp, label=f"h = {hd} Tage")
    ax.plot([0, 1], [0, 1], "k--", lw=0.8, label="perfekt kalibriert")
    ax.set_xlabel("nominelle Überdeckung"); ax.set_ylabel("empirische Überdeckung")
    ax.set_title("Kalibrierung der GBM-Bänder (alle Titel)", fontsize=9); ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(FIG / "04_kalibrierung.png"); plt.close(fig)


def section_convergence(prices, md):
    f = fit_mle(prices["^GSPC"].to_numpy())
    md.append("## 5. Euler-Maruyama vs. Milstein\n")
    cases = [("S&P-Parameter", f.mu, f.sigma), ("Stressparameter", 0.5, 0.8)]
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
    md.append("| Parameter | μ | σ | Ordnung stark EM | stark Milstein | schwach (analytisch) |")
    md.append("|---|---|---|---|---|---|")
    for a, (name, mu, sig) in zip(ax, cases):
        res = gbm_convergence_study(mu, sig, n_paths=20_000, seed=SEED)
        dt = res["dt"]
        o = (fitted_order(dt, res["strong_em"]), fitted_order(dt, res["strong_mil"]),
             fitted_order(dt, res["weak_analytic"]))
        md.append(f"| {name} | {mu:.3f} | {sig:.3f} | {o[0]:.3f} | {o[1]:.3f} | {o[2]:.3f} |")
        a.errorbar(dt, res["strong_em"], yerr=1.96 * res["strong_em_se"], fmt="o-", ms=3,
                   color=C_MODEL, label=f"stark EM (≈{o[0]:.2f})")
        a.errorbar(dt, res["strong_mil"], yerr=1.96 * res["strong_mil_se"], fmt="s-", ms=3,
                   color=C_ALT, label=f"stark Milstein (≈{o[1]:.2f})")
        a.plot(dt, res["weak_analytic"], "^-", ms=3, color="k", label=f"schwach, beide, exakt (≈{o[2]:.2f})")
        a.plot(dt, res["weak_em_mc"], "x", color="gray", label="schwach EM, MC-Schätzung")
        ref = res["strong_em"][0] * (dt / dt[0]) ** 0.5
        a.plot(dt, ref, ":", color=C_MODEL, lw=0.8, label="Referenz ∝ Δt^½")
        a.plot(dt, res["strong_mil"][0] * (dt / dt[0]), ":", color=C_ALT, lw=0.8, label="Referenz ∝ Δt")
        a.set_xscale("log", base=2); a.set_yscale("log")
        a.set_xlabel("Δt [Jahre]"); a.set_ylabel("Fehler"); a.set_title(f"{name}: μ={mu:.2f}, σ={sig:.2f}, T=1, S0=1", fontsize=8)
        a.legend(fontsize=6)
    fig.tight_layout(); fig.savefig(FIG / "05_konvergenz.png"); plt.close(fig)
    md.append("\nStarker Fehler: E|X_T − S_T| auf demselben Brownschen Pfad (20 000 Pfade, "
              "Δt = 2⁻² … 2⁻¹⁰). Schwacher Fehler für f(x)=x exakt: |e^{μT} − (1+μΔt)^N|. "
              "Die MC-Schätzung des Schwachfehlers wird bei kleinem Δt vom MC-Rauschen dominiert; "
              "deshalb die analytische Formel (herleitung.md §5.3).\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="snapshot", choices=["snapshot", "auto", "yfinance"])
    args = ap.parse_args()
    FIG.mkdir(exist_ok=True)
    rng = np.random.default_rng(SEED)
    prices = {tk: load_prices(tk, source=args.source) for tk in TICKERS}
    md = ["# Ergebnisse Projekt 1 (automatisch erzeugt von run.py, nicht von Hand editieren)\n",
          f"Datenquelle: `{args.source}`, Seed {SEED}.\n"]
    section_estimates(prices, md)
    section_diagnostics(prices, md)
    section_fan(prices, md, rng)
    section_backtest(prices, md)
    section_convergence(prices, md)
    (HERE / "ergebnisse.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
