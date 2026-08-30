import 'leaflet/dist/leaflet.css';
import './styles.css';
import L from 'leaflet';
import type { FeatureCollection, Geometry } from 'geojson';
import type { EnrichmentCollection } from './enrichment-types';
import { hasEnrichmentData } from './enrichment';
import type { ChangeEvent, MonitoringLevel, Project, ProjectCollection, ProjectSource } from './types';
import {
  aggregateProjects,
  filterProjects,
  formatFiscalYear,
  formatMillionYen,
  getAllChangeEvents,
  getMonitoringLevel,
  getProjectChangeEvents,
  getProjectIdFromPath,
  type ProjectFilters,
} from './domain';

const base = import.meta.env.BASE_URL;
const app = document.querySelector<HTMLDivElement>('#app');
if (!app) throw new Error('App root not found');

const esc = (value: string) => value.replace(/[&<>'"]/g, (char) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#039;', '"': '&quot;',
}[char] ?? char));

async function loadData() {
  const [projectsResponse, geoResponse, enrichmentResponse] = await Promise.all([
    fetch(`${base}data/projects.json`),
    fetch(`${base}data/projects.geojson`),
    fetch(`${base}data/enrichment.json`),
  ]);
  if (!projectsResponse.ok || !geoResponse.ok) throw new Error('データを読み込めませんでした。');
  const enrichment = enrichmentResponse.ok
    ? await enrichmentResponse.json() as EnrichmentCollection
    : { enrichmentSchemaVersion: '2.1.0', generatedAt: '', dataPolicy: '', records: [] };
  return {
    dataset: await projectsResponse.json() as ProjectCollection,
    geojson: await geoResponse.json() as FeatureCollection<Geometry>,
    enrichment,
  };
}

function enrichedIds(enrichment: EnrichmentCollection): Set<string> {
  return new Set(enrichment.records.filter(hasEnrichmentData).map((record) => record.projectId));
}

function header(subtitle: string) {
  return `<header class="site-header"><a class="brand" href="${base}">EHIME CIVIL WORKS MONITOR</a><p>INFRASTRUCTURE OBSERVATORY · ${esc(subtitle)}</p></header>`;
}

function projectUrl(project: Project) {
  return `${base}projects/${encodeURIComponent(project.id)}/`;
}

const depthLabels: Record<MonitoringLevel, string> = {
  inventory: 'INVENTORY',
  snapshot: 'SNAPSHOT',
  history: 'HISTORY',
  enriched: 'ENRICHED',
};

function depthBadge(project: Project, ids: ReadonlySet<string>) {
  const level = getMonitoringLevel(project, ids.has(project.id));
  return `<span class="depth-badge depth-${level}" title="Data Depth">${depthLabels[level]}</span>`;
}

function popup(project: Project, ids: ReadonlySet<string>) {
  const cost = project.totalProjectCostMillionYen === null
    ? ''
    : `<dt>全体事業費</dt><dd>${formatMillionYen(project.totalProjectCostMillionYen)}</dd>`;
  const progress = project.progressPercent === null
    ? ''
    : `<dt>進捗率</dt><dd>${project.progressPercent}%</dd>`;
  return `<article class="map-popup"><div class="popup-labels"><span class="eyebrow">${esc(project.categoryLabel)} · ${esc(project.statusLabel)}</span>${depthBadge(project, ids)}</div><h3>${esc(project.name)}</h3><dl><dt>事業主体</dt><dd>${esc(project.operator)}</dd><dt>市町</dt><dd>${esc(project.municipalities.join('・'))}</dd>${cost}${progress}</dl><a href="${projectUrl(project)}">詳細・履歴・一次情報 →</a></article>`;
}

function mapBase(id: string, center: L.LatLngExpression, zoom: number) {
  const map = L.map(id).setView(center, zoom);
  L.tileLayer('https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png', {
    attribution: '<a href="https://maps.gsi.go.jp/development/ichiran.html" target="_blank" rel="noreferrer">国土地理院</a>',
    maxZoom: 18,
  }).addTo(map);
  return map;
}

