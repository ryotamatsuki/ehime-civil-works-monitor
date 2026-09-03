import type {
  AnnualBudgetAuditRecord,
  AnnualBudgetCollection,
  AnnualBudgetObservation,
  AnnualBudgetSource,
  BudgetAuditStatus,
} from './annual-budget-types';

export interface AnnualBudgetStats {
  confirmedProjectCount: number;
  byFiscalYear: Record<number, number>;
  comparable2Plus: number;
  comparable3Plus: number;
  comparable4: number;
}

export function getAnnualBudgetRecord(
  collection: AnnualBudgetCollection,
  projectId: string,
): AnnualBudgetAuditRecord | null {
  return collection.records.find((record) => record.projectId === projectId) ?? null;
}

export function getAnnualBudgetSource(
  collection: AnnualBudgetCollection,
  sourceId: string,
): AnnualBudgetSource | null {
  return collection.sources.find((source) => source.id === sourceId) ?? null;
}

export function getAnnualBudgetAuditStatus(
  collection: AnnualBudgetCollection,
  projectId: string,
): BudgetAuditStatus {
  return getAnnualBudgetRecord(collection, projectId)?.auditStatus ?? collection.defaultUnresolvedStatus;
}

export function getAnnualBudgetAuditNote(
  collection: AnnualBudgetCollection,
  projectId: string,
): string {
  return getAnnualBudgetRecord(collection, projectId)?.note ?? collection.defaultUnresolvedNote;
}

export function getAnnualBudgetObservations(
  collection: AnnualBudgetCollection,
  projectId: string,
): AnnualBudgetObservation[] {
  return [...(getAnnualBudgetRecord(collection, projectId)?.observations ?? [])]
    .sort((a, b) => a.fiscalYear - b.fiscalYear || a.asOf.localeCompare(b.asOf));
}

export function aggregateAnnualBudget(collection: AnnualBudgetCollection): AnnualBudgetStats {
  const byFiscalYear: Record<number, number> = Object.fromEntries(
    collection.targetFiscalYears.map((fiscalYear) => [fiscalYear, 0]),
  );
  let comparable2Plus = 0;
  let comparable3Plus = 0;
  let comparable4 = 0;
  let confirmedProjectCount = 0;

  for (const record of collection.records) {
    const years = new Set(record.observations.map((entry) => entry.fiscalYear));
    if (record.auditStatus === 'CONFIRMED_PROJECT_BUDGET' && years.size > 0) confirmedProjectCount += 1;
    for (const fiscalYear of collection.targetFiscalYears) {
      if (years.has(fiscalYear)) byFiscalYear[fiscalYear] = (byFiscalYear[fiscalYear] ?? 0) + 1;
    }
    if (years.size >= 2) comparable2Plus += 1;
    if (years.size >= 3) comparable3Plus += 1;
    if (collection.targetFiscalYears.every((fiscalYear) => years.has(fiscalYear))) comparable4 += 1;
  }

  return { confirmedProjectCount, byFiscalYear, comparable2Plus, comparable3Plus, comparable4 };
}
