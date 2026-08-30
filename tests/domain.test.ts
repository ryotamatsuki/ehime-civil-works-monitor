import { describe, expect, it } from 'vitest';
import { aggregateProjects, filterProjects, formatMillionYen, getProjectIdFromPath } from '../src/domain';
import type { Project } from '../src/types';

const project = (overrides: Partial<Project>): Project => ({
  id: 'test-project', name: 'テスト河川事業', category: 'river', categoryLabel: '河川', operator: '愛媛県', department: '河川課', municipalities: ['松山市'], status: 'under_construction', statusLabel: '事業中', startFiscalYear: 2020, plannedCompletionFiscalYear: 2030, totalProjectCostMillionYen: 1200, currentFiscalYearBudgetMillionYen: null, progressPercent: 50, progressAsOf: '令和6年度末', landAcquisitionProgressPercent: null, benefitCostRatio: 1.5, lastVerified: '2026-08-30', summary: 'summary', scope: 'scope', geometryRef: 'test-project', locationAccuracy: 'approximate', locationSource: 'source-1', sources: [{ id: 'source-1', title: 'source', publisher: '愛媛県', url: 'https://example.com', accessed: '2026-08-30' }], provenance: {}, ...overrides,
});

describe('filterProjects', () => {
  const projects = [project({ id: 'a', name: '松山河川', municipalities: ['松山市'] }), project({ id: 'b', name: '大洲道路', category: 'road', categoryLabel: '道路', municipalities: ['大洲市'] })];
  it('filters by free text and municipality', () => {
    expect(filterProjects(projects, { query: '大洲', category: '', operator: '', municipality: '', status: '' }).map((p) => p.id)).toEqual(['b']);
    expect(filterProjects(projects, { query: '', category: '', operator: '', municipality: '松山市', status: '' }).map((p) => p.id)).toEqual(['a']);
  });
});

describe('aggregateProjects', () => {
  it('sums only known costs', () => {
    const stats = aggregateProjects([project({ id: 'a', totalProjectCostMillionYen: 1200 }), project({ id: 'b', totalProjectCostMillionYen: null })]);
    expect(stats.projectCount).toBe(2);
    expect(stats.knownCostCount).toBe(1);
    expect(stats.totalKnownCostMillionYen).toBe(1200);
  });
});

describe('routing and formatting', () => {
  it('extracts project ids from static detail paths', () => {
    expect(getProjectIdFromPath('/ehime-civil-works-monitor/projects/abc-road/')).toBe('abc-road');
    expect(getProjectIdFromPath('/ehime-civil-works-monitor/')).toBeNull();
  });
  it('formats project costs', () => {
    expect(formatMillionYen(1200)).toBe('12億円');
    expect(formatMillionYen(null)).toBe('公表値未確認');
  });
});
