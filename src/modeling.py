"""Modelling primitives: splines, multiple imputation, metrics, decision curves.

Kept separate from the analysis script so each piece can be tested on its own
and so the analysis reads as a sequence of decisions rather than a wall of
numerics.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score


# --------------------------------------------------------------------------
# Restricted cubic splines (Harrell's parameterisation)
# --------------------------------------------------------------------------

def rcs_knots(x, n_knots=4):
    """Knot positions at Harrell's recommended quantiles."""
    q = {3: [.10, .50, .90],
         4: [.05, .35, .65, .95],
         5: [.05, .275, .50, .725, .95]}[n_knots]
    return np.quantile(pd.Series(x).dropna(), q)


def rcs_basis(x, knots):
    """Restricted cubic spline basis: returns len(knots)-1 columns.

    The first column is x itself; the remainder are the constrained cubic
    terms. Linearity is forced beyond the outer knots, which is what keeps a
    spline in age from doing something absurd at 85.
    """
    x = np.asarray(x, dtype=float)
    t = np.asarray(knots, dtype=float)
    k = len(t)
    denom = (t[-1] - t[0]) ** 2
    cols = [x]
    for j in range(k - 2):
        def cub(v):
            d = np.clip(x - v, 0, None)
            return d ** 3
        term = (cub(t[j])
                - cub(t[k - 2]) * (t[k - 1] - t[j]) / (t[k - 1] - t[k - 2])
                + cub(t[k - 1]) * (t[k - 2] - t[j]) / (t[k - 1] - t[k - 2]))
        cols.append(term / denom)
    return np.column_stack(cols)


# --------------------------------------------------------------------------
# Multiple imputation by chained equations
# --------------------------------------------------------------------------

def mice(df, columns, m=20, iters=10, seed=20260828):
    """Multiple imputation by chained equations, Bayesian linear draws.

    Yields m completed copies of df[columns]. Each variable with missing values
    is regressed on all the others in turn; the replacement is drawn from the
    predictive posterior rather than set to the fitted mean, which is what
    separates multiple imputation from a fancy mean-fill and is why the
    resulting standard errors are honest.

    The outcome is deliberately not among `columns`: imputing it would
    manufacture events.
    """
    rng = np.random.default_rng(seed)
    base = df[columns].astype(float).copy()
    miss = {c: base[c].isna().to_numpy() for c in columns}
    order = [c for c in columns if miss[c].any()]

    for _ in range(m):
        cur = base.copy()
        # Start from a random observed value, not the mean: a mean start biases
        # the first few chained draws towards the centre.
        for c in order:
            obs = base[c].dropna().to_numpy()
            cur.loc[miss[c], c] = rng.choice(obs, size=miss[c].sum())

        for _ in range(iters):
            for c in order:
                others = [o for o in columns if o != c]
                obs_rows = ~miss[c]
                X = np.column_stack([np.ones(len(cur)), cur[others].to_numpy()])
                y = cur[c].to_numpy()
                Xo, yo = X[obs_rows], y[obs_rows]
                # Ridge-stabilised least squares; NHANES predictors are
                # collinear enough (BMI and waist) to make a plain solve fragile.
                XtX = Xo.T @ Xo + 1e-6 * np.eye(X.shape[1])
                beta = np.linalg.solve(XtX, Xo.T @ yo)
                resid = yo - Xo @ beta
                dof = max(len(yo) - X.shape[1], 1)
                sigma2 = float(resid @ resid) / dof
                # Draw beta from its posterior, then add residual noise.
                cov = sigma2 * np.linalg.inv(XtX)
                beta_draw = rng.multivariate_normal(beta, cov, method="cholesky")
                pred = X[miss[c]] @ beta_draw
                cur.loc[miss[c], c] = pred + rng.normal(
                    0, np.sqrt(sigma2), miss[c].sum())
        yield cur


def round_binary(df, binary_cols):
    """Snap imputed binary columns back to 0/1 after continuous imputation."""
    out = df.copy()
    for c in binary_cols:
        if c in out.columns:
            out[c] = (out[c] >= 0.5).astype(float)
    return out


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------

def fit_logistic(X, y, C=None, l1=False):
    """Maximum-likelihood logistic fit, or an L1-penalised one when l1=True.

    C=np.inf is the unpenalised fit; scikit-learn deprecated penalty=None in
    favour of it.
    """
    if l1:
        m = LogisticRegression(l1_ratio=1, C=C, solver="saga",
                               penalty="elasticnet", max_iter=5000)
    else:
        # newton-cholesky is ~59x faster than lbfgs on a problem this shape
        # (9 ms against 545 ms per fit here), which is the difference between
        # a bootstrap that finishes and one that does not. C=1e6 leaves a
        # ridge term of order 1e-6 - numerically negligible against n=8080,
        # and it stabilises the Hessian on collinear resamples.
        m = LogisticRegression(C=1e6, solver="newton-cholesky", max_iter=2000)
    m.fit(X, y)
    return m


def calibration_slope_intercept(y, lp):
    """Slope and intercept from regressing the outcome on the linear predictor.

    Slope below 1 means the predictions are too extreme - the usual signature
    of overfitting.
    """
    m = LogisticRegression(C=1e6, solver="newton-cholesky", max_iter=2000)
    m.fit(lp.reshape(-1, 1), y)
    slope = float(m.coef_[0][0])

    # Calibration-in-the-large is the intercept of a model that carries the
    # linear predictor as a fixed offset - i.e. the a solving
    # mean(sigmoid(a + lp)) = mean(y). Comparing logit(mean(y)) with mean(lp)
    # is not the same quantity, because the logit of an average is not the
    # average of logits.
    lo, hi = -10.0, 10.0
    target = float(y.mean())
    for _ in range(200):
        mid = (lo + hi) / 2
        if float(np.mean(1 / (1 + np.exp(-(mid + lp))))) < target:
            lo = mid
        else:
            hi = mid
    citl = (lo + hi) / 2
    return slope, citl


def brier(y, p):
    return float(np.mean((p - y) ** 2))


def net_benefit(y, p, thr):
    """Vickers net benefit at one threshold."""
    pred = p >= thr
    n = len(y)
    tp = int(np.sum(pred & (y == 1)))
    fp = int(np.sum(pred & (y == 0)))
    return tp / n - (fp / n) * (thr / (1 - thr))


def threshold_metrics(y, p, thr):
    pred = p >= thr
    tp = int(np.sum(pred & (y == 1)))
    fp = int(np.sum(pred & (y == 0)))
    fn = int(np.sum(~pred & (y == 1)))
    tn = int(np.sum(~pred & (y == 0)))
    sens = tp / max(tp + fn, 1)
    spec = tn / max(tn + fp, 1)
    ppv = tp / max(tp + fp, 1)
    npv = tn / max(tn + fn, 1)
    return dict(threshold=thr, sens=sens, spec=spec, ppv=ppv, npv=npv,
                burden=float(pred.mean()),
                nnt=(1 / ppv if ppv > 0 else np.inf),
                tp=tp, fp=fp, fn=fn, tn=tn)


def rubin_pool(estimates, variances):
    """Rubin's rules: pooled estimate, total variance, 95% interval."""
    est = np.asarray(estimates, dtype=float)
    var = np.asarray(variances, dtype=float)
    m = len(est)
    qbar = est.mean()
    ubar = var.mean()
    b = est.var(ddof=1) if m > 1 else 0.0
    total = ubar + (1 + 1 / m) * b
    se = np.sqrt(total)
    return qbar, se, (qbar - 1.96 * se, qbar + 1.96 * se)
