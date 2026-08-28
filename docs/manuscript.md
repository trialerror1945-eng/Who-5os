# Which feet deserve the Doppler? Derivation and internal validation of a no-equipment clinical risk score to triage ankle–brachial index and monofilament testing in resource-limited primary care

**Running title:** A no-equipment triage score for lower-extremity disease

---

## Abstract

**Background.** Peripheral artery disease (PAD) and peripheral neuropathy are
the two principal pathways to foot ulceration and amputation, and both are
largely silent. The tests that detect them — a handheld Doppler and a 10 g
monofilament — are inexpensive, but examination *time* is not, and primary
care in low- and middle-income settings defaults to a crude rule: test the
patients with diabetes. We asked whether a score built only from data already
recorded at a health centre can allocate that scarce examination capacity
better than the rule clinicians already apply.

**Methods.** We derived and internally validated a points-based score in the
three National Health and Nutrition Examination Survey cycles (1999–2004) in
which the Lower Extremity Disease component was fielded — the only nationally
representative data containing both ankle–brachial index (ABI) and
monofilament testing in the same participants. Adults aged ≥40 years with at
least one valid test were eligible. The primary outcome was a composite of
PAD (ABI <0·90 in either leg) or peripheral neuropathy (≥1 insensate site on
either foot), defined a priori. Two versions were specified in advance:
Version A used nine variables requiring no laboratory or device; Version B
added HbA1c and eGFR. Missing predictors were handled by multiple imputation
with posterior draws (m=20). Models were logistic regressions with restricted
cubic splines, validated by 1000 bootstrap resamples with refitting from
scratch. The prespecified decisive endpoint was decision-curve net benefit
against the "test everyone with diabetes" heuristic. Score strata were
anchored to mortality through 31 December 2019.

**Findings.** Of 8080 eligible adults, 1813 (22·4%) had lower-extremity
disease; the survey-weighted prevalence was 16·97% (95% CI 15·89–18·05), with
PAD at 5·23% (4·67–5·79). Version A achieved an optimism-corrected AUC of
0·739 (95% CI 0·727–0·752) with a calibration slope of 0·986 and
calibration-in-the-large of 0·000. Adding laboratory tests changed the AUC by
0·001 (Version B 0·740, 0·728–0·753). A gradient-boosting benchmark on the
same predictors was *worse* (0·725). The integer score cost 0·010 of AUC
(0·729) and stratified observed risk from 5·6% to 42·3% across five bands.
The score exceeded the "test everyone with diabetes" rule at 23 of 23
threshold probabilities examined, and the "test everyone aged ≥60" rule at 23
of 23. Notably, 1402 of 1813 cases (77·3%) occurred in participants *without*
diagnosed diabetes and are therefore unreachable by the current heuristic at
any threshold. Over a median 16·2 years, cardiovascular mortality rose from
1·1 to 29·5 per 1000 person-years across score bands (adjusted HR per point
1·238, 95% CI 1·197–1·280).

**Interpretation.** A nine-variable score requiring no device, no laboratory
and under three minutes outperforms the triage rules currently used in
practice, and identifies a large population of undiagnosed disease that a
diabetes-based rule cannot reach by construction. One prespecified target was
not met: achieving ≥0·85 sensitivity requires examining 65·7% of attendees,
not the ≤40% we had hoped for. We report this as found. The score reorders a
queue well; it does not shorten it as much as we intended.

**Funding.** None.

---

## Research in context

**Evidence before this study.** Population data have established for two
decades that most lower-extremity disease is asymptomatic: roughly two-thirds
of US adults aged ≥40 with an ABI below 0·9 report no leg symptoms, and
prevalence of lower-extremity disease approaches 30% among adults with
diagnosed diabetes. Several models predict PAD from clinical variables, and
the US Preventive Services Task Force concluded in 2018 that evidence is
insufficient to recommend ABI screening in asymptomatic adults. What has not
been reported is a model that (i) restricts itself to variables already
recorded at health-centre level, (ii) targets an objectively measured
*composite* of ABI and monofilament findings rather than either alone, and
(iii) is tested explicitly against the heuristic clinicians actually use.

