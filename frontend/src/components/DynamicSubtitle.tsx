import { useState, useEffect } from 'preact/hooks';
import { getIpGeolocationData } from '../lib/ipGeolocation';

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
      const data = await getIpGeolocationData();
      
      if (data) {
        if (data.region) {
          setLocationText(`${data.region} directory`);
        } else if (data.country_name && data.country_name !== 'United States') {
          // If outside US, show country
          setLocationText(`${data.country_name} directory`);
        }
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
