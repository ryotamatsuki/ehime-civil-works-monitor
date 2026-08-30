import { describe, expect, it } from 'vitest';
import {
  aggregateProjects,
  filterProjects,
  formatMillionYen,
  getLatestChangeEvent,
  getProjectAlerts,
  getProjectChangeEvents,
  getProjectIdFromPath,
} from '../src/domain';
import type { Project } from '../src/types';

const project = (overrides: Partial<Project>): Project => ({
  id: 'test-project',
  name: 'テスト河川事業',
  category: 'river',
  categoryLabel: '河川',
  operator: '愛媛県',
  department: '河川課',
  municipalities: ['松山市'],
  status: 'under_construction',
  statusLabel: '事業中',
  startFiscalYear: 2020,
  plannedCompletionFiscalYear: 2030,
  totalProjectCostMillionYen: 1200,
  currentFiscalYearBudgetMillionYen: null,
  progressPercent: 50,
  progressAsOf: '令和6年度末',
  landAcquisitionProgressPercent: null,
  benefitCostRatio: 1.5,
  lastVerified: '2026-08-30',
  summary: 'summary',
  scope: 'scope',
  geometryRef: 'test-project',
  locationAccuracy: 'approximate',
  locationSource: 'source-1',
  sources: [{ id: 'source-1', title: 'source', publisher: '愛媛県', url: 'https://example.com', accessed: '2026-08-30' }],
  provenance: {},
  costHistory: [],
  scheduleHistory: [],
  progressHistory: [],
  ...overrides,
});

describe('filterProjects', () => {
  const projects = [
    project({ id: 'a', name: '松山河川', municipalities: ['松山市'] }),
    project({ id: 'b', name: '大洲道路', category: 'road', categoryLabel: '道路', municipalities: ['大洲市'] }),
  ];

  it('filters by free text and municipality', () => {
    expect(filterProjects(projects, { query: '大洲', category: '', operator: '', municipality: '', status: '' }).map((p) => p.id)).toEqual(['b']);
    expect(filterProjects(projects, { query: '', category: '', operator: '', municipality: '松山市', status: '' }).map((p) => p.id)).toEqual(['a']);
  });

  it('combines alert filters with normal filters using AND', () => {
    const changedRoad = project({
      id: 'changed-road',
      category: 'road',
      categoryLabel: '道路',
      municipalities: ['大洲市'],
      costHistory: [
        { asOf: '2024-01-01', fiscalYear: 2024, valueMillionYen: 100, sourceId: 'source-1' },
        { asOf: '2025-01-01', fiscalYear: 2025, valueMillionYen: 120, sourceId: 'source-1' },
      ],
    });
    const changedRiver = project({
      id: 'changed-river',
      municipalities: ['松山市'],
      scheduleHistory: [
        { asOf: '2024-01-01', plannedCompletionFiscalYear: 2028, sourceId: 'source-1' },
        { asOf: '2025-01-01', plannedCompletionFiscalYear: 2030, sourceId: 'source-1' },
      ],
    });
    const filtered = filterProjects([changedRoad, changedRiver], {
      query: '', category: 'road', operator: '', municipality: '大洲市', status: '', alert: 'cost_increase',
    });
    expect(filtered.map((p) => p.id)).toEqual(['changed-road']);
    expect(filterProjects([changedRoad, changedRiver], { query: '', category: '', operator: '', municipality: '', status: '', alert: 'delayed' }).map((p) => p.id)).toEqual(['changed-river']);
  });
});

