# Adding and Updating Projects

Phase 2.2 separates **project discovery** from **data depth**. A project may be added to the inventory before cost, schedule, progress, or historical observations are available, provided that its identity, operator, broad location, category, and primary-source basis can be justified.

Do not fabricate missing values to make an Inventory project look like a Snapshot or Enriched project. Unknown values remain `null` or empty arrays.

## 1. Decide whether the candidate is a real project

Before editing JSON, reconcile the candidate against existing records.

1. Start from a primary source: official project page, public-works evaluation material, office jurisdiction map, budget document, project overview, or equivalent.
2. Confirm that the label refers to a discrete public-works project rather than a road/river/port name, facility, district, completed structure, or map annotation.
3. Search existing project names, aliases, municipalities, and operators for duplicates.
4. If the source is an overview map or image panel, do not register labels that cannot be read or identified with sufficient confidence.
5. If the same project appears under different names across sources, keep one canonical project and document the naming relationship in `summary`, `scope`, `locationNote`, or source notes as appropriate.

The inventory is intentionally conservative: omission is preferable to a false-positive project.

## 2. Assign Data Depth

Data Depth is derived from the verified data present for the project; it is not a manually asserted quality score.

### Inventory

Use when project identity and primary-source existence are verified, but key quantitative snapshot fields remain incomplete.

Typical minimum evidence:

- canonical project name;
- category;
- operator / department where identifiable;
- municipality or municipalities;
- status when the source supports it, otherwise `unknown`;
- primary source;
- justified display location;
- descriptive `summary` / `scope` sufficient to distinguish the project.

Total project cost, completion year, progress, B/C, and history may remain unknown.

### Snapshot

Use when the project has materially useful current-state data, such as verified total cost, planned completion, progress, or equivalent project-level quantitative information, but no deeper history/enrichment sufficient for the higher tiers.

### History

Use when at least one history layer contains genuinely comparable multiple observations and the project is not already classified as Enriched.

History observations must obey the comparability rules below. A single current observation stored in a history array for provenance does not by itself constitute meaningful longitudinal monitoring.

### Enriched

Use when Phase 2.1 enrichment data materially deepens the record, for example annual budget, cumulative investment, B/C history, or documented reasons. Enriched is the deepest exclusive tier even when the same project also has Cost / Schedule / Progress history.

## 3. Add the canonical project record

1. Add the project to `public/data/projects.json` with a unique lowercase slug.
2. Normalize total project cost, when known, to **million yen**.
3. Register every source in the project-local `sources` array.
4. Link important current fields through `provenance` only when those fields are non-null and the cited source supports the value.
5. Leave unavailable quantitative fields `null`; do not estimate them from maps, construction photographs, news summaries, or arithmetic on unrelated budget figures.
6. Add empty `costHistory`, `scheduleHistory`, and `progressHistory` arrays when no comparable observations are verified.

Schema `2.2.0` permits Inventory records with incomplete snapshots. The validator still requires project/source/geometry integrity and validates any quantitative value that is present.

## 4. Add enrichment record

Every project must have a corresponding record in `public/data/enrichment.json`, even when all enrichment arrays are empty.

Only add values that satisfy the Phase 2.1 definitions:

- `annualBudgetHistory[]` — project-level annual budget/allocation observations;
- `cumulativeInvestmentHistory[]` — cumulative investment with `actual` and `planned` distinguished;
- `benefitCostHistory[]` — B/C with scope and perspective preserved;
- `documentedReasons[]` — reasons explicitly documented by a primary source.

Do not use annual budgets, cumulative expenditure, or contracts as substitutes for total project cost.

## 5. Add geometry

Add one matching feature to `public/data/projects.geojson` for every canonical project.

Supported display geometries include `Point`, `LineString`, `MultiLineString`, and supported polygonal forms in the validator/schema.

Accuracy rules:

- `official` — geometry is directly supplied as official GIS/coordinate geometry;
- `derived` — geometry is reproducibly derived from an official address or sufficiently precise official description;
- `approximate` — representative point or approximate route digitized from an official location/jurisdiction map;
- `unknown` — use only where the schema permits and the limitation is explicit.

An approximate route must not be presented as an exact alignment or construction footprint. In the UI, approximate LineStrings are intentionally differentiated from exact/official geometry.

For linear projects, use a LineString only when the route can be represented with reasonable confidence from the source. Otherwise use a representative Point rather than inventing an alignment.

## 6. History rules

### Cost

`costHistory` contains only **total project cost** observations that are definitionally comparable.

Do not compare total project cost with:

- annual budget;
- cumulative investment/expenditure;
- contract value;
- construction-only cost;
- land acquisition cost;
- one sub-section of a larger project.

### Schedule

Record the planned/target completion fiscal year stated in the source. A later completion target is not manually marked `DELAYED`; Change Detection derives it from consecutive comparable observations.

### Progress

Only place observations in one series when the underlying progress definition is comparable. Physical progress, expenditure-based progress, land acquisition progress, and other measures must not be silently mixed.

If the definition changes, keep the incompatible observation outside the comparison series or explain the limitation in `note`.

### Observation dates

Use `asOf` for the date to which the observation applies. Source publication/access date, fiscal year, committee date, and progress reference date are separate concepts. If only the publication/committee date is available, use it only when appropriate and document material ambiguity.

## 7. Notes and reasons

A `note` may describe facts supported by the cited primary source. Reasons for cost growth, schedule change, delay, or other events must not be inferred from chronology, media coverage, or model output.

`documentedReasons` is reserved for reasons explicitly stated in the source. A contextual sentence does not automatically justify a machine-derived `DELAYED` or `COST+` event.

## 8. Updating an existing project

When a newer source changes the current snapshot:

1. add the source;
2. append a new comparable history observation where appropriate;
3. update the current snapshot;
4. update `provenance` to the newest authoritative source;
5. update enrichment only if the new source contains enrichment-class information;
6. improve geometry only when the new source justifies the improvement;
7. re-run validation and coverage reporting.

Do not add persistent fields such as `isDelayed`, `costIncreased`, or `dataDepth`. Change events and Data Depth are derived by application/domain logic from the canonical data.

## 9. Inventory reconciliation workflow

When expanding from a comprehensive official overview such as an office jurisdiction map:

1. enumerate clearly identifiable candidates;
2. reconcile each candidate against the existing inventory;
3. mark existing matches rather than creating duplicates;
4. add only candidates that satisfy the minimum identity/source/location threshold;
5. record excluded or unresolved labels in an audit document when useful;
6. add deeper numbers/history only after independent source verification.

This allows broad geographic coverage without weakening the provenance standard.

## 10. Verification

Run:

```bash
npm run lint
npm test
npm run validate
python3 scripts/report_inventory.py
npm run build
```

The CI workflow runs these checks on every branch/PR. `scripts/report_inventory.py` reports project counts, exclusive Data Depth, monitoring coverage, categories, geometry types, location accuracy, and quantitative/history/enrichment coverage.

Before merging, confirm at minimum:

- project IDs are unique;
- `projects.json`, GeoJSON, and enrichment project sets agree;
- every history/enrichment `sourceId` resolves;
- latest comparable history agrees with the current snapshot where required;
- no duplicate project was introduced under an alternate name;
- approximate geometry is labelled as approximate;
- unknown values remain unknown rather than estimated;
- lint, tests, both validators, coverage report, and production build pass.

The two governing rules are: **do not invent data** and **do not make approximate geography look exact**.
