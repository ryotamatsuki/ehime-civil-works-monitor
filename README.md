# Ehime Civil Works Monitor

愛媛県内の主要公共土木事業を、地図・事業費・進捗・一次情報源を横断して確認するための非公式Web GISです。

## What is this?

公共機関が公開している事業評価資料等を構造化し、「どこで、どのような事業が、いくらの事業費で、どの段階まで進んでいるか」を地図から探索できるようにします。Phase 1 MVPでは、令和7年度愛媛県公共事業評価委員会の審議対象県事業から10件を収録しています。

## Features

- 国土地理院標準地図上の事業表示
- カテゴリー、事業主体、市町、ステータスによる絞り込み
- 事業名・市町名のフリーワード検索
- 登録事業数、確認済み全体事業費等の簡易ダッシュボード
- 事業別の詳細ページ
- フィールド単位のprovenanceを保持できるデータモデル
- JSON / GeoJSONのPython検証
- GitHub Actionsによるlint / test / validation / build
- GitHub Pagesへの静的デプロイ

## Data Sources

Phase 1の主要ソースは愛媛県「令和7年度愛媛県公共事業評価委員会」です。

- https://www.pref.ehime.jp/page/127397.html
- https://www.pref.ehime.jp/uploaded/attachment/162763.pdf

個別事業について追加資料を確認した場合は `public/data/projects.json` の `sources` に記録しています。

## Data Policy

1. 愛媛県、国土交通省、市町等の一次情報を優先します。
2. 確認できない数値は推測せず `null` とします。
3. 年度事業費・全体事業費・予算額・契約額を区別します。
4. 重要フィールドは `provenance` で出典IDと関連付けます。
5. `lastVerified` と各sourceの `accessed` を保持します。
6. `locationAccuracy: approximate` の座標は公式位置図等を基にした概略位置であり、施工範囲を示しません。

**掲載値は各機関の公表資料を整理したものであり、最新情報は必ず原資料を確認してください。**

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

## Validate Data

```bash
python scripts/validate_data.py
# or
npm run validate
```

## Test

```bash
npm test
```

## Build

```bash
npm run build
```

`npm run build` はViteのproduction build後に各事業の `projects/<id>/index.html` を生成します。

一括確認:

```bash
npm run check
```

## Deployment

`main` へのpushで `.github/workflows/deploy.yml` がbuildし、GitHub Pages artifactをデプロイします。GitHub repository settingsで Pages のSourceを **GitHub Actions** に設定してください。

GitHub Pagesでは `/ehime-civil-works-monitor/` をbase pathとしてbuildします。

## Adding a Project

1. `public/data/projects.json` に事業を追加
2. 出典URL・確認日を `sources` に登録
3. 重要フィールドを `provenance` に紐付け
4. 位置を確認できる場合のみ `public/data/projects.geojson` にFeatureを追加
5. `locationAccuracy` と位置根拠を記録
6. `npm run validate`
7. `npm test && npm run build`

詳細は [`docs/adding-projects.md`](docs/adding-projects.md) を参照してください。

## Updating Existing Data

既存値を上書きする際は、古い資料ではなく更新後の一次資料をsourceとして追加し、該当フィールドの `provenance` を新しいsource IDへ変更してください。将来のPhaseで事業費・進捗・完成年度の履歴を別配列として保持する予定です。

## Data Disclaimer

本サイトは愛媛県その他の行政機関が運営する公式サイトではありません。表示している位置には概略点を含みます。事業の最新状況、正確な事業区域、予算・契約情報については必ずリンク先の原資料をご確認ください。

## License

ソースコードはMIT Licenseです。行政機関の公表資料、地図タイル等には各提供元の利用条件が適用されます。
