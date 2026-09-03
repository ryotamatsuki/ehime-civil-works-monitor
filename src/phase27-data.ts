import type { Feature, FeatureCollection } from 'geojson';
import type { AnnualBudgetCollection, AnnualBudgetAuditRecord } from './annual-budget-types';
import type { EnrichmentCollection, ProjectEnrichmentRecord } from './enrichment-types';
import type { Project, ProjectCategory, ProjectCollection, ProjectSource } from './types';
import { representativePoint } from './phase26-data';
import './phase27.css';

type SourceSeed = { title: string; publisher: string; url: string };
type ProjectSeed = [
  string,
  string,
  ProjectCategory,
  string,
  string,
  string[],
  string,
  string,
];

export interface Phase27Seed {
  v: string;
  d: string;
  expectedAdditions: number;
  expectedRuntimeTotal: number;
  sources: Record<string, SourceSeed>;
  projects: ProjectSeed[];
  excludedCandidates: Array<{ name: string; classification: string; reason: string }>;
}

function sourceFor(seed: Phase27Seed, key: string): ProjectSource {
  const source = seed.sources[key];
  if (!source) throw new Error(`Unknown Phase 2.7 source: ${key}`);
  return {
    id: `phase27-${key}`,
    title: source.title,
    publisher: source.publisher,
    url: source.url,
    accessed: seed.d,
    note: 'Phase 2.7A/2.7A-2 candidate reconciliation primary source.',
  };
}

export function phase27Projects(seed: Phase27Seed): Project[] {
  return seed.projects.map(([id, name, category, categoryLabel, department, municipalities, sourceKey, scope]) => {
    const source = sourceFor(seed, sourceKey);
    return {
      id,
      name,
      category,
      categoryLabel,
      operator: '愛媛県',
      department,
      municipalities,
      status: 'under_construction',
      statusLabel: '事業中',
      startFiscalYear: null,
      plannedCompletionFiscalYear: null,
      totalProjectCostMillionYen: null,
      currentFiscalYearBudgetMillionYen: null,
      progressPercent: null,
      progressAsOf: null,
      landAcquisitionProgressPercent: null,
      benefitCostRatio: null,
      lastVerified: seed.d,
      summary: scope,
      scope,
      geometryRef: id,
      locationAccuracy: 'approximate',
      locationSource: source.id,
      locationNote: '公式資料に記載された市町・地区を基に作成した検索用代表点。正確な施工区域・施設位置・河川改修区間を示さない。',
      sources: [source],
      provenance: { summary: source.id, geometryRef: source.id },
      costHistory: [],
      scheduleHistory: [],
      progressHistory: [],
    } satisfies Project;
  });
}

export function mergePhase27Projects(base: ProjectCollection, seed: Phase27Seed): ProjectCollection {
  return {
    ...base,
    datasetTitle: 'Ehime Civil Works Monitor Phase 2.7 — Reconciled Canonical Expansion',
    generatedAt: seed.d,
    projects: [...base.projects, ...phase27Projects(seed)],
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
  return { ...base, generatedAt: seed.d, records: [...base.records, ...additions] };
}

export function mergePhase27AnnualBudget(base: AnnualBudgetCollection, seed: Phase27Seed): AnnualBudgetCollection {
  const additions: AnnualBudgetAuditRecord[] = phase27Projects(seed).map((project) => ({
    projectId: project.id,
    auditStatus: 'SOURCE_NOT_FOUND',
    observations: [],
    note: 'Phase 2.7でcanonical inventoryへ追加。R5～R8案件単位年度予算は未監査であり、0円を意味しない。',
  }));
  return { ...base, generatedAt: seed.d, records: [...base.records, ...additions] };
}