**Added value of this study.** We derive such a score and subject it to the
third test directly. It is the third element that matters: a triage tool must
beat current practice, not the strawmen of "test everyone" and "test no one"
that decision-curve analyses usually plot. The score does beat it, across the
entire practical threshold range, and the reason is quantified: more than
three-quarters of prevalent disease sits outside diagnosed diabetes. We also
report two negative findings that the literature under-reports — a laboratory
adds essentially nothing (ΔAUC 0·001), and gradient boosting is worse than
penalised logistic regression on the same variables.

**Implications of all the available evidence.** Where examination capacity is
rationed, the ordering of that queue is a clinical decision that currently
has no evidence behind it. This score provides one, on a single printed page,
computable without equipment. It should be externally validated in the
setting it is designed for before deployment; the USPSTF position on
population screening is not in tension with it, because the question here is
allocation among attendees rather than whether to screen a population.

---

## 1. Introduction

Peripheral artery disease and peripheral neuropathy converge on the same
endpoint. Amputation is rarely the product of ischaemia or sensory loss
alone; it is usually both, arriving together in a foot whose owner felt
nothing wrong until an ulcer appeared. Both conditions are detectable early
and cheaply — an ABI needs a handheld Doppler, a neuropathy screen needs a
10 g monofilament — and both are, in most of the world, not looked for.

The reason is not the price of the instruments. A monofilament costs less
than a stethoscope. The constraint is examination time: a properly performed
ABI requires the patient supine and rested, with pressures taken at several
sites, and a clinic seeing sixty patients in a morning cannot do that for
everyone. Faced with the arithmetic, practice has settled on a heuristic that
is defensible, widely taught, and — as we show — badly calibrated to where
the disease actually is: examine the patients with diabetes, and let the rest
go.

Symptom-driven case finding fails for a structural reason. In nationally
representative US data, about two-thirds of adults aged 40 or over with an
ABI below 0·9 report no leg symptoms at all. Waiting for a complaint is
therefore not a conservative strategy but a systematic one for missing most
disease.

Existing prediction models for PAD do not solve the triage problem. They
typically require variables a health centre does not hold, target PAD alone
rather than the composite that actually drives foot outcomes, and — the
decisive omission — are evaluated against "treat all" and "treat none"
reference strategies rather than against the rule a clinician would otherwise
have used. A model that beats "test everyone" is not thereby useful; a model
that cannot beat "test everyone with diabetes" is not useful at all.

We therefore set out to derive a score usable at the point of first contact,
validate it against an objectively measured composite endpoint, and test it
explicitly against the two heuristics in current use. We committed in advance
to reporting the result of that test in either direction.

## 2. Methods

### 2.1 Study design and data source

We analysed the National Health and Nutrition Examination Survey (NHANES)
cycles 1999–2000, 2001–2002 and 2003–2004. These are the only three cycles in
which the Lower Extremity Disease component was fielded, and therefore the
only nationally representative data in which ABI and monofilament testing were
performed on the same participants. The component comprises an ABPI section
and a peripheral neuropathy section (files `LEXAB`/`LEXABPI` and `LEXPN`).
ABPI values are computed and verified by the National Center for Health
Statistics before release and were not recomputed here.

Systolic pressure was measured at the right brachial artery (left if the right
was unusable) and at both posterior tibial arteries with a Doppler probe after
supine rest; participants aged 40–59 were measured twice at each site and
those aged ≥60 once, per protocol. Neuropathy was assessed with a 5·07
Semmes-Weinstein (10 g) monofilament at three sites on each foot using a
two-interval forced-choice method.

Data were retrieved programmatically and gated by a verification step that
reproduces the published 2003–2004 codebook frequencies exactly — all levels
of `LEALPN` and `LEARPN` including the −1 code, and both ABPI
present/missing splits — before any analysis was permitted to run. Nine
distinct silent-failure modes were identified and handled; they are
enumerated in `docs/DATA_TRAPS.md` and summarised in §2.10.

### 2.2 Participants