function addLayer(
  map: L.Map,
  projects: Project[],
  geojson: FeatureCollection<Geometry>,
  ids: ReadonlySet<string>,
) {
  const visibleIds = new Set(projects.map((project) => project.id));
  const byId = new Map(projects.map((project) => [project.id, project]));
  const featureCollection: FeatureCollection<Geometry> = {
    type: 'FeatureCollection',
    features: geojson.features.filter((feature) => visibleIds.has(String(feature.properties?.projectId ?? ''))),
  };
  return L.geoJSON(featureCollection, {
    pointToLayer: (feature, latlng) => {
      const project = byId.get(String(feature.properties?.projectId ?? ''));
      const level = project ? getMonitoringLevel(project, ids.has(project.id)) : 'inventory';
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
      });
      return L.marker(latlng, { icon });
    },
    style: (feature) => {
      const project = byId.get(String(feature?.properties?.projectId ?? ''));
      return {
        weight: 4,
        opacity: .82,
        fillOpacity: .14,
        dashArray: project?.locationAccuracy === 'approximate' ? '7 6' : undefined,
      };
    },
    onEachFeature: (feature, layer) => {
      const project = byId.get(String(feature.properties?.projectId ?? ''));
      if (project) layer.bindPopup(popup(project, ids), { maxWidth: 340 });
    },
  }).addTo(map);
}

function dashboard(projects: Project[], ids: ReadonlySet<string>) {
  const stats = aggregateProjects(projects, new Date(), ids);
  return `<section class="dashboard dashboard-phase22">
    <div class="metric"><strong>${stats.projectCount}</strong><span>PROJECTS<br>登録事業</span></div>
    <div class="metric"><strong>${stats.monitoredCount}</strong><span>MONITORED<br>数値観測あり</span></div>
    <div class="metric"><strong>${stats.historyCount}</strong><span>HISTORY+<br>履歴・深掘り</span></div>
    <div class="metric"><strong>${(stats.totalKnownCostMillionYen / 100).toLocaleString('ja-JP', { maximumFractionDigits: 1 })}億円</strong><span>TOTAL COST<br>確認済み ${stats.knownCostCount}件のみ</span></div>
    <div class="metric"><strong>${stats.costIncreaseProjectCount}</strong><span>COST+<br>増額履歴あり</span></div>
    <div class="metric"><strong>${stats.delayedProjectCount}</strong><span>DELAYED<br>完成予定後ろ倒し</span></div>
  </section>`;
}

function options(values: string[]) {
  return [...new Set(values)].sort((a, b) => a.localeCompare(b, 'ja')).map((value) => `<option value="${esc(value)}">${esc(value)}</option>`).join('');
}

const eventLabels: Record<ChangeEvent['type'], string> = {
  cost_increase: 'COST+',
  cost_decrease: 'COST−',
  delayed: 'DELAYED',
  accelerated: 'EARLIER',
  progress_updated: 'UPDATED',
};

function signed(value: number, digits = 1) {
  const rounded = Number(value.toFixed(digits));
  return `${rounded > 0 ? '+' : ''}${rounded.toLocaleString('ja-JP')}`;
}

function eventValue(event: ChangeEvent) {
  if (event.type === 'cost_increase' || event.type === 'cost_decrease') {
    const percent = event.percentChange === undefined ? '' : ` / ${signed(event.percentChange)}%`;
    return `${formatMillionYen(event.previousValue)} → ${formatMillionYen(event.currentValue)} · ${signed(event.absoluteChange / 100)}億円${percent}`;
  }
  if (event.type === 'delayed' || event.type === 'accelerated') {
    return `${formatFiscalYear(event.previousValue)} → ${formatFiscalYear(event.currentValue)} · ${signed(event.absoluteChange, 0)}年度`;
  }
  return `${event.previousValue}% → ${event.currentValue}% · ${signed(event.absoluteChange)}pt`;
}

function eventBadge(event: ChangeEvent) {
  return `<span class="change-badge change-${event.type} severity-${event.severity}">${eventLabels[event.type]}</span>`;
}

function projectBadges(project: Project) {
  const types = new Set<ChangeEvent['type']>();
  const events = getProjectChangeEvents(project).filter((event) => {
    if (types.has(event.type)) return false;
    types.add(event.type);
    return true;
  });
  return events.length ? `<div class="change-badges">${events.map(eventBadge).join('')}</div>` : '';
}

