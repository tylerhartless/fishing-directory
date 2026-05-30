import type { APIRoute } from 'astro';
import { getSpots } from '../lib/database';

export const GET: APIRoute = async () => {
  const spots = await getSpots();
  const serialized = spots.map(s => ({
    canonical_id: s.canonical_id,
    name: s.name,
    state: s.state,
    state_route: s.state_route,
    county: s.county,
    county_slug: s.county_slug,
    latitude: s.latitude,
    longitude: s.longitude,
    spot_type: s.spot_type,
    water_body_names: s.water_body_names,
    amenities: s.amenities,
  }));

  return new Response(JSON.stringify(serialized), {
    headers: { 'Content-Type': 'application/json' },
  });
};
