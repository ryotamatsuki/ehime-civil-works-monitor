# Change Detection

Phase 2 treats a change as a difference between two comparable, source-linked historical observations. The JSON dataset does not store manual flags such as `isDelayed` or `costIncreased`.

## Event types

`src/domain.ts` derives five event types from consecutive history entries.

- `cost_increase` (`COST+`): total project cost increased.
- `cost_decrease` (`COST−`): total project cost decreased.
- `delayed` (`DELAYED`): planned completion fiscal year moved later.
- `accelerated` (`EARLIER`): planned completion fiscal year moved earlier.
- `progress_updated` (`UPDATED`): a comparable progress percentage changed.

Equal adjacent values produce no event.

## Cost changes

For a cost change:

- `absoluteChange = current - previous` in million yen.
- `percentChange = absoluteChange / previous * 100` when the previous value is non-zero.
- when the previous cost is zero, percentage change is left undefined rather than dividing by zero.

Only total project cost may be compared. A difference caused by mixing total cost with annual budget or cumulative expenditure is a data error, not a project change.

## Schedule changes

For completion years:

- positive difference = `delayed`;
- negative difference = `accelerated`;
- zero = no schedule event.

The UI reports the factual source change only. It does not label a project as failed, wasteful, problematic, or dangerous.

## Progress updates

Progress observations are compared only when the definition is compatible. Phase 2's verified multi-period progress series use project-cost-basis progress figures. If a source uses a different concept, that observation must not be joined into the same comparison series merely because both are percentages.

## Source rules

Every event inherits the `sourceId`, date, and optional factual note from the newer history entry that generated the event. Users can follow history entries and change cards back to the primary source.

Media reports may help discover official material, but they are not used to overwrite verified project values in the initial Phase 2 dataset.

## False-positive avoidance

Before adding a historical observation, verify:

1. same project / project scope;
2. same cost semantic;
3. same progress semantic;
4. fiscal-year conversion;
5. units;
6. whether the source value is actual, target, forecast, or year-end estimate;
7. source date versus observation `asOf` date.

If comparability is uncertain, omit the comparison rather than create an alert.

## Severity

Severity is an internal presentation aid, not an administrative evaluation.

- cost change with absolute percentage change of 10% or more: `major`;
- other cost changes: `notice`;
- delay of two or more fiscal years: `major`;
- one-year delay: `notice`;
- acceleration and progress updates: `info`.

The public UI always includes explicit text labels and does not rely on color alone.

## Dashboard interpretation

- `COST+` counts projects that have at least one verified cost-increase event.
- `DELAYED` counts projects that have at least one verified delay event.
- `UPDATED / 365D` counts projects with at least one derived event whose effective date falls within 365 days of the viewer's current date.

`Recent Changes` shows the newest derived events across the currently filtered projects.
