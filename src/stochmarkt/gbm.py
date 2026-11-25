"""Geometrische Brownsche Bewegung (GBM): exakte Lösung, MLE, Vorhersageverteilungen.

Modell (Itô-SDE):
    dS_t = mu * S_t dt + sigma * S_t dW_t

Exakte Lösung (Herleitung: projekte/01_gbm/herleitung.md, Abschnitt 1):
    S_t = S_0 * exp((mu - sigma^2/2) t + sigma W_t)

Wir parametrisieren intern oft mit der Log-Drift  nu := mu - sigma^2/2,
weil die Log-Renditen r = ln(S_{t+dt}/S_t) ~ N(nu*dt, sigma^2*dt) iid sind.
Zeiteinheit überall: Jahre. Ein Handelstag ist dt = 1/252 (siehe ADR 0003).
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np
from scipy import stats

TRADING_DAYS = 252


@dataclass(frozen=True)
class GBMFit:
    """Ergebnis der Maximum-Likelihood-Schätzung aus n äquidistanten Log-Renditen."""

    mu: float          # Drift von S (pro Jahr)
    sigma: float       # Volatilität (pro sqrt(Jahr))
    nu: float          # Log-Drift mu - sigma^2/2
    se_mu: float       # asymptotischer Standardfehler von mu (Delta-Methode)
    se_sigma: float    # asymptotischer Standardfehler von sigma
    se_nu: float       # exakter Standardfehler von nu (gegeben sigma), = sigma/sqrt(T)
    n: int             # Anzahl Log-Renditen
    dt: float          # Schrittweite in Jahren
    T: float           # Gesamtlänge des Fensters in Jahren, = n*dt
    s2_unbiased: float  # erwartungstreue Varianz der Log-Renditen pro Schritt, Nenner n-1
    m_hat: float       # Mittelwert der Log-Renditen pro Schritt
    loglik: float      # maximierte Log-Likelihood

    def as_dict(self) -> dict:
        return asdict(self)


def log_returns(prices: np.ndarray) -> np.ndarray:
    prices = np.asarray(prices, dtype=float)
    if np.any(prices <= 0):
        raise ValueError("GBM verlangt strikt positive Preise.")
    return np.diff(np.log(prices))


def fit_mle(prices: np.ndarray, dt: float = 1.0 / TRADING_DAYS) -> GBMFit:
    """MLE für (mu, sigma) aus einer Preisreihe mit konstantem Zeitschritt dt.

    Herleitung: herleitung.md, Abschnitt 2. Kurz:
        m_hat  = mean(r)                      (MLE von nu*dt)
        s2_hat = mean((r - m_hat)^2)          (MLE von sigma^2*dt, Nenner n!)
        sigma_hat^2 = s2_hat/dt,   nu_hat = m_hat/dt,   mu_hat = nu_hat + sigma_hat^2/2
    Wegen Invarianz der MLE unter Reparametrisierung ist mu_hat die MLE von mu.
    """
    r = log_returns(prices)
    n = r.size
    if n < 2:
        raise ValueError("Mindestens drei Preise nötig.")
    m_hat = r.mean()
    s2_hat = np.mean((r - m_hat) ** 2)
    sigma2 = s2_hat / dt
    sigma = np.sqrt(sigma2)
    nu = m_hat / dt
    mu = nu + 0.5 * sigma2
    T = n * dt

    # Fisher-Information (herleitung.md, Abschnitt 3):
    #   Var(nu_hat)      = sigma^2 / T                     (exakt, gegeben sigma)
    #   Var(sigma2_hat) ~= 2 sigma^4 / n
    #   Var(sigma_hat)  ~= sigma^2 / (2n)                  (Delta-Methode)
    #   Var(mu_hat)     ~= sigma^2/T + sigma^4/(2n)        (nu_hat, sigma2_hat unabhängig)
    se_nu = sigma / np.sqrt(T)
    se_sigma = sigma / np.sqrt(2 * n)
    se_mu = np.sqrt(sigma2 / T + sigma2**2 / (2 * n))

    loglik = float(np.sum(stats.norm.logpdf(r, loc=m_hat, scale=np.sqrt(s2_hat))))
    s2_unb = s2_hat * n / (n - 1)
    return GBMFit(mu=mu, sigma=sigma, nu=nu, se_mu=se_mu, se_sigma=se_sigma, se_nu=se_nu,
                  n=n, dt=dt, T=T, s2_unbiased=s2_unb, m_hat=m_hat, loglik=loglik)


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

def exact_paths(S0: float, mu: float | np.ndarray, sigma: float | np.ndarray, T: float,
                n_steps: int, n_paths: int, rng: np.random.Generator) -> np.ndarray:
    """Pfade über die exakte Lösung (kein Diskretisierungsfehler).

    mu, sigma dürfen Arrays der Länge n_paths sein (ein Parameterpaar pro Pfad),
    damit Parameterunsicherheit simuliert werden kann.
    Rückgabe: Array (n_paths, n_steps+1), Spalte 0 = S0.
    """
    dt = T / n_steps
    mu = np.broadcast_to(np.asarray(mu, float), (n_paths,))[:, None]
    sigma = np.broadcast_to(np.asarray(sigma, float), (n_paths,))[:, None]
    dW = rng.standard_normal((n_paths, n_steps)) * np.sqrt(dt)
    incr = (mu - 0.5 * sigma**2) * dt + sigma * dW
    logS = np.concatenate([np.zeros((n_paths, 1)), np.cumsum(incr, axis=1)], axis=1)
    return S0 * np.exp(logS)


def sample_posterior(fit: GBMFit, size: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Ziehungen (mu, sigma) aus der Posterior unter der Prior p(nu, sigma^2) ∝ 1/sigma^2.

    Standardergebnis (Normal-Inverse-Chi^2, herleitung.md Abschnitt 4):
        sigma^2 * dt | Daten ~ Scaled-Inv-Chi^2(n-1, s2_unbiased)
        nu | sigma^2, Daten   ~ N(nu_hat, sigma^2 / T)
    Zweck: Parameterunsicherheit in die Bänder einrechnen (ADR 0004).
    """
    chi2 = rng.chisquare(fit.n - 1, size=size)
    sigma2 = (fit.n - 1) * fit.s2_unbiased / chi2 / fit.dt
    nu = fit.nu + np.sqrt(sigma2 / fit.T) * rng.standard_normal(size)
    mu = nu + 0.5 * sigma2
    return mu, np.sqrt(sigma2)