Adults aged ≥40 years with at least one valid ABI or monofilament result were
eligible. We excluded participants with prevalent amputation or an active
foot lesion, who are referred irrespective of any score. Bilateral amputees
and participants weighing over 400 lb were excluded from examination by
survey protocol and never enter the data; this is addressed in the
limitations.

### 2.3 Outcomes

The primary outcome was a composite of PAD (ABI <0·90 in either leg) or
peripheral neuropathy (≥1 insensate site on either foot). Both thresholds and
the neuropathy definition were fixed before the data were examined.

A composite was chosen for three reasons, stated in advance so that it is not
read as endpoint manipulation. **Clinically**, the action taken by a general
practitioner is the same for either finding: a foot-care programme, footwear
advice, scheduled review, referral if needed. **Statistically**, PAD alone
yields roughly 5–6% prevalence and correspondingly wide confidence intervals.
**For honest reporting**, each component is nevertheless analysed separately
as a secondary endpoint, because a reader is entitled to know whether the
score is in truth only good for neuropathy.

Secondary endpoints were PAD alone, neuropathy alone, the high-risk foot
(both present), and abnormal ABI including incompressible arteries (<0·90 or
>1·40). Alternative neuropathy definitions (≥2 insensate sites; ≥1 site on
*both* feet) were prespecified as sensitivity analyses.

### 2.4 Predictors

Version A comprised nine terms available without any device or laboratory:
age, sex, waist circumference, mean systolic blood pressure, current smoking,
former smoking, diabetes duration category (none / <5 / 5–10 / >10 years),
antihypertensive treatment, and known cardiovascular disease. Version B added
HbA1c and eGFR (CKD-EPI 2021, race-free, with 1999–2000 creatinine calibrated
to the later assay).

Three protocol deviations, all decided on collinearity diagnostics rather
than on the outcome, are recorded in `docs/TRIPOD-AI-checklist.md`: binary
diabetes status was dropped as an exact function of diabetes duration
(r=0·90); body-mass index was dropped in favour of waist circumference
(r=0·86, and BMI took an implausible negative sign in the joint model); and
glycaemia entered Version B as HbA1c rather than fasting glucose, which is
measured only in NHANES' fasting subsample and is missing for 52% of this
cohort by design.

### 2.5 Sample size

We did not fix a sample size; the available data are the three cycles that
exist. With 1813 events, 8080 participants and 13 estimated parameters, the
events-per-parameter ratio is 139 and the criteria of Riley et al. are met
with a wide margin. Sample size was therefore not a binding constraint, and
we report it for completeness rather than as a justification.

### 2.6 Missing data

Predictor missingness was low (≤6·3% for all Version A terms). We used
multiple imputation by chained equations with draws from the posterior
predictive distribution (m=20, 10 iterations), including the outcome as a
predictor in the imputation model. The outcome itself was never imputed.
Estimates were pooled by Rubin's rules; predictions were pooled on the
linear-predictor scale.

### 2.7 Model development

Models were logistic regressions with restricted cubic splines (four knots at
the 5th, 35th, 65th and 95th centiles) on age and systolic pressure. An
L1-penalised path with cross-validated penalty was fitted and reported; it
shrank no term to zero in either version, which is expected at 139 events per
parameter, and we therefore retained all prespecified terms rather than
letting a selection step act where it had nothing to do.

A gradient-boosting classifier on the same predictors was fitted as a
methodological benchmark, with the result to be reported whichever way it
fell.

The points table was derived from a *separate, all-linear* model. Spline
basis coefficients are not quantities a clinician can read off a patient, and
rounding them would produce a table whose arithmetic no longer corresponds to
the validated model. Points follow the Sullivan method with B set so that
five years of age is worth one point, awarded for distance from an explicit
reference value. The resulting integer score was then validated in its own
right.

### 2.8 Performance

Discrimination was summarised by the AUC, corrected for optimism by 1000
bootstrap resamples in which the entire model was refitted from scratch and
scored on the original sample. Calibration was assessed by the bootstrap
calibration slope, calibration-in-the-large (the intercept of a model
carrying the linear predictor as a fixed offset), a decile calibration plot
and the Brier score. The uniform shrinkage factor is the bootstrap slope.

