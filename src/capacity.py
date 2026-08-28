#!/usr/bin/env python3
"""
capacity.py - the analysis the clinical problem actually poses.

A decision curve answers "is this model worth using at threshold t?". That is
not the question a puskesmas asks. Its question is fixed by the morning's
staffing: *we can examine twenty feet today - whose?* Net benefit does not
answer that, because it prices false positives against true positives on an
abstract exchange rate rather than against a hard ceiling on examinations.

So this evaluates every strategy under an explicit capacity constraint K: rank
all attendees, examine the top K%, and count what is found. The framework is
the one Kelly et al. set out for constrained diagnostic capacity in COVID
testing (Med Decis Making 2021); it has not, as far as we can find, been
applied to lower-extremity disease.

Strategies compared, all under the same ceiling:
  - the triage score
  - the Zhang 2016 published model
  - test everyone with diabetes (the rule in current use)
  - test everyone aged >=60
  - random selection (what an unordered queue delivers)

    python3 src/capacity.py
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import OUT
from modeling import fit_logistic

SEED = 20260828
CAPACITIES = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
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


def yield_at_capacity(y, rank, k, rng, n_rep=200):
    """Cases found when the top k fraction by `rank` is examined.

    Ties matter here and are not a technicality. "Everyone with diabetes" is a
    binary rule: at a capacity below the number of diabetic attendees it gives
    no way to choose among them, so the tie is broken at random and averaged.
    Ranking the tied group by anything else would be crediting the rule with
    information it does not have.
    """
    n = len(y)
    n_exam = int(round(k * n))
    if n_exam == 0:
        return 0.0, 0.0
    found = []
    for _ in range(n_rep):
        jitter = rng.random(n) * 1e-6
        order = np.argsort(-(rank + jitter))
        found.append(y[order[:n_exam]].sum())
    found = np.array(found)
    return found.mean(), found.std()


def main():
    d = pd.read_csv(os.path.join(OUT, "cohort.csv"))
    d = d[d["led"].notna()].reset_index(drop=True)
    d["sex_f"] = (d["sex"] == 2).astype(float)
    d["smoke_former"] = (d["smoke"] == 1).astype(float)
    d["smoke_current"] = (d["smoke"] == 2).astype(float)
    d["smoke_ever"] = (d["smoke"] >= 1).astype(float)
    d["pulse_pressure"] = d["sbp"] - d["dbp"]
    d["tc_hdl"] = d["tchol"] / d["hdl"]
    d["race_mex"] = d["race"].isin([1, 2]).astype(float)
    d["race_black"] = (d["race"] == 4).astype(float)
    d["race_other"] = (d["race"] == 5).astype(float)

    OURS = ["age", "sbp", "waist", "sex_f", "smoke_former", "smoke_current",
            "dm_dur_cat", "htn_med", "prior_cvd"]
    ZHANG = ["age", "sex_f", "race_mex", "race_black", "race_other",
             "pulse_pressure", "tc_hdl", "smoke_ever"]

    cc = d[d[OURS + ZHANG].notna().all(axis=1)].reset_index(drop=True)
    y = cc["led"].to_numpy(float)
    rng = np.random.default_rng(SEED)

    log("=" * 74)
    log("EXAMINATION UNDER A CAPACITY CEILING")
    log("=" * 74)
    log(f"Attendees {len(cc)}, cases {int(y.sum())} ({100 * y.mean():.1f}%)")
    log("Every strategy ranks the same people; only the ranking differs.")

    p_ours = cv_predict(cc[OURS].to_numpy(float), y)
    p_zhang = cv_predict(cc[ZHANG].to_numpy(float), y)
    strategies = {
        "Triage score": p_ours,
        "Zhang 2016": p_zhang,
        "Diabetes rule": (cc["dm"].fillna(0) == 1).to_numpy(float),
        "Age >=60 rule": (cc["age"] >= 60).to_numpy(float),
        "Random order": rng.random(len(y)),
    }

    log(f"\n--- CASES FOUND, by share of attendees examined ---")
    hdr = "".join(f"{int(100 * k):>8}%" for k in CAPACITIES)
    log(f"{'strategy':<16}{hdr}")
    results = {}
    for name, rank in strategies.items():
        row = []
        for k in CAPACITIES:
            m, _ = yield_at_capacity(y, rank, k, rng)
            row.append(m)
        results[name] = row
        log(f"{name:<16}" + "".join(f"{v:>9.0f}" for v in row))

    log(f"\n--- SHARE OF ALL CASES CAPTURED (sensitivity at that capacity) ---")
    log(f"{'strategy':<16}{hdr}")
    for name, row in results.items():
        log(f"{name:<16}" + "".join(f"{100 * v / y.sum():>8.1f}%" for v in row))

    log(f"\n--- EXTRA CASES FOUND vs THE DIABETES RULE, same capacity ---")
    log(f"{'strategy':<16}{hdr}")
    base = results["Diabetes rule"]
    for name in ("Triage score", "Zhang 2016", "Age >=60 rule", "Random order"):
        row = results[name]
        log(f"{name:<16}" + "".join(f"{v - b:>+9.0f}" for v, b in zip(row, base)))

    log(f"\n--- CASES FOUND PER 100 EXAMINATIONS (the clinic's efficiency) ---")
    log(f"{'strategy':<16}{hdr}")
    for name, row in results.items():
        log(f"{name:<16}"
            + "".join(f"{100 * v / max(round(k * len(cc)), 1):>9.1f}"
                      for v, k in zip(row, CAPACITIES)))

    # ---- the headline number ------------------------------------------------
    k = 0.20
    n_exam = int(round(k * len(cc)))
    ours = results["Triage score"][CAPACITIES.index(k)]
    dmr = results["Diabetes rule"][CAPACITIES.index(k)]
    log("\n" + "=" * 74)
    log(f"AT 20% CAPACITY ({n_exam} examinations per {len(cc)} attendees)")
    log("=" * 74)
    log(f"  Triage score finds  {ours:.0f} cases")
    log(f"  Diabetes rule finds {dmr:.0f} cases")
    log(f"  Difference          {ours - dmr:+.0f} cases "
        f"({100 * (ours - dmr) / dmr:+.0f}%)")
    log(f"  Put the other way: the diabetes rule would need "
        f"{100 * next((kk for kk, v in zip(CAPACITIES, results['Diabetes rule']) if v >= ours), 1.0):.0f}% "
        f"capacity to find what the score finds at 20%.")

    log("\n--- DISCRIMINATION, for reference ---")
    log(f"  Triage score AUC {roc_auc_score(y, p_ours):.3f}   "
        f"Zhang 2016 AUC {roc_auc_score(y, p_zhang):.3f}")

    pd.DataFrame(results, index=[f"{int(100*k)}%" for k in CAPACITIES]).to_csv(
        os.path.join(OUT, "capacity_yield.csv"))
    with open(os.path.join(OUT, "capacity.txt"), "w") as f:
        f.write("\n".join(lines))
    log(f"\nWrote {OUT}/capacity.txt and capacity_yield.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
