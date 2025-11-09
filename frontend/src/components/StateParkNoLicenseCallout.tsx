/**
 * State Park No-License Callout Component
 * Displays callout for states where state parks don't require fishing licenses
 * Currently: Texas
 */

import { useState, useEffect } from 'preact/hooks';

interface StateNoLicenseInfo {
  state: string;
  stateName: string;
  stateSlug: string;
  hasNoLicenseRule: boolean;
}

const stateNameLookup: Record<string, string> = {
  'TX': 'Texas',
  // Add more states as they're confirmed to have no-license rules
};

const stateSlugLookup: Record<string, string> = {
  'TX': 'texas',
  // Add more states as needed
};

// States where state parks don't require fishing licenses
const noLicenseStates = ['TX']; // Add more states as confirmed

export default function StateParkNoLicenseCallout() {
  const [stateInfo, setStateInfo] = useState<StateNoLicenseInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Only run in browser
    if (typeof window === 'undefined') {
      return;
    }

    const detectState = async () => {
      try {
        const response = await fetch('https://ipapi.co/json/');
        if (response.ok) {
          const data = await response.json();
          const detectedState = data.region_code || 'TX';

          // Check if this state has the no-license rule
          if (noLicenseStates.includes(detectedState)) {
            setStateInfo({
              state: detectedState,
              stateName: stateNameLookup[detectedState] || 'Texas',
              stateSlug: stateSlugLookup[detectedState] || 'texas',
              hasNoLicenseRule: true
            });
          } else {
            setStateInfo({
              state: detectedState,
              stateName: '',
              stateSlug: '',
              hasNoLicenseRule: false
            });
          }
        }
      } catch (error) {
        console.log('Could not detect state for no-license callout');
        // Default to showing Texas callout if detection fails
        setStateInfo({
          state: 'TX',
          stateName: 'Texas',
          stateSlug: 'texas',
          hasNoLicenseRule: true
        });
      } finally {
        setIsLoading(false);
      }
    };

    detectState();
  }, []);

  // Don't show anything while loading
  if (isLoading) {
    return null;
  }

  // Don't show if state doesn't have no-license rule
  if (!stateInfo || !stateInfo.hasNoLicenseRule) {
    return null;
  }

  return (
    <div class="retro-info-box no-license-callout" style="display: flex; align-items: center; gap: 1.5rem;">
      <div style="font-size: 3rem; flex-shrink: 0;">🎣</div>
      <div style="flex: 1;">
        <h3 class="retro-heading-sm" style="margin-bottom: 0.75rem;">FISH WITHOUT A LICENSE</h3>
        <p style="margin: 0 0 1rem 0; font-family: var(--font-terminal); font-size: 1.25rem; line-height: 1.5;">
          {stateInfo.stateName} state parks don't require fishing licenses. Find all state parks with fishing.
        </p>
        <a href={`/${stateInfo.stateSlug}/fishing-without-license`} class="retro-btn retro-btn-search" style="display: inline-block; text-decoration: none;">
          → View State Parks
        </a>
      </div>
    </div>
  );
}
