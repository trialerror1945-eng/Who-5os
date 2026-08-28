# TRIPOD+AI reporting checklist

Mapping of the 27 TRIPOD+AI items (Collins et al., *BMJ* 2024;385:e078378) to
where each is addressed. Section numbers refer to `docs/manuscript.md`.

| # | Item | Where |
|---|------|-------|
| 1 | Title identifies study as developing a prediction model, names target population and outcome | Title |
| 2 | Structured abstract | Abstract |
| 3 | Background and rationale, including existing models | Introduction ¶1–3 |
| 4 | Objectives | Introduction ¶4 |
| 5 | Data source and dates | Methods §2.1 |
| 6 | Eligibility criteria | Methods §2.2; Figure 1 |
| 7 | Outcome definition, blinded to predictors | Methods §2.3 |
| 8 | Predictors, definition and timing | Methods §2.4 |
| 9 | Sample size justification | Methods §2.5 |
| 10 | Missing data handling | Methods §2.6 |
| 11 | Analytical methods, model type and specification | Methods §2.7 |
| 12 | Model performance measures | Methods §2.8 |
| 13 | Model updating / recalibration | Not applicable (development only) |
| 14 | Class imbalance handling | Methods §2.7 — none applied; 22.4% event rate |
| 15 | Fairness / subgroup evaluation | Methods §2.9; Results §3.6 |
| 16 | Open science: funding, conflicts, protocol, data, code | Declarations |
| 17 | Patient and public involvement | Declarations |
| 18 | Participant flow | Results §3.1; Figure 1 |
| 19 | Participant characteristics | Results §3.1; Table 1 |
| 20 | Model specification, full equation and intercept | Results §3.3; Table 2; Appendix A |
| 21 | Model performance with uncertainty | Results §3.4; Table 3 |
| 22 | Model updating results | Not applicable |
| 23 | Interpretation in context | Discussion ¶1–4 |
| 24 | Limitations | Discussion ¶5–6 |
| 25 | Usability and clinical implications | Discussion ¶7; §3.5 |
| 26 | Data availability | Declarations |
| 27 | Code availability | Declarations |

## Deviations from protocol

Three, all recorded before results were interpreted:

1. **Glycaemia in Version B is HbA1c, not fasting glucose.** The protocol
   allowed either. Fasting glucose is measured only in NHANES' morning
   fasting subsample and is missing for 52% of this cohort by design; a
   fasting-glucose model would rest on imputing its main new predictor for
   half the participants. HbA1c is missing for 3%.

2. **Body-mass index dropped in favour of waist circumference.** The protocol
   specified testing the pair for redundancy and retaining one. They
   correlate at r=0.86 (VIF ~4.1), and with both present BMI took a negative
   coefficient — a suppression artefact, not protection. Reported both ways.

3. **Binary diabetes status dropped in favour of diabetes duration.**
   `dm_dur_cat == 0` holds for every non-diabetic participant and only for
   them, so the binary is an exact function of the ordinal (r=0.90). Keeping
   both left diabetes with a coefficient near zero, which misreads as
   "diabetes does not matter".