function card(project: Project, ids: ReadonlySet<string>) {
  const numbers: string[] = [];
  if (project.totalProjectCostMillionYen !== null) numbers.push(`<span><small>全体事業費</small>${formatMillionYen(project.totalProjectCostMillionYen)}</span>`);
  if (project.progressPercent !== null) numbers.push(`<span><small>進捗率</small>${project.progressPercent}%</span>`);
  const numericBlock = numbers.length ? `<div class="project-numbers">${numbers.join('')}</div>` : '<p class="inventory-note">数値情報は追加一次資料を確認後に収録します。</p>';
  return `<article class="project-card"><div class="project-card-top"><span class="tag">${esc(project.categoryLabel)}</span><span class="status">${esc(project.statusLabel)}</span></div><div class="project-depth-row">${depthBadge(project, ids)}</div>${projectBadges(project)}<h3><a href="${projectUrl(project)}">${esc(project.name)}</a></h3><p>${esc(project.municipalities.join('・'))} / ${esc(project.operator)}</p>${numericBlock}</article>`;
}

function recentChanges(projects: Project[]) {
  const byId = new Map(projects.map((project) => [project.id, project]));
  const events = getAllChangeEvents(projects).slice(0, 8);
  const body = events.length ? events.map((event) => {
    const project = byId.get(event.projectId);
    if (!project) return '';
    return `<a class="change-card" href="${projectUrl(project)}"><div class="change-card-head">${eventBadge(event)}<time>${esc(event.effectiveDate)}</time></div><strong>${esc(project.name)}</strong><p>${esc(eventValue(event))}</p></a>`;
  }).join('') : '<p class="empty-change">比較可能な複数時点の履歴から検出された変更はありません。</p>';
  return `<section class="changes-section"><div class="section-heading"><div><p class="eyebrow">CHANGE DETECTION</p><h2>Recent Changes</h2></div><p>比較可能な一次資料の履歴から機械的に導出。Inventory案件に変更イベントを推測付与しません。</p></div><div class="change-grid">${body}</div></section>`;
}

