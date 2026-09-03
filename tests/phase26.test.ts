import { describe, expect, it } from 'vitest';
import baseProjects from '../public/data/projects.json';
import baseEnrichment from '../public/data/enrichment.json';
import baseBudget from '../public/data/annual-budget-r5-r8.json';
import rawSeed from '../public/data/phase26-inventory.json';
import { filterProjects } from '../src/domain';
import {
  mergeAnnualBudget,
  mergeEnrichment,
  mergeProjects,
  phase26Features,
  phase26Projects,
  type Phase26Seed,
} from '../src/phase26-data';
import type { ProjectCollection } from '../src/types';
import type { EnrichmentCollection } from '../src/enrichment-types';
import type { AnnualBudgetCollection } from '../src/annual-budget-types';

const seed = rawSeed as unknown as Phase26Seed;
const projects = mergeProjects(baseProjects as unknown as ProjectCollection, seed);

describe('Phase 2.6 comprehensive inventory', () => {
  it('expands the 50-project baseline past the 100-project benchmark without duplicate ids', () => {
    expect(baseProjects.projects).toHaveLength(50);
    expect(phase26Projects(seed)).toHaveLength(59);
    expect(projects.projects).toHaveLength(109);
    expect(new Set(projects.projects.map((project) => project.id)).size).toBe(109);
  });

  it('keeps the existing filter system usable at the expanded scale', () => {
    const roads = filterProjects(projects.projects, {
      query: '', category: 'road', operator: '', municipality: '', status: '', depth: '', alert: '',
    }, new Set());
    const imabari = filterProjects(projects.projects, {
      query: '今治', category: '', operator: '', municipality: '今治市', status: '', depth: '', alert: '',
    }, new Set());
    expect(roads.length).toBeGreaterThanOrEqual(60);
    expect(imabari.length).toBeGreaterThan(0);
  });

  it('generates one approximate geometry per new project without pretending it is official alignment', () => {
    const features = phase26Features(seed);
    expect(features).toHaveLength(59);
    expect(features.every((feature) => feature.geometry.type === 'Point')).toBe(true);
    expect(features.every((feature) => feature.properties?.locationAccuracy === 'approximate')).toBe(true);
  });

  it('synchronizes enrichment and annual-budget audit sets for every new canonical project', () => {
    const enrichment = mergeEnrichment(baseEnrichment as unknown as EnrichmentCollection, seed);
    const budget = mergeAnnualBudget(baseBudget as unknown as AnnualBudgetCollection, seed);
    expect(enrichment.records).toHaveLength(109);
    expect(budget.records).toHaveLength(109);
    const newIds = new Set(phase26Projects(seed).map((project) => project.id));
    expect(enrichment.records.filter((record) => newIds.has(record.projectId)).every((record) =>
      record.annualBudgetHistory.length === 0 && record.cumulativeInvestmentHistory.length === 0 && record.benefitCostHistory.length === 0 && record.documentedReasons.length === 0,
    )).toBe(true);
    expect(budget.records.filter((record) => newIds.has(record.projectId)).every((record) =>
      record.auditStatus === 'SOURCE_NOT_FOUND' && record.observations.length === 0,
    )).toBe(true);
  });

  it('keeps unknown financial values unknown instead of manufacturing data for coverage', () => {
    const road = phase26Projects(seed).find((project) => project.id === 'r494-omogo');
    const sabo = phase26Projects(seed).find((project) => project.id === 'higashimachi-river-sabo');
    expect(road?.totalProjectCostMillionYen).toBeNull();
    expect(road?.currentFiscalYearBudgetMillionYen).toBeNull();
    expect(sabo?.totalProjectCostMillionYen).toBe(340);
    expect(sabo?.benefitCostRatio).toBe(71.85);
  });
});
