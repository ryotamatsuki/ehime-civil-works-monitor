import 'leaflet/dist/leaflet.css';
import './styles.css';
import L from 'leaflet';
import type { FeatureCollection, Geometry } from 'geojson';
import type { ChangeEvent, Project, ProjectCollection, ProjectSource } from './types';
import {
  aggregateProjects,
  filterProjects,
  formatFiscalYear,
  formatMillionYen,
  getAllChangeEvents,
  getProjectChangeEvents,
  getProjectIdFromPath,
  type ProjectFilters,
} from './domain';

const base = import.meta.env.BASE_URL;
const app = document.querySelector<HTMLDivElement>('#app');
if (!app) throw new Error('App root not found');

const esc = (s: string) => s.replace(/[&<>'"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#039;', '"': '&quot;' }[c] ?? c));

async function loadData() {
  const [a, b] = await Promise.all([fetch(`${base}data/projects.json`), fetch(`${base}data/projects.geojson`)]);
  if (!a.ok || !b.ok) throw new Error('データを読み込めませんでした。');
  return { dataset: await a.json() as ProjectCollection, geojson: await b.json() as FeatureCollection<Geometry> };
}

function header(subtitle: string) {
  return `<header class="site-header"><a class="brand" href="${base}">EHIME CIVIL WORKS MONITOR</a><p>${esc(subtitle)}</p></header>`;
}

function projectUrl(p: Project) { return `${base}projects/${encodeURIComponent(p.id)}/`; }

function popup(p: Project) {
  return `<article class="map-popup"><p class="eyebrow">${esc(p.categoryLabel)} · ${esc(p.statusLabel)}</p><h3>${esc(p.name)}</h3><dl><dt>事業主体</dt><dd>${esc(p.operator)}</dd><dt>市町</dt><dd>${esc(p.municipalities.join('・'))}</dd><dt>全体事業費</dt><dd>${formatMillionYen(p.totalProjectCostMillionYen)}</dd><dt>進捗率</dt><dd>${p.progressPercent === null ? '公表値未確認' : `${p.progressPercent}%`}</dd></dl><a href="${projectUrl(p)}">詳細・履歴・一次情報 →</a></article>`;
}

function mapBase(id: string, center: L.LatLngExpression, zoom: number) {
  const map = L.map(id).setView(center, zoom);
  L.tileLayer('https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png', {
    attribution: '<a href="https://maps.gsi.go.jp/development/ichiran.html" target="_blank" rel="noreferrer">国土地理院</a>',
    maxZoom: 18,
  }).addTo(map);
  return map;
}

function addLayer(map: L.Map, projects: Project[], geojson: FeatureCollection<Geometry>) {
  const ids = new Set(projects.map(p => p.id));
  const byId = new Map(projects.map(p => [p.id, p]));
  const fc: FeatureCollection<Geometry> = { type: 'FeatureCollection', features: geojson.features.filter(f => ids.has(String(f.properties?.projectId ?? ''))) };
  const layer = L.geoJSON(fc, {
    pointToLayer: (feature, latlng) => {
      const p = byId.get(String(feature.properties?.projectId ?? ''));
      const icon = L.divIcon({ className: 'marker-wrap', html: `<span class="marker category-${p?.category ?? 'river'}"></span>`, iconSize: [18, 18], iconAnchor: [9, 9] });
      return L.marker(latlng, { icon });
    },
    style: feature => {
      const p = byId.get(String(feature?.properties?.projectId ?? ''));
      return { weight: 4, opacity: .85, fillOpacity: .16, dashArray: p?.locationAccuracy === 'approximate' ? '7 6' : undefined };
    },
    onEachFeature: (feature, l) => {
      const p = byId.get(String(feature.properties?.projectId ?? ''));
      if (p) l.bindPopup(popup(p), { maxWidth: 340 });
    },
  }).addTo(map);
  return layer;
}

