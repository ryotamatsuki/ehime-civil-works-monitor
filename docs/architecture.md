# Architecture

Browser → Vite-built TypeScript → `projects.json` + `projects.geojson` → Leaflet → 国土地理院標準地図タイル、という静的構成です。API server、DB、認証は使用しません。

`vite build` 後に `scripts/generate-detail-pages.mjs` が `dist/projects/<project-id>/index.html` を生成します。詳細ページはpathnameからproject IDを取得します。

`scripts/validate_data.py` はデータ整合性を独立検査し、GitHub Actionsでlint / test / validation / buildを実行します。GitHub Actions上ではVite baseを `/ehime-civil-works-monitor/` に設定します。
