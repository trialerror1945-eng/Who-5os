"""Shared helpers for the LED triage study pipeline."""

import os
import numpy as np
import pandas as pd

RAW = os.path.join("data", "raw")
OUT = "results"

CYCLES = ["1999-2000", "2001-2002", "2003-2004"]

# --- a priori decision thresholds, fixed before any data was inspected -------
ABI_LOW = 0.90         # PAD
ABI_HIGH = 1.40        # incompressible artery (sensitivity analysis only)
PN_MIN_INSENSATE = 1   # >=1 insensate site on either foot = neuropathy
AGE_MIN = 40

# NHANES questionnaire missing-value conventions.
REFUSED_DK = {
    1: [7, 9],
    2: [77, 99],
    3: [777, 999],
    4: [7777, 9999],
    5: [77777, 99999],
}


def read_xpt(cycle, name):
    """Read one NHANES transport file; return None if absent."""
    path = os.path.join(RAW, cycle, f"{name}.XPT")
    if not os.path.exists(path):
        return None
    df = pd.read_sas(path, format="xport")
    df.columns = [c.upper() for c in df.columns]
    if "SEQN" in df.columns:
        df["SEQN"] = df["SEQN"].astype("int64")
        # A duplicated SEQN would silently multiply rows at every merge.
        if df["SEQN"].duplicated().any():
            raise ValueError(f"{cycle}/{name}: duplicated SEQN")
    return df


def col(df, *candidates):
    """First candidate column present, as a float Series; NaN Series if none.

    Variable names drift between cycles far more than the codebooks suggest,
    so every access goes through a candidate list rather than a fixed name.
    """
    if df is None:
        return None
    for c in candidates:
        if c in df.columns:
            return pd.to_numeric(df[c], errors="coerce")
    return pd.Series(np.nan, index=df.index, dtype=float)


def clean(series, width=1):
    """Blank out NHANES refused / don't-know codes at the given digit width."""
    if series is None:
        return series
    return series.replace(REFUSED_DK[width], np.nan)


def yes_no(series, width=1):
    """NHANES 1=yes / 2=no -> 1.0 / 0.0, with refused and don't-know as NaN.

    Written out rather than using (s == 1), which quietly maps 'refused' and
    'don't know' to 'no' and biases every prevalence downwards.
    """
    s = clean(series, width)
    out = pd.Series(np.nan, index=s.index, dtype=float)
    out[s == 1] = 1.0
    out[s == 2] = 0.0
    return out


def ckd_epi_2021(scr, age, female):
    """eGFR, CKD-EPI 2021 creatinine equation (race-free)."""
    kappa = np.where(female == 1, 0.7, 0.9)
    alpha = np.where(female == 1, -0.241, -0.302)
    ratio = scr / kappa
    egfr = (142
            * np.minimum(ratio, 1) ** alpha
            * np.maximum(ratio, 1) ** -1.200
            * 0.9938 ** age
            * np.where(female == 1, 1.012, 1.0))
    return pd.Series(egfr, index=scr.index)


def calibrate_creatinine(scr, cycle):
    """Align serum creatinine across cycles to the 2003-2004 standard.

    NCHS documents that the 1999-2000 assay reads high relative to later
    cycles and publishes a correction; 2001-2002 needs none. Skipping this
    puts a step change in eGFR at a cycle boundary that looks like signal.
    """
    if cycle == "1999-2000":
        return 1.013 * scr + 0.147
    return scr