function home(dataset: ProjectCollection, geojson: FeatureCollection<Geometry>, enrichment: EnrichmentCollection) {
  const ids = enrichedIds(enrichment);
  const categories = new Map(dataset.projects.map((project) => [project.categoryLabel, project.category]));
  const statuses = new Map(dataset.projects.map((project) => [project.statusLabel, project.status]));
  app.innerHTML = `${header('愛媛県内の主要公共事業を広く把握し、確認できた案件は履歴まで追跡します。')}<main>
    <section class="hero"><div><p class="eyebrow">EHIME INFRASTRUCTURE OBSERVATORY</p><h1>公共事業の現在地を、<br>地図と変化で読む。</h1><p class="lead">県内50事業を地図で俯瞰し、一次資料で確認できた総事業費・工程・進捗・B/C・履歴を同じ画面で追跡します。値が確認できない案件は推測せずInventoryとして明示します。</p></div><aside class="notice"><strong>PHASE 2.4 · VISUAL SYSTEM / 2026-08-31</strong><p>地図を主役に、Data Depth・変更履歴・一次資料への導線を視覚階層化。概略点・概略ルートは正確な施工区域や公式線形を意味しません。</p></aside></section>
    <div id="dashboard-root">${dashboard(dataset.projects, ids)}</div>
    <section class="workspace"><aside class="filters"><div class="filter-heading"><h2>Filter</h2><button id="reset" type="button">リセット</button></div>
      <label>検索<input id="q" type="search" placeholder="事業名・市町名"></label>
      <label>カテゴリー<select id="category"><option value="">すべて</option>${[...categories].sort().map(([label, value]) => `<option value="${value}">${esc(label)}</option>`).join('')}</select></label>
      <label>事業主体<select id="operator"><option value="">すべて</option>${options(dataset.projects.map((project) => project.operator))}</select></label>
      <label>市町<select id="municipality"><option value="">すべて</option>${options(dataset.projects.flatMap((project) => project.municipalities))}</select></label>
      <label>ステータス<select id="status"><option value="">すべて</option>${[...statuses].sort().map(([label, value]) => `<option value="${value}">${esc(label)}</option>`).join('')}</select></label>
      <label>Data Depth<select id="depth"><option value="">すべて</option><option value="inventory">Inventory</option><option value="snapshot">Snapshot+</option><option value="history">History+</option><option value="enriched">Enriched</option></select></label>
      <label>変更<select id="alert"><option value="">すべて</option><option value="changed">変更あり</option><option value="cost_increase">COST+ / 増額</option><option value="delayed">DELAYED / 延期</option><option value="progress_updated">PROGRESS UPDATED</option></select></label>
      <p id="count" class="result-count">${dataset.projects.length}件表示</p></aside><div class="map-column"><div id="map" class="main-map"></div><p class="map-note">点・破線ルートには概略位置を含みます。正確な施工区域・線形は各一次資料を確認してください。</p></div></section>
    <div id="changes-root">${recentChanges(dataset.projects)}</div>
    <section class="project-section"><div class="section-heading"><div><p class="eyebrow">PROJECT INVENTORY</p><h2>事業一覧</h2></div><p>Data Depthは収録できた一次情報の深さを示します。</p></div><div id="project-list" class="project-grid">${dataset.projects.map((project) => card(project, ids)).join('')}</div></section>
  </main><footer><p>非公式サイト。データ出典：愛媛県・国土交通省等の公表資料。</p><p>Map tiles © 国土地理院</p></footer>`;

  const map = mapBase('map', [33.55, 132.75], 8);
  let layer = addLayer(map, dataset.projects, geojson, ids);
  const q = document.querySelector<HTMLInputElement>('#q')!;
  const category = document.querySelector<HTMLSelectElement>('#category')!;
  const operator = document.querySelector<HTMLSelectElement>('#operator')!;
  const municipality = document.querySelector<HTMLSelectElement>('#municipality')!;
  const status = document.querySelector<HTMLSelectElement>('#status')!;
  const depth = document.querySelector<HTMLSelectElement>('#depth')!;
  const alert = document.querySelector<HTMLSelectElement>('#alert')!;
  const controls = [q, category, operator, municipality, status, depth, alert];
  const params = new URLSearchParams(location.search);
  const initialAlert = params.get('alert');
  const initialDepth = params.get('depth');
  if (initialAlert && [...alert.options].some((option) => option.value === initialAlert)) alert.value = initialAlert;
  if (initialDepth && [...depth.options].some((option) => option.value === initialDepth)) depth.value = initialDepth;

  const apply = () => {
    const filters: ProjectFilters = {
      query: q.value,
      category: category.value,
      operator: operator.value,
      municipality: municipality.value,
      status: status.value,
      depth: depth.value as ProjectFilters['depth'],
      alert: alert.value,
    };
    const filtered = filterProjects(dataset.projects, filters, ids);
    layer.remove();
    layer = addLayer(map, filtered, geojson, ids);
    document.querySelector<HTMLDivElement>('#project-list')!.innerHTML = filtered.map((project) => card(project, ids)).join('') || '<p class="empty-state">該当する事業はありません。</p>';
    document.querySelector<HTMLParagraphElement>('#count')!.textContent = `${filtered.length}件表示`;
    document.querySelector<HTMLDivElement>('#dashboard-root')!.innerHTML = dashboard(filtered, ids);
    document.querySelector<HTMLDivElement>('#changes-root')!.innerHTML = recentChanges(filtered);
    const url = new URL(location.href);
    if (alert.value) url.searchParams.set('alert', alert.value); else url.searchParams.delete('alert');
    if (depth.value) url.searchParams.set('depth', depth.value); else url.searchParams.delete('depth');
    history.replaceState(null, '', url);
  };
  controls.forEach((control) => control.addEventListener('input', apply));
  document.querySelector<HTMLButtonElement>('#reset')!.addEventListener('click', () => {
    controls.forEach((control) => { control.value = ''; });
    apply();
  });
  if (initialAlert || initialDepth) apply();
}

function row(label: string, value: string) {
  return `<div class="detail-row"><dt>${esc(label)}</dt><dd>${value}</dd></div>`;
}

function sourceFor(project: Project, sourceId: string): ProjectSource | undefined {
  return project.sources.find((source) => source.id === sourceId);
}

function sourceAnchor(project: Project, sourceId: string) {
  const source = sourceFor(project, sourceId);
  if (!source) return '<span class="history-source">出典未解決</span>';
  return `<a class="history-source" href="${esc(source.url)}" target="_blank" rel="noreferrer">原資料 ↗</a>`;
}

function costHistory(project: Project) {
  const items = project.costHistory ?? [];
  return `<ol class="history-list">${items.map((entry, index) => {
    const previous = items[index - 1];
    const delta = previous ? entry.valueMillionYen - previous.valueMillionYen : null;
    return `<li><div class="history-date">${esc(entry.asOf)}</div><div><strong>${formatMillionYen(entry.valueMillionYen)}</strong>${delta === null ? '' : `<span class="history-delta">${signed(delta / 100)}億円</span>`}<p>${entry.note ? esc(entry.note) : ''}</p>${sourceAnchor(project, entry.sourceId)}</div></li>`;
  }).join('')}</ol>`;
}

