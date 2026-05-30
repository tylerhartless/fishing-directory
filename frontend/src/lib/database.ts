/**
 * Loads canonical fishing spots from the pipeline-produced JSON files at
 * <repo>/data/publish/<state>/spots.json. State code is the directory name.
 * Drop new state files into that directory; no other wiring required.
 */

import * as fs from 'node:fs';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

// Resolve <repo>/data/publish from this source file (frontend/src/lib/database.ts → ../../../data/publish)
const DATA_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../../data/publish');

export const SPOT_TYPES = [
  'boat_ramp',
  'pier',
  'state_park',
  'lake',
  'public_water',
  'river_access',
  'community_park',
] as const;

export type SpotType = typeof SPOT_TYPES[number];

export interface PipelineSource {
  source_id: string;
  record_id: string;
  contributed_fields: string[] | null;
  source_evidence?: {
    record_id?: string;
    method?: string;
    host_polygon_id?: string;
    host_polygon_name?: string;
    host_polygon_canonical_type?: string;
    previous_name?: string | null;
  } | null;
}

export interface PointOfInterest {
  spot_type: string;
  name: string;
  latitude: number;
  longitude: number;
  water_body_name?: string | null;
  address?: string | null;
  city?: string | null;
  zip_code?: string | null;
  source_id?: string | null;
}

/**
 * One canonical fishing spot. Shape mirrors `publish/<state>/spots.json` with
 * the addition of derived fields (canonical_id, county_slug, state_route)
 * computed at load time.
 */
export interface FishingSpot {
  // Identity
  canonical_id: string;     // e.g. "tx-anderson-trinity-river-anderson001"; same string used in URLs and catch_reports
  state: string;            // 2-letter uppercase, e.g. "TX"
  state_route: string;      // URL segment, e.g. "texas"
  county: string;           // e.g. "Anderson"
  county_slug: string;      // e.g. "anderson"
  name: string;

  // Geo
  latitude: number;
  longitude: number;

  // Categorization
  spot_type: SpotType;
  water_body_names: string[];
  acres: number | null;

  // Address (often null for rural records)
  address: string | null;
  city: string | null;
  zip_code: string | null;

  // Content
  description: string;
  meta_title: string;
  meta_description: string;
  amenities: Record<string, boolean>;
  species: string[];

  // Embedded children (rendered only on parent detail page; dropped from flat array)
  points_of_interest: PointOfInterest[];

  // Provenance
  sources: PipelineSource[];

  // Flags & metadata
  is_verified: boolean;
  is_active: boolean;
  needs_review?: boolean;
  review_reason?: string | null;
  _synthetic_water_body?: boolean;
  _describe_status?: string | null;
  validation_flags?: string[];

  // Admin-only — don't render publicly
  descriptions?: string[];
}

const STATE_ROUTE_BY_CODE: Record<string, string> = {
  AL: 'alabama', AK: 'alaska', AZ: 'arizona', AR: 'arkansas', CA: 'california',
  CO: 'colorado', CT: 'connecticut', DE: 'delaware', FL: 'florida', GA: 'georgia',
  HI: 'hawaii', ID: 'idaho', IL: 'illinois', IN: 'indiana', IA: 'iowa',
  KS: 'kansas', KY: 'kentucky', LA: 'louisiana', ME: 'maine', MD: 'maryland',
  MA: 'massachusetts', MI: 'michigan', MN: 'minnesota', MS: 'mississippi', MO: 'missouri',
  MT: 'montana', NE: 'nebraska', NV: 'nevada', NH: 'new-hampshire', NJ: 'new-jersey',
  NM: 'new-mexico', NY: 'new-york', NC: 'north-carolina', ND: 'north-dakota', OH: 'ohio',
  OK: 'oklahoma', OR: 'oregon', PA: 'pennsylvania', RI: 'rhode-island', SC: 'south-carolina',
  SD: 'south-dakota', TN: 'tennessee', TX: 'texas', UT: 'utah', VT: 'vermont',
  VA: 'virginia', WA: 'washington', WV: 'west-virginia', WI: 'wisconsin', WY: 'wyoming',
};

export function stateRouteFromCode(code: string): string {
  return STATE_ROUTE_BY_CODE[code?.toUpperCase()] || code?.toLowerCase() || '';
}

