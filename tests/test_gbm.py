"""Tests gegen bekannte Antworten: synthetische Daten mit vorgegebenen Parametern."""
import numpy as np
import pytest
from scipy import stats

from stochmarkt.gbm import (exact_paths, fit_mle, sample_posterior, plugin_logreturn_dist,
                            predictive_logreturn_dist, price_quantiles, TRADING_DAYS)
from stochmarkt.sde import gbm_convergence_study, fitted_order

MU, SIGMA = 0.08, 0.25


def test_exact_paths_moments():
    rng = np.random.default_rng(1)
    S = exact_paths(100.0, MU, SIGMA, T=1.0, n_steps=10, n_paths=200_000, rng=rng)
    # E[S_T] = S0 e^{mu T};  Var[ln S_T] = sigma^2 T
    assert S[:, -1].mean() == pytest.approx(100 * np.exp(MU), rel=3e-3)
    assert np.log(S[:, -1]).var() == pytest.approx(SIGMA**2, rel=1e-2)


def test_mle_recovers_parameters_and_se_is_calibrated():
    """Über viele Replikate: z = (theta_hat - theta)/SE muss ~ N(0,1) sein."""
    rng = np.random.default_rng(2)
    n = 3 * TRADING_DAYS
    zs_mu, zs_sig = [], []
    for _ in range(400):
        S = exact_paths(1.0, MU, SIGMA, T=n / TRADING_DAYS, n_steps=n, n_paths=1, rng=rng)[0]
        f = fit_mle(S)
        zs_mu.append((f.mu - MU) / f.se_mu)
        zs_sig.append((f.sigma - SIGMA) / f.se_sigma)
    for z in (np.array(zs_mu), np.array(zs_sig)):
        assert abs(z.mean()) < 0.2
        assert z.std() == pytest.approx(1.0, abs=0.12)


def test_drift_se_depends_only_on_T_not_on_sampling():
    """Kernaussage aus herleitung.md §3: SE(nu) = sigma/sqrt(T), unabhängig von dt."""
    rng = np.random.default_rng(3)
    S = exact_paths(1.0, MU, SIGMA, T=4.0, n_steps=4 * 252, n_paths=1, rng=rng)[0]
    f_daily = fit_mle(S, dt=1 / 252)
    f_weekly = fit_mle(S[::5], dt=5 / 252)
    assert f_daily.se_nu == pytest.approx(f_weekly.se_nu, rel=0.1)
    assert f_daily.se_sigma < f_weekly.se_sigma  # sigma profitiert dagegen von mehr Punkten


def test_posterior_matches_predictive_t():
    """MC aus Posterior + exakter Simulation muss die analytische t-Prädiktive treffen."""
    rng = np.random.default_rng(4)
    S = exact_paths(1.0, MU, SIGMA, T=1.0, n_steps=252, n_paths=1, rng=rng)[0]
    f = fit_mle(S)
    h = 0.5
    mu_s, sig_s = sample_posterior(f, 200_000, rng)
    X = np.log(exact_paths(1.0, mu_s, sig_s, T=h, n_steps=1, n_paths=mu_s.size, rng=rng)[:, -1])
    d = predictive_logreturn_dist(f, h)
    for q in (0.05, 0.25, 0.5, 0.75, 0.95):
        assert np.quantile(X, q) == pytest.approx(d.ppf(q), abs=4e-3)
    # Prädiktive ist breiter als Plug-in
    assert d.std() > plugin_logreturn_dist(f, h).std()


def test_price_quantiles_shape():
    rng = np.random.default_rng(5)
    S = exact_paths(1.0, MU, SIGMA, T=1.0, n_steps=252, n_paths=1, rng=rng)[0]
    f = fit_mle(S)
    Q = price_quantiles(100.0, plugin_logreturn_dist(f, np.array([0.1, 0.2, 0.3])), [0.05, 0.5, 0.95])
    assert Q.shape == (3, 3)
    assert np.all(np.diff(Q, axis=0) > 0)
    assert Q[1, 0] == pytest.approx(100 * np.exp(f.nu * 0.1))  # Median = S0 e^{nu h}


def test_convergence_orders():
    res = gbm_convergence_study(mu=0.5, sigma=0.8, levels=(3, 4, 5, 6, 7, 8), n_paths=5_000, seed=6)
    assert fitted_order(res["dt"], res["strong_em"]) == pytest.approx(0.5, abs=0.1)
    assert fitted_order(res["dt"], res["strong_mil"]) == pytest.approx(1.0, abs=0.1)
    assert fitted_order(res["dt"], res["weak_analytic"]) == pytest.approx(1.0, abs=0.05)


def test_mle_rejects_nonpositive():
    with pytest.raises(ValueError):
        fit_mle(np.array([1.0, 0.0, 2.0]))
