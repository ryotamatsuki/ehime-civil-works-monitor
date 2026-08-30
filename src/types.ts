export type ProjectCategory = 'river' | 'coast' | 'sabo' | 'road' | 'urban';
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
}

export interface ProjectCollection {
  schemaVersion: string;
  datasetTitle: string;
  generatedAt: string;
  dataPolicy: string;
  projects: Project[];
}
