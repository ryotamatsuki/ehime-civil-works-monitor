# Phase 2.4 — Visual System & UX Redesign

Phase 2.4 changes presentation, information hierarchy and map interaction without changing the canonical project data model.

## Design direction

The site is treated as an **Infrastructure Observatory** rather than a conventional administrative information page. The reference site `JAPAN CIVIL WORKS MONITOR` informed the emphasis on map-first navigation, telemetry-style metrics and fast project scanning, but the visual system is independently implemented.

The Ehime design language uses:

- graphite / technical navy as the primary interface frame
- off-white data surfaces
- teal as the main interaction and provenance accent
- muted amber for cost increases
- muted red for schedule delays
- tabular numerals and small monospace labels for telemetry
- thin technical-rule borders rather than rounded dashboard cards

## Home hierarchy

The first screen is now ordered as:

1. compact project statement
2. telemetry strip
3. filter + large map workspace
4. recent detected changes
5. full project inventory

The map therefore appears before the change feed and project card catalogue.

## Map encoding

Marker appearance carries more information without changing the underlying geometry:

- marker fill = project category
- smaller marker = Inventory depth
- larger marker = Enriched depth
- amber outer ring = COST+ history exists
- muted-red outer ring = DELAYED history exists when no COST+ ring is present

Approximate route geometry remains visually distinct and continues to mean approximate corridor only.

## Project detail hierarchy

Project detail pages now expose the three main operational values immediately below the title:

- COST
- COMPLETION
- PROGRESS

If a comparable change event exists, the current KPI also displays its latest change context. This is presentation-only; change events are still derived from the existing history model.

The remaining information hierarchy is:

1. project identity / municipality / operator / verification date
2. KPI strip
3. map + metadata
4. change summary
5. history timeline
6. scope
7. primary sources

## History presentation

Cost, schedule and progress histories retain their existing source-linked data but are presented as technical timelines with nodes, dates, current values and deltas. No historical values are added or inferred by the redesign.

## Responsive behavior

Desktop uses a filter rail beside a large map. Tablet collapses project and history grids progressively. Mobile uses a single-column map-first layout, compact telemetry and a vertically stacked filter interface.

## Data integrity

Phase 2.4 does not change:

- project IDs
- data-depth derivation
- cost / schedule / progress histories
- change-detection semantics
- B/C or enrichment data
- source/provenance rules
- approximate geometry semantics

The redesign must therefore pass the same lint, tests, validators and static build used by Phase 2.3.
