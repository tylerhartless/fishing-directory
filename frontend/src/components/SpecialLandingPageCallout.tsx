/**
 * Special Landing Page Callout Component
 * Displays callouts for state-specific special landing pages (e.g., fishing without license info)
 * Can be configured to show based on IP geolocation or always show for a specific state
 */

import { useState, useEffect } from 'preact/hooks';

interface LandingPage {
  icon: string;
  title: string;
  description: string;
  buttonText: string;
  slug: string;
}

interface SpecialLandingPageCalloutProps {
  /** If provided, always show this state's landing pages (no geolocation). Used on state pages. */
  forceState?: string;
  /** If true, only show if user is geolocated to the state. Used on homepage. */
  geolocateOnly?: boolean;
}

const stateNameLookup: Record<string, string> = {
  'TX': 'Texas',
  // Add more states as needed
};

const stateSlugLookup: Record<string, string> = {
  'TX': 'texas',
  // Add more states as needed
};

// Special landing pages per state
const stateLandingPages: Record<string, LandingPage[]> = {
  'TX': [
    {
      icon: '🎣',
      title: 'FISH WITHOUT A LICENSE',
      description: 'Texas state parks don\'t require fishing licenses. Find all state parks with fishing.',
      buttonText: 'View State Parks',
      slug: 'fishing-without-license'
    }
    // Add more Texas landing pages here as needed
  ]
  // Add more states here as needed
};

export default function SpecialLandingPageCallout({ forceState, geolocateOnly = false }: SpecialLandingPageCalloutProps) {
  const [detectedState, setDetectedState] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(!forceState); // Skip loading if forceState is provided

  useEffect(() => {
    // If forceState is provided, use it immediately
    if (forceState) {
      setDetectedState(forceState);
      setIsLoading(false);
      return;
    }

    // Only run geolocation in browser and if geolocateOnly is true
    if (typeof window === 'undefined' || !geolocateOnly) {
      setIsLoading(false);
      return;
    }

    const detectState = async () => {
      try {
        const response = await fetch('https://ipapi.co/json/');
        if (response.ok) {
          const data = await response.json();
          const state = data.region_code;
          // Only show if detected state is Texas (or in future, any state with landing pages)
          if (state === 'TX') {
            setDetectedState(state);
          } else {
            setDetectedState(null);
          }
        } else {
          setDetectedState(null);
        }
      } catch (error) {
        console.log('Could not detect state for landing page callout');
        // Don't show callout if detection fails
        setDetectedState(null);
      } finally {
        setIsLoading(false);
      }
    };

    detectState();
  }, [forceState, geolocateOnly]);

  // Don't show anything while loading
  if (isLoading) {
    return null;
  }

  // Don't show if no state detected or state has no landing pages
  if (!detectedState || !stateLandingPages[detectedState]) {
    return null;
  }

  const landingPages = stateLandingPages[detectedState];
  const stateName = stateNameLookup[detectedState] || detectedState;
  const stateSlug = stateSlugLookup[detectedState] || detectedState.toLowerCase();

  return (
    <>
      {landingPages.map((page, index) => (
        <div key={index} class="retro-info-box no-license-callout text-center">
          <h3 class="mb-0">
            {page.title}
          </h3>
          <p class="font-body-text font-size-md line-height-normal mb-md" style="margin-top: 0.15rem;">
            {page.description}
          </p>
          <a href={`/${stateSlug}/${page.slug}`} class="retro-btn retro-btn-search no-underline display-inline-block">
            {page.buttonText}
          </a>
        </div>
      ))}
    </>
  );
}
