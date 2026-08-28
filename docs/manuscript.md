# Which feet deserve the Doppler? A no-equipment triage score for ankle–brachial index and monofilament testing under fixed examination capacity

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
disease; survey-weighted prevalence was 16·97% (95% CI 15·89–18·05). Version A
achieved an optimism-corrected AUC of 0·739 (95% CI 0·727–0·752), calibration
slope 0·986. **Under a 20% examination ceiling the score found 636 cases
against 428 for the diabetes rule (+208, +48%); the diabetes rule required
double the capacity to match what the score found at 20%.** Efficiency was
46·3 against 31·2 cases per 100 examinations. A published NHANES PAD model
(Zhang 2016), refitted here, performed closely behind the score (607 cases at
20% capacity; AUC 0·722 on the composite, 0·790 on PAD alone against our 0·797)
and also beat the diabetes rule — risk-based triage, not this particular
score, is what separates from current practice. Leg symptoms were near-useless
for triage: 88·1% of cases reported no leg pain, and the symptom item alone had
an AUC of 0·506. Adding laboratory tests changed the AUC by 0·001; gradient
boosting was worse (0·725). Over a median 16·2 years cardiovascular mortality
rose from 1·1 to 29·5 per 1000 person-years across score bands (adjusted HR per
point 1·238, 95% CI 1·197–1·280).

**Interpretation.** Where examination capacity is rationed, the order of the
queue is a clinical decision currently made by a rule that finds barely more
disease than examining people at random. Any risk-based ordering — ours or an
existing published model — substantially outperforms it, and the case for
abandoning diabetes status as the triage rule does not rest on adopting our
particular score. One prespecified target was not met: reaching 85%
sensitivity requires examining 65·7% of attendees, not the ≤40% intended. We
report this as found.

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

**Added value of this study.** We evaluate triage the way a clinic
experiences it — under a fixed ceiling on examinations — rather than only on
discrimination or on decision-curve thresholds. Under that framing the gap
between risk-based ordering and the diabetes heuristic is large and concrete:
+208 cases at 20% capacity, with the heuristic needing double the capacity to
catch up. We also refit the closest published NHANES PAD model on the same
participants and report that it, too, beats the heuristic — a finding that
argues against current practice more broadly than it argues for our score. Two
further negatives are reported that the literature under-reports: a laboratory
adds 0·001 of AUC, and gradient boosting is worse than penalised logistic
regression on the same variables. Finally, we test the field's founding
assumption in its own data and find that asking about leg symptoms has an AUC
of 0·506.

**Implications of all the available evidence.** The actionable message is not
"use this score" but "stop using diabetes status to decide whose feet get
examined." Where a score is wanted, this one needs no device, no laboratory
and no race term, fits on one page, and carries a 16-year mortality gradient.
External validation in the intended setting is required before deployment; the
USPSTF position on population screening is not in tension with it, because the
question here is allocation among attendees rather than whether to screen.

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

### 2.9 Evaluation under a capacity ceiling

Decision-curve analysis prices a false positive against a true positive at an
exchange rate set by the threshold. A health centre does not face that trade;
it faces a ceiling set by the morning's staffing. We therefore added an
evaluation matched to the real constraint: rank every attendee by each
strategy, examine the top K%, and count what is found, for K from 5% to 50%.
The framework follows Kelly and colleagues' treatment of triage testing when
reference-test capacity is constrained.

Five strategies were ranked on identical participants: the triage score; the
Zhang 2016 published NHANES PAD model, refitted on our cohort; test everyone
with diabetes; test everyone aged ≥60; and an unordered queue. Binary rules
provide no ordering within their own group — below a capacity equal to the
number of diabetic attendees, "test everyone with diabetes" cannot say which
of them to see. Those ties are broken at random and averaged over 200 draws,
rather than resolved by any other variable, which would credit the rule with
information it does not have.

### 2.10 Symptoms

The premise that symptom-driven case finding fails is usually supported by
citation. We tested it here. A leg-symptom item (LEQ020) is carried inside the
LEXAB examination file rather than a questionnaire file, and only from
2001–2002; 3739 participants have it. We report disease prevalence by symptom
status, the operating characteristics of "examine whoever complains" as a
triage rule, and score performance restricted to those reporting no symptoms.

### 2.11 Comparison with a published model

