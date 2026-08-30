import type { ChangeEvent, ChangeType, MonitoringLevel, Project } from './types';

export type DepthFilter = '' | 'inventory' | 'snapshot' | 'history' | 'enriched';

export interface ProjectFilters {
  query: string;
  category: string;
  operator: string;
  municipality: string;
  status: string;
  alert?: string;
  depth?: DepthFilter;
}

export interface DashboardStats {
  projectCount: number;
  inventoryCount: number;
  monitoredCount: number;
  historyCount: number;
  enrichedCount: number;
  knownCostCount: number;
  totalKnownCostMillionYen: number;
  statusCounts: Record<string, number>;
  categoryCounts: Record<string, number>;
  costIncreaseProjectCount: number;
  delayedProjectCount: number;
  updatedLast365Days: number;
}

function costSeverity(percentChange?: number): 'notice' | 'major' {
  return percentChange !== undefined && Math.abs(percentChange) >= 10 ? 'major' : 'notice';
}

function eventSort(a: ChangeEvent, b: ChangeEvent): number {
  if (a.effectiveDate !== b.effectiveDate) return b.effectiveDate.localeCompare(a.effectiveDate);
  return a.type.localeCompare(b.type);
}

export function getProjectChangeEvents(project: Project): ChangeEvent[] {
  const events: ChangeEvent[] = [];
  const costHistory = [...(project.costHistory ?? [])].sort((a, b) => a.asOf.localeCompare(b.asOf));
  const scheduleHistory = [...(project.scheduleHistory ?? [])].sort((a, b) => a.asOf.localeCompare(b.asOf));
  const progressHistory = [...(project.progressHistory ?? [])].sort((a, b) => a.asOf.localeCompare(b.asOf));

  for (let i = 1; i < costHistory.length; i += 1) {
    const previous = costHistory[i - 1];
    const current = costHistory[i];
    const change = current.valueMillionYen - previous.valueMillionYen;
    if (change === 0) continue;
    const percentChange = previous.valueMillionYen === 0 ? undefined : (change / previous.valueMillionYen) * 100;
    events.push({
      projectId: project.id,
      type: change > 0 ? 'cost_increase' : 'cost_decrease',
      effectiveDate: current.asOf,
      sourceId: current.sourceId,
      previousValue: previous.valueMillionYen,
      currentValue: current.valueMillionYen,
      absoluteChange: change,
      percentChange,
      severity: costSeverity(percentChange),
      note: current.note,
    });
  }

  for (let i = 1; i < scheduleHistory.length; i += 1) {
    const previous = scheduleHistory[i - 1];
    const current = scheduleHistory[i];
    const change = current.plannedCompletionFiscalYear - previous.plannedCompletionFiscalYear;
    if (change === 0) continue;
    events.push({
      projectId: project.id,
      type: change > 0 ? 'delayed' : 'accelerated',
      effectiveDate: current.asOf,
      sourceId: current.sourceId,
      previousValue: previous.plannedCompletionFiscalYear,
      currentValue: current.plannedCompletionFiscalYear,
      absoluteChange: change,
      severity: change > 0 ? (change >= 2 ? 'major' : 'notice') : 'info',
      note: current.note,
    });
  }

  for (let i = 1; i < progressHistory.length; i += 1) {
    const previous = progressHistory[i - 1];
    const current = progressHistory[i];
    const change = current.progressPercent - previous.progressPercent;
    if (change === 0) continue;
    events.push({
      projectId: project.id,
      type: 'progress_updated',
      effectiveDate: current.asOf,
      sourceId: current.sourceId,
      previousValue: previous.progressPercent,
      currentValue: current.progressPercent,
      absoluteChange: change,
      severity: 'info',
      note: current.note,
    });
  }

  return events.sort(eventSort);
}

export function getAllChangeEvents(projects: Project[]): ChangeEvent[] {
  return projects.flatMap(getProjectChangeEvents).sort(eventSort);
}

export function getLatestChangeEvent(project: Project): ChangeEvent | null {
  return getProjectChangeEvents(project)[0] ?? null;
}

export function getProjectAlerts(project: Project): ChangeEvent[] {
  return getProjectChangeEvents(project);
}

function hasAlert(project: Project, alert: string): boolean {
  const events = getProjectChangeEvents(project);
  if (!alert) return true;
  if (alert === 'changed') return events.length > 0;
  return events.some((event) => event.type === alert);
}

function hasMultiPeriodHistory(project: Project): boolean {
  return [project.costHistory, project.scheduleHistory, project.progressHistory].some((history) => (history?.length ?? 0) >= 2);
}

