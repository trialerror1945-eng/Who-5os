# Which feet deserve the Doppler?

A no-equipment clinical risk score that triages ankle–brachial index and
monofilament testing in resource-limited primary care.

Derived and internally validated in NHANES 1999–2004 — the only three cycles
in which the Lower Extremity Disease component was fielded, and therefore the
only nationally representative data holding both ABI and monofilament results
for the same participants.

## Headline results

| | |
|---|---|
| Cohort | 8080 adults aged ≥40 |
| Composite events | 1813 (22·4%); weighted prevalence 16·97% (95% CI 15·89–18·05) |
| AUC, optimism-corrected | **0·739** (95% CI 0·727–0·752) |
| Calibration slope | 0·986; calibration-in-the-large 0·000 |
| Integer score | 0–18, risk 5·6% → 42·3% across five bands |
| **Beats "test everyone with diabetes"** | **at 23 of 23 thresholds** |
| Cases the diabetes rule cannot reach | 1402 of 1813 (77·3%) |
| CV mortality across bands | 1·1 → 29·5 per 1000 person-years |

Three findings we did not go looking for, reported as found:

- **A laboratory adds nothing.** Version B (HbA1c + eGFR) changes the AUC by
  0·001. Where a clinic must choose between a phlebotomy pathway and a tape
  measure, these data support the tape measure.
- **Gradient boosting is worse** than penalised logistic regression on the
  same nine predictors (0·725 vs 0·739).
- **One prespecified target was missed.** Reaching 85% sensitivity requires
  examining 65·7% of attendees, not the ≤40% intended. The score reorders the
  queue well; it does not shorten it as much as we wanted.

## Layout

```
tools/fetch_nhanes.py    download from CDC (runs in CI, not here)
tools/verify_raw.py      hard gate: reproduces published codebook frequencies
src/common.py            file reading, missing-code handling, eGFR
src/modeling.py          splines, MICE, metrics, decision curves
src/build_cohort.py      cohort, endpoints, participant flow
src/analyze.py           models, validation, DCA, points tables, Figures 2–4
src/mortality.py         Cox prognostic anchor, Figure 5
src/make_calculator.py   emits the offline scoring card
docs/manuscript.md       full manuscript with tables
docs/DATA_TRAPS.md       nine silent-failure modes and how each is handled
docs/TRIPOD-AI-checklist.md
docs/calculator.html     self-contained, works offline on a phone
results/                 all outputs, figures and the SHA-256 manifest
```

## Reproducing

The raw NHANES files are committed under `data/raw/` with a SHA-256 manifest.
To rebuild everything from them:

```bash
pip install pandas numpy scikit-learn scipy matplotlib statsmodels
python3 tools/verify_raw.py          # must pass before anything else
python3 src/build_cohort.py
python3 src/analyze.py --m 20 --boot 1000
python3 src/mortality.py
python3 src/make_calculator.py
```

To re-fetch from CDC, run the **Fetch NHANES raw data** workflow. It runs on a
GitHub runner because CDC hosts are unreachable from the analysis sandbox, and
it will not commit anything that fails `verify_raw.py`.

## On trusting these numbers

`tools/verify_raw.py` reproduces the published 2003–2004 codebook frequencies
exactly — every level of `LEALPN` and `LEARPN` including the −1 code, and both
ABPI present/missing splits — before any analysis may run. It has already
earned its keep twice: it caught a first fetch in which CDC served an HTML
interstitial for all 38 files (identical SHA-256, and large enough to pass any
size check), and it surfaced the XPORT decoded-zero artefact that made 2269
genuine zeros match no expected level.

Nine distinct silent-failure modes were found and handled. Four were known in
advance; five were found only by checking the delivered files against their own
codebooks. The one most likely to have gone unnoticed: `DID040G` is a 1/2/7/9
flag for *whether* an age at diabetes diagnosis was given, not the age. Read as
an age, it places every diabetic diagnosis at age 1 and turns diabetes duration
into a near-constant fifty years — a strong and entirely artefactual predictor,
with nothing to signal that anything went wrong. See `docs/DATA_TRAPS.md`.