Decision-curve analysis compared the score against four strategies: test
everyone, test no one, **test everyone with diabetes**, and **test everyone
aged ≥60**. The last two are the rules in actual use and constitute the real
test. The operating threshold was chosen as the lowest examination burden
achieving sensitivity ≥0·85, with burden and number needed to test reported.

### 2.9 Subgroups

Performance was examined by diabetes status, sex, age band and obesity. The
non-diabetic subgroup is the one that matters: it is where a score can add
anything to current practice.

### 2.10 Prevalence, weighting and software

Individual-level prediction was modelled unweighted, since the target is a
prediction for a person rather than an estimate for a population. Prevalence
and population-level examination burden are reported *with* six-year MEC
weights (WTMEC4YR × 2/3 for 1999–2002, WTMEC2YR × 1/3 for 2003–2004), strata
and PSU, with Taylor-linearised standard errors.

Analyses used Python 3.11 with pandas, NumPy, scikit-learn and statsmodels.
All code, the verification gate and the fetch pipeline are in the repository.

### 2.11 Prognostic anchor

Participants were linked to the public-use linked mortality file with
follow-up to 31 December 2019. Cox models estimated all-cause and
cardiovascular mortality by score, unadjusted and adjusted for age and sex,
the latter to establish that any gradient is not age reappearing under
another name.

## 3. Results

### 3.1 Participants

Of 31 126 participants across three cycles, 9970 were aged ≥40. Of these,
8193 had at least one valid lower-extremity test; 23 were excluded for
prevalent amputation and 90 for an active foot lesion, leaving **8080**.
Baseline characteristics appear in Table 1.

1813 participants (22·4%) met the composite endpoint: 586 had PAD, 1381 had
neuropathy, and 154 had both. Survey-weighted prevalence was 16·97% (95% CI
15·89–18·05) for the composite, 5·23% (4·67–5·79) for PAD, 13·32%
(12·32–14·32) for neuropathy and 1·20% (0·94–1·46) for the high-risk foot.
The weighted PAD estimate is consistent with published NHANES estimates,
which supports the cohort construction.

### 3.2 Model performance

Version A achieved an apparent AUC of 0·742, a 10-fold cross-validated AUC of
0·739, and an optimism-corrected AUC of **0·739 (95% CI 0·727–0·752)**.
Optimism was 0·0024. The calibration slope was 0·986 and
calibration-in-the-large 0·000; the Brier score was 0·151.

Version B, adding HbA1c and eGFR, gave an optimism-corrected AUC of 0·740
(0·728–0·753) — a difference of 0·001. **A laboratory adds nothing of
consequence to this score.** Gradient boosting on the same predictors gave a
cross-validated AUC of 0·725, *below* the spline logistic model by 0·014.

The integer points score (Table 2) achieved an AUC of 0·729, a cost of 0·010
relative to the continuous model, and ranges from 0 to 18. Observed risk by
band: ≤4, 5·6%; 5–6, 9·5%; 7–8, 15·2%; 9–10, 24·9%; ≥11, 42·3%.

### 3.3 Thresholds and examination burden

At a threshold of 0·125 the score reaches sensitivity 0·88 with specificity
0·41, requiring examination of 65·7% of attendees, with a number needed to
test of 3·3. At 0·225 the burden falls to 40·0% at sensitivity 0·68 (NNT
2·6). Full results are in Table 3.

The prespecified target of ≤40% burden *at* sensitivity ≥0·85 was **not
met**. There is no threshold at which both hold. This is reported as found.

### 3.4 Decision curve: the decisive comparison

The score's net benefit exceeded "test everyone with diabetes" at **23 of 23**
threshold probabilities from 0·05 to 0·60, and exceeded "test everyone aged
≥60" at **23 of 23** (Figure 4). At a threshold of 0·20, net benefit was
0·0914 for the score against 0·0283 for the diabetes rule and 0·0817 for the
age rule. The prespecified decisive KPI is met.

The mechanism is straightforward: **1402 of 1813 cases (77·3%) occurred in
participants without diagnosed diabetes.** No diabetes-based rule can reach
them at any threshold.

