import './enrichment.css';
import type {
  AnnualBudgetEntry,
  BenefitCostHistoryEntry,
  DocumentedReason,
  EnrichmentCollection,
  ProjectEnrichmentRecord,
} from './enrichment-types';
import { aggregateEnrichment, getEnrichmentRecord, hasEnrichmentData } from './enrichment';
import { formatFiscalYear, formatMillionYen, getProjectIdFromPath } from './domain';

const base = import.meta.env.BASE_URL;

const esc = (value: string) => value.replace(/[&<>'"]/g, (char) => ({
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  "'": '&#039;',
  '"': '&quot;',
}[char] ?? char));

function sourceAnchor(record: ProjectEnrichmentRecord, sourceId: string) {
  const source = record.sources.find((item) => item.id === sourceId);
  if (!source) return '<span class="enrichment-source">出典未解決</span>';
  return `<a class="enrichment-source" href="${esc(source.url)}" target="_blank" rel="noreferrer">原資料 ↗</a>`;
}

function budgetBasisLabel(entry: AnnualBudgetEntry) {
  const labels: Record<AnnualBudgetEntry['basis'], string> = {
    project_allocation: '事業配分額',
    national_subsidy: '国費・補助額',
    prefectural_budget: '県予算額',
  };
  return labels[entry.basis];
}

function annualBudget(record: ProjectEnrichmentRecord) {
  if (!record.annualBudgetHistory.length) return '<p class="enrichment-empty">この従来Enrichment層には追加の年度予算記録はありません。R5～R8の体系的な年度比較はPhase 2.5の「年度別予算・配分」を参照してください。</p>';
  return `<ol class="enrichment-list">${record.annualBudgetHistory.map((entry) => `
    <li class="enrichment-row">
      <div class="enrichment-row-head"><strong>${formatFiscalYear(entry.fiscalYear)}年度 · ${formatMillionYen(entry.amountMillionYen)}</strong><time>${esc(entry.asOf)}</time></div>
      <span class="enrichment-scope">${esc(budgetBasisLabel(entry))}</span>
      ${entry.note ? `<p class="enrichment-note">${esc(entry.note)}</p>` : ''}
      ${sourceAnchor(record, entry.sourceId)}
    </li>`).join('')}</ol>`;
}

function cumulativeInvestment(record: ProjectEnrichmentRecord) {
  if (!record.cumulativeInvestmentHistory.length) return '<p class="enrichment-empty">累計投資事業費は未確認です。</p>';
  return `<ol class="enrichment-list">${record.cumulativeInvestmentHistory.map((entry) => `
    <li class="enrichment-row">
      <div class="enrichment-row-head"><strong>${formatFiscalYear(entry.fiscalYear)}年度 · ${formatMillionYen(entry.amountMillionYen)}</strong><time>${esc(entry.asOf)}</time></div>
      <span class="enrichment-status enrichment-status-${entry.status}">${entry.status === 'actual' ? '実績' : '年度末見込'}</span>
      ${entry.note ? `<p class="enrichment-note">${esc(entry.note)}</p>` : ''}
      ${sourceAnchor(record, entry.sourceId)}
    </li>`).join('')}</ol>`;
}

function bcLabels(entry: BenefitCostHistoryEntry) {
  const scope = entry.scope === 'project' ? '当該事業' : 'ネットワーク全体';
  const perspective = entry.perspective === 'whole' ? '事業全体' : '残事業';
  return `${scope} / ${perspective}`;
}

function benefitCost(record: ProjectEnrichmentRecord) {
  if (!record.benefitCostHistory.length) return '<p class="enrichment-empty">B/C履歴は未確認です。</p>';
  const entries = [...record.benefitCostHistory].sort((a, b) => a.asOf.localeCompare(b.asOf) || a.scope.localeCompare(b.scope) || a.perspective.localeCompare(b.perspective));
  return `<ol class="enrichment-list">${entries.map((entry) => `
    <li class="enrichment-row">
      <div class="enrichment-row-head"><strong>B/C ${entry.value.toLocaleString('ja-JP')}</strong><time>${esc(entry.asOf)}</time></div>
      <span class="enrichment-scope">${esc(bcLabels(entry))}</span>
      ${entry.fiscalYear === null ? '' : `<span class="enrichment-scope">${formatFiscalYear(entry.fiscalYear)}年度評価</span>`}
      ${entry.note ? `<p class="enrichment-note">${esc(entry.note)}</p>` : ''}
      ${sourceAnchor(record, entry.sourceId)}
    </li>`).join('')}</ol>`;
}

function reasonLabel(reason: DocumentedReason) {
  const labels: Record<DocumentedReason['type'], string> = {
    cost_change: '事業費変更',
    schedule_change: '完成予定変更',
    delay_context: '遅延事情',
  };
  return labels[reason.type];
}

