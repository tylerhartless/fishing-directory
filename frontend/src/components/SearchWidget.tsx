import { useState } from 'preact/hooks';
import type { JSX } from 'preact';

interface SearchWidgetProps {
  nominatimEmail?: string;
}

export default function SearchWidget({ nominatimEmail = 'contact@wherecanifish.com' }: SearchWidgetProps) {
  const [isLoadingLocation, setIsLoadingLocation] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState<Array<{ name: string; county: string }>>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isSearching, setIsSearching] = useState(false);

  // Common Texas locations for autocomplete
  const commonLocations = [
    { name: 'Houston', county: 'Harris' },
    { name: 'Austin', county: 'Travis' },
    { name: 'Dallas', county: 'Dallas' },
    { name: 'Fort Worth', county: 'Tarrant' },
    { name: 'San Antonio', county: 'Bexar' },
  ];

  const handleUseLocation = () => {
    if ('geolocation' in navigator) {
      setIsLoadingLocation(true);

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          window.location.href = `/spots?lat=${latitude}&lon=${longitude}`;
        },
        (error) => {
          setIsLoadingLocation(false);
          let errorMessage = 'Unable to get your location. ';

          if (error.code === error.PERMISSION_DENIED) {
            errorMessage += 'Location permission was denied. Please enable it in your browser settings.';
          } else if (window.location.protocol === 'http:' && window.location.hostname !== 'localhost') {
            errorMessage += 'Location requires HTTPS when not on localhost. Please search manually or enable HTTPS.';
          } else {
            errorMessage += 'Please enter your location manually.';
          }

          alert(errorMessage);
        }
      );
    } else {
      alert('Geolocation is not supported by your browser');
    }
  };

  const handleSearchSubmit = async (e: JSX.TargetedEvent<HTMLFormElement, Event>) => {
    e.preventDefault();

    const query = searchQuery.trim();
    if (!query) return;

    setIsSearching(true);
    setShowSuggestions(false);

    // Make the query more specific for better results
    const specificQuery = query + ', texas';
    const apiUrl = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(specificQuery)}&format=json&limit=1&email=${nominatimEmail}`;

    try {
      const response = await fetch(apiUrl);

      if (!response.ok) {
        throw new Error(`API response not OK: ${response.status}`);
      }

      const data = await response.json();

      if (data && data.length > 0) {
        const lat = data[0].lat;
        const lon = data[0].lon;
        window.location.href = `/spots?lat=${lat}&lon=${lon}`;
      } else {
        // Fallback to text search
        window.location.href = `/spots?q=${encodeURIComponent(query)}`;
      }
    } catch (error) {
      console.error('Geocoding error:', error);
      // Fallback to text search
      window.location.href = `/spots?q=${encodeURIComponent(query)}`;
    }
  };

  const handleInputChange = (e: JSX.TargetedEvent<HTMLInputElement, Event>) => {
    const value = (e.target as HTMLInputElement).value;
    setSearchQuery(value);

    if (value.length < 2) {
      setShowSuggestions(false);
      return;
    }

    const matches = commonLocations.filter(loc =>
      loc.name.toLowerCase().includes(value.toLowerCase()) ||
      loc.county.toLowerCase().includes(value.toLowerCase())
    );

    if (matches.length > 0) {
      setSuggestions(matches);
      setShowSuggestions(true);
    } else {
      setShowSuggestions(false);
    }
  };

  const handleInputFocus = (e: JSX.TargetedEvent<HTMLInputElement, Event>) => {
    // Scroll the input into view when focused, with some padding at the top
    setTimeout(() => {
      (e.target as HTMLInputElement).scrollIntoView({
        behavior: 'smooth',
        block: 'center'
      });
    }, 300); // Small delay to let mobile keyboard appear first
  };

  const handleSuggestionClick = (county: string) => {
    const countySlug = county.toLowerCase().replace(/\s+/g, '-');
    window.location.href = `/texas/${countySlug}`;
  };

  const handleClickOutside = (e: MouseEvent) => {
    const target = e.target as HTMLElement;
    if (!target.closest('.search-widget')) {
      setShowSuggestions(false);
    }
  };

  // Close suggestions when clicking outside
  if (typeof document !== 'undefined') {
    document.addEventListener('click', handleClickOutside);
  }

  return (
    <div class="search-widget">
      <div class="location-prompt">
        <svg class="location-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
        <p>Enter or select a location to see fishing spots</p>
      </div>

      <div class="search-actions">
        <button
          type="button"
          class="btn-primary"
          onClick={handleUseLocation}
          disabled={isLoadingLocation}
        >
          {isLoadingLocation ? (
            <>
              <svg class="spinner" width="20" height="20" viewBox="0 0 50 50">
                <circle cx="25" cy="25" r="20" fill="none" stroke="white" stroke-width="4" stroke-dasharray="80" stroke-dashoffset="60"/>
              </svg>
              Getting location...
            </>
          ) : (
            <>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
              </svg>
              Use Current Location
            </>
          )}
        </button>

        <div class="search-divider">or</div>

        <form class="search-form" onSubmit={handleSearchSubmit}>
          <input
            type="text"
            placeholder="Enter city, county, or zip code..."
            autocomplete="off"
            value={searchQuery}
            onInput={handleInputChange}
            onFocus={handleInputFocus}
          />
          <button type="submit" class="btn-search" disabled={isSearching}>
            {isSearching ? 'Searching...' : 'Search'}
          </button>
        </form>

        {showSuggestions && suggestions.length > 0 && (
          <div class="suggestions active">
            {suggestions.map((loc) => (
              <div
                key={loc.county}
                class="suggestion-item"
                onClick={() => handleSuggestionClick(loc.county)}
              >
                {loc.name} ({loc.county} County)
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
