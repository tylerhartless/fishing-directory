import { useState, useEffect } from 'preact/hooks';

const CACHE_KEY = 'ip_geolocation_data';
const CACHE_EXPIRY = 60 * 60 * 1000; // 1 hour

export default function DynamicSubtitle() {
  const [locationText, setLocationText] = useState('Complete directory');

  useEffect(() => {
    // Only run in browser
    if (typeof window === 'undefined') {
      return;
    }

    // Use IP geolocation - no permission required, completely silent
    // Using ipapi.co free tier (1,000 requests/day, no API key needed)
    const detectLocation = async () => {
      try {
        // Check cache first
        const cached = localStorage.getItem(CACHE_KEY);
        if (cached) {
          try {
            const cachedData = JSON.parse(cached);
            const now = Date.now();
            if (now - cachedData.timestamp < CACHE_EXPIRY && cachedData.region) {
              setLocationText(`${cachedData.region} directory`);
              return;
            }
          } catch (e) {
            // Invalid cache, continue to fetch
          }
        }

        // Fetch fresh data
        const response = await fetch('https://ipapi.co/json/');

        if (response.ok) {
          const data = await response.json();

          // Cache the data
          localStorage.setItem(CACHE_KEY, JSON.stringify({
            ...data,
            timestamp: Date.now()
          }));

          // Get state name from response
          if (data.region) {
            setLocationText(`${data.region} directory`);
          } else if (data.country_name && data.country_name !== 'United States') {
            // If outside US, show country
            setLocationText(`${data.country_name} directory`);
          }
        }
      } catch (error) {
        // Silently fail - keep default "Complete directory"
        console.log('Could not detect location via IP');
      }
    };

    detectLocation();
  }, []);

  return (
    <p class="subtitle">
      Public fishing spots near you - {locationText}
    </p>
  );
}
