#!/usr/bin/env python3
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "public/data/projects.json"
BUDGETS = ROOT / "public/data/annual-budget-r5-r8.json"


def comparable_year_count(record):
    groups = defaultdict(set)
    for entry in record.get("observations", []):
        key = (entry.get("basis"), entry.get("budgetStage"), entry.get("scope"))
        groups[key].add(entry.get("fiscalYear"))
    return max((len(years) for years in groups.values()), default=0)


def main():
    projects = json.loads(PROJECTS.read_text(encoding="utf-8"))
    budgets = json.loads(BUDGETS.read_text(encoding="utf-8"))
    target_years = budgets["targetFiscalYears"]
    records = budgets["records"]

    by_year = {year: 0 for year in target_years}
    for record in records:
        years = {entry["fiscalYear"] for entry in record.get("observations", [])}
        for year in target_years:
            by_year[year] += int(year in years)

    comparable = [comparable_year_count(record) for record in records]
    status_counts = Counter(record["auditStatus"] for record in records)

    print(f"Canonical projects: {len(projects['projects'])}")
    print(f"Audited projects: {len(records)}")
    for year in target_years:
        print(f"FY{year} confirmed: {by_year[year]}")
    print(f"2+ year comparable (same basis/stage/scope): {sum(count >= 2 for count in comparable)}")
    print(f"3+ year comparable (same basis/stage/scope): {sum(count >= 3 for count in comparable)}")
    print(f"4-year comparable (same basis/stage/scope): {sum(count >= 4 for count in comparable)}")
    print("Audit status:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")


if __name__ == "__main__":
    main()
