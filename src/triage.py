from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Tuple


@dataclass
class Finding:
    key: str
    severity: str          # "low" | "medium" | "high"
    summary: str
    evidence: Dict[str, Any]
    hypothesis: str
    suggested_actions: List[str]


def _topk_by_abs_diff(items: List[Tuple[str, float]], k: int = 2) -> List[Tuple[str, float]]:
    return sorted(items, key=lambda x: abs(x[1]), reverse=True)[:k]


def triage(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Rule-based triage on metrics_sample.json to produce anomalies + hypotheses.
    """
    findings: List[Finding] = []

    global_ctr = metrics.get("global_ctr", None)
    route_stats = metrics.get("route_stats", {})
    surface_stats = metrics.get("surface_stats", {})
    calib = metrics.get("calibration_drift", None)

    # --- Route bias detection (efficiency & share) ---
    effs = []
    shares = []
    for route, stats in route_stats.items():
        eff = stats.get("efficiency", None)
        share = stats.get("share", None)
        if eff is not None:
            effs.append((route, float(eff)))
        if share is not None:
            shares.append((route, float(share)))

    # Flag extreme efficiencies
    for route, eff in effs:
        if eff >= 1.15:
            findings.append(Finding(
                key=f"route_eff_high:{route}",
                severity="medium" if eff < 1.3 else "high",
                summary=f"{route} route efficiency is high (eff={eff:.3f}) relative to global CTR.",
                evidence={"route": route, "efficiency": eff, "global_ctr": global_ctr, "route_stats": route_stats.get(route, {})},
                hypothesis=f"{route} may be over-privileged or over-delivering high-quality ads, potentially cannibalizing other routes.",
                suggested_actions=[
                    f"Check {route} blending ratio / privilege scaling at early-stage recall.",
                    f"Inspect {route} score distribution vs other routes (avg_pred_ctr / avg_rank_score).",
                    "Run a small A/B reducing route share or privilege to measure trade-off (CTR vs value vs diversity)."
                ]
            ))
        if eff <= 0.90:
            findings.append(Finding(
                key=f"route_eff_low:{route}",
                severity="medium" if eff > 0.8 else "high",
                summary=f"{route} route efficiency is low (eff={eff:.3f}) relative to global CTR.",
                evidence={"route": route, "efficiency": eff, "global_ctr": global_ctr, "route_stats": route_stats.get(route, {})},
                hypothesis=f"{route} may be underperforming due to weak retrieval quality or miscalibrated ranking score scaling.",
                suggested_actions=[
                    f"Check {route} candidate quality and coverage; verify retrieval constraints.",
                    f"Audit {route} score scaling and blending inputs; compare pred_ctr distribution vs click.",
                    "Try a targeted A/B increasing route share only for segments where it historically performs well."
                ]
            ))

    # Flag share imbalance (optional heuristic)
    for route, share in shares:
        if share >= 0.70:
            findings.append(Finding(
                key=f"route_share_overflow:{route}",
                severity="high",
                summary=f"{route} takes an unusually large share of traffic (share={share:.2%}).",
                evidence={"route": route, "share": share, "route_stats": route_stats.get(route, {})},
                hypothesis=f"Potential {route} overflow in early-stage recall, starving other routes and harming diversity.",
                suggested_actions=[
                    "Inspect blending constraints / caps; confirm no recent config drift.",
                    "Run an A/B introducing route caps or rebalancing to recover diversity and long-tail quality."
                ]
            ))

    # --- Surface imbalance detection ---
    # Find surfaces with CTR far from global
    if global_ctr is not None and surface_stats:
        diffs = []
        for s, stats in surface_stats.items():
            ctr = stats.get("ctr", None)
            if ctr is not None:
                diffs.append((s, float(ctr) - float(global_ctr)))
        for s, d in _topk_by_abs_diff(diffs, k=2):
            if abs(d) >= 0.02:  # 2pp gap threshold for sample; tune later
                findings.append(Finding(
                    key=f"surface_ctr_gap:{s}",
                    severity="medium" if abs(d) < 0.05 else "high",
                    summary=f"{s} CTR differs from global by {d:+.3f} (possible cross-surface shift).",
                    evidence={"surface": s, "delta_ctr_vs_global": d, "surface_stats": surface_stats.get(s, {}), "global_ctr": global_ctr},
                    hypothesis="Surface-level traffic/value composition may have shifted; potential cross-surface cannibalization or misaligned objectives.",
                    suggested_actions=[
                        "Slice by surface and route to see which routes drive the gap.",
                        "Consider a cross-surface objective adjustment or surface-specific blending guardrails.",
                        "Run an A/B with surface-level caps / invalidation to control cannibalization."
                    ]
                ))

    # --- Calibration signal ---
    if calib is not None:
        calib = float(calib)
        if abs(calib) >= 0.01:
            findings.append(Finding(
                key="calibration_drift",
                severity="medium" if abs(calib) < 0.03 else "high",
                summary=f"Predicted CTR shows drift vs observed (mean pred_ctr - ctr = {calib:+.4f}).",
                evidence={"calibration_drift": calib},
                hypothesis="Model calibration or score scaling drift may be contributing to ranking inefficiency and unstable traffic allocation.",
                suggested_actions=[
                    "Check pred_ctr distribution shift vs baseline; validate feature/logging changes.",
                    "Run a calibration A/B (e.g., temperature scaling / isotonic) and measure CTR stability & value.",
                    "Add drift monitoring and guardrails for score scaling changes."
                ]
            ))

    return {
        "global_ctr": global_ctr,
        "num_findings": len(findings),
        "findings": [asdict(f) for f in findings],
    }
