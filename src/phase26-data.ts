import type { Feature, FeatureCollection } from 'geojson';
import type { Project, ProjectCollection, ProjectSource } from './types';
import type { EnrichmentCollection, ProjectEnrichmentRecord } from './enrichment-types';
import type { AnnualBudgetCollection, AnnualBudgetAuditRecord } from './annual-budget-types';

type RoadSeed = [string, string, string, string[], number, number | null, string];
type SaboSeed = [string, string, string, number, number, number, number, number, string];

export interface Phase26Seed {
  v: string;
  d: string;
  roadSource: string;
  evalSource: string;
  roads: RoadSeed[];
  sabo: SaboSeed[];
}

const centers: Record<string, [number, number]> = {
  松山市: [132.765, 33.839], 伊予市: [132.703, 33.757], 内子町: [132.650, 33.548], 大洲市: [132.544, 33.506],
  愛南町: [132.584, 32.963], 宇和島市: [132.560, 33.223], 今治市: [132.997, 34.066], 四国中央市: [133.549, 33.981],
  西予市: [132.511, 33.363], 八幡浜市: [132.423, 33.463], 久万高原町: [132.901, 33.655], 松野町: [132.711, 33.227],
  鬼北町: [132.684, 33.255], 伊方町: [132.354, 33.488], 西条市: [133.181, 33.919], 新居浜市: [133.283, 33.960],
  宿毛市: [132.727, 32.939],
};

function hashOffset(id: string) {
  let hash = 0;
  for (const char of id) hash = ((hash * 31) + char.charCodeAt(0)) >>> 0;
  return [((hash % 9) - 4) * 0.002, ((((hash / 9) | 0) % 9) - 4) * 0.002] as const;
}

export function representativePoint(municipalities: string[], id: string): [number, number] {
  const points = municipalities.map((name) => centers[name]).filter((point): point is [number, number] => Boolean(point));
  if (!points.length) return [132.765, 33.839];
  const lon = points.reduce((sum, point) => sum + point[0], 0) / points.length;
  const lat = points.reduce((sum, point) => sum + point[1], 0) / points.length;
  const [dx, dy] = hashOffset(id);
  return [Number((lon + dx).toFixed(5)), Number((lat + dy).toFixed(5))];
}

function roadSource(seed: Phase26Seed): ProjectSource {
  return { id: 'phase26-road-program', title: '道路の整備に関するプログラム2018～2027（Vol.8）資料編（対象路線一覧表）', publisher: '愛媛県土木部道路都市局', url: seed.roadSource, accessed: seed.d, note: 'Phase 2.6 population rebuild primary source.' };
}

function evaluationSource(seed: Phase26Seed): ProjectSource {
  return { id: 'phase26-r7-second-evaluation', title: '令和7年度 愛媛県公共事業評価委員会（第2回）審議対象事業一覧表', publisher: '愛媛県', url: seed.evalSource, accessed: seed.d, note: 'Phase 2.6 sand-control cohort primary source.' };
}

function baseProject(id: string, name: string, municipalities: string[], source: ProjectSource, seed: Phase26Seed): Omit<Project, 'category' | 'categoryLabel' | 'operator' | 'department' | 'summary' | 'scope'> {
  return {
    id, name, municipalities, status: 'under_construction', statusLabel: '事業中', startFiscalYear: null, plannedCompletionFiscalYear: null,
    totalProjectCostMillionYen: null, currentFiscalYearBudgetMillionYen: null, progressPercent: null, progressAsOf: null,
    landAcquisitionProgressPercent: null, benefitCostRatio: null, lastVerified: seed.d, geometryRef: id, locationAccuracy: 'approximate',
    locationSource: source.id, locationNote: '公式資料の施工市町・地区名から作成した検索用代表点。正確な道路線形・施工区域・施設位置を示さない。',
    sources: [source], provenance: { geometryRef: source.id }, costHistory: [], scheduleHistory: [], progressHistory: [],
  };
}

