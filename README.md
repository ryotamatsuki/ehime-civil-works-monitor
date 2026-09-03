# Ehime Civil Works Monitor

愛媛県内の公共土木事業を、地図・一次情報源・現在値・履歴・変更・年度予算から確認するための非公式Web GISです。

公開サイト: https://ryotamatsuki.github.io/ehime-civil-works-monitor/

## Data model

**Project Inventory → Current Snapshot → History → Change Detection → Enrichment → Primary Sources** の段階構造です。

- **Inventory**: 独立した事業identity、operator/所管、市町、概略位置、一次資料を確認
- **Snapshot**: 総事業費、事業期間、進捗、B/C等のcurrent-state fieldを確認
- **History**: 同一定義で比較できる複数時点の値
- **Change Detection**: `COST+`, `COST−`, `DELAYED`, `EARLIER`, `UPDATED` を履歴差分から導出
- **Enrichment**: 年度予算、累計投資、B/C history、一次資料に明記された増額・延期事情

未確認値は推測せず `null` または空配列とします。

## Phase 2.7A-2 — Reconciled Canonical Expansion

Phase 2.7A / 2.7A-2では、Phase 2.6の109件を正しい全母集団とは仮定せず、農業農村整備、林業・治山・林道、漁港、河川、港湾・海岸およびH29～R8公共事業評価を重点的に再調査しました。

Round 1 / Round 2候補について、既存canonicalとの一致、Work Package、Program、Asset、completed historical、市町単独、identity/scope conflictを除去し、公式一次資料から独立Projectとして確認できたA/B候補だけをcanonicalへ追加しています。

- Phase 2.6 runtime canonical: **109 projects**
- Phase 2.7 new reconciled projects: **60 projects**
- runtime canonical inventory: **169 projects**

Phase 2.7追加60件の内訳:

| Category | New |
| --- | ---: |
| agriculture | 7 |
| forestry | 20 |
| fishing-port | 3 |
| river | 24 |
| sabo | 5 |
| road | 1 |
| **Total** | **60** |

Round 1の「広域河川改修事業（二級河川 渦井川・室川・界谷川・金剛院谷川）」は、既存canonicalの「二級河川 界谷川 広域河川改修事業」と親子・複合scopeの関係が未解決であるため、重複リスクを避けてHoldとしています。

詳細: [`docs/phase27a2-canonical-expansion.md`](docs/phase27a2-canonical-expansion.md)

### Current category coverage

| Category | Projects |
| --- | ---: |
| road | 67 |
| sabo | 27 |
| river | 32 |
| port | 4 |
| urban | 4 |
| agriculture | 9 |
| coast | 2 |
| dam | 1 |
| forestry | 20 |
| fishing-port | 3 |
| **Total** | **169** |

### Data Depth projection

Phase 2.7追加60件は、identity/operator/municipality/current primary sourceを確認したInventoryとして追加し、未確認の総事業費、完成年度、進捗率、年度予算等を推測していません。

| Data Depth | Projects |
| --- | ---: |
| Inventory | 64 |
| Snapshot | 77 |
| History | 0 |
| Enriched | 28 |
| **Total** | **169** |

`History+`は28、Monitoredは105です。Inventory追加により掲載母集団は広がりましたが、数値監視が済んでいない案件をSnapshotへ水増ししていません。

### Phase 2.7 overlay

既存109件のJSON/history/年度予算観測を回帰させないため、Phase 2.7追加母集団は `public/data/phase27-inventory.json` に分離しています。

runtimeでは `src/phase26-bootstrap.ts` がPhase 2.6とPhase 2.7のoverlayを順次mergeし、

- projects
- GeoJSON
- enrichment
- annual-budget audit

を169件のcanonical unionとして読み込みます。静的detail route生成、validator、inventory reportも同じ169件を検証します。

Phase 2.7追加60件のgeometryはすべて `locationAccuracy: approximate` の検索・俯瞰用representative Pointです。公式の施工区域、河川改修区間、林道線形、治山施設位置、漁港施設位置等を意味しません。

## Phase 2.6 — Comprehensive Project Inventory Expansion

Phase 2.6では、従来50件を「愛媛県の主要50事業」という公式母集団とは扱わず、公式資料横断で独立Projectをreconcileしました。

- baseline: 50 projects
- new road projects: 50
- new sabo projects: 9
- Phase 2.6 runtime canonical: **109 projects**

主なstructured source:

- 愛媛県「道路の整備に関するプログラム2018～2027 Vol.8」対象路線一覧表
- 令和7年度 愛媛県公共事業評価委員会 第2回審議対象事業一覧表

