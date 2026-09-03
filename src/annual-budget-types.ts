import type { BudgetBasis } from './enrichment-types';

export type BudgetStage = 'initial' | 'supplementary' | 'final' | 'allocation' | 'unknown';
export type BudgetScope = 'project';
export type BudgetAuditStatus =
  | 'CONFIRMED_PROJECT_BUDGET'
  | 'PROJECT_LISTED_NO_AMOUNT'
  | 'BROADER_PROGRAM_ONLY'
  | 'SCOPE_MISMATCH'
  | 'SOURCE_NOT_FOUND'
  | 'NOT_APPLICABLE';

export interface AnnualBudgetSource {
  id: string;
  title: string;
  publisher: string;
  url: string;
  accessed: string;
  fiscalYear: number;
  budgetStage: BudgetStage;
  locator?: string;
  note?: string;
}

export interface AnnualBudgetObservation {
  fiscalYear: number;
  asOf: string;
  amountMillionYen: number;
  basis: BudgetBasis;
  budgetStage: BudgetStage;
  scope: BudgetScope;
  sourceId: string;
  note?: string;
}

export interface AnnualBudgetAuditRecord {
  projectId: string;
  auditStatus: BudgetAuditStatus;
  observations: AnnualBudgetObservation[];
  note?: string;
}

export interface AnnualBudgetCollection {
  schemaVersion: string;
  generatedAt: string;
  targetFiscalYears: number[];
  dataPolicy: string;
  defaultUnresolvedStatus: BudgetAuditStatus;
  defaultUnresolvedNote: string;
  sources: AnnualBudgetSource[];
  records: AnnualBudgetAuditRecord[];
}