function dashboard(projects: Project[]) {
  const s = aggregateProjects(projects);
  return `<section class="dashboard"><div class="metric"><strong>${s.projectCount}</strong><span>PROJECTS<br>登録事業</span></div><div class="metric"><strong>${(s.totalKnownCostMillionYen / 100).toLocaleString('ja-JP', { maximumFractionDigits: 1 })}億円</strong><span>TOTAL COST<br>確認済み ${s.knownCostCount}件</span></div><div class="metric"><strong>${s.costIncreaseProjectCount}</strong><span>COST+<br>増額履歴あり</span></div><div class="metric"><strong>${s.delayedProjectCount}</strong><span>DELAYED<br>完成予定後ろ倒し</span></div><div class="metric"><strong>${s.updatedLast365Days}</strong><span>UPDATED / 365D<br>直近365日の変更</span></div></section>`;
}

function options(values: string[]) { return [...new Set(values)].sort((a, b) => a.localeCompare(b, 'ja')).map(v => `<option value="${esc(v)}">${esc(v)}</option>`).join(''); }

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
    const pct = event.percentChange === undefined ? '' : ` / ${signed(event.percentChange)}%`;
    return `${formatMillionYen(event.previousValue)} → ${formatMillionYen(event.currentValue)} · ${signed(event.absoluteChange / 100)}億円${pct}`;
  }
  if (event.type === 'delayed' || event.type === 'accelerated') {
    return `${formatFiscalYear(event.previousValue)} → ${formatFiscalYear(event.currentValue)} · ${signed(event.absoluteChange, 0)}年度`;
  }
  return `${event.previousValue}% → ${event.currentValue}% · ${signed(event.absoluteChange)}pt`;
}

function eventBadge(event: ChangeEvent) {
  return `<span class="change-badge change-${event.type} severity-${event.severity}">${eventLabels[event.type]}</span>`;
}

function projectBadges(p: Project) {
  const types = new Set<ChangeEvent['type']>();
  const badges = getProjectChangeEvents(p).filter(event => {
    if (types.has(event.type)) return false;
    types.add(event.type);
    return true;
  });
  return badges.length ? `<div class="change-badges">${badges.map(eventBadge).join('')}</div>` : '';
}

function card(p: Project) {
  return `<article class="project-card"><div class="project-card-top"><span class="tag">${esc(p.categoryLabel)}</span><span class="status">${esc(p.statusLabel)}</span></div>${projectBadges(p)}<h3><a href="${projectUrl(p)}">${esc(p.name)}</a></h3><p>${esc(p.municipalities.join('・'))} / ${esc(p.operator)}</p><div class="project-numbers"><span><small>全体事業費</small>${formatMillionYen(p.totalProjectCostMillionYen)}</span><span><small>進捗率</small>${p.progressPercent === null ? '未確認' : `${p.progressPercent}%`}</span></div></article>`;
}

function recentChanges(projects: Project[]) {
  const byId = new Map(projects.map(p => [p.id, p]));
  const events = getAllChangeEvents(projects).slice(0, 8);
  const body = events.length ? events.map(event => {
    const p = byId.get(event.projectId);
    if (!p) return '';
    return `<a class="change-card" href="${projectUrl(p)}"><div class="change-card-head">${eventBadge(event)}<time>${esc(event.effectiveDate)}</time></div><strong>${esc(p.name)}</strong><p>${esc(eventValue(event))}</p></a>`;
  }).join('') : '<p class="empty-change">比較可能な複数時点の履歴はまだありません。</p>';
  return `<section class="changes-section"><div class="section-heading"><div><p class="eyebrow">CHANGE DETECTION</p><h2>Recent Changes</h2></div><p>一次資料の比較可能な履歴から機械的に導出。評価・推測ではありません。</p></div><div class="change-grid">${body}</div></section>`;
}

