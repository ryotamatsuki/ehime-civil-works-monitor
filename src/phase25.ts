import './annual-budget.css';
import type {
  AnnualBudgetCollection,
  AnnualBudgetObservation,
  BudgetAuditStatus,
  BudgetStage,
} from './annual-budget-types';
import {
  aggregateAnnualBudget,
  getAnnualBudgetAuditNote,
  getAnnualBudgetAuditStatus,
  getAnnualBudgetObservations,
  getAnnualBudgetSource,
  getComparableBudgetSeries,
} from './annual-budget';
import { formatFiscalYear, formatMillionYen, getProjectIdFromPath } from './domain';

const base = import.meta.env.BASE_URL;

const esc = (value: string) => value.replace(/[&<>'"]/g, (char) => ({
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  "'": '&#039;',
  '"': '&quot;',
}[char] ?? char));

const stageLabels: Record<BudgetStage, string> = {
  initial: '当初',
  supplementary: '補正',
  final: '最終',
  allocation: '配分',
  unknown: '区分未確定',
};

const basisLabels: Record<AnnualBudgetObservation['basis'], string> = {
  project_allocation: '事業配分額',
  national_subsidy: '国費・補助額',
  prefectural_budget: '県予算額',
};

const auditLabels: Record<BudgetAuditStatus, string> = {
  CONFIRMED_PROJECT_BUDGET: '案件金額確認済み',
  PROJECT_LISTED_NO_AMOUNT: '案件名のみ確認',
  BROADER_PROGRAM_ONLY: '上位事業の総額のみ',
  SCOPE_MISMATCH: '対象範囲が不一致',
  SOURCE_NOT_FOUND: '案件金額未確認',
  NOT_APPLICABLE: '対象外',
};

function sourceAnchor(collection: AnnualBudgetCollection, sourceId: string) {
  const source = getAnnualBudgetSource(collection, sourceId);
  if (!source) return '<span class="budget-source">出典未解決</span>';
  const locator = source.locator ? ` · ${source.locator}` : '';
  return `<a class="budget-source" href="${esc(source.url)}" target="_blank" rel="noreferrer" title="${esc(source.title + locator)}">原資料 ↗</a>`;
}

function observationCard(collection: AnnualBudgetCollection, entry: AnnualBudgetObservation) {
  return `<div class="budget-observation">
    <strong>${formatMillionYen(entry.amountMillionYen)}</strong>
    <div class="budget-tags"><span>${esc(stageLabels[entry.budgetStage])}</span><span>${esc(basisLabels[entry.basis])}</span></div>
    ${entry.note ? `<p>${esc(entry.note)}</p>` : ''}
    ${sourceAnchor(collection, entry.sourceId)}
  </div>`;
}

function fiscalYearColumn(
  collection: AnnualBudgetCollection,
  fiscalYear: number,
  observations: AnnualBudgetObservation[],
) {
  const entries = observations.filter((entry) => entry.fiscalYear === fiscalYear);
  return `<article class="budget-year-card">
    <div class="budget-year-head"><span>FY${fiscalYear}</span><strong>${formatFiscalYear(fiscalYear)}年度</strong></div>
    ${entries.length
      ? entries.map((entry) => observationCard(collection, entry)).join('')
      : '<div class="budget-missing">—<span>案件単位金額は未確認</span></div>'}
  </article>`;
}

function comparableNote(observations: AnnualBudgetObservation[]) {
  const series = getComparableBudgetSeries(observations)
    .map((item) => ({ ...item, years: new Set(item.observations.map((entry) => entry.fiscalYear)).size }))
    .filter((item) => item.years >= 2)
    .sort((a, b) => b.years - a.years);
  if (!series.length) return '<p class="budget-comparable-note">同一定義で2年度以上比較できる系列はまだありません。</p>';
  return `<div class="budget-series-list">${series.map((item) => `<span><strong>${item.years}年度比較</strong> ${esc(basisLabels[item.basis])} / ${esc(stageLabels[item.budgetStage])}</span>`).join('')}</div>`;
}

