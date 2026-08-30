# Data Schema

`public/data/projects.json` is the canonical project dataset. Phase 2 uses `schemaVersion: "2.0.0"` because project snapshots now coexist with source-linked historical observations.

## Current snapshot

The existing fields remain the current display values: `id`, `name`, `category`, `operator`, `department`, `municipalities`, `status`, `startFiscalYear`, `plannedCompletionFiscalYear`, `totalProjectCostMillionYen`, `progressPercent`, `benefitCostRatio`, `sources`, `provenance`, and `locationAccuracy`.

Project costs are normalized to **million yen**. Unknown values are `null` rather than estimated.

## History arrays

Each project has three arrays.

### `costHistory`

Stores comparable observations of **total project cost only**.

```json
{
  "asOf": "2025-08-28",
  "fiscalYear": 2025,
  "valueMillionYen": 14900,
  "sourceId": "source-r7-detail",
  "note": "optional factual note from the source"
}
```

Do not mix annual budgets, cumulative expenditure, contracts, construction cost, or land cost into `costHistory`.

### `scheduleHistory`

```json
{
  "asOf": "2025-08-28",
  "plannedCompletionFiscalYear": 2035,
  "sourceId": "source-r7-detail"
}
```

### `progressHistory`

```json
{
  "asOf": "2025-03-31",
  "progressPercent": 8.5,
  "sourceId": "source-r7-list"
}
```

Only progress figures with a comparable definition are placed in the same history. In the initial Phase 2 data, compared progress figures are project-cost-basis progress rates.

## `asOf` semantics

`asOf` is the date to which the observation applies. Prefer the explicit reference date in the source. For year-end progress, use the fiscal year-end date. If only a committee/publication date is available for a cost or completion target, use that date and explain ambiguity in `note` when material.

`source.accessed`, source publication date, `progressAsOf`, fiscal year, and history `asOf` are distinct concepts.

## Snapshot consistency

When a history array is non-empty, its latest value must equal the corresponding current snapshot:

- latest `costHistory.valueMillionYen` = `totalProjectCostMillionYen`
- latest `scheduleHistory.plannedCompletionFiscalYear` = `plannedCompletionFiscalYear`
- latest `progressHistory.progressPercent` = `progressPercent`

`scripts/validate_data.py` enforces these invariants, source resolution, ISO dates, chronological order, unique `asOf` values, ranges, and finite numbers.

## Sources and provenance

Every history entry must have a `sourceId` resolving to the same project's `sources`. History therefore remains traceable independently of the current field-level `provenance` map.

## Geometry

`public/data/projects.geojson` contains display geometry separately. Point / LineString / Polygon are supported and `properties.projectId` must match a project `id`.

`locationAccuracy` is `official | derived | approximate | unknown`. `approximate` means a representative point or approximate position derived from an official location map; it must not be interpreted as the exact construction area.
