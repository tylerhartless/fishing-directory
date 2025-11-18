/**
 * IP Geolocation Utility
 * Handles fetching and caching IP geolocation data from ipapi.co
 * Shared across all components that need location data
 */

export interface IpGeolocationData {
  ip: string;
  city: string;
  region: string;
  region_code: string;
  country: string;
  country_name: string;
  postal: string;
  latitude: number;
  longitude: number;
  timezone: string;
  [key: string]: any; // Allow other fields from API
}

interface CachedGeolocationData extends IpGeolocationData {
  timestamp: number;
}

const CACHE_KEY = 'ip_geolocation_data';
const CACHE_EXPIRY = 60 * 60 * 1000; // 1 hour
const API_URL = 'https://ipapi.co/json/';

/**
 * Get cached geolocation data if valid
 */
function getCachedData(): IpGeolocationData | null {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    const cached = localStorage.getItem(CACHE_KEY);
    if (!cached) {
      return null;
    }

    const cachedData: CachedGeolocationData = JSON.parse(cached);
    const now = Date.now();

    if (now - cachedData.timestamp < CACHE_EXPIRY) {
      // Remove timestamp before returning
      const { timestamp, ...data } = cachedData;
      return data as IpGeolocationData;
    }
  } catch (e) {
    // Invalid cache, ignore
  }

  return null;
}

/**
 * Cache geolocation data
 */
function setCachedData(data: IpGeolocationData): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    const cachedData: CachedGeolocationData = {
      ...data,
      timestamp: Date.now()
    };
    localStorage.setItem(CACHE_KEY, JSON.stringify(cachedData));
  } catch (e) {
    // Storage quota exceeded or other error, ignore
    console.warn('Failed to cache geolocation data:', e);
  }
}

/**
 * Fetch fresh geolocation data from API
 */
async function fetchGeolocationData(): Promise<IpGeolocationData | null> {
  try {
    const response = await fetch(API_URL);
    if (!response.ok) {
      return null;
    }

    const data: IpGeolocationData = await response.json();
    setCachedData(data);
    return data;
  } catch (error) {
    console.log('Could not detect location via IP:', error);
    return null;
  }
}

/**
 * Get IP geolocation data (cached or fresh)
 * Returns cached data if available and valid, otherwise fetches fresh data
 */
export async function getIpGeolocationData(): Promise<IpGeolocationData | null> {
  // Check cache first
  const cached = getCachedData();
  if (cached) {
    return cached;
  }

  // Fetch fresh data
  return await fetchGeolocationData();
}

/**
 * State name lookup (used by CountyListing and other components)
 */
export const stateNameLookup: Record<string, string> = {
  'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
  'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
  'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
  'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
  'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
  'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
  'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
  'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
  'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
  'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
};

/**
 * State slug lookup (used by CountyListing and other components)
 */
export const stateSlugLookup: Record<string, string> = {
  'AL': 'alabama', 'AK': 'alaska', 'AZ': 'arizona', 'AR': 'arkansas', 'CA': 'california',
  'CO': 'colorado', 'CT': 'connecticut', 'DE': 'delaware', 'FL': 'florida', 'GA': 'georgia',
  'HI': 'hawaii', 'ID': 'idaho', 'IL': 'illinois', 'IN': 'indiana', 'IA': 'iowa',
  'KS': 'kansas', 'KY': 'kentucky', 'LA': 'louisiana', 'ME': 'maine', 'MD': 'maryland',
  'MA': 'massachusetts', 'MI': 'michigan', 'MN': 'minnesota', 'MS': 'mississippi', 'MO': 'missouri',
  'MT': 'montana', 'NE': 'nebraska', 'NV': 'nevada', 'NH': 'new-hampshire', 'NJ': 'new-jersey',
  'NM': 'new-mexico', 'NY': 'new-york', 'NC': 'north-carolina', 'ND': 'north-dakota', 'OH': 'ohio',
  'OK': 'oklahoma', 'OR': 'oregon', 'PA': 'pennsylvania', 'RI': 'rhode-island', 'SC': 'south-carolina',
  'SD': 'south-dakota', 'TN': 'tennessee', 'TX': 'texas', 'UT': 'utah', 'VT': 'vermont',
  'VA': 'virginia', 'WA': 'washington', 'WV': 'west-virginia', 'WI': 'wisconsin', 'WY': 'wyoming'
};