function hasSnapshotData(project: Project): boolean {
  return [
    project.startFiscalYear,
    project.plannedCompletionFiscalYear,
    project.totalProjectCostMillionYen,
    project.progressPercent,
    project.landAcquisitionProgressPercent,
    project.benefitCostRatio,
  ].some((value) => value !== null) || [project.costHistory, project.scheduleHistory, project.progressHistory].some((history) => (history?.length ?? 0) > 0);
}

export function getMonitoringLevel(project: Project, isEnriched = false): MonitoringLevel {
  if (isEnriched) return 'enriched';
  if (hasMultiPeriodHistory(project)) return 'history';
  if (hasSnapshotData(project)) return 'snapshot';
  return 'inventory';
}

export function matchesDepthFilter(level: MonitoringLevel, filter: DepthFilter): boolean {
  if (!filter) return true;
  if (filter === 'inventory') return level === 'inventory';
  if (filter === 'snapshot') return level !== 'inventory';
  if (filter === 'history') return level === 'history' || level === 'enriched';
  return level === 'enriched';
}

export function filterProjects(
  projects: Project[],
  filters: ProjectFilters,
  enrichedProjectIds: ReadonlySet<string> = new Set<string>(),
): Project[] {
  const q = filters.query.trim().toLocaleLowerCase('ja-JP');
  return projects.filter((project) => {
    const haystack = [project.name, project.summary, ...project.municipalities]
      .join(' ')
      .toLocaleLowerCase('ja-JP');
    const level = getMonitoringLevel(project, enrichedProjectIds.has(project.id));
    return (
      (!q || haystack.includes(q)) &&
      (!filters.category || project.category === filters.category) &&
      (!filters.operator || project.operator === filters.operator) &&
      (!filters.municipality || project.municipalities.includes(filters.municipality)) &&
      (!filters.status || project.status === filters.status) &&
      hasAlert(project, filters.alert ?? '') &&
      matchesDepthFilter(level, filters.depth ?? '')
    );
  });
}

function changedWithinDays(project: Project, referenceDate: Date, days: number): boolean {
  const reference = referenceDate.getTime();
  const maxAge = days * 24 * 60 * 60 * 1000;
  return getProjectChangeEvents(project).some((event) => {
    const eventTime = Date.parse(`${event.effectiveDate}T00:00:00Z`);
    const age = reference - eventTime;
    return Number.isFinite(eventTime) && age >= 0 && age <= maxAge;
  });
}

export function aggregateProjects(
  projects: Project[],
  referenceDate = new Date(),
  enrichedProjectIds: ReadonlySet<string> = new Set<string>(),
): DashboardStats {
  const costs = projects.flatMap((project) =>
    project.totalProjectCostMillionYen === null ? [] : [project.totalProjectCostMillionYen],
  );
  const eventTypes = (project: Project) => new Set(getProjectChangeEvents(project).map((event) => event.type));
  const levels = projects.map((project) => getMonitoringLevel(project, enrichedProjectIds.has(project.id)));
  return {
    projectCount: projects.length,
    inventoryCount: levels.filter((level) => level === 'inventory').length,
    monitoredCount: levels.filter((level) => level !== 'inventory').length,
    historyCount: levels.filter((level) => level === 'history' || level === 'enriched').length,
    enrichedCount: levels.filter((level) => level === 'enriched').length,
    knownCostCount: costs.length,
    totalKnownCostMillionYen: costs.reduce((sum, value) => sum + value, 0),
    statusCounts: projects.reduce<Record<string, number>>((acc, project) => {
      acc[project.status] = (acc[project.status] ?? 0) + 1;
      return acc;
    }, {}),
    categoryCounts: projects.reduce<Record<string, number>>((acc, project) => {
      acc[project.categoryLabel] = (acc[project.categoryLabel] ?? 0) + 1;
      return acc;
    }, {}),
    costIncreaseProjectCount: projects.filter((project) => eventTypes(project).has('cost_increase')).length,
    delayedProjectCount: projects.filter((project) => eventTypes(project).has('delayed')).length,
    updatedLast365Days: projects.filter((project) => changedWithinDays(project, referenceDate, 365)).length,
  };
}

export function countChangeEvents(projects: Project[], type: ChangeType): number {
  return getAllChangeEvents(projects).filter((event) => event.type === type).length;
}

export function formatMillionYen(value: number | null): string {
  if (value === null) return '公表値未確認';
  if (value >= 100) return `${(value / 100).toLocaleString('ja-JP', { maximumFractionDigits: 1 })}億円`;
  return `${value.toLocaleString('ja-JP')}百万円`;
}

export function formatFiscalYear(year: number): string {
  if (year >= 2019) return `R${year - 2018}`;
  if (year >= 1989) return `H${year - 1988}`;
  return `${year}`;
}

export function getProjectIdFromPath(pathname: string): string | null {
  const match = pathname.match(/\/projects\/([^/]+)\/?$/);
  return match?.[1] ? decodeURIComponent(match[1]) : null;
}
