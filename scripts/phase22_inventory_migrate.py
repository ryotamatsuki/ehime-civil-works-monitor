#!/usr/bin/env python3
"""One-shot Phase 2.2 migration. Remove after canonical files are committed."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS_PATH = ROOT / "public/data/projects.json"
GEOJSON_PATH = ROOT / "public/data/projects.geojson"
ENRICHMENT_PATH = ROOT / "public/data/enrichment.json"
TODAY = "2026-08-31"

MAP_SOURCE = {
    "id": "source-ehime-civil-works-2026-map",
    "title": "えひめの土木2026 愛媛県管内図",
    "publisher": "愛媛県",
    "url": "https://www.pref.ehime.jp/uploaded/life/149017_306429_misc.pdf",
    "accessed": TODAY,
    "note": "令和8年度時点の主要土木事業のInventory seed。数値情報の出典には使用しない。",
}

ROAD_PROGRESS_SOURCE = {
    "id": "source-skr-road-progress-r7",
    "title": "四国地方整備局の事業進捗等について（道路・令和7年3月末時点）",
    "publisher": "国土交通省 四国地方整備局",
    "url": "https://www.skr.mlit.go.jp/infomation/jigyoshintyoku/pdf/douro.pdf",
    "accessed": TODAY,
}


def source(source_id, title, publisher, url, note=None):
    item = {"id": source_id, "title": title, "publisher": publisher, "url": url, "accessed": TODAY}
    if note:
        item["note"] = note
    return item


def project(
    pid, name, category, label, operator, department, municipalities, status, status_label,
    summary, scope, geometry, extra_sources=None, start=None, completion=None, cost=None,
    progress=None, progress_as_of=None, benefit_cost=None,
):
    sources = [copy.deepcopy(MAP_SOURCE)] + copy.deepcopy(extra_sources or [])
    provenance = {
        "name": "source-ehime-civil-works-2026-map",
        "category": "source-ehime-civil-works-2026-map",
        "status": "source-ehime-civil-works-2026-map",
        "summary": "source-ehime-civil-works-2026-map",
        "geometryRef": "source-ehime-civil-works-2026-map",
    }
    numeric_source = sources[-1]["id"] if len(sources) > 1 else None
    if numeric_source:
        for key, value in (
            ("startFiscalYear", start),
            ("plannedCompletionFiscalYear", completion),
            ("totalProjectCostMillionYen", cost),
            ("progressPercent", progress),
            ("benefitCostRatio", benefit_cost),
        ):
            if value is not None:
                provenance[key] = numeric_source
    item = {
        "id": pid,
        "name": name,
        "category": category,
        "categoryLabel": label,
        "operator": operator,
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
        "benefitCostRatio": benefit_cost,
        "lastVerified": TODAY,
        "summary": summary,
        "scope": scope,
        "geometryRef": pid,
        "locationAccuracy": "approximate",
        "locationSource": "source-ehime-civil-works-2026-map",
        "locationNote": "えひめの土木2026管内図等を参考に作成した概略位置・概略ルート。公式の施工範囲・道路線形を示すものではない。",
        "sources": sources,
        "provenance": provenance,
        "costHistory": [],
        "scheduleHistory": [],
        "progressHistory": [],
    }
    if cost is not None and progress is not None and progress_as_of == "令和7年3月末":
        item["costHistory"] = [{
            "asOf": "2025-03-31", "fiscalYear": 2024, "valueMillionYen": cost,
            "sourceId": "source-skr-road-progress-r7",
            "note": "四国地方整備局の事業進捗資料に記載された総事業費。",
        }]
        item["progressHistory"] = [{
            "asOf": "2025-03-31", "progressPercent": progress,
            "sourceId": "source-skr-road-progress-r7",
            "note": "四国地方整備局資料の令和7年3月末事業進捗率。",
        }]
    return item, {
        "type": "Feature",
        "id": pid,
        "properties": {"projectId": pid, "locationAccuracy": "approximate"},
        "geometry": geometry,
    }


IWAGI_SOURCE = source(
    "source-iwagi-official", "上島架橋（岩城橋）", "愛媛県",
    "https://www.pref.ehime.jp/page/8597.html",
)
TOYO_SOURCE = source(
    "source-toyo-review", "令和4年度愛媛県公共事業評価委員会（港湾改修事業・東予港）", "愛媛県",
    "https://www.pref.ehime.jp/page/8359.html",
)
IMABARI_SOURCE = copy.deepcopy(ROAD_PROGRESS_SOURCE)
MISHIMA_SOURCE = source(
    "source-mishima-port", "三島川之江港の整備", "国土交通省 四国地方整備局",
    "https://www.pa.skr.mlit.go.jp/matsuyama/5works/harbors/mishima/work.html",
    "既存港湾の事業同一性確認用。令和8年度新規事業の数値根拠には使用しない。",
)
SAKAIDANI_SOURCE = source(
    "source-sakaidani-review", "愛媛県公共事業評価委員会資料（界谷川）", "愛媛県",
    "https://www.pref.ehime.jp/page/8227.html",
)
SAWAZU_SOURCE = source(
    "source-sawazu-official", "愛媛県優良建設工事等表彰資料（沢津地区）", "愛媛県",
    "https://eweb.pref.ehime.jp/uploaded/life/128516_226208_misc.pdf",
)
R5_EVAL_SOURCE = source(
    "source-r5-eval", "令和5年度愛媛県公共事業評価委員会", "愛媛県",
    "https://www.pref.ehime.jp/page/49383.html",
)
MATSuyama_PORT_SOURCE = source(
    "source-matsuyama-port", "港湾整備によるストック効果（松山港・東予港）", "愛媛県",
    "https://www.pref.ehime.jp/page/8116.html",
)
NAKANOTANI_SOURCE = source(
    "source-nakanotani-zone", "土砂災害（特別）警戒区域（伊予市）", "愛媛県",
    "https://www.pref.ehime.jp/page/10251.html",
)
OUTER_RING_SOURCE = source(
    "source-outer-ring", "松山外環状道路整備事業", "愛媛県",
    "https://www.pref.ehime.jp/site/chuyo/1472.html",
)
NEXCO_SOURCE = source(
    "source-nexco-fourlane", "E56 松山自動車道（伊予IC～大洲IC）4車線化", "NEXCO西日本",
    "https://corp.w-nexco.co.jp/activity/open_info/progress/individual/58/",
)
HIJI_NOMURA_SOURCE = source(
    "source-hiji-nomura", "肱川大規模特定河川事業（野村地区）", "愛媛県",
    "https://www.pref.ehime.jp/page/1711.html",
)
HIJI_NOMURA_REVIEW = source(
    "source-hiji-nomura-review", "肱川大規模特定河川事業 再評価資料", "愛媛県",
    "https://www.pref.ehime.jp/uploaded/attachment/100885.pdf",
)
EAST_KAMA_SOURCE = source(
    "source-east-kama-plan", "愛媛県砂防関係事業計画（東鎌川）", "愛媛県",
    "https://www.pref.ehime.jp/uploaded/attachment/165838.pdf",
)
TSUWAI_SOURCE = source(
    "source-tsuwai-plan", "防災・減災、国土強靱化のための5か年加速化対策（津羽井地区）", "愛媛県",
    "https://www.pref.ehime.jp/uploaded/attachment/131215.pdf",
)
TSUBASA_SOURCE = source(
    "source-tsubasa-road", "令和6年度道路事業箇所資料（嵐田之浜岩松線 翼橋）", "国土交通省",
    "https://www.mlit.go.jp/road/ir/ir-yosan/r6yhai/pdf/ho/1238k.pdf",
)
KITAYAMA_SOURCE = source(
    "source-kitayama-plan", "防災・減災、国土強靱化のための5か年加速化対策（北山崎海岸）", "愛媛県",
    "https://www.pref.ehime.jp/uploaded/attachment/131215.pdf",
)
YAWATAHAMA_SOURCE = source(
    "source-yawatahama-road", "国道197号 八幡浜道路", "愛媛県",
    "https://www.pref.ehime.jp/page/8581.html",
)
SUKUMO_SOURCE = copy.deepcopy(ROAD_PROGRESS_SOURCE)
NOMURA_DAM_SOURCE = source(
    "source-nomura-dam", "野村ダム改良事業", "国土交通省 四国地方整備局",
    "https://www.skr.mlit.go.jp/oozu/kawa/ksq_202210500_1.html",
)

NEW = []

def add(*args, **kwargs):
    NEW.append(project(*args, **kwargs))

add("iwagi-bridge", "一般県道岩城弓削線 上島架橋（岩城橋）", "road", "道路", "愛媛県", "道路建設課", ["上島町"], "completed", "供用済", "上島町の岩城島と生名島を結ぶ上島架橋の岩城橋。", "岩城橋は令和4年3月20日に開通。管内図では主要事業として掲載されている。", {"type":"Point","coordinates":[133.154,34.253]}, [IWAGI_SOURCE], start=2013, cost=18300)
add("toyo-port-improvement", "東予港 港湾改修事業", "port", "港湾", "愛媛県", "港湾海岸課", ["西条市"], "under_construction", "事業中", "東予港で岸壁・防波堤等の港湾機能を整備・改良する事業。", "管内図の主要事業パネルと公共事業評価資料で事業存在を確認。個別施設の事業費を港全体の総事業費として合算しない。", {"type":"Point","coordinates":[133.105,33.949]}, [TOYO_SOURCE])
add("imabari-road", "一般国道196号 今治道路", "road", "道路", "国土交通省 四国地方整備局", "松山河川国道事務所", ["今治市"], "under_construction", "事業中", "今治小松自動車道の一部を構成する延長10.3kmの自動車専用道路。", "令和7年3月末の四国地方整備局資料では総事業費780億円、事業進捗率約77%。一部区間の開通予定を全体完成予定として扱わない。", {"type":"LineString","coordinates":[[132.98,34.07],[133.01,34.04],[133.05,34.00]]}, [IMABARI_SOURCE], start=2001, cost=78000, progress=77, progress_as_of="令和7年3月末")
add("mishima-kawanoe-kaneko-roro", "三島川之江港 金子地区 複合一貫輸送ターミナル整備事業", "port", "港湾", "愛媛県・国土交通省", "港湾海岸課・松山港湾・空港整備事務所", ["四国中央市"], "planned", "新規事業化", "三島川之江港金子地区で進める複合一貫輸送ターミナル整備。", "えひめの土木2026では令和8年度新規事業化として掲載。既存の国際物流ターミナル整備と数値履歴を混同しない。", {"type":"Point","coordinates":[133.55,33.97]}, [MISHIMA_SOURCE])
add("sakaidani-river", "二級河川 界谷川 広域河川改修事業", "river", "河川", "愛媛県", "河川課", ["西条市"], "under_construction", "事業中", "界谷川の浸水被害軽減を目的とする河川改修事業。", "管内図では排水機場を含む主要事業として掲載。詳細数値は比較可能な一次資料を確認後に追加する。", {"type":"Point","coordinates":[133.17,33.93]}, [SAKAIDANI_SOURCE])
add("sawazu-slope", "沢津地区 急傾斜地崩壊対策事業", "sabo", "砂防・急傾斜", "愛媛県", "砂防課", ["今治市"], "under_construction", "事業中", "今治市伯方町木浦の沢津地区で行う急傾斜地崩壊対策事業。", "管内図の主要事業パネルと愛媛県資料から事業同一性を確認。", {"type":"Point","coordinates":[133.10,34.20]}, [SAWAZU_SOURCE])
add("asakawa-river", "二級河川 浅川 広域河川改修事業", "river", "河川", "愛媛県", "河川課", ["今治市"], "under_construction", "事業中", "今治市の浅川で進める広域河川改修事業。", "令和5年度公共事業評価委員会と令和8年度管内図で事業存在を確認。", {"type":"Point","coordinates":[132.99,34.08]}, [R5_EVAL_SOURCE])
add("okawa-river", "二級河川 大川 広域河川改修事業", "river", "河川", "愛媛県", "河川課", ["松山市"], "under_construction", "事業中", "松山市の大川で進める広域河川改修事業。", "令和5年度公共事業評価委員会と令和8年度管内図で事業存在を確認。", {"type":"Point","coordinates":[132.75,33.90]}, [R5_EVAL_SOURCE])
add("matsuyama-port-improvement", "松山港 港湾改修事業", "port", "港湾", "愛媛県・国土交通省", "港湾海岸課・松山港湾・空港整備事務所", ["松山市"], "under_construction", "事業中", "松山港で港湾機能の強化・改良を進める事業群。", "管内図の主要事業として確認。個別地区・施設の費用を港全体の総事業費として合算しない。", {"type":"Point","coordinates":[132.70,33.86]}, [MATSuyama_PORT_SOURCE])
add("nakanotani-sabo", "中ノ谷川 通常砂防事業", "sabo", "砂防", "愛媛県", "砂防課", ["伊予市"], "under_construction", "事業中", "伊予市八倉の中ノ谷川で進める通常砂防事業。", "同名渓流との誤統合を避け、伊予市八倉の事業として登録。", {"type":"Point","coordinates":[132.72,33.72]}, [NAKANOTANI_SOURCE])
add("matsuyama-outer-ring-airport", "一般国道56号 松山外環状道路 空港線", "road", "道路", "国土交通省 四国地方整備局", "松山河川国道事務所", ["松山市"], "under_construction", "事業中", "国道56号から松山空港方面を結ぶ松山外環状道路の空港線。", "令和7年3月末時点で総事業費672億円、事業進捗率約77%。一部区間は供用済だが事業全体は継続中。", {"type":"LineString","coordinates":[[132.73,33.80],[132.71,33.81],[132.69,33.82]]}, [ROAD_PROGRESS_SOURCE, OUTER_RING_SOURCE], start=2008, cost=67200, progress=77, progress_as_of="令和7年3月末")
add("matsuyama-expressway-four-lane", "E56 松山自動車道 伊予IC～大洲IC 4車線化", "road", "道路", "西日本高速道路株式会社（NEXCO西日本）", "四国支社 愛媛工事事務所", ["伊予市","内子町","大洲市"], "under_construction", "事業中", "松山自動車道の伊予IC～大洲IC間で進める4車線化事業。", "一部区間は4車線化済みだが、内子・大洲地区等で工事・調査が継続しているため事業全体をcompletedとはしない。", {"type":"LineString","coordinates":[[132.76,33.78],[132.70,33.66],[132.65,33.55]]}, [NEXCO_SOURCE])
add("hijikawa-nomura-major-river", "一級河川 肱川 大規模特定河川事業（野村地区）", "river", "河川", "愛媛県", "河川課", ["西予市"], "under_construction", "事業中", "西予市野村地区の肱川で河道拡幅や橋梁架替等を行う河川改修事業。", "愛媛県資料では令和元年度事業着手、全体事業費45億円、完成目標令和9年度。野村大橋は関連する橋梁架替として別Inventoryにも掲載。", {"type":"Point","coordinates":[132.65,33.37]}, [HIJI_NOMURA_SOURCE, HIJI_NOMURA_REVIEW], start=2019, completion=2027, cost=4500)
add("nomura-bridge", "一般国道441号 野村大橋", "road", "道路・橋梁", "愛媛県", "道路建設課・河川課", ["西予市"], "under_construction", "事業中", "肱川大規模特定河川事業に伴う国道441号野村大橋の架替。", "河川事業と関連するが、えひめの土木2026では独立した主要事業として掲載されるためrelated projectとして別IDで管理する。", {"type":"Point","coordinates":[132.649,33.371]}, [HIJI_NOMURA_SOURCE])
add("tsushima-road", "一般国道56号 津島道路", "road", "道路", "国土交通省 四国地方整備局", "中村河川国道事務所", ["宇和島市","愛南町"], "under_construction", "事業中", "愛南町柏から宇和島市津島町岩松を結ぶ一般国道56号の自動車専用道路。", "令和7年3月末時点で総事業費491億円、事業進捗率約58%。", {"type":"LineString","coordinates":[[132.56,33.18],[132.53,33.10],[132.51,33.03]]}, [ROAD_PROGRESS_SOURCE], start=2012, cost=49100, progress=58, progress_as_of="令和7年3月末")
add("hijikawa-interproject-river", "一級河川 肱川 事業間連携河川事業", "river", "河川", "愛媛県", "河川課", ["大洲市"], "under_construction", "事業中", "肱川水系で国の治水対策と連携して進める事業間連携河川事業。", "令和5年度公共事業評価委員会の同名事業と管内図を照合。工区別の費用を無条件に事業全体へ合算しない。", {"type":"Point","coordinates":[132.55,33.51]}, [R5_EVAL_SOURCE])
add("higashikama-sabo", "東鎌川 通常砂防事業", "sabo", "砂防", "愛媛県", "砂防課", ["宇和島市"], "under_construction", "事業中", "宇和島市の東鎌川で進める通常砂防事業。", "管内図と愛媛県の砂防関係計画資料で事業存在を確認。", {"type":"Point","coordinates":[132.55,33.20]}, [EAST_KAMA_SOURCE])
add("tsuwai-landslide", "津羽井地区 地すべり対策事業", "sabo", "地すべり", "愛媛県", "砂防課", ["八幡浜市"], "under_construction", "事業中", "八幡浜市津羽井で集水井・横ボーリング・アンカー等を行う地すべり対策事業。", "管内図と国土強靱化関係資料で事業存在・場所を確認。", {"type":"Point","coordinates":[132.42,33.47]}, [TSUWAI_SOURCE])
add("tsubasa-bridge", "一般県道 嵐田之浜岩松線 翼橋", "road", "道路・橋梁", "愛媛県", "道路建設課", ["宇和島市"], "under_construction", "事業中", "一般県道嵐田之浜岩松線で整備する翼橋。", "管内図の主要事業パネルと国土交通省道路事業箇所資料で事業名・事業主体を確認。", {"type":"Point","coordinates":[132.54,33.13]}, [TSUBASA_SOURCE])
add("kitayamazaki-coast", "北山崎海岸 高潮対策事業", "coast", "海岸", "愛媛県", "港湾海岸課", ["伊予市"], "under_construction", "事業中", "伊予市本郡の北山崎海岸で進める高潮対策事業。", "管内図と国土強靱化関係資料で事業存在を確認。", {"type":"Point","coordinates":[132.68,33.75]}, [KITAYAMA_SOURCE])
add("kawanoe-mishima-bypass", "一般国道11号 川之江三島バイパス", "road", "道路", "国土交通省 四国地方整備局", "松山河川国道事務所", ["四国中央市"], "under_construction", "事業中", "四国中央市川之江町から中之庄町を結ぶ国道11号バイパス。", "令和7年3月末時点で総事業費722億円、事業進捗率約60%。一部区間は供用済。", {"type":"LineString","coordinates":[[133.55,33.98],[133.50,33.98],[133.45,33.98]]}, [ROAD_PROGRESS_SOURCE], start=1972, cost=72200, progress=60, progress_as_of="令和7年3月末")
add("niihama-bypass", "一般国道11号 新居浜バイパス", "road", "道路", "国土交通省 四国地方整備局", "松山河川国道事務所", ["新居浜市"], "under_construction", "事業中", "新居浜市船木から大生院を結ぶ国道11号バイパス。", "令和7年3月末時点で総事業費609億円、事業進捗率約78%。複数区間が供用済だが事業全体は継続中。", {"type":"LineString","coordinates":[[133.33,33.95],[133.30,33.94],[133.27,33.93]]}, [ROAD_PROGRESS_SOURCE], start=1987, cost=60900, progress=78, progress_as_of="令和7年3月末")
add("komatsu-bypass", "一般国道11号 小松バイパス", "road", "道路", "国土交通省 四国地方整備局", "松山河川国道事務所", ["西条市"], "under_construction", "事業中", "西条市小松町新屋敷から安井を結ぶ国道11号バイパス。", "令和7年3月末時点で総事業費203億円、事業進捗率約57%。一部区間は供用済。", {"type":"LineString","coordinates":[[133.13,33.89],[133.10,33.88],[133.07,33.87]]}, [ROAD_PROGRESS_SOURCE], start=1991, cost=20300, progress=57, progress_as_of="令和7年3月末")
add("yawatahama-road", "一般国道197号 八幡浜道路", "road", "道路", "愛媛県", "道路建設課", ["八幡浜市"], "completed", "供用済", "大洲・八幡浜自動車道を構成する八幡浜道路。", "八幡浜市郷～大平の延長3.8km区間は令和5年3月25日に開通。完成済事業のため進捗率100%とは推定しない。", {"type":"LineString","coordinates":[[132.43,33.46],[132.42,33.45],[132.41,33.44]]}, [YAWATAHAMA_SOURCE])
add("sukumo-uchiumi-misho-uchiumi", "一般国道56号 宿毛内海道路（御荘～内海）", "road", "道路", "国土交通省 四国地方整備局", "中村河川国道事務所", ["愛南町"], "under_construction", "事業中", "愛南町御荘平城から柏を結ぶ宿毛内海道路の御荘～内海区間。", "令和7年3月末時点で総事業費473億円、事業進捗率約2%。", {"type":"LineString","coordinates":[[132.52,32.96],[132.50,32.92],[132.48,32.88]]}, [SUKUMO_SOURCE], start=2022, cost=47300, progress=2, progress_as_of="令和7年3月末")
add("matsuyama-outer-ring-inter-east", "一般国道33号 松山外環状道路 インター東線", "road", "道路", "国土交通省 四国地方整備局", "松山河川国道事務所", ["松山市"], "under_construction", "事業中", "松山市北土居から来住町を結ぶ松山外環状道路インター東線。", "令和7年3月末時点で総事業費398億円、事業進捗率約8%。", {"type":"LineString","coordinates":[[132.77,33.78],[132.79,33.79],[132.81,33.80]]}, [ROAD_PROGRESS_SOURCE, OUTER_RING_SOURCE], start=2018, cost=39800, progress=8, progress_as_of="令和7年3月末")
add("nomura-dam-improvement", "野村ダム改良事業", "dam", "ダム", "国土交通省 四国地方整備局", "大洲河川国道事務所", ["西予市"], "under_construction", "事業中", "野村ダムに新たな放流設備等を整備し治水機能を強化する改良事業。", "令和8年度管内図で主要事業として位置を確認し、四国地方整備局の公式説明で事業内容を確認。", {"type":"Point","coordinates":[132.67,33.37]}, [NOMURA_DAM_SOURCE])

EXISTING_MAP_MATCHES = {
    "nishimachi-nakamura-street",
    "jr-matsuyama-grade-separation",
    "yohiru-road",
    "uwajima-port-oura",
    "narubae-coast-tsunami",
    "sanaki-widening",
}


def main():
    data = json.loads(PROJECTS_PATH.read_text(encoding="utf-8"))
    geo = json.loads(GEOJSON_PATH.read_text(encoding="utf-8"))
    enrichment = json.loads(ENRICHMENT_PATH.read_text(encoding="utf-8"))

    data["schemaVersion"] = "2.2.0"
    data["datasetTitle"] = "Ehime Civil Works Monitor Phase 2.2 — Project Inventory Expansion"
    data["generatedAt"] = TODAY
    data["dataPolicy"] = (
        "公的機関の一次資料を優先し、不明値は推測せずnullとする。Phase 2.2では事業存在・名称・位置・出典を確認できた案件をInventoryとして収録し、"
        "総事業費・完成予定・進捗等は追加一次資料で確認できた場合だけsnapshot/historyへ昇格する。概略位置・概略ルートは公式施工範囲・線形を示さない。"
    )

    by_id = {item["id"]: item for item in data["projects"]}
    feature_ids = {feature.get("properties", {}).get("projectId") for feature in geo["features"]}
    enrichment_ids = {record["projectId"] for record in enrichment["records"]}

    for pid in EXISTING_MAP_MATCHES:
        existing = by_id.get(pid)
        if not existing:
            continue
        if not any(src.get("id") == MAP_SOURCE["id"] for src in existing.get("sources", [])):
            existing["sources"].append(copy.deepcopy(MAP_SOURCE))

    for item, feature in NEW:
        if item["id"] not in by_id:
            data["projects"].append(item)
            by_id[item["id"]] = item
        if item["id"] not in feature_ids:
            geo["features"].append(feature)
            feature_ids.add(item["id"])
        if item["id"] not in enrichment_ids:
            enrichment["records"].append({
                "projectId": item["id"],
                "sources": [],
                "annualBudgetHistory": [],
                "cumulativeInvestmentHistory": [],
                "benefitCostHistory": [],
                "documentedReasons": [],
            })
            enrichment_ids.add(item["id"])

    geo["name"] = "ehime-civil-works-monitor-phase22"
    enrichment["generatedAt"] = TODAY

    PROJECTS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    GEOJSON_PATH.write_text(json.dumps(geo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ENRICHMENT_PATH.write_text(json.dumps(enrichment, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Phase 2.2 migration: {len(data['projects'])} projects, {len(geo['features'])} features, {len(enrichment['records'])} enrichment records")


if __name__ == "__main__":
    main()
