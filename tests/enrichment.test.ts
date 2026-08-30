import { describe, expect, it } from 'vitest';
import { aggregateEnrichment, getEnrichmentRecord } from '../src/enrichment';
import type { EnrichmentCollection, ProjectEnrichmentRecord } from '../src/enrichment-types';

const record = (projectId: string, overrides: Partial<ProjectEnrichmentRecord> = {}): ProjectEnrichmentRecord => ({
  projectId,
  sources: [{ id: 'source-1', title: 'source', publisher: '愛媛県', url: 'https://example.com', accessed: '2026-08-30' }],
  annualBudgetHistory: [],
  cumulativeInvestmentHistory: [],
  benefitCostHistory: [],
  documentedReasons: [],
  ...overrides,
});

const collection = (records: ProjectEnrichmentRecord[]): EnrichmentCollection => ({
  enrichmentSchemaVersion: '2.1.0',
  generatedAt: '2026-08-30',
  dataPolicy: 'test',
  records,
});

describe('Phase 2.1 enrichment', () => {
  it('finds a project enrichment record without mutating the base project model', () => {
    const data = collection([record('a'), record('b')]);
    expect(getEnrichmentRecord(data, 'b')?.projectId).toBe('b');
    expect(getEnrichmentRecord(data, 'missing')).toBeNull();
  });

  it('counts data depth by metric and multi-period B/C', () => {
    const data = collection([
      record('deep', {
        annualBudgetHistory: [{ fiscalYear: 2025, asOf: '2025-04-01', amountMillionYen: 100, basis: 'project_allocation', sourceId: 'source-1' }],
        cumulativeInvestmentHistory: [{ fiscalYear: 2024, asOf: '2025-03-31', amountMillionYen: 400, status: 'actual', sourceId: 'source-1' }],
        benefitCostHistory: [
          { fiscalYear: 2023, asOf: '2023-10-01', value: 1.1, scope: 'project', perspective: 'whole', sourceId: 'source-1' },
          { fiscalYear: 2025, asOf: '2025-08-01', value: 1.2, scope: 'project', perspective: 'whole', sourceId: 'source-1' },
        ],
        documentedReasons: [{ effectiveDate: '2025-08-01', type: 'cost_change', summary: '増額', sourceId: 'source-1' }],
      }),
      record('bc-only', {
        benefitCostHistory: [{ fiscalYear: 2025, asOf: '2025-08-01', value: 2.0, scope: 'project', perspective: 'whole', sourceId: 'source-1' }],
      }),
      record('empty'),
    ]);

    expect(aggregateEnrichment(data)).toEqual({
      enrichedProjectCount: 2,
      annualBudgetProjectCount: 1,
      cumulativeInvestmentProjectCount: 1,
      benefitCostHistoryProjectCount: 2,
      documentedReasonProjectCount: 1,
      multiPeriodBenefitCostProjectCount: 1,
    });
  });

  it('does not treat whole/remaining B/C observations on the same date as multiple periods', () => {
    const data = collection([
      record('same-date', {
        benefitCostHistory: [
          { fiscalYear: 2025, asOf: '2025-08-28', value: 1.0, scope: 'project', perspective: 'whole', sourceId: 'source-1' },
          { fiscalYear: 2025, asOf: '2025-08-28', value: 1.5, scope: 'project', perspective: 'remaining', sourceId: 'source-1' },
        ],
      }),
    ]);
    expect(aggregateEnrichment(data).multiPeriodBenefitCostProjectCount).toBe(0);
  });
});
