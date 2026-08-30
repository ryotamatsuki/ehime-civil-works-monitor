# Ehime Civil Works Monitor

愛媛県内の主要公共土木事業を、地図・事業費・進捗・完成予定・一次情報源とその変化から確認するための非公式Web GISです。

## What is this?

公共機関が公開している事業評価資料等を構造化し、「どこで、どのような事業が、いくらの事業費で、どの段階まで進み、過去の公表値から何が変わったか」を一次資料まで遡れる形で探索できるようにします。

Phase 1では令和7年度愛媛県公共事業評価委員会の審議対象県事業から10件を収録しました。Phase 2では比較可能な過年度一次資料を確認できた案件にCost / Schedule / Progress履歴を追加し、変更を履歴から自動導出しました。Phase 2.1では現10案件を一次資料でさらに深掘りし、年度予算・累計投資事業費・B/C履歴・文書化された増額／延期事情を別レイヤーとして追加します。

## Phase 2.1 Data Enrichment

- Annual Budget — 案件単位で確認できた年度予算・配分額
- Cumulative Investment — 累計投資事業費。実績と年度末見込を分離
- B/C History — 当該事業／ネットワーク全体、事業全体／残事業を分離
- Documented Reasons — 一次資料に明記された増額・延期・遅延事情のみ
- Data Depth summary — どの種類の深掘りデータを何案件で確認できたかをトップ画面に表示
- Dedicated validator — `public/data/enrichment.json` を独立検証

初回のPhase 2.1 enrichmentは現10案件すべてを対象としています。累計投資とB/Cは10案件に収録し、案件単位の年度予算は一次資料で直接確認できた案件のみ収録します。比較可能な複数時点B/Cは大洲西道路、夜昼道路、JR松山駅付近連続立体交差事業から開始しています。

重要なデータ品質ルールとして、評価委員会開催時点で将来となる「年度末投資事業費」は `planned` とし、過去年度末の実績 `actual` と区別します。また、R7の大洲西道路・夜昼道路では一覧表と個別再評価票で投資事業費の基準時点表記が一致しないため、詳細個表を優先し、その差異をnoteに残します。

## Phase 2 Features

- Cost History — 全体事業費の公表値履歴
- Schedule History — 完成予定年度の履歴
- Progress History — 比較可能な進捗率の履歴
- Change Detection — `COST+`, `COST−`, `DELAYED`, `EARLIER`, `UPDATED`
- Recent Changes — 最新の変更イベントを一覧表示
- Alert Filter — 通常のカテゴリー・市町・ステータス条件とAND検索
- Detail Timeline — 各履歴値から原資料へ直接遡れる詳細ページ
- Dashboard — COST+案件数、DELAYED案件数、直近365日の更新案件数

変更フラグはJSONへ手入力せず、`src/domain.ts` が履歴の隣接差分からpure functionとして導出します。

## Existing Features

- 国土地理院標準地図上の事業表示
- カテゴリー、事業主体、市町、ステータスによる絞り込み
- 事業名・市町名のフリーワード検索
- 事業別の詳細ページ
- フィールド単位のprovenance
- JSON / GeoJSON / History / EnrichmentのPython検証
- GitHub Actionsによるlint / test / validation / build
- GitHub Pagesへの静的デプロイ

## Data Sources

主要ソースは愛媛県「公共事業評価委員会」です。

- https://www.pref.ehime.jp/page/127397.html
- https://www.pref.ehime.jp/uploaded/attachment/162763.pdf

Phase 2 / 2.1では過年度の公共事業評価委員会資料、政府予算案反映状況調書等も用います。各history/enrichment entryの `sourceId` は一次資料へ解決でき、個々の値から原資料へ戻れる設計です。

## Data Policy

1. 愛媛県、国土交通省、市町等の一次情報を優先します。
2. 確認できない数値は推測せず `null` または空配列とします。
3. 年度事業費・全体事業費・予算額・契約額・累計投資事業費を区別します。
4. `costHistory` は全体事業費だけを比較します。
5. 年度予算は全体事業費の増減検知に使用しません。
6. 累計投資は `actual` と `planned` を分離します。
7. B/Cは対象範囲（project/network）と評価視点（whole/remaining）を分離します。
8. 異なる定義の進捗率を同一時系列として比較しません。
9. 重要な現在値は `provenance`、履歴・enrichment値は `sourceId` で根拠へ紐付けます。
10. 増額・延期理由は一次資料に明記された場合だけ記録し、AIで推測しません。
11. `delay_context` の記述だけから機械的な `DELAYED` イベントを生成しません。
12. `lastVerified` と各sourceの `accessed` を保持します。
13. `locationAccuracy: approximate` は概略位置であり、施工範囲を示しません。

**掲載値は各機関の公表資料を整理したものであり、最新情報は必ず原資料を確認してください。**

## Schema

Phase 2 project dataset schema is `2.0.0` and Phase 2.1 enrichment schema is `2.1.0`.

```text
Project current snapshot (2.0.0)
├── provenance
├── sources
├── costHistory[]
├── scheduleHistory[]
└── progressHistory[]
        ↓
Change Detection
        ↓
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

バックエンド、DB、認証は使用しません。Phase 2.1もstatic JSONを追加するだけで既存アーキテクチャを維持します。

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
npm run build
```

一括確認:

```bash
npm run check
```

ValidatorはPhase 2 historyの型・日付・source参照・時系列順・最新snapshot整合・GeoJSONに加え、Phase 2.1の年度予算basis、累計投資actual/planned、B/C scope/perspective、reason type、source解決、数値範囲を検査します。

## Deployment

`main` へのpushで `.github/workflows/deploy.yml` がproduction buildを作成し、GitHub Pagesへデプロイします。

GitHub Pages base path:

`/ehime-civil-works-monitor/`

## Adding and Updating Projects

1. `public/data/projects.json` に現在値を追加・更新
2. 出典を `sources` に登録
3. 現在値を `provenance` に紐付け
4. 比較可能な過去値だけをPhase 2 historyへ時系列順に追加
5. `public/data/enrichment.json` に年度予算・累計投資・B/C・理由を追加
6. 各entryを一次資料の `sourceId` に紐付け
7. 位置を確認できる場合のみGeoJSONへ追加
8. `npm run validate && npm run lint && npm test && npm run build`

過年度案件の拡張は、案件名だけで追加せず、評価年度ごとのcohort単位で事業同一性・事業範囲・評価手法・位置を確認してから行います。方針は [`docs/data-enrichment.md`](docs/data-enrichment.md) を参照してください。

## Data Disclaimer

本サイトは愛媛県その他の行政機関が運営する公式サイトではありません。`COST+` や `DELAYED` は公表値の差分を示すラベルであり、事業の妥当性・効率性・責任等を評価するものではありません。年度予算、累計投資、B/Cは定義・基準時点・対象範囲を確認した上で表示していますが、最新状況は必ずリンク先の原資料をご確認ください。表示位置には概略点を含みます。

## License

ソースコードはMIT Licenseです。行政機関の公表資料、地図タイル等には各提供元の利用条件が適用されます。
