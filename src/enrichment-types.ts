import type { ProjectSource } from './types';

export type BudgetBasis = 'project_allocation' | 'national_subsidy' | 'prefectural_budget';
export type ObservationStatus = 'actual' | 'planned';
export type BenefitCostScope = 'project' | 'network';
export type BenefitCostPerspective = 'whole' | 'remaining';
export type DocumentedReasonType = 'cost_change' | 'schedule_change' | 'delay_context';

export interface AnnualBudgetEntry {
  fiscalYear: number;
  asOf: string;
  amountMillionYen: number;
  basis: BudgetBasis;
  sourceId: string;
  note?: string;
}

export interface CumulativeInvestmentEntry {
  fiscalYear: number;
  asOf: string;
  amountMillionYen: number;
  status: ObservationStatus;
  sourceId: string;
  note?: string;
}

export interface BenefitCostHistoryEntry {
  fiscalYear: number | null;
  asOf: string;
  value: number;
  scope: BenefitCostScope;
  perspective: BenefitCostPerspective;
  sourceId: string;
  note?: string;
}

export interface DocumentedReason {
  effectiveDate: string;
  type: DocumentedReasonType;
  summary: string;
  sourceId: string;
  note?: string;
}

export interface ProjectEnrichmentRecord {
  projectId: string;
  sources: ProjectSource[];
  annualBudgetHistory: AnnualBudgetEntry[];
  cumulativeInvestmentHistory: CumulativeInvestmentEntry[];
  benefitCostHistory: BenefitCostHistoryEntry[];
  documentedReasons: DocumentedReason[];
}

export interface EnrichmentCollection {
  enrichmentSchemaVersion: string;
  generatedAt: string;
  dataPolicy: string;
  records: ProjectEnrichmentRecord[];
}
