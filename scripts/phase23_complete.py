#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
projects_path = ROOT / 'public/data/projects.json'
enrichment_path = ROOT / 'public/data/enrichment.json'

projects_doc = json.loads(projects_path.read_text(encoding='utf-8'))
enrichment_doc = json.loads(enrichment_path.read_text(encoding='utf-8'))
projects = {p['id']: p for p in projects_doc['projects']}
records = {r['projectId']: r for r in enrichment_doc['records']}


def add_source(project, source):
    if not any(s['id'] == source['id'] for s in project['sources']):
        project['sources'].append(source)


def set_fields(pid, source, **fields):
    p = projects[pid]
    add_source(p, source)
    for key, value in fields.items():
        p[key] = value
        if key in {'startFiscalYear','plannedCompletionFiscalYear','totalProjectCostMillionYen','progressPercent','landAcquisitionProgressPercent','benefitCostRatio','status','summary'}:
            p.setdefault('provenance', {})[key] = source['id']
    p['lastVerified'] = '2026-08-31'
    return p


def set_history(pid, kind, entries):
    projects[pid][kind] = entries


def enrich(pid, source, cumulative=None, bc=None, reasons=None):
    r = records[pid]
    if not any(s['id'] == source['id'] for s in r['sources']):
        r['sources'].append(source)
    if cumulative is not None:
        r['cumulativeInvestmentHistory'] = cumulative
    if bc is not None:
        r['benefitCostHistory'] = bc
    if reasons is not None:
        r['documentedReasons'] = reasons

# 1. 東予港: R3 -> R4(第2回) is a comparable re-evaluation sequence.
r3_toyo = {'id':'phase23-toyo-r3','title':'令和3年度 愛媛県公共事業評価委員会 再評価事業一覧表','publisher':'愛媛県','url':'https://www.pref.ehime.jp/uploaded/attachment/45475.pdf','accessed':'2026-08-31'}
r4_toyo = {'id':'phase23-toyo-r4','title':'港湾改修事業（東予港）再評価個表','publisher':'愛媛県','url':'https://www.pref.ehime.jp/uploaded/attachment/45521.pdf','accessed':'2026-08-31','note':'資料上の全体事業費は「約62億円」と表記。'}
p = set_fields('toyo-port-improvement', r4_toyo, startFiscalYear=1994, plannedCompletionFiscalYear=2030, totalProjectCostMillionYen=6200, benefitCostRatio=1.10)
add_source(p, r3_toyo)
p['scope'] = '東予港西条地区の小型船だまり整備。令和4年度第2回再評価では令和12年度末の完成を目標とし、総事業費は約62億円、B/Cは1.10。'
set_history('toyo-port-improvement','costHistory',[
    {'asOf':'2021-09-06','fiscalYear':2021,'valueMillionYen':4927,'sourceId':'phase23-toyo-r3','note':'令和3年度一覧表の現計画。'},
    {'asOf':'2023-01-19','fiscalYear':2022,'valueMillionYen':6200,'sourceId':'phase23-toyo-r4','note':'令和4年度第2回再評価資料。資料表記は約62億円。'},
])
set_history('toyo-port-improvement','scheduleHistory',[
    {'asOf':'2021-09-06','plannedCompletionFiscalYear':2025,'sourceId':'phase23-toyo-r3'},
    {'asOf':'2023-01-19','plannedCompletionFiscalYear':2030,'sourceId':'phase23-toyo-r4'},
])
enrich('toyo-port-improvement', r4_toyo, bc=[
    {'fiscalYear':2021,'asOf':'2021-09-06','value':1.13,'scope':'project','perspective':'whole','sourceId':'phase23-toyo-r3'},
    {'fiscalYear':2022,'asOf':'2023-01-19','value':1.10,'scope':'project','perspective':'whole','sourceId':'phase23-toyo-r4'},
], reasons=[
    {'effectiveDate':'2023-01-19','type':'cost_increase','summary':'資材価格等の高騰、労務単価の上昇、設計基準改訂等を踏まえて事業費を見直し','sourceId':'phase23-toyo-r4'}
])
# enrichment helper only added r4 source; add r3 too.
if not any(s['id']=='phase23-toyo-r3' for s in records['toyo-port-improvement']['sources']): records['toyo-port-improvement']['sources'].append(r3_toyo)

