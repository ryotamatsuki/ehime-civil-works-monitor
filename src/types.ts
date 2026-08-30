export type ProjectCategory = 'river' | 'coast' | 'sabo' | 'road' | 'urban' | 'agriculture' | 'port';
export type ProjectStatus = 'planned' | 'under_construction' | 'completed' | 'unknown';
export type LocationAccuracy = 'official' | 'derived' | 'approximate' | 'unknown';

export interface ProjectSource {
  id: string;
  title: string;
  publisher: string;
  url: string;
  accessed: string;
  note?: string;
}

export interface CostHistoryEntry {
  asOf: string;
  fiscalYear: number | null;
  valueMillionYen: number;
  sourceId: string;
  note?: string;
}

export interface ScheduleHistoryEntry {
  asOf: string;
  plannedCompletionFiscalYear: number;
  sourceId: string;
  note?: string;
}

export interface ProgressHistoryEntry {
  asOf: string;
  progressPercent: number;
  sourceId: string;
  note?: string;
}

export type ChangeType =
  | 'cost_increase'
  | 'cost_decrease'
  | 'delayed'
  | 'accelerated'
  | 'progress_updated';

export type AlertSeverity = 'info' | 'notice' | 'major';

export interface ChangeEvent {
  projectId: string;
  type: ChangeType;
  effectiveDate: string;
  sourceId: string;
  previousValue: number;
  currentValue: number;
  absoluteChange: number;
  percentChange?: number;
  severity: AlertSeverity;
  note?: string;
}

export interface Project {
  id: string;
  name: string;
  category: ProjectCategory;
  categoryLabel: string;
  operator: string;
  department: string;
  municipalities: string[];
  status: ProjectStatus;
  statusLabel: string;
  startFiscalYear: number | null;
  plannedCompletionFiscalYear: number | null;
  totalProjectCostMillionYen: number | null;
  currentFiscalYearBudgetMillionYen: number | null;
  progressPercent: number | null;
  progressAsOf: string | null;
  landAcquisitionProgressPercent: number | null;
  benefitCostRatio: number | null;
  lastVerified: string;
  summary: string;
  scope: string;
  geometryRef: string | null;
  locationAccuracy: LocationAccuracy;
  locationSource: string | null;
  locationNote?: string;
  sources: ProjectSource[];
  provenance: Record<string, string>;
  costHistory?: CostHistoryEntry[];
  scheduleHistory?: ScheduleHistoryEntry[];
  progressHistory?: ProgressHistoryEntry[];
}

export interface ProjectCollection {
  schemaVersion: string;
  datasetTitle: string;
  generatedAt: string;
  dataPolicy: string;
  projects: Project[];
}
