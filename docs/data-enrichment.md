# Phase 2.1 Data Enrichment

Phase 2.1 adds a second, source-traceable data layer to the Phase 2 project/change model. The goal is to distinguish a project's total cost from annual allocations and cumulative investment, preserve B/C calculation scope, and record only reasons explicitly stated in primary sources.

## Files

- `public/data/projects.json` — Phase 2 canonical project snapshot/history (`2.0.0`)
- `public/data/enrichment.json` — Phase 2.1 financial/evaluation enrichment (`2.1.0`)
- `scripts/validate_enrichment.py` — enrichment schema/data-integrity validator

The separate enrichment file avoids changing the meaning of `totalProjectCostMillionYen` or the Phase 2 change-detection histories.

## Annual budget

`annualBudgetHistory[]` stores an amount tied to one fiscal year and an explicit basis.

```json
{
  "fiscalYear": 2025,
  "asOf": "2025-04-01",
  "amountMillionYen": 340,
  "basis": "project_allocation",
  "sourceId": "enrichment-r7-budget"
}
```

Allowed `basis` values:

- `project_allocation` — a source explicitly allocates an amount to the named project
- `national_subsidy` — a project-specific national subsidy amount
- `prefectural_budget` — a project-specific prefectural budget amount

These values are never compared directly with total project cost.

## Cumulative investment

`cumulativeInvestmentHistory[]` stores the investment amount accumulated or expected by a stated fiscal-year endpoint.

```json
{
  "fiscalYear": 2025,
  "asOf": "2025-08-28",
  "amountMillionYen": 9670,
  "status": "planned",
  "sourceId": "enrichment-r7-review"
}
```

`status` is essential:

- `actual` — the source reports a fiscal-year endpoint that has already passed at the source's observation date
- `planned` — the source reports an end-of-fiscal-year amount before that fiscal year has ended

For the FY2025 Ozu West Road and Yohiru Road review sheets, the detailed review sheets label the figures as `R7末投資事業費`, while the consolidated FY2025 list uses a column headed `R6年度までの事業費`. Phase 2.1 preserves the detailed-sheet wording, labels the figures `planned`, and records the discrepancy in `note`. It does not silently reinterpret them as FY2024 actuals.

## B/C history

A B/C value is only meaningful with its calculation scope and perspective.

```json
{
  "fiscalYear": 2025,
  "asOf": "2025-08-28",
  "value": 0.53,
  "scope": "project",
  "perspective": "whole",
  "sourceId": "enrichment-r7-review"
}
```

`scope`:

- `project` — the named project only
- `network` — a wider network explicitly used by the source

`perspective`:

- `whole` — whole-project B/C
- `remaining` — remaining-project B/C

The UI therefore does not plot `0.53` for Yohiru Road against the `1.09` network-wide value as if they were the same metric.

## Documented reasons

`documentedReasons[]` stores only statements supported by a primary source.

Types:

- `cost_change`
- `schedule_change`
- `delay_context`

A `delay_context` can be shown even when there is no comparable earlier completion-year observation. For example, the FY2025 Kobutani River review says land acquisition difficulty delayed the project, but the current dataset does not have a prior official completion-year value. The site therefore shows the documented delay context without deriving a `DELAYED` event.

No reason is inferred from cost changes, schedule differences, construction conditions, news reports, or AI-generated explanations.

## Current Phase 2.1 coverage

The first enrichment pass covers all 10 current projects.

- Cumulative investment: 10 / 10 projects
- B/C observation: 10 / 10 projects
- Project-specific annual budget/allocation: 3 projects where a directly comparable primary-source amount was confirmed
- Multi-period B/C: Ozu West Road, Yohiru Road, JR Matsuyama grade separation
- Explicit cost/schedule/delay reasons: projects where the source actually states the reason

Empty arrays are valid and preferable to invented values.

## False-positive controls

Do not:

1. compare annual budget with total project cost as a cost change;
2. treat a planned fiscal-year-end investment amount as actual;
3. mix project B/C with network B/C;
4. mix whole-project B/C with remaining-project B/C;
5. derive a delay event from prose alone when no previous completion-year value exists;
6. infer causes that are not stated in the primary source.

## Expansion to past evaluation projects

After current-project enrichment, the next data-expansion unit is an evaluation cohort, not an arbitrary list of projects.

Recommended order:

1. FY2025 evaluation cohort: reuse the existing source format and ingest high-information projects first;
2. FY2024 and FY2023 cohorts;
3. older recurring projects with multiple comparable evaluations;
4. add/verify geometry only after project identity and historical continuity are resolved.

Before adding a past project to the map, verify that changes in project name, route, scope, scheme, or evaluation methodology do not create a false historical series.

The same Phase 2.1 enrichment schema can be used for every added project; no backend or database is required.
