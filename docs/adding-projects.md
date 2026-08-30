# Adding and Updating Projects

1. Secure primary sources from the project operator: official project pages, public-works evaluation material, budget documents, or equivalent. Unknown values stay `null`.
2. Add the project to `public/data/projects.json` with a unique slug. Normalize total project cost to million yen.
3. Register every source in `sources` and link current important fields through `provenance`.
4. Add `costHistory`, `scheduleHistory`, and `progressHistory`. An empty array is valid when no comparable historical observation is verified.
5. If an older official source is found, add it to `sources` before adding a history entry. Every history entry must resolve its `sourceId`.
6. Keep history arrays in ascending `asOf` order. The latest history value must match the current snapshot.
7. Add a geometry to `projects.geojson` only when location can be justified. Official GIS geometry is `official`, geometry derived from an official address/description is `derived`, and a representative point from an official location map is `approximate`.
8. Run `npm run validate`, `npm run lint`, `npm test`, and `npm run build`.

## History rules

### Cost

`costHistory` contains only **total project cost** observations. Do not compare it with annual budget, cumulative expenditure, contract value, construction-only cost, or land cost.

### Schedule

Record the planned/target completion fiscal year as stated in the source. A later target is not manually flagged as delayed; Change Detection derives that event from consecutive observations.

### Progress

Only place observations in the same series if the underlying progress definition is comparable. If a source changes the definition, do not create a false time-series comparison; document the issue in `note` or leave the historical series incomplete.

## Notes and reasons

A `note` may state a reason only when the official source explicitly supports it. Do not infer reasons from chronology, media coverage, or model output.

## Updating current values

When a newer source changes the current snapshot:

1. add the source;
2. append the new history observation;
3. update the current snapshot;
4. update `provenance` to the newest authoritative source;
5. validate.

Do not add fields such as `isDelayed` or `costIncreased`. Those states are derived from history by `src/domain.ts`.

The most important rules are to avoid invented history and to avoid presenting approximate geometry as an exact construction footprint.