function scheduleHistory(project: Project) {
  const items = project.scheduleHistory ?? [];
  return `<ol class="history-list">${items.map((entry, index) => {
    const previous = items[index - 1];
    const delta = previous ? entry.plannedCompletionFiscalYear - previous.plannedCompletionFiscalYear : null;
    return `<li><div class="history-date">${esc(entry.asOf)}</div><div><strong>${formatFiscalYear(entry.plannedCompletionFiscalYear)}年度</strong>${delta === null || delta === 0 ? '' : `<span class="history-delta">${signed(delta, 0)}年度</span>`}<p>${entry.note ? esc(entry.note) : ''}</p>${sourceAnchor(project, entry.sourceId)}</div></li>`;
  }).join('')}</ol>`;
}

function progressHistory(project: Project) {
  const items = project.progressHistory ?? [];
  return `<ol class="history-list">${items.map((entry, index) => {
    const previous = items[index - 1];
    const delta = previous ? entry.progressPercent - previous.progressPercent : null;
    return `<li><div class="history-date">${esc(entry.asOf)}</div><div><strong>${entry.progressPercent}%</strong>${delta === null ? '' : `<span class="history-delta">${signed(delta)}pt</span>`}<p>${entry.note ? esc(entry.note) : ''}</p>${sourceAnchor(project, entry.sourceId)}</div></li>`;
  }).join('')}</ol>`;
}

function historySection(project: Project) {
  const hasCost = (project.costHistory?.length ?? 0) > 0;
  const hasSchedule = (project.scheduleHistory?.length ?? 0) > 0;
  const hasProgress = (project.progressHistory?.length ?? 0) > 0;
  if (!hasCost && !hasSchedule && !hasProgress) return '';
  return `<section class="detail-section detail-wide"><p class="eyebrow">HISTORY</p><h2>事業履歴</h2><div class="history-grid">${hasCost ? `<article class="history-panel"><h3>Cost History</h3>${costHistory(project)}</article>` : ''}${hasSchedule ? `<article class="history-panel"><h3>Schedule History</h3>${scheduleHistory(project)}</article>` : ''}${hasProgress ? `<article class="history-panel"><h3>Progress History</h3>${progressHistory(project)}</article>` : ''}</div></section>`;
}

function changeSummary(project: Project) {
  const events = getProjectChangeEvents(project);
  if (!events.length) return '';
  return `<section class="detail-section detail-wide"><p class="eyebrow">CHANGE SUMMARY</p><h2>確認できた変化</h2><p class="section-note">同一定義で比較可能な一次資料の履歴のみを差分計算しています。</p><div class="detail-change-grid">${events.map((event) => `<div class="detail-change-card"><div>${eventBadge(event)}<time>${esc(event.effectiveDate)}</time></div><strong>${esc(eventValue(event))}</strong>${event.note ? `<p>${esc(event.note)}</p>` : ''}${sourceAnchor(project, event.sourceId)}</div>`).join('')}</div></section>`;
}

