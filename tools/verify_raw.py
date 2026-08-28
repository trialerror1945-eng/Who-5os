#!/usr/bin/env python3
"""
verify_raw.py - assert the downloaded NHANES files parse to the exact
frequencies published in the official 2003-2004 codebooks (LEXAB_C, LEXPN_C).

This is a hard gate, not a smoke test. The four data traps documented in
VARIABLES.md all corrupt the analysis silently - a -1 read as a count, a
column swapped, a merge that duplicates rows. None of them raise an error.
Matching the published frequencies to the last participant is the only cheap
way to prove the bytes on disk are the bytes NCHS released.

Exits non-zero on any mismatch.
"""

import os
import sys
import pandas as pd

RAW = os.path.join("data", "raw")

# Published frequencies, NHANES 2003-2004 Lower Extremity Disease codebooks.
# Keys are variable values; -1 means "insufficient information collected".
EXPECTED_PN = {
    "LEALPN": {0: 2269, 1: 243, 2: 91, 3: 60, -1: 87},   # left foot
    "LEARPN": {0: 2330, 1: 207, 2: 75, 3: 59, -1: 73},   # right foot
}
EXPECTED_PN_MISSING = {"LEALPN": 336, "LEARPN": 342}
EXPECTED_ABPI_PRESENT = {"LEXLABPI": 2346, "LEXRABPI": 2339}
EXPECTED_ABPI_MISSING = {"LEXLABPI": 740, "LEXRABPI": 747}
EXPECTED_LEXPN_N = 3086

failures = []


def check(label, got, want):
    ok = got == want
    print(f"  {'PASS' if ok else 'FAIL'}  {label:34s} got {got:>6}  want {want:>6}")
    if not ok:
        failures.append(label)


def main():
    pn_path = os.path.join(RAW, "2003-2004", "LEXPN.XPT")
    ab_path = os.path.join(RAW, "2003-2004", "LEXAB.XPT")
    for p in (pn_path, ab_path):
        if not os.path.exists(p):
            print(f"missing file: {p}")
            return 1

    print("LEXPN_C - monofilament (peripheral neuropathy)")
    pn = pd.read_sas(pn_path, format="xport")
    check("row count", len(pn), EXPECTED_LEXPN_N)

    for var, counts in EXPECTED_PN.items():
        if var not in pn.columns:
            print(f"  FAIL  {var} absent from file")
            failures.append(var)
            continue
        # Counted by direct equality rather than value_counts().get(). Series.get
        # does label lookup, and a 0.0 key against a float index resolves
        # unreliably - it reported zero for the 2269 genuine zeros while every
        # other level matched.
        for value, want in counts.items():
            got = int((pn[var] == value).sum())
            check(f"{var} == {value}", got, want)
        check(f"{var} missing", int(pn[var].isna().sum()),
              EXPECTED_PN_MISSING[var])

    print("\nLEXAB_C - ankle-brachial pressure index")
    ab = pd.read_sas(ab_path, format="xport")
    check("row count", len(ab), EXPECTED_LEXPN_N)
    for var, want in EXPECTED_ABPI_PRESENT.items():
        if var not in ab.columns:
            print(f"  FAIL  {var} absent from file")
            failures.append(var)
            continue
        check(f"{var} present", int(ab[var].notna().sum()), want)
        check(f"{var} missing", int(ab[var].isna().sum()),
              EXPECTED_ABPI_MISSING[var])

    print()
    if failures:
        print(f"VERIFICATION FAILED - {len(failures)} mismatch(es): "
              + ", ".join(failures))
        print("Do not proceed. The files on disk are not what NCHS published,")
        print("or the parser is reading them wrongly.")
        return 1
    print("VERIFICATION PASSED - all published frequencies reproduced exactly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
