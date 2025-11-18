/**
 * County Listing Component
 * Displays top counties from user's state with spot counts
 * Uses IP geolocation to detect state
 */

import { useState, useEffect } from 'preact/hooks';
import { getIpGeolocationData, stateNameLookup, stateSlugLookup } from '../lib/ipGeolocation';

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
        // Get geolocation data (uses shared utility with caching)
        const geoData = await getIpGeolocationData();
        
        if (!geoData || !geoData.region_code) {
          setIsLoading(false);
          return; // Don't show section if we can't detect state
        }

        const detectedState = geoData.region_code;
        const stateName = stateNameLookup[detectedState] || detectedState;
        const stateSlug = stateSlugLookup[detectedState] || detectedState.toLowerCase();

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
