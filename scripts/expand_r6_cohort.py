#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS_PATH = ROOT / "public/data/projects.json"
GEOJSON_PATH = ROOT / "public/data/projects.geojson"
ENRICHMENT_PATH = ROOT / "public/data/enrichment.json"
TYPES_PATH = ROOT / "src/types.ts"
VALIDATOR_PATH = ROOT / "scripts/validate_data.py"
STYLES_PATH = ROOT / "src/styles.css"
README_PATH = ROOT / "README.md"
ARCHIVE_DOC_PATH = ROOT / "docs/archive-expansion.md"

ACCESS = "2026-08-30"
R6_DATE = "2024-09-03"
R6_PAGE = "https://www.pref.ehime.jp/page/91481.html"
R6_MINUTES = "https://www.pref.ehime.jp/uploaded/attachment/129992.pdf"

def src(sid, title, url, publisher="愛媛県", note=None):
    x = {"id": sid, "title": title, "publisher": publisher, "url": url, "accessed": ACCESS}
    if note:
        x["note"] = note
    return x

def project(
    pid, name, category, category_label, department, municipalities,
    start, completion, cost, progress, progress_as_of, bc, summary, scope,
    detail_url=None, status="under_construction", status_label="事業中",
    coord=None, extra_sources=None, histories=None, location_note=None,
):
    sources = []
    if detail_url:
        sources.append(src("source-r6-detail", f"令和6年度 {name} 再評価個表", detail_url))
    sources.append(src("source-r6-page", "令和6年度 愛媛県公共事業評価委員会", R6_PAGE))
    if extra_sources:
        sources.extend(extra_sources)
    source_ids = {s["id"] for s in sources}
    primary = "source-r6-detail" if "source-r6-detail" in source_ids else "source-r6-page"
    p = {
        "id": pid,
        "name": name,
        "category": category,
        "categoryLabel": category_label,
        "operator": "愛媛県",
        "department": department,
        "municipalities": municipalities,
        "status": status,
        "statusLabel": status_label,
        "startFiscalYear": start,
        "plannedCompletionFiscalYear": completion,
        "totalProjectCostMillionYen": cost,
        "currentFiscalYearBudgetMillionYen": None,
        "progressPercent": progress,
        "progressAsOf": progress_as_of,
        "landAcquisitionProgressPercent": None,
        "benefitCostRatio": bc,
        "lastVerified": ACCESS,
        "summary": summary,
        "scope": scope,
        "geometryRef": pid if coord else None,
        "locationAccuracy": "approximate" if coord else "unknown",
        "locationSource": primary if coord else None,
        "locationNote": location_note or ("令和6年度再評価資料の事業箇所を基にした概略点。施工範囲そのものを示さない。" if coord else None),
        "sources": sources,
        "provenance": {},
        "costHistory": [],
        "scheduleHistory": [],
        "progressHistory": [],
    }
    for field, value in (
        ("startFiscalYear", start),
        ("plannedCompletionFiscalYear", completion),
        ("totalProjectCostMillionYen", cost),
        ("progressPercent", progress),
        ("benefitCostRatio", bc),
        ("summary", summary),
        ("scope", scope),
    ):
        if value is not None:
            p["provenance"][field] = primary
    if coord:
        p["provenance"]["geometryRef"] = primary
    if histories:
        p["costHistory"] = histories.get("costHistory", [])
        p["scheduleHistory"] = histories.get("scheduleHistory", [])
        p["progressHistory"] = histories.get("progressHistory", [])
    else:
        if cost is not None:
            p["costHistory"] = [{"asOf": R6_DATE, "fiscalYear": 2024, "valueMillionYen": cost, "sourceId": primary}]
        if completion is not None:
            p["scheduleHistory"] = [{"asOf": R6_DATE, "plannedCompletionFiscalYear": completion, "sourceId": primary}]
        if progress is not None:
            p["progressHistory"] = [{"asOf": "2024-03-31" if progress_as_of == "令和5年度末" else R6_DATE, "progressPercent": progress, "sourceId": primary,
                                     "note": progress_as_of or "令和6年度再評価資料の事業費ベース進捗率。"}]
    return p, coord

projects_to_add = []
geo_to_add = []
enrichment_to_add = []

def add_project(p, coord, enrichment):
    projects_to_add.append(p)
    if coord:
        geo_to_add.append({
            "type": "Feature",
            "properties": {"projectId": p["id"]},
            "geometry": {"type": "Point", "coordinates": coord},
        })
    enrichment_to_add.append(enrichment)

