import type { Feature, FeatureCollection } from 'geojson';
import type { AnnualBudgetAuditRecord, AnnualBudgetCollection } from './annual-budget-types';
import type { EnrichmentCollection, ProjectEnrichmentRecord } from './enrichment-types';
import { representativePoint } from './phase26-data';
import type { Project, ProjectCategory, ProjectCollection, ProjectSource, ProjectStatus } from './types';

interface Phase27SourceSeed {
  id: string;
  title: string;
  publisher: string;
  url: string;
}

export interface Phase27AdditionSeed {
  id: string;
  name: string;
  category: ProjectCategory;
  categoryLabel: string;
  operator: string;
  department: string;
  municipalities: string[];
  status: ProjectStatus;
  statusLabel: string;
  summary: string;
  scope: string;
  source: Phase27SourceSeed;
}

export interface Phase27PatchSeed {
  projectId: string;
  status?: ProjectStatus;
  statusLabel?: string;
  plannedCompletionFiscalYear?: number | null;
  note: string;
  source: Phase27SourceSeed;
}

export interface Phase27Seed {
  schemaVersion: string;
  auditedAt: string;
  canonicalScope: string;
  additions: Phase27AdditionSeed[];
  patches: Phase27PatchSeed[];
}

function source(seed: Phase27Seed, value: Phase27SourceSeed): ProjectSource {
  return { ...value, accessed: seed.auditedAt, note: 'Phase 2.7 exhaustive universe audit evidence.' };
}

export function phase27Projects(seed: Phase27Seed): Project[] {
  return seed.additions.map((item) => {
    const primary = source(seed, item.source);
    return {
      id: item.id,
      name: item.name,
      category: item.category,
      categoryLabel: item.categoryLabel,
      operator: item.operator,
      department: item.department,
      municipalities: item.municipalities,
      status: item.status,
      statusLabel: item.statusLabel,
      startFiscalYear: null,
      plannedCompletionFiscalYear: null,
      totalProjectCostMillionYen: null,
      currentFiscalYearBudgetMillionYen: null,
      progressPercent: null,
      progressAsOf: null,
      landAcquisitionProgressPercent: null,
      benefitCostRatio: null,
      lastVerified: seed.auditedAt,
      summary: item.summary,
      scope: item.scope,
      geometryRef: item.id,
      locationAccuracy: 'approximate',
      locationSource: primary.id,
      locationNote: '公式資料の市町・地区名から作成した検索用代表点。正確な施工区域・線形・施設位置を示さない。',
      sources: [primary],
      provenance: { summary: primary.id, scope: primary.id, geometryRef: primary.id },
      costHistory: [],
      scheduleHistory: [],
      progressHistory: [],
    };
  });
}

function patchProject(project: Project, patch: Phase27PatchSeed, seed: Phase27Seed): Project {
  const primary = source(seed, patch.source);
  const provenance = { ...project.provenance };
  if (patch.status !== undefined) provenance.status = primary.id;
  if (patch.plannedCompletionFiscalYear !== undefined) provenance.plannedCompletionFiscalYear = primary.id;
  return {
    ...project,
    status: patch.status ?? project.status,
    statusLabel: patch.statusLabel ?? project.statusLabel,
    plannedCompletionFiscalYear: patch.plannedCompletionFiscalYear === undefined ? project.plannedCompletionFiscalYear : patch.plannedCompletionFiscalYear,
    lastVerified: seed.auditedAt,
    sources: [...project.sources, primary],
    provenance,
    scope: `${project.scope} Phase 2.7監査: ${patch.note}`,
  };
}

export function mergePhase27Projects(base: ProjectCollection, seed: Phase27Seed): ProjectCollection {
  const patches = new Map(seed.patches.map((item) => [item.projectId, item]));
  const patched = base.projects.map((project) => {
    const patch = patches.get(project.id);
    return patch ? patchProject(project, patch, seed) : project;
  });
  return {
    ...base,
    datasetTitle: 'Ehime Civil Works Monitor Phase 2.7 — Exhaustive Universe Audit',
    generatedAt: seed.auditedAt,
    dataPolicy: `${base.dataPolicy} Phase 2.7 canonical scope: ${seed.canonicalScope}`,
    projects: [...patched, ...phase27Projects(seed)],
  };
}

export function phase27Features(seed: Phase27Seed): Feature[] {
  return phase27Projects(seed).map((project) => ({
    type: 'Feature' as const,
    properties: { projectId: project.id, locationAccuracy: 'approximate', phase: '2.7' },
    geometry: { type: 'Point' as const, coordinates: representativePoint(project.municipalities, project.id) },
  }));
}

export function mergePhase27GeoJson(base: FeatureCollection, seed: Phase27Seed): FeatureCollection {
  return { ...base, features: [...base.features, ...phase27Features(seed)] };
}

export function mergePhase27Enrichment(base: EnrichmentCollection, seed: Phase27Seed): EnrichmentCollection {
  const additions: ProjectEnrichmentRecord[] = phase27Projects(seed).map((project) => ({
    projectId: project.id,
    sources: [],
    annualBudgetHistory: [],
    cumulativeInvestmentHistory: [],
    benefitCostHistory: [],
    documentedReasons: [],
  }));
  return { ...base, generatedAt: seed.auditedAt, records: [...base.records, ...additions] };
}

export function mergePhase27AnnualBudget(base: AnnualBudgetCollection, seed: Phase27Seed): AnnualBudgetCollection {
  const additions: AnnualBudgetAuditRecord[] = phase27Projects(seed).map((project) => ({
    projectId: project.id,
    auditStatus: 'SOURCE_NOT_FOUND',
    observations: [],
    note: 'Phase 2.7でcanonical inventoryへ追加。R5～R8案件単位年度予算は未監査であり、0円を意味しない。',
  }));
  return { ...base, generatedAt: seed.auditedAt, records: [...base.records, ...additions] };
}