function home(dataset: ProjectCollection, geojson: FeatureCollection<Geometry>) {
  const cat = new Map(dataset.projects.map(p => [p.categoryLabel, p.category]));
  const sts = new Map(dataset.projects.map(p => [p.statusLabel, p.status]));
  app.innerHTML = `${header('愛媛県内の主要公共土木事業を、一次情報と履歴まで辿れる形で可視化します。')}<main><section class="hero"><div><p class="eyebrow">PUBLIC INFRASTRUCTURE · OPEN SOURCES</p><h1>愛媛の公共事業を<br>変化から追う。</h1><p class="lead">公表資料に記載された事業費・進捗・完成目標を時系列で整理し、増額や完成予定の変更を履歴から検出する非公式モニターです。</p></div><aside class="notice"><strong>PHASE 2 / 2026-08-30</strong><p>変更は比較可能な一次資料の値だけから導出します。概略位置は施工範囲そのものを示しません。最新情報は必ず原資料で確認してください。</p></aside></section><div id="dashboard-root">${dashboard(dataset.projects)}</div><div id="changes-root">${recentChanges(dataset.projects)}</div><section class="workspace"><aside class="filters"><div class="filter-heading"><h2>Filter</h2><button id="reset" type="button">リセット</button></div><label>検索<input id="q" type="search" placeholder="事業名・市町名"></label><label>カテゴリー<select id="category"><option value="">すべて</option>${[...cat].sort().map(([l, v]) => `<option value="${v}">${esc(l)}</option>`).join('')}</select></label><label>事業主体<select id="operator"><option value="">すべて</option>${options(dataset.projects.map(p => p.operator))}</select></label><label>市町<select id="municipality"><option value="">すべて</option>${options(dataset.projects.flatMap(p => p.municipalities))}</select></label><label>ステータス<select id="status"><option value="">すべて</option>${[...sts].sort().map(([l, v]) => `<option value="${v}">${esc(l)}</option>`).join('')}</select></label><label>変更<select id="alert"><option value="">すべて</option><option value="changed">変更あり</option><option value="cost_increase">COST+ / 増額</option><option value="delayed">DELAYED / 延期</option><option value="progress_updated">PROGRESS UPDATED</option></select></label><p id="count" class="result-count">${dataset.projects.length}件表示</p></aside><div class="map-column"><div id="map" class="main-map"></div><p class="map-note">概略位置を含みます。正確な施工区域は各一次資料を確認してください。</p></div></section><section class="project-section"><div class="section-heading"><div><p class="eyebrow">PROJECT INDEX</p><h2>事業一覧</h2></div><p>金額は全体事業費。進捗率は原資料記載時点です。</p></div><div id="project-list" class="project-grid">${dataset.projects.map(card).join('')}</div></section></main><footer><p>非公式サイト。データ出典：愛媛県等の公表資料。</p><p>Map tiles © 国土地理院</p></footer>`;

  const map = mapBase('map', [33.55, 132.75], 8);
  let layer = addLayer(map, dataset.projects, geojson);
  const q = document.querySelector<HTMLInputElement>('#q')!;
  const category = document.querySelector<HTMLSelectElement>('#category')!;
  const operator = document.querySelector<HTMLSelectElement>('#operator')!;
  const municipality = document.querySelector<HTMLSelectElement>('#municipality')!;
  const status = document.querySelector<HTMLSelectElement>('#status')!;
  const alert = document.querySelector<HTMLSelectElement>('#alert')!;
  const controls = [q, category, operator, municipality, status, alert];
  const initialAlert = new URLSearchParams(location.search).get('alert');
  if (initialAlert && [...alert.options].some(option => option.value === initialAlert)) alert.value = initialAlert;
  const apply = () => {
    const filters: ProjectFilters = { query: q.value, category: category.value, operator: operator.value, municipality: municipality.value, status: status.value, alert: alert.value };
    const filtered = filterProjects(dataset.projects, filters);
    layer.remove();
    layer = addLayer(map, filtered, geojson);
    document.querySelector<HTMLDivElement>('#project-list')!.innerHTML = filtered.map(card).join('') || '<p class="empty-state">該当する事業はありません。</p>';
    document.querySelector<HTMLParagraphElement>('#count')!.textContent = `${filtered.length}件表示`;
    document.querySelector<HTMLDivElement>('#dashboard-root')!.innerHTML = dashboard(filtered);
    document.querySelector<HTMLDivElement>('#changes-root')!.innerHTML = recentChanges(filtered);
    const url = new URL(location.href);
    if (alert.value) url.searchParams.set('alert', alert.value); else url.searchParams.delete('alert');
    history.replaceState(null, '', url);
  };
  controls.forEach(c => c.addEventListener('input', apply));
  document.querySelector<HTMLButtonElement>('#reset')!.addEventListener('click', () => { controls.forEach(c => { c.value = ''; }); apply(); });
  if (initialAlert) apply();
}