Zhang and colleagues developed a PAD prediction model in NHANES 1999–2002 with
external validation in 2003–2004 (age, sex, race, pulse pressure, the total
cholesterol/HDL ratio, ever-smoking; C=0·82 training, 0·76 validation). Because
their data and ours overlap, we refitted their variable set on our cohort and
put both models through identical tests rather than comparing published numbers
across different samples and validation designs.

### 2.12 Subgroups

Performance was examined by diabetes status, sex, age band and obesity. The
non-diabetic subgroup is the one that matters: it is where a score can add
anything to current practice.

### 2.13 Prevalence, weighting and software

Individual-level prediction was modelled unweighted, since the target is a
prediction for a person rather than an estimate for a population. Prevalence
and population-level examination burden are reported *with* six-year MEC
weights (WTMEC4YR × 2/3 for 1999–2002, WTMEC2YR × 1/3 for 2003–2004), strata
and PSU, with Taylor-linearised standard errors.

Analyses used Python 3.11 with pandas, NumPy, scikit-learn and statsmodels.
All code, the verification gate and the fetch pipeline are in the repository.

### 2.14 Prognostic anchor

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

### 3.5 Examination under a capacity ceiling

This is the analysis matched to the constraint clinics actually face, and it
separates the strategies far more sharply than the AUC does (Figure 1, Table 4).

Among 6863 participants with both variable sets complete (1514 cases), at a 20%
examination ceiling — 1373 examinations — the triage score found **636 cases**
against **428** for the diabetes rule: **208 more cases, a 48% increase**, from
the same number of examinations. Put the other way, the diabetes rule needed
**40% capacity — double — to find what the score found at 20%.** Efficiency was
46·3 against 31·2 cases per 100 examinations.

The advantage held across the range. At 10% capacity the score found 354 cases
against 248; at 30%, 849 against 564. The age ≥60 rule was worse than the
diabetes rule below 20% capacity and better above it. An unordered queue found
331 cases at 20% — meaning **the diabetes rule outperforms random ordering by
97 cases, while the score outperforms it by 305.**

The refitted Zhang 2016 model found 607 cases at 20% capacity, close behind the
score and far ahead of both heuristics. This matters for what the paper claims:
the separation that counts clinically is between *any* risk-based ordering and
the rules in current use, not between one model and another.

### 3.6 Head-to-head with a published model

Refitted on our participants, the Zhang 2016 variable set achieved an AUC of
0·790 for PAD alone against our 0·797, and 0·722 for the composite against our
0·737. It beat the diabetes rule at 12 of 12 thresholds, as ours did, and
required a 63·1% examination burden at 85% sensitivity against our 62·3%.

We report this plainly: **on discrimination the two models are close enough
that the difference is not the point.** What separates them is what each can be
used for. Their model predicts PAD alone, and 1227 of our 1813 cases (67·7%)
were neuropathy without PAD — structurally invisible to a PAD-only endpoint at
any threshold. Their model requires a total cholesterol and HDL measurement;
ours requires none. Three of their eight terms are US race/ethnicity categories
(Black OR 2·37; "Other" OR 0·12, 95% CI 0·03–0·54, estimated on 119 people),
which have no counterpart in the population this score is designed for. Their
output is a logit with an intercept of −9·37; ours is an integer between 0 and
18.

### 3.7 Disease without symptoms

Among 3362 participants with the leg-symptom item and complete predictors,
**643 of 730 cases (88·1%) occurred in people reporting no leg pain.**
Prevalence was 23·7% among those reporting pain and 21·5% among those not — a
difference of 2·2 percentage points. The symptom item alone had an **AUC of
0·506**: asking the patient is a coin flip.

As a triage rule, "examine whoever complains" had a sensitivity of 0·119 and a
PPV of 0·237, examining 10·9% of attendees to find 87 of 730 cases. Examining
the same number of people by score instead found **201 cases (+131%)**.

Score discrimination was undiminished among the symptomless (AUC 0·755 against
0·740 overall) — the group a symptom-led approach cannot reach by construction.

### 3.8 Secondary endpoints and sensitivity analyses

The score performed *better* for PAD alone (AUC 0·791) than for the composite,
and best for the high-risk foot with both conditions present (0·831).
Neuropathy alone gave 0·727. Abnormal ABI including incompressible arteries
gave 0·766. Alternative neuropathy definitions changed little: ≥2 insensate
sites 0·740, ≥1 site on both feet 0·735. The score is therefore not an
artefact of one endpoint definition, and it is not merely a neuropathy
detector.

