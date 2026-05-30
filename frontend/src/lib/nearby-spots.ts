/**
 * Build-time computation of nearby fishing spots for a target spot.
 * Uses haversine distance with a bounding-box prefilter so it scales to
 * thousands of spots without quadratic blowup.
 */

import type { FishingSpot } from './database';

export interface NearbyEntry {
  canonical_id: string;
  name: string;
  state_route: string;
  county_slug: string;
  spot_type: string;
  /** Distance from target spot in miles */
  distance: number;
}

const EARTH_RADIUS_MILES = 3958.8;
const MILES_PER_DEG_LAT = 69;

function toRadians(degrees: number): number {
  return (degrees * Math.PI) / 180;
}

function haversineMiles(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const dLat = toRadians(lat2 - lat1);
  const dLon = toRadians(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) * Math.sin(dLon / 2) ** 2;
  return 2 * EARTH_RADIUS_MILES * Math.asin(Math.sqrt(a));
}

export function computeNearby(
  target: FishingSpot,
  pool: FishingSpot[],
  limit = 6,
  maxMiles = 50,
): NearbyEntry[] {
  const latRange = maxMiles / MILES_PER_DEG_LAT;
  const lonRange = maxMiles / (MILES_PER_DEG_LAT * Math.cos(toRadians(target.latitude)));

  const candidates: { spot: FishingSpot; distance: number }[] = [];
  for (const s of pool) {
    if (s.canonical_id === target.canonical_id) continue;
    if (Math.abs(s.latitude - target.latitude) > latRange) continue;
    if (Math.abs(s.longitude - target.longitude) > lonRange) continue;
    const d = haversineMiles(target.latitude, target.longitude, s.latitude, s.longitude);
    if (d <= maxMiles) candidates.push({ spot: s, distance: d });
  }

  return candidates
    .sort((a, b) => a.distance - b.distance)
    .slice(0, limit)
    .map((e) => ({
      canonical_id: e.spot.canonical_id,
      name: e.spot.name,
      state_route: e.spot.state_route,
      county_slug: e.spot.county_slug,
      spot_type: e.spot.spot_type,
      distance: e.distance,
    }));
}