# 1 灘地区: current committee minutes provide a clear project-specific cost.
p, c = project(
    "nada-irrigation",
    "水利施設等保全高度化事業（水利施設整備事業）（灘地区）",
    "agriculture", "農業・水利", "農地整備課",
    ["八幡浜市", "伊方町"],
    None, None, 581, None, None, None,
    "八幡浜市・伊方町の柑橘園地で、老朽化したスプリンクラー自動化施設の更新を進める水利施設整備事業。",
    "令和6年度公共事業評価委員会では事業継続が妥当とされ、議事要旨で事業費581百万円と確認できる。年度・B/C等は比較可能な一次資料で確認できた項目だけを掲載する。",
    "https://www.pref.ehime.jp/uploaded/attachment/129978.pdf",
    coord=[132.36, 33.47],
    extra_sources=[src("source-r6-minutes", "令和6年度 愛媛県公共事業評価委員会 議事要旨", R6_MINUTES)],
)
p["provenance"]["totalProjectCostMillionYen"] = "source-r6-minutes"
p["costHistory"] = [{"asOf": R6_DATE, "fiscalYear": 2024, "valueMillionYen": 581, "sourceId": "source-r6-minutes",
                     "note": "議事要旨で受益者負担の説明に用いられた当該事業の事業費5億8100万円。"}]
add_project(p, c, {
    "projectId": p["id"],
    "sources": [src("enrichment-r6-minutes", "令和6年度 愛媛県公共事業評価委員会 議事要旨", R6_MINUTES)],
    "annualBudgetHistory": [],
    "cumulativeInvestmentHistory": [],
    "benefitCostHistory": [],
    "documentedReasons": [],
})

# 2 吉田地区
p, c = project(
    "yoshida-irrigation",
    "水利施設等保全高度化事業（水利施設整備事業）（吉田地区）",
    "agriculture", "農業・水利", "農地整備課",
    ["宇和島市"],
    2015, 2026, 1443, 78.0, "令和5年度末", 1.88,
    "宇和島市吉田町で、老朽化したスプリンクラー自動化施設を補修・更新し、柑橘産地の機能維持と担い手負担の軽減を図る事業。",
    "配水施設57箇所、揚水施設9箇所、制御室39ブロック、幹線水路一式。令和5年度末投資事業費1,125百万円、進捗率78.0%。",
    "https://www.pref.ehime.jp/uploaded/attachment/129979.pdf",
    coord=[132.54, 33.27],
)
add_project(p, c, {
    "projectId": p["id"],
    "sources": [src("enrichment-r6-detail", "令和6年度 吉田地区 再評価個表", "https://www.pref.ehime.jp/uploaded/attachment/129979.pdf")],
    "annualBudgetHistory": [],
    "cumulativeInvestmentHistory": [{"fiscalYear": 2023, "asOf": "2024-03-31", "amountMillionYen": 1125, "status": "actual", "sourceId": "enrichment-r6-detail"}],
    "benefitCostHistory": [{"fiscalYear": 2024, "asOf": R6_DATE, "value": 1.88, "scope": "project", "perspective": "whole", "sourceId": "enrichment-r6-detail"}],
    "documentedReasons": [],
})

# 3 芹谷川
mlit_bc_url = "https://www.mlit.go.jp/tec/hyouka/public/kisha/250401R06/pdf/00_2.pdf"
p, c = project(
    "seritani-sabo",
    "事業間連携砂防等事業（砂）芹谷川",
    "sabo", "砂防", "砂防課",
    ["四国中央市"],
    2017, 2029, 555, 18.0, "令和5年度末", 6.6,
    "四国中央市川滝町領家の土石流危険渓流で、砂防堰堤・渓流保全工等を整備する事業。",
    "砂防堰堤1基、渓流保全工222m、工事用道路0.46km、管理用道路0.16km。令和7年度工事着手見込み。",
    "https://www.pref.ehime.jp/uploaded/attachment/129980.pdf",
    coord=[133.58, 33.96],
    extra_sources=[src("source-r6-mlit-bc", "令和6年度 公共事業評価結果（砂防関係）", mlit_bc_url, "国土交通省")],
)
p["provenance"]["benefitCostRatio"] = "source-r6-mlit-bc"
add_project(p, c, {
    "projectId": p["id"],
    "sources": [
        src("enrichment-r6-detail", "令和6年度 芹谷川 再評価個表", "https://www.pref.ehime.jp/uploaded/attachment/129980.pdf"),
        src("enrichment-r6-mlit-bc", "令和6年度 公共事業評価結果（砂防関係）", mlit_bc_url, "国土交通省"),
    ],
    "annualBudgetHistory": [],
    "cumulativeInvestmentHistory": [{"fiscalYear": 2023, "asOf": "2024-03-31", "amountMillionYen": 94, "status": "actual", "sourceId": "enrichment-r6-detail"}],
    "benefitCostHistory": [{"fiscalYear": 2024, "asOf": R6_DATE, "value": 6.6, "scope": "project", "perspective": "whole", "sourceId": "enrichment-r6-mlit-bc"}],
    "documentedReasons": [],
})

