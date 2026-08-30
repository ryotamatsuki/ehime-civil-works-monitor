# Phase 2.2 Inventory Coverage

## Seed source

Phase 2.2 uses the official Ehime Prefecture map **「えひめの土木2026 愛媛県管内図」** as the broad inventory seed:

- https://www.pref.ehime.jp/uploaded/life/149017_306429_misc.pdf
- reference fiscal year: FY2026 / 令和8年度
- access/verification date: 2026-08-31

The map is used to identify projects, broad status/category context, and approximate location. It is **not** used as a source for total project cost, completion year, or progress unless those values are explicitly stated in another project-specific official source.

## Numbered photo-panel audit

The map contains 26 clearly visible numbered photo panels: 1–13 and 15–27. A #14 photo card was not identifiable on the supplied map, so no project is invented for that number.

Six panels reconcile to projects that already existed in the canonical dataset and therefore keep their existing IDs:

- 西町中村線
- JR松山駅付近連続立体交差事業
- 国道197号 夜昼道路
- 宇和島港 港湾改修事業 — reconciled with the existing 大浦地区 record as a broader/narrower relationship; numeric histories are not merged across scope
- 成碆海岸 津波対策緊急事業
- 国道378号 三秋拡幅

The remaining 20 clearly identified photo-panel projects were added as new inventory/snapshot records after checking project identity against additional official sources where available.

## Additional map-only projects

Seven high-confidence projects shown on the main map were also added:

- 国道11号 川之江三島バイパス
- 国道11号 新居浜バイパス
- 国道11号 小松バイパス
- 国道197号 八幡浜道路
- 国道56号 宿毛内海道路（御荘～内海）
- 国道33号 松山外環状道路 インター東線
- 野村ダム改良事業

The one-page map also contains smaller labels. Labels that could not be read and reconciled with sufficient confidence were not turned into production projects. They remain future research candidates rather than guessed records.

## Reconciliation result

For the high-confidence candidate set used in this release:

| Item | Count |
| --- | ---: |
| Numbered photo-panel projects identified | 26 |
| Additional high-confidence map-only projects | 7 |
| Candidate set | 33 |
| Existing canonical matches | 6 |
| Newly added | 27 |
| Production exclusions within the verified candidate set | 0 |
| Canonical projects after Phase 2.2 | 50 |

This count deliberately does not claim that every tiny label on the cartographic sheet has been resolved. Coverage should grow by verification, not by treating ambiguous map text as a project identity.

## Data Depth

`MonitoringLevel` is derived from the data and is not redundantly stored in JSON.

- `inventory`: project identity/location/source confirmed, but no monitored numeric snapshot
- `snapshot`: at least one monitored current field is known
- `history`: comparable multi-period Cost / Schedule / Progress history exists
- `enriched`: Phase 2.1 annual-budget, cumulative-investment, B/C, or documented-reason data exists

Exclusive distribution after this release:

| Data Depth | Projects |
| --- | ---: |
| Inventory | 17 |
| Snapshot | 11 |
| History | 0 |
| Enriched | 22 |
| **Total** | **50** |

`History+` in the UI includes History and Enriched projects, so the current `History+` count is 22. `Monitored` means Snapshot / History / Enriched and is currently 33.

A project can contain multi-period history and also be classified as `enriched`; the exclusive level intentionally reports the deepest layer available.

## Category distribution

| Category | Projects |
| --- | ---: |
| road | 16 |
| sabo | 13 |
| river | 8 |
| port | 4 |
| urban | 4 |
| agriculture | 2 |
| coast | 2 |
| dam | 1 |

`dam` was added as a first-class category because 野村ダム改良事業 does not fit the existing categories without obscuring the asset type.

## Geometry coverage

| Geometry | Count |
| --- | ---: |
| Point | 40 |
| LineString | 10 |

Location accuracy:

| Accuracy | Count |
| --- | ---: |
| approximate | 49 |
| derived | 1 |
| official | 0 |

All Phase 2.2 route LineStrings are intentionally `approximate`. They provide corridor context only and must not be interpreted as official road alignment, land-take, or construction limits. The map UI renders approximate route geometry with a dashed style.

## Numeric/source coverage

The reproducible report from `scripts/report_inventory.py` gives:

| Field | Projects |
| --- | ---: |
| Known total project cost | 32 |
| Known completion year | 22 |
| Known progress | 29 |
| Any Cost History observation | 30 |
| Comparable Cost History (2+ observations) | 7 |
| Any Schedule History observation | 21 |
| Comparable Schedule History (2+ observations) | 7 |
| Any Progress History observation | 29 |
| Comparable Progress History (2+ observations) | 5 |
| Annual Budget enrichment | 3 |
| Cumulative Investment enrichment | 21 |
| B/C enrichment | 22 |
| Documented Reasons | 11 |

Unknown values remain `null` or empty arrays. An Inventory project is therefore a valid record rather than an incomplete snapshot that must be artificially filled.

## False-positive controls

Phase 2.2 applies the following reconciliation rules:

1. A broader port/river/road label is not automatically merged with a narrower district/work package.
2. A completed or partially opened route is not assigned `progressPercent: 100` unless an official source explicitly provides that metric.
3. FY budget/allocation is never used as total project cost.
4. A route copied approximately from a map is never labelled `official` geometry.
5. Similar project names are not auto-merged. The validator emits a normalized-name warning, leaving reconciliation to source review.
6. A single current observation can create Snapshot data but cannot create a change event; Change Detection still requires comparable observations.

## Reproducibility

Run:

```bash
npm run validate
python3 scripts/report_inventory.py
npm test
npm run build
```

CI runs the inventory report on every branch/PR so project count, data-depth distribution, category coverage, geometry coverage, and numeric coverage can be inspected from the workflow log.
