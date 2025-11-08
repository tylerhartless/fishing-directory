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
  const [errorMessage, setErrorMessage] = useState('');
  const [loadingMessage, setLoadingMessage] = useState('');

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
      setErrorMessage('');
      setLoadingMessage('Accessing GPS...');

      setTimeout(() => {
        if (isLoadingLocation) {
          setLoadingMessage('Locating position...');
        }
      }, 1000);

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          setLoadingMessage('Location acquired!');
          setTimeout(() => {
            window.location.href = `/spots?lat=${latitude}&lon=${longitude}`;
          }, 500);
        },
        (error) => {
          setIsLoadingLocation(false);
          setLoadingMessage('');

          if (error.code === error.PERMISSION_DENIED) {
            setErrorMessage('Location access denied. Please enable location permissions in your browser settings to use this feature.');
          } else if (window.location.protocol === 'http:' && window.location.hostname !== 'localhost') {
            setErrorMessage('Location requires HTTPS. Please search manually or enable HTTPS.');
          } else {
            setErrorMessage('Unable to determine your location. Please try searching manually below.');
          }
        }
      );
    } else {
      setErrorMessage('Your browser does not support geolocation. Please search manually below.');
    }
  };

  const handleSearchSubmit = async (e: JSX.TargetedEvent<HTMLFormElement, Event>) => {
    e.preventDefault();

    const query = searchQuery.trim();
    if (!query) return;

    setIsSearching(true);
    setShowSuggestions(false);
    setErrorMessage('');
    setLoadingMessage('Searching locations...');

    // Make the query more specific for better results
    const specificQuery = query + ', texas';
    const apiUrl = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(specificQuery)}&format=json&limit=1&email=${nominatimEmail}`;

    setTimeout(() => {
      if (isSearching) {
        setLoadingMessage('Finding coordinates...');
      }
    }, 800);

    try {
      const response = await fetch(apiUrl);

      if (!response.ok) {
        throw new Error(`API response not OK: ${response.status}`);
      }

      const data = await response.json();

      if (data && data.length > 0) {
        const lat = data[0].lat;
        const lon = data[0].lon;
        setLoadingMessage('Location found!');
        setTimeout(() => {
          window.location.href = `/spots?lat=${lat}&lon=${lon}`;
        }, 500);
      } else {
        // Fallback to text search
        window.location.href = `/spots?q=${encodeURIComponent(query)}`;
      }
    } catch (error) {
      console.error('Geocoding error:', error);
      setIsSearching(false);
      setLoadingMessage('');
      setErrorMessage('Connection error. Trying alternative search...');

      // Fallback to text search after a brief delay
      setTimeout(() => {
        window.location.href = `/spots?q=${encodeURIComponent(query)}`;
      }, 1500);
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

  const dismissError = () => {
    setErrorMessage('');
  };

  // Close suggestions when clicking outside
  if (typeof document !== 'undefined') {
    document.addEventListener('click', handleClickOutside);
  }

  return (
    <div class="search-widget">
      <div class="location-prompt">
        <svg class="location-icon" width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
        <p class="location-title">Find Fishing Spots Near You</p>
      </div>

      <div class="search-actions">
        {/* Primary action: Use Current Location - HERO ELEMENT */}
        <button
          type="button"
          class="btn-location-hero"
          onClick={handleUseLocation}
          disabled={isLoadingLocation}
        >
          {isLoadingLocation ? (
            <>
              <div class="location-loading">
                <svg class="spinner" width="28" height="28" viewBox="0 0 50 50">
                  <circle cx="25" cy="25" r="20" fill="none" stroke="currentColor" stroke-width="4" stroke-dasharray="80" stroke-dashoffset="60"/>
                </svg>
                <span class="loading-text">{loadingMessage || 'Locating...'}</span>
              </div>
            </>
          ) : (
            <>
              <svg class="location-pin" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
              </svg>
              <span class="btn-location-text">Use Current Location</span>
            </>
          )}
        </button>

        {/* Error message display */}
        {errorMessage && (
          <div class="error-message">
            <div class="error-content">
              <span class="error-icon">⚠</span>
              <span class="error-text">{errorMessage}</span>
              <button class="error-dismiss" onClick={dismissError} aria-label="Dismiss error">×</button>
            </div>
          </div>
        )}

        <div class="search-divider">
          <span class="divider-text">or search manually</span>
        </div>

        {/* Secondary action: Manual Search */}
        <div class="search-form-section">
          <div class="search-form-header">
            <span class="search-prompt">›</span>
            <span class="search-label">Search by Location</span>
          </div>

          <form class="search-form" onSubmit={handleSearchSubmit}>
            <div class="input-wrapper">
              <input
                type="text"
                class="search-input"
                placeholder="Enter city, county, or zip code"
                autocomplete="off"
                value={searchQuery}
                onInput={handleInputChange}
                onFocus={handleInputFocus}
                disabled={isSearching}
              />
              <span class="input-cursor"></span>
            </div>
            <button type="submit" class="btn-search" disabled={isSearching || !searchQuery.trim()}>
              {isSearching ? (
                <span class="searching-state">
                  <svg class="spinner-small" width="16" height="16" viewBox="0 0 50 50">
                    <circle cx="25" cy="25" r="20" fill="none" stroke="currentColor" stroke-width="5" stroke-dasharray="80" stroke-dashoffset="60"/>
                  </svg>
                  {loadingMessage || 'Searching...'}
                </span>
              ) : (
                'Search'
              )}
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
                  <span class="suggestion-prompt">›</span>
                  <span class="suggestion-text">{loc.name} <span class="suggestion-county">({loc.county} County)</span></span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