# 2. 三島川之江港金子地区: FY2026 new-project evaluation.
mishima = {'id':'phase23-mishima-r8-eval','title':'三島川之江港金子地区 複合一貫輸送ターミナル整備事業 新規事業採択時評価','publisher':'国土交通省','url':'https://www.mlit.go.jp/policy/shingikai/content/001991682.pdf','accessed':'2026-08-31'}
set_fields('mishima-kawanoe-kaneko-roro', mishima, startFiscalYear=2026, totalProjectCostMillionYen=23200)
projects['mishima-kawanoe-kaneko-roro']['scope'] = '令和8年度新規事業化。国の新規事業採択時評価では総事業費232億円。完成時期は「令和10年代半ば」とされ、正確な年度は公表値として確認できないためnullを維持。'
set_history('mishima-kawanoe-kaneko-roro','costHistory',[{'asOf':'2026-03-23','fiscalYear':2026,'valueMillionYen':23200,'sourceId':'phase23-mishima-r8-eval'}])

# 3. 界谷川: current R7-R11 social-capital plan.
sakaidani = {'id':'phase23-sakaidani-r7-plan','title':'社会資本総合整備計画 防災・安全交付金（界谷川広域河川改修事業）','publisher':'愛媛県','url':'https://www.pref.ehime.jp/uploaded/attachment/139993.pdf','accessed':'2026-08-31','note':'R7-R11計画に記載された要素事業の全体事業費・実施期間。'}
set_fields('sakaidani-river', sakaidani, plannedCompletionFiscalYear=2029, totalProjectCostMillionYen=1205)
projects['sakaidani-river']['scope'] = 'R7-R11社会資本総合整備計画では、護岸・掘削・排水機場整備、全体事業費1,205百万円、R7-R11の実施期間として掲載。旧計画の金額とは事業範囲の比較可能性を確認できないため履歴接続しない。'

# 4. 浅川
asakawa = {'id':'phase23-asakawa-r5','title':'二級河川 浅川 広域河川改修事業 再評価個表','publisher':'愛媛県','url':'https://www.pref.ehime.jp/uploaded/attachment/100919.pdf','accessed':'2026-08-31'}
set_fields('asakawa-river', asakawa, startFiscalYear=1973, plannedCompletionFiscalYear=2033, totalProjectCostMillionYen=17440, progressPercent=89.8, landAcquisitionProgressPercent=87.2, benefitCostRatio=11.46)
projects['asakawa-river']['progressAsOf'] = '令和4年度末'
projects['asakawa-river']['scope'] = '改修区間6,830m。令和5年度再評価では全体事業費17,440百万円、令和4年度末の事業進捗89.8%、用地87.2%、B/C 11.46。'
set_history('asakawa-river','costHistory',[{'asOf':'2023-10-26','fiscalYear':2023,'valueMillionYen':17440,'sourceId':'phase23-asakawa-r5'}])
set_history('asakawa-river','scheduleHistory',[{'asOf':'2023-10-26','plannedCompletionFiscalYear':2033,'sourceId':'phase23-asakawa-r5'}])
set_history('asakawa-river','progressHistory',[{'asOf':'2023-03-31','progressPercent':89.8,'sourceId':'phase23-asakawa-r5','note':'令和4年度末の事業費換算進捗率。'}])
enrich('asakawa-river', asakawa, cumulative=[{'fiscalYear':2022,'asOf':'2023-03-31','amountMillionYen':15666,'status':'actual','sourceId':'phase23-asakawa-r5','note':'令和4年度末投資事業費。'}], bc=[{'fiscalYear':2023,'asOf':'2023-10-26','value':11.46,'scope':'project','perspective':'whole','sourceId':'phase23-asakawa-r5'}])