# 4 大平川
p, c = project(
    "ohiragawa-sabo",
    "事業間連携砂防等事業（砂）大平川",
    "sabo", "砂防", "砂防課",
    ["伊予市"],
    2020, 2029, 355, 18.6, "令和5年度末", 2.06,
    "伊予市双海町高岸の土石流危険渓流で、人家・国道378号・JR予讃線を保全する砂防事業。",
    "砂防堰堤1基、渓流保全工13.6m、管理用道路160m。令和6年度再評価時点では工事未着手。",
    "https://www.pref.ehime.jp/uploaded/attachment/129981.pdf",
    status="planned", status_label="工事未着手",
    coord=[132.63, 33.67],
)
add_project(p, c, {
    "projectId": p["id"],
    "sources": [src("enrichment-r6-detail", "令和6年度 大平川 再評価個表", "https://www.pref.ehime.jp/uploaded/attachment/129981.pdf")],
    "annualBudgetHistory": [],
    "cumulativeInvestmentHistory": [{"fiscalYear": 2023, "asOf": "2024-03-31", "amountMillionYen": 66, "status": "actual", "sourceId": "enrichment-r6-detail"}],
    "benefitCostHistory": [{"fiscalYear": 2024, "asOf": R6_DATE, "value": 2.06, "scope": "project", "perspective": "whole", "sourceId": "enrichment-r6-detail"}],
    "documentedReasons": [{
        "effectiveDate": R6_DATE, "type": "delay_context",
        "summary": "一部相続人等の関係で用地調査が難航し、用地交渉の開始が令和5年度となった。",
        "sourceId": "enrichment-r6-detail",
        "note": "過去の完成予定年度を比較できる一次資料を同時に確認していないため、DELAYEDイベントには変換しない。"
    }],
})

# 5 風呂の奥川
p, c = project(
    "furonookugawa-sabo",
    "事業間連携砂防等事業（砂）風呂の奥川",
    "sabo", "砂防", "砂防課",
    ["砥部町"],
    2019, 2026, 203, 57.0, "令和5年度末", 2.24,
    "砥部町総津の土石流危険渓流で、人家と国道379号を保全する砂防事業。",
    "砂防堰堤1基、渓流保全工15m。用地買収・工事用道路は完了し、令和6年度再評価時点で砂防堰堤を施工中。",
    "https://www.pref.ehime.jp/uploaded/attachment/129982.pdf",
    coord=[132.76, 33.58],
    location_note="令和6年度再評価個表の事業箇所「伊予郡砥部町総津」を採用した概略点。施工範囲そのものを示さない。",
)
add_project(p, c, {
    "projectId": p["id"],
    "sources": [src("enrichment-r6-detail", "令和6年度 風呂の奥川 再評価個表", "https://www.pref.ehime.jp/uploaded/attachment/129982.pdf")],
    "annualBudgetHistory": [],
    "cumulativeInvestmentHistory": [{"fiscalYear": 2023, "asOf": "2024-03-31", "amountMillionYen": 116, "status": "actual", "sourceId": "enrichment-r6-detail"}],
    "benefitCostHistory": [{"fiscalYear": 2024, "asOf": R6_DATE, "value": 2.24, "scope": "project", "perspective": "whole", "sourceId": "enrichment-r6-detail"}],
    "documentedReasons": [{
        "effectiveDate": R6_DATE, "type": "delay_context",
        "summary": "堰堤工着手時に想定と異なる岩質が確認され、対策工法の追加工事が必要となり事業期間が順延。",
        "sourceId": "enrichment-r6-detail",
        "note": "比較可能な過去完成予定値を同時に収録していないため、DELAYEDイベントには変換しない。"
    }],
})

