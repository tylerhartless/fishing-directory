/**
 * County Navigation Link Component
 * Conditionally shows "Browse by County" link only if user's location is detected via IP
 */

import { useState, useEffect } from 'preact/hooks';

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

export default function CountyNavLink() {
  const [stateSlug, setStateSlug] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Only run in browser
    if (typeof window === 'undefined') {
      setIsLoading(false);
      return;
    }

    const detectState = async () => {
      try {
        const response = await fetch('https://ipapi.co/json/');
        if (response.ok) {
          const data = await response.json();
          const stateCode = data.region_code;
          
          // Only show link if we successfully detected a state and have a slug for it
          if (stateCode && stateSlugLookup[stateCode]) {
            setStateSlug(stateSlugLookup[stateCode]);
          } else {
            setStateSlug(null);
          }
        } else {
          setStateSlug(null);
        }
      } catch (error) {
        // Silently fail - don't show the link
        console.log('Could not detect location for county nav link');
        setStateSlug(null);
      } finally {
        setIsLoading(false);
      }
    };

    detectState();
  }, []);

  // Don't show anything while loading or if no state detected
  if (isLoading || !stateSlug) {
    return null;
  }

  return (
    <li>
      <a href={`/${stateSlug}`}>Browse by County</a>
    </li>
  );
}

