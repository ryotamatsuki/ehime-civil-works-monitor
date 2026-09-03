# Phase 2.5 — R5–R8 Annual Budget Source Inventory

最終確認: 2026-09-03

この一覧は、canonical projectへ年度予算・配分額を結び付ける際に確認した主要一次資料を記録する。案件名と金額が直接対応しない資料は、事業の存在確認には使えても案件予算には採用しない。

| FY | Stage | Document | Source | Project-level amount | Use |
| --- | --- | --- | --- | --- | --- |
| 2023 / R5 | allocation | 令和5年度重要施策提案・要望 政府予算案反映状況調書 | https://www.pref.ehime.jp/uploaded/attachment/18086.pdf | yes / partial | 高規格道路・野村ダム等の個別配分を採用 |
| 2023 / R5 | initial | JR松山駅付近連続立体交差事業費 | https://www.pref.ehime.jp/uploaded/attachment/49083.pdf | yes | JR松山駅の当初予算を採用 |
| 2024 / R6 | allocation | 令和6年度重要施策提案・要望 政府予算案反映状況調書 | https://www.pref.ehime.jp/uploaded/attachment/118582.pdf | yes / partial | 高規格道路・野村ダム等の個別配分を採用 |
| 2025 / R7 | allocation | 令和7年度重要施策提案・要望 政府予算案反映状況調書 | https://www.pref.ehime.jp/uploaded/attachment/148176.pdf | yes / partial | 高規格道路・野村ダム等の個別配分を採用 |
| 2025 / R7 | initial | 令和7年度当初予算（案）の部局別事業一覧（土木部） | https://www.pref.ehime.jp/uploaded/attachment/138990.pdf | yes / partial | JR松山駅のR7当初、同表の前年度欄からR6当初を採用 |
| 2025 / R7 | supplementary | 令和7年度6月補正予算（案）の部局別事業一覧（土木部） | https://www.pref.ehime.jp/uploaded/attachment/148846.pdf | yes / partial | JR松山駅の6月補正純増額を別観測として採用 |
| 2026 / R8 | allocation | 令和8年度重要施策提案・要望 政府予算案反映状況調書 | https://www.pref.ehime.jp/uploaded/attachment/180777.pdf | yes / partial | 高規格道路・野村ダム等の個別配分を採用 |
| 2026 / R8 | initial | 令和8年度当初予算（案）の部局別事業一覧（土木部） | https://www.pref.ehime.jp/uploaded/attachment/170546.pdf | yes / partial | JR松山駅の当初予算を採用 |
| 2026 / R8 | initial | 令和8年度当初予算（案）個別事業説明書 PR版（土木部） | https://www.pref.ehime.jp/uploaded/attachment/169537.pdf | yes / partial | 夜昼道路・大洲西道路の県当初予算を別系列として採用 |
| 2026 / R8 | June supplementary | 令和8年度6月補正予算（案）個別事業説明書 PR版（土木部） | https://www.pref.ehime.jp/page/149999.html | partial | baseline audit。複数箇所をまとめた事業費は個別案件へ配賦しない |
| 2026 / R8 | September supplementary | 令和8年度9月補正予算（案）個別事業説明書 PR版（土木部） | https://www.pref.ehime.jp/page/156358.html | partial | 2026-09-01公表分をbaseline audit。個別帰属できない金額は採用しない |
| 2023–2026 | archive | 予算発表資料（令和5年度～） | https://www.pref.ehime.jp/page/8776.html | index | 当初・補正資料の年度別入口 |

## Reconciliation policy

- `project_allocation / allocation / project`、`prefectural_budget / initial / project` 等、同じ `basis × budgetStage × scope` の系列だけを年度比較する。
- 同一年度に国の配分額と県当初予算額が存在しても合算しない。
- 補正予算額は、資料が純増額として示す場合はそのまま `supplementary` として保存し、既定予算額との機械的合算値をcanonical化しない。
- 「○○などN箇所」の事業費総額は、掲載された個別箇所へ按分しない。
- `宿毛内海道路` のようにcanonical recordより広いscopeしか確認できないものは `SCOPE_MISMATCH` とする。

## Baseline audit result

`public/data/annual-budget-r5-r8.json` は現行50 canonical projectsすべてにaudit recordを持つ。確認できたproject-specific observationだけを保存し、残りは `BROADER_PROGRAM_ONLY`、`SCOPE_MISMATCH`、`SOURCE_NOT_FOUND` 等で理由を残す。未確認はゼロを意味しない。