export function phase26Projects(seed: Phase26Seed): Project[] {
  const roads = seed.roads.map(([id, name, operator, municipalities, start, completion, scale]) => {
    const source = roadSource(seed);
    const provenance: Record<string, string> = { startFiscalYear: source.id, summary: source.id, geometryRef: source.id };
    if (completion !== null) provenance.plannedCompletionFiscalYear = source.id;
    return {
      ...baseProject(id, name, municipalities, source, seed), category: 'road' as const, categoryLabel: '道路', operator,
      department: operator === '愛媛県' ? '道路建設課' : operator.includes('国土交通省') ? '四国地方整備局' : '高速道路事業',
      startFiscalYear: start, plannedCompletionFiscalYear: completion,
      summary: '道路整備プログラムVol.8の対象路線一覧表に独立した事業箇所として掲載されている道路整備事業。',
      scope: `公表事業規模${scale}。事業期間は一覧表の記載を使用し、完成年度が※の箇所はnullとして推測しない。`, provenance,
    } satisfies Project;
  });
  const sabo = seed.sabo.map(([id, name, municipality, start, completion, cost, progress, bc, scale]) => {
    const source = evaluationSource(seed);
    return {
      ...baseProject(id, name, [municipality], source, seed), category: 'sabo' as const, categoryLabel: '砂防', operator: '愛媛県', department: '砂防課',
      startFiscalYear: start, plannedCompletionFiscalYear: completion, totalProjectCostMillionYen: cost, progressPercent: progress,
      progressAsOf: '令和6年度まで', benefitCostRatio: bc,
      summary: `令和7年度公共事業評価委員会（第2回）で個別事業として審議された砂防事業。${scale}。`,
      scope: `${scale}。一覧表記載の概算事業費${cost}百万円、完了目標年度、事業費進捗率を収録。`,
      provenance: { startFiscalYear: source.id, plannedCompletionFiscalYear: source.id, totalProjectCostMillionYen: source.id, progressPercent: source.id, benefitCostRatio: source.id, summary: source.id, geometryRef: source.id },
    } satisfies Project;
  });
  return [...roads, ...sabo];
}

export function mergeProjects(base: ProjectCollection, seed: Phase26Seed): ProjectCollection {
  return { ...base, datasetTitle: 'Ehime Civil Works Monitor Phase 2.6 — Comprehensive Inventory', generatedAt: seed.d, projects: [...base.projects, ...phase26Projects(seed)] };
}

export function phase26Features(seed: Phase26Seed): Feature[] {
  return phase26Projects(seed).map((project) => ({ type: 'Feature' as const, properties: { projectId: project.id, locationAccuracy: 'approximate', phase: '2.6' }, geometry: { type: 'Point' as const, coordinates: representativePoint(project.municipalities, project.id) } }));
}

export function mergeGeoJson(base: FeatureCollection, seed: Phase26Seed): FeatureCollection {
  return { ...base, features: [...base.features, ...phase26Features(seed)] };
}

export function mergeEnrichment(base: EnrichmentCollection, seed: Phase26Seed): EnrichmentCollection {
  const additions: ProjectEnrichmentRecord[] = phase26Projects(seed).map((project) => ({ projectId: project.id, sources: [], annualBudgetHistory: [], cumulativeInvestmentHistory: [], benefitCostHistory: [], documentedReasons: [] }));
  return { ...base, generatedAt: seed.d, records: [...base.records, ...additions] };
}

export function mergeAnnualBudget(base: AnnualBudgetCollection, seed: Phase26Seed): AnnualBudgetCollection {
  const additions: AnnualBudgetAuditRecord[] = phase26Projects(seed).map((project) => ({ projectId: project.id, auditStatus: 'SOURCE_NOT_FOUND', observations: [], note: 'Phase 2.6でcanonical inventoryへ追加。R5～R8案件単位年度予算は未監査であり、0円を意味しない。' }));
  return { ...base, generatedAt: seed.d, records: [...base.records, ...additions] };
}
