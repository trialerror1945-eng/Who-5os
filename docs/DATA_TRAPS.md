# Data traps in NHANES 1999-2004 Lower Extremity Disease

Nine ways this analysis could have gone wrong without raising an error. Four
were documented in the study package before any data were downloaded; five
were found by checking the delivered files against their own codebooks.

Each is verified in `tools/verify_raw.py` or handled at the single point in
`src/common.py` and `src/build_cohort.py` where the relevant file is read.

## Known in advance

**1. `LEALPN` / `LEARPN` code -1.** Means "insufficient information
collected", not a count. Left numeric it reads as fewer than zero insensate
sites. 87 left feet and 73 right feet in 2003-2004. Recoded to missing.

**2. Missingness that is not at random — incompressible arteries.** Of 3,086
eligible participants in 2003-2004, ABPI is available for 2,346. The largest
single reason is `LEDSCCT2` = 58, "unable to obtain all blood pressures", for
565 people. Some of these are not technical failures: 43 had a left ankle
systolic above 255 mmHg and 45 a right. That is medial calcification — a
high-risk finding common in long-standing diabetes and kidney disease.
Discarding them as missing discards some of the sickest patients. Retained
via `noncompressible` and the `abi_abnormal` sensitivity endpoint.

**3. Absent second readings at age >=60 are protocol, not damage.**
`LEXBRP2`, `LEXLPTS2` and `LEXRPTS2` are empty for every participant aged 60
and over because the protocol measures them once. Imputing them would invent
data. The NCHS-computed means (`LEXBRPM`, `LEXLPTSM`, `LEXRPTSM`) are used.

**4. Exclusions that happened before the data existed.** Bilateral amputees
and participants over 400 lb were excluded from examination by survey
protocol and never appear. The highest-risk group is therefore absent, and
every prevalence here is a lower bound. Stated in the limitations.

## Found in the delivered files

**5. XPORT decodes numeric zero as 5.397605346934028e-79.** A SAS transport
numeric zero is an IBM hex float that pandas does not normalise. It does not
raise. It does not even change the composite endpoint, because
`5.4e-79 >= 1` is false exactly as `0 >= 1` is false. What it breaks is
every equality test: `== 0` recodes, and any tabulation of "no insensate
sites". Found as 2,269 zeros in `LEALPN` matching no expected level.
Normalised at read time for any value under 1e-30.

**6. `DID040G` / `DIQ040G` is a flag, not an age.** It takes values 1, 2, 7
and 9, meaning whether an age at diagnosis was reported. The age itself is
`DIQ040Q` (1999-2000) and `DID040Q` (2001-2004). Reading the flag as an age
places every diabetic diagnosis at age 1 and turns diabetes duration into a
near-constant fifty years — a strong, entirely artefactual predictor.

**7. Serum creatinine changes name mid-study.** `LBXSCR` in 1999-2000 and
2003-2004, `LBDSCR` in 2001-2002. A fixed name silently drops eGFR for a
third of the cohort.

**8. Incompressible-artery flags do not exist in 1999-2000.** `LEALAPNC` and
`LEARAPNC` were introduced in 2001-2002. Coding their absence as 0 asserts
that nobody in the first cycle had an incompressible artery. Recorded as
unknown.

**9. Linked mortality follow-up sits at columns 42-48.** Not where a first
reading of the layout document put it. Blanks parse to an all-missing
follow-up time, and a Cox model on all-missing time simply drops everyone.
Offsets verified against the delivered file: median follow-up 16.2 years,
3,336 deaths, 1,086 cardiovascular.

## Also handled

- **Survey weights for a pooled six-year sample.** `WTMEC4YR` x 2/3 for
  1999-2002 and `WTMEC2YR` x 1/3 for 2003-2004. Using `WTMEC2YR` throughout
  doubles the weight of the earlier cycles.
- **Diastolic zeros.** A zero diastolic is NHANES' code for an unobtainable
  Korotkoff phase 5, not a measurement. Averaging it in drags DBP down.
- **Refused and don't-know codes (7/9, 77/99, ...).** Mapping these to "no"
  via `== 1` biases every questionnaire prevalence downwards.
