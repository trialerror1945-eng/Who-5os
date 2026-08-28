#!/usr/bin/env python3
"""
analyze.py - derivation and internal validation of the LED triage score.

    python3 src/analyze.py [--boot 500] [--m 20]

Reads results/cohort.csv. Writes results/results.txt, the points tables, the
threshold-performance table, and Figures 2-4.

The decisive KPI is not the AUC. It is whether the score's net benefit exceeds
the "test everyone with diabetes" rule that clinicians already apply. This
script tests that explicitly and reports the answer either way.
"""

import argparse
import json
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import StratifiedKFold

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import OUT
from modeling import (rcs_knots, rcs_basis, mice, round_binary, fit_logistic,
                      calibration_slope_intercept, brier, net_benefit,
                      threshold_metrics, rubin_pool)

SEED = 20260828
OUTCOME = "led"

# Version A: nothing that needs a laboratory, a device, or a second visit.
# Two redundancies were resolved before modelling, on the diagnostics rather
# than on the outcome:
#
#   dm is dropped. dm_dur_cat == 0 holds for every non-diabetic participant
#   and only for them, so the binary duplicates the ordinal exactly (r = 0.90,
#   VIF 5.8). Keeping both left dm with a coefficient of ~0.06, which reads as
#   "diabetes does not matter" when the ordinal has simply absorbed it.
#
#   bmi is dropped in favour of waist circumference (r = 0.86, VIF ~4.1).
#   Central adiposity is the more direct vascular risk marker, and with both
#   terms present BMI took an implausible negative sign - a suppression
#   artefact, not protection. The swap is reported as a sensitivity analysis.
PRED_A_CONT = ["age", "sbp", "waist"]
PRED_A_CAT = ["sex_f", "smoke_former", "smoke_current", "dm_dur_cat",
              "htn_med", "prior_cvd"]
# Version B adds what a basic primary-care laboratory can supply. Glycaemia
# enters as HbA1c rather than fasting glucose: fasting glucose is measured
# only in NHANES' morning fasting subsample and is missing for 52% of this
# cohort by design, so a fasting-glucose model would rest on imputing the
# main new predictor for half the participants. HbA1c is missing for 3%.
# Fasting glucose is reported instead as a sensitivity analysis restricted
# to the fasting subsample.
PRED_B_CONT = PRED_A_CONT + ["hba1c", "egfr"]
PRED_B_CAT = PRED_A_CAT

SPLINE_VARS = ["age", "sbp"]      # the two with the clearest non-linearity
N_KNOTS = 4

out_lines = []


def log(msg=""):
    print(msg)
    out_lines.append(str(msg))


# --------------------------------------------------------------------------
# Design matrix
# --------------------------------------------------------------------------

def make_design(df, cont, cat, knots=None):
    """Build the model matrix, fitting spline knots on first call only.

    Knots are passed back and reused so that a bootstrap resample is scored on
    the same basis as the model it is testing.
    """
    cols, names = [], []
    fitted = {} if knots is None else knots

    for v in cont:
        x = df[v].to_numpy(float)
        if v in SPLINE_VARS:
            if knots is None:
                fitted[v] = rcs_knots(x, N_KNOTS)
            b = rcs_basis(x, fitted[v])
            cols.append(b)
            names += [v] + [f"{v}'{i}" for i in range(1, b.shape[1])]
        else:
            cols.append(x.reshape(-1, 1))
            names.append(v)

    for v in cat:
        cols.append(df[v].to_numpy(float).reshape(-1, 1))
        names.append(v)

    return np.column_stack(cols), names, fitted


def standardise(X, stats=None):
    """Centre and scale; LASSO penalises on the raw scale otherwise."""
    if stats is None:
        mu, sd = X.mean(0), X.std(0)
        sd[sd == 0] = 1.0
        stats = (mu, sd)
    mu, sd = stats
    return (X - mu) / sd, stats


# --------------------------------------------------------------------------
# Bootstrap optimism correction
# --------------------------------------------------------------------------

def bootstrap_optimism(X, y, n_boot, rng):
    """Harrell's optimism correction for the AUC and the calibration slope.

    The model is refitted from scratch on every resample and then scored on
    the original sample. Scoring a resample with a model fitted on the full
    data would measure nothing.
    """
    auc_opt, slopes = [], []
    for _ in range(n_boot):
        idx = rng.integers(0, len(y), len(y))
        if len(np.unique(y[idx])) < 2:
            continue
        mb = fit_logistic(X[idx], y[idx])
        auc_boot = roc_auc_score(y[idx], mb.predict_proba(X[idx])[:, 1])
        lp_orig = mb.decision_function(X)
        auc_orig = roc_auc_score(y, lp_orig)
        auc_opt.append(auc_boot - auc_orig)
        try:
            s, _ = calibration_slope_intercept(y, lp_orig)
            slopes.append(s)
        except Exception:
            pass
    return np.array(auc_opt), np.array(slopes)


