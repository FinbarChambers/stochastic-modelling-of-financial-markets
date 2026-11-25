"""Allgemeine Diskretisierungsverfahren für skalare Itô-SDEs  dX = a(X) dt + b(X) dW.

Für GBM gibt es eine exakte Lösung; wir benutzen sie hier als *Testfall mit bekannter
Antwort*, um die Verfahren zu verifizieren, bevor sie in späteren Projekten (Heston,
CIR, ...) ohne exakte Lösung eingesetzt werden (ADR 0005).

Euler-Maruyama:  X_{k+1} = X_k + a dt + b dW
Milstein:        X_{k+1} = X_k + a dt + b dW + 1/2 b b' (dW^2 - dt)

Konvergenzordnungen (Kloeden & Platen 1992, Thm. 10.2.2 und 10.3.5; unter globalen
Lipschitz- und Wachstumsbedingungen an a, b, die für GBM erfüllt sind):
    stark:  EM 1/2, Milstein 1       (E|X_T - X^dt_T| <= C dt^gamma)
    schwach: beide 1                  (|E f(X_T) - E f(X^dt_T)| <= C dt^beta)
"""
from __future__ import annotations

from typing import Callable

import numpy as np

Func = Callable[[np.ndarray], np.ndarray]


def euler_maruyama(a: Func, b: Func, x0: float, dW: np.ndarray, dt: float) -> np.ndarray:
    """dW: (n_paths, n_steps). Rückgabe: Endwerte X_T, Form (n_paths,)."""
    x = np.full(dW.shape[0], x0, dtype=float)
    for k in range(dW.shape[1]):
        x = x + a(x) * dt + b(x) * dW[:, k]
    return x


def milstein(a: Func, b: Func, db: Func, x0: float, dW: np.ndarray, dt: float) -> np.ndarray:
    x = np.full(dW.shape[0], x0, dtype=float)
    for k in range(dW.shape[1]):
        w = dW[:, k]
        bx = b(x)
        x = x + a(x) * dt + bx * w + 0.5 * bx * db(x) * (w * w - dt)
    return x


def coarsen(dW_fine: np.ndarray, factor: int) -> np.ndarray:
    """Summiert je `factor` feine Brownsche Inkremente zu einem groben.

    Wichtig für den *starken* Fehler: grobe und exakte Lösung müssen auf demselben
    Brownschen Pfad leben, sonst misst man nur die Streuung zweier unabhängiger Pfade.
    """
    n_paths, n_fine = dW_fine.shape
    assert n_fine % factor == 0
    return dW_fine.reshape(n_paths, n_fine // factor, factor).sum(axis=2)


def gbm_convergence_study(mu: float, sigma: float, S0: float = 1.0, T: float = 1.0,
                          levels: tuple[int, ...] = (2, 3, 4, 5, 6, 7, 8, 9, 10),
                          n_paths: int = 20_000, seed: int = 0) -> dict:
    """Stark- und Schwachfehler von EM und Milstein für GBM gegen die exakte Lösung.

    levels: dt = T / 2^level.  Feinstes Gitter: 2^max(levels) Schritte.

    Schwacher Fehler wird für f(x) = x zusätzlich *analytisch* berechnet: Da
    E[dW]=0 und E[dW^2-dt]=0 und die Inkremente unabhängig von X_k sind, gilt für
    beide Verfahren exakt E[X_N] = S0 (1 + mu dt)^N, während E[S_T] = S0 e^{mu T}.
    Damit ist der Schwachfehler frei von Monte-Carlo-Rauschen bestimmbar
    (herleitung.md, Abschnitt 5.3).
    """
    rng = np.random.default_rng(seed)
    n_fine = 2 ** max(levels)
    dt_fine = T / n_fine
    dW_fine = rng.standard_normal((n_paths, n_fine)) * np.sqrt(dt_fine)
    W_T = dW_fine.sum(axis=1)
    exact = S0 * np.exp((mu - 0.5 * sigma**2) * T + sigma * W_T)

    a = lambda x: mu * x
    b = lambda x: sigma * x
    db = lambda x: sigma * np.ones_like(x)

    out = {"dt": [], "strong_em": [], "strong_mil": [], "strong_em_se": [], "strong_mil_se": [],
           "weak_em_mc": [], "weak_mil_mc": [], "weak_mc_se": [], "weak_analytic": []}
    for lev in levels:
        N = 2**lev
        dt = T / N
        dW = coarsen(dW_fine, n_fine // N)
        x_em = euler_maruyama(a, b, S0, dW, dt)
        x_mil = milstein(a, b, db, S0, dW, dt)
        e_em = np.abs(x_em - exact)
        e_mil = np.abs(x_mil - exact)
        out["dt"].append(dt)
        out["strong_em"].append(e_em.mean())
        out["strong_mil"].append(e_mil.mean())
        out["strong_em_se"].append(e_em.std(ddof=1) / np.sqrt(n_paths))
        out["strong_mil_se"].append(e_mil.std(ddof=1) / np.sqrt(n_paths))
        # Schwachfehler per MC: gemeinsamer Pfad -> Differenz hat viel kleinere Varianz
        # als zwei unabhängige Stichproben (Common Random Numbers).
        out["weak_em_mc"].append(abs(np.mean(x_em - exact)))
        out["weak_mil_mc"].append(abs(np.mean(x_mil - exact)))
        out["weak_mc_se"].append(np.std(x_em - exact, ddof=1) / np.sqrt(n_paths))
        out["weak_analytic"].append(abs(S0 * np.exp(mu * T) - S0 * (1 + mu * dt) ** N))
    return {k: np.array(v) for k, v in out.items()}


def fitted_order(dt: np.ndarray, err: np.ndarray) -> float:
    """Steigung der Regression log(err) = log(C) + gamma log(dt)."""
    return float(np.polyfit(np.log(dt), np.log(err), 1)[0])
