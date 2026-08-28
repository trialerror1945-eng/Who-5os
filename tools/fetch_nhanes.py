#!/usr/bin/env python3
"""
fetch_nhanes.py - retrieve every NHANES file required by the LED triage study.

Runs on a host with open internet (GitHub Actions runner). Writes to data/raw/.

Two things make this less trivial than it looks:

  1. NHANES file names are not consistent across cycles. The ABPI file is
     LEXABPI in 1999-2000 but LEXAB_B / LEXAB_C afterwards, and the laboratory
     files change name almost every cycle. Each logical file therefore carries
     a list of candidate names, tried in order.

  2. CDC serves the same file from two URL layouts depending on when the file
     was last republished. Both are tried before a candidate is declared dead.

Every downloaded file is recorded in data/raw/MANIFEST.json with its SHA-256,
so the analysis can assert it ran against the same bytes that were verified.
"""

import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request

OUT = os.path.join("data", "raw")

# CDC serves NHANES from two layouts. The modern one is tried first because
# the legacy path now answers with an HTML interstitial rather than a 404,
# which is indistinguishable from success on status code alone.
URL_PATTERNS = [
    "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/{year}/DataFiles/{fname}.xpt",
    "https://wwwn.cdc.gov/Nchs/Nhanes/{cycle}/{fname}.XPT",
]

# (cycle folder, file suffix, first year - used by the modern URL layout)
CYCLES = [
    ("1999-2000", "", "1999"),
    ("2001-2002", "_B", "2001"),
    ("2003-2004", "_C", "2003"),
]

# Core files. Version A (no laboratory) depends on all of these.
CORE = [
    ("DEMO",  ["DEMO"]),                  # age, sex, race, survey weights, strata, PSU
    ("BMX",   ["BMX"]),                   # BMI, waist circumference
    ("BPX",   ["BPX"]),                   # blood pressure
    ("LEXAB", ["LEXAB", "LEXABPI"]),      # ABPI            <- vascular label
    ("LEXPN", ["LEXPN"]),                 # monofilament    <- neuropathy label
    ("DIQ",   ["DIQ"]),                   # diabetes
    ("SMQ",   ["SMQ"]),                   # smoking
    ("BPQ",   ["BPQ"]),                   # hypertension history / treatment
    ("MCQ",   ["MCQ"]),                   # cardiovascular history
    ("CDQ",   ["CDQ"]),                   # Rose claudication / leg symptoms
]

# Laboratory files, for Version B only. Names are the least stable of all.
LAB = [
    ("GLU",   ["LAB10AM", "L10AM", "L10AM_B", "L10AM_C"]),   # fasting glucose
    ("BIO",   ["LAB18", "L40", "L40_B", "L40_C"]),           # biochemistry -> creatinine
    ("TCHOL", ["LAB13", "L13", "L13_B", "L13_C"]),           # total cholesterol
    ("GHB",   ["LAB10", "L10", "L10_B", "GHB_C"]),           # HbA1c
]

# Public-use linked mortality files, follow-up through 31 Dec 2019.
MORT_BASE = ("https://ftp.cdc.gov/pub/HEALTH_STATISTICS/NCHS/"
             "datalinkage/linked_mortality")
MORT = [
    ("1999-2000", "NHANES_1999_2000_MORT_2019_PUBLIC.dat"),
    ("2001-2002", "NHANES_2001_2002_MORT_2019_PUBLIC.dat"),
    ("2003-2004", "NHANES_2003_2004_MORT_2019_PUBLIC.dat"),
]

# CDC's edge rejects requests that do not look like a browser, and a bare
# urllib User-Agent is the usual reason a fetch returns markup instead of data.
UA = {
    "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://wwwn.cdc.gov/nchs/nhanes/",
}