describe('change detection', () => {
  it('detects a cost increase with absolute and percent changes', () => {
    const p = project({ costHistory: [
      { asOf: '2024-01-01', fiscalYear: 2024, valueMillionYen: 100, sourceId: 'source-1' },
      { asOf: '2025-01-01', fiscalYear: 2025, valueMillionYen: 120, sourceId: 'source-1' },
    ] });
    const event = getProjectChangeEvents(p)[0];
    expect(event.type).toBe('cost_increase');
    expect(event.absoluteChange).toBe(20);
    expect(event.percentChange).toBe(20);
    expect(event.severity).toBe('major');
  });

  it('does not create a cost alert when cost is unchanged', () => {
    const p = project({ costHistory: [
      { asOf: '2024-01-01', fiscalYear: 2024, valueMillionYen: 100, sourceId: 'source-1' },
      { asOf: '2025-01-01', fiscalYear: 2025, valueMillionYen: 100, sourceId: 'source-1' },
    ] });
    expect(getProjectChangeEvents(p).filter((event) => event.type.startsWith('cost_'))).toHaveLength(0);
  });

  it('detects delayed and accelerated schedules', () => {
    const delayed = project({ scheduleHistory: [
      { asOf: '2024-01-01', plannedCompletionFiscalYear: 2026, sourceId: 'source-1' },
      { asOf: '2025-01-01', plannedCompletionFiscalYear: 2028, sourceId: 'source-1' },
    ] });
    expect(getProjectChangeEvents(delayed)[0]).toMatchObject({ type: 'delayed', absoluteChange: 2, severity: 'major' });

    const accelerated = project({ scheduleHistory: [
      { asOf: '2024-01-01', plannedCompletionFiscalYear: 2030, sourceId: 'source-1' },
      { asOf: '2025-01-01', plannedCompletionFiscalYear: 2029, sourceId: 'source-1' },
    ] });
    expect(getProjectChangeEvents(accelerated)[0]).toMatchObject({ type: 'accelerated', absoluteChange: -1, severity: 'info' });
  });

  it('detects a progress update in percentage points', () => {
    const p = project({ progressHistory: [
      { asOf: '2024-03-31', progressPercent: 50, sourceId: 'source-1' },
      { asOf: '2025-03-31', progressPercent: 65, sourceId: 'source-1' },
    ] });
    expect(getProjectChangeEvents(p)[0]).toMatchObject({ type: 'progress_updated', absoluteChange: 15 });
  });

  it('handles missing history without crashing', () => {
    const p = project({ costHistory: undefined, scheduleHistory: undefined, progressHistory: undefined });
    expect(getProjectChangeEvents(p)).toEqual([]);
    expect(getProjectAlerts(p)).toEqual([]);
    expect(getLatestChangeEvent(p)).toBeNull();
  });

  it('avoids division by zero for cost percent changes', () => {
    const p = project({ costHistory: [
      { asOf: '2024-01-01', fiscalYear: 2024, valueMillionYen: 0, sourceId: 'source-1' },
      { asOf: '2025-01-01', fiscalYear: 2025, valueMillionYen: 100, sourceId: 'source-1' },
    ] });
    expect(getProjectChangeEvents(p)[0].percentChange).toBeUndefined();
  });
});

describe('aggregateProjects', () => {
  it('sums only known costs', () => {
    const stats = aggregateProjects([project({ id: 'a', totalProjectCostMillionYen: 1200 }), project({ id: 'b', totalProjectCostMillionYen: null })]);
    expect(stats.projectCount).toBe(2);
    expect(stats.knownCostCount).toBe(1);
    expect(stats.totalKnownCostMillionYen).toBe(1200);
  });

  it('counts projects with cost and delay alerts and recent updates', () => {
    const p = project({
      costHistory: [
        { asOf: '2025-01-01', fiscalYear: 2025, valueMillionYen: 100, sourceId: 'source-1' },
        { asOf: '2025-08-28', fiscalYear: 2025, valueMillionYen: 120, sourceId: 'source-1' },
      ],
      scheduleHistory: [
        { asOf: '2025-01-01', plannedCompletionFiscalYear: 2028, sourceId: 'source-1' },
        { asOf: '2025-08-28', plannedCompletionFiscalYear: 2030, sourceId: 'source-1' },
      ],
    });
    const stats = aggregateProjects([p], new Date('2025-09-01T00:00:00Z'));
    expect(stats.costIncreaseProjectCount).toBe(1);
    expect(stats.delayedProjectCount).toBe(1);
    expect(stats.updatedLast365Days).toBe(1);
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
