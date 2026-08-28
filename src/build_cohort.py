#!/usr/bin/env python3
"""
build_cohort.py - assemble the analysis cohort from raw NHANES transport files.

    python3 src/build_cohort.py

Writes results/cohort.csv and results/flow.txt (the participant flow diagram).

Every threshold used here was fixed before the data were inspected and is
declared in src/common.py, not buried in this file.
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (RAW, OUT, CYCLES, ABI_LOW, ABI_HIGH, PN_MIN_INSENSATE,
                    AGE_MIN, read_xpt, col, clean, yes_no, ckd_epi_2021,
                    calibrate_creatinine)

flow = []


def log(msg=""):
    print(msg)
    flow.append(str(msg))


def frame(df, **cols):
    """Build a SEQN-keyed frame from columns of df."""
    out = pd.DataFrame({"SEQN": df["SEQN"]})
    for k, v in cols.items():
        out[k] = v.to_numpy() if isinstance(v, pd.Series) else v
    return out


def build_cycle(cycle):
    log(f"\n--- {cycle} ---")
    demo = read_xpt(cycle, "DEMO")
    if demo is None:
        log("  DEMO absent - cycle skipped")
        return None

    # Six-year MEC weights. NHANES guidance for pooling 1999-2004 is the
    # four-year weight scaled by 2/3 for 1999-2002 and the two-year weight
    # scaled by 1/3 for 2003-2004. Using WTMEC2YR throughout would overstate
    # the earlier cycles by a factor of two.
    if cycle in ("1999-2000", "2001-2002"):
        w4 = col(demo, "WTMEC4YR")
        wt = w4 * (2.0 / 3.0)
        if w4.isna().all():
            log("  WTMEC4YR absent - falling back to WTMEC2YR (check this)")
            wt = col(demo, "WTMEC2YR") * (1.0 / 3.0)
    else:
        wt = col(demo, "WTMEC2YR") * (1.0 / 3.0)

    d = frame(
        demo,
        age=col(demo, "RIDAGEYR"),
        sex=col(demo, "RIAGENDR"),
        race=col(demo, "RIDRETH1"),
        wt=wt,
        psu=col(demo, "SDMVPSU"),
        strata=col(demo, "SDMVSTRA"),
    )
    d["cycle"] = cycle
    log(f"  DEMO      {len(d):5d} rows")

    # ---- anthropometry -----------------------------------------------------
    bmx = read_xpt(cycle, "BMX")
    if bmx is not None:
        d = d.merge(frame(bmx, bmi=col(bmx, "BMXBMI"),
                          waist=col(bmx, "BMXWAIST")), on="SEQN", how="left")
    else:
        d["bmi"] = np.nan
        d["waist"] = np.nan

    # ---- blood pressure: mean of all valid readings ------------------------
    bpx = read_xpt(cycle, "BPX")
    if bpx is not None:
        sysc = [c for c in ("BPXSY1", "BPXSY2", "BPXSY3", "BPXSY4")
                if c in bpx.columns]
        diac = [c for c in ("BPXDI1", "BPXDI2", "BPXDI3", "BPXDI4")
                if c in bpx.columns]
        # A zero diastolic is NHANES' code for an unobtainable Korotkoff
        # phase 5, not a measurement; averaging it in drags DBP down.
        sbp = bpx[sysc].replace(0, np.nan).mean(axis=1) if sysc else np.nan
        dbp = bpx[diac].replace(0, np.nan).mean(axis=1) if diac else np.nan
        d = d.merge(frame(bpx, sbp=sbp, dbp=dbp), on="SEQN", how="left")
        log(f"  BPX       {len(sysc)} systolic readings averaged")
    else:
        d["sbp"] = np.nan
        d["dbp"] = np.nan

    # ---- diabetes ----------------------------------------------------------
    diq = read_xpt(cycle, "DIQ")
    if diq is not None:
        dm = clean(col(diq, "DIQ010"))
        dm_bin = pd.Series(np.nan, index=diq.index, dtype=float)
        dm_bin[dm == 1] = 1.0
        dm_bin[dm.isin([2, 3])] = 0.0        # 3 = borderline, treated as no
        # DIQ040Q (1999-2000) and DID040Q (2001-2004) hold age at diagnosis in
        # years. The similarly named DID040G / DIQ040G do NOT: they are a
        # 1/2/7/9 flag saying whether an age was given. Reading the flag as an
        # age puts every diabetic participant's diagnosis at age 1 and turns
        # diabetes duration into a near-constant 50 years, with nothing to
        # signal that anything went wrong.
        age_dx = col(diq, "DIQ040Q", "DID040Q")
        age_dx = age_dx.where(age_dx < 120)
        d = d.merge(frame(diq, dm=dm_bin, dm_age_dx=age_dx),
                    on="SEQN", how="left")
    else:
        d["dm"] = np.nan
        d["dm_age_dx"] = np.nan

    # ---- smoking -----------------------------------------------------------
    smq = read_xpt(cycle, "SMQ")
    if smq is not None:
        ever = clean(col(smq, "SMQ020"))     # >=100 cigarettes lifetime
        now = clean(col(smq, "SMQ040"))      # 1,2 = still smokes; 3 = not now
        smk = pd.Series(np.nan, index=smq.index, dtype=float)
        smk[ever == 2] = 0.0                             # never
        smk[(ever == 1) & (now == 3)] = 1.0              # former
        smk[(ever == 1) & (now.isin([1, 2]))] = 2.0      # current
        d = d.merge(frame(smq, smoke=smk), on="SEQN", how="left")
    else:
        d["smoke"] = np.nan

    # ---- hypertension ------------------------------------------------------
    bpq = read_xpt(cycle, "BPQ")
    if bpq is not None:
        d = d.merge(frame(bpq,
                          htn_hx=yes_no(col(bpq, "BPQ020")),
                          htn_med=yes_no(col(bpq, "BPQ050A", "BPQ040A"))),
                    on="SEQN", how="left")
        # Not being on treatment is only meaningful for those told they had
        # hypertension; the question is skipped for everyone else.
        d.loc[d["htn_hx"] == 0, "htn_med"] = 0.0
    else:
        d["htn_hx"] = np.nan
        d["htn_med"] = np.nan

    # ---- prior cardiovascular disease --------------------------------------
    mcq = read_xpt(cycle, "MCQ")
    if mcq is not None:
        parts = [yes_no(col(mcq, c))
                 for c in ("MCQ160B", "MCQ160C", "MCQ160E", "MCQ160F")
                 if c in mcq.columns]
        if parts:
            stack = pd.concat(parts, axis=1)
            # Positive if any condition is yes; missing only if all are missing.
            cvd = np.where(stack.eq(1).any(axis=1), 1.0,
                           np.where(stack.notna().any(axis=1), 0.0, np.nan))
        else:
            cvd = np.nan
        d = d.merge(frame(mcq, prior_cvd=pd.Series(cvd, index=mcq.index)),
                    on="SEQN", how="left")
    else:
        d["prior_cvd"] = np.nan

    # ---- LABEL 1: ankle-brachial pressure index ----------------------------
    ab = read_xpt(cycle, "LEXAB")
    if ab is None:
        log("  LEXAB absent - cycle unusable")
        return None
    left = col(ab, "LEXLABPI")
    right = col(ab, "LEXRABPI")
    both = pd.concat([left, right], axis=1)
    # Incompressible: ankle systolic above 255 mmHg, which leaves ABPI blank.
    # These flags exist only from 2001-2002 on. Where the file does not carry
    # them the status is unknown, not negative - recording a 0 would assert
    # that nobody in 1999-2000 had an incompressible artery.
    if "LEALAPNC" in ab.columns or "LEARAPNC" in ab.columns:
        ncomp = np.where(
            (clean(col(ab, "LEALAPNC")) == 1) | (clean(col(ab, "LEARAPNC")) == 1),
            1.0, 0.0)
    else:
        log("  LEXAB     incompressible-artery flags absent this cycle")
        ncomp = np.nan
    d = d.merge(frame(ab,
                      abi_left=left, abi_right=right,
                      abi_min=both.min(axis=1), abi_max=both.max(axis=1),
                      noncompressible=pd.Series(ncomp, index=ab.index),
                      abpi_comment=col(ab, "LEDSCCT2")),
                on="SEQN", how="left")
    log(f"  LEXAB     {len(ab):5d} rows, {both.min(axis=1).notna().sum()} with ABPI")

    # ---- LABEL 2: monofilament ---------------------------------------------
    pn = read_xpt(cycle, "LEXPN")
    if pn is None:
        log("  LEXPN absent - composite endpoint cannot be built")
        return None
    # -1 means "insufficient information collected". Left numeric it reads as
    # fewer than zero insensate sites and corrupts the endpoint silently.
    lpn = col(pn, "LEALPN").replace(-1, np.nan)
    rpn = col(pn, "LEARPN").replace(-1, np.nan)
    amp = np.where(
        col(pn, "LEALAMP").isin([2, 3, 4, 5, 6])
        | col(pn, "LEARAMP").isin([2, 3, 4, 5, 6]), 1.0, 0.0)
    les = np.where((col(pn, "LEALLES") == 1) | (col(pn, "LEARLES") == 1),
                   1.0, 0.0)
    d = d.merge(frame(pn, pn_left=lpn, pn_right=rpn,
                      amputation=pd.Series(amp, index=pn.index),
                      foot_lesion=pd.Series(les, index=pn.index)),
                on="SEQN", how="left")
    log(f"  LEXPN     {len(pn):5d} rows, "
        f"{pd.concat([lpn, rpn], axis=1).notna().any(axis=1).sum()} with monofilament")

    # ---- laboratory (Version B) --------------------------------------------
    glu = read_xpt(cycle, "GLU")
    if glu is not None:
        d = d.merge(frame(glu, glucose=col(glu, "LBXGLU", "LBDGLUSI")),
                    on="SEQN", how="left")
    else:
        d["glucose"] = np.nan

    bio = read_xpt(cycle, "BIO")
    if bio is not None:
        # Serum creatinine is LBXSCR in 1999-2000 and 2003-2004 but LBDSCR in
        # 2001-2002.
        scr = calibrate_creatinine(col(bio, "LBXSCR", "LBDSCR"), cycle)
        d = d.merge(frame(bio, creatinine=scr), on="SEQN", how="left")
    else:
        d["creatinine"] = np.nan

    tc = read_xpt(cycle, "TCHOL")
    if tc is not None:
        d = d.merge(frame(tc, tchol=col(tc, "LBXTC")), on="SEQN", how="left")
    else:
        d["tchol"] = np.nan

    ghb = read_xpt(cycle, "GHB")
    if ghb is not None:
        d = d.merge(frame(ghb, hba1c=col(ghb, "LBXGH")), on="SEQN", how="left")
    else:
        d["hba1c"] = np.nan

    return d


def read_mortality(cycle):
    """Read one public-use linked mortality file (fixed width, through 2019)."""
    path = os.path.join(RAW, cycle, "MORT.dat")
    if not os.path.exists(path):
        return None
    # Column offsets verified against the delivered file rather than taken
    # from the layout document: the follow-up fields sit at 42-48, not where
    # a first reading of the spec put them, and reading blanks there yields a
    # silently all-missing follow-up time.
    spec = [(0, 14), (14, 15), (15, 16), (16, 19), (19, 20), (20, 21),
            (42, 45), (45, 48)]
    names = ["SEQN", "eligstat", "mortstat", "ucod_leading", "diabetes_mcod",
             "hyperten_mcod", "permth_int", "permth_exm"]
    m = pd.read_fwf(path, colspecs=spec, names=names, header=None)
    m["SEQN"] = pd.to_numeric(m["SEQN"], errors="coerce").astype("Int64")
    m = m[m["eligstat"] == 1]                      # eligible for linkage
    m["dead"] = pd.to_numeric(m["mortstat"], errors="coerce")
    m["ucod"] = pd.to_numeric(m["ucod_leading"], errors="coerce")
    # Leading-cause codes 001 (heart disease) and 005 (cerebrovascular)
    # are the cardiovascular deaths.
    m["cv_death"] = np.where(m["dead"] == 1,
                             m["ucod"].isin([1, 5]).astype(float), 0.0)
    m["months"] = pd.to_numeric(m["permth_exm"], errors="coerce")
    out = m[["SEQN", "dead", "cv_death", "months"]].dropna(subset=["SEQN"])
    out["SEQN"] = out["SEQN"].astype("int64")
    return out


def main():
    os.makedirs(OUT, exist_ok=True)

    parts = []
    for c in CYCLES:
        p = build_cycle(c)
        if p is not None:
            mort = read_mortality(c)
            if mort is not None:
                p = p.merge(mort, on="SEQN", how="left")
                log(f"  MORT      {p['dead'].notna().sum()} linked")
            else:
                p["dead"] = np.nan
                p["cv_death"] = np.nan
                p["months"] = np.nan
            parts.append(p)
    if not parts:
        log("\nNo cycle could be read. Run the fetch workflow first.")
        return 1
    d = pd.concat(parts, ignore_index=True)

    log("\n=== PARTICIPANT FLOW ===")
    log(f"All participants, three cycles          : {len(d)}")

    d = d[d["age"] >= AGE_MIN]
    log(f"Aged >={AGE_MIN} years                        : {len(d)}")

    # ---- endpoints ---------------------------------------------------------
    has_abi = d["abi_min"].notna()
    has_pn = d[["pn_left", "pn_right"]].notna().any(axis=1)

    d["pad"] = np.where(has_abi, (d["abi_min"] < ABI_LOW).astype(float), np.nan)
    d["pn"] = np.where(
        has_pn,
        ((d["pn_left"] >= PN_MIN_INSENSATE)
         | (d["pn_right"] >= PN_MIN_INSENSATE)).astype(float), np.nan)

    # Composite: positive if either component is positive; missing only when
    # both are missing. A participant negative on the one test they had is a
    # genuine negative for that test, not an unknown.
    d["led"] = np.where((d["pad"] == 1) | (d["pn"] == 1), 1.0,
                        np.where(has_abi | has_pn, 0.0, np.nan))

    # Sensitivity: abnormal ABI includes incompressible arteries.
    d["abi_abnormal"] = np.where(
        has_abi | (d["noncompressible"] == 1),
        ((d["abi_min"] < ABI_LOW) | (d["abi_max"] > ABI_HIGH)
         | (d["noncompressible"] == 1)).astype(float), np.nan)

    d["high_risk_foot"] = np.where(
        d["pad"].notna() & d["pn"].notna(),
        ((d["pad"] == 1) & (d["pn"] == 1)).astype(float), np.nan)

    before = len(d)
    d = d[d["led"].notna()]
    log(f"Had at least one valid LED test         : {len(d)}  (-{before - len(d)})")

    before = len(d)
    d = d[d["amputation"] != 1]
    log(f"Excluding prevalent amputation          : {len(d)}  (-{before - len(d)})")
    before = len(d)
    d = d[d["foot_lesion"] != 1]
    log(f"Excluding active foot lesion            : {len(d)}  (-{before - len(d)})")

    # ---- derived predictors ------------------------------------------------
    dur = np.where(d["dm"] == 1, d["age"] - d["dm_age_dx"], 0.0)
    d["dm_duration"] = np.clip(dur, 0, None)
    # Ordinal: 0 no diabetes, 1 <5y, 2 5-10y, 3 >10y. Diabetic participants
    # whose age at diagnosis is missing fall to category 1 rather than 0, so a
    # missing date never reads as "no diabetes".
    cat = pd.cut(d["dm_duration"], [-0.1, 0.001, 5, 10, 200],
                 labels=[0, 1, 2, 3]).astype(float)
    d["dm_dur_cat"] = np.where(d["dm"] == 1, np.where(np.isnan(cat), 1.0,
                                                     np.maximum(cat, 1.0)),
                               np.where(d["dm"] == 0, 0.0, np.nan))

    female = (d["sex"] == 2).astype(float)
    d["egfr"] = ckd_epi_2021(d["creatinine"], d["age"], female)

    log("\n=== ENDPOINT PREVALENCE (unweighted) ===")
    for lab in ["pad", "pn", "led", "abi_abnormal", "high_risk_foot"]:
        s = d[lab].dropna()
        if len(s):
            log(f"  {lab:16s} {int(s.sum()):5d} / {len(s):5d} = {100 * s.mean():5.1f}%")

    log("\n=== MISSINGNESS IN CANDIDATE PREDICTORS ===")
    for c in ["age", "sex", "sbp", "dbp", "bmi", "waist", "smoke", "dm",
              "dm_dur_cat", "htn_hx", "htn_med", "prior_cvd",
              "glucose", "egfr", "hba1c", "tchol"]:
        if c in d.columns:
            log(f"  {c:12s} missing {int(d[c].isna().sum()):5d} "
                f"({100 * d[c].isna().mean():5.1f}%)")

    log("\n=== BY CYCLE ===")
    log(d.groupby("cycle")["led"].agg(["size", "sum", "mean"]).to_string())

    d.to_csv(os.path.join(OUT, "cohort.csv"), index=False)
    with open(os.path.join(OUT, "flow.txt"), "w") as f:
        f.write("\n".join(flow))
    log(f"\nWrote {OUT}/cohort.csv ({len(d)} rows) and {OUT}/flow.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
