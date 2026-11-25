"""Out-of-Sample-Validierung von Vorhersageverteilungen (ADR 0006).

Rolling-Origin-Backtest: an jedem Ursprung t wird nur mit Daten aus [t-W, t] geschätzt,
dann wird die Verteilung von X_h = ln(S_{t+h}/S_t) für mehrere Horizonte h prognostiziert
und mit dem realisierten Wert verglichen.

Kennzahlen
- PIT u = F_pred(x_real). Ist das Modell korrekt kalibriert, gilt u ~ U(0,1).
- Überdeckung: Anteil realisierter Werte im zentralen p-Intervall; Soll = p.
- Mittlerer Log-Score: mean log f_pred(x_real), höher = besser. Nur zum *Vergleich*
  zweier Modelle auf denselben Daten aussagekräftig.

Ehrlicher Hinweis: Für h > Schrittweite zwischen Ursprüngen überlappen die Zielfenster,
die PIT-Werte sind dann korreliert. Die Binomial-Konfidenz für die Überdeckung ist dann
zu optimistisch; wir geben deshalb die effektive Anzahl unabhängiger Fenster mit an.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from .gbm import GBMFit, fit_mle, plugin_logreturn_dist, predictive_logreturn_dist, TRADING_DAYS


@dataclass
class BacktestResult:
    table: pd.DataFrame       # eine Zeile pro (Ursprung, Horizont)
    window_days: int
    step_days: int


def rolling_backtest(prices: pd.Series, window_days: int = 3 * TRADING_DAYS,
                     horizons_days: tuple[int, ...] = (1, 5, 21, 63),
                     step_days: int = 21) -> BacktestResult:
    p = prices.to_numpy(float)
    dates = prices.index
    rows = []
    hmax = max(horizons_days)
    for t in range(window_days, len(p) - hmax, step_days):
        fit = fit_mle(p[t - window_days: t + 1])
        for hd in horizons_days:
            h = hd / TRADING_DAYS
            x = np.log(p[t + hd] / p[t])
            d_plug = plugin_logreturn_dist(fit, h)
            d_pred = predictive_logreturn_dist(fit, h)
            # Benchmark: Martingal-Preis (mu = 0  <=>  nu = -sigma^2/2), gleiches sigma
            d_mart = stats.norm(loc=-0.5 * fit.sigma**2 * h, scale=fit.sigma * np.sqrt(h))
            rows.append(dict(origin=dates[t], h_days=hd, x=x, mu=fit.mu, sigma=fit.sigma,
                             pit_plugin=d_plug.cdf(x), pit_pred=d_pred.cdf(x),
                             pit_mart=d_mart.cdf(x),
                             ls_plugin=d_plug.logpdf(x), ls_pred=d_pred.logpdf(x),
                             ls_mart=d_mart.logpdf(x)))
    return BacktestResult(pd.DataFrame(rows), window_days, step_days)


def coverage(pit: np.ndarray, level: float) -> float:
    """Zentrales Intervall [ (1-p)/2, (1+p)/2 ] im PIT-Raum."""
    lo, hi = (1 - level) / 2, (1 + level) / 2
    return float(np.mean((pit >= lo) & (pit <= hi)))


def summarize(bt: BacktestResult, levels=(0.5, 0.8, 0.95), pit_col="pit_pred") -> pd.DataFrame:
    out = []
    for hd, g in bt.table.groupby("h_days"):
        row = {"h_days": hd, "n": len(g),
               "n_eff": int(np.ceil(len(g) * min(1.0, bt.step_days / hd)))}
        for lv in levels:
            row[f"cov{int(lv*100)}"] = coverage(g[pit_col].to_numpy(), lv)
        row["ls_pred"] = g["ls_pred"].mean()
        row["ls_plugin"] = g["ls_plugin"].mean()
        row["ls_mart"] = g["ls_mart"].mean()
        row["ks_p"] = stats.kstest(g[pit_col], "uniform").pvalue
        out.append(row)
    return pd.DataFrame(out)


def return_diagnostics(prices: pd.Series) -> dict:
    """Prüft die GBM-Annahme 'Log-Renditen iid normal'."""
    r = np.diff(np.log(prices.to_numpy(float)))
    jb = stats.jarque_bera(r)

    def acf(x, lag):
        x = x - x.mean()
        return float(np.dot(x[:-lag], x[lag:]) / np.dot(x, x))

    return {"n": r.size,
            "skew": float(stats.skew(r)),
            "excess_kurtosis": float(stats.kurtosis(r)),  # 0 für Normalverteilung
            "jarque_bera_p": float(jb.pvalue),
            "acf1_r": acf(r, 1),
            "acf1_abs_r": acf(np.abs(r), 1),
            "acf1_r2": acf(r**2, 1),
            "frac_beyond_4sd": float(np.mean(np.abs(r - r.mean()) > 4 * r.std())),
            "normal_frac_beyond_4sd": float(2 * stats.norm.sf(4))}
