#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "public/data/projects.json"
GEOJSON = ROOT / "public/data/projects.geojson"
ENRICHMENT = ROOT / "public/data/enrichment.json"

projects = json.loads(PROJECTS.read_text(encoding="utf-8"))
geo = json.loads(GEOJSON.read_text(encoding="utf-8"))
enrichment = json.loads(ENRICHMENT.read_text(encoding="utf-8"))

new_projects = [
    {
        "id": "sanaki-widening",
        "name": "道路改築事業（国道378号 三秋拡幅）",
        "category": "road",
        "categoryLabel": "道路",
        "operator": "愛媛県",
        "department": "道路建設課",
        "municipalities": ["伊予市"],
        "status": "under_construction",
        "statusLabel": "事業中",
        "startFiscalYear": 1995,
        "plannedCompletionFiscalYear": 2027,
        "totalProjectCostMillionYen": 6160,
        "currentFiscalYearBudgetMillionYen": None,
        "progressPercent": 69.8,
        "progressAsOf": "令和5年度末",
        "landAcquisitionProgressPercent": None,
        "benefitCostRatio": 1.13,
        "lastVerified": "2026-08-30",
        "summary": "伊予市三秋から双海町高野川までの国道378号で、道路拡幅・線形改良を行う道路改築事業。",
        "scope": "計画延長3,700m。令和6年度公共事業評価資料では、全体事業費6,160百万円、令和5年度末の投資事業費4,300百万円、事業費ベース進捗率69.8%、完成予定令和9年度とされている。",
        "geometryRef": "sanaki-widening",
        "locationAccuracy": "approximate",
        "locationSource": "source-r6-review",
        "locationNote": "再評価個表に記載された起終点（伊予市三秋～双海町高野川）を参考にした概略点。道路線形・施工範囲そのものではない。",
        "sources": [
            {
                "id": "source-r6-review",
                "title": "令和6年度 道路改築事業（国道378号 三秋拡幅）再評価個表",
                "publisher": "愛媛県",
                "url": "https://www.pref.ehime.jp/uploaded/attachment/129987.pdf",
                "accessed": "2026-08-30"
            }
        ],
        "provenance": {
            "startFiscalYear": "source-r6-review",
            "plannedCompletionFiscalYear": "source-r6-review",
            "totalProjectCostMillionYen": "source-r6-review",
            "progressPercent": "source-r6-review",
            "benefitCostRatio": "source-r6-review",
            "summary": "source-r6-review",
            "scope": "source-r6-review",
            "geometryRef": "source-r6-review"
        },
        "costHistory": [
            {"asOf": "2024-09-03", "fiscalYear": 2024, "valueMillionYen": 6160, "sourceId": "source-r6-review"}
        ],
        "scheduleHistory": [
            {"asOf": "2024-09-03", "plannedCompletionFiscalYear": 2027, "sourceId": "source-r6-review"}
        ],
        "progressHistory": [
            {"asOf": "2024-03-31", "progressPercent": 69.8, "sourceId": "source-r6-review", "note": "令和6年度再評価個表に記載された令和5年度末の事業費ベース進捗率。"}
        ]
    },
    {
        "id": "nishimachi-nakamura-street",
        "name": "都市計画街路事業（西町中村線）",
        "category": "urban",
        "categoryLabel": "都市",
        "operator": "愛媛県",
        "department": "都市整備課",
        "municipalities": ["新居浜市"],
        "status": "under_construction",
        "statusLabel": "事業中",
        "startFiscalYear": 2005,
        "plannedCompletionFiscalYear": 2029,
        "totalProjectCostMillionYen": 7787,
        "currentFiscalYearBudgetMillionYen": None,
        "progressPercent": 82.0,
        "progressAsOf": "令和5年度末",
        "landAcquisitionProgressPercent": None,
        "benefitCostRatio": 1.01,
        "lastVerified": "2026-08-30",
        "summary": "新居浜市滝の宮町から本郷までの都市計画道路西町中村線を整備し、幹線道路ネットワークの強化と市街地交通の円滑化を図る事業。",
        "scope": "計画延長1,080m。令和6年度再評価個表では、全体事業費7,787百万円、令和5年度末投資事業費6,388百万円、進捗率82.0%、完成予定令和11年度。",
        "geometryRef": "nishimachi-nakamura-street",
        "locationAccuracy": "approximate",
        "locationSource": "source-r6-review",
        "locationNote": "再評価個表の起終点（新居浜市滝の宮町～本郷）を参考にした概略点。道路線形・施工範囲そのものではない。",
        "sources": [
            {
                "id": "source-r6-review",
                "title": "令和6年度 都市計画街路事業（西町中村線）再評価個表",
                "publisher": "愛媛県",
                "url": "https://www.pref.ehime.jp/uploaded/attachment/129988.pdf",
                "accessed": "2026-08-30"
            },
            {
                "id": "source-r1-review",
                "title": "令和元年度 都市計画街路事業（西町中村線）再評価資料",
                "publisher": "愛媛県",
                "url": "https://www.pref.ehime.jp/uploaded/attachment/45451.pdf",
                "accessed": "2026-08-30"
            }
        ],
        "provenance": {
            "startFiscalYear": "source-r6-review",
            "plannedCompletionFiscalYear": "source-r6-review",
            "totalProjectCostMillionYen": "source-r6-review",
            "progressPercent": "source-r6-review",
            "benefitCostRatio": "source-r6-review",
            "summary": "source-r6-review",
            "scope": "source-r6-review",
            "geometryRef": "source-r6-review"
        },
        "costHistory": [
            {"asOf": "2014-09-05", "fiscalYear": 2014, "valueMillionYen": 3602.210, "sourceId": "source-r1-review", "note": "令和元年度資料の前回評価比較欄に記載された平成26年度再評価時の全体事業費。"},
            {"asOf": "2019-08-26", "fiscalYear": 2019, "valueMillionYen": 5470.864, "sourceId": "source-r1-review", "note": "令和元年度再評価時の全体事業費。"},
            {"asOf": "2024-09-03", "fiscalYear": 2024, "valueMillionYen": 7787, "sourceId": "source-r6-review", "note": "令和6年度再評価時の全体事業費。"}
        ],
        "scheduleHistory": [
            {"asOf": "2014-09-05", "plannedCompletionFiscalYear": 2019, "sourceId": "source-r1-review", "note": "平成26年度再評価時の完成予定。"},
            {"asOf": "2019-08-26", "plannedCompletionFiscalYear": 2024, "sourceId": "source-r1-review", "note": "令和元年度再評価時の完成予定。"},
            {"asOf": "2024-09-03", "plannedCompletionFiscalYear": 2029, "sourceId": "source-r6-review", "note": "令和6年度再評価時の完成予定。"}
        ],
        "progressHistory": [
            {"asOf": "2014-09-05", "progressPercent": 43.6, "sourceId": "source-r1-review", "note": "平成26年度再評価時の事業費ベース進捗率。"},
            {"asOf": "2019-08-26", "progressPercent": 56.0, "sourceId": "source-r1-review", "note": "令和元年度再評価時の事業費ベース進捗率。"},
            {"asOf": "2024-03-31", "progressPercent": 82.0, "sourceId": "source-r6-review", "note": "令和6年度再評価個表に記載された令和5年度末の事業費ベース進捗率。"}
        ]
    }
]

