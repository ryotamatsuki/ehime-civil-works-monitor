#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
BASE = json.loads((ROOT / 'public/data/projects.json').read_text(encoding='utf-8'))
GEO = json.loads((ROOT / 'public/data/projects.geojson').read_text(encoding='utf-8'))
ENRICHMENT = json.loads((ROOT / 'public/data/enrichment.json').read_text(encoding='utf-8'))
BUDGET = json.loads((ROOT / 'public/data/annual-budget-r5-r8.json').read_text(encoding='utf-8'))
SEED = json.loads((ROOT / 'public/data/phase26-inventory.json').read_text(encoding='utf-8'))
RECONCILIATION = json.loads((ROOT / 'public/data/phase26-reconciliation.json').read_text(encoding='utf-8'))

ID_RE = re.compile(r'^[a-z0-9][a-z0-9-]*$')


def norm(value):
    return re.sub(r'[\s　（）()・･\-‐―ー]', '', value).lower()


def good_url(value):
    p = urlparse(value) if isinstance(value, str) else None
    return bool(p and p.scheme == 'https' and p.netloc)


def validate_road(row, ctx, errors):
    if not isinstance(row, list) or len(row) != 7:
        errors.append(f'{ctx}: expected 7 fields')
        return None
    pid, name, operator, municipalities, start, completion, scale = row
    if not isinstance(pid, str) or not ID_RE.match(pid): errors.append(f'{ctx}: invalid id')
    if not all(isinstance(v, str) and v.strip() for v in (name, operator, scale)): errors.append(f'{ctx}: missing identity field')
    if not isinstance(municipalities, list) or not municipalities or not all(isinstance(x, str) and x.strip() for x in municipalities): errors.append(f'{ctx}: municipalities required')
    if not isinstance(start, int) or not 1900 <= start <= 2200: errors.append(f'{ctx}: invalid start year')
    if completion is not None and (not isinstance(completion, int) or not start <= completion <= 2200): errors.append(f'{ctx}: invalid completion year')
    return pid, name


