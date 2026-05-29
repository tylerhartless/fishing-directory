import type { APIRoute } from 'astro';
import { getSpots } from '../lib/database';

interface CountyAggregate {
  state: string;
  state_route: string;
  county: string;
  county_slug: string;
  spot_count: number;
  totalLat: number;
  totalLon: number;
}

export const GET: APIRoute = async () => {
  const spots = await getSpots();

  const byKey = new Map<string, CountyAggregate>();
  for (const spot of spots) {
    const key = `${spot.state}|${spot.county_slug}`;
    if (!byKey.has(key)) {
      byKey.set(key, {
        state: spot.state,
        state_route: spot.state_route,
        county: spot.county,
        county_slug: spot.county_slug,
        spot_count: 0,
        totalLat: 0,
        totalLon: 0,
      });
    }
    const agg = byKey.get(key)!;
    agg.spot_count++;
    agg.totalLat += spot.latitude;
    agg.totalLon += spot.longitude;
  }

  const counties = Array.from(byKey.values()).map(c => ({
    state: c.state,
    state_route: c.state_route,
    county: c.county,
    county_slug: c.county_slug,
    spot_count: c.spot_count,
    lat: c.totalLat / c.spot_count,
    lon: c.totalLon / c.spot_count,
  }));

  return new Response(JSON.stringify(counties), {
    headers: { 'Content-Type': 'application/json' },
  });
};
