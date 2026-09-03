#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = json.loads((ROOT / 'public/data/projects.json').read_text(encoding='utf-8'))['projects']
FEATURES = json.loads((ROOT / 'public/data/projects.geojson').read_text(encoding='utf-8'))['features']
ENRICHMENT = json.loads((ROOT / 'public/data/enrichment.json').read_text(encoding='utf-8'))['records']
PHASE26 = json.loads((ROOT / 'public/data/phase26-inventory.json').read_text(encoding='utf-8'))
RECONCILIATION = json.loads((ROOT / 'public/data/phase26-reconciliation.json').read_text(encoding='utf-8'))
PHASE27 = json.loads((ROOT / 'public/data/phase27-inventory.json').read_text(encoding='utf-8'))


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

excluded = {item['candidateId'] for item in RECONCILIATION['excludedExistingRoadIds']}
new_roads = [row for row in PHASE26['roads'] if row[0] not in excluded] + RECONCILIATION['roadAdditions']
new_sabo = PHASE26['sabo']
phase26_count = len(new_roads) + len(new_sabo)
phase27_rows = PHASE27['projects']
phase27_count = len(phase27_rows)
levels['snapshot'] += phase26_count
levels['inventory'] += phase27_count

category_counts = Counter(project['category'] for project in PROJECTS)
category_counts['road'] += len(new_roads)
category_counts['sabo'] += len(new_sabo)
for row in phase27_rows:
    category_counts[row[2]] += 1

status_counts = Counter(project['status'] for project in PROJECTS)
status_counts['under_construction'] += phase26_count + phase27_count
location_counts = Counter(project['locationAccuracy'] for project in PROJECTS)
location_counts['approximate'] += phase26_count + phase27_count
geometry_counts = Counter(feature['geometry']['type'] for feature in FEATURES)
geometry_counts['Point'] += phase26_count + phase27_count


def covered(key):
    return sum(project.get(key) is not None for project in PROJECTS)


total = len(PROJECTS) + phase26_count + phase27_count
report = {
    'projects': total,
    'baseProjects': len(PROJECTS),
    'phase26NewProjects': phase26_count,
    'phase27NewProjects': phase27_count,
    'projectedGeojsonFeatures': len(FEATURES) + phase26_count + phase27_count,
    'projectedEnrichmentRecords': len(ENRICHMENT) + phase26_count + phase27_count,
    'status': dict(sorted(status_counts.items())),
    'dataDepthExclusive': dict(sorted(levels.items())),
    'historyPlus': levels['history'] + levels['enriched'],
    'monitored': total - levels['inventory'],
    'categories': dict(sorted(category_counts.items())),
    'geometry': dict(sorted(geometry_counts.items())),
    'locationAccuracy': dict(sorted(location_counts.items())),
    'coverage': {
        'knownTotalCost': covered('totalProjectCostMillionYen') + len(new_sabo),
        'knownCompletionYear': covered('plannedCompletionFiscalYear') + sum(1 for row in new_roads if row[5] is not None) + len(new_sabo),
        'knownProgress': covered('progressPercent') + len(new_sabo),
    },
    'phase26': {
        'productionAdditions': {'road': len(new_roads), 'sabo': len(new_sabo), 'total': phase26_count},
        'reconciledExistingCandidates': len(RECONCILIATION['excludedExistingRoadIds']),
    },
    'phase27': {
        'productionAdditions': dict(sorted(Counter(row[2] for row in phase27_rows).items())),
        'total': phase27_count,
        'expectedRuntimeTotal': PHASE27['expectedRuntimeTotal'],
        'scopeConflictHolds': len(PHASE27.get('excludedCandidates', [])),
        'remainingBlindSpots': [
            'R8 public-works evaluation final result after the 2026-09-01 meeting',
            'Round 1 composite river scope conflict: Uzuigawa/Murogawa/Sakaidani/Kongoin-dani versus existing Sakaidani project',
            'project-level decomposition of remaining agriculture and port/coast source families',
            'official GIS geometry for most Phase 2.7 projects',
        ],
    },
}
assert total == PHASE27['expectedRuntimeTotal'] == 169
print(json.dumps(report, ensure_ascii=False, indent=2))
