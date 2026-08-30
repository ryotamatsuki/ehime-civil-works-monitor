#!/usr/bin/env python3
import json
import math
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "public/data/projects.json"
GEOJSON = ROOT / "public/data/projects.geojson"
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CATEGORIES = {"river", "coast", "sabo", "road", "urban", "agriculture", "port"}
STATUSES = {"planned", "under_construction", "completed", "unknown"}
LOCATION = {"official", "derived", "approximate", "unknown"}


def valid_url(value):
    p = urlparse(value)
    return p.scheme == "https" and bool(p.netloc)


def valid_date(value):
    if not isinstance(value, str) or not DATE_RE.match(value):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def check_position(coords, errors, ctx):
    if not isinstance(coords, list) or len(coords) < 2:
        errors.append(f"{ctx}: invalid position")
        return
    lon, lat = coords[:2]
    if not finite_number(lon) or not finite_number(lat):
        errors.append(f"{ctx}: non-numeric or non-finite coordinate")
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
            for i, p in enumerate(c):
                check_position(p, errors, f"{ctx}[{i}]")
    elif t == "Polygon":
        if not isinstance(c, list) or not c:
            errors.append(f"{ctx}: Polygon needs rings")
        else:
            for r, ring in enumerate(c):
                if not isinstance(ring, list) or len(ring) < 4 or ring[0] != ring[-1]:
                    errors.append(f"{ctx}: ring {r} must be closed")
                else:
                    for i, p in enumerate(ring):
                        check_position(p, errors, f"{ctx}[{r}][{i}]")
    else:
        errors.append(f"{ctx}: unsupported geometry {t!r}")


def check_history(p, key, source_ids, errors, value_key, value_validator, latest_snapshot_key):
    ctx = f"{p.get('id', 'unknown')}.{key}"
    history = p.get(key)
    if not isinstance(history, list):
        errors.append(f"{ctx}: must be an array")
        return

    dates = []
    seen_dates = set()
    for i, entry in enumerate(history):
        ectx = f"{ctx}[{i}]"
        if not isinstance(entry, dict):
            errors.append(f"{ectx}: must be an object")
            continue
        as_of = entry.get("asOf")
        if not valid_date(as_of):
            errors.append(f"{ectx}: invalid asOf")
        else:
            if as_of in seen_dates:
                errors.append(f"{ectx}: duplicate asOf {as_of}")
            seen_dates.add(as_of)
            dates.append(as_of)
        source_id = entry.get("sourceId")
        if not isinstance(source_id, str) or source_id not in source_ids:
            errors.append(f"{ectx}: sourceId {source_id!r} does not resolve to project.sources")
        value = entry.get(value_key)
        if not value_validator(value):
            errors.append(f"{ectx}: invalid {value_key}")
        note = entry.get("note")
        if note is not None and not isinstance(note, str):
            errors.append(f"{ectx}: note must be a string")
        if key == "costHistory":
            fiscal_year = entry.get("fiscalYear")
            if fiscal_year is not None and (not isinstance(fiscal_year, int) or isinstance(fiscal_year, bool) or not 1900 <= fiscal_year <= 2200):
                errors.append(f"{ectx}: invalid fiscalYear")

    if dates != sorted(dates):
        errors.append(f"{ctx}: entries must be ordered by asOf ascending")

    if history:
        latest = history[-1].get(value_key) if isinstance(history[-1], dict) else None
        snapshot = p.get(latest_snapshot_key)
        if latest != snapshot:
            errors.append(
                f"{ctx}: latest history value {latest!r} does not match {latest_snapshot_key} {snapshot!r}"
            )