### 3.9 Subgroups

AUC was 0·734 in participants without diabetes and 0·690 in those with it —
the expected direction, since within a diabetic population much of the
score's information is already spent. It was 0·732 in women and 0·734 in men;
0·660 at ages 40–59 and 0·677 at ≥60; 0·711 in obese and 0·753 in non-obese
participants. Performance within age bands is lower than overall because age
carries much of the discrimination.

### 3.10 Prognostic anchor

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
laboratory, finds 48% more lower-extremity disease than the rule clinics
currently use, from the same number of examinations. Under a 20% capacity
ceiling that is 208 additional cases per 1373 examinations; the diabetes rule
needs double the capacity to match it.

**The finding is about triage, not about our model.** A published NHANES PAD
model refitted on the same participants found 607 cases at the same ceiling —
close behind ours, far ahead of both heuristics — and beat the diabetes rule at
every threshold, as ours did. We could have omitted that comparison. Reporting
it changes the paper's claim for the better: the evidence supports abandoning
diabetes status as the triage rule, and does not depend on adopting any
particular replacement. A clinic that prefers an existing model should use it.

The size of the gap has a simple explanation. More than three-quarters of
prevalent disease in this cohort occurred in people *without* diagnosed
diabetes. A rule keyed to diabetes cannot find them at any threshold, however
diligently applied. This is not a criticism of clinicians; it is a property of
the epidemiology that a heuristic developed inside diabetic foot programmes was
never built to accommodate. The diabetes rule is not useless — it beats random
ordering by 97 cases at 20% capacity — but it recovers only a third of what
ordering by risk recovers.

**Asking the patient does not work.** The claim that symptom-driven case
finding fails is usually supported by citation; we tested it here and the
result is starker than the citation implies. The leg-symptom item had an AUC of
0·506 — indistinguishable from chance — and 88·1% of cases occurred in people
who reported no leg pain. Prevalence differed between symptomatic and
asymptomatic attendees by 2·2 percentage points. Any workflow that waits for a
complaint, or that uses a complaint to prioritise, is close to selecting at
random. Crucially, the score's discrimination did not degrade among the
symptomless (AUC 0·755), which is precisely the group such workflows cannot
reach.

**Two negative results deserve emphasis** because the literature
under-reports them. Adding laboratory tests was worth 0·001 of AUC: where a
health centre must choose between a phlebotomy pathway and a tape measure,
these data support the tape measure. And gradient boosting was *worse* than
penalised logistic regression on identical inputs (0·725 versus 0·739). With
1813 events and nine well-understood predictors there is little non-linear
structure to find, and a flexible learner pays variance for looking. We report
this because quietly dropping the benchmark that disappointed is how the
impression arises that flexible methods always win.

**The target we missed matters.** We had hoped to reach 85% sensitivity while
examining no more than 40% of attendees. That combination does not exist in
these data: 85% sensitivity costs a 65·7% examination burden. A clinic willing
to examine two-thirds of its attendees does not have much of a capacity problem
to begin with. The honest reading is that the score reorders the queue well but
does not shorten it as much as we wanted. Table 3 and Table 4 are reported in
full so that a service picks its own point on that trade-off rather than
inheriting ours.

The USPSTF concluded in 2018 that evidence is insufficient to recommend ABI
screening in asymptomatic adults, and we anticipate the objection directly.
That determination concerns whether to screen a general population where the
alternative is doing nothing. Our question is different: given a clinic that
will examine *some* patients today, which ones? Allocating scarce capacity is
not the same decision as creating a screening programme, and the neuropathy
component rests on a firmer guideline footing through established diabetic
foot-care pathways.

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
Sixth, the symptom analysis rests on a single item available only in
2001–2004 and answered by 3739 participants; we took the variable at its
codebook name and could not retrieve the exact question wording, so it
should be read as a screening question for leg pain on walking rather
than a full Edinburgh claudication instrument. Seventh, the capacity
analysis assumes attendees present as a single batch to be ranked; a real
clinic sees them sequentially, and a prospective implementation would need
a fixed score cut-off rather than a daily ranking.

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
13. Zhang Y, Huang J, Wang P. A prediction model for the peripheral arterial
    disease using NHANES data. *Medicine* 2016;95(16):e3454.