# 5. 大川
okawa = {'id':'phase23-okawa-r5','title':'二級河川 大川 広域河川改修事業 再評価個表','publisher':'愛媛県','url':'https://www.pref.ehime.jp/uploaded/attachment/100920.pdf','accessed':'2026-08-31'}
set_fields('okawa-river', okawa, startFiscalYear=1970, plannedCompletionFiscalYear=2028, totalProjectCostMillionYen=5500, progressPercent=91.9, landAcquisitionProgressPercent=91.5, benefitCostRatio=22.82)
projects['okawa-river']['progressAsOf'] = '令和4年度末'
projects['okawa-river']['scope'] = '全体計画2,650m。令和5年度再評価では全体事業費5,500百万円、令和4年度末の事業進捗91.9%、用地91.5%、B/C 22.82。'
set_history('okawa-river','costHistory',[{'asOf':'2023-10-26','fiscalYear':2023,'valueMillionYen':5500,'sourceId':'phase23-okawa-r5'}])
set_history('okawa-river','scheduleHistory',[{'asOf':'2023-10-26','plannedCompletionFiscalYear':2028,'sourceId':'phase23-okawa-r5'}])
set_history('okawa-river','progressHistory',[{'asOf':'2023-03-31','progressPercent':91.9,'sourceId':'phase23-okawa-r5','note':'令和4年度末の事業費換算進捗率。'}])
enrich('okawa-river', okawa, cumulative=[{'fiscalYear':2022,'asOf':'2023-03-31','amountMillionYen':5055,'status':'actual','sourceId':'phase23-okawa-r5','note':'令和4年度末投資事業費。'}], bc=[{'fiscalYear':2023,'asOf':'2023-10-26','value':22.82,'scope':'project','perspective':'whole','sourceId':'phase23-okawa-r5'}])

# 6. 中ノ谷川
nakanotani = {'id':'phase23-nakanotani-r5','title':'通常砂防事業（中ノ谷川）再評価個表','publisher':'愛媛県','url':'https://www.pref.ehime.jp/uploaded/attachment/100897.pdf','accessed':'2026-08-31'}
set_fields('nakanotani-sabo', nakanotani, startFiscalYear=2016, totalProjectCostMillionYen=360, progressPercent=73.6, landAcquisitionProgressPercent=100.0, benefitCostRatio=15.98)
projects['nakanotani-sabo']['progressAsOf'] = '令和4年度末'
projects['nakanotani-sabo']['scope'] = '透過型堰堤1基、渓流保全工27.5m、管理用道路325m。R5再評価では総事業費360百万円、R4末事業進捗73.6%、用地100%、B/C 15.98。R6完成見込みは既に経過しているため現在の完成予定年度には採用しない。'
set_history('nakanotani-sabo','costHistory',[{'asOf':'2023-10-26','fiscalYear':2023,'valueMillionYen':360,'sourceId':'phase23-nakanotani-r5'}])
set_history('nakanotani-sabo','progressHistory',[{'asOf':'2023-03-31','progressPercent':73.6,'sourceId':'phase23-nakanotani-r5','note':'令和4年度末の事業費換算進捗率。'}])
enrich('nakanotani-sabo', nakanotani, cumulative=[{'fiscalYear':2022,'asOf':'2023-03-31','amountMillionYen':265,'status':'actual','sourceId':'phase23-nakanotani-r5','note':'令和4年度末投資事業費。'}], bc=[{'fiscalYear':2023,'asOf':'2023-10-26','value':15.98,'scope':'project','perspective':'whole','sourceId':'phase23-nakanotani-r5'}], reasons=[{'effectiveDate':'2023-10-26','type':'delay_context','summary':'西日本豪雨被災地域への重点投資により当該事業の年間投資額が減少し、2年程度遅延','sourceId':'phase23-nakanotani-r5','note':'現在の完成予定年度を別資料で確認できないため、DELAYEDイベントには変換しない。'}])

# 7. 松山道4車線化: current NEXCO progress is definitionally not a single physical-progress percentage.
expressway = {'id':'phase23-matsuyama-exp-current','title':'E56 松山自動車道（伊予IC～大洲IC）4車線化 建設進捗情報','publisher':'NEXCO西日本','url':'https://corp.w-nexco.co.jp/activity/open_info/progress/individual/58/','accessed':'2026-08-31'}
set_fields('matsuyama-expressway-four-lane', expressway, landAcquisitionProgressPercent=100.0)
projects['matsuyama-expressway-four-lane']['scope'] = '対象3区間はいずれも令和8年7月末時点で用地取得率100%。工事着手率は区間別に100%・31%・0%であり、物理的進捗率とは定義が異なるためprogressPercentへ集約しない。'