さらに「えひめの土木」過年度版、地方局・土木事務所、R2–R8公共事業評価、R8予算、国土交通省・四国地方整備局、発注見通しをdiscovery/reconciliation sourceとして監査しています。

工事契約1件、設計・測量業務、施設名、broader route/river labelは、それだけではcanonical Projectにしません。

詳細: [`docs/comprehensive-project-inventory-audit.md`](docs/comprehensive-project-inventory-audit.md)

## Phase 2.5 — Project-Level Annual Budget Reconstruction

R5～R8の公式予算・配分資料を案件scopeへ照合し、project-specific amountを確認できた値だけを収録します。

- 当初 / 補正 / 配分を分離
- 国配分と県予算を自動合算しない
- broader program totalを個別Projectへ按分しない
- missingを0円にしない

詳細: [`docs/annual-budget-reconstruction.md`](docs/annual-budget-reconstruction.md)

## Features

- 国土地理院標準地図上のPoint / LineString表示
- カテゴリー、事業主体、市町、ステータス、Data Depthによる絞り込み
- 変更ラベルによる絞り込み
- 事業名・市町名のフリーワード検索
- 全canonical Projectの静的detail page
- Cost / Schedule / Progress History
- 年度予算・累計投資・B/C・documented reasons
- フィールド単位provenance / sourceId traceability
- Python validators / reproducible coverage reports
- Vitest / ESLint / GitHub Actions / GitHub Pages

## Data policy

1. 愛媛県、国土交通省、市町、事業主体等の一次情報を優先する。
2. 独立した事業identityと一次資料を確認できれば、数値不足だけを理由に除外しない。
3. 工事・業務契約とProjectを区別する。
4. Project / Work Package / Assetを区別する。
5. 不明値は推測せず `null` または空配列。
6. 年度事業費・全体事業費・予算額・契約額・累計投資を区別する。
7. `costHistory` は同scopeの全体事業費だけを比較する。
8. 異なる定義の進捗率を同一時系列に混ぜない。
9. `COST+` / `DELAYED` 等は比較可能な履歴差分からのみ生成する。
10. 増額・延期理由は一次資料に明記された場合だけ記録する。
11. approximate geometryをofficial geometryのように表示しない。
12. 類似名称・broader/narrower scopeを自動mergeしない。
13. Phase 2.6 / 2.7追加案件で年度予算未監査なら `SOURCE_NOT_FOUND`。0円を意味しない。
14. 掲載件数は、公式資料から確認済みのProject件数であり、愛媛県内公共事業の全件数ではない。

## Schema / files

- Base canonical dataset: `public/data/projects.json` / schema `2.2.0`
- Base geometry: `public/data/projects.geojson`
- Enrichment: `public/data/enrichment.json` / schema `2.1.0`
- R5–R8 annual budget audit: `public/data/annual-budget-r5-r8.json` / schema `2.5.0`
- Phase 2.6 inventory overlay: `public/data/phase26-inventory.json` / version `2.6.0`
- Phase 2.7 inventory overlay: `public/data/phase27-inventory.json` / version `2.7.0`

Relevant documentation:

- [`docs/phase27a2-canonical-expansion.md`](docs/phase27a2-canonical-expansion.md)
- [`docs/comprehensive-project-inventory-audit.md`](docs/comprehensive-project-inventory-audit.md)
- [`docs/inventory-coverage.md`](docs/inventory-coverage.md)
- [`docs/adding-projects.md`](docs/adding-projects.md)
- [`docs/data-schema.md`](docs/data-schema.md)
- [`docs/change-detection.md`](docs/change-detection.md)
- [`docs/data-enrichment.md`](docs/data-enrichment.md)
- [`docs/annual-budget-reconstruction.md`](docs/annual-budget-reconstruction.md)

## Verification

```bash
npm install
npm run lint
npm test
npm run validate
npm run report:inventory
npm run report:budget
npm run build
npm run check
```

`main` pushでGitHub Pagesをbuild/deployします。

## Disclaimer

本サイトは愛媛県その他の行政機関が運営する公式サイトではありません。掲載値・位置は公表資料を整理したもので、最新情報・正確な施工区域は必ず原資料を確認してください。`COST+` や `DELAYED` は公表値の差分ラベルであり、事業の妥当性・効率性・責任を評価するものではありません。

## License

ソースコードはMIT Licenseです。行政機関の公表資料、地図タイル等には各提供元の利用条件が適用されます。
