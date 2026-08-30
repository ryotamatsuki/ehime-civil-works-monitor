#!/usr/bin/env python3
from pathlib import Path

path = Path('src/main.ts')
text = path.read_text(encoding='utf-8')

def replace_once(old: str, new: str, label: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f'Phase 2.4 patch target not found: {label}')
    text = text.replace(old, new, 1)

replace_once(
'''function header(subtitle: string) {
  return `<header class="site-header"><a class="brand" href="${base}">EHIME CIVIL WORKS MONITOR</a><p>${esc(subtitle)}</p></header>`;
}''',
'''function header(subtitle: string) {
  return `<header class="site-header"><a class="brand" href="${base}">EHIME CIVIL WORKS MONITOR</a><p>INFRASTRUCTURE OBSERVATORY · ${esc(subtitle)}</p></header>`;
}''',
'header',
)

replace_once(
'''      const icon = L.divIcon({
        className: 'marker-wrap',
        html: `<span class="marker category-${project?.category ?? 'river'}"></span>`,
        iconSize: [18, 18],
        iconAnchor: [9, 9],
      });''',
'''      const level = project ? getMonitoringLevel(project, ids.has(project.id)) : 'inventory';
      const eventTypes = project ? new Set(getProjectChangeEvents(project).map((event) => event.type)) : new Set<ChangeEvent['type']>();
      const size = level === 'enriched' ? 20 : level === 'inventory' ? 14 : 17;
      const ring = eventTypes.has('cost_increase')
        ? 'outline:3px solid #c59a50;outline-offset:2px;'
        : eventTypes.has('delayed')
          ? 'outline:3px solid #a86159;outline-offset:2px;'
          : '';
      const icon = L.divIcon({
        className: 'marker-wrap',
        html: `<span class="marker category-${project?.category ?? 'river'}" style="width:${size}px;height:${size}px;${ring}"></span>`,
        iconSize: [28, 28],
        iconAnchor: [14, 14],
      });''',
'marker visual encoding',
)

replace_once(
'''    <section class="hero"><div><p class="eyebrow">EHIME CIVIL WORKS INVENTORY</p><h1>愛媛の公共事業を<br>広く、深く追う。</h1><p class="lead">「えひめの土木2026」等の一次資料から主要事業をInventory化し、総事業費・工程・進捗を確認できた案件だけを段階的に履歴・変更検知へ接続する非公式Web GISです。</p></div><aside class="notice"><strong>PHASE 2.2 / 2026-08-31</strong><p>INVENTORYは事業存在・位置・概要を確認した層です。未確認の事業費・完成年度・進捗率は推測せず空欄とし、概略ルートは公式線形を意味しません。</p></aside></section>
    <div id="dashboard-root">${dashboard(dataset.projects, ids)}</div>
    <div id="changes-root">${recentChanges(dataset.projects)}</div>
    <section class="workspace">''',
'''    <section class="hero"><div><p class="eyebrow">EHIME INFRASTRUCTURE OBSERVATORY</p><h1>公共事業の現在地を、<br>地図と変化で読む。</h1><p class="lead">県内50事業を地図で俯瞰し、一次資料で確認できた総事業費・工程・進捗・B/C・履歴を同じ画面で追跡します。値が確認できない案件は推測せずInventoryとして明示します。</p></div><aside class="notice"><strong>PHASE 2.4 · VISUAL SYSTEM / 2026-08-31</strong><p>地図を主役に、Data Depth・変更履歴・一次資料への導線を視覚階層化。概略点・概略ルートは正確な施工区域や公式線形を意味しません。</p></aside></section>
    <div id="dashboard-root">${dashboard(dataset.projects, ids)}</div>
    <section class="workspace">''',
'home hero and map-first ordering',
)

replace_once(
'''</div></section>
    <section class="project-section">''',
'''</div></section>
    <div id="changes-root">${recentChanges(dataset.projects)}</div>
    <section class="project-section">''',
'recent changes placement',
)

replace_once(
'''  const inventoryNote = getMonitoringLevel(project, ids.has(project.id)) === 'inventory'
    ? '<p class="inventory-detail-note">この案件はInventory層です。存在・位置・概要を一次資料で確認していますが、総事業費・完成年度・進捗率は確認できた資料がないため推測していません。</p>'
    : '';
  app.innerHTML = `${header('PROJECT DETAIL')}''',
'''  const inventoryNote = getMonitoringLevel(project, ids.has(project.id)) === 'inventory'
    ? '<p class="inventory-detail-note">この案件はInventory層です。存在・位置・概要を一次資料で確認していますが、総事業費・完成年度・進捗率は確認できた資料がないため推測していません。</p>'
    : '';
  const detailEvents = getProjectChangeEvents(project);
  const latestCostChange = [...detailEvents].reverse().find((event) => event.type === 'cost_increase' || event.type === 'cost_decrease');
  const latestScheduleChange = [...detailEvents].reverse().find((event) => event.type === 'delayed' || event.type === 'accelerated');
  const costKpi = project.totalProjectCostMillionYen === null ? '—' : formatMillionYen(project.totalProjectCostMillionYen);
  const periodKpi = project.plannedCompletionFiscalYear === null ? '—' : `${formatFiscalYear(project.plannedCompletionFiscalYear)}年度`;
  const progressKpi = project.progressPercent === null ? '—' : `${project.progressPercent}%`;
  const detailKpis = `<section class="dashboard detail-kpis"><div class="metric"><strong>${costKpi}</strong><span>COST<br>${latestCostChange ? esc(eventValue(latestCostChange)) : 'CURRENT SNAPSHOT'}</span></div><div class="metric"><strong>${periodKpi}</strong><span>COMPLETION<br>${latestScheduleChange ? esc(eventValue(latestScheduleChange)) : 'CURRENT TARGET'}</span></div><div class="metric"><strong>${progressKpi}</strong><span>PROGRESS<br>${project.progressAsOf ? esc(project.progressAsOf) : 'PUBLIC VALUE'}</span></div></section>`;
  app.innerHTML = `${header('PROJECT DETAIL')}''',
'detail KPI calculation',
)

replace_once(
'''<h1>${esc(project.name)}</h1><p class="lead">${esc(project.summary)}</p>${inventoryNote}</section><section class="detail-layout">''',
'''<h1>${esc(project.name)}</h1><p class="lead">${esc(project.municipalities.join('・'))} · ${esc(project.operator)} · VERIFIED ${esc(project.lastVerified)}</p><p class="lead">${esc(project.summary)}</p>${inventoryNote}</section>${detailKpis}<section class="detail-layout">''',
'detail hierarchy',
)

path.write_text(text, encoding='utf-8')
print('Phase 2.4 main.ts redesign applied')
