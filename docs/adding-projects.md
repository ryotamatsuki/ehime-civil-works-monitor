# Adding Projects

1. 事業主体の公式ページ、公共事業評価資料、予算資料等の一次資料を確保します。未公表値はnullにします。
2. `public/data/projects.json` に一意なslugで追加し、金額は百万円単位に正規化します。
3. `sources` に出典を登録し、重要フィールドを `provenance` でsource IDに紐付けます。
4. 位置を確認できる場合だけ `projects.geojson` に追加します。正式GISは `official`、公式住所等から導いたものは `derived`、公式位置図の代表点等は `approximate` とします。
5. `npm run validate`、`npm run lint`、`npm test`、`npm run build` を実行します。

概略点を正確な施工位置のように見せないことが最重要です。