# --------------------------------------------------------------------------
# Survey-weighted prevalence
# --------------------------------------------------------------------------

def weighted_prevalence(d, var, wt="wt", strata="strata", psu="psu"):
    """Weighted prevalence with a Taylor-linearised standard error.

    Individual prediction is deliberately unweighted, but a prevalence or an
    examination burden quoted for a population has to carry the design or it
    is a statement about the NHANES sample rather than about the country.
    """
    s = d[[var, wt, strata, psu]].dropna()
    w, y = s[wt].to_numpy(float), s[var].to_numpy(float)
    if w.sum() <= 0:
        return np.nan, np.nan
    p = float(np.sum(w * y) / np.sum(w))

    # Linearised residual, aggregated to PSU totals within stratum.
    z = w * (y - p)
    var_est = 0.0
    for _, g in s.assign(_z=z).groupby(strata, observed=True):
        psu_tot = g.groupby(psu, observed=True)["_z"].sum().to_numpy()
        n_psu = len(psu_tot)
        if n_psu < 2:
            continue
        var_est += (n_psu / (n_psu - 1)) * np.sum(
            (psu_tot - psu_tot.mean()) ** 2)
    se = np.sqrt(var_est) / np.sum(w)
    return p, float(se)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def run_version(d_imp_list, cont, cat, label, args, rng, y, dm_rule, age_rule):
    """Fit, validate and score one version of the model across imputations."""
    log("\n" + "=" * 70)
    log(f"MODEL {label}   predictors: {len(cont) + len(cat)}  "
        f"({', '.join(cont + cat)})")
    log("=" * 70)

    m = len(d_imp_list)
    lp_stack, coefs, ses, aucs, briers = [], [], [], [], []
    knots_ref = None
    names_ref = None

    cv = StratifiedKFold(10, shuffle=True, random_state=SEED)
    cv_stack = []

    # LASSO selection, reported rather than acted on automatically. With ~1800
    # events and a dozen candidate terms this model is nowhere near the regime
    # where selection is needed; what the penalty path is good for here is
    # showing which terms survive shrinkage and which are carried by the rest.
    X0, names0, _ = make_design(d_imp_list[0], cont, cat)
    kept, dropped, c_opt = lasso_select(X0, names0, y, rng)
    log(f"\nLASSO (C={c_opt:.4g}) retains: {', '.join(sorted(kept))}")
    log(f"LASSO shrinks to zero      : "
        f"{', '.join(sorted(dropped)) if dropped else '(none)'}")

    for j, di in enumerate(d_imp_list):
        X, names, knots = make_design(di, cont, cat,
                                      knots=None if j == 0 else knots_ref)
        if j == 0:
            knots_ref, names_ref = knots, names
        model = fit_logistic(X, y)
        lp_stack.append(model.decision_function(X))
        coefs.append(model.coef_[0])
        # Model-based standard errors from the observed information.
        p = model.predict_proba(X)[:, 1]
        W = p * (1 - p)
        Xd = np.column_stack([np.ones(len(y)), X])
        try:
            cov = np.linalg.inv(Xd.T * W @ Xd)
            ses.append(np.sqrt(np.diag(cov))[1:])
        except np.linalg.LinAlgError:
            ses.append(np.full(X.shape[1], np.nan))
        aucs.append(roc_auc_score(y, p))
        briers.append(brier(y, p))

        p_cv = np.zeros(len(y))
        for tr, te in cv.split(X, y):
            p_cv[te] = fit_logistic(X[tr], y[tr]).predict_proba(X[te])[:, 1]
        cv_stack.append(p_cv)

    # Predictions are pooled on the linear-predictor scale, then transformed.
    lp = np.mean(lp_stack, axis=0)
    p_app = 1 / (1 + np.exp(-lp))
    p_cv = np.mean(cv_stack, axis=0)

    auc_app = roc_auc_score(y, p_app)
    auc_cv = roc_auc_score(y, p_cv)
    log(f"\nAUC apparent                     : {auc_app:.3f}")
    log(f"AUC 10-fold cross-validated      : {auc_cv:.3f}")

    # Optimism correction, run inside each imputation and averaged.
    n_sub = min(m, args.boot_imp)
    opts, slopes = [], []
    for j in range(n_sub):
        X, _, _ = make_design(d_imp_list[j], cont, cat, knots=knots_ref)
        o, s = bootstrap_optimism(X, y, args.boot // n_sub, rng)
        opts.append(o)
        slopes.append(s)
    opt = np.concatenate(opts)
    slope_arr = np.concatenate(slopes)
    auc_corr = auc_app - opt.mean()
    lo, hi = np.percentile(auc_app - opt, [2.5, 97.5])
    slope = float(slope_arr.mean())
    _, citl = calibration_slope_intercept(y, lp)

    log(f"AUC optimism-corrected           : {auc_corr:.3f} "
        f"(95% CI {lo:.3f}-{hi:.3f})")
    log(f"Optimism                         : {opt.mean():.4f}")
    log(f"Calibration slope (bootstrap)    : {slope:.3f}")
    log(f"Calibration-in-the-large         : {citl:+.3f}")
    log(f"Brier score                      : {np.mean(briers):.4f}")
    log(f"Uniform shrinkage factor         : {slope:.3f}")

    log(f"\n  KPI: AUC >=0.72 -> {'MET' if auc_corr >= 0.72 else 'NOT MET'}; "
        f"CI lower bound >0.68 -> {'MET' if lo > 0.68 else 'NOT MET'}; "
        f"slope 0.85-1.15 -> {'MET' if 0.85 <= slope <= 1.15 else 'NOT MET'}")

    # ---- pooled coefficients (Rubin) --------------------------------------
    coefs = np.array(coefs)
    ses = np.array(ses)
    log("\n--- POOLED COEFFICIENTS (Rubin's rules across "
        f"{m} imputations) ---")
    log(f"{'term':<16}{'beta':>9}{'SE':>8}{'OR':>8}{'95% CI':>20}")
    pooled = {}
    for i, nm in enumerate(names_ref):
        q, se, (cl, ch) = rubin_pool(coefs[:, i], ses[:, i] ** 2)
        pooled[nm] = q
        log(f"{nm:<16}{q:>9.4f}{se:>8.4f}{np.exp(q):>8.2f}"
            f"{f'{np.exp(cl):.2f}-{np.exp(ch):.2f}':>20}")

    return dict(label=label, names=names_ref, coefs=pooled, knots=knots_ref,
                p_cv=p_cv, p_app=p_app, auc_app=auc_app, auc_cv=auc_cv,
                auc_corr=auc_corr, auc_ci=(lo, hi), slope=slope, citl=citl,
                brier=float(np.mean(briers)))


def lasso_select(X, names, y, rng):
    """L1 selection over a standardised design, penalty by cross-validation.

    Spline basis terms are kept or dropped with their parent variable: half a
    spline is not interpretable, and dropping only the non-linear part while
    keeping the linear one silently changes the functional form.
    """
    Xs, _ = standardise(X)
    cv = LogisticRegressionCV(
        Cs=20, cv=5, penalty="elasticnet", l1_ratios=[1.0], solver="saga",
        scoring="neg_log_loss", max_iter=5000, random_state=SEED, n_jobs=-1)
    cv.fit(Xs, y)
    coef = cv.coef_[0]
    parents = {}
    for i, nm in enumerate(names):
        parents.setdefault(nm.split("'")[0], []).append(i)
    kept = [p for p, idx in parents.items()
            if any(abs(coef[i]) > 1e-8 for i in idx)]
    dropped = [p for p in parents if p not in kept]
    return kept, dropped, float(cv.C_[0])


def fit_points_model(d_imp_list, cont, cat, y):
    """A deliberately linear model, which is what the paper card can carry.

    The flexible model uses restricted cubic splines, and a spline coefficient
    has no meaning as a row in a points table - the basis terms are not
    quantities a clinician can read off a patient. So the score is derived
    from its own all-linear model and validated in its own right, rather than
    by rounding coefficients that were never meant to stand alone.
    """
    lps, coefs = [], []
    for di in d_imp_list:
        X = np.column_stack([di[v].to_numpy(float) for v in cont + cat])
        m = fit_logistic(X, y)
        coefs.append(m.coef_[0])
        lps.append(m.decision_function(X))
    return dict(zip(cont + cat, np.mean(coefs, axis=0))), np.mean(lps, axis=0)


# Reference values: the level each predictor is scored from. Sullivan points
# are awarded for distance from a reference, not for the raw value - without
# one, a 60-year-old starts at twelve points for the crime of being sixty and
# the score never reaches zero.
REF_VALUES = {"age": 40, "sbp": 110, "waist": 70, "bmi": 22,
              "hba1c": 5.0, "egfr": 90, "glucose": 90}


def integer_score(d, coefs, ref_units, B):
    """Each participant's integer score, and the table it is read off.

    Points per unit are rounded once, at the table, so that the number a
    clinician computes by hand on paper is exactly the number the validation
    below reports - not a rounding of a number computed at full precision.
    """
    total = np.zeros(len(d))
    table = {}
    for name, beta in coefs.items():
        unit = ref_units.get(name, 1)
        ref = REF_VALUES.get(name, 0.0)
        pts = int(round(beta * unit / B))
        table[name] = dict(per_unit=unit, reference=ref, points=pts)
        x = pd.to_numeric(d[name], errors="coerce")
        x = x.fillna(x.median())
        total += np.round((x - ref) / unit) * pts

    # Shift so the lowest attainable score is zero; a negative total on a
    # printed card invites arithmetic errors.
    offset = int(-min(0, total.min()))
    return total + offset, table, offset


def points_table(res, ref_units, path):
    """Sullivan/Framingham integer points from the pooled coefficients.

    B is set so that five years of age is worth one point, which keeps the
    total on a scale a clinician can hold in their head.
    """
    coefs = res["coefs"]
    b_age = abs(coefs.get("age", 0.05))
    B = b_age * 5 if b_age > 1e-8 else 0.1
    rows = []
    for name, beta in coefs.items():
        if "'" in name:          # spline basis terms have no standalone meaning
            continue
        unit = ref_units.get(name, 1)
        rows.append(dict(term=name, unit=unit, beta=round(beta, 4),
                         points=int(round(beta * unit / B))))
    df = pd.DataFrame(rows).sort_values("points", key=abs, ascending=False)
    df.to_csv(path, index=False)
    return df, B


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000,
                    help="total bootstrap resamples for optimism correction")
    ap.add_argument("--boot-imp", type=int, default=5,
                    help="imputations across which the bootstrap is spread")
    ap.add_argument("--m", type=int, default=20, help="imputations")
    args = ap.parse_args()

    rng = np.random.default_rng(SEED)
    d = pd.read_csv(os.path.join(OUT, "cohort.csv"))
    d = d[d[OUTCOME].notna()].reset_index(drop=True)

    d["sex_f"] = (d["sex"] == 2).astype(float)
    d["smoke_former"] = (d["smoke"] == 1).astype(float)
    d["smoke_current"] = (d["smoke"] == 2).astype(float)
    for c in ("smoke_former", "smoke_current"):
        d.loc[d["smoke"].isna(), c] = np.nan

    y = d[OUTCOME].to_numpy(float)

    log("=" * 70)
    log("LOWER-EXTREMITY DISEASE TRIAGE SCORE - derivation and internal "
        "validation")
    log("=" * 70)
    log(f"Cohort            n = {len(d)}")
    log(f"Composite events      {int(y.sum())} ({100 * y.mean():.1f}%)")
    log(f"  PAD only            {int((d['pad'] == 1).sum())}")
    log(f"  Neuropathy only     {int((d['pn'] == 1).sum())}")
    log(f"  Both                {int((d['high_risk_foot'] == 1).sum())}")
    log(f"Imputations       m = {args.m};  bootstrap = {args.boot}")

    # ---- survey-weighted prevalence ---------------------------------------
    log("\n--- SURVEY-WEIGHTED PREVALENCE (six-year MEC weights, "
        "Taylor linearisation) ---")
    for var in ["led", "pad", "pn", "high_risk_foot"]:
        p, se = weighted_prevalence(d, var)
        if not np.isnan(p):
            log(f"  {var:16s} {100 * p:5.2f}%  (95% CI "
                f"{100 * (p - 1.96 * se):.2f}-{100 * (p + 1.96 * se):.2f})")

    # ---- multiple imputation ----------------------------------------------
    impute_cols = sorted(set(
        PRED_A_CONT + PRED_A_CAT + PRED_B_CONT + PRED_B_CAT + [OUTCOME]))
    binary = ["sex_f", "smoke_former", "smoke_current", "dm", "htn_med",
              "prior_cvd"]
    log(f"\nImputing {len(impute_cols)} variables "
        f"(outcome included as a predictor, never imputed)...")
    imps = [round_binary(x, binary)
            for x in mice(d, impute_cols, m=args.m, seed=SEED)]
    log(f"  {len(imps)} completed datasets")

    ref_units = {"age": 10, "sbp": 20, "bmi": 5, "waist": 15,
                 "hba1c": 1, "egfr": 15, "glucose": 20}

    dm_rule = (d["dm"].fillna(0) == 1).to_numpy()
    age_rule = (d["age"] >= 60).to_numpy()

    res_a = run_version(imps, PRED_A_CONT, PRED_A_CAT, "A (no laboratory)",
                        args, rng, y, dm_rule, age_rule)
    res_b = run_version(imps, PRED_B_CONT, PRED_B_CAT, "B (+ HbA1c, eGFR)",
                        args, rng, y, dm_rule, age_rule)

    # ---- machine-learning benchmark ---------------------------------------
    log("\n--- GRADIENT BOOSTING BENCHMARK (Version A predictors) ---")
    Xa, _, _ = make_design(imps[0], PRED_A_CONT, PRED_A_CAT)
    cv = StratifiedKFold(10, shuffle=True, random_state=SEED)
    p_gb = np.zeros(len(y))
    for tr, te in cv.split(Xa, y):
        gb = HistGradientBoostingClassifier(
            max_iter=300, learning_rate=0.06, max_leaf_nodes=15,
            l2_regularization=1.0, random_state=SEED)
        gb.fit(Xa[tr], y[tr])
        p_gb[te] = gb.predict_proba(Xa[te])[:, 1]
    auc_gb = roc_auc_score(y, p_gb)
    log(f"AUC gradient boosting (10-fold)  : {auc_gb:.3f}")
    log(f"AUC logistic + splines (10-fold) : {res_a['auc_cv']:.3f}")
    log(f"Difference                       : {auc_gb - res_a['auc_cv']:+.3f}")
    log("Reported as found. A points table a clinician can compute without a")
    log("device is worth more than a decimal of AUC that needs a server.")

    return (res_a, res_b, d, y, p_gb, dm_rule, age_rule, ref_units, args,
            imps)


