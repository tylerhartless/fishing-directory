/**
 * Database utilities for fetching fishing spot data
 *
 * In production, you would connect to MySQL here.
 * For static generation, you can also pre-export data to JSON.
 */

export interface FishingSpot {
  id: number;
  name: string;
  slug: string;
  latitude: number;
  longitude: number;
  county: string;
  water_body_name?: string;
  spot_type: 'boat_ramp' | 'bank_fishing' | 'pier' | 'wade_fishing' | 'kayak_launch' | 'fishing_pier' | 'state_park';
  description?: string;
  amenities?: {
    parking?: boolean;
    restrooms?: boolean;
    lighting?: boolean;
    fish_cleaning?: boolean;
    boat_trailer_parking?: boolean;
    camping?: boolean;
    fishing_pier?: boolean;
  };
  data_source: string;
  is_verified: boolean;
  meta_title?: string;
  meta_description?: string;
  created_at?: string;
  updated_at?: string;
}

/**
 * Fetch all fishing spots from database or JSON export
 *
 * For Astro static generation:
 * 1. Export your MySQL data to JSON using a script
 * 2. Place in /public/data/fishing-spots.json
 * 3. Load during build time
 */
export async function getSpots(): Promise<FishingSpot[]> {
  // Option 1: Load from static JSON export (for build time)
  // You would generate this file with a Python script
  const response = await fetch('/data/fishing-spots.json');

  if (!response.ok) {
    console.warn('Could not load fishing spots data');
    return [];
  }

  return await response.json();
}

/**
 * Get spots filtered by county
 */
export async function getSpotsByCounty(county: string): Promise<FishingSpot[]> {
  const allSpots = await getSpots();
  return allSpots.filter(spot =>
    spot.county.toLowerCase() === county.toLowerCase() && spot.is_active !== false
  );
}

/**
 * Get a single spot by slug
 */
export async function getSpotBySlug(slug: string): Promise<FishingSpot | null> {
  const allSpots = await getSpots();
  return allSpots.find(spot => spot.slug === slug) || null;
}

/**
 * Get unique list of counties
 */
export async function getCounties(): Promise<string[]> {
  const allSpots = await getSpots();
  const counties = new Set(allSpots.map(spot => spot.county));
  return Array.from(counties).sort();
}

/**
 * Generate Mapbox static map URL
 */
export function generateMapUrl(lat: number, lon: number, zoom: number = 13): string {
  const token = import.meta.env.PUBLIC_MAPBOX_TOKEN || 'YOUR_TOKEN';
  const marker = `pin-s+285A98(${lon},${lat})`;
  const size = '600x400@2x';

  return `https://api.mapbox.com/styles/v1/mapbox/outdoors-v12/static/${marker}/${lon},${lat},${zoom},0/${size}?access_token=${token}`;
}
