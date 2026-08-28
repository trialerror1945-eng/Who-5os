#!/usr/bin/env python3
"""
fig_capacity.py - Figure 1: what each triage strategy finds under a ceiling.

A cumulative gain curve is the honest form for this question. Every strategy
ranks the same attendees; the curve shows what share of all disease each one
has found by the time a given share of the clinic has been examined. The
diagonal is what an unordered queue delivers.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedKFold

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import OUT
from modeling import fit_logistic

SEED = 20260828

# Validated categorical slots (see dataviz validator, light mode):
# worst adjacent CVD dE 9.2, normal-vision 16.3, all checks pass.
C_SCORE = "#2a78d6"   # slot 1, blue
C_ZHANG = "#4a3aa7"   # slot 7, violet
C_DM    = "#eb6834"   # slot 2, orange
C_AGE   = "#1baf7a"   # slot 3, aqua
C_REF   = "#8a8a85"   # neutral: a reference baseline, not a category
INK     = "#16191b"
MUTED   = "#5c6669"


def cv_predict(X, y, folds=10):
    cv = StratifiedKFold(folds, shuffle=True, random_state=SEED)
    p = np.zeros(len(y))
    for tr, te in cv.split(X, y):
        p[te] = fit_logistic(X[tr], y[tr]).predict_proba(X[te])[:, 1]
    return p


def gain_curve(y, rank, rng, n_rep=60):
    """Share of cases found against share examined, ties broken at random.

    A binary rule gives no ordering inside its own group, so the tie is broken
    at random and averaged rather than credited with information it lacks.
    """
    n = len(y)
    acc = np.zeros(n + 1)
    for _ in range(n_rep):
        order = np.argsort(-(rank + rng.random(n) * 1e-6))
        acc[1:] += np.cumsum(y[order])
    acc /= n_rep
    return np.arange(n + 1) / n, acc / y.sum()


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

    series = [
        ("Triage score", cv_predict(cc[OURS].to_numpy(float), y), C_SCORE, "-", 2.2),
        ("Zhang 2016 model", cv_predict(cc[ZHANG].to_numpy(float), y), C_ZHANG, (0, (5, 1.6)), 1.6),
        ("Test everyone with diabetes", (cc["dm"].fillna(0) == 1).to_numpy(float), C_DM, (0, (3, 1.4)), 1.9),
        ("Test everyone aged 60+", (cc["age"] >= 60).to_numpy(float), C_AGE, (0, (1, 1.4)), 1.9),
        ("Unordered queue", rng.random(len(y)), C_REF, (0, (4, 3)), 1.2),
    ]

    plt.rcParams.update({
        "font.size": 8.5, "font.family": "DejaVu Sans",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#c9cfce", "axes.labelcolor": INK,
        "xtick.color": MUTED, "ytick.color": MUTED, "figure.dpi": 300,
    })
    fig, ax = plt.subplots(figsize=(5.6, 4.2))

    for name, rank, color, style, lw in series:
        x, g = gain_curve(y, rank, rng)
        ax.plot(x, 100 * g, color=color, ls=style, lw=lw, label=name,
                solid_capstyle="round")

    # A legend rather than direct labels: at five series the curves converge
    # in the upper right and every direct-label placement collided. The dash
    # patterns carry identity alongside hue, which the aqua slot needs - it
    # sits below 3:1 against this surface.
    ax.legend(loc="upper left", frameon=False, fontsize=7.8,
              handlelength=2.6, borderpad=0, labelspacing=0.55,
              bbox_to_anchor=(0.015, 0.99))

    # The operating point the paper quotes.
    ax.axvline(0.20, color="#c9cfce", lw=0.9, zorder=0)
    # Sits at the foot of the rule: the head of it is under the legend.
    ax.annotate("20% capacity", (0.205, 1.5), fontsize=7.2, color=MUTED,
                ha="left", va="bottom")
    for rank_name, val, col in (("score", 42.0, C_SCORE), ("diabetes", 28.3, C_DM)):
        ax.plot([0.20], [val], "o", ms=5, color=col, mec="white", mew=1.2, zorder=5)
    ax.annotate("42%", (0.205, 42.0), fontsize=8, color=C_SCORE,
                weight="bold", va="center", xytext=(8, 0),
                textcoords="offset points")
    ax.annotate("28%", (0.205, 28.3), fontsize=8, color=C_DM,
                weight="bold", va="center", xytext=(8, 0),
                textcoords="offset points")

    ax.set_xlim(0, 1); ax.set_ylim(0, 105)
    ax.set_xticks(np.arange(0, 1.01, 0.2))
    ax.set_xticklabels([f"{int(100*v)}%" for v in np.arange(0, 1.01, 0.2)])
    ax.set_yticks(np.arange(0, 101, 25))
    ax.set_yticklabels([f"{v}%" for v in np.arange(0, 101, 25)])
    ax.set_xlabel("Share of attendees examined")
    ax.set_ylabel("Share of all lower-extremity disease found")
    ax.grid(axis="y", color="#eef1f0", lw=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig1_capacity.png"), facecolor="white")
    plt.close(fig)
    print(f"Wrote {OUT}/fig1_capacity.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
