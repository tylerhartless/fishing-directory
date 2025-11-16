/**
 * County Listing Component
 * Displays top counties from user's state with spot counts
 * Uses IP geolocation to detect state
 */

import { useState, useEffect } from 'preact/hooks';

interface County {
  name: string;
  slug: string;
  state: string;
  spot_count: number;
}

interface LocationData {
  state: string;
  stateName: string;
  stateSlug: string;
}

const stateNameLookup: Record<string, string> = {
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

const stateSlugLookup: Record<string, string> = {
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

export default function CountyListing() {
  const [counties, setCounties] = useState<County[]>([]);
  const [location, setLocation] = useState<LocationData>({
    state: 'TX',
    stateName: 'Texas',
    stateSlug: 'texas'
  });
  const [isLoading, setIsLoading] = useState(true);

  // API URL
  const API_URL = typeof window !== 'undefined'
    ? (window.location.hostname === 'localhost' || window.location.hostname.startsWith('100.') || window.location.hostname.startsWith('127.') || window.location.port === '4321'
        ? `http://${window.location.hostname}:8000`
        : `${window.location.protocol}//${window.location.host}/api`)
    : '';

  useEffect(() => {
    // Only run in browser
    if (typeof window === 'undefined') {
      return;
    }

    const loadCounties = async () => {
      try {
        // Step 1: Detect user's state via IP geolocation
        let detectedState = 'TX'; // Default to Texas
        try {
          const geoResponse = await fetch('https://ipapi.co/json/');
          if (geoResponse.ok) {
            const geoData = await geoResponse.json();
            if (geoData.region_code) {
              detectedState = geoData.region_code;
            }
          }
        } catch (error) {
          console.log('Could not detect location via IP, defaulting to Texas');
        }

        // Step 2: Get state name and slug
        const stateName = stateNameLookup[detectedState] || 'Texas';
        const stateSlug = stateSlugLookup[detectedState] || 'texas';

        setLocation({
          state: detectedState,
          stateName,
          stateSlug
        });

        // Step 3: Fetch counties for the detected state
        const countyResponse = await fetch(`${API_URL}/county-stats.php?state=${detectedState}&limit=6`);
        if (countyResponse.ok) {
          const countyData = await countyResponse.json();
          if (countyData.success && countyData.counties) {
            setCounties(countyData.counties);
          }
        }
      } catch (error) {
        console.error('Error loading counties:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadCounties();
  }, [API_URL]);

  if (isLoading) {
    return (
      <div class="county-listing-section">
        <p class="loading-text">Loading nearby counties...</p>
      </div>
    );
  }

  if (counties.length === 0) {
    return null; // Don't show section if no counties available
  }

  return (
    <div class="retro-section">
      <h2>TOP {location.stateName.toUpperCase()} COUNTIES</h2>

      <div class="flex flex-column gap-md mb-xl">
        {counties.map((county) => (
          <a
            key={county.slug}
            href={`/${location.stateSlug}/${county.slug}`}
            class="county-item"
          >
            <span>{county.name} County</span>
            <span class="county-dots"></span>
            <span class="retro-badge">{county.spot_count}</span>
          </a>
        ))}
      </div>

      <div class="flex flex-column gap-lg mt-lg">
        <a href={`/${location.stateSlug}`} class="retro-btn retro-btn-search text-center no-underline">
          See All {location.stateName} Counties
        </a>
        <a href="/states" class="retro-btn county-browse-btn text-center no-underline">
          Browse Other States
        </a>
      </div>
    </div>
  );
}