def main():
    errors = []
    base_projects = BASE.get('projects', [])
    base_ids = {p.get('id') for p in base_projects}
    base_by_id = {p.get('id'): p for p in base_projects}
    base_names = {norm(p.get('name', '')): p.get('id') for p in base_projects}

    if SEED.get('v') != '2.6.0': errors.append('phase26 seed version must be 2.6.0')
    if SEED.get('d') != '2026-09-03': errors.append('phase26 verification date must be 2026-09-03')
    for key in ('roadSource', 'evalSource'):
        if not good_url(SEED.get(key)): errors.append(f'invalid {key}')

    roads = SEED.get('roads') if isinstance(SEED.get('roads'), list) else []
    sabo = SEED.get('sabo') if isinstance(SEED.get('sabo'), list) else []
    exclusions = RECONCILIATION.get('excludedExistingRoadIds') if isinstance(RECONCILIATION.get('excludedExistingRoadIds'), list) else []
    additions = RECONCILIATION.get('roadAdditions') if isinstance(RECONCILIATION.get('roadAdditions'), list) else []
    seed_road_by_id = {row[0]: row for row in roads if isinstance(row, list) and len(row) == 7}
    excluded_ids = set()

    for i, item in enumerate(exclusions):
        ctx = f'excludedExistingRoadIds[{i}]'
        if not isinstance(item, dict): errors.append(f'{ctx}: object required'); continue
        candidate = item.get('candidateId')
        existing = item.get('existingProjectId')
        if candidate not in seed_road_by_id: errors.append(f'{ctx}: candidateId not in seed')
        if existing not in base_by_id: errors.append(f'{ctx}: existingProjectId not in base')
        if not isinstance(item.get('reason'), str) or not item.get('reason', '').strip(): errors.append(f'{ctx}: reason required')
        if candidate in seed_road_by_id and existing in base_by_id:
            if norm(seed_road_by_id[candidate][1]) != norm(base_by_id[existing]['name']):
                errors.append(f'{ctx}: reconciliation names are not the same normalized project')
        excluded_ids.add(candidate)

    production_roads = []
    for i, row in enumerate(roads):
        identity = validate_road(row, f'roads[{i}]', errors)
        if identity and identity[0] not in excluded_ids: production_roads.append(row)
    for i, row in enumerate(additions):
        identity = validate_road(row, f'roadAdditions[{i}]', errors)
        if identity: production_roads.append(row)

    production_ids = []
    production_names = []
    for row in production_roads:
        production_ids.append(row[0]); production_names.append((row[0], row[1]))

    for i, row in enumerate(sabo):
        ctx = f'sabo[{i}]'
        if not isinstance(row, list) or len(row) != 9:
            errors.append(f'{ctx}: expected 9 fields'); continue
        pid, name, municipality, start, completion, cost, progress, bc, scale = row
        if not isinstance(pid, str) or not ID_RE.match(pid): errors.append(f'{ctx}: invalid id')
        if not all(isinstance(v, str) and v.strip() for v in (name, municipality, scale)): errors.append(f'{ctx}: missing identity field')
        if not isinstance(start, int) or not isinstance(completion, int) or not start <= completion <= 2200: errors.append(f'{ctx}: invalid period')
        if not isinstance(cost, (int, float)) or cost < 0: errors.append(f'{ctx}: invalid cost')
        if not isinstance(progress, (int, float)) or not 0 <= progress <= 100: errors.append(f'{ctx}: invalid progress')
        if not isinstance(bc, (int, float)) or bc < 0: errors.append(f'{ctx}: invalid B/C')
        production_ids.append(pid); production_names.append((pid, name))

    if len(production_ids) != len(set(production_ids)): errors.append('duplicate Phase 2.6 production project id')
    overlap = base_ids & set(production_ids)
    if overlap: errors.append('Phase 2.6 production IDs already exist in base: ' + ', '.join(sorted(overlap)))

    seen_names = {}
    for pid, name in production_names:
        key = norm(name)
        if key in base_names: errors.append(f'{pid}: normalized name duplicates base {base_names[key]}')
        if key in seen_names: errors.append(f'{pid}: normalized name duplicates Phase 2.6 {seen_names[key]}')
        seen_names[key] = pid
        if 'うち強靭化' in name: errors.append(f'{pid}: work-package-like production name')

    base_geo = {f.get('properties', {}).get('projectId') for f in GEO.get('features', [])}
    base_enrichment = {r.get('projectId') for r in ENRICHMENT.get('records', [])}
    base_budget = {r.get('projectId') for r in BUDGET.get('records', [])}
    if base_geo != base_ids: errors.append('base GeoJSON set mismatch before overlay')
    if base_enrichment != base_ids: errors.append('base enrichment set mismatch before overlay')
    if base_budget != base_ids: errors.append('base annual-budget audit set mismatch before overlay')

    union = base_ids | set(production_ids)
    if len(union) < 100: errors.append(f'canonical union below benchmark: {len(union)}')
    if len(production_ids) != 59: errors.append(f'expected audited production additions 59, got {len(production_ids)}')
    if len(production_roads) != 50: errors.append(f'expected 50 production road projects, got {len(production_roads)}')

    if errors:
        print('Phase 2.6 validation failed:', file=sys.stderr)
        for error in errors: print(' - ' + error, file=sys.stderr)
        return 1

    print(f'Phase 2.6 validation OK: {len(base_ids)} base + {len(production_ids)} new = {len(union)} canonical projects')
    print(f'  new road: {len(production_roads)} / new sabo: {len(sabo)}')
    print(f'  reconciled existing candidates excluded: {len(excluded_ids)}')
    print(f'  projected GeoJSON/enrichment/annual-budget record sets: {len(union)} each')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
