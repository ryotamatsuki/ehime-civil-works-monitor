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
BUDGETS = ROOT / "public/data/annual-budget-r5-r8.json"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TARGET_YEARS = [2023, 2024, 2025, 2026]
BASIS = {"project_allocation", "national_subsidy", "prefectural_budget"}
STAGES = {"initial", "supplementary", "final", "allocation", "unknown"}
AUDIT_STATUS = {
    "CONFIRMED_PROJECT_BUDGET",
    "PROJECT_LISTED_NO_AMOUNT",
    "BROADER_PROGRAM_ONLY",
    "SCOPE_MISMATCH",
    "SOURCE_NOT_FOUND",
    "NOT_APPLICABLE",
}


def valid_date(value):
    if not isinstance(value, str) or not DATE_RE.match(value):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def valid_url(value):
    parsed = urlparse(value) if isinstance(value, str) else None
    return bool(parsed and parsed.scheme == "https" and parsed.netloc)


def finite_nonnegative(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0


def main():
    errors = []
    try:
        projects = json.loads(PROJECTS.read_text(encoding="utf-8"))
        budgets = json.loads(BUDGETS.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: cannot parse annual budget data: {exc}", file=sys.stderr)
        return 1

    if budgets.get("schemaVersion") != "2.5.0":
        errors.append("schemaVersion must be 2.5.0")
    if not valid_date(budgets.get("generatedAt")):
        errors.append("generatedAt must be ISO date")
    if budgets.get("targetFiscalYears") != TARGET_YEARS:
        errors.append(f"targetFiscalYears must be {TARGET_YEARS}")
    if not isinstance(budgets.get("dataPolicy"), str) or not budgets.get("dataPolicy", "").strip():
        errors.append("dataPolicy required")
    if budgets.get("defaultUnresolvedStatus") not in AUDIT_STATUS:
        errors.append("invalid defaultUnresolvedStatus")
    if not isinstance(budgets.get("defaultUnresolvedNote"), str) or not budgets.get("defaultUnresolvedNote", "").strip():
        errors.append("defaultUnresolvedNote required")

    project_ids = {
        project.get("id") for project in projects.get("projects", [])
        if isinstance(project, dict) and isinstance(project.get("id"), str)
    }

    source_ids = set()
    for index, source in enumerate(budgets.get("sources", [])):
        ctx = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{ctx}: must be object")
            continue
        sid = source.get("id")
        if not isinstance(sid, str) or not sid:
            errors.append(f"{ctx}: id required")
        elif sid in source_ids:
            errors.append(f"{ctx}: duplicate id {sid}")
        else:
            source_ids.add(sid)
        for key in ("title", "publisher"):
            if not isinstance(source.get(key), str) or not source.get(key, "").strip():
                errors.append(f"{ctx}: {key} required")
        if not valid_url(source.get("url")):
            errors.append(f"{ctx}: invalid https URL")
        if not valid_date(source.get("accessed")):
            errors.append(f"{ctx}: invalid accessed")
        if source.get("fiscalYear") not in TARGET_YEARS:
            errors.append(f"{ctx}: fiscalYear outside target")
        if source.get("budgetStage") not in STAGES:
            errors.append(f"{ctx}: invalid budgetStage")
        for key in ("locator", "note"):
            if source.get(key) is not None and not isinstance(source.get(key), str):
                errors.append(f"{ctx}: {key} must be string")

    records = budgets.get("records")
    if not isinstance(records, list):
        errors.append("records must be an array")
        records = []

    seen_projects = set()
    for index, record in enumerate(records):
        ctx = f"records[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{ctx}: must be object")
            continue
        pid = record.get("projectId")
        if pid not in project_ids:
            errors.append(f"{ctx}: unknown projectId {pid!r}")
        if pid in seen_projects:
            errors.append(f"{ctx}: duplicate projectId {pid!r}")
        seen_projects.add(pid)
        status = record.get("auditStatus")
        if status not in AUDIT_STATUS:
            errors.append(f"{ctx}: invalid auditStatus")
        observations = record.get("observations")
        if not isinstance(observations, list):
            errors.append(f"{ctx}: observations must be an array")
            observations = []
        if status == "CONFIRMED_PROJECT_BUDGET" and not observations:
            errors.append(f"{ctx}: confirmed project requires observations")
        if status != "CONFIRMED_PROJECT_BUDGET" and observations:
            errors.append(f"{ctx}: unresolved status must not contain observations")
        if status != "CONFIRMED_PROJECT_BUDGET" and not isinstance(record.get("note"), str):
            errors.append(f"{ctx}: unresolved audit record requires note")
        if record.get("note") is not None and not isinstance(record.get("note"), str):
            errors.append(f"{ctx}: note must be string")

        identities = set()
        for j, entry in enumerate(observations):
            ectx = f"{ctx}.observations[{j}]"
            if not isinstance(entry, dict):
                errors.append(f"{ectx}: must be object")
                continue
            fiscal_year = entry.get("fiscalYear")
            if fiscal_year not in TARGET_YEARS:
                errors.append(f"{ectx}: fiscalYear outside target")
            if not valid_date(entry.get("asOf")):
                errors.append(f"{ectx}: invalid asOf")
            if not finite_nonnegative(entry.get("amountMillionYen")):
                errors.append(f"{ectx}: invalid amountMillionYen")
            if entry.get("basis") not in BASIS:
                errors.append(f"{ectx}: invalid basis")
            if entry.get("budgetStage") not in STAGES:
                errors.append(f"{ectx}: invalid budgetStage")
            if entry.get("scope") != "project":
                errors.append(f"{ectx}: scope must be project")
            if entry.get("sourceId") not in source_ids:
                errors.append(f"{ectx}: sourceId does not resolve")
            if entry.get("note") is not None and not isinstance(entry.get("note"), str):
                errors.append(f"{ectx}: note must be string")
            identity = (
                fiscal_year,
                entry.get("budgetStage"),
                entry.get("basis"),
                entry.get("scope"),
                entry.get("sourceId"),
            )
            if identity in identities:
                errors.append(f"{ectx}: duplicate observation identity")
            identities.add(identity)

    missing = project_ids - seen_projects
    extra = seen_projects - project_ids
    if missing:
        errors.append("missing audit records: " + ", ".join(sorted(missing)))
    if extra:
        errors.append("unknown audit records: " + ", ".join(sorted(extra)))

    if errors:
        print("Annual budget validation failed:", file=sys.stderr)
        for error in errors:
            print(" - " + error, file=sys.stderr)
        return 1

    confirmed = sum(1 for record in records if record.get("auditStatus") == "CONFIRMED_PROJECT_BUDGET")
    unresolved = len(records) - confirmed
    print(
        f"Annual budget validation OK: {len(project_ids)} canonical projects audited, "
        f"{confirmed} confirmed project budgets, {unresolved} unresolved/withheld by audit controls, "
        f"schema {budgets.get('schemaVersion')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