# 6 七津川
p, c = project(
    "nanatsugawa-sabo",
    "事業間連携砂防等事業（砂）七津川",
    "sabo", "砂防", "砂防課",
    ["内子町"],
    2010, 2029, 937, 35.9, "令和5年度末", 1.75,
    "内子町中田渡の七津川と支渓で、人家・国道379号・町道・公民館を保全する砂防事業。",
    "第1谷～第3谷に砂防堰堤・渓流保全工・管理用道路を整備。令和6年度再評価では全体事業費937百万円。",
    "https://www.pref.ehime.jp/uploaded/attachment/129983.pdf",
    coord=[132.67, 33.55],
)
add_project(p, c, {
    "projectId": p["id"],
    "sources": [src("enrichment-r6-detail", "令和6年度 七津川 再評価個表", "https://www.pref.ehime.jp/uploaded/attachment/129983.pdf")],
    "annualBudgetHistory": [],
    "cumulativeInvestmentHistory": [{"fiscalYear": 2023, "asOf": "2024-03-31", "amountMillionYen": 336, "status": "actual", "sourceId": "enrichment-r6-detail"}],
    "benefitCostHistory": [{"fiscalYear": 2024, "asOf": R6_DATE, "value": 1.75, "scope": "project", "perspective": "whole", "sourceId": "enrichment-r6-detail"}],
    "documentedReasons": [{
        "effectiveDate": R6_DATE, "type": "schedule_change",
        "summary": "第2谷・第3谷の堰堤規模拡大や第3谷の斜面対策等により施設規模が増え、事業期間を延長。",
        "sourceId": "enrichment-r6-detail",
        "note": "再評価個表では従前の完成予定年度にも言及するが、比較用historyには評価日の確定した観測だけを登録する。"
    }],
})

# 7 河口東地区
p, c = project(
    "koguchi-higashi-slope",
    "事業間連携砂防等事業（急）河口東地区",
    "sabo", "砂防", "砂防課",
    ["久万高原町"],
    2018, 2029, 176, 13.1, "令和5年度末", 5.21,
    "久万高原町有枝の急傾斜地で、人家・国道33号・県道209号を保全する急傾斜地崩壊対策事業。",
    "待受式擁壁工166m、落石防護柵工161m、現場打吹付法枠工472㎡。令和6年度再評価時点では工事未着手。",
    "https://www.pref.ehime.jp/uploaded/attachment/129984.pdf",
    status="planned", status_label="工事未着手",
    coord=[132.91, 33.66],
)
add_project(p, c, {
    "projectId": p["id"],
    "sources": [src("enrichment-r6-detail", "令和6年度 河口東地区 再評価個表", "https://www.pref.ehime.jp/uploaded/attachment/129984.pdf")],
    "annualBudgetHistory": [],
    "cumulativeInvestmentHistory": [{"fiscalYear": 2023, "asOf": "2024-03-31", "amountMillionYen": 23, "status": "actual", "sourceId": "enrichment-r6-detail"}],
    "benefitCostHistory": [{"fiscalYear": 2024, "asOf": R6_DATE, "value": 5.21, "scope": "project", "perspective": "whole", "sourceId": "enrichment-r6-detail"}],
    "documentedReasons": [{
        "effectiveDate": R6_DATE, "type": "delay_context",
        "summary": "令和6年5月時点で地権者1名から事業への協力が得られておらず、用地取得が進まず工事未着手。",
        "sourceId": "enrichment-r6-detail",
        "note": "完成予定年度の比較historyを伴わないため、DELAYEDイベントには変換しない。"
    }],
})

# 8 内平ヶ谷川: comparable FY2019 and FY2024 evaluations.
r1_uchi = src("source-r1-review", "令和元年度 広域河川改修事業（一）内平ヶ谷川 再評価個表",
              "https://www.pref.ehime.jp/uploaded/attachment/45448.pdf")
