import type { FeatureCollection } from 'geojson';
import {
  mergeAnnualBudget,
  mergeEnrichment,
  mergeGeoJson,
  mergeProjects,
  reconcilePhase26Seed,
  type Phase26Reconciliation,
  type Phase26Seed,
} from './phase26-data';
import type { ProjectCollection } from './types';
import type { EnrichmentCollection } from './enrichment-types';
import type { AnnualBudgetCollection } from './annual-budget-types';

const nativeFetch = window.fetch.bind(window);
const base = import.meta.env.BASE_URL;
let seedPromise: Promise<Phase26Seed> | null = null;

function loadSeed() {
  seedPromise ??= Promise.all([
    nativeFetch(`${base}data/phase26-inventory.json`),
    nativeFetch(`${base}data/phase26-reconciliation.json`),
  ]).then(async ([seedResponse, reconciliationResponse]) => {
    if (!seedResponse.ok) throw new Error(`Phase 2.6 seed HTTP ${seedResponse.status}`);
    if (!reconciliationResponse.ok) throw new Error(`Phase 2.6 reconciliation HTTP ${reconciliationResponse.status}`);
    const seed = await seedResponse.json() as Phase26Seed;
    const reconciliation = await reconciliationResponse.json() as Phase26Reconciliation;
    return reconcilePhase26Seed(seed, reconciliation);
  });
  return seedPromise;
}

function jsonResponse(value: unknown) {
  return new Response(JSON.stringify(value), { status: 200, headers: { 'content-type': 'application/json; charset=utf-8' } });
}

window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
  const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url;
  const pathname = new URL(url, window.location.href).pathname;
  const phase26DataTarget = pathname.endsWith('/data/phase26-inventory.json') || pathname.endsWith('/data/phase26-reconciliation.json');
  if (phase26DataTarget) return nativeFetch(input, init);
  const mergers: Record<string, (baseValue: unknown, seed: Phase26Seed) => unknown> = {
    '/data/projects.json': (value, seed) => mergeProjects(value as ProjectCollection, seed),
    '/data/projects.geojson': (value, seed) => mergeGeoJson(value as FeatureCollection, seed),
    '/data/enrichment.json': (value, seed) => mergeEnrichment(value as EnrichmentCollection, seed),
    '/data/annual-budget-r5-r8.json': (value, seed) => mergeAnnualBudget(value as AnnualBudgetCollection, seed),
  };
  const entry = Object.entries(mergers).find(([suffix]) => pathname.endsWith(suffix));
  if (!entry) return nativeFetch(input, init);
  const [baseResponse, seed] = await Promise.all([nativeFetch(input, init), loadSeed()]);
  if (!baseResponse.ok) return baseResponse;
  const value = await baseResponse.json() as unknown;
  return jsonResponse(entry[1](value, seed));
};
