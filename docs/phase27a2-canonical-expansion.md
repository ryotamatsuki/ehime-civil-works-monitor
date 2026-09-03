# Phase 2.7A-2 — Reconciled Canonical Expansion

実装日: 2026-09-03

## Result

- Phase 2.6 runtime canonical: 109
- Round 1 high-confidence candidates: 9
- Round 1 scope-conflict hold: 1
- Round 1 additions: 8
- Round 2 A/B additions: 52
- Phase 2.7 additions: 60
- Runtime canonical after merge: **169**

## Reconciliation rule

既存canonicalとの一致、Work Package、Program、Asset、completed historical、市町単独、identity/scope conflictは追加しない。Round 1の「広域河川改修事業（二級河川 渦井川・室川・界谷川・金剛院谷川）」は、既存 `sakaidani-river`（二級河川 界谷川 広域河川改修事業）との親子・複合scope関係が未解決のためHoldとした。

## Additions

| Category | New |
| --- | ---: |
| agriculture | 7 |
| forestry | 20 |
| fishing-port | 3 |
| river | 24 |
| sabo | 5 |
| road | 1 |
| **Total** | **60** |

`forestry` と `fishing-port` をcanonical categoryとして追加する。

## Source families

- 第4期 えひめの農村づくりと農村地域防災プラン（その2）
- 第4期 えひめの森林づくりと山村地域防災プラン（その4）
- 第4期 えひめの漁村づくりと漁村地域防災プラン（その2）
- R7～R11 社会資本総合整備計画（河川）
- R7～R11 社会資本総合整備計画（砂防）
- 公共事業評価資料
- R8発注見通し（上位Projectのcurrent evidenceとして使用）

## Data-depth policy

Phase 2.7追加案件は、identity/operator/municipality/current sourceを確認したInventoryとして追加する。総事業費、完成年度、進捗率、年度予算等は、同一scopeの一次資料で確認できるまで `null` / `SOURCE_NOT_FOUND` とし、推測しない。

## Geometry

追加60件の位置は市町・地区文脈から作成した `locationAccuracy: approximate` の検索用代表点であり、施工区域、河川区間、林道線形、漁港施設位置等を示す公式geometryではない。

## Coverage statement

169件は「県内公共事業の全件数」ではない。公式一次資料を横断し、独立Projectとして確認でき、重複・scope conflictを除去してcanonical化した現時点の掲載件数である。