### 3.5 Secondary endpoints and sensitivity analyses

The score performed *better* for PAD alone (AUC 0·791) than for the composite,
and best for the high-risk foot with both conditions present (0·831).
Neuropathy alone gave 0·727. Abnormal ABI including incompressible arteries
gave 0·766. Alternative neuropathy definitions changed little: ≥2 insensate
sites 0·740, ≥1 site on both feet 0·735. The score is therefore not an
artefact of one endpoint definition, and it is not merely a neuropathy
detector.

### 3.6 Subgroups

AUC was 0·734 in participants without diabetes and 0·690 in those with it —
the expected direction, since within a diabetic population much of the
score's information is already spent. It was 0·732 in women and 0·734 in men;
0·660 at ages 40–59 and 0·677 at ≥60; 0·711 in obese and 0·753 in non-obese
participants. Performance within age bands is lower than overall because age
carries much of the discrimination.

### 3.7 Prognostic anchor

Among 8067 linked participants followed a median 16·2 years there were 3335
deaths, 1085 cardiovascular. All-cause mortality rose from 4·1 to 80·6 per
1000 person-years across score bands, and cardiovascular mortality from 1·1
to 29·5 (Figure 5). The hazard ratio per point was 1·400 (95% CI 1·383–1·416)
for all-cause and 1·477 (1·445–1·509) for cardiovascular mortality; adjusted
for age and sex these were 1·182 (1·159–1·206) and 1·238 (1·197–1·280).
Measured lower-extremity disease itself carried an unadjusted hazard ratio
of 2·712 (2·526–2·912) for all-cause and 3·532 (3·129–3·986) for
cardiovascular death.

The score is therefore not only predicting the result of a test today; it is
marking people at materially higher risk of dying, and of dying of vascular
causes.

## 4. Discussion

A nine-item score, computable in under three minutes with no device and no
laboratory, discriminates undiagnosed lower-extremity disease with an
optimism-corrected AUC of 0·739 and — the finding we consider decisive —
delivers greater net benefit than the two triage rules currently used in
practice across the entire practical threshold range.

The size of the gap is explained by a single number. More than three-quarters
of prevalent lower-extremity disease in this cohort occurred in people
*without* diagnosed diabetes. A rule keyed to diabetes cannot find them, at
any threshold, however diligently applied. This is not a criticism of
clinicians; it is a property of the epidemiology that a heuristic developed
around diabetic foot programmes was never designed to accommodate.

Two negative results deserve emphasis because the literature systematically
under-reports them. First, **adding laboratory tests was worth 0·001 of AUC.**
Where a health centre must choose between a phlebotomy pathway and a tape
measure, our data support the tape measure. Second, **gradient boosting was
worse than penalised logistic regression** on identical inputs (0·725 versus
0·739). With 1813 events and nine well-understood predictors, there is little
non-linear structure for a flexible learner to find, and it pays a variance
cost for looking. We report this because the alternative — quietly omitting
the benchmark that disappointed — is how the impression arises that flexible
methods always win.

**The target we missed matters.** We had hoped to reach 85% sensitivity while
examining no more than 40% of attendees. That combination does not exist in
these data: 85% sensitivity costs a 65·7% examination burden. A clinic
willing to examine two-thirds of its attendees does not have much of a
capacity problem to begin with. The honest reading is that the score reorders
the queue well but does not shorten it as much as we wanted, and a service
adopting it must choose its own point on that trade-off — perhaps 40% burden
at 68% sensitivity — rather than inherit ours. We report the full threshold
table (Table 3) precisely so that this choice is made locally and explicitly.

The USPSTF concluded in 2018 that evidence is insufficient to recommend ABI
screening in asymptomatic adults, and we anticipate the objection directly.
That determination concerns whether to screen a general population in a
setting where the alternative is doing nothing. Our question is different:
given a clinic that will examine *some* patients today, which ones? Allocating
scarce capacity is not the same decision as creating a screening programme,
and the neuropathy component in particular rests on a firmer guideline footing
through established diabetic foot-care pathways.