new_features = [
    {
        "type": "Feature",
        "properties": {"projectId": "sanaki-widening"},
        "geometry": {"type": "Point", "coordinates": [132.65, 33.70]}
    },
    {
        "type": "Feature",
        "properties": {"projectId": "nishimachi-nakamura-street"},
        "geometry": {"type": "Point", "coordinates": [133.28, 33.95]}
    }
]

new_enrichment = [
    {
        "projectId": "sanaki-widening",
        "sources": [
            {
                "id": "enrichment-r6-review",
                "title": "令和6年度 道路改築事業（国道378号 三秋拡幅）再評価個表",
                "publisher": "愛媛県",
                "url": "https://www.pref.ehime.jp/uploaded/attachment/129987.pdf",
                "accessed": "2026-08-30"
            }
        ],
        "annualBudgetHistory": [],
        "cumulativeInvestmentHistory": [
            {"fiscalYear": 2023, "asOf": "2024-03-31", "amountMillionYen": 4300, "status": "actual", "sourceId": "enrichment-r6-review", "note": "令和5年度末投資事業費。"}
        ],
        "benefitCostHistory": [
            {"fiscalYear": 2024, "asOf": "2024-09-03", "value": 1.13, "scope": "project", "perspective": "whole", "sourceId": "enrichment-r6-review"},
            {"fiscalYear": 2024, "asOf": "2024-09-03", "value": 8.04, "scope": "project", "perspective": "remaining", "sourceId": "enrichment-r6-review"}
        ],
        "documentedReasons": []
    },
    {
        "projectId": "nishimachi-nakamura-street",
        "sources": [
            {
                "id": "enrichment-r6-review",
                "title": "令和6年度 都市計画街路事業（西町中村線）再評価個表",
                "publisher": "愛媛県",
                "url": "https://www.pref.ehime.jp/uploaded/attachment/129988.pdf",
                "accessed": "2026-08-30"
            },
            {
                "id": "enrichment-r1-review",
                "title": "令和元年度 都市計画街路事業（西町中村線）再評価資料",
                "publisher": "愛媛県",
                "url": "https://www.pref.ehime.jp/uploaded/attachment/45451.pdf",
                "accessed": "2026-08-30"
            }
        ],
        "annualBudgetHistory": [],
        "cumulativeInvestmentHistory": [
            {"fiscalYear": 2023, "asOf": "2024-03-31", "amountMillionYen": 6388, "status": "actual", "sourceId": "enrichment-r6-review", "note": "令和5年度末投資事業費。"}
        ],
        "benefitCostHistory": [
            {"fiscalYear": 2014, "asOf": "2014-09-05", "value": 1.10, "scope": "project", "perspective": "whole", "sourceId": "enrichment-r1-review", "note": "令和元年度資料の前回評価比較欄から収録。"},
            {"fiscalYear": 2014, "asOf": "2014-09-05", "value": 2.22, "scope": "project", "perspective": "remaining", "sourceId": "enrichment-r1-review", "note": "令和元年度資料の前回評価比較欄から収録。"},
            {"fiscalYear": 2019, "asOf": "2019-08-26", "value": 1.62, "scope": "project", "perspective": "whole", "sourceId": "enrichment-r1-review"},
            {"fiscalYear": 2019, "asOf": "2019-08-26", "value": 4.54, "scope": "project", "perspective": "remaining", "sourceId": "enrichment-r1-review"},
            {"fiscalYear": 2024, "asOf": "2024-09-03", "value": 1.01, "scope": "project", "perspective": "whole", "sourceId": "enrichment-r6-review"},
            {"fiscalYear": 2024, "asOf": "2024-09-03", "value": 8.09, "scope": "project", "perspective": "remaining", "sourceId": "enrichment-r6-review"}
        ],
        "documentedReasons": [
            {"effectiveDate": "2019-08-26", "type": "cost_change", "summary": "起点側区間の延伸に伴い事業範囲と全体事業費を変更", "sourceId": "enrichment-r1-review", "note": "平成26年度再評価時3,602.210百万円から令和元年度5,470.864百万円へ変更。"},
            {"effectiveDate": "2019-08-26", "type": "schedule_change", "summary": "大規模物件の用地買収および工事工程の精査により完成予定を令和元年度から令和6年度へ変更", "sourceId": "enrichment-r1-review"}
        ]
    }
]

existing_ids = {p["id"] for p in projects["projects"]}
for project in new_projects:
    if project["id"] not in existing_ids:
        projects["projects"].append(project)

feature_ids = {f.get("properties", {}).get("projectId") for f in geo["features"]}
for feature in new_features:
    if feature["properties"]["projectId"] not in feature_ids:
        geo["features"].append(feature)

enrichment_ids = {r["projectId"] for r in enrichment["records"]}
for record in new_enrichment:
    if record["projectId"] not in enrichment_ids:
        enrichment["records"].append(record)

projects["datasetTitle"] = "Ehime Civil Works Monitor Phase 2.1 dataset"
projects["generatedAt"] = "2026-08-30"
enrichment["generatedAt"] = "2026-08-30"

PROJECTS.write_text(json.dumps(projects, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
GEOJSON.write_text(json.dumps(geo, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
ENRICHMENT.write_text(json.dumps(enrichment, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

print(f"projects={len(projects['projects'])}, features={len(geo['features'])}, enrichment={len(enrichment['records'])}")
