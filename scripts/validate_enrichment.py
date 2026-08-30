#!/usr/bin/env python3
import json
import math
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "public/data/projects.json"
ENRICHMENT = ROOT / "public/data/enrichment.json"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
BUDGET_BASIS = {"project_allocation", "national_subsidy", "prefectural_budget"}
OBSERVATION_STATUS = {"actual", "planned"}
BC_SCOPE = {"project", "network"}
BC_PERSPECTIVE = {"whole", "remaining"}
REASON_TYPES = {"cost_change", "schedule_change", "delay_context"}


def valid_date(value):
    if not isinstance(value, str) or not DATE_RE.match(value):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def valid_url(value):
    p = urlparse(value) if isinstance(value, str) else None
    return bool(p and p.scheme == "https" and p.netloc)


def finite_nonnegative(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0


def valid_fiscal_year(value, nullable=False):
    if value is None:
        return nullable
    return isinstance(value, int) and not isinstance(value, bool) and 1900 <= value <= 2200


def validate_source(source, ctx, errors):
    if not isinstance(source, dict):
        errors.append(f"{ctx}: must be an object")
        return None
    sid = source.get("id")
    if not isinstance(sid, str) or not sid:
        errors.append(f"{ctx}: id required")
        sid = None
    for key in ("title", "publisher"):
        if not isinstance(source.get(key), str) or not source.get(key).strip():
            errors.append(f"{ctx}: {key} required")
    if not valid_url(source.get("url")):
        errors.append(f"{ctx}: invalid https URL")
    if not valid_date(source.get("accessed")):
        errors.append(f"{ctx}: invalid accessed date")
    if source.get("note") is not None and not isinstance(source.get("note"), str):
        errors.append(f"{ctx}: note must be string")
    return sid


def check_source(entry, source_ids, ctx, errors):
    sid = entry.get("sourceId")
    if not isinstance(sid, str) or sid not in source_ids:
        errors.append(f"{ctx}: sourceId {sid!r} does not resolve to record.sources")


def main():
    errors = []
    try:
        base = json.loads(BASE.read_text(encoding="utf-8"))
        enrichment = json.loads(ENRICHMENT.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: cannot parse data: {exc}", file=sys.stderr)
        return 1

    if enrichment.get("enrichmentSchemaVersion") != "2.1.0":
        errors.append("enrichmentSchemaVersion must be 2.1.0")
    if not valid_date(enrichment.get("generatedAt")):
        errors.append("generatedAt must be ISO date")
    if not isinstance(enrichment.get("dataPolicy"), str) or not enrichment.get("dataPolicy").strip():
        errors.append("dataPolicy required")

    base_projects = base.get("projects", [])
    project_ids = {project.get("id") for project in base_projects if isinstance(project, dict)}
    records = enrichment.get("records")
    if not isinstance(records, list):
        errors.append("records must be an array")
        records = []

    seen_projects = set()
    for i, record in enumerate(records):
        ctx = f"records[{i}]"
        if not isinstance(record, dict):
            errors.append(f"{ctx}: must be an object")
            continue
        pid = record.get("projectId")
        if pid not in project_ids:
            errors.append(f"{ctx}: unknown projectId {pid!r}")
        if pid in seen_projects:
            errors.append(f"{ctx}: duplicate projectId {pid!r}")
        seen_projects.add(pid)

        required_arrays = (
            "sources",
            "annualBudgetHistory",
            "cumulativeInvestmentHistory",
            "benefitCostHistory",
            "documentedReasons",
        )
        for key in required_arrays:
            if not isinstance(record.get(key), list):
                errors.append(f"{ctx}.{key}: must be an array")

        sources = record.get("sources") if isinstance(record.get("sources"), list) else []
        source_ids = set()
        for j, source in enumerate(sources):
            sid = validate_source(source, f"{ctx}.sources[{j}]", errors)
            if sid:
                if sid in source_ids:
                    errors.append(f"{ctx}.sources[{j}]: duplicate source id {sid}")
                source_ids.add(sid)

        seen_budget = set()
        for j, entry in enumerate(record.get("annualBudgetHistory", [])):
            ectx = f"{ctx}.annualBudgetHistory[{j}]"
            if not isinstance(entry, dict):
                errors.append(f"{ectx}: must be object")
                continue
            if not valid_fiscal_year(entry.get("fiscalYear")):
                errors.append(f"{ectx}: invalid fiscalYear")
            if not valid_date(entry.get("asOf")):
                errors.append(f"{ectx}: invalid asOf")
            if not finite_nonnegative(entry.get("amountMillionYen")):
                errors.append(f"{ectx}: invalid amountMillionYen")
            if entry.get("basis") not in BUDGET_BASIS:
                errors.append(f"{ectx}: invalid basis")
            check_source(entry, source_ids, ectx, errors)
            identity = (entry.get("fiscalYear"), entry.get("basis"))
            if identity in seen_budget:
                errors.append(f"{ectx}: duplicate fiscalYear/basis")
            seen_budget.add(identity)

        investment = record.get("cumulativeInvestmentHistory", [])
        seen_investment = set()
        investment_keys = []
        for j, entry in enumerate(investment):
            ectx = f"{ctx}.cumulativeInvestmentHistory[{j}]"
            if not isinstance(entry, dict):
                errors.append(f"{ectx}: must be object")
                continue
            if not valid_fiscal_year(entry.get("fiscalYear")):
                errors.append(f"{ectx}: invalid fiscalYear")
            if not valid_date(entry.get("asOf")):
                errors.append(f"{ectx}: invalid asOf")
            if not finite_nonnegative(entry.get("amountMillionYen")):
                errors.append(f"{ectx}: invalid amountMillionYen")
            if entry.get("status") not in OBSERVATION_STATUS:
                errors.append(f"{ectx}: invalid status")
            check_source(entry, source_ids, ectx, errors)
            identity = (entry.get("fiscalYear"), entry.get("asOf"))
            if identity in seen_investment:
                errors.append(f"{ectx}: duplicate fiscalYear/asOf")
            seen_investment.add(identity)
            investment_keys.append(identity)
        if investment_keys != sorted(investment_keys):
            errors.append(f"{ctx}.cumulativeInvestmentHistory: must be ordered by fiscalYear/asOf")

        seen_bc = set()
        for j, entry in enumerate(record.get("benefitCostHistory", [])):
            ectx = f"{ctx}.benefitCostHistory[{j}]"
            if not isinstance(entry, dict):
                errors.append(f"{ectx}: must be object")
                continue
            if not valid_fiscal_year(entry.get("fiscalYear"), nullable=True):
                errors.append(f"{ectx}: invalid fiscalYear")
            if not valid_date(entry.get("asOf")):
                errors.append(f"{ectx}: invalid asOf")
            if not finite_nonnegative(entry.get("value")):
                errors.append(f"{ectx}: invalid value")
            if entry.get("scope") not in BC_SCOPE:
                errors.append(f"{ectx}: invalid scope")
            if entry.get("perspective") not in BC_PERSPECTIVE:
                errors.append(f"{ectx}: invalid perspective")
            check_source(entry, source_ids, ectx, errors)
            identity = (entry.get("asOf"), entry.get("scope"), entry.get("perspective"))
            if identity in seen_bc:
                errors.append(f"{ectx}: duplicate asOf/scope/perspective")
            seen_bc.add(identity)

        for j, entry in enumerate(record.get("documentedReasons", [])):
            ectx = f"{ctx}.documentedReasons[{j}]"
            if not isinstance(entry, dict):
                errors.append(f"{ectx}: must be object")
                continue
            if not valid_date(entry.get("effectiveDate")):
                errors.append(f"{ectx}: invalid effectiveDate")
            if entry.get("type") not in REASON_TYPES:
                errors.append(f"{ectx}: invalid type")
            if not isinstance(entry.get("summary"), str) or not entry.get("summary").strip():
                errors.append(f"{ectx}: summary required")
            check_source(entry, source_ids, ectx, errors)

        for key in required_arrays[1:]:
            for j, entry in enumerate(record.get(key, [])):
                if isinstance(entry, dict) and entry.get("note") is not None and not isinstance(entry.get("note"), str):
                    errors.append(f"{ctx}.{key}[{j}]: note must be string")

    missing = project_ids - seen_projects
    if missing:
        errors.append("missing enrichment records for current projects: " + ", ".join(sorted(missing)))

    if errors:
        print("Enrichment validation failed:", file=sys.stderr)
        for error in errors:
            print(" - " + error, file=sys.stderr)
        return 1

    budget_count = sum(bool(record["annualBudgetHistory"]) for record in records)
    bc_multi = sum(len({entry["asOf"] for entry in record["benefitCostHistory"]}) >= 2 for record in records)
    reason_count = sum(bool(record["documentedReasons"]) for record in records)
    print(
        f"Enrichment validation OK: {len(records)} records, "
        f"annual budgets {budget_count} projects, multi-period B/C {bc_multi} projects, "
        f"documented reasons {reason_count} projects, schema {enrichment.get('enrichmentSchemaVersion')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
