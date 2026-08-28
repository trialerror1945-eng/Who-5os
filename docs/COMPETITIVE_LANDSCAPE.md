# Competitive landscape: NHANES studies on the same ground

Structured scan run before submission, as the protocol requires. Benchmark:
Quan et al., *Sci Rep* 2025 — systematic review of **24 PAD diagnostic
prediction models**, pooled AUC **0.79 (0.74–0.84)**, 2–20 predictors, most at
high risk of bias.

| Study | Data | Endpoint | Discrimination | Capacity analysis | Heuristic comparator | Symptoms tested | Points table | Mortality anchor | Needs lab |
|---|---|---|---|---|---|---|---|---|---|
| **This study** | NHANES 1999–2004 | **PAD *or* neuropathy** | 0.739 composite / 0.797 PAD | **Yes** | **Yes — diabetes, age ≥60** | **Yes** | **Yes, 0–18** | **Yes, 16.2 y** | **No** |
| Zhang 2016, *Medicine* | NHANES 1999–2002 → 2003–04 | PAD only | 0.82 train / 0.76 external | No | No | No | No | No | Yes (TC/HDL) |
| Matsushita 2019, *JAHA* | 6 US cohorts | PAD, lifetime risk | c 0.77 | No | No | No | No | n/a | Yes |
| Ann Vasc Surg 2025 | NHANES 1999–2004 | PAD only | ML, 6 models + SMOTE | No | No | No | No | No | Yes (+ diet recall) |
| Oxidative Balance Score 2025 | NHANES, n=7249 | PAD only | GLMNet + SHAP | No | No | No | No | No | Yes (+ diet) |
| BMC Med Inform 2024 | 479 diabetic inpatients | DPN and LEAD, **separately** | ML | No | No | No | No | No | Yes |
| Gregg 2004, *Diabetes Care* | NHANES 1999–2000 | LED, descriptive | n/a — prevalence paper | No | No | No | No | No | — |

## Where we are not novel

- NHANES + PAD + machine learning is crowded: at least three papers in 2025.
- Our composite AUC (0.739) is **below** the pooled 0.79 of the systematic
  review, and below Zhang's 0.82 training figure. The comparison is not
  like-for-like — they predict PAD alone, which is rarer and more separable —
  but a reviewer will make it anyway. Our PAD-alone figure is 0.791.
- **Beating the diabetes heuristic is not unique to our score.** Refitted on
  our participants, Zhang's model also beats it at 12 of 12 thresholds. Any
  claim of exclusivity here is false and must not be made.

## What survives, in order of strength

1. **Capacity-constrained evaluation.** No PAD model has been assessed under a
   fixed examination ceiling. It is also the framing that separates strategies
   most sharply: +208 cases (+48%) at 20% capacity against the diabetes rule,
   which needs double the capacity to match.
2. **Composite endpoint.** 67.7% of our cases are neuropathy without PAD —
   structurally invisible to every PAD-only model in the table above.
3. **The symptom result.** AUC 0.506 for the leg-pain item; 88.1% of cases
   symptomless. The field's founding premise, tested rather than cited.
4. **Deployability.** No laboratory, no race terms, integer score, offline
   calculator. Zhang's model carries three US race/ethnicity coefficients that
   have no counterpart in the target population.
5. **Prognostic anchor.** 16.2 years of follow-up; nobody else links a triage
   score to survival.
6. **Reported negatives.** Lab adds 0.001; gradient boosting is worse.

## Claims to avoid

- "The first score to…" — there are 24 models.
- "Our model outperforms existing models" — it does not, meaningfully.
- "Only our score beats current practice" — false.

## The claim to make

> Risk-based triage — ours or an existing published model — finds roughly half
> again as much disease as the diabetes rule from the same examination
> capacity. Diabetes status should be abandoned as the triage rule. Where a
> score is wanted, this one adds the neuropathy pathway that PAD-only models
> cannot see, needs no laboratory, and carries a 16-year mortality gradient.