hist = {
    "costHistory": [
        {"asOf": "2019-08-26", "fiscalYear": 2019, "valueMillionYen": 2236, "sourceId": "source-r1-review"},
        {"asOf": R6_DATE, "fiscalYear": 2024, "valueMillionYen": 2666, "sourceId": "source-r6-detail"},
    ],
    "scheduleHistory": [
        {"asOf": "2019-08-26", "plannedCompletionFiscalYear": 2021, "sourceId": "source-r1-review"},
        {"asOf": R6_DATE, "plannedCompletionFiscalYear": 2029, "sourceId": "source-r6-detail"},
    ],
    "progressHistory": [
        {"asOf": "2019-08-26", "progressPercent": 86.0, "sourceId": "source-r1-review",
         "note": "令和元年度再評価時の事業費ベース進捗率。"},
        {"asOf": "2024-03-31", "progressPercent": 83.3, "sourceId": "source-r6-detail",
         "note": "令和5年度末の事業費ベース進捗率。事業費増額により分母が変わるため単純な物理進捗後退を意味しない。"},
    ],
}
p, c = project(
    "uchihiragatani-river",
    "広域河川改修事業（一）内平ヶ谷川",
    "river", "河川", "河川課",
    ["宇和島市"],
    1990, 2029, 2666, 83.3, "令和5年度末", None,
    "宇和島市三間町宮野下を流れる内平ヶ谷川で、河積拡大や横断工作物改築により浸水被害の軽減を図る河川改修事業。",
    "計画延長1,500m。築堤、掘削、護岸、道路橋・鉄道橋・堰の改築等を実施。",
    "https://www.pref.ehime.jp/uploaded/attachment/129985.pdf",
    coord=[132.61, 33.29],
    extra_sources=[r1_uchi],
    histories=hist,
)
add_project(p, c, {
    "projectId": p["id"],
    "sources": [
        src("enrichment-r1-review", "令和元年度 内平ヶ谷川 再評価個表", "https://www.pref.ehime.jp/uploaded/attachment/45448.pdf"),
        src("enrichment-r6-detail", "令和6年度 内平ヶ谷川 再評価個表", "https://www.pref.ehime.jp/uploaded/attachment/129985.pdf"),
    ],
    "annualBudgetHistory": [],
    "cumulativeInvestmentHistory": [
        {"fiscalYear": 2019, "asOf": "2019-08-26", "amountMillionYen": 1923.999, "status": "planned", "sourceId": "enrichment-r1-review",
         "note": "令和元年度評価時点の投資事業費。年度途中の評価のためplanned扱い。"},
        {"fiscalYear": 2023, "asOf": "2024-03-31", "amountMillionYen": 2220.8, "status": "actual", "sourceId": "enrichment-r6-detail"},
    ],
    "benefitCostHistory": [
        {"fiscalYear": 2019, "asOf": "2019-08-26", "value": 6.52, "scope": "project", "perspective": "whole", "sourceId": "enrichment-r1-review"}
    ],
    "documentedReasons": [],
})

# 9 宇和島港 大浦地区: FY2021 -> FY2024.
r3_port = src("source-r3-review", "令和3年度 港湾改修事業 宇和島港大浦地区 再評価個表",
              "https://www.pref.ehime.jp/uploaded/attachment/45483.pdf")
minutes_port = src("source-r6-minutes", "令和6年度 愛媛県公共事業評価委員会 議事要旨", R6_MINUTES)
hist = {
    "costHistory": [
        {"asOf": "2021-09-06", "fiscalYear": 2021, "valueMillionYen": 8510, "sourceId": "source-r3-review"},
        {"asOf": R6_DATE, "fiscalYear": 2024, "valueMillionYen": 9097, "sourceId": "source-r6-detail"},
    ],
    "scheduleHistory": [
        {"asOf": "2021-09-06", "plannedCompletionFiscalYear": 2025, "sourceId": "source-r3-review"},
        {"asOf": R6_DATE, "plannedCompletionFiscalYear": 2030, "sourceId": "source-r6-detail"},
    ],
    "progressHistory": [
        {"asOf": "2024-03-31", "progressPercent": 82.5, "sourceId": "source-r6-detail",
         "note": "令和5年度末の事業費ベース進捗率。"},
    ],
}
p, c = project(
    "uwajima-port-oura",
    "港湾改修事業（重）宇和島港 大浦地区",
    "port", "港湾", "港湾海岸課",
    ["宇和島市"],
    1996, 2030, 9097, 82.5, "令和5年度末", 1.10,
    "宇和島港大浦地区で、国内物流ターミナルと小型船だまりを整備する港湾改修事業。",
    "岸壁（水深5.5m）200m、道路466m、橋梁1基、ふ頭用地1.5ha等。令和6年度再評価では完成予定を令和12年度としている。",
    "https://www.pref.ehime.jp/uploaded/attachment/129986.pdf",
    coord=[132.55, 33.24],
    extra_sources=[r3_port, minutes_port],
    histories=hist,
)
add_project(p, c, {
    "projectId": p["id"],
    "sources": [
        src("enrichment-r3-review", "令和3年度 宇和島港大浦地区 再評価個表", "https://www.pref.ehime.jp/uploaded/attachment/45483.pdf"),
        src("enrichment-r6-detail", "令和6年度 宇和島港大浦地区 再評価個表", "https://www.pref.ehime.jp/uploaded/attachment/129986.pdf"),
        src("enrichment-r6-minutes", "令和6年度 愛媛県公共事業評価委員会 議事要旨", R6_MINUTES),
    ],
    "annualBudgetHistory": [],
    "cumulativeInvestmentHistory": [
        {"fiscalYear": 2023, "asOf": "2024-03-31", "amountMillionYen": 7506, "status": "actual", "sourceId": "enrichment-r6-detail"}
    ],
    "benefitCostHistory": [
        {"fiscalYear": 2021, "asOf": "2021-09-06", "value": 1.17, "scope": "project", "perspective": "whole", "sourceId": "enrichment-r3-review"},
        {"fiscalYear": 2024, "asOf": R6_DATE, "value": 1.10, "scope": "project", "perspective": "whole", "sourceId": "enrichment-r6-detail"},
    ],
    "documentedReasons": [
        {"effectiveDate": R6_DATE, "type": "cost_change", "summary": "労務単価・材料費の高騰に伴い全体事業費を増額。", "sourceId": "enrichment-r6-detail"},
        {"effectiveDate": R6_DATE, "type": "schedule_change", "summary": "物揚場の完成時期について関係者との協議等に不測の日数を要し、完成年度が遅延。", "sourceId": "enrichment-r6-minutes"},
    ],
})