function renderHome(collection: AnnualBudgetCollection) {
  if (document.querySelector('.annual-budget-summary')) return;
  const stats = aggregateAnnualBudget(collection);
  const section = document.createElement('section');
  section.className = 'annual-budget-summary';
  section.innerHTML = `
    <div class="annual-budget-summary-head">
      <div><p class="eyebrow">PHASE 2.5 · ANNUAL BUDGET RECONSTRUCTION</p><h2>R5–R8を、同じ定義だけで比べる。</h2></div>
      <p>当初・補正・国の配分を混ぜず、案件名と金額が一次資料で直接対応する値だけを収録しています。</p>
    </div>
    <div class="annual-budget-metrics">
      <div><strong>${stats.confirmedProjectCount}</strong><span>CONFIRMED<br>案件金額確認</span></div>
      ${collection.targetFiscalYears.map((year) => `<div><strong>${stats.byFiscalYear[year] ?? 0}</strong><span>FY${year}<br>金額確認</span></div>`).join('')}
      <div><strong>${stats.comparable4}</strong><span>4-YEAR<br>同一定義比較</span></div>
    </div>
    <p class="annual-budget-policy">同一年度に複数の数字がある場合も、basis・budget stageが異なれば別系列です。自動合算しません。</p>`;
  const enrichmentSummary = document.querySelector('.enrichment-summary');
  const changesRoot = document.querySelector('#changes-root');
  if (enrichmentSummary) enrichmentSummary.insertAdjacentElement('afterend', section);
  else changesRoot?.insertAdjacentElement('afterend', section);
}

function renderDetail(collection: AnnualBudgetCollection, projectId: string) {
  if (document.querySelector('.annual-budget-detail')) return;
  const status = getAnnualBudgetAuditStatus(collection, projectId);
  const note = getAnnualBudgetAuditNote(collection, projectId);
  const observations = getAnnualBudgetObservations(collection, projectId);
  const section = document.createElement('section');
  section.className = 'detail-section detail-wide annual-budget-detail';
  section.innerHTML = `
    <div class="annual-budget-detail-head">
      <div><p class="eyebrow">PHASE 2.5 · ANNUAL BUDGET</p><h2>年度別予算・配分</h2></div>
      <span class="budget-audit-status status-${status.toLowerCase()}">${esc(auditLabels[status])}</span>
    </div>
    <p class="budget-intro">R5～R8の一次資料を案件scopeへ照合した結果です。全体事業費、契約額、累計投資額、複数箇所をまとめた予算事業額はここへ転記しません。</p>
    <div class="budget-year-grid">${collection.targetFiscalYears.map((year) => fiscalYearColumn(collection, year, observations)).join('')}</div>
    ${comparableNote(observations)}
    ${status === 'CONFIRMED_PROJECT_BUDGET' ? '' : `<p class="budget-audit-note">${esc(note)}</p>`}
    <div class="budget-rule">当初＋補正、国の配分＋県予算などは機械的に合算しません。空欄は0円ではなく「案件単位で確認できる金額を採用していない」ことを示します。</div>`;

  const enrichment = document.querySelector('.enrichment-detail');
  if (enrichment) enrichment.insertAdjacentElement('afterend', section);
  else {
    const wide = document.querySelectorAll<HTMLElement>('.detail-section.detail-wide');
    const anchor = wide.item(wide.length - 1);
    if (anchor) anchor.insertAdjacentElement('afterend', section);
  }
}

async function waitForMainView() {
  for (let frame = 0; frame < 180; frame += 1) {
    if (document.querySelector('.detail-main, .project-section, .error-panel')) return;
    await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
  }
}

async function phase25() {
  try {
    const response = await fetch(`${base}data/annual-budget-r5-r8.json`);
    if (!response.ok) return;
    const collection = await response.json() as AnnualBudgetCollection;
    await waitForMainView();
    const projectId = getProjectIdFromPath(location.pathname);
    if (projectId) renderDetail(collection, projectId);
    else renderHome(collection);
  } catch {
    // Core Phase 2 rendering remains available if this optional data layer fails.
  }
}

void phase25();
