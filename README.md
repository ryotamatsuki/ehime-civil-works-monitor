# Ehime Civil Works Monitor

愛媛県内の主要公共土木事業を、地図・事業費・進捗・完成予定・一次情報源とその変化から確認するための非公式Web GISです。

## What is this?

公共機関が公開している事業評価資料等を構造化し、「どこで、どのような事業が、いくらの事業費で、どの段階まで進み、過去の公表値から何が変わったか」を一次資料まで遡れる形で探索できるようにします。

Phase 1では令和7年度愛媛県公共事業評価委員会の審議対象県事業から10件を収録しました。Phase 2では同じ10件を維持したまま、比較可能な過年度一次資料を確認できた案件に履歴を追加し、変更を履歴から自動導出します。

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
- 登録事業数、確認済み全体事業費等の簡易ダッシュボード
- 事業別の詳細ページ
- フィールド単位のprovenance
- JSON / GeoJSON / HistoryのPython検証
- GitHub Actionsによるlint / test / validation / build
- GitHub Pagesへの静的デプロイ

## Data Sources

主要ソースは愛媛県「公共事業評価委員会」です。

- https://www.pref.ehime.jp/page/127397.html
- https://www.pref.ehime.jp/uploaded/attachment/162763.pdf

Phase 2では過年度の公共事業評価委員会資料も用います。各履歴entryの `sourceId` は同じProjectの `sources` に必ず解決し、個々の値から一次資料へ戻れる設計です。

## Data Policy

1. 愛媛県、国土交通省、市町等の一次情報を優先します。
2. 確認できない数値は推測せず `null` とします。
3. 年度事業費・全体事業費・予算額・契約額を区別します。
4. `costHistory` は全体事業費だけを比較します。
5. 異なる定義の進捗率を同一時系列として比較しません。
6. 重要な現在値は `provenance`、履歴値は `sourceId` で根拠へ紐付けます。
7. 増額・延期理由は一次資料に明記された場合だけ記録し、AIで推測しません。
8. `lastVerified` と各sourceの `accessed` を保持します。
9. `locationAccuracy: approximate` は概略位置であり、施工範囲を示しません。

**掲載値は各機関の公表資料を整理したものであり、最新情報は必ず原資料を確認してください。**

## Schema

Phase 2 dataset schema is `2.0.0`.

```text
Project current snapshot
├── provenance
├── sources
├── costHistory[]
├── scheduleHistory[]
└── progressHistory[]
        ↓
Change Detection
        ↓
COST± / DELAYED / EARLIER / UPDATED
```

See:

- [`docs/data-schema.md`](docs/data-schema.md)
- [`docs/change-detection.md`](docs/change-detection.md)
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
npm run build
```

一括確認:

```bash
npm run check
```

Validatorはhistoryの型、日付、source参照、時系列順、重複日、数値範囲、finite number、最新snapshotとの一致、GeoJSON等を検査します。

## Deployment

`main` へのpushで `.github/workflows/deploy.yml` がproduction buildを作成し、GitHub Pagesへデプロイします。

GitHub Pages base path:

`/ehime-civil-works-monitor/`

## Adding and Updating Projects

1. `public/data/projects.json` に現在値を追加・更新
2. 出典を `sources` に登録
3. 現在値を `provenance` に紐付け
4. 比較可能な過去値だけをhistoryへ時系列順に追加
5. 各history entryを `sourceId` に紐付け
6. 位置を確認できる場合のみGeoJSONへ追加
7. `npm run validate && npm run lint && npm test && npm run build`

詳細は [`docs/adding-projects.md`](docs/adding-projects.md) を参照してください。

## Data Disclaimer

本サイトは愛媛県その他の行政機関が運営する公式サイトではありません。`COST+` や `DELAYED` は公表値の差分を示すラベルであり、事業の妥当性・効率性・責任等を評価するものではありません。表示位置には概略点を含みます。事業の最新状況、正確な事業区域、予算・契約情報については必ずリンク先の原資料をご確認ください。

## License

ソースコードはMIT Licenseです。行政機関の公表資料、地図タイル等には各提供元の利用条件が適用されます。
