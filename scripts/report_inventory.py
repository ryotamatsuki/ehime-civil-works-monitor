#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = json.loads((ROOT / "public/data/projects.json").read_text(encoding="utf-8"))["projects"]
FEATURES = json.loads((ROOT / "public/data/projects.geojson").read_text(encoding="utf-8"))["features"]
ENRICHMENT = json.loads((ROOT / "public/data/enrichment.json").read_text(encoding="utf-8"))["records"]


def has_nonempty_enrichment(record):
    return any(record.get(key) for key in (
        "annualBudgetHistory", "cumulativeInvestmentHistory", "benefitCostHistory", "documentedReasons"
    ))


def has_multi_history(project):
    return any(len(project.get(key, [])) >= 2 for key in ("costHistory", "scheduleHistory", "progressHistory"))


def has_snapshot(project):
    return any(project.get(key) is not None for key in (
        "totalProjectCostMillionYen", "plannedCompletionFiscalYear", "progressPercent",
        "startFiscalYear", "benefitCostRatio"
    ))


enriched_ids = {record["projectId"] for record in ENRICHMENT if has_nonempty_enrichment(record)}
levels = Counter()
for project in PROJECTS:
    if project["id"] in enriched_ids:
        levels["enriched"] += 1
    elif has_multi_history(project):
        levels["history"] += 1
    elif has_snapshot(project):
        levels["snapshot"] += 1
    else:
        levels["inventory"] += 1

category_counts = Counter(project["category"] for project in PROJECTS)
location_counts = Counter(project["locationAccuracy"] for project in PROJECTS)
geometry_counts = Counter(feature["geometry"]["type"] for feature in FEATURES)

known_cost = sum(project["totalProjectCostMillionYen"] is not None for project in PROJECTS)
known_completion = sum(project["plannedCompletionFiscalYear"] is not None for project in PROJECTS)
known_progress = sum(project["progressPercent"] is not None for project in PROJECTS)
cost_history = sum(bool(project.get("costHistory")) for project in PROJECTS)
schedule_history = sum(bool(project.get("scheduleHistory")) for project in PROJECTS)
progress_history = sum(bool(project.get("progressHistory")) for project in PROJECTS)
multi_cost_history = sum(len(project.get("costHistory", [])) >= 2 for project in PROJECTS)
multi_schedule_history = sum(len(project.get("scheduleHistory", [])) >= 2 for project in PROJECTS)
multi_progress_history = sum(len(project.get("progressHistory", [])) >= 2 for project in PROJECTS)
bc_projects = sum(bool(record.get("benefitCostHistory")) for record in ENRICHMENT)
reason_projects = sum(bool(record.get("documentedReasons")) for record in ENRICHMENT)
annual_budget_projects = sum(bool(record.get("annualBudgetHistory")) for record in ENRICHMENT)
investment_projects = sum(bool(record.get("cumulativeInvestmentHistory")) for record in ENRICHMENT)

report = {
    "projects": len(PROJECTS),
    "geojsonFeatures": len(FEATURES),
    "enrichmentRecords": len(ENRICHMENT),
    "dataDepthExclusive": dict(sorted(levels.items())),
    "historyPlus": levels["history"] + levels["enriched"],
    "monitored": len(PROJECTS) - levels["inventory"],
    "categories": dict(sorted(category_counts.items())),
    "geometry": dict(sorted(geometry_counts.items())),
    "locationAccuracy": dict(sorted(location_counts.items())),
    "coverage": {
        "knownTotalCost": known_cost,
        "knownCompletionYear": known_completion,
        "knownProgress": known_progress,
        "costHistoryAny": cost_history,
        "scheduleHistoryAny": schedule_history,
        "progressHistoryAny": progress_history,
        "costHistoryComparable": multi_cost_history,
        "scheduleHistoryComparable": multi_schedule_history,
        "progressHistoryComparable": multi_progress_history,
        "annualBudget": annual_budget_projects,
        "cumulativeInvestment": investment_projects,
        "benefitCost": bc_projects,
        "documentedReasons": reason_projects,
    },
}
print(json.dumps(report, ensure_ascii=False, indent=2))
