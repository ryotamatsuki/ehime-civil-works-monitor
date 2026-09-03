# Project Inventory Coverage

最終更新: 2026-09-03 / Phase 2.6

## Current canonical population

Phase 2.6では、従来の50件を「公式に選定された主要50事業」とは扱わず、公式資料横断で独立した公共土木Projectを再探索した。

- Phase 2.5 baseline: 50
- Phase 2.6 new canonical projects: 59
- Current runtime canonical inventory: **109**

追加59件の内訳:

- road: 50
- sabo: 9

詳細なsource-family audit、候補reconciliation、除外ルールは [`comprehensive-project-inventory-audit.md`](comprehensive-project-inventory-audit.md) を参照。

## Population seed and expansion logic

### Historical baseline

Phase 2.2では「えひめの土木2026 愛媛県管内図」を主要なinventory seedとし、公共事業評価cohort等と合わせて50件まで拡張した。ただし、これは全土木事業の母集団ではなく、当時高確度で同定できた集合である。

### Phase 2.6

Phase 2.6では特に次を追加探索した。

1. 道路の整備に関するプログラム2018–2027 Vol.8
2. R2–R7公共事業評価結果とR7第2回審議案件
3. 地方局・土木事務所の主要事業・管内事業
4. R8当初・6月・9月補正資料
5. 国土交通省・四国地方整備局の県内主要事業
6. 発注見通し（Project discoveryのみ）

工事契約、測量・設計業務、broader route/river label、完成施設名は、独立Project identityを別一次資料で確認できない限りcanonical化しない。

## Category projection

| Category | Projects |
| --- | ---: |
| road | 66 |
| sabo | 22 |
| river | 8 |
| port | 4 |
| urban | 4 |
| agriculture | 2 |
| coast | 2 |
| dam | 1 |
| **Total** | **109** |

## Data Depth

Phase 2.6追加59件はすべて公式資料から少なくとも事業開始年度等のcurrent-state fieldを持つため、現行domain ruleではSnapshotに分類される。

Baseline 50のexclusive Data DepthはPhase 2.3終了時点で Inventory 4 / Snapshot 18 / History 0 / Enriched 28。

Phase 2.6 projection:

| Data Depth | Projects |
| --- | ---: |
| Inventory | 4 |
| Snapshot | 77 |
| History | 0 |
| Enriched | 28 |
| **Total** | **109** |

`History+`はHistory + Enrichedで28。Monitoredは105。

## Geometry

Phase 2.6追加59件はすべて `locationAccuracy: approximate` のrepresentative Pointで表示する。公式事業資料の市町・地区文脈から検索・俯瞰用に作成したもので、道路線形、砂防施設位置、施工区域、用地境界を意味しない。

既存geometryを変更せず、runtime unionで59 Pointを追加する。

## Coverage assessment

- road: high
- sabo: high
- river: medium
- port: medium
- coast: medium
- urban: medium
- dam: high
- agriculture: medium

道路はstructured active-project listを統合したため相対的に網羅性が高い。河川・港湾・海岸・都市は、地方局ページのbroader labelから全active projectを一意に分解できない領域が残るため、道路と同程度の網羅性は主張しない。

## False-positive controls

1. broader project / district / work packageを自動mergeしない。
2. 工事・業務契約をcanonical Projectにしない。
3. 年度予算・契約額・累計投資を全体事業費に読み替えない。
4. 完成年度が一次資料で確定しない場合はnull。
5. approximate geometryをofficialと表示しない。
6. Similar namesはvalidatorで検査し、人手reconciliationを残す。
7. Phase 2.6追加案件のR5–R8年度予算は未監査なら `SOURCE_NOT_FOUND`。0円を意味しない。

## Reproducibility

```bash
npm run lint
npm test
npm run validate
npm run report:inventory
npm run report:budget
npm run build
npm run check
```