# 10 余戸北吉田線: FY2022 -> FY2024.
r4_yogo = src("source-r4-review", "令和4年度 都市計画街路事業（都）余戸北吉田線 再評価個表",
              "https://www.pref.ehime.jp/uploaded/attachment/45508.pdf")
minutes_yogo = src("source-r6-minutes", "令和6年度 愛媛県公共事業評価委員会 議事要旨", R6_MINUTES)
hist = {
    "costHistory": [
        {"asOf": "2022-08-29", "fiscalYear": 2022, "valueMillionYen": 8296, "sourceId": "source-r4-review"},
        {"asOf": R6_DATE, "fiscalYear": 2024, "valueMillionYen": 9784, "sourceId": "source-r6-detail"},
    ],
    "scheduleHistory": [
        {"asOf": "2022-08-29", "plannedCompletionFiscalYear": 2027, "sourceId": "source-r4-review"},
        {"asOf": R6_DATE, "plannedCompletionFiscalYear": 2027, "sourceId": "source-r6-detail"},
    ],
    "progressHistory": [
        {"asOf": "2022-08-29", "progressPercent": 89.2, "sourceId": "source-r4-review",
         "note": "令和4年度末見込の事業費ベース進捗率。"},
        {"asOf": R6_DATE, "progressPercent": 80.6, "sourceId": "source-r6-detail",
         "note": "令和6年度末見込。全体事業費の増額で分母が増えたため、前回より進捗率が低下。"},
    ],
}
p, c = project(
    "yogo-kita-yoshida-street",
    "都市計画街路事業（都）余戸北吉田線",
    "urban", "都市計画街路", "都市整備課",
    ["松山市"],
    2009, 2027, 9784, 80.6, "令和6年度末見込", None,
    "松山外環状道路空港線の一般道路部として、県道伊予松山港線から県道松山空港線まで1.3kmを整備する都市計画街路事業。",
    "計画延長1.3km、総幅員21.5m。松山市内の渋滞緩和と松山IC・空港・港へのアクセス向上を目的とする。",
    "https://www.pref.ehime.jp/uploaded/attachment/129989.pdf",
    coord=[132.72, 33.83],
    extra_sources=[r4_yogo, minutes_yogo],
    histories=hist,
)
add_project(p, c, {
    "projectId": p["id"],
    "sources": [
        src("enrichment-r4-review", "令和4年度 余戸北吉田線 再評価個表", "https://www.pref.ehime.jp/uploaded/attachment/45508.pdf"),
        src("enrichment-r6-detail", "令和6年度 余戸北吉田線 再評価個表", "https://www.pref.ehime.jp/uploaded/attachment/129989.pdf"),
        src("enrichment-r6-minutes", "令和6年度 愛媛県公共事業評価委員会 議事要旨", R6_MINUTES),
    ],
    "annualBudgetHistory": [],
    "cumulativeInvestmentHistory": [
        {"fiscalYear": 2022, "asOf": "2022-08-29", "amountMillionYen": 7399, "status": "planned", "sourceId": "enrichment-r4-review",
         "note": "令和4年度末見込。"},
        {"fiscalYear": 2024, "asOf": R6_DATE, "amountMillionYen": 7882, "status": "planned", "sourceId": "enrichment-r6-detail",
         "note": "令和6年度末見込。"},
    ],
    "benefitCostHistory": [
        {"fiscalYear": 2022, "asOf": "2022-08-29", "value": 1.3, "scope": "network", "perspective": "whole", "sourceId": "enrichment-r4-review",
         "note": "松山外環状道路空港線全体としての評価。"},
        {"fiscalYear": 2022, "asOf": "2022-08-29", "value": 3.2, "scope": "network", "perspective": "remaining", "sourceId": "enrichment-r4-review",
         "note": "松山外環状道路空港線全体としての評価。"},
        {"fiscalYear": 2024, "asOf": R6_DATE, "value": 1.2, "scope": "network", "perspective": "whole", "sourceId": "enrichment-r6-detail",
         "note": "松山外環状道路空港線全体としての評価。"},
        {"fiscalYear": 2024, "asOf": R6_DATE, "value": 1.9, "scope": "network", "perspective": "remaining", "sourceId": "enrichment-r6-detail",
         "note": "松山外環状道路空港線全体としての評価。"},
    ],
    "documentedReasons": [{
        "effectiveDate": R6_DATE, "type": "cost_change",
        "summary": "物価・労務費上昇等と渋滞対策の追加により全体事業費を増額。",
        "sourceId": "enrichment-r6-minutes",
        "note": "議事要旨では完成年度までの労務費・物価上昇額を見込んだと説明。"
    }],
})

