import { describe, expect, it } from 'vitest';
import {
  aggregateProjects,
  filterProjects,
  getMonitoringLevel,
  matchesDepthFilter,
} from '../src/domain';
import type { Project } from '../src/types';

const baseProject = (overrides: Partial<Project> = {}): Project => ({
  id: 'inventory-project',
  name: 'テスト事業',
  category: 'road',
  categoryLabel: '道路',
  operator: '愛媛県',
  department: '道路建設課',
  municipalities: ['松山市'],
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
  lastVerified: '2026-08-31',
  summary: '一次資料で存在・位置を確認したInventory案件。',
  scope: '詳細数値は未確認。',
  geometryRef: 'inventory-project',
  locationAccuracy: 'approximate',
  locationSource: 'source-map',
  sources: [{
    id: 'source-map',
    title: 'えひめの土木2026 愛媛県管内図',
    publisher: '愛媛県',
    url: 'https://www.pref.ehime.jp/example.pdf',
    accessed: '2026-08-31',
  }],
  provenance: {},
  costHistory: [],
  scheduleHistory: [],
  progressHistory: [],
  ...overrides,
});

describe('monitoring levels', () => {
  it('keeps projects with no numeric observations at inventory level', () => {
    expect(getMonitoringLevel(baseProject())).toBe('inventory');
  });

  it('derives snapshot, history and enriched without storing a duplicate level field', () => {
    expect(getMonitoringLevel(baseProject({ totalProjectCostMillionYen: 1000 }))).toBe('snapshot');
    expect(getMonitoringLevel(baseProject({
      totalProjectCostMillionYen: 1200,
      costHistory: [
        { asOf: '2025-01-01', fiscalYear: 2025, valueMillionYen: 1000, sourceId: 'source-map' },
        { asOf: '2026-01-01', fiscalYear: 2026, valueMillionYen: 1200, sourceId: 'source-map' },
      ],
    }))).toBe('history');
    expect(getMonitoringLevel(baseProject(), true)).toBe('enriched');
  });

  it('implements Inventory / Snapshot+ / History+ / Enriched depth semantics', () => {
    expect(matchesDepthFilter('inventory', 'inventory')).toBe(true);
    expect(matchesDepthFilter('inventory', 'snapshot')).toBe(false);
    expect(matchesDepthFilter('snapshot', 'snapshot')).toBe(true);
    expect(matchesDepthFilter('history', 'snapshot')).toBe(true);
    expect(matchesDepthFilter('history', 'history')).toBe(true);
    expect(matchesDepthFilter('enriched', 'history')).toBe(true);
    expect(matchesDepthFilter('history', 'enriched')).toBe(false);
  });
});

describe('inventory filtering and aggregation', () => {
  it('combines depth with normal category and municipality filters using AND', () => {
    const inventory = baseProject({ id: 'inventory', geometryRef: 'inventory' });
    const snapshot = baseProject({ id: 'snapshot', geometryRef: 'snapshot', totalProjectCostMillionYen: 500 });
    const river = baseProject({ id: 'river', geometryRef: 'river', category: 'river', categoryLabel: '河川', municipalities: ['大洲市'] });
    const filtered = filterProjects(
      [inventory, snapshot, river],
      { query: '', category: 'road', operator: '', municipality: '松山市', status: '', depth: 'inventory' },
    );
    expect(filtered.map((project) => project.id)).toEqual(['inventory']);
  });

  it('never treats unknown cost as zero in the known-cost denominator or total', () => {
    const stats = aggregateProjects([
      baseProject({ id: 'unknown', geometryRef: 'unknown' }),
      baseProject({ id: 'known', geometryRef: 'known', totalProjectCostMillionYen: 2500 }),
    ]);
    expect(stats.projectCount).toBe(2);
    expect(stats.knownCostCount).toBe(1);
    expect(stats.totalKnownCostMillionYen).toBe(2500);
  });
});