export function slugify(input: string): string {
  return input
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function recordIdTail(record_id: string): string {
  // sources[0].record_id is "tx_tpwd_boat_ramps:4357" — take the part after the last colon
  const tail = record_id.includes(':') ? record_id.split(':').pop()! : record_id;
  return slugify(tail);
}

function deriveCanonicalId(state: string, county: string, name: string, sources: PipelineSource[]): string | null {
  const tail = sources?.[0]?.record_id ? recordIdTail(sources[0].record_id) : null;
  if (!tail) return null;
  const parts = [state.toLowerCase(), slugify(county), slugify(name), tail].filter(Boolean);
  if (parts.length < 4) return null;
  return parts.join('-');
}

interface RawSpot {
  name: string;
  latitude: number;
  longitude: number;
  state: string;
  county: string;
  spot_type: string;
  address?: string | null;
  city?: string | null;
  zip_code?: string | null;
  amenities?: Record<string, boolean>;
  description?: string;
  meta_title?: string;
  meta_description?: string;
  water_body_names?: string[];
  species?: string[];
  points_of_interest?: PointOfInterest[];
  sources?: PipelineSource[];
  descriptions?: string[];
  acres?: number | null;
  is_verified?: boolean;
  is_active?: boolean;
  needs_review?: boolean;
  review_reason?: string | null;
  _synthetic_water_body?: boolean;
  _describe_status?: string | null;
  validation_flags?: string[];
}

function normalize(raw: RawSpot): FishingSpot | null {
  if (!raw?.name || !raw?.county || !raw?.state || !raw?.sources?.length) return null;
  const canonical_id = deriveCanonicalId(raw.state, raw.county, raw.name, raw.sources);
  if (!canonical_id) return null;

  return {
    canonical_id,
    state: raw.state.toUpperCase(),
    state_route: stateRouteFromCode(raw.state),
    county: raw.county,
    county_slug: slugify(raw.county),
    name: raw.name,
    latitude: Number(raw.latitude),
    longitude: Number(raw.longitude),
    spot_type: raw.spot_type as SpotType,
    water_body_names: raw.water_body_names ?? [],
    acres: raw.acres ?? null,
    address: raw.address ?? null,
    city: raw.city ?? null,
    zip_code: raw.zip_code ?? null,
    description: raw.description ?? '',
    meta_title: raw.meta_title ?? '',
    meta_description: raw.meta_description ?? '',
    amenities: raw.amenities ?? {},
    species: raw.species ?? [],
    points_of_interest: raw.points_of_interest ?? [],
    sources: raw.sources,
    is_verified: raw.is_verified ?? false,
    is_active: raw.is_active ?? true,
    needs_review: raw.needs_review,
    review_reason: raw.review_reason ?? null,
    _synthetic_water_body: raw._synthetic_water_body,
    _describe_status: raw._describe_status ?? null,
    validation_flags: raw.validation_flags,
    descriptions: raw.descriptions,
  };
}

let cachedSpots: FishingSpot[] | null = null;

/**
 * Load every spot from every state present at data/publish/<state>/spots.json.
 * Returns [] when the data directory is missing or empty so the build can run
 * before the JSON files are dropped in.
 */
export async function getSpots(): Promise<FishingSpot[]> {
  if (cachedSpots) return cachedSpots;

  if (!fs.existsSync(DATA_DIR)) {
    cachedSpots = [];
    return cachedSpots;
  }

  const stateDirs = fs.readdirSync(DATA_DIR, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => d.name);

  const all: FishingSpot[] = [];
  const seen = new Set<string>();

  for (const stateDir of stateDirs) {
    const jsonPath = path.join(DATA_DIR, stateDir, 'spots.json');
    if (!fs.existsSync(jsonPath)) continue;

    let raw: RawSpot[];
    try {
      raw = JSON.parse(fs.readFileSync(jsonPath, 'utf-8')) as RawSpot[];
    } catch (err) {
      console.error(`[getSpots] Failed to parse ${jsonPath}:`, err);
      continue;
    }

    if (!Array.isArray(raw)) continue;

    for (const r of raw) {
      const spot = normalize(r);
      if (!spot) continue;
      if (seen.has(spot.canonical_id)) {
        console.warn(`[getSpots] Duplicate canonical_id collision: ${spot.canonical_id}`);
        continue;
      }
      seen.add(spot.canonical_id);
      all.push(spot);
    }
  }

  cachedSpots = all;
  return cachedSpots;
}

export async function getSpotsByCounty(stateCode: string, county: string): Promise<FishingSpot[]> {
  const all = await getSpots();
  const targetState = stateCode.toUpperCase();
  const targetCounty = county.toLowerCase();
  return all.filter(s => s.state === targetState && s.county_slug === targetCounty);
}

export async function getSpotByCanonicalId(canonical_id: string): Promise<FishingSpot | null> {
  const all = await getSpots();
  return all.find(s => s.canonical_id === canonical_id) ?? null;
}

export async function getCountiesByState(stateCode: string): Promise<string[]> {
  const all = await getSpots();
  const target = stateCode.toUpperCase();
  return Array.from(new Set(all.filter(s => s.state === target).map(s => s.county))).sort();
}

export function generateMapUrl(lat: number, lon: number, zoom = 13): string {
  const token = import.meta.env.PUBLIC_MAPBOX_TOKEN || 'YOUR_TOKEN';
  const marker = `pin-s+285A98(${lon},${lat})`;
  return `https://api.mapbox.com/styles/v1/mapbox/outdoors-v12/static/${marker}/${lon},${lat},${zoom},0/600x400@2x?access_token=${token}`;
}

export function formatWaterBodies(names: string[]): string {
  if (!names || names.length === 0) return '';
  if (names.length === 1) return names[0];
  if (names.length === 2) return `${names[0]} and ${names[1]}`;
  return names.slice(0, -1).join(', ') + ', and ' + names[names.length - 1];
}
