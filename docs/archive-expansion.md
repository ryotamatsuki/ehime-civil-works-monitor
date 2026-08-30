# Past Evaluation Cohort Expansion

Phase 2.1 first deepens the original FY2025 10-project dataset and then starts expanding the project population by evaluation cohort.

## First expansion: FY2024 cohort

The first two added projects are:

1. `sanaki-widening` — 道路改築事業（国道378号 三秋拡幅）
2. `nishimachi-nakamura-street` — 都市計画街路事業（西町中村線）

Both are from the FY2024 (令和6年度) Ehime Public Works Evaluation Committee cohort.

### Sanaki widening

Current FY2024 primary-source observation:

- start: FY1995
- planned completion: FY2027
- total project cost: 6,160 million yen
- FY2023-end cumulative investment: 4,300 million yen
- progress: 69.8%
- whole-project B/C: 1.13
- remaining-project B/C: 8.04

No older cost/schedule observation was inserted in the first pass unless a comparable primary-source observation could be tied to a sufficiently clear evaluation date and definition.

### Nishimachi–Nakamura street

The FY2014, FY2019 and FY2024 evaluation records provide a usable multi-period series.

- total project cost: 3,602.210 → 5,470.864 → 7,787 million yen
- planned completion: FY2019 → FY2024 → FY2029
- progress: 43.6% → 56.0% → 82.0%
- whole-project B/C: 1.10 → 1.62 → 1.01
- remaining-project B/C: 2.22 → 4.54 → 8.09
- FY2023-end cumulative investment: 6,388 million yen

The FY2019 source explicitly attributes the earlier scope/cost change to extension of the starting-side section and the schedule change to large-property land acquisition and construction-schedule review. These are stored as documented reasons, not AI-inferred explanations.

## Geometry

Both new projects are represented by `locationAccuracy: approximate` points. The points are search/navigation aids only and do not represent the official road alignment or construction footprint.

## Expansion rule

Future additions should continue cohort-by-cohort. Before a past project enters the canonical map dataset, verify:

- project identity across evaluation years;
- total-cost definition;
- completion-year definition;
- progress definition;
- B/C scope and perspective;
- source date / observation date;
- approximate or official geometry provenance.

An empty history is preferable to a false longitudinal series.
