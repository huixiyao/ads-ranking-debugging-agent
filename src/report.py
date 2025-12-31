from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, List


@dataclass
class Experiment:
    name: str
    description: str
    success_metrics: List[str]
    guardrails: List[str]


@dataclass
class DebugReport:
    summary: str
    hypotheses: List[Dict[str, Any]]
    experiments: List[Experiment]
    notes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["experiments"] = [asdict(e) for e in self.experiments]
        return d


def render_markdown(report: DebugReport) -> str:
    lines = []
    lines.append(f"# Debug Report\n\n{report.summary}\n")
    lines.append("## Hypotheses\n")
    for i, h in enumerate(report.hypotheses, 1):
        lines.append(f"### H{i}: {h.get('title','')}\n")
        lines.append(f"- **Confidence:** {h.get('confidence','')}\n")
        lines.append(f"- **Evidence:** {h.get('evidence','')}\n")
        lines.append(f"- **Proposed validation:** {h.get('validation','')}\n")
        lines.append("")
    lines.append("## Recommended Experiments\n")
    for e in report.experiments:
        lines.append(f"### {e.name}\n")
        lines.append(f"{e.description}\n")
        lines.append(f"- **Success metrics:** {', '.join(e.success_metrics)}\n")
        lines.append(f"- **Guardrails:** {', '.join(e.guardrails)}\n")
        lines.append("")
    if report.notes:
        lines.append("## Notes / Confounders\n")
        for n in report.notes:
            lines.append(f"- {n}")
        lines.append("")
    return "\n".join(lines)
