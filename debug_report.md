# Debug Report

Generated 1 triage findings from aggregate metrics. This report prioritizes route bias, surface imbalance, and calibration signals.

## Hypotheses

### H1: Predicted CTR shows drift vs observed (mean pred_ctr - ctr = +0.0131).

- **Confidence:** medium

- **Evidence:** {'calibration_drift': 0.013051838727101006}

- **Proposed validation:** Run targeted A/B as suggested; confirm effect on route share, CTR, and value composition.


## Recommended Experiments

### Calibration adjustment A/B (temperature scaling)

Apply calibration layer to pred_ctr and/or score scaling; measure stability and downstream CTR/value proxies.

- **Success metrics:** calibration_drift, global_ctr, ctr_stability_proxy

- **Guardrails:** revenue_proxy, latency, auction_health_proxy


## Notes / Confounders

- System is noisy and landscape changes frequently; prefer short ramp, strong guardrails, and holdout-based validation.
- Aggregate metrics can hide segment-level regressions; slice by surface×route×user cohorts where possible.
- Beware of novelty effects and auction dynamics when adjusting route share/privilege.
