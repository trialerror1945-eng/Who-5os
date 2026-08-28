#!/usr/bin/env python3
"""
mortality.py - the prognostic anchor.

    python3 src/mortality.py

Asks whether the triage score marks people who go on to die sooner, not just
people who will fail a test today. Cox models for cardiovascular and all-cause
mortality by score band, follow-up to 31 December 2019.

This changes what the score claims. A score that only predicts the result of a
Doppler examination is a convenience; one that also stratifies survival is
identifying people whose feet are a symptom of something systemic.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from statsmodels.duration.hazard_regression import PHReg

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import OUT

out_lines = []


def log(msg=""):
    print(msg)
    out_lines.append(str(msg))


def km(times, events):
    """Kaplan-Meier survival curve, written out to avoid a dependency."""
    order = np.argsort(times)
    t, e = times[order], events[order]
    uniq = np.unique(t)
    surv, s, n = [], 1.0, len(t)
    for ut in uniq:
        at_risk = int(np.sum(t >= ut))
        d = int(np.sum((t == ut) & (e == 1)))
        if at_risk > 0 and d > 0:
            s *= (1 - d / at_risk)
        surv.append(s)
    return uniq, np.array(surv)


def cox(df, covariates, event_col, time_col):
    d = df[covariates + [event_col, time_col]].dropna()
    d = d[d[time_col] > 0]
    if d[event_col].sum() < 10:
        return None
    model = PHReg(d[time_col].to_numpy(float),
                  d[covariates].to_numpy(float),
                  status=d[event_col].to_numpy(float))
    return model.fit(disp=False), len(d), int(d[event_col].sum())


def main():
    coh = pd.read_csv(os.path.join(OUT, "cohort.csv"))
    sc_path = os.path.join(OUT, "scores.csv")
    if not os.path.exists(sc_path):
        print("results/scores.csv missing - run src/analyze.py first.")
        return 1
    sc = pd.read_csv(sc_path)
    d = coh.merge(sc[["SEQN", "score_a", "led"]].drop(columns="led"),
                  on="SEQN", how="inner")

    d = d[d["months"].notna() & d["dead"].notna()]
    d["years"] = d["months"] / 12.0
    d = d[d["years"] > 0]

    log("=" * 70)
    log("PROGNOSTIC ANCHOR - mortality through 31 December 2019")
    log("=" * 70)
    log(f"Linked participants        : {len(d)}")
    log(f"Median follow-up (years)   : {d['years'].median():.1f}")
    log(f"Deaths, all causes         : {int(d['dead'].sum())}")
    log(f"Deaths, cardiovascular     : {int(d['cv_death'].sum())}")

    # ---- score bands -------------------------------------------------------
    edges = [int(round(q)) for q in np.quantile(d["score_a"], [.25, .5, .75])]
    edges = sorted(set(edges))
    d["band"] = np.digitize(d["score_a"], edges)
    labels = {}
    prev = int(d["score_a"].min())
    for i, e in enumerate(edges):
        labels[i] = f"{prev}-{e - 1}"
        prev = e
    labels[len(edges)] = f">={prev}"

    log("\n--- MORTALITY BY SCORE BAND ---")
    log(f"{'band':>10}{'n':>7}{'deaths':>8}{'CV deaths':>11}"
        f"{'all-cause/1000py':>18}{'CV/1000py':>12}")
    for b in sorted(d["band"].unique()):
        g = d[d["band"] == b]
        py = g["years"].sum()
        log(f"{labels[b]:>10}{len(g):>7}{int(g['dead'].sum()):>8}"
            f"{int(g['cv_death'].sum()):>11}"
            f"{1000 * g['dead'].sum() / py:>18.1f}"
            f"{1000 * g['cv_death'].sum() / py:>12.1f}")

    # ---- Cox models --------------------------------------------------------
    for label, ev in (("ALL-CAUSE", "dead"), ("CARDIOVASCULAR", "cv_death")):
        log(f"\n--- COX, {label} MORTALITY ---")

        r = cox(d, ["score_a"], ev, "years")
        if r:
            fit, n, k = r
            hr = float(np.exp(fit.params[0]))
            lo, hi = np.exp(fit.conf_int()[0])
            log(f"  per 1 point   HR {hr:.3f} (95% CI {lo:.3f}-{hi:.3f})   "
                f"n={n}, events={k}, p={fit.pvalues[0]:.2e}")

        # Adjusted for the demographics the score is built from, to show the
        # gradient is not simply age reappearing under another name.
        r = cox(d, ["score_a", "age", "sex"], ev, "years")
        if r:
            fit, n, k = r
            hr = float(np.exp(fit.params[0]))
            lo, hi = np.exp(fit.conf_int()[0])
            log(f"  adj age+sex   HR {hr:.3f} (95% CI {lo:.3f}-{hi:.3f})   "
                f"p={fit.pvalues[0]:.2e}")

        # And by measured disease, the thing the score is triaging for.
        r = cox(d, ["led"], ev, "years") if "led" in d.columns else None
        if r:
            fit, n, k = r
            hr = float(np.exp(fit.params[0]))
            lo, hi = np.exp(fit.conf_int()[0])
            log(f"  LED present   HR {hr:.3f} (95% CI {lo:.3f}-{hi:.3f})   "
                f"events={k}")

    # ---- Figure 5 ----------------------------------------------------------
    plt.rcParams.update({"font.size": 8, "axes.spines.top": False,
                         "axes.spines.right": False, "figure.dpi": 200})
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 3.0))
    for ax, (ev, title) in zip(axes, (("dead", "All-cause mortality"),
                                      ("cv_death", "Cardiovascular mortality"))):
        for b in sorted(d["band"].unique()):
            g = d[d["band"] == b]
            t, s = km(g["years"].to_numpy(), g[ev].to_numpy())
            ax.step(t, s, where="post", lw=1.4, label=f"score {labels[b]}")
        ax.set_xlabel("Years from examination")
        ax.set_ylabel("Survival")
        ax.set_title(title, fontsize=8)
        ax.set_ylim(0.4, 1.0)
    axes[0].legend(frameon=False, fontsize=6, loc="lower left")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig5_survival.png"))
    plt.close(fig)

    with open(os.path.join(OUT, "mortality.txt"), "w") as f:
        f.write("\n".join(out_lines))
    log(f"\nWrote {OUT}/mortality.txt and fig5_survival.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
