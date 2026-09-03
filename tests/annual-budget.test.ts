import { describe, expect, it } from 'vitest';
import {
  aggregateAnnualBudget,
  getAnnualBudgetAuditStatus,
  getAnnualBudgetObservations,
  getComparableBudgetSeries,
} from '../src/annual-budget';
import type {
  AnnualBudgetAuditRecord,
  AnnualBudgetCollection,
  AnnualBudgetObservation,
} from '../src/annual-budget-types';

const observation = (
  fiscalYear: number,
  amountMillionYen: number,
  overrides: Partial<AnnualBudgetObservation> = {},
): AnnualBudgetObservation => ({
  fiscalYear,
  asOf: `${fiscalYear}-04-01`,
  amountMillionYen,
  basis: 'project_allocation',
  budgetStage: 'allocation',
  scope: 'project',
  sourceId: `source-${fiscalYear}`,
  ...overrides,
});

const record = (
  projectId: string,
  observations: AnnualBudgetObservation[] = [],
  auditStatus: AnnualBudgetAuditRecord['auditStatus'] = observations.length
    ? 'CONFIRMED_PROJECT_BUDGET'
    : 'SOURCE_NOT_FOUND',
): AnnualBudgetAuditRecord => ({
  projectId,
  auditStatus,
  observations,
  ...(auditStatus === 'CONFIRMED_PROJECT_BUDGET' ? {} : { note: '未確認' }),
});

const collection = (records: AnnualBudgetAuditRecord[]): AnnualBudgetCollection => ({
  schemaVersion: '2.5.0',
  generatedAt: '2026-09-03',
  targetFiscalYears: [2023, 2024, 2025, 2026],
  dataPolicy: 'test',
  defaultUnresolvedStatus: 'SOURCE_NOT_FOUND',
  defaultUnresolvedNote: '未確認',
  sources: [],
  records,
});

describe('Phase 2.5 annual budget reconstruction', () => {
  it('compares only observations with the same basis, budget stage and scope', () => {
    const observations = [
      observation(2023, 100),
      observation(2024, 120),
      observation(2025, 130),
      observation(2026, 140),
      observation(2026, 90, {
        basis: 'prefectural_budget',
        budgetStage: 'initial',
        sourceId: 'prefectural-2026',
      }),
    ];

    const series = getComparableBudgetSeries(observations);
    expect(series).toHaveLength(2);
    expect(series.find((item) => item.basis === 'project_allocation')?.observations).toHaveLength(4);
    expect(series.find((item) => item.basis === 'prefectural_budget')?.observations).toHaveLength(1);
  });

  it('does not treat a missing fiscal year as zero', () => {
    const data = collection([
      record('partial', [observation(2023, 100), observation(2025, 130)]),
    ]);
    const observations = getAnnualBudgetObservations(data, 'partial');

    expect(observations.map((entry) => entry.fiscalYear)).toEqual([2023, 2025]);
    expect(observations.some((entry) => entry.fiscalYear === 2024)).toBe(false);
    expect(observations.some((entry) => entry.amountMillionYen === 0)).toBe(false);
  });

  it('counts comparable years using like-for-like series, not any observation in the year', () => {
    const data = collection([
      record('four-year', [
        observation(2023, 100),
        observation(2024, 110),
        observation(2025, 120),
        observation(2026, 130),
      ]),
      record('mixed', [
        observation(2023, 100),
        observation(2024, 110),
        observation(2025, 120, { basis: 'prefectural_budget', budgetStage: 'initial' }),
        observation(2026, 130, { basis: 'prefectural_budget', budgetStage: 'initial' }),
      ]),
    ]);

    expect(aggregateAnnualBudget(data)).toEqual({
      confirmedProjectCount: 2,
      byFiscalYear: { 2023: 2, 2024: 2, 2025: 2, 2026: 2 },
      comparable2Plus: 2,
      comparable3Plus: 1,
      comparable4: 1,
    });
  });

  it('returns the explicit audit status and conservative default for absent records', () => {
    const data = collection([
      record('broader', [], 'BROADER_PROGRAM_ONLY'),
    ]);

    expect(getAnnualBudgetAuditStatus(data, 'broader')).toBe('BROADER_PROGRAM_ONLY');
    expect(getAnnualBudgetAuditStatus(data, 'missing')).toBe('SOURCE_NOT_FOUND');
  });
});