# 11 Matsuyama delegated project. The official minutes provide B/C and current construction context but not a comparable full financial snapshot.
p, c = project(
    "izumi-housing-regeneration",
    "地域居住機能再生推進事業（和泉周辺地区）",
    "urban", "公営住宅・地域再生", "住宅課",
    ["松山市"],
    None, None, None, None, None, 0.95,
    "松山市の市営住宅を集約して建て替え、周辺の居住機能再生を進める事業。",
    "令和6年度愛媛県公共事業評価委員会の松山市付託案件。議事要旨ではB/C 0.95（国基準0.8以上）を参考値として扱う趣旨が示されている。",
    None,
    status="under_construction", status_label="事業中",
    coord=[132.76, 33.82],
    extra_sources=[src("source-r6-minutes", "令和6年度 愛媛県公共事業評価委員会 議事要旨", R6_MINUTES)],
)
p["operator"] = "松山市"
p["locationSource"] = "source-r6-minutes"
p["provenance"]["benefitCostRatio"] = "source-r6-minutes"
p["provenance"]["summary"] = "source-r6-minutes"
p["provenance"]["scope"] = "source-r6-minutes"
p["provenance"]["geometryRef"] = "source-r6-minutes"
add_project(p, c, {
    "projectId": p["id"],
    "sources": [src("enrichment-r6-minutes", "令和6年度 愛媛県公共事業評価委員会 議事要旨", R6_MINUTES)],
    "annualBudgetHistory": [],
    "cumulativeInvestmentHistory": [],
    "benefitCostHistory": [{
        "fiscalYear": 2024, "asOf": R6_DATE, "value": 0.95, "scope": "project", "perspective": "whole",
        "sourceId": "enrichment-r6-minutes",
        "note": "議事要旨では国基準0.8以上。本事業は福祉に近い性質を持つため、対応方針決定上の参考値として扱うことが望ましいとの意見が示された。"
    }],
    "documentedReasons": [],
})

def upsert(items, additions, key):
    by_key = {item[key]: item for item in items}
    for item in additions:
        by_key[item[key]] = item
    old_keys = [item[key] for item in items]
    new_keys = [item[key] for item in additions if item[key] not in old_keys]
    return [by_key[k] for k in old_keys + new_keys]

data = json.loads(PROJECTS_PATH.read_text(encoding="utf-8"))
geo = json.loads(GEOJSON_PATH.read_text(encoding="utf-8"))
enrichment = json.loads(ENRICHMENT_PATH.read_text(encoding="utf-8"))

data["datasetTitle"] = "Ehime Civil Works Monitor Phase 2.1 dataset — FY2024 cohort complete"
data["generatedAt"] = ACCESS
data["projects"] = upsert(data["projects"], projects_to_add, "id")

existing_geo = {f.get("properties", {}).get("projectId"): f for f in geo["features"]}
for f in geo_to_add:
    existing_geo[f["properties"]["projectId"]] = f
old_geo_ids = [f.get("properties", {}).get("projectId") for f in geo["features"]]
new_geo_ids = [f["properties"]["projectId"] for f in geo_to_add if f["properties"]["projectId"] not in old_geo_ids]
geo["features"] = [existing_geo[k] for k in old_geo_ids + new_geo_ids]

