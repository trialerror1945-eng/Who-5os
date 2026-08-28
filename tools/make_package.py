#!/usr/bin/env python3
"""
make_package.py - build the single self-contained archive of the study.

    python3 tools/make_package.py

Everything needed to re-run, re-check or continue the analysis elsewhere: the
typeset manuscript, every figure, the analysis-ready cohort, all result files,
all code, and the raw NHANES transport files with their SHA-256 manifest.

The raw files are included despite their bulk because they compress about
sevenfold - a .XPT is mostly padding - and because a package that cannot
reproduce its own numbers from source is not a backing dataset.
"""

import hashlib
import os
import shutil
import sys
import zipfile
from datetime import date

ROOT = "Who5os_LED_triage_package"
OUT = f"{ROOT}.zip"

LAYOUT = [
    # (source, destination inside the archive)
    ("docs/manuscript.pdf",              "manuscript/manuscript.pdf"),
    ("docs/manuscript.md",               "manuscript/manuscript.md"),
    ("docs/COMPETITIVE_LANDSCAPE.md",    "manuscript/COMPETITIVE_LANDSCAPE.md"),
    ("docs/TRIPOD-AI-checklist.md",      "manuscript/TRIPOD-AI-checklist.md"),
    ("docs/DATA_TRAPS.md",               "manuscript/DATA_TRAPS.md"),
    ("docs/calculator.html",             "calculator/calculator.html"),
]

FIGURES = ["fig1_capacity.png", "fig2_roc.png", "fig3_calibration.png",
           "fig4_dca.png", "fig5_survival.png"]

RESULT_FILES = [
    "cohort.csv", "scores.csv", "summary.json",
    "threshold_table.csv", "points_A.csv", "points_B.csv",
    "score_bands.csv", "capacity_yield.csv",
    "results.txt", "flow.txt", "mortality.txt", "capacity.txt",
    "asymptomatic.txt", "comparison_zhang2016.txt",
]

CODE_DIRS = ["src", "tools"]


def add(zf, src, dest):
    if not os.path.exists(src):
        print(f"  MISSING {src}")
        return 0
    zf.write(src, os.path.join(ROOT, dest))
    return os.path.getsize(src)


def main():
    if os.path.exists(OUT):
        os.remove(OUT)
    total = 0
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for src, dest in LAYOUT:
            total += add(zf, src, dest)
        for f in FIGURES:
            total += add(zf, os.path.join("results", f), f"figures/{f}")
        for f in RESULT_FILES:
            total += add(zf, os.path.join("results", f), f"analysis_data/{f}")
        for d in CODE_DIRS:
            for fn in sorted(os.listdir(d)):
                if fn.endswith(".py"):
                    total += add(zf, os.path.join(d, fn), f"code/{d}/{fn}")
        add(zf, ".github/workflows/fetch-nhanes.yml",
            "code/fetch-nhanes-workflow.yml")

        # Raw NHANES, with the manifest that ties each file to its source URL.
        add(zf, "data/raw/MANIFEST.json", "raw_nhanes/MANIFEST.json")
        for cyc in sorted(os.listdir("data/raw")):
            cdir = os.path.join("data/raw", cyc)
            if not os.path.isdir(cdir):
                continue
            for fn in sorted(os.listdir(cdir)):
                total += add(zf, os.path.join(cdir, fn),
                             f"raw_nhanes/{cyc}/{fn}")

        zf.writestr(os.path.join(ROOT, "README.md"), readme())

    size = os.path.getsize(OUT)
    sha = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
    print(f"Wrote {OUT}")
    print(f"  uncompressed {total / 1e6:.1f} MB -> archive {size / 1e6:.1f} MB")
    print(f"  sha256 {sha}")
    with zipfile.ZipFile(OUT) as zf:
        print(f"  {len(zf.namelist())} files")
    return 0


def readme():
    return f"""# Which feet deserve the Doppler? - complete study package

Built {date.today().isoformat()}. Everything needed to read, re-check or
continue this analysis in a fresh session.

## Start here

`manuscript/manuscript.pdf` - the paper, 18 pages, figures and tables inline.
`manuscript/COMPETITIVE_LANDSCAPE.md` - how this sits against the 24 published
PAD models, including the claims that must NOT be made.

## What the study found

A nine-item score needing no device and no laboratory, derived in NHANES
1999-2004 (n=8080, 1813 composite events).

- Optimism-corrected AUC 0.739 (95% CI 0.727-0.752), calibration slope 0.986
- **Under a 20% examination ceiling it finds 636 cases against 428 for the
  "test everyone with diabetes" rule - 208 more from the same 1373
  examinations. That rule needs double the capacity to catch up.**
- The leg-symptom item has an AUC of 0.506. 88.1% of cases report no leg pain.
- A refitted published model (Zhang 2016) also beats the diabetes rule, so the
  finding is about risk-based triage generally, not about this score.
- Adding laboratory tests moves the AUC by 0.001. Gradient boosting is worse.
- One prespecified target was missed: 85% sensitivity costs a 65.7% burden.

## Layout

```
manuscript/        paper (PDF + markdown source), reporting checklist,
                   competitive landscape, the nine data traps
figures/           Figures 1-5 as PNG
analysis_data/     cohort.csv is the analysis-ready dataset (8080 rows);
                   scores.csv holds per-participant scores; the .txt files
                   are the verbatim console output of each analysis
code/src/          the pipeline, in run order
code/tools/        fetcher, verification gate, PDF and package builders
raw_nhanes/        the .XPT and mortality files, with SHA-256 manifest
calculator/        offline scoring card, opens in any browser
```

## To reproduce from raw

```bash
pip install pandas numpy scikit-learn scipy matplotlib statsmodels
python3 code/tools/verify_raw.py     # must pass before anything else
python3 code/src/build_cohort.py
python3 code/src/analyze.py --m 20 --boot 1000
python3 code/src/mortality.py
python3 code/src/capacity.py
python3 code/src/asymptomatic.py
python3 code/src/compare_zhang.py
```

Paths assume `raw_nhanes/` is moved to `data/raw/` and the scripts are run
from the package root.

## Two things to carry forward

**The data has nine silent failure modes.** Four were documented in advance;
five were found only by checking the delivered files against their own
codebooks. The worst: `DID040G` is a 1/2/7/9 flag for *whether* an age at
diabetes diagnosis was given, not the age - read as an age it puts every
diagnosis at age 1 and makes diabetes duration a near-constant fifty years,
with nothing to signal anything went wrong. See `manuscript/DATA_TRAPS.md`.

**This is internal validation only.** External validation in the target
population is required before any clinical use.
"""


if __name__ == "__main__":
    sys.exit(main())
