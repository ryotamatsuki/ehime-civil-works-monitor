#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = json.loads((ROOT / 'public/data/projects.json').read_text(encoding='utf-8'))
P26 = json.loads((ROOT / 'public/data/phase26-inventory.json').read_text(encoding='utf-8'))
REC = json.loads((ROOT / 'public/data/phase26-reconciliation.json').read_text(encoding='utf-8'))
P27 = json.loads((ROOT / 'public/data/phase27-inventory.json').read_text(encoding='utf-8'))

excluded = {item['candidateId'] for item in REC['excludedExistingRoadIds']}
phase26_ids = [row[0] for row in P26['roads'] if row[0] not in excluded]
phase26_ids += [row[0] for row in REC['roadAdditions']]
phase26_ids += [row[0] for row in P26['sabo']]
base_ids = [project['id'] for project in BASE['projects']]
phase27_ids = [row[0] for row in P27['projects']]

assert len(phase27_ids) == P27['expectedAdditions'] == 60
assert len(set(phase27_ids)) == len(phase27_ids), 'duplicate Phase 2.7 ids'
assert not (set(phase27_ids) & set(base_ids)), 'Phase 2.7 duplicates base canonical ids'
assert not (set(phase27_ids) & set(phase26_ids)), 'Phase 2.7 duplicates Phase 2.6 ids'
assert len(base_ids) + len(phase26_ids) + len(phase27_ids) == P27['expectedRuntimeTotal'] == 169

allowed = {'river','coast','sabo','road','urban','agriculture','port','dam','forestry','fishing-port'}
for row in P27['projects']:
    assert len(row) == 8
    project_id, name, category, category_label, department, municipalities, source_key, scope = row
    assert project_id and name and category_label and department and scope
    assert category in allowed
    assert municipalities and all(isinstance(x, str) and x for x in municipalities)
    assert source_key in P27['sources']

assert any(item['classification'] == 'SCOPE_CONFLICT_HOLD' for item in P27['excludedCandidates'])
print(f"Phase 2.7 validation PASS: +{len(phase27_ids)} projects, runtime={P27['expectedRuntimeTotal']}")