# ---------------------------------------------------------------------------
# Analytische Vorhersageverteilungen für X_h := ln(S_{t+h}/S_t), h in Jahren
# ---------------------------------------------------------------------------

def plugin_logreturn_dist(fit: GBMFit, h: float | np.ndarray):
    """Plug-in: X_h ~ N(nu_hat h, sigma_hat^2 h). Ignoriert Schätzunsicherheit."""
    h = np.asarray(h, float)
    return stats.norm(loc=fit.nu * h, scale=fit.sigma * np.sqrt(h))


def predictive_logreturn_dist(fit: GBMFit, h: float | np.ndarray):
    """Posterior-Prädiktive Verteilung: X_h ~ t_{n-1}(nu_hat h, (s2_unb/dt)(h + h^2/T)).

    Der Term h^2/T ist die Drift-Unsicherheit; er wächst quadratisch im Horizont
    und wird relevant, sobald h nicht mehr klein gegen T ist. Herleitung: Abschnitt 4.
    """
    h = np.asarray(h, float)
    scale = np.sqrt(fit.s2_unbiased / fit.dt * (h + h**2 / fit.T))
    return stats.t(df=fit.n - 1, loc=fit.nu * h, scale=scale)


def price_quantiles(S0: float, dist, q: np.ndarray) -> np.ndarray:
    """Quantile von S_{t+h} = S0*exp(X_h). exp ist monoton, also Quantile direkt übertragbar.

    Rückgabe hat Form (len(q), *shape(h)).
    """
    q = np.asarray(q, float)
    q = q.reshape(q.shape + (1,) * np.ndim(dist.mean()))
    return S0 * np.exp(dist.ppf(q))
