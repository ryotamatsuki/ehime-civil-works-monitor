# Phase 2.5 — Project-Level Annual Budget Reconstruction

Phase 2.5 reconstructs FY2023–FY2026 (R5–R8) project-level budget/allocation histories from official sources without conflating different financial concepts.

## Current coverage

- Canonical projects audited: 50 / 50
- Project-specific amount confirmed: 11 projects
- FY2023 amount confirmed: 8 projects
- FY2024 amount confirmed: 11 projects
- FY2025 amount confirmed: 11 projects
- FY2026 amount confirmed: 11 projects
- 2+ fiscal years comparable under the same `basis × budgetStage × scope`: 11 projects
- 3+ fiscal years comparable under the same definition: 11 projects
- 4 fiscal years comparable under the same definition: 8 projects

Audit results that are deliberately not converted into project budgets remain explicit: `BROADER_PROGRAM_ONLY`, `SCOPE_MISMATCH`, or `SOURCE_NOT_FOUND`. Missing values are never converted to zero.

## Data file

`public/data/annual-budget-r5-r8.json`

Schema version: `2.5.0`

Each observation contains:

```json
{
  "fiscalYear": 2026,
  "asOf": "2026-04-01",
  "amountMillionYen": 814,
  "basis": "project_allocation",
  "budgetStage": "allocation",
  "scope": "project",
  "sourceId": "r8-important-proposals",
  "note": "..."
}
```

## Comparability rule

A time series is comparable only when `basis`, `budgetStage`, and `scope` all match.

For example, the national/project allocation for a road and the prefectural initial-budget amount for the same road are both useful observations, but they are not one homogeneous series and are not added together. Likewise, a supplementary increment is preserved as `supplementary`; the application does not infer a final annual total unless a source explicitly supports it.

## Audit status

- `CONFIRMED_PROJECT_BUDGET` — project-specific amount confirmed
- `PROJECT_LISTED_NO_AMOUNT` — project listed but no project-specific amount available
- `BROADER_PROGRAM_ONLY` — only a broader program or multiple-location total is available
- `SCOPE_MISMATCH` — source scope differs from the canonical project
- `SOURCE_NOT_FOUND` — baseline R5–R8 source audit did not confirm a directly attributable amount
- `NOT_APPLICABLE` — not applicable to the target period/scope

## Reproduction

```bash
npm run validate
npm run report:budget
npm test
npm run build
npm run check
```

See `docs/annual-budget-source-inventory.md` for the source inventory and locator notes.
