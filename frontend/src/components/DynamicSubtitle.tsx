import { useState, useEffect } from 'preact/hooks';

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
        const response = await fetch('https://ipapi.co/json/');

        if (response.ok) {
          const data = await response.json();

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
