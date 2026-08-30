# Data Schema

`public/data/projects.json` is the canonical project dataset. Phase 2.2 uses `schemaVersion: "2.2.0"`.

The schema supports both broad **Project Inventory** records and deeply monitored projects. A project does not need a known cost, completion year, or progress rate in order to be a valid Inventory record.

## Current snapshot

Core fields remain:

- `id`
- `name`
- `category` / `categoryLabel`
- `operator`
- `department`
- `municipalities`
- `status` / `statusLabel`
- `startFiscalYear`
- `plannedCompletionFiscalYear`
- `totalProjectCostMillionYen`
- `currentFiscalYearBudgetMillionYen`
- `progressPercent` / `progressAsOf`
- `benefitCostRatio`
- `lastVerified`
- `summary` / `scope`
- `geometryRef`
- `locationAccuracy` / `locationSource` / `locationNote`
- `sources`
- `provenance`

Unknown numerical or year values are `null` rather than estimated. Project costs are normalized to million yen only when the source clearly represents **total project cost**.

## Inventory records

An Inventory project may legitimately have:

```json
{
  "startFiscalYear": null,
  "plannedCompletionFiscalYear": null,
  "totalProjectCostMillionYen": null,
  "progressPercent": null,
  "benefitCostRatio": null,
  "costHistory": [],
  "scheduleHistory": [],
  "progressHistory": []
}
```

The record remains useful when project identity, category, operator/context, municipality, location, source, and summary are verified.

## Data Depth

`MonitoringLevel` is a **derived value** and is not stored redundantly in `projects.json`.

```ts
type MonitoringLevel =
  | 'inventory'
  | 'snapshot'
  | 'history'
  | 'enriched';
```

Interpretation:

- `inventory`: identity/location/source confirmed, but no monitored current numeric/year observation
- `snapshot`: at least one current monitored field is known
- `history`: at least one Cost / Schedule / Progress series has two or more comparable observations
- `enriched`: the Phase 2.1 record contains annual budget, cumulative investment, B/C, or documented reason data

The deepest available level wins. Therefore a project with multi-period history plus B/C enrichment is displayed as `ENRICHED`, not `HISTORY`.

## Categories

Phase 2.2 canonical categories are:

```text
river
coast
sabo
road
urban
agriculture
port
dam
```

`dam` was added for dam-upgrade projects that do not fit the other categories without obscuring the asset type. Do not create separate categories merely for national roads, expressways, bridges, etc.; use the broader category and project name/summary.

## Status

```text
planned
under_construction
completed
unknown
```

Partial opening does not make an entire project `completed`. Use `under_construction` and explain partial opening in `summary`, `scope`, or a source note when the project continues.

## History arrays

Each project has three arrays. Empty arrays are valid.

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

Do not mix annual budgets, cumulative expenditure/investment, contracts, construction-only cost, or land cost into `costHistory`.

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

Only progress figures with a comparable definition belong in the same time series. A single current observation is allowed but does not create a Change Event.

## `asOf` semantics

`asOf` is the date to which the observation applies. Prefer an explicit reference date in the source. For fiscal-year-end progress, use the fiscal year-end date. If only a committee/publication date is available for a cost or completion target, use that date and explain material ambiguity in `note`.

`source.accessed`, source publication date, `progressAsOf`, fiscal year, and history `asOf` are distinct concepts.

## Snapshot consistency

When a history array is non-empty, its latest value must equal the corresponding current snapshot:

- latest `costHistory.valueMillionYen` = `totalProjectCostMillionYen`
- latest `scheduleHistory.plannedCompletionFiscalYear` = `plannedCompletionFiscalYear`
- latest `progressHistory.progressPercent` = `progressPercent`

`scripts/validate_data.py` enforces these invariants, source resolution, dates, chronological order, ranges, and finite numbers.

## Sources and provenance

Every project has at least one primary/public source. Every history entry has a `sourceId` resolving to the same project's `sources`.

Phase 2.2 uses the official `えひめの土木2026 愛媛県管内図` as an Inventory seed where appropriate. It can support project identity/category/status/location context, but it must not be cited for cost/progress/completion values that are not stated in that document. Those fields require their own official source and provenance.

## Geometry

`public/data/projects.geojson` stores display geometry separately from the project metadata.

Supported geometry types:

- `Point`
- `LineString`
- `MultiLineString`
- `Polygon`

`properties.projectId` must match a canonical project `id`.

`locationAccuracy` is:

```text
official
derived
approximate
unknown
```

A route traced or simplified from an official overview map is still `approximate`, not `official`. Phase 2.2 approximate LineStrings are rendered dashed and are intended only to show corridor context. They must not be interpreted as authoritative alignment, construction limits, property boundaries, or survey geometry.

## Enrichment

Phase 2.1 enrichment remains a separate static dataset at `public/data/enrichment.json` with `enrichmentSchemaVersion: "2.1.0"`.

Its records contain:

- `annualBudgetHistory[]`
- `cumulativeInvestmentHistory[]`
- `benefitCostHistory[]`
- `documentedReasons[]`

Inventory projects may have an empty enrichment record. Empty enrichment does not make the project `ENRICHED`.

## Validation and coverage

Run:

```bash
npm run validate
python3 scripts/report_inventory.py
```

The validator checks schema/category/status/source/provenance/history/geometry consistency. `report_inventory.py` reports project count, derived Data Depth, category coverage, geometry/location accuracy, and numeric-data coverage.