def main():
    errors = []
    try:
        data = json.loads(PROJECTS.read_text(encoding="utf-8"))
        geo = json.loads(GEOJSON.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: cannot parse data: {exc}", file=sys.stderr)
        return 1

    if data.get("schemaVersion") != "2.0.0":
        errors.append("schemaVersion must be 2.0.0 for Phase 2")

    projects = data.get("projects")
    if not isinstance(projects, list) or not projects:
        print("ERROR: projects must be non-empty array", file=sys.stderr)
        return 1

    ids = set()
    refs = set()
    required = {
        "id", "name", "category", "categoryLabel", "operator", "department", "municipalities",
        "status", "statusLabel", "lastVerified", "summary", "scope", "sources", "provenance",
        "costHistory", "scheduleHistory", "progressHistory"
    }
    for i, p in enumerate(projects):
        ctx = f"projects[{i}]"
        for key in required - p.keys():
            errors.append(f"{ctx}: missing {key}")
        pid = p.get("id")
        if not isinstance(pid, str) or not ID_RE.match(pid):
            errors.append(f"{ctx}: invalid id")
        elif pid in ids:
            errors.append(f"{ctx}: duplicate id {pid}")
        else:
            ids.add(pid)
        if p.get("category") not in CATEGORIES:
            errors.append(f"{ctx}: invalid category")
        if p.get("status") not in STATUSES:
            errors.append(f"{ctx}: invalid status")
        if p.get("locationAccuracy") not in LOCATION:
            errors.append(f"{ctx}: invalid locationAccuracy")
        if not isinstance(p.get("municipalities"), list) or not p.get("municipalities"):
            errors.append(f"{ctx}: municipalities required")
        for key in ("startFiscalYear", "plannedCompletionFiscalYear"):
            v = p.get(key)
            if v is not None and (not isinstance(v, int) or isinstance(v, bool) or not 1900 <= v <= 2200):
                errors.append(f"{ctx}: invalid {key}")
        if isinstance(p.get("startFiscalYear"), int) and isinstance(p.get("plannedCompletionFiscalYear"), int) and p["plannedCompletionFiscalYear"] < p["startFiscalYear"]:
            errors.append(f"{ctx}: completion before start")
        for key in ("totalProjectCostMillionYen", "currentFiscalYearBudgetMillionYen"):
            v = p.get(key)
            if v is not None and (not finite_number(v) or v < 0):
                errors.append(f"{ctx}: invalid {key}")
        for key in ("progressPercent", "landAcquisitionProgressPercent"):
            v = p.get(key)
            if v is not None and (not finite_number(v) or not 0 <= v <= 100):
                errors.append(f"{ctx}: invalid {key}")
        if not valid_date(p.get("lastVerified")):
            errors.append(f"{ctx}: invalid lastVerified")
        sources = p.get("sources", [])
        if not isinstance(sources, list) or not sources:
            errors.append(f"{ctx}: source required")
            sources = []
        source_ids = set()
        for j, s in enumerate(sources):
            sid = s.get("id")
            sctx = f"{ctx}.sources[{j}]"
            if not isinstance(sid, str) or not sid:
                errors.append(f"{sctx}: id required")
            elif sid in source_ids:
                errors.append(f"{sctx}: duplicate id")
            else:
                source_ids.add(sid)
            if not valid_url(s.get("url", "")):
                errors.append(f"{sctx}: invalid https URL")
            if not valid_date(s.get("accessed")):
                errors.append(f"{sctx}: invalid accessed")
        provenance = p.get("provenance", {})
        if not isinstance(provenance, dict):
            errors.append(f"{ctx}: provenance must be object")
        else:
            for field, sid in provenance.items():
                if field not in p:
                    errors.append(f"{ctx}: provenance unknown field {field}")
                if sid not in source_ids:
                    errors.append(f"{ctx}: missing provenance source {sid}")
        if p.get("locationSource") is not None and p["locationSource"] not in source_ids:
            errors.append(f"{ctx}: invalid locationSource")
        if p.get("geometryRef") is not None:
            refs.add(p["geometryRef"])

        check_history(
            p, "costHistory", source_ids, errors, "valueMillionYen",
            lambda v: finite_number(v) and v >= 0,
            "totalProjectCostMillionYen"
        )
        check_history(
            p, "scheduleHistory", source_ids, errors, "plannedCompletionFiscalYear",
            lambda v: isinstance(v, int) and not isinstance(v, bool) and 1900 <= v <= 2200,
            "plannedCompletionFiscalYear"
        )
        check_history(
            p, "progressHistory", source_ids, errors, "progressPercent",
            lambda v: finite_number(v) and 0 <= v <= 100,
            "progressPercent"
        )

    if geo.get("type") != "FeatureCollection" or not isinstance(geo.get("features"), list):
        errors.append("GeoJSON root must be FeatureCollection")
        features = []
    else:
        features = geo["features"]
    feature_ids = set()
    for i, f in enumerate(features):
        ctx = f"geojson.features[{i}]"
        pid = f.get("properties", {}).get("projectId")
        if pid not in ids:
            errors.append(f"{ctx}: unknown projectId")
        elif pid in feature_ids:
            errors.append(f"{ctx}: duplicate project geometry")
        else:
            feature_ids.add(pid)
        check_geometry(f.get("geometry"), errors, ctx)
    if refs - feature_ids:
        errors.append("Missing GeoJSON: " + ", ".join(sorted(refs - feature_ids)))

    if errors:
        print("Data validation failed:", file=sys.stderr)
        for e in errors:
            print(" - " + e, file=sys.stderr)
        return 1
    print(f"Data validation OK: {len(projects)} projects, {len(features)} GeoJSON features, schema {data.get('schemaVersion')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