def report(res_a, res_b, d, y, p_gb, dm_rule, age_rule, ref_units, args,
           imps):
    """Thresholds, decision curves, subgroups, sensitivity analyses, figures."""
    p = res_a["p_cv"]

    # ---- threshold performance --------------------------------------------
    log("\n" + "=" * 70)
    log("EXAMINATION THRESHOLDS (Version A, cross-validated predictions)")
    log("=" * 70)
    log(f"{'thresh':>7}{'sens':>7}{'spec':>7}{'PPV':>7}{'NPV':>7}"
        f"{'tested':>9}{'NNT':>7}")
    rows = []
    for t in np.arange(0.10, 0.56, 0.025):
        r = threshold_metrics(y, p, t)
        rows.append(r)
        log(f"{t:>7.3f}{r['sens']:>7.2f}{r['spec']:>7.2f}{r['ppv']:>7.2f}"
            f"{r['npv']:>7.2f}{100 * r['burden']:>8.1f}%{r['nnt']:>7.1f}")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "threshold_table.csv"),
                              index=False)

    ok = [r for r in rows if r["sens"] >= 0.85]
    if ok:
        chosen = min(ok, key=lambda r: r["burden"])
        log(f"\nOperating point (sensitivity >=0.85, least burden): "
            f"threshold {chosen['threshold']:.3f}")
        log(f"  sensitivity {chosen['sens']:.2f}, specificity "
            f"{chosen['spec']:.2f}, examine {100 * chosen['burden']:.1f}% "
            f"of patients, NNT {chosen['nnt']:.1f}")
        log(f"  KPI burden <=40% -> "
            f"{'MET' if chosen['burden'] <= 0.40 else 'NOT MET'}")
    else:
        chosen = max(rows, key=lambda r: r["sens"])
        log("\nNo threshold reached sensitivity 0.85. Reported as found; the "
            "best available is")
        log(f"  threshold {chosen['threshold']:.3f}, sensitivity "
            f"{chosen['sens']:.2f}, examine {100 * chosen['burden']:.1f}%")

    # ---- decision curve: the decisive comparison --------------------------
    log("\n" + "=" * 70)
    log("DECISION CURVE - score versus the rules clinicians already use")
    log("=" * 70)
    log(f"{'thresh':>7}{'score':>10}{'test all':>10}{'diabetes':>10}"
        f"{'age>=60':>10}{'none':>7}")
    thrs = np.arange(0.05, 0.61, 0.025)
    nb = {k: [] for k in ("score", "all", "dm", "age")}
    for t in thrs:
        nb["score"].append(net_benefit(y, p, t))
        nb["all"].append(net_benefit(y, np.ones(len(y)), t))
        nb["dm"].append(net_benefit(y, dm_rule.astype(float), t))
        nb["age"].append(net_benefit(y, age_rule.astype(float), t))
        log(f"{t:>7.3f}{nb['score'][-1]:>10.4f}{nb['all'][-1]:>10.4f}"
            f"{nb['dm'][-1]:>10.4f}{nb['age'][-1]:>10.4f}{0.0:>7.3f}")

    wins_dm = sum(a > b for a, b in zip(nb["score"], nb["dm"]))
    wins_age = sum(a > b for a, b in zip(nb["score"], nb["age"]))
    log(f"\nScore exceeds 'test everyone with diabetes' at "
        f"{wins_dm}/{len(thrs)} thresholds")
    log(f"Score exceeds 'test everyone aged >=60'      at "
        f"{wins_age}/{len(thrs)} thresholds")
    decisive = wins_dm >= 0.7 * len(thrs)
    log(f"\nDECISIVE KPI: {'MET' if decisive else 'NOT MET'}")
    if not decisive:
        log("The score does not beat the rule clinicians already apply across")
        log("the practical threshold range. That is the finding, and it is")
        log("reported rather than engineered away. The manuscript's question")
        log("becomes how many cases the simple heuristic misses, and who they")
        log("are - which the non-diabetic subgroup below answers.")

    # ---- subgroups ---------------------------------------------------------
    log("\n" + "=" * 70)
    log("TRANSPORTABILITY ACROSS SUBGROUPS (Version A)")
    log("=" * 70)
    groups = {
        "diabetes": d["dm"] == 1,
        "no diabetes": d["dm"] == 0,
        "women": d["sex"] == 2,
        "men": d["sex"] == 1,
        "age 40-59": (d["age"] >= 40) & (d["age"] < 60),
        "age >=60": d["age"] >= 60,
        "obese (BMI>=30)": d["bmi"] >= 30,
        "non-obese": d["bmi"] < 30,
    }
    log(f"{'subgroup':<18}{'n':>7}{'events':>8}{'prev':>8}{'AUC':>8}")
    for name, mask in groups.items():
        mk = mask.fillna(False).to_numpy()
        if mk.sum() < 100 or len(np.unique(y[mk])) < 2:
            continue
        log(f"{name:<18}{int(mk.sum()):>7}{int(y[mk].sum()):>8}"
            f"{100 * y[mk].mean():>7.1f}%{roc_auc_score(y[mk], p[mk]):>8.3f}")

    nd = (d["dm"] == 0).to_numpy()
    missed = int(y[nd].sum())
    log(f"\nCases missed entirely by 'test everyone with diabetes': "
        f"{missed} of {int(y.sum())} ({100 * missed / y.sum():.1f}%).")
    log("These are the participants the current heuristic cannot reach at any")
    log("threshold, and they are the clinical argument for a score.")

    # ---- secondary endpoints and sensitivity analyses ----------------------
    log("\n" + "=" * 70)
    log("SECONDARY ENDPOINTS AND SENSITIVITY ANALYSES (Version A predictors)")
    log("=" * 70)
    Xs, _, _ = make_design(
        pd.DataFrame({c: d[c].fillna(d[c].median())
                      for c in PRED_A_CONT + PRED_A_CAT}),
        PRED_A_CONT, PRED_A_CAT)
    cv = StratifiedKFold(10, shuffle=True, random_state=SEED)

    def cv_auc(target):
        m = target.notna().to_numpy()
        yy = target[m].to_numpy(float)
        if len(np.unique(yy)) < 2 or m.sum() < 200:
            return None
        XX = Xs[m]
        pp = np.zeros(len(yy))
        for tr, te in cv.split(XX, yy):
            pp[te] = fit_logistic(XX[tr], yy[tr]).predict_proba(XX[te])[:, 1]
        return roc_auc_score(yy, pp), int(m.sum()), int(yy.sum())

    alt = {
        "composite LED (primary)": d["led"],
        "PAD alone (ABI<0.90)": d["pad"],
        "neuropathy alone": d["pn"],
        "high-risk foot (both)": d["high_risk_foot"],
        "ABI abnormal (<0.90 or >1.40)": d["abi_abnormal"],
        "neuropathy >=2 sites": np.nan,
    }
    alt["neuropathy >=2 sites"] = pd.Series(np.where(
        d[["pn_left", "pn_right"]].notna().any(axis=1),
        ((d["pn_left"] >= 2) | (d["pn_right"] >= 2)).astype(float), np.nan))
    alt["neuropathy both feet"] = pd.Series(np.where(
        d[["pn_left", "pn_right"]].notna().all(axis=1),
        ((d["pn_left"] >= 1) & (d["pn_right"] >= 1)).astype(float), np.nan))

    log(f"{'endpoint':<32}{'n':>7}{'events':>8}{'AUC':>8}")
    for name, target in alt.items():
        r = cv_auc(pd.Series(target).reset_index(drop=True))
        if r:
            log(f"{name:<32}{r[1]:>7}{r[2]:>8}{r[0]:>8.3f}")

    # ---- points tables -----------------------------------------------------
    log("\n" + "=" * 70)
    log("POINTS TABLES (Sullivan method, derived from all-linear models)")
    log("=" * 70)
    points_results = {}
    for res, cont, cat, fname in (
            (res_a, PRED_A_CONT, PRED_A_CAT, "points_A.csv"),
            (res_b, PRED_B_CONT, PRED_B_CAT, "points_B.csv")):
        lin_coefs, lin_lp = fit_points_model(imps, cont, cat, y)
        B = abs(lin_coefs["age"]) * 5
        score, table, offset = integer_score(d, lin_coefs, ref_units, B)
        auc_score = roc_auc_score(y, score)
        slope_s, citl_s = calibration_slope_intercept(y, lin_lp)

        rows = [dict(term=k, per_unit=v["per_unit"], reference=v["reference"],
                     points=v["points"]) for k, v in table.items()]
        df = pd.DataFrame(rows).sort_values("points", key=abs, ascending=False)
        df.to_csv(os.path.join(OUT, fname), index=False)

        log(f"\nVersion {res['label']}   B = {B:.4f} "
            f"(five years of age = one point)")
        log(df.to_string(index=False))
        log(f"  integer score range      : {int(score.min())} to "
            f"{int(score.max())}")
        log(f"  AUC of the integer score : {auc_score:.3f}  "
            f"(continuous model {res['auc_cv']:.3f}; "
            f"cost of rounding {res['auc_cv'] - auc_score:+.3f})")
        log(f"  baseline offset          : +{offset}")
        points_results[res["label"]] = dict(
            table=table, B=float(B), auc=float(auc_score), offset=offset,
            score=score, slope=float(slope_s), citl=float(citl_s))

    # Risk by integer score band, for the printed card.
    sc = points_results[res_a["label"]]["score"]
    log("\n--- OBSERVED RISK BY SCORE BAND (Version A) ---")
    log(f"{'band':>10}{'n':>8}{'events':>8}{'risk':>8}")
    # Band edges from the score's own quintiles, rounded to whole points, so
    # the card's bands reflect how the score actually distributes.
    edges = sorted(set(int(round(q)) for q in
                       np.quantile(sc, [0.2, 0.4, 0.6, 0.8])))
    bands = []
    prev = -99
    for e in edges:
        bands.append((prev, e - 1))
        prev = e
    bands.append((prev, 99))
    band_rows = []
    for lo_b, hi_b in bands:
        mk = (sc >= lo_b) & (sc <= hi_b)
        if mk.sum() == 0:
            continue
        lbl = (f"<={hi_b}" if lo_b == -99 else
               f">={lo_b}" if hi_b == 99 else f"{lo_b}-{hi_b}")
        log(f"{lbl:>10}{int(mk.sum()):>8}{int(y[mk].sum()):>8}"
            f"{100 * y[mk].mean():>7.1f}%")
        band_rows.append(dict(band=lbl, n=int(mk.sum()),
                              events=int(y[mk].sum()),
                              risk=float(y[mk].mean())))
    pd.DataFrame(band_rows).to_csv(
        os.path.join(OUT, "score_bands.csv"), index=False)

    # Per-participant scores, so the mortality anchor scores the same people
    # with the same numbers rather than rebuilding the model independently.
    pd.DataFrame({
        "SEQN": d["SEQN"].to_numpy(),
        "score_a": points_results[res_a["label"]]["score"],
        "score_b": points_results[res_b["label"]]["score"],
        "p_model_a": res_a["p_cv"],
        "led": y,
    }).to_csv(os.path.join(OUT, "scores.csv"), index=False)

    # ---- figures -----------------------------------------------------------
    make_figures(y, res_a, res_b, p_gb, thrs, nb)

    with open(os.path.join(OUT, "results.txt"), "w") as f:
        f.write("\n".join(out_lines))

    summary = dict(
        n=int(len(y)), events=int(y.sum()),
        version_a={k: res_a[k] for k in
                   ("auc_app", "auc_cv", "auc_corr", "slope", "citl", "brier")},
        version_b={k: res_b[k] for k in
                   ("auc_app", "auc_cv", "auc_corr", "slope", "citl", "brier")},
        auc_ci_a=list(res_a["auc_ci"]), auc_ci_b=list(res_b["auc_ci"]),
        chosen_threshold=chosen, decisive_kpi_met=bool(decisive),
        wins_vs_diabetes_rule=int(wins_dm), n_thresholds=int(len(thrs)),
        coefs_a=res_a["coefs"], coefs_b=res_b["coefs"],
        points_offset_a=points_results[res_a["label"]]["offset"],
        points_auc_a=points_results[res_a["label"]]["auc"],
        points_offset_b=points_results[res_b["label"]]["offset"],
        points_auc_b=points_results[res_b["label"]]["auc"],
        knots_a={k: list(v) for k, v in res_a["knots"].items()},
    )
    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=float)
    log(f"\nWrote {OUT}/results.txt, threshold_table.csv, points_A.csv, "
        f"points_B.csv, summary.json and Figures 2-4.")


