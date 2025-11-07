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
  county: string; // DEPRECATED: Legacy single county field for backward compatibility
  counties?: string[]; // NEW: Array of counties for spots spanning multiple counties
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
  // Use the correct API URL (we assume you have it set as a secret)
  const apiUrl = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000/api';
  const fullUrl = `${apiUrl}/spots.php?limit=5000`;

  console.log(`[getSpots] Fetching from: ${fullUrl}`);

  try {
    const response = await fetch(fullUrl);

    if (!response.ok) {
      console.error(`[getSpots] API request failed: ${response.status} ${response.statusText}`);
      console.error(`[getSpots] URL was: ${fullUrl}`);
      return [];
    }

    const data = await response.json();

    // ⭐ THE DEFINITIVE FIX: Check for the array wrapped in the 'spots' key
    if (data && Array.isArray(data.spots)) {
        console.log(`[getSpots] Successfully loaded ${data.spots.length} spots from API`);
        return data.spots;
    }

    // Check 2: Fallback to assume the top level is the array (less likely, but safe)
    if (Array.isArray(data)) {
        console.log(`[getSpots] Successfully loaded ${data.length} spots from API (array format)`);
        return data;
    }

    // Final Fail: If the format is wrong, return an empty array
    console.error('[getSpots] API response format is incorrect. Could not find array in response.');
    console.error('[getSpots] Response data:', data);
    return [];

  } catch (error) {
    console.error('[getSpots] An error occurred during API fetch or JSON parsing:', error);
    return [];
  }
}

/**
 * Helper: Get all counties for a spot (supports both legacy and new format)
 */
export function getSpotCounties(spot: FishingSpot): string[] {
  // If spot has new counties array, use it
  if (spot.counties && spot.counties.length > 0) {
    return spot.counties;
  }

  // Otherwise, use legacy single county field
  // Skip 'Multiple Counties' placeholder as it's not a real county
  if (spot.county && spot.county !== 'Multiple Counties') {
    return [spot.county];
  }

  return [];
}

/**
 * Helper: Check if a spot is in a given county
 */
export function spotIsInCounty(spot: FishingSpot, countyName: string): boolean {
  const counties = getSpotCounties(spot);
  return counties.some(c => c.toLowerCase() === countyName.toLowerCase());
}

/**
 * Helper: Get display name for spot's county/counties
 */
export function getSpotCountyDisplay(spot: FishingSpot): string {
  const counties = getSpotCounties(spot);

  if (counties.length === 0) {
    return 'Multiple Counties';
  }

  if (counties.length === 1) {
    return counties[0];
  }

  // Multiple counties: "County A & County B" or "County A, County B, & County C"
  if (counties.length === 2) {
    return `${counties[0]} & ${counties[1]}`;
  }

  return counties.slice(0, -1).join(', ') + ', & ' + counties[counties.length - 1];
}

/**
 * Get spots filtered by county (supports both legacy and new multi-county format)
 */
export async function getSpotsByCounty(county: string): Promise<FishingSpot[]> {
  const allSpots = await getSpots();
  return allSpots.filter(spot =>
    spotIsInCounty(spot, county) && spot.is_active !== false
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