# 8. 野村大橋
nomura_bridge = {'id':'phase23-nomura-bridge-current','title':'一級河川肱川（西予市野村町野村）大規模特定河川事業の概要','publisher':'愛媛県','url':'https://www.pref.ehime.jp/page/1711.html','accessed':'2026-08-31'}
set_fields('nomura-bridge', nomura_bridge, startFiscalYear=2023, plannedCompletionFiscalYear=2026)
projects['nomura-bridge']['scope'] = '野村大橋架替え。仮橋工事は令和5年4月着手、令和7年3月に仮橋へ交通切替。令和7年度に本橋工事着手、令和8年度に本橋完成・交通切替予定。'
set_history('nomura-bridge','scheduleHistory',[{'asOf':'2025-03-07','plannedCompletionFiscalYear':2026,'sourceId':'phase23-nomura-bridge-current','note':'本橋完成・交通切替予定年度。'}])

# 9. 肱川事業間連携
hijikawa = {'id':'phase23-hijikawa-r5','title':'事業間連携河川事業（一級河川肱川）再評価個表','publisher':'愛媛県','url':'https://www.pref.ehime.jp/uploaded/attachment/100886.pdf','accessed':'2026-08-31'}
set_fields('hijikawa-interproject-river', hijikawa, startFiscalYear=2020, plannedCompletionFiscalYear=2027, totalProjectCostMillionYen=5000, progressPercent=21.4, landAcquisitionProgressPercent=30.5, benefitCostRatio=1.13)
projects['hijikawa-interproject-river']['progressAsOf'] = '令和4年度末'
projects['hijikawa-interproject-river']['scope'] = '計画延長2,200m。R5再評価では総事業費5,000百万円、R4末事業進捗21.4%、用地30.5%、B/C 1.13。'
set_history('hijikawa-interproject-river','costHistory',[{'asOf':'2023-10-26','fiscalYear':2023,'valueMillionYen':5000,'sourceId':'phase23-hijikawa-r5'}])
set_history('hijikawa-interproject-river','scheduleHistory',[{'asOf':'2023-10-26','plannedCompletionFiscalYear':2027,'sourceId':'phase23-hijikawa-r5'}])
set_history('hijikawa-interproject-river','progressHistory',[{'asOf':'2023-03-31','progressPercent':21.4,'sourceId':'phase23-hijikawa-r5','note':'令和4年度末の事業費換算進捗率。'}])
enrich('hijikawa-interproject-river', hijikawa, cumulative=[{'fiscalYear':2022,'asOf':'2023-03-31','amountMillionYen':1070,'status':'actual','sourceId':'phase23-hijikawa-r5','note':'令和4年度末投資事業費。'}], bc=[{'fiscalYear':2023,'asOf':'2023-10-26','value':1.13,'scope':'project','perspective':'whole','sourceId':'phase23-hijikawa-r5'}], reasons=[{'effectiveDate':'2023-10-26','type':'cost_increase_context','summary':'社会経済情勢の急激な変化による全体事業費の増額を理由に再評価','sourceId':'phase23-hijikawa-r5','note':'比較可能な直前総事業費を今回確認できていないためCOST+イベントは生成しない。'}])

# 10. 東鎌川: current R7-R11 social-capital plan; actual project inception is not inferred from plan start.
higashikama = {'id':'phase23-higashikama-r7-plan','title':'土砂災害につよい愛ある県土づくり 社会資本総合整備計画（東鎌川通常砂防事業）','publisher':'愛媛県','url':'https://www.pref.ehime.jp/uploaded/attachment/165838.pdf','accessed':'2026-08-31'}
set_fields('higashikama-sabo', higashikama, plannedCompletionFiscalYear=2026, totalProjectCostMillionYen=44, benefitCostRatio=3.08)
projects['higashikama-sabo']['scope'] = 'R7-R11社会資本総合整備計画では東鎌川通常砂防事業をR7-R8、全体事業費44百万円、B/C 3.08として掲載。計画開始年度を事業採択年度とはみなさない。'