function detail(project: Project, geojson: FeatureCollection<Geometry>, ids: ReadonlySet<string>) {
  const sources = project.sources.map((source) => `<li><a href="${esc(source.url)}" target="_blank" rel="noreferrer">${esc(source.title)}</a><span>${esc(source.publisher)} / 確認 ${esc(source.accessed)}</span>${source.note ? `<p>${esc(source.note)}</p>` : ''}</li>`).join('');
  const rows = [
    row('事業主体', esc(project.operator)),
    project.department ? row('所管', esc(project.department)) : '',
    row('対象市町', esc(project.municipalities.join('・'))),
    project.startFiscalYear !== null || project.plannedCompletionFiscalYear !== null
      ? row('事業期間', `${project.startFiscalYear === null ? '開始年度未確認' : `${formatFiscalYear(project.startFiscalYear)}年度`} ～ ${project.plannedCompletionFiscalYear === null ? '完成予定未確認' : `${formatFiscalYear(project.plannedCompletionFiscalYear)}年度（目標）`}`)
      : '',
    project.totalProjectCostMillionYen === null ? '' : row('全体事業費', formatMillionYen(project.totalProjectCostMillionYen)),
    project.progressPercent === null ? '' : row('進捗率', `${project.progressPercent}%${project.progressAsOf ? `（${esc(project.progressAsOf)}時点）` : ''}`),
    project.benefitCostRatio === null ? '' : row('B/C', String(project.benefitCostRatio)),
    row('Data Depth', depthBadge(project, ids)),
    row('最終確認日', esc(project.lastVerified)),
  ].filter(Boolean).join('');
  const inventoryNote = getMonitoringLevel(project, ids.has(project.id)) === 'inventory'
    ? '<p class="inventory-detail-note">この案件はInventory層です。存在・位置・概要を一次資料で確認していますが、総事業費・完成年度・進捗率は確認できた資料がないため推測していません。</p>'
    : '';
  const detailEvents = getProjectChangeEvents(project);
  const latestCostChange = [...detailEvents].reverse().find((event) => event.type === 'cost_increase' || event.type === 'cost_decrease');
  const latestScheduleChange = [...detailEvents].reverse().find((event) => event.type === 'delayed' || event.type === 'accelerated');
  const costKpi = project.totalProjectCostMillionYen === null ? '—' : formatMillionYen(project.totalProjectCostMillionYen);
  const periodKpi = project.plannedCompletionFiscalYear === null ? '—' : `${formatFiscalYear(project.plannedCompletionFiscalYear)}年度`;
  const progressKpi = project.progressPercent === null ? '—' : `${project.progressPercent}%`;
  const detailKpis = `<section class="dashboard detail-kpis"><div class="metric"><strong>${costKpi}</strong><span>COST<br>${latestCostChange ? esc(eventValue(latestCostChange)) : 'CURRENT SNAPSHOT'}</span></div><div class="metric"><strong>${periodKpi}</strong><span>COMPLETION<br>${latestScheduleChange ? esc(eventValue(latestScheduleChange)) : 'CURRENT TARGET'}</span></div><div class="metric"><strong>${progressKpi}</strong><span>PROGRESS<br>${project.progressAsOf ? esc(project.progressAsOf) : 'PUBLIC VALUE'}</span></div></section>`;
  app.innerHTML = `${header('PROJECT DETAIL')}<main class="detail-main"><nav class="breadcrumb"><a href="${base}">← 地図へ戻る</a></nav><section class="detail-hero"><p class="eyebrow">${esc(project.categoryLabel)} · ${esc(project.statusLabel)}</p><div class="detail-depth">${depthBadge(project, ids)}</div>${projectBadges(project)}<h1>${esc(project.name)}</h1><p class="lead">${esc(project.municipalities.join('・'))} · ${esc(project.operator)} · VERIFIED ${esc(project.lastVerified)}</p><p class="lead">${esc(project.summary)}</p>${inventoryNote}</section>${detailKpis}<section class="detail-layout"><div class="detail-map-panel"><div id="detail-map" class="detail-map"></div><p class="map-note">位置精度：${esc(project.locationAccuracy)}。${esc(project.locationNote ?? '')}</p></div><dl class="detail-table">${rows}</dl></section>${changeSummary(project)}${historySection(project)}<section class="detail-section"><p class="eyebrow">SCOPE</p><h2>事業概要</h2><p>${esc(project.scope)}</p></section><section class="detail-section sources"><p class="eyebrow">PRIMARY SOURCES</p><h2>情報源</h2><ol>${sources}</ol><p class="source-note">掲載値は各機関の公表資料を整理したものです。最新情報・正確な施工区域は必ず原資料を確認してください。</p></section></main><footer><p>Ehime Civil Works Monitor / unofficial</p></footer>`;
  const map = mapBase('detail-map', [33.55, 132.75], 9);
  const feature = geojson.features.find((item) => item.properties?.projectId === project.id);
  if (feature) {
    const layer = addLayer(map, [project], { type: 'FeatureCollection', features: [feature] }, ids);
    const bounds = layer.getBounds();
    if (bounds.isValid()) map.fitBounds(bounds.pad(.8), { maxZoom: 14 });
  }
}

async function main() {
  try {
    const { dataset, geojson, enrichment } = await loadData();
    const ids = enrichedIds(enrichment);
    const projectId = getProjectIdFromPath(location.pathname);
    if (projectId) {
      const project = dataset.projects.find((item) => item.id === projectId);
      if (!project) throw new Error('指定された事業が見つかりません。');
      document.title = `${project.name} | Ehime Civil Works Monitor`;
      detail(project, geojson, ids);
    } else {
      home(dataset, geojson, enrichment);
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : '不明なエラー';
    app.innerHTML = `${header('ERROR')}<main class="error-panel"><h1>表示できませんでした</h1><p>${esc(message)}</p><a href="${base}">トップへ戻る</a></main>`;
  }
}

void main();