function row(label: string, value: string) { return `<div class="detail-row"><dt>${esc(label)}</dt><dd>${value}</dd></div>`; }

function sourceFor(p: Project, sourceId: string): ProjectSource | undefined {
  return p.sources.find(source => source.id === sourceId);
}

function sourceAnchor(p: Project, sourceId: string) {
  const source = sourceFor(p, sourceId);
  if (!source) return '<span class="history-source">出典未解決</span>';
  return `<a class="history-source" href="${esc(source.url)}" target="_blank" rel="noreferrer">原資料 ↗</a>`;
}

function costHistory(p: Project) {
  const items = p.costHistory ?? [];
  if (!items.length) return '<p class="history-empty">履歴未確認</p>';
  return `<ol class="history-list">${items.map((entry, index) => {
    const previous = items[index - 1];
    const delta = previous ? entry.valueMillionYen - previous.valueMillionYen : null;
    return `<li><div class="history-date">${esc(entry.asOf)}</div><div><strong>${formatMillionYen(entry.valueMillionYen)}</strong>${delta === null ? '' : `<span class="history-delta">${signed(delta / 100)}億円</span>`}<p>${entry.note ? esc(entry.note) : ''}</p>${sourceAnchor(p, entry.sourceId)}</div></li>`;
  }).join('')}</ol>`;
}

function scheduleHistory(p: Project) {
  const items = p.scheduleHistory ?? [];
  if (!items.length) return '<p class="history-empty">履歴未確認</p>';
  return `<ol class="history-list">${items.map((entry, index) => {
    const previous = items[index - 1];
    const delta = previous ? entry.plannedCompletionFiscalYear - previous.plannedCompletionFiscalYear : null;
    return `<li><div class="history-date">${esc(entry.asOf)}</div><div><strong>${formatFiscalYear(entry.plannedCompletionFiscalYear)}年度</strong>${delta === null || delta === 0 ? '' : `<span class="history-delta">${signed(delta, 0)}年度</span>`}<p>${entry.note ? esc(entry.note) : ''}</p>${sourceAnchor(p, entry.sourceId)}</div></li>`;
  }).join('')}</ol>`;
}

function progressHistory(p: Project) {
  const items = p.progressHistory ?? [];
  if (!items.length) return '<p class="history-empty">履歴未確認</p>';
  return `<ol class="history-list">${items.map((entry, index) => {
    const previous = items[index - 1];
    const delta = previous ? entry.progressPercent - previous.progressPercent : null;
    return `<li><div class="history-date">${esc(entry.asOf)}</div><div><strong>${entry.progressPercent}%</strong>${delta === null ? '' : `<span class="history-delta">${signed(delta)}pt</span>`}<p>${entry.note ? esc(entry.note) : ''}</p>${sourceAnchor(p, entry.sourceId)}</div></li>`;
  }).join('')}</ol>`;
}

function changeSummary(p: Project) {
  const events = getProjectChangeEvents(p);
  if (!events.length) return '<p class="history-empty">比較可能な複数時点の履歴から検出された変更はありません。</p>';
  return `<div class="detail-change-grid">${events.map(event => `<div class="detail-change-card"><div>${eventBadge(event)}<time>${esc(event.effectiveDate)}</time></div><strong>${esc(eventValue(event))}</strong>${event.note ? `<p>${esc(event.note)}</p>` : ''}${sourceAnchor(p, event.sourceId)}</div>`).join('')}</div>`;
}

