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
import {
  mergePhase27AnnualBudget,
  mergePhase27Enrichment,
  mergePhase27GeoJson,
  mergePhase27Projects,
  type Phase27Seed,
} from './phase27-data';
import type { ProjectCollection } from './types';
import type { EnrichmentCollection } from './enrichment-types';
import type { AnnualBudgetCollection } from './annual-budget-types';

const nativeFetch = window.fetch.bind(window);
const base = import.meta.env.BASE_URL;
let seedsPromise: Promise<{ phase26: Phase26Seed; phase27: Phase27Seed }> | null = null;

function loadSeeds() {
  seedsPromise ??= Promise.all([
    nativeFetch(`${base}data/phase26-inventory.json`),
    nativeFetch(`${base}data/phase26-reconciliation.json`),
    nativeFetch(`${base}data/phase27-inventory.json`),
  ]).then(async ([seedResponse, reconciliationResponse, phase27Response]) => {
    if (!seedResponse.ok) throw new Error(`Phase 2.6 seed HTTP ${seedResponse.status}`);
    if (!reconciliationResponse.ok) throw new Error(`Phase 2.6 reconciliation HTTP ${reconciliationResponse.status}`);
    if (!phase27Response.ok) throw new Error(`Phase 2.7 seed HTTP ${phase27Response.status}`);
    const seed = await seedResponse.json() as Phase26Seed;
    const reconciliation = await reconciliationResponse.json() as Phase26Reconciliation;
    const phase27 = await phase27Response.json() as Phase27Seed;
    return { phase26: reconcilePhase26Seed(seed, reconciliation), phase27 };
  });
  return seedsPromise;
}

function jsonResponse(value: unknown) {
  return new Response(JSON.stringify(value), { status: 200, headers: { 'content-type': 'application/json; charset=utf-8' } });
}

window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
  const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url;
  const pathname = new URL(url, window.location.href).pathname;
  const phaseDataTarget = pathname.endsWith('/data/phase26-inventory.json')
    || pathname.endsWith('/data/phase26-reconciliation.json')
    || pathname.endsWith('/data/phase27-inventory.json');
  if (phaseDataTarget) return nativeFetch(input, init);
  const mergers: Record<string, (baseValue: unknown, phase26: Phase26Seed, phase27: Phase27Seed) => unknown> = {
    '/data/projects.json': (value, phase26, phase27) => mergePhase27Projects(mergeProjects(value as ProjectCollection, phase26), phase27),
    '/data/projects.geojson': (value, phase26, phase27) => mergePhase27GeoJson(mergeGeoJson(value as FeatureCollection, phase26), phase27),
    '/data/enrichment.json': (value, phase26, phase27) => mergePhase27Enrichment(mergeEnrichment(value as EnrichmentCollection, phase26), phase27),
    '/data/annual-budget-r5-r8.json': (value, phase26, phase27) => mergePhase27AnnualBudget(mergeAnnualBudget(value as AnnualBudgetCollection, phase26), phase27),
  };
  const entry = Object.entries(mergers).find(([suffix]) => pathname.endsWith(suffix));
  if (!entry) return nativeFetch(input, init);
  const [baseResponse, seeds] = await Promise.all([nativeFetch(input, init), loadSeeds()]);
  if (!baseResponse.ok) return baseResponse;
  const value = await baseResponse.json() as unknown;
  return jsonResponse(entry[1](value, seeds.phase26, seeds.phase27));
};
