#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "public/data/projects.json"
GEOJSON = ROOT / "public/data/projects.geojson"
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CATEGORIES = {"river", "coast", "sabo", "road", "urban"}
STATUSES = {"planned", "under_construction", "completed", "unknown"}
LOCATION = {"official", "derived", "approximate", "unknown"}


def valid_url(value):
    p = urlparse(value)
    return p.scheme == "https" and bool(p.netloc)


def check_position(coords, errors, ctx):
    if not isinstance(coords, list) or len(coords) < 2:
        errors.append(f"{ctx}: invalid position")
        return
    lon, lat = coords[:2]
    if not isinstance(lon, (int, float)) or not isinstance(lat, (int, float)):
        errors.append(f"{ctx}: non-numeric coordinate")
        return
    if not (-180 <= lon <= 180 and -90 <= lat <= 90):
        errors.append(f"{ctx}: coordinate outside global range")
    if not (131.5 <= lon <= 133.8 and 32.7 <= lat <= 34.5):
        errors.append(f"{ctx}: coordinate outside broad Ehime vicinity")


def check_geometry(g, errors, ctx):
    if not isinstance(g, dict):
        errors.append(f"{ctx}: geometry must be object")
        return
    t, c = g.get("type"), g.get("coordinates")
    if t == "Point":
        check_position(c, errors, ctx)
    elif t == "LineString":
        if not isinstance(c, list) or len(c) < 2:
            errors.append(f"{ctx}: LineString needs >=2 points")
        else:
            for i, p in enumerate(c): check_position(p, errors, f"{ctx}[{i}]")
    elif t == "Polygon":
        if not isinstance(c, list) or not c:
            errors.append(f"{ctx}: Polygon needs rings")
        else:
            for r, ring in enumerate(c):
                if not isinstance(ring, list) or len(ring) < 4 or ring[0] != ring[-1]:
                    errors.append(f"{ctx}: ring {r} must be closed")
                else:
                    for i, p in enumerate(ring): check_position(p, errors, f"{ctx}[{r}][{i}]")
    else:
        errors.append(f"{ctx}: unsupported geometry {t!r}")


def main():
    errors = []
    try:
        data = json.loads(PROJECTS.read_text(encoding="utf-8"))
        geo = json.loads(GEOJSON.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: cannot parse data: {exc}", file=sys.stderr)
        return 1

    projects = data.get("projects")
    if not isinstance(projects, list) or not projects:
        print("ERROR: projects must be non-empty array", file=sys.stderr)
        return 1

    ids = set()
    refs = set()
    required = {"id","name","category","categoryLabel","operator","department","municipalities","status","statusLabel","lastVerified","summary","scope","sources","provenance"}
    for i, p in enumerate(projects):
        ctx = f"projects[{i}]"
        for key in required - p.keys(): errors.append(f"{ctx}: missing {key}")
        pid = p.get("id")
        if not isinstance(pid, str) or not ID_RE.match(pid): errors.append(f"{ctx}: invalid id")
        elif pid in ids: errors.append(f"{ctx}: duplicate id {pid}")
        else: ids.add(pid)
        if p.get("category") not in CATEGORIES: errors.append(f"{ctx}: invalid category")
        if p.get("status") not in STATUSES: errors.append(f"{ctx}: invalid status")
        if p.get("locationAccuracy") not in LOCATION: errors.append(f"{ctx}: invalid locationAccuracy")
        if not isinstance(p.get("municipalities"), list) or not p.get("municipalities"): errors.append(f"{ctx}: municipalities required")
        for key in ("startFiscalYear","plannedCompletionFiscalYear"):
            v = p.get(key)
            if v is not None and (not isinstance(v, int) or not 1900 <= v <= 2200): errors.append(f"{ctx}: invalid {key}")
        if isinstance(p.get("startFiscalYear"), int) and isinstance(p.get("plannedCompletionFiscalYear"), int) and p["plannedCompletionFiscalYear"] < p["startFiscalYear"]: errors.append(f"{ctx}: completion before start")
        for key in ("totalProjectCostMillionYen","currentFiscalYearBudgetMillionYen"):
            v = p.get(key)
            if v is not None and (not isinstance(v, (int,float)) or v < 0): errors.append(f"{ctx}: invalid {key}")
        for key in ("progressPercent","landAcquisitionProgressPercent"):
            v = p.get(key)
            if v is not None and (not isinstance(v, (int,float)) or not 0 <= v <= 100): errors.append(f"{ctx}: invalid {key}")
        if not isinstance(p.get("lastVerified"), str) or not DATE_RE.match(p["lastVerified"]): errors.append(f"{ctx}: invalid lastVerified")
        sources = p.get("sources", [])
        if not isinstance(sources, list) or not sources: errors.append(f"{ctx}: source required"); sources=[]
        source_ids = set()
        for j, s in enumerate(sources):
            sid=s.get("id"); sctx=f"{ctx}.sources[{j}]"
            if not isinstance(sid,str) or not sid: errors.append(f"{sctx}: id required")
            elif sid in source_ids: errors.append(f"{sctx}: duplicate id")
            else: source_ids.add(sid)
            if not valid_url(s.get("url", "")): errors.append(f"{sctx}: invalid https URL")
            if not isinstance(s.get("accessed"),str) or not DATE_RE.match(s["accessed"]): errors.append(f"{sctx}: invalid accessed")
        provenance=p.get("provenance",{})
        if not isinstance(provenance,dict): errors.append(f"{ctx}: provenance must be object")
        else:
            for field,sid in provenance.items():
                if field not in p: errors.append(f"{ctx}: provenance unknown field {field}")
                if sid not in source_ids: errors.append(f"{ctx}: missing provenance source {sid}")
        if p.get("locationSource") is not None and p["locationSource"] not in source_ids: errors.append(f"{ctx}: invalid locationSource")
        if p.get("geometryRef") is not None: refs.add(p["geometryRef"])

    if geo.get("type") != "FeatureCollection" or not isinstance(geo.get("features"), list):
        errors.append("GeoJSON root must be FeatureCollection")
        features=[]
    else: features=geo["features"]
    feature_ids=set()
    for i,f in enumerate(features):
        ctx=f"geojson.features[{i}]"
        pid=f.get("properties",{}).get("projectId")
        if pid not in ids: errors.append(f"{ctx}: unknown projectId")
        elif pid in feature_ids: errors.append(f"{ctx}: duplicate project geometry")
        else: feature_ids.add(pid)
        check_geometry(f.get("geometry"),errors,ctx)
    if refs-feature_ids: errors.append("Missing GeoJSON: "+", ".join(sorted(refs-feature_ids)))

    if errors:
        print("Data validation failed:", file=sys.stderr)
        for e in errors: print(" - "+e, file=sys.stderr)
        return 1
    print(f"Data validation OK: {len(projects)} projects, {len(features)} GeoJSON features")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
