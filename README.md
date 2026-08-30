# Ehime Civil Works Monitor

愛媛県内の主要公共事業を、地図・一次情報源・現在値・履歴・変更から確認するための非公式Web GISです。

## What is this?

Phase 2.2では、深い数値データがある案件だけを掲載する方式から、**Project Inventory → Current Snapshot → History → Change Detection → Enrichment → Primary Sources** という段階構造へ移行しました。

- **Project Inventory**: 事業存在・名称・地域・位置・一次資料を確認できた主要事業を広く掲載
- **Monitored Project**: 総事業費、完成予定、進捗等を一次資料で確認できた案件を数値監視
- **History**: 同一定義で比較できる過年度値だけを保存
- **Change Detection**: `COST+`, `COST−`, `DELAYED`, `EARLIER`, `UPDATED` を履歴から自動導出
- **Enrichment**: 年度予算、累計投資、B/C、一次資料に明記された増額・延期事情を追加

未確認値は推測せず `null` または空配列とします。

## Phase 2.2 — Project Inventory Expansion

主要なinventory seedは、愛媛県「えひめの土木2026 愛媛県管内図」です。

- https://www.pref.ehime.jp/uploaded/life/149017_306429_misc.pdf
- FY2026 / 令和8年度時点

管内図は、主に事業の存在、名称、カテゴリー、地域、概略位置・ルート、事業中／供用済等の文脈を確認するために使用します。総事業費・完成年度・進捗率は、個別の公式事業資料・再評価資料等で確認できた場合だけ収録します。

現在のcanonical datasetは **50案件** です。Phase 2.2で高信頼に照合できた管内図候補33件について、既存6件を既存IDへreconcileし、新規27件を追加しました。小さく判読・同定できない地図ラベルは推測登録していません。

### Data Depth

Data DepthはJSONに固定保存せず、現在の収録データからderiveします。

- `INVENTORY` — 事業位置・概要・一次資料を確認
- `SNAPSHOT` — 現在の主要数値を少なくとも1つ確認
- `HISTORY` — Cost / Schedule / Progressの比較可能な複数時点あり
- `ENRICHED` — 年度予算・累計投資・B/C・documented reasons等あり

現在のexclusive distributionは、Inventory 17 / Snapshot 11 / History 0 / Enriched 22です。Enriched案件にも履歴が含まれるため、UIの `History+` は22案件です。

### Geometry

50 GeoJSON featuresの内訳は、Point 40 / LineString 10です。Phase 2.2で追加した路線LineStringはすべて `locationAccuracy: approximate` とし、破線表示します。これは路線の位置関係を把握するための概略ルートであり、公式線形・施工範囲・用地境界ではありません。

詳細なcoverage auditは [`docs/inventory-coverage.md`](docs/inventory-coverage.md) を参照してください。

## Phase 2.1 — Data Enrichment

- Annual Budget — 案件単位で確認できた年度予算・配分額
- Cumulative Investment — 累計投資事業費。実績と年度末見込を分離
- B/C History — 当該事業／ネットワーク全体、事業全体／残事業を分離
- Documented Reasons — 一次資料に明記された増額・延期・遅延事情のみ
- Dedicated validator — `public/data/enrichment.json` を独立検証

年度末見込は `planned` とし、過去年度末の実績 `actual` と区別します。異なる対象範囲のB/Cや、全体事業費と年度予算は混同しません。

## Phase 2 — History & Change Detection

- Cost History — 全体事業費の比較可能な公表値履歴
- Schedule History — 完成予定年度の履歴
- Progress History — 同一定義で比較可能な進捗率
- Recent Changes — 最新の変更イベント
- Alert Filter — 通常フィルターとAND検索
- Detail Timeline — 履歴値から原資料へ直接遡れる詳細ページ

変更フラグをJSONへ手入力せず、`src/domain.ts` のpure functionが履歴の隣接差分から導出します。

## Current coverage

`python3 scripts/report_inventory.py` で再現可能な現在のcoverageは次のとおりです。

| Item | Projects |
| --- | ---: |
| Canonical projects | 50 |
| Monitored (Snapshot / History / Enriched) | 33 |
| Known total project cost | 32 |
| Known completion year | 22 |
| Known progress | 29 |
| Comparable Cost History (2+) | 7 |
| Comparable Schedule History (2+) | 7 |
| Comparable Progress History (2+) | 5 |
| B/C enrichment | 22 |
| Documented reasons | 11 |

