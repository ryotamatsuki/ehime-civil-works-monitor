# Phase 2.6 — Comprehensive Project Inventory Audit

最終確認: 2026-09-03

## 1. Population definition

Phase 2.6では、従来50件を「主要50事業」とは扱わず、2026年9月時点で実施中・事業化済み・具体的に計画された公共土木事業のうち、公式資料から独立したProject identity、operator/所管、市町、概略位置を合理的に確認できるものをcanonical inventoryへ収録する。

Project / Work Package / Assetは分離する。単一工事、設計・測量業務、維持補修契約、施設名だけのラベルはcanonical Projectへ昇格させない。

## 2. Source-family audit

| Family | Audit result | Production use |
| --- | --- | --- |
| えひめの土木 2024–2026 | audited | 既存50件とのidentity/location reconciliation。小さな未同定ラベルは推測登録しない |
| 道路の整備に関するプログラム2018–2027 Vol.8 | audited | 対象路線一覧表から独立事業区間をreconcileし、新規50件を追加 |
| 地方局・土木事務所 | audited as discovery layer | 路線・河川・港湾等のbroader labelだけではProject化せず、道路プログラム・評価資料等でscopeを独立確認できた案件のみ採用 |
| 公共事業評価 R2–R7 | audited/reconciled | 既存cohortと照合し、R7第2回の砂防9案件を追加。過年度資料はidentity/history確認に使用 |
| 公共事業評価 R8 | notice audited | 2026-09-01開催分は詳細なproject-level結果が確認できるまでproduction数値・案件追加に使用しない |
| R8当初・6月・9月補正 | audited | Phase 2.5の予算監査を継承。予算事業総額を個別Projectへ按分しない |
| 国土交通省・四国地方整備局 | audited/reconciled | 直轄道路のoperator・事業区間を照合。県内区間を持つ独立Projectのみ採用 |
| 発注見通し | audited as discovery only | 上位Project発見の補助。工事・業務契約1件をそのままProjectにしない |

主要一次資料:

- えひめの土木: https://www.pref.ehime.jp/page/8387.html
- 道路整備プログラム Vol.8 対象路線一覧表: https://www.pref.ehime.jp/uploaded/attachment/176206.pdf
- R7公共事業評価結果: https://www.pref.ehime.jp/page/155231.html
- R7第2回審議対象事業一覧表: https://www.pref.ehime.jp/uploaded/attachment/175404.pdf
- R8予算発表資料: https://www.pref.ehime.jp/page/8776.html
- 東予地方局建設部: https://www.pref.ehime.jp/page/1949.html
- 南予地方局河川港湾課: https://www.pref.ehime.jp/soshiki/259/index-2.html
- 工事等発注見通し入口: https://www.pref.ehime.jp/site/nyusatsu/5834.html

## 3. Structured candidate master

今回production判定まで構造化したcandidate cohortは69件。

| Candidate status | Count | Treatment |
| --- | ---: | --- |
| `NEW_CANONICAL_PROJECT` | 59 | productionへ追加 |
| `EXISTING_PROJECT_MATCH` | 10 | 既存IDを維持し重複追加しない |
| `WORK_PACKAGE_OF_EXISTING_PROJECT` | 0 | 発注見通しは契約行として監査したが、独立Project候補masterへ昇格させない |
| `BROADER_LABEL_ONLY` | 0 | 地方局ページの路線・河川名はdiscovery layerに留め、独立scope確認前はcandidate masterへ昇格させない |
| `ASSET_ONLY` | 0 | 施設名だけの表示はcandidate masterへ昇格させない |
| `COMPLETED_HISTORICAL_PROJECT` | 0 | 今回のproduction cohortはcurrent/plannedを優先 |
| `DUPLICATE_NAME` | 0 | validatorでproduction unionを検査 |
| `IDENTITY_AMBIGUOUS` | 0 | 未同定ラベルはproduction candidateから除外しblind spotとして記録 |
| `OUT_OF_SCOPE` | 0 | 市町単独事業・純粋な契約行はsource-family audit時点で除外 |