**Limitations.** The data are from 1999–2004 and from the United States. The
risk-factor profile is arguably closer to that of contemporary
middle-income populations than to that of the contemporary US, but this is an
argument, not evidence, and external validation in the intended setting is
required before deployment. Second, participants with bilateral amputation or
weighing over 400 lb were excluded from examination by survey protocol: the
highest-risk group is absent, and every prevalence here is a lower bound.
Third, this is internal validation only; the optimism correction was small
(0·0024) and the calibration slope near unity, but a bootstrap cannot
substitute for a new population. Fourth, ABI was unobtainable in a
non-random subset, some of whom had incompressible arteries — a high-risk
finding rather than a technical failure; we addressed this with the abnormal-
ABI sensitivity endpoint (AUC 0·766) but cannot fully repair it. Fifth, the
public-use linked mortality file is perturbed to reduce re-identification
risk, so very small subgroup mortality estimates should not be read closely.

**Implications.** The deliverable is a one-page table and an offline
calculator, not a model that needs a server. Where examination capacity is
rationed — which is most of the world — the order of the queue is currently
decided by a rule with no evidence behind it. This provides one.

## 5. Declarations

**Data availability.** All data are public NHANES files. The fetch pipeline,
the SHA-256 manifest of every file used, and the verification gate that
reproduces the published codebook frequencies are in the repository.

**Code availability.** All analysis code is in the repository under `src/`.

**Ethics.** NHANES is de-identified public data; secondary analysis requires
no new ethical approval beyond compliance with the NCHS data user agreement.
Prospective external validation would require institutional approval.

**Funding.** None.

**Conflicts of interest.** None declared.

**Patient and public involvement.** None; this is a secondary analysis of
existing survey data.

## 6. References

1. Collins GS, Moons KGM, Dhiman P, et al. TRIPOD+AI statement: updated
   guidance for reporting clinical prediction models that use regression or
   machine learning methods. *BMJ* 2024;385:e078378.
2. Selvin E, Erlinger TP. Prevalence of and risk factors for peripheral
   arterial disease in the United States: results from the National Health
   and Nutrition Examination Survey, 1999–2000. *Circulation*
   2004;110:738–43.
3. Gregg EW, Sorlie P, Paulose-Ram R, et al. Prevalence of lower-extremity
   disease in the US adult population ≥40 years of age with and without
   diabetes: 1999–2000 National Health and Nutrition Examination Survey.
   *Diabetes Care* 2004;27:1591–7.
4. US Preventive Services Task Force. Screening for peripheral artery disease
   and cardiovascular disease risk assessment with the ankle-brachial index:
   US Preventive Services Task Force recommendation statement. *JAMA*
   2018;320:177–83.
5. Riley RD, Snell KI, Ensor J, et al. Minimum sample size for developing a
   multivariable prediction model: part II — binary and time-to-event
   outcomes. *Stat Med* 2019;38:1276–96.
6. Vickers AJ, Elkin EB. Decision curve analysis: a novel method for
   evaluating prediction models. *Med Decis Making* 2006;26:565–74.
7. Sullivan LM, Massaro JM, D'Agostino RB Sr. Presentation of multivariate
   data for clinical use: the Framingham Study risk score functions. *Stat
   Med* 2004;23:1631–60.
8. Steyerberg EW, Harrell FE Jr, Borsboom GJ, et al. Internal validation of
   predictive models: efficiency of some procedures for logistic regression
   analysis. *J Clin Epidemiol* 2001;54:774–81.
9. van Buuren S, Groothuis-Oudshoorn K. mice: multivariate imputation by
   chained equations in R. *J Stat Softw* 2011;45:1–67.
10. Harrell FE Jr. *Regression Modeling Strategies*. 2nd ed. Springer, 2015.
11. Inker LA, Eneanya ND, Coresh J, et al. New creatinine- and cystatin
    C-based equations to estimate GFR without race. *N Engl J Med*
    2021;385:1737–49.
12. National Center for Health Statistics. NHANES 1999–2004 Lower Extremity
    Disease documentation, codebooks and frequencies (LEXAB, LEXPN).

---

## Table 1. Baseline characteristics by lower-extremity disease status