## Features

- 国土地理院標準地図上のPoint / LineString表示
- カテゴリー、事業主体、市町、ステータス、Data Depthによる絞り込み
- 変更ラベルによる絞り込み
- 事業名・市町名のフリーワード検索
- Project Inventoryを含む全案件の静的detail page
- フィールド単位provenance
- History / EnrichmentのsourceId traceability
- Python validator
- Vitest / ESLint
- GitHub Actions / GitHub Pages

## Data Policy

1. 愛媛県、国土交通省、市町、事業主体等の一次情報を優先します。
2. 事業存在・名称・位置・一次資料を確認できればInventoryへ登録できます。数値情報は必須ではありません。
3. 確認できない数値は推測せず `null` または空配列とします。
4. 年度事業費・全体事業費・予算額・契約額・累計投資事業費を区別します。
5. `costHistory` は全体事業費だけを比較します。
6. 異なる定義の進捗率を同一時系列として比較しません。
7. `COST+` や `DELAYED` は履歴差分からのみ生成します。
8. B/Cは対象範囲と評価視点を分離します。
9. 増額・延期理由は一次資料に明記された場合だけ記録し、AIで推測しません。
10. 概略点・概略ルートは `locationAccuracy: approximate` とし、正確な施工区域のように表示しません。
11. 類似名称を自動mergeしません。
12. 各案件・履歴値から一次資料へ戻れることを優先します。

**掲載値は各機関の公表資料を整理したものであり、最新情報・正確な施工区域は必ず原資料を確認してください。**

## Schema

Canonical project dataset: `schemaVersion: "2.2.0"`

Phase 2.1 enrichment dataset: `enrichmentSchemaVersion: "2.1.0"`

```text
Project Inventory / Snapshot (2.2.0)
├── provenance
├── sources
├── nullable current snapshot
├── geometryRef / locationAccuracy
├── costHistory[]
├── scheduleHistory[]
└── progressHistory[]
        ↓
Derived Data Depth + Change Detection
        ↓
INVENTORY / SNAPSHOT / HISTORY / ENRICHED
COST± / DELAYED / EARLIER / UPDATED

Project enrichment (2.1.0)
├── annualBudgetHistory[]
├── cumulativeInvestmentHistory[]   actual / planned
├── benefitCostHistory[]            project / network × whole / remaining
└── documentedReasons[]
```

See:

- [`docs/data-schema.md`](docs/data-schema.md)
- [`docs/change-detection.md`](docs/change-detection.md)
- [`docs/data-enrichment.md`](docs/data-enrichment.md)
- [`docs/inventory-coverage.md`](docs/inventory-coverage.md)
- [`docs/adding-projects.md`](docs/adding-projects.md)

## Architecture

- Vite
- TypeScript
- Leaflet
- 国土地理院標準地図タイル
- JSON / GeoJSON
- Python 3
- Vitest / ESLint
- GitHub Actions / GitHub Pages

バックエンド、DB、認証は使用しません。

## Local Development

```bash
npm install
npm run dev
```

## Verification

```bash
npm run lint
npm test
npm run validate
python3 scripts/report_inventory.py
npm run build
```

一括確認:

```bash
npm run check
```

## Deployment

`main` へのpushで `.github/workflows/deploy.yml` がproduction buildを作成し、GitHub Pagesへデプロイします。

https://ryotamatsuki.github.io/ehime-civil-works-monitor/

## Adding and Updating Projects

Inventory登録から始め、数値・履歴・Enrichmentは一次資料を確認できた段階で追加します。具体的な手順は [`docs/adding-projects.md`](docs/adding-projects.md) を参照してください。

## Data Disclaimer

本サイトは愛媛県その他の行政機関が運営する公式サイトではありません。`COST+` や `DELAYED` は公表値の差分を示すラベルであり、事業の妥当性・効率性・責任等を評価するものではありません。表示位置・概略ルートには近似情報を含みます。

## License

ソースコードはMIT Licenseです。行政機関の公表資料、地図タイル等には各提供元の利用条件が適用されます。
