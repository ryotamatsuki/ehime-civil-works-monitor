import type { EnrichmentCollection, ProjectEnrichmentRecord } from './enrichment-types';

export interface EnrichmentStats {
  enrichedProjectCount: number;
  annualBudgetProjectCount: number;
  cumulativeInvestmentProjectCount: number;
  benefitCostHistoryProjectCount: number;
  documentedReasonProjectCount: number;
  multiPeriodBenefitCostProjectCount: number;
}

export function getEnrichmentRecord(
  enrichment: EnrichmentCollection,
  projectId: string,
): ProjectEnrichmentRecord | null {
  return enrichment.records.find((record) => record.projectId === projectId) ?? null;
}

export function aggregateEnrichment(enrichment: EnrichmentCollection): EnrichmentStats {
  const records = enrichment.records;
  return {
    enrichedProjectCount: records.filter((record) =>
      record.annualBudgetHistory.length > 0 ||
      record.cumulativeInvestmentHistory.length > 0 ||
      record.benefitCostHistory.length > 0 ||
      record.documentedReasons.length > 0,
    ).length,
    annualBudgetProjectCount: records.filter((record) => record.annualBudgetHistory.length > 0).length,
    cumulativeInvestmentProjectCount: records.filter((record) => record.cumulativeInvestmentHistory.length > 0).length,
    benefitCostHistoryProjectCount: records.filter((record) => record.benefitCostHistory.length > 0).length,
    documentedReasonProjectCount: records.filter((record) => record.documentedReasons.length > 0).length,
    multiPeriodBenefitCostProjectCount: records.filter((record) => {
      const dates = new Set(record.benefitCostHistory.map((entry) => entry.asOf));
      return dates.size >= 2;
    }).length,
  };
}