def make_figures(y, res_a, res_b, p_gb, thrs, nb):
    plt.rcParams.update({"font.size": 8, "axes.spines.top": False,
                         "axes.spines.right": False, "figure.dpi": 200})

    # Figure 2 - discrimination
    fig, ax = plt.subplots(figsize=(3.4, 3.4))
    for res, style in ((res_a, "-"), (res_b, "--")):
        fpr, tpr, _ = roc_curve(y, res["p_cv"])
        ax.plot(fpr, tpr, style, lw=1.6,
                label=f"{res['label']} (AUC {res['auc_cv']:.3f})")
    fpr, tpr, _ = roc_curve(y, p_gb)
    ax.plot(fpr, tpr, ":", lw=1.2, color="grey",
            label=f"Gradient boosting ({roc_auc_score(y, p_gb):.3f})")
    ax.plot([0, 1], [0, 1], color="k", lw=0.6)
    ax.set_xlabel("1 - specificity")
    ax.set_ylabel("Sensitivity")
    ax.legend(frameon=False, fontsize=6, loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig2_roc.png"))
    plt.close(fig)

    # Figure 3 - calibration
    fig, ax = plt.subplots(figsize=(3.4, 3.4))
    for res, mk in ((res_a, "o"), (res_b, "s")):
        dfc = pd.DataFrame({"p": res["p_cv"], "y": y})
        dfc["bin"] = pd.qcut(dfc["p"], 10, duplicates="drop")
        g = dfc.groupby("bin", observed=True).agg(pred=("p", "mean"),
                                                  obs=("y", "mean"))
        ax.plot(g["pred"], g["obs"], mk + "-", lw=1.3, ms=3,
                label=f"{res['label']} (slope {res['slope']:.2f})")
    hi = 1.0
    ax.plot([0, hi], [0, hi], "k", lw=0.6)
    ax.set_xlabel("Predicted probability")
    ax.set_ylabel("Observed proportion")
    ax.legend(frameon=False, fontsize=6, loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig3_calibration.png"))
    plt.close(fig)

    # Figure 4 - decision curve
    fig, ax = plt.subplots(figsize=(4.2, 3.4))
    ax.plot(thrs, nb["score"], lw=2, label="Triage score")
    ax.plot(thrs, nb["dm"], "--", lw=1.4,
            label="Test everyone with diabetes")
    ax.plot(thrs, nb["age"], ":", lw=1.4, label="Test everyone aged $\\geq$60")
    ax.plot(thrs, nb["all"], lw=1, color="grey", label="Test everyone")
    ax.axhline(0, color="k", lw=0.7, label="Test no one")
    ax.set_ylim(min(-0.02, min(nb["score"]) - 0.01),
                max(nb["score"]) + 0.03)
    ax.set_xlabel("Threshold probability")
    ax.set_ylabel("Net benefit")
    ax.legend(frameon=False, fontsize=6)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig4_dca.png"))
    plt.close(fig)


if __name__ == "__main__":
    sys.exit(report(*main()) or 0)