この69件は「発見した文字列すべて」ではなく、独立Projectとしてproduction eligibilityを判定できる段階まで上げたcandidate masterである。地方局ページのbroader route labelや発注見通しの契約行は、Project identityが未確定の段階で件数を膨らませない。

### Existing matches retained

道路プログラム等で再確認した既存canonicalの代表例:

- 一般国道11号 川之江三島バイパス
- 一般国道11号 新居浜バイパス
- 一般国道11号 小松バイパス
- 一般国道196号 今治道路
- 一般国道197号 夜昼道路
- 一般国道197号 大洲西道路
- 一般国道197号 八幡浜道路
- 一般国道56号 津島道路
- 一般国道56号 宿毛内海道路（御荘～内海）
- 一般国道378号 三秋拡幅

これらは別名・新しいsource appearanceを理由に新IDを作らない。

## 4. Production additions

新規59件:

- Road: 50
- Sabo: 9

Road 50件は `public/data/phase26-inventory.json` の `roads` に全件記録し、道路整備プログラムVol.8の対象路線一覧表をprimary sourceとする。完成年度が資料上※等で確定しない事業は `null` のまま保持する。

Sabo 9件はR7公共事業評価委員会第2回の個別審議案件:

1. 事業間連携砂防等事業（東町川）
2. 事業間連携砂防等事業（前神寺谷川）
3. 事業間連携砂防等事業（今戸川）
4. 事業間連携砂防等事業（ウルシサコ）
5. 事業間連携砂防等事業（神納川）
6. 事業間連携砂防等事業（久保川）
7. まちづくり連携砂防等事業（根元川）
8. まちづくり連携砂防等事業（仏師谷川）
9. まちづくり連携砂防等事業（根元川2）

## 5. Canonical result

- Before: 50
- New: 59
- After: 109

Category projection:

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

## 6. Geometry policy

Phase 2.6 additions are represented by deterministic approximate Points derived from the municipality/district context in the official source. They are navigation aids only. Exact road alignment, construction footprint, parcel boundary, sabo structure coordinate等を意味しない。

`locationAccuracy: approximate`を強制し、official geometryとは表示しない。

## 7. Enrichment / annual-budget compatibility

Phase 2.6の59件には、runtime canonical union上でそれぞれempty enrichment recordとannual-budget audit recordを生成する。

年度予算はPhase 2.6で未監査のため `SOURCE_NOT_FOUND` とする。これは0円を意味しない。既存50件のPhase 2.5 observationは変更しない。

## 8. Coverage assessment

2026-09-03時点の母集団coverage評価:

- 道路: **高** — 県道路整備プログラムのstructured project listを取り込み、国/NEXCOをreconcile
- 砂防: **高** — えひめの土木＋評価cohortを拡張。ただし評価対象外の小規模事業は残り得る
- 河川: **中** — 評価・主要事業は収録済みだが、地方局のbroader river labelsから全active projectへの分解は未完
- 港湾: **中** — 主要港湾事業はあるが地区・施設単位scopeのreconciliation余地あり
- 海岸: **中** — 評価・主要案件中心。全active coast projectのstructured listは未統合
- 都市: **中** — 評価・主要街路中心
- ダム: **高** — 主要大規模事業の母集団は限定的
- 農業: **中** — 現行サイトは土木部中心で、農林土木全体系の網羅を目的としていない

## 9. Remaining blind spots

1. R8公共事業評価委員会の2026-09-01開催分について、詳細なproject-level公表結果が確認できた時点で再監査する。
2. 地方局ページで路線名・河川名しか示されないものは、独立事業scopeを別一次資料で確認する必要がある。
3. 発注見通しはwork package discoveryには有用だが、上位Projectへのmachine reconciliationは未実装。
4. Phase 2.6追加geometryは概略点であり、公式GIS geometryではない。
5. 河川・港湾・海岸・都市について道路プログラム相当の単一structured active-project listがない領域は、道路ほどの網羅性を主張しない。

## 10. Reproduction

```bash
npm run lint
npm test
npm run validate
npm run report:inventory
npm run report:budget
npm run build
npm run check
```

原則は **coverageよりidentity correctness**。100件超は結果であって、件数目標のための工事・業務・broader labelの水増しは行わない。