def _get(url, timeout=120, retries=3):
    """Fetch a URL, retrying on transient failures. Returns bytes or None."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None          # wrong candidate name, not a transient error
            print(f"      HTTP {e.code} on {url}")
        except Exception as e:
            print(f"      {type(e).__name__}: {e}")
        if attempt < retries - 1:
            time.sleep(2 ** attempt)
    return None


def is_xport(data):
    """True only for a genuine SAS XPORT v5 file.

    Size alone is not evidence. When CDC declines to serve a file it returns an
    HTML interstitial that is comfortably larger than any size threshold, and
    every such page is byte-identical - which is how a first run 'downloaded'
    38 files that shared one SHA-256. An XPORT file always opens with the
    library header record, so check that instead.
    """
    return data is not None and data[:60].startswith(
        b"HEADER RECORD*******LIBRARY HEADER RECORD")


def is_mort(data):
    """True for a linked-mortality fixed-width record file (ASCII, no markup)."""
    if data is None or len(data) < 1000:
        return False
    head = data[:200].lstrip()
    if head[:1] in (b"<", b"{"):
        return False
    return all(c in b"0123456789 .-\r\n" for c in data[:200])


def fetch_xpt(cycle, suffix, year, candidates, logical, manifest):
    dest = os.path.join(OUT, cycle, f"{logical}.XPT")
    if os.path.exists(dest) and os.path.getsize(dest) > 1000:
        print(f"   skip  {logical:6s} already present")
        return True

    # A candidate that already carries this cycle's suffix is used verbatim;
    # otherwise the suffix is appended. Order is preserved, duplicates dropped.
    names = []
    for cand in candidates:
        n = cand if (suffix and cand.endswith(suffix)) else f"{cand}{suffix}"
        if n not in names:
            names.append(n)

    for fname in names:
        for pattern in URL_PATTERNS:
            url = pattern.format(cycle=cycle, year=year, fname=fname)
            data = _get(url)
            if data is None:
                continue
            if not is_xport(data):
                print(f"      not XPORT ({len(data)} B, starts "
                      f"{data[:24]!r}) - {url}")
                continue
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as f:
                f.write(data)
            sha = hashlib.sha256(data).hexdigest()
            manifest.append({
                "cycle": cycle, "logical": logical, "source_name": fname,
                "url": url, "bytes": len(data), "sha256": sha,
            })
            print(f"   ok    {logical:6s} <- {fname}.XPT  "
                  f"({len(data)/1e6:.1f} MB)  {sha[:12]}")
            return True
    return False


def fetch_mortality(cycle, fname, manifest):
    dest = os.path.join(OUT, cycle, "MORT.dat")
    if os.path.exists(dest) and os.path.getsize(dest) > 1000:
        print(f"   skip  MORT   already present")
        return True
    url = f"{MORT_BASE}/{fname}"
    data = _get(url)
    if not is_mort(data):
        if data is not None:
            print(f"      not a mortality file ({len(data)} B, starts "
                  f"{data[:24]!r})")
        return False
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as f:
        f.write(data)
    sha = hashlib.sha256(data).hexdigest()
    manifest.append({
        "cycle": cycle, "logical": "MORT", "source_name": fname,
        "url": url, "bytes": len(data), "sha256": sha,
    })
    print(f"   ok    MORT   <- {fname}  ({len(data)/1e6:.1f} MB)  {sha[:12]}")
    return True


def main():
    os.makedirs(OUT, exist_ok=True)
    manifest, missing_core, missing_opt = [], [], []

    for cycle, suffix, year in CYCLES:
        print(f"\n=== {cycle} ===")
        print("  core:")
        for logical, cands in CORE:
            if not fetch_xpt(cycle, suffix, year, cands, logical, manifest):
                print(f"   FAIL  {logical} - no candidate resolved: {cands}")
                missing_core.append((cycle, logical))
        print("  laboratory (Version B only):")
        for logical, cands in LAB:
            if not fetch_xpt(cycle, suffix, year, cands, logical, manifest):
                print(f"   miss  {logical}")
                missing_opt.append((cycle, logical))
        print("  linked mortality:")
        for mcycle, mname in MORT:
            if mcycle == cycle and not fetch_mortality(mcycle, mname, manifest):
                print(f"   miss  MORT")
                missing_opt.append((cycle, "MORT"))

    with open(os.path.join(OUT, "MANIFEST.json"), "w") as f:
        json.dump({"files": manifest,
                   "missing_core": missing_core,
                   "missing_optional": missing_opt}, f, indent=2)

    print("\n" + "=" * 62)
    print(f"downloaded {len(manifest)} files")
    if missing_core:
        print("MISSING CORE FILES - Version A cannot be built:")
        for c, l in missing_core:
            print(f"  {c}  {l}")
        return 1
    print("all core files present")
    if missing_opt:
        print(f"optional files missing ({len(missing_opt)}): "
              + ", ".join(f"{c}/{l}" for c, l in missing_opt))
    return 0


if __name__ == "__main__":
    sys.exit(main())
