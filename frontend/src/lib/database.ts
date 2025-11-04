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
  // 1. Use the environment variable with the local URL as a fallback.
  // NOTE: I've added '/api' back to the fallback, assuming it's part of the path.
  const apiUrl = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000/api'; 

  try {
    // 2. Fetch the spots data from the API endpoint
    const response = await fetch(`${apiUrl}/spots.php?limit=5000`);

    if (!response.ok) {
      console.warn(`Could not load fishing spots data from API: ${response.status} ${response.statusText}`);
      return [];
    }

    // 3. PROCESS THE JSON DATA (The critical change is here)
    const data = await response.json();
    
    // Check 1: Handle API responses where the array is wrapped in a 'data' property
    if (data && Array.isArray(data.data)) {
        console.log('API data successfully unwrapped from "data" property.');
        return data.data; 
    }
    
    // Check 2: Fallback to assume the top level is the array
    if (Array.isArray(data)) {
        console.log('API data is an array at the top level.');
        return data; 
    }
    
    // Final Fail: If the format is wrong, return an empty array and log the failure
    console.error('API response format is incorrect. Could not find array in response.');
    return [];

  } catch (error) {
    console.error('An error occurred during API fetch or JSON parsing in getSpots:', error);
    // Always return an array on error to prevent the build crash
    return [];
  }
}

/**
 * Get spots filtered by county (This function now uses the corrected getSpots())
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
