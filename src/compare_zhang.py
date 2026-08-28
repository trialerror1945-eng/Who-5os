#!/usr/bin/env python3
"""
compare_zhang.py - head-to-head against the closest published competitor.

Zhang Y, Huang J, Wang P. A prediction model for the peripheral arterial
disease using NHANES data. Medicine 2016;95(16):e3454.

Same survey, overlapping cycles, same PAD definition. Their final model is
age, sex, race, pulse pressure, the total-cholesterol/HDL ratio and ever-
smoking, reported at C=0.82 in training (NHANES 1999-2002) and 0.76 in
external validation (2003-2004).

Rather than argue about novelty in prose, this refits their variable set on
our cohort and puts both models through the same tests: their endpoint, our
endpoint, and the decision-curve comparison against the rule clinicians
actually use - which their paper does not report.

    python3 src/compare_zhang.py
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import OUT
from modeling import fit_logistic, net_benefit, threshold_metrics

SEED = 20260828
lines = []


def log(m=""):
    print(m)
    lines.append(str(m))


def cv_predict(X, y, folds=10):
    cv = StratifiedKFold(folds, shuffle=True, random_state=SEED)
    p = np.zeros(len(y))
    for tr, te in cv.split(X, y):
        p[te] = fit_logistic(X[tr], y[tr]).predict_proba(X[te])[:, 1]
    return p


def main():
    d = pd.read_csv(os.path.join(OUT, "cohort.csv"))
    d = d[d["led"].notna()].reset_index(drop=True)

    d["sex_f"] = (d["sex"] == 2).astype(float)
    d["smoke_ever"] = (d["smoke"] >= 1).astype(float)      # their coding
    d["smoke_former"] = (d["smoke"] == 1).astype(float)
    d["smoke_current"] = (d["smoke"] == 2).astype(float)
    d["pulse_pressure"] = d["sbp"] - d["dbp"]
    d["tc_hdl"] = d["tchol"] / d["hdl"]
    # Their race terms, White as reference.
    d["race_mex"] = d["race"].isin([1, 2]).astype(float)   # Mexican + other Hispanic
    d["race_black"] = (d["race"] == 4).astype(float)
    d["race_other"] = (d["race"] == 5).astype(float)

    ZHANG = ["age", "sex_f", "race_mex", "race_black", "race_other",
             "pulse_pressure", "tc_hdl", "smoke_ever"]
    OURS = ["age", "sbp", "waist", "sex_f", "smoke_former", "smoke_current",
            "dm_dur_cat", "htn_med", "prior_cvd"]

    log("=" * 72)
    log("HEAD-TO-HEAD: Zhang 2016 variable set vs the triage score")
    log("=" * 72)

    # ---- coverage: can the model even be computed? ------------------------
    log("\n--- DEPLOYABILITY: for how many patients can each score be computed? ---")
    cov_z = d[ZHANG].notna().all(axis=1)
    cov_o = d[OURS].notna().all(axis=1)
    log(f"  Zhang 2016 (needs a lipid panel) : {int(cov_z.sum()):5d} / {len(d)} "
        f"({100 * cov_z.mean():.1f}%)")
    log(f"  Triage score (no laboratory)     : {int(cov_o.sum()):5d} / {len(d)} "
        f"({100 * cov_o.mean():.1f}%)")
    log(f"  Patients Zhang cannot score      : {int((~cov_z).sum()):5d} "
        f"({100 * (~cov_z).mean():.1f}%)")
    log("  A lipid panel is not a formality in a health centre without one.")

    # ---- like-for-like on complete cases -----------------------------------
    cc = d[cov_z & cov_o].reset_index(drop=True)
    log(f"\nLike-for-like comparison on {len(cc)} participants with both "
        f"variable sets complete.")

    results = {}
    for label, target in (("PAD alone (their endpoint)", "pad"),
                          ("Composite LED (our endpoint)", "led")):
        sub = cc[cc[target].notna()].reset_index(drop=True)
        y = sub[target].to_numpy(float)
        log(f"\n--- {label}:  n={len(sub)}, events={int(y.sum())} "
            f"({100 * y.mean():.1f}%) ---")
        row = {}
        for name, cols in (("Zhang 2016", ZHANG), ("Triage score", OURS)):
            X = sub[cols].to_numpy(float)
            p = cv_predict(X, y)
            auc = roc_auc_score(y, p)
            row[name] = (auc, p, y, sub)
            log(f"  {name:14s} AUC {auc:.3f}")
        diff = row["Triage score"][0] - row["Zhang 2016"][0]
        log(f"  Difference                {diff:+.3f}")
        results[target] = row

    # ---- the test their paper never runs -----------------------------------
    log("\n" + "=" * 72)
    log("THE TEST NEITHER PAPER'S PREDECESSORS RAN: net benefit vs the")
    log("'test everyone with diabetes' heuristic, on the composite endpoint")
    log("=" * 72)
    row = results["led"]
    sub = row["Zhang 2016"][3]
    y = row["Zhang 2016"][2]
    dm_rule = (sub["dm"].fillna(0) == 1).to_numpy().astype(float)
    age_rule = (sub["age"] >= 60).to_numpy().astype(float)

    log(f"{'thresh':>8}{'Zhang':>10}{'Triage':>10}{'diabetes':>10}"
        f"{'age>=60':>10}")
    thrs = np.arange(0.05, 0.61, 0.05)
    wins_z = wins_o = 0
    for t in thrs:
        nb_z = net_benefit(y, row["Zhang 2016"][1], t)
        nb_o = net_benefit(y, row["Triage score"][1], t)
        nb_d = net_benefit(y, dm_rule, t)
        nb_a = net_benefit(y, age_rule, t)
        wins_z += nb_z > nb_d
        wins_o += nb_o > nb_d
        log(f"{t:>8.2f}{nb_z:>10.4f}{nb_o:>10.4f}{nb_d:>10.4f}{nb_a:>10.4f}")
    log(f"\n  Zhang 2016 beats the diabetes rule at  {wins_z}/{len(thrs)} thresholds")
    log(f"  Triage score beats it at               {wins_o}/{len(thrs)} thresholds")

    # ---- examination burden -------------------------------------------------
    log("\n--- EXAMINATION BURDEN AT SENSITIVITY >=0.85 (composite endpoint) ---")
    for name in ("Zhang 2016", "Triage score"):
        p = row[name][1]
        best = None
        for t in np.arange(0.02, 0.9, 0.005):
            m = threshold_metrics(y, p, t)
            if m["sens"] >= 0.85:
                best = m if best is None or m["burden"] < best["burden"] else best
        if best:
            log(f"  {name:14s} examine {100 * best['burden']:5.1f}% "
                f"(sens {best['sens']:.2f}, NNT {best['nnt']:.1f})")

    with open(os.path.join(OUT, "comparison_zhang2016.txt"), "w") as f:
        f.write("\n".join(lines))
    log(f"\nWrote {OUT}/comparison_zhang2016.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
