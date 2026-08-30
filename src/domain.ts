import type { Project } from './types';

export interface ProjectFilters {
  query: string;
  category: string;
  operator: string;
  municipality: string;
  status: string;
}

export interface DashboardStats {
  projectCount: number;
  knownCostCount: number;
  totalKnownCostMillionYen: number;
  statusCounts: Record<string, number>;
  categoryCounts: Record<string, number>;
}

export function filterProjects(projects: Project[], filters: ProjectFilters): Project[] {
  const q = filters.query.trim().toLocaleLowerCase('ja-JP');
  return projects.filter((project) => {
    const haystack = [project.name, project.summary, ...project.municipalities]
      .join(' ')
      .toLocaleLowerCase('ja-JP');
    return (
      (!q || haystack.includes(q)) &&
      (!filters.category || project.category === filters.category) &&
      (!filters.operator || project.operator === filters.operator) &&
      (!filters.municipality || project.municipalities.includes(filters.municipality)) &&
      (!filters.status || project.status === filters.status)
    );
  });
}

export function aggregateProjects(projects: Project[]): DashboardStats {
  const costs = projects.flatMap((project) =>
    project.totalProjectCostMillionYen === null ? [] : [project.totalProjectCostMillionYen],
  );
  return {
    projectCount: projects.length,
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
  };
}

export function formatMillionYen(value: number | null): string {
  if (value === null) return '公表値未確認';
  if (value >= 100) return `${(value / 100).toLocaleString('ja-JP', { maximumFractionDigits: 1 })}億円`;
  return `${value.toLocaleString('ja-JP')}百万円`;
}

export function getProjectIdFromPath(pathname: string): string | null {
  const match = pathname.match(/\/projects\/([^/]+)\/?$/);
  return match?.[1] ? decodeURIComponent(match[1]) : null;
}