14. Kelly SL, Ward H, Flaxman AD, et al. Evaluation of triage tests when
    existing test capacity is constrained: application to rapid diagnostic
    testing in COVID-19. *Med Decis Making* 2021;41(7):main.
15. Quan Y, et al. Diagnosis models to predict peripheral arterial disease: a
    systematic review and meta-analysis. *Sci Rep* 2025;15:26661.

---

## Figures

**Figure 1.** Cumulative gain under a capacity ceiling: share of all
lower-extremity disease found against share of attendees examined, for the
triage score, the refitted Zhang 2016 model, the two heuristics in current use,
and an unordered queue. `results/fig1_capacity.png`

**Figure 2.** Receiver operating characteristic curves, Version A, Version B
and the gradient-boosting benchmark. `results/fig2_roc.png`

**Figure 3.** Decile calibration plot. `results/fig3_calibration.png`

**Figure 4.** Decision curve against four comparator strategies.
`results/fig4_dca.png`

**Figure 5.** Kaplan–Meier survival by score band, all-cause and
cardiovascular mortality. `results/fig5_survival.png`

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


## Table 4. Cases found under a capacity ceiling

Among 6863 attendees with 1514 cases. Every strategy ranks the same
people; ties inside a binary rule are broken at random and averaged.

| Share examined | Triage score | Zhang 2016 | Diabetes rule | Age ≥60 rule | Unordered queue |
|---|---|---|---|---|---|
| **5%** | 189 (12%) | 181 (12%) | 125 (8%) | 108 (7%) | 73 (5%) |
| **10%** | 354 (23%) | 343 (23%) | 248 (16%) | 216 (14%) | 147 (10%) |
| **15%** | 502 (33%) | 482 (32%) | 359 (24%) | 323 (21%) | 241 (16%) |
| **20%** | 636 (42%) | 607 (40%) | 428 (28%) | 433 (29%) | 331 (22%) |
| **25%** | 749 (49%) | 722 (48%) | 496 (33%) | 541 (36%) | 404 (27%) |
| **30%** | 849 (56%) | 803 (53%) | 564 (37%) | 648 (43%) | 492 (32%) |
| **40%** | 1029 (68%) | 993 (66%) | 699 (46%) | 863 (57%) | 643 (42%) |
| **50%** | 1163 (77%) | 1149 (76%) | 834 (55%) | 1079 (71%) | 784 (52%) |

Cases found (share of all 1514 cases). At 20% capacity the score finds 208
more cases than the diabetes rule from the same 1373 examinations; the
diabetes rule requires 40% capacity to match the score's 20% yield.

## Table 5. Head-to-head with Zhang 2016, refitted on these participants

| | Zhang 2016 | Triage score |
|---|---|---|
| AUC, PAD alone | 0.790 | 0.797 |
| AUC, composite endpoint | 0.722 | 0.737 |
| Cases found at 20% capacity | 607 | 636 |
| Beats the diabetes rule | 12/12 thresholds | 12/12 thresholds |
| Burden at 85% sensitivity | 63.1% | 62.3% |
| Requires a laboratory | Yes (total cholesterol, HDL) | No |
| Contains US race/ethnicity terms | Yes (3 of 8 terms) | No |
| Captures neuropathy | No | Yes |
| Deployable form | logit, intercept −9.37 | integer score 0–18 |
| Mortality anchor | No | Yes (16.2 years) |

Discrimination is close. What separates the models is what each can be
used for, and 67.7% of cases here are neuropathy without PAD — invisible
to a PAD-only endpoint at any threshold.

## Table 6. Leg symptoms as a triage rule

| | Value |
|---|---|
| Participants with the symptom item | 3362 |
| Cases | 730 |
| Prevalence, reports leg pain | 23.7% (87/367) |
| Prevalence, reports no leg pain | 21.5% (643/2995) |
| Cases in people reporting no pain | 643 (88.1%) |
| AUC of the symptom item alone | **0.506** |
| Sensitivity of 'examine whoever complains' | 0.119 |
| Cases found examining 10.9% by symptoms | 87 |
| Cases found examining 10.9% by score | 201 (+131%) |
| Score AUC among the symptomless | 0.755 |

