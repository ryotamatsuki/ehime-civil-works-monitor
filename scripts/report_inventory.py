#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = json.loads((ROOT / 'public/data/projects.json').read_text(encoding='utf-8'))['projects']
FEATURES = json.loads((ROOT / 'public/data/projects.geojson').read_text(encoding='utf-8'))['features']
ENRICHMENT = json.loads((ROOT / 'public/data/enrichment.json').read_text(encoding='utf-8'))['records']
PHASE26 = json.loads((ROOT / 'public/data/phase26-inventory.json').read_text(encoding='utf-8'))


def has_nonempty_enrichment(record):
    return any(record.get(key) for key in ('annualBudgetHistory', 'cumulativeInvestmentHistory', 'benefitCostHistory', 'documentedReasons'))


def has_multi_history(project):
    return any(len(project.get(key, [])) >= 2 for key in ('costHistory', 'scheduleHistory', 'progressHistory'))


def has_snapshot(project):
    return any(project.get(key) is not None for key in (
        'startFiscalYear', 'plannedCompletionFiscalYear', 'totalProjectCostMillionYen',
        'progressPercent', 'landAcquisitionProgressPercent', 'benefitCostRatio'
    )) or any(bool(project.get(key, [])) for key in ('costHistory', 'scheduleHistory', 'progressHistory'))


enriched_ids = {record['projectId'] for record in ENRICHMENT if has_nonempty_enrichment(record)}
levels = Counter()
for project in PROJECTS:
    if project['id'] in enriched_ids: levels['enriched'] += 1
    elif has_multi_history(project): levels['history'] += 1
    elif has_snapshot(project): levels['snapshot'] += 1
    else: levels['inventory'] += 1

new_roads = PHASE26['roads']
new_sabo = PHASE26['sabo']
new_count = len(new_roads) + len(new_sabo)
# All Phase 2.6 production additions carry at least an official start year, so they are Snapshot under current domain rules.
levels['snapshot'] += new_count

category_counts = Counter(project['category'] for project in PROJECTS)
category_counts['road'] += len(new_roads)
category_counts['sabo'] += len(new_sabo)
status_counts = Counter(project['status'] for project in PROJECTS)
status_counts['under_construction'] += new_count
location_counts = Counter(project['locationAccuracy'] for project in PROJECTS)
location_counts['approximate'] += new_count
geometry_counts = Counter(feature['geometry']['type'] for feature in FEATURES)
geometry_counts['Point'] += new_count

def covered(key): return sum(project.get(key) is not None for project in PROJECTS)

report = {
    'projects': len(PROJECTS) + new_count,
    'baseProjects': len(PROJECTS),
    'phase26NewProjects': new_count,
    'projectedGeojsonFeatures': len(FEATURES) + new_count,
    'projectedEnrichmentRecords': len(ENRICHMENT) + new_count,
    'status': dict(sorted(status_counts.items())),
    'dataDepthExclusive': dict(sorted(levels.items())),
    'historyPlus': levels['history'] + levels['enriched'],
    'monitored': len(PROJECTS) + new_count - levels['inventory'],
    'categories': dict(sorted(category_counts.items())),
    'geometry': dict(sorted(geometry_counts.items())),
    'locationAccuracy': dict(sorted(location_counts.items())),
    'coverage': {
        'knownTotalCost': covered('totalProjectCostMillionYen') + len(new_sabo),
        'knownCompletionYear': covered('plannedCompletionFiscalYear') + sum(1 for row in new_roads if row[5] is not None) + len(new_sabo),
        'knownProgress': covered('progressPercent') + len(new_sabo),
    },
    'phase26': {
        'productionAdditions': {'road': len(new_roads), 'sabo': len(new_sabo), 'total': new_count},
        'sourceFamilySaturation': {
            'EhimeCivilWorks2024_2026': 'audited as discovery/reconciliation source',
            'RoadProgramVol8': 'audited; production candidate table reconciled',
            'LocalOffices': 'audited as discovery source; broader route/river labels withheld unless project scope independently confirmed',
            'EvaluationR2_R7': 'audited; R7 second-meeting sabo cohort added; older cohorts used for reconciliation/history',
            'EvaluationR8': 'meeting notice audited; detailed post-meeting result not used without published project-level result',
            'R8BudgetInitialJuneSeptember': 'audited in Phase 2.5; program totals not allocated to projects',
            'MLITShikoku': 'audited for major Ehime road projects and operator reconciliation',
            'Procurement': 'audited for discovery only; contracts/work packages not canonicalized',
        },
        'remainingBlindSpots': [
            'R8 public-works evaluation detailed result after the 2026-09-01 meeting',
            'project-level identity behind local-office pages that list only broad route/river names',
            'official GIS geometry for most projects',
        ],
    },
}
print(json.dumps(report, ensure_ascii=False, indent=2))