function detail(p: Project, geojson: FeatureCollection<Geometry>) {
  const sources = p.sources.map(s => `<li><a href="${esc(s.url)}" target="_blank" rel="noreferrer">${esc(s.title)}</a><span>${esc(s.publisher)} / 確認 ${esc(s.accessed)}</span>${s.note ? `<p>${esc(s.note)}</p>` : ''}</li>`).join('');
  app.innerHTML = `${header('PROJECT DETAIL')}<main class="detail-main"><nav class="breadcrumb"><a href="${base}">← 地図へ戻る</a></nav><section class="detail-hero"><p class="eyebrow">${esc(p.categoryLabel)} · ${esc(p.statusLabel)}</p>${projectBadges(p)}<h1>${esc(p.name)}</h1><p class="lead">${esc(p.summary)}</p></section><section class="detail-layout"><div class="detail-map-panel"><div id="detail-map" class="detail-map"></div><p class="map-note">位置精度：${esc(p.locationAccuracy)}。${esc(p.locationNote ?? '')}</p></div><dl class="detail-table">${row('事業主体', esc(p.operator))}${row('所管', esc(p.department))}${row('対象市町', esc(p.municipalities.join('・')))}${row('事業期間', `${p.startFiscalYear ?? '不明'}年度 ～ ${p.plannedCompletionFiscalYear ?? '不明'}年度（目標）`)}${row('全体事業費', formatMillionYen(p.totalProjectCostMillionYen))}${row('進捗率', p.progressPercent === null ? '公表値未確認' : `${p.progressPercent}%${p.progressAsOf ? `（${esc(p.progressAsOf)}時点）` : ''}`)}${row('B/C', p.benefitCostRatio === null ? '公表値未確認' : String(p.benefitCostRatio))}${row('最終確認日', esc(p.lastVerified))}</dl></section><section class="detail-section detail-wide"><p class="eyebrow">CHANGE SUMMARY</p><h2>確認できた変化</h2><p class="section-note">同一定義で比較可能な一次資料の履歴のみを差分計算しています。</p>${changeSummary(p)}</section><section class="detail-section detail-wide"><p class="eyebrow">HISTORY</p><h2>事業履歴</h2><div class="history-grid"><article class="history-panel"><h3>Cost History</h3>${costHistory(p)}</article><article class="history-panel"><h3>Schedule History</h3>${scheduleHistory(p)}</article><article class="history-panel"><h3>Progress History</h3>${progressHistory(p)}</article></div></section><section class="detail-section"><p class="eyebrow">SCOPE</p><h2>事業概要</h2><p>${esc(p.scope)}</p></section><section class="detail-section sources"><p class="eyebrow">PRIMARY SOURCES</p><h2>情報源</h2><ol>${sources}</ol><p class="source-note">掲載値は各機関の公表資料を整理したものです。最新情報・正確な施工区域は必ず原資料を確認してください。</p></section></main><footer><p>Ehime Civil Works Monitor / unofficial</p></footer>`;
  const map = mapBase('detail-map', [33.55, 132.75], 9);
  const f = geojson.features.find(x => x.properties?.projectId === p.id);
  if (f) {
    const l = addLayer(map, [p], { type: 'FeatureCollection', features: [f] });
    const b = l.getBounds();
    if (b.isValid()) map.fitBounds(b.pad(.8), { maxZoom: 14 });
  }
}

async function main() {
  try {
    const { dataset, geojson } = await loadData();
    const id = getProjectIdFromPath(location.pathname);
    if (id) {
      const p = dataset.projects.find(x => x.id === id);
      if (!p) throw new Error('指定された事業が見つかりません。');
      document.title = `${p.name} | Ehime Civil Works Monitor`;
      detail(p, geojson);
    } else {
      home(dataset, geojson);
    }
  } catch (e) {
    const m = e instanceof Error ? e.message : '不明なエラー';
    app.innerHTML = `${header('ERROR')}<main class="error-panel"><h1>表示できませんでした</h1><p>${esc(m)}</p><a href="${base}">トップへ戻る</a></main>`;
  }
}

void main();