function documentedReasons(record: ProjectEnrichmentRecord) {
  if (!record.documentedReasons.length) return '<p class="enrichment-empty">一次資料で明記された増額・延期理由は未確認です。</p>';
  return `<ol class="enrichment-list">${record.documentedReasons.map((reason) => `
    <li class="enrichment-row enrichment-reason">
      <div class="enrichment-row-head"><strong>${esc(reason.summary)}</strong><time>${esc(reason.effectiveDate)}</time></div>
      <span class="enrichment-scope">${esc(reasonLabel(reason))}</span>
      ${reason.note ? `<p class="enrichment-note">${esc(reason.note)}</p>` : ''}
      ${sourceAnchor(record, reason.sourceId)}
    </li>`).join('')}</ol>`;
}

function renderHome(enrichment: EnrichmentCollection) {
  const changesRoot = document.querySelector<HTMLElement>('#changes-root');
  if (!changesRoot || document.querySelector('.enrichment-summary')) return;
  const stats = aggregateEnrichment(enrichment);
  const section = document.createElement('section');
  section.className = 'enrichment-summary';
  section.innerHTML = `
    <div class="enrichment-summary-head">
      <div><p class="eyebrow">PHASE 2.1 · DATA ENRICHMENT</p><h2>一次資料を、もう一段深く。</h2></div>
      <p>累計投資・B/C・文書化された増額／延期事情に加え、従来から確認済みの年度予算値を元資料へ戻れる形で保持しています。R5～R8の体系的な年度比較はPhase 2.5で扱います。</p>
    </div>
    <div class="enrichment-metrics">
      <div class="enrichment-metric"><strong>${stats.enrichedProjectCount}</strong><span>ENRICHED<br>深掘り済み案件</span></div>
      <div class="enrichment-metric"><strong>${stats.annualBudgetProjectCount}</strong><span>LEGACY BUDGET<br>従来確認済み値</span></div>
      <div class="enrichment-metric"><strong>${stats.cumulativeInvestmentProjectCount}</strong><span>INVESTMENT<br>累計投資確認</span></div>
      <div class="enrichment-metric"><strong>${stats.multiPeriodBenefitCostProjectCount}</strong><span>B/C HISTORY<br>複数時点比較</span></div>
      <div class="enrichment-metric"><strong>${stats.documentedReasonProjectCount}</strong><span>REASONS<br>理由・事情確認</span></div>
    </div>`;
  changesRoot.insertAdjacentElement('afterend', section);
}

function renderDetail(record: ProjectEnrichmentRecord) {
  if (document.querySelector('.enrichment-detail')) return;
  const wideSections = document.querySelectorAll<HTMLElement>('.detail-section.detail-wide');
  const anchor = wideSections.item(wideSections.length - 1);
  if (!anchor) return;
  const section = document.createElement('section');
  section.className = 'detail-section detail-wide enrichment-detail';
  section.innerHTML = `
    <p class="eyebrow">PHASE 2.1 · DATA ENRICHMENT</p>
    <h2>投資・評価の深掘り</h2>
    <p class="enrichment-intro">全体事業費とは別に、従来から確認済みの年度予算値、累計投資事業費、B/Cの評価条件、一次資料に明記された増額・延期事情を整理しています。R5～R8の体系的な年度予算比較はPhase 2.5に分離しています。</p>
    <div class="enrichment-grid">
      <article class="enrichment-panel"><div class="enrichment-panel-head"><h3>Legacy Budget</h3><span class="enrichment-kicker">従来確認済み値</span></div>${annualBudget(record)}</article>
      <article class="enrichment-panel"><div class="enrichment-panel-head"><h3>Cumulative Investment</h3><span class="enrichment-kicker">累計投資事業費</span></div>${cumulativeInvestment(record)}</article>
      <article class="enrichment-panel"><div class="enrichment-panel-head"><h3>B/C History</h3><span class="enrichment-kicker">対象範囲を分離</span></div>${benefitCost(record)}</article>
      <article class="enrichment-panel"><div class="enrichment-panel-head"><h3>Documented Reasons</h3><span class="enrichment-kicker">一次資料に明記された内容のみ</span></div>${documentedReasons(record)}</article>
    </div>
    <div class="enrichment-legend">B/Cは「当該事業／ネットワーク全体」と「事業全体／残事業」を混同しません。累計投資の「年度末見込」は、評価委員会開催時点で将来の年度末値として示されたものです。理由が一次資料に明記されない場合は推測して補いません。</div>`;
  anchor.insertAdjacentElement('afterend', section);
}

async function waitForMainView() {
  for (let frame = 0; frame < 180; frame += 1) {
    if (document.querySelector('.detail-main, .project-section, .error-panel')) return;
    await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
  }
}

async function phase21() {
  try {
    const response = await fetch(`${base}data/enrichment.json`);
    if (!response.ok) return;
    const enrichment = await response.json() as EnrichmentCollection;
    await waitForMainView();
    const projectId = getProjectIdFromPath(location.pathname);
    if (projectId) {
      const record = getEnrichmentRecord(enrichment, projectId);
      if (record && hasEnrichmentData(record)) renderDetail(record);
    } else {
      renderHome(enrichment);
    }
  } catch {
    // Phase 1/2 rendering remains usable even if optional enrichment cannot load.
  }
}

void phase21();