| Characteristic | LED present (n=1813) | LED absent (n=6267) |
|---|---|---|
| **Mean (SD)** | | |
| Age, years | 68.4 (12.4) | 58.7 (12.7) |
| Waist circumference, cm | 102.1 (14.0) | 98.6 (14.1) |
| Body-mass index, kg/m² | 28.7 (5.8) | 28.6 (5.9) |
| Systolic blood pressure, mmHg | 138.9 (23.4) | 131.7 (21.2) |
| Diastolic blood pressure, mmHg | 70.0 (13.8) | 73.6 (11.9) |
| HbA1c, % | 6.06 (1.34) | 5.73 (1.08) |
| eGFR, mL/min/1·73m² | 76.2 (22.1) | 86.6 (18.9) |
| Triage score (Version A) | 10.3 (2.9) | 7.7 (3.1) |
| **n (%)** | | |
| Women | 753 (41.5%) | 3280 (52.3%) |
| Age ≥60 years | 1400 (77.2%) | 2958 (47.2%) |
| Current smoker | 319 (17.6%) | 1201 (19.2%) |
| Former smoker | 726 (40.0%) | 2057 (32.8%) |
| Diagnosed diabetes | 409 (22.6%) | 721 (11.5%) |
| Diabetes >10 years | 198 (10.9%) | 255 (4.1%) |
| History of hypertension | 983 (54.2%) | 2498 (39.9%) |
| On antihypertensive treatment | 817 (45.1%) | 1905 (30.4%) |
| Known cardiovascular disease | 481 (26.5%) | 732 (11.7%) |
| Died by 31 Dec 2019 | 1205 (66.5%) | 2131 (34.0%) |

## Table 2. Version A points table

Score = 2 + sum of points. Range 0–18.

| Variable | Points | Awarded per | From reference |
|---|---|---|---|
| Age | +2 | 10 unit | 40 |
| Current smoker | +2 | present | — |
| Waist circumference | +1 | 15 unit | 70 |
| Diabetes duration category | +1 | present | — |
| Female sex | -1 | present | — |
| Known CVD | +1 | present | — |
| Systolic blood pressure | +0 | 20 unit | 110 |
| Former smoker | +0 | present | — |
| On antihypertensive | +0 | present | — |

| Score band | n | Cases | Observed risk |
|---|---|---|---|
| <=4 | 1117 | 63 | 5.6% |
| 5-6 | 1430 | 136 | 9.5% |
| 7-8 | 1613 | 245 | 15.2% |
| 9-10 | 1666 | 415 | 24.9% |
| >=11 | 2254 | 954 | 42.3% |

## Table 3. Performance across examination thresholds (Version A)

| Threshold | Sensitivity | Specificity | PPV | NPV | % examined | NNT |
|---|---|---|---|---|---|---|
| 0.100 | 0.93 | 0.29 | 0.27 | 0.93 | 75.9% | 3.6 |
| 0.125 | 0.88 | 0.41 | 0.30 | 0.92 | 65.7% | 3.3 |
| 0.150 | 0.82 | 0.49 | 0.32 | 0.91 | 57.7% | 3.1 |
| 0.175 | 0.78 | 0.56 | 0.34 | 0.90 | 51.4% | 2.9 |
| 0.200 | 0.73 | 0.63 | 0.36 | 0.89 | 45.2% | 2.8 |
| 0.225 | 0.68 | 0.68 | 0.38 | 0.88 | 40.0% | 2.6 |
| 0.250 | 0.63 | 0.73 | 0.40 | 0.87 | 35.4% | 2.5 |
| 0.300 | 0.53 | 0.80 | 0.43 | 0.85 | 27.5% | 2.3 |
| 0.350 | 0.44 | 0.86 | 0.48 | 0.84 | 20.6% | 2.1 |
| 0.400 | 0.34 | 0.90 | 0.50 | 0.82 | 15.1% | 2.0 |
| 0.500 | 0.17 | 0.96 | 0.55 | 0.80 | 6.9% | 1.8 |

*Bold row in practice:* threshold 0·125 is the lowest-burden point reaching sensitivity ≥0·85 (0·88), at a cost of examining 65·7% of attendees.