enrichment["generatedAt"] = ACCESS
enrichment["records"] = upsert(enrichment["records"], enrichment_to_add, "projectId")

PROJECTS_PATH.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
GEOJSON_PATH.write_text(json.dumps(geo, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
ENRICHMENT_PATH.write_text(json.dumps(enrichment, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

types = TYPES_PATH.read_text(encoding="utf-8")
types = types.replace(
    "export type ProjectCategory = 'river' | 'coast' | 'sabo' | 'road' | 'urban';",
    "export type ProjectCategory = 'river' | 'coast' | 'sabo' | 'road' | 'urban' | 'agriculture' | 'port';",
)
TYPES_PATH.write_text(types, encoding="utf-8")

validator = VALIDATOR_PATH.read_text(encoding="utf-8")
validator = validator.replace(
    'CATEGORIES = {"river", "coast", "sabo", "road", "urban"}',
    'CATEGORIES = {"river", "coast", "sabo", "road", "urban", "agriculture", "port"}',
)
VALIDATOR_PATH.write_text(validator, encoding="utf-8")

styles = STYLES_PATH.read_text(encoding="utf-8")
needle = ".category-urban{background:#a74b52}"
if ".category-agriculture" not in styles:
    styles = styles.replace(
        needle,
        needle + ".category-agriculture{background:#687a39}.category-port{background:#356a9a}",
    )
STYLES_PATH.write_text(styles, encoding="utf-8")

readme = README_PATH.read_text(encoding="utf-8")
readme = readme.replace(
    "Phase 2.1では現10案件を一次資料でさらに深掘りし、年度予算・累計投資事業費・B/C履歴・文書化された増額／延期事情を別レイヤーとして追加します。",
    "Phase 2.1では当初10案件を一次資料でさらに深掘りし、年度予算・累計投資事業費・B/C履歴・文書化された増額／延期事情を別レイヤーとして追加したうえで、令和6年度公共事業評価委員会の再評価13案件（松山市付託1件を含む）をcohort単位で収録しました。",
)
readme = readme.replace(
    "初回のPhase 2.1 enrichmentは現10案件すべてを対象としています。累計投資とB/Cは10案件に収録し、案件単位の年度予算は一次資料で直接確認できた案件のみ収録します。比較可能な複数時点B/Cは大洲西道路、夜昼道路、JR松山駅付近連続立体交差事業から開始しています。",
    "Phase 2.1 enrichmentは掲載全案件にレコードを持たせ、確認できない値は空配列のまま保持します。令和6年度cohortは県事業12件と松山市付託1件の全13案件を収録し、比較可能な過年度資料がある内平ヶ谷川・宇和島港・余戸北吉田線等では履歴まで追加しています。",
)
README_PATH.write_text(readme, encoding="utf-8")

archive = ARCHIVE_DOC_PATH.read_text(encoding="utf-8")
marker = "## FY2024 cohort completion"
if marker not in archive:
    archive += f"""

{marker}

The FY2024 (令和6年度) re-evaluation cohort is now complete: all 13 projects considered by the committee are represented, including the one Matsuyama City delegated project.

Newly added after the first two-project pass:

- 水利施設等保全高度化事業（灘地区）
- 水利施設等保全高度化事業（吉田地区）
- 事業間連携砂防等事業（芹谷川）
- 事業間連携砂防等事業（大平川）
- 事業間連携砂防等事業（風呂の奥川）
- 事業間連携砂防等事業（七津川）
- 事業間連携砂防等事業（河口東地区）
- 広域河川改修事業（内平ヶ谷川）
- 港湾改修事業（宇和島港 大浦地区）
- 都市計画街路事業（余戸北吉田線）
- 地域居住機能再生推進事業（和泉周辺地区、松山市付託）

The same conservative rule remains in force: a project can enter the map with a sparse current snapshot when the committee confirms its identity and continuation, while longitudinal history is added only where evaluation dates and definitions are comparable. In particular, the Matsuyama delegated project is included with the B/C and context available in the official committee minutes, while unverified cost/schedule/progress values remain null.

This expansion also introduces `agriculture` and `port` as first-class map categories.
"""
ARCHIVE_DOC_PATH.write_text(archive, encoding="utf-8")

workflow = ROOT / ".github/workflows/apply-r6-cohort-expansion.yml"
try:
    workflow.unlink()
except FileNotFoundError:
    pass
try:
    Path(__file__).unlink()
except FileNotFoundError:
    pass

print(f"Expanded dataset to {len(data['projects'])} projects / {len(geo['features'])} features / {len(enrichment['records'])} enrichment records.")
