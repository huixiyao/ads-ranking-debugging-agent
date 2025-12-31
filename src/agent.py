from __future__ import annotations
import json
from typing import Any, Dict

from src.triage import triage
from src.report import DebugReport, Experiment, render_markdown


def build_report(metrics: Dict[str, Any], triage_out: Dict[str, Any]) -> DebugReport:
    findings = triage_out.get("findings", [])

    # Convert findings -> hypotheses (rule-based MVP)
    hypotheses = []
    for f in findings[:5]:
        hypotheses.append({
            "title": f["summary"],
            "confidence": f["severity"],
            "evidence": f["evidence"],
            "validation": "Run targeted A/B as suggested; confirm effect on route share, CTR, and value composition."
        })

    # Build a small set of experiments (dedup-ish by category)
    experiments = []
    if any("route_share_overflow" in f["key"] for f in findings):
        experiments.append(Experiment(
            name="Route cap / rebalancing at early-stage recall",
            description="Introduce route caps or adjust blending ratios to prevent overflow and recover diversity.",
            success_metrics=["global_ctr", "route_efficiency", "route_share", "diversity_proxy"],
            guardrails=["overall_revenue_proxy", "latency", "delivery_stability"]
        ))
    if any("route_eff_high" in f["key"] for f in findings):
        experiments.append(Experiment(
            name="Reduce privilege scaling for strong routes",
            description="Decrease route scaling factor (or blending weight) for routes with abnormally high efficiency; evaluate cannibalization impact.",
            success_metrics=["global_ctr", "surface_ctr", "route_share"],
            guardrails=["revenue_proxy", "advertiser_spend_stability"]
        ))
    if any("route_eff_low" in f["key"] for f in findings):
        experiments.append(Experiment(
            name="Targeted route boost for weak routes (segment-gated)",
            description="Increase share only for segments where the route has historically positive lift; avoid global boost.",
            success_metrics=["segment_ctr", "cold_start_ctr_proxy", "route_efficiency"],
            guardrails=["user_experience_proxy", "delivery_diversity"]
        ))
    if any(f["key"] == "calibration_drift" for f in findings):
        experiments.append(Experiment(
            name="Calibration adjustment A/B (temperature scaling)",
            description="Apply calibration layer to pred_ctr and/or score scaling; measure stability and downstream CTR/value proxies.",
            success_metrics=["calibration_drift", "global_ctr", "ctr_stability_proxy"],
            guardrails=["revenue_proxy", "latency", "auction_health_proxy"]
        ))

    if not experiments:
        experiments.append(Experiment(
            name="Baseline diagnostics A/B",
            description="Run a small, low-risk A/B toggling a single blending knob to validate sensitivity and establish baseline.",
            success_metrics=["global_ctr", "route_share", "route_efficiency"],
            guardrails=["revenue_proxy", "delivery_stability"]
        ))

    summary = (
        f"Generated {len(findings)} triage findings from aggregate metrics. "
        "This report prioritizes route bias, surface imbalance, and calibration signals."
    )

    notes = [
        "System is noisy and landscape changes frequently; prefer short ramp, strong guardrails, and holdout-based validation.",
        "Aggregate metrics can hide segment-level regressions; slice by surface×route×user cohorts where possible.",
        "Beware of novelty effects and auction dynamics when adjusting route share/privilege."
    ]

    return DebugReport(summary=summary, hypotheses=hypotheses, experiments=experiments, notes=notes)


def run(metrics_path: str = "../metrics_sample.json") -> Dict[str, Any]:
    with open(metrics_path, "r") as f:
        metrics = json.load(f)

    triage_out = triage(metrics)
    report = build_report(metrics, triage_out)
    return {
        "triage": triage_out,
        "report": report.to_dict(),
        "report_markdown": render_markdown(report),
    }