# 11. 津羽井地区
tsuwai = {'id':'phase23-tsuwai-r7-plan','title':'土砂災害につよい愛ある県土づくり 社会資本総合整備計画（津羽井地区地すべり対策事業）','publisher':'愛媛県','url':'https://www.pref.ehime.jp/uploaded/attachment/165838.pdf','accessed':'2026-08-31'}
set_fields('tsuwai-landslide', tsuwai, plannedCompletionFiscalYear=2029, totalProjectCostMillionYen=300, benefitCostRatio=35.7)
projects['tsuwai-landslide']['scope'] = 'R7-R11社会資本総合整備計画では水路工、全体事業費300百万円、B/C 35.7、R7-R11の実施期間として掲載。過年度にも同地区で事業があるためR7を事業採択年度とはみなさない。'

# 12. 八幡浜道路: completed project. Current status comes from the official opening announcement.
yawatahama_open = {'id':'phase23-yawatahama-open','title':'大洲・八幡浜自動車道「八幡浜道路」の開通式の開催について','publisher':'愛媛県','url':'https://www.pref.ehime.jp/page/8595.html','accessed':'2026-08-31'}
yawatahama_eval = {'id':'phase23-yawatahama-r3','title':'道路改築事業 一般国道197号 八幡浜道路 再評価個表','publisher':'愛媛県','url':'https://www.pref.ehime.jp/uploaded/attachment/45484.pdf','accessed':'2026-08-31'}
p = set_fields('yawatahama-road', yawatahama_open, status='completed', startFiscalYear=2005, plannedCompletionFiscalYear=2022, totalProjectCostMillionYen=25200)
p['statusLabel'] = '供用済'
add_source(p, yawatahama_eval)
p['provenance']['benefitCostRatio'] = 'phase23-yawatahama-r3'
p['benefitCostRatio'] = 0.53
p['scope'] = '延長3.8km、2車線。事業期間H17-R4、総事業費約252億円。令和5年3月25日に全区間を一般交通へ供用。R3再評価時の事業全体B/Cは0.53。'
set_history('yawatahama-road','costHistory',[{'asOf':'2023-03-25','fiscalYear':2022,'valueMillionYen':25200,'sourceId':'phase23-yawatahama-open','note':'開通時公表の総事業費約252億円。'}])
set_history('yawatahama-road','scheduleHistory',[{'asOf':'2023-03-25','plannedCompletionFiscalYear':2022,'sourceId':'phase23-yawatahama-open','note':'公表された事業期間H17-R4。'}])
enrich('yawatahama-road', yawatahama_eval, cumulative=[{'fiscalYear':2020,'asOf':'2021-03-31','amountMillionYen':23070,'status':'actual','sourceId':'phase23-yawatahama-r3','note':'令和3年度評価一覧表のR2年度までの事業費。'}], bc=[{'fiscalYear':2021,'asOf':'2021-09-06','value':0.53,'scope':'project','perspective':'whole','sourceId':'phase23-yawatahama-r3'}])

# 13. 野村ダム改良
nomura_dam = {'id':'phase23-nomura-dam-r6-paper','title':'野村ダム施設改良工事の進捗と最新技術の採用','publisher':'国土交通省 四国地方整備局','url':'https://www.skr.mlit.go.jp/kikaku/kenkyu/r6/ronbun/13.pdf','accessed':'2026-08-31','note':'全体工事費は資料上「約205億円」。'}
set_fields('nomura-dam-improvement', nomura_dam, plannedCompletionFiscalYear=2027, totalProjectCostMillionYen=20500)
projects['nomura-dam-improvement']['scope'] = '放流設備増設等の野村ダム施設改良。国交省技術資料では令和9年度末完成を目標、全体工事費は約205億円。'

projects_doc['schemaVersion'] = '2.2.0'
projects_doc['datasetTitle'] = 'Ehime Civil Works Monitor Phase 2.3 — Data Completion'
projects_doc['generatedAt'] = '2026-08-31'
projects_doc['dataPolicy'] = '公的機関の一次資料を優先し、不明値は推測せずnullとする。Phase 2.3ではInventory案件を個別一次資料で再調査し、比較可能性・scope・基準時点を確認できた値だけsnapshot/history/enrichmentへ昇格する。古い完成見込み、区間別工事着手率、計画期間を現在の物理進捗や事業採択年度へ機械的に読み替えない。'
enrichment_doc['generatedAt'] = '2026-08-31'

projects_path.write_text(json.dumps(projects_doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
enrichment_path.write_text(json.dumps(enrichment_doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Phase 2.3 data completion applied')
