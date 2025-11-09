import { useState, useEffect, useRef } from 'preact/hooks';
import type { JSX } from 'preact';

interface SearchWidgetProps {
  nominatimEmail?: string;
}

interface Spot {
  id: number;
  slug: string;
  name: string;
  state: string;
  county: string;
  latitude: string;
  longitude: string;
  spot_type: string;
  water_body_name?: string;
  amenities?: any;
  distance?: number;
}

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

export default function SearchWidget({ nominatimEmail = 'contact@wherecanifish.com' }: SearchWidgetProps) {
  // Search state
  const [isLoadingLocation, setIsLoadingLocation] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState<Array<{ name: string; county: string }>>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [loadingMessage, setLoadingMessage] = useState('');

  // Results state
  const [showResults, setShowResults] = useState(false);
  const [showTransition, setShowTransition] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [allSpots, setAllSpots] = useState<Spot[]>([]);
  const [filteredSpots, setFilteredSpots] = useState<Spot[]>([]);
  const [displayedSpots, setDisplayedSpots] = useState<Spot[]>([]);
  const [isLoadingSpots, setIsLoadingSpots] = useState(false);
  const [userLocation, setUserLocation] = useState<{ lat: number; lon: number } | null>(null);
  const [searchContext, setSearchContext] = useState<string>('');

  // Filter state
  const [showFilters, setShowFilters] = useState(false);
  const [typeFilters, setTypeFilters] = useState<Set<string>>(new Set());
  const [sortBy, setSortBy] = useState<'distance' | 'name'>('distance');

  // Infinite scroll state
  const [displayCount, setDisplayCount] = useState(20);
  const resultsRef = useRef<HTMLDivElement>(null);
  const searchResultsRef = useRef<HTMLDivElement>(null);
  const widgetRef = useRef<HTMLDivElement>(null);

  // Theme detection
  const [isDarkMode, setIsDarkMode] = useState(true);

  useEffect(() => {
    if (typeof document !== 'undefined') {
      const checkTheme = () => {
        const theme = document.documentElement.getAttribute('data-theme');
        setIsDarkMode(theme !== 'light');
      };

      checkTheme();

      // Watch for theme changes
      const observer = new MutationObserver(checkTheme);
      observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['data-theme']
      });

      return () => observer.disconnect();
    }
  }, []);

  // Restore search state from sessionStorage on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedState = sessionStorage.getItem('searchWidgetState');
      if (savedState) {
        try {
          const state = JSON.parse(savedState);

          // Ensure all loading states are cleared
          setIsLoadingLocation(false);
          setIsSearching(false);
          setIsLoadingSpots(false);
          setLoadingMessage('');
          setErrorMessage('');

          // Restore search state
          setUserLocation(state.userLocation);
          setSearchContext(state.searchContext);
          setAllSpots(state.allSpots);
          setTypeFilters(new Set(state.typeFilters));
          setSortBy(state.sortBy);
          setDisplayCount(state.displayCount);
          setShowResults(true);
        } catch (error) {
          console.error('Failed to restore search state:', error);
          sessionStorage.removeItem('searchWidgetState');
        }
      }
    }
  }, []);

  // Save search state to sessionStorage when results are shown
  useEffect(() => {
    if (typeof window !== 'undefined' && showResults && allSpots.length > 0) {
      const state = {
        userLocation,
        searchContext,
        allSpots,
        typeFilters: Array.from(typeFilters),
        sortBy,
        displayCount,
      };
      sessionStorage.setItem('searchWidgetState', JSON.stringify(state));
    }
  }, [showResults, userLocation, searchContext, allSpots, typeFilters, sortBy, displayCount]);

  // API URL
  const API_URL = typeof window !== 'undefined'
    ? (window.location.hostname === 'localhost' || window.location.hostname.startsWith('100.') || window.location.hostname.startsWith('127.') || window.location.port === '4321'
        ? `http://${window.location.hostname}:8000`
        : `${window.location.protocol}//${window.location.host}/api`)
    : '';

  // Common Texas locations for autocomplete
  const commonLocations = [
    { name: 'Houston', county: 'Harris' },
    { name: 'Austin', county: 'Travis' },
    { name: 'Dallas', county: 'Dallas' },
    { name: 'Fort Worth', county: 'Tarrant' },
    { name: 'San Antonio', county: 'Bexar' },
  ];

  // Calculate distance between two points (Haversine formula)
  const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number): number => {
    const R = 3958.8; // Earth's radius in miles
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  };

  // Load all spots from API
  const loadSpots = async () => {
    setIsLoadingSpots(true);
    try {
      const response = await fetch(`${API_URL}/spots.php?limit=5000`);
      const data = await response.json();

      if (data.success) {
        setAllSpots(data.spots);
      } else {
        setErrorMessage('Failed to load fishing spots');
      }
    } catch (error) {
      console.error('Error loading spots:', error);
      setErrorMessage('Failed to load fishing spots. Please try again later.');
    } finally {
      setIsLoadingSpots(false);
    }
  };

  // Filter and sort spots
  useEffect(() => {
    if (!showResults) return;

    let filtered = [...allSpots];

    // Apply type filters (checkbox-based)
    if (typeFilters.size > 0) {
      filtered = filtered.filter(spot => typeFilters.has(spot.spot_type));
    }

    // Calculate distances if we have user location
    if (userLocation) {
      filtered = filtered.map(spot => ({
        ...spot,
        distance: calculateDistance(
          userLocation.lat,
          userLocation.lon,
          parseFloat(spot.latitude),
          parseFloat(spot.longitude)
        )
      }));
    }

    // Sort
    if (sortBy === 'distance' && userLocation) {
      filtered.sort((a, b) => (a.distance || 0) - (b.distance || 0));
    } else if (sortBy === 'name') {
      filtered.sort((a, b) => a.name.localeCompare(b.name));
    }

    // Limit to top 100 for performance if using distance
    if (userLocation) {
      filtered = filtered.slice(0, 100);
    }

    setFilteredSpots(filtered);
    setDisplayedSpots(filtered.slice(0, displayCount));
  }, [allSpots, typeFilters, sortBy, userLocation, showResults, displayCount]);

  // Infinite scroll handler
  const handleScroll = () => {
    if (!resultsRef.current) return;

    const { scrollTop, scrollHeight, clientHeight } = resultsRef.current;
    if (scrollHeight - scrollTop <= clientHeight * 1.5) {
      // Load more when scrolled to 150% of viewport
      if (displayedSpots.length < filteredSpots.length) {
        setDisplayCount(prev => prev + 20);
      }
    }
  };

  // Attach scroll listener
  useEffect(() => {
    const resultsElement = resultsRef.current;
    if (resultsElement && showResults) {
      resultsElement.addEventListener('scroll', handleScroll);
      return () => resultsElement.removeEventListener('scroll', handleScroll);
    }
  }, [showResults, displayedSpots.length, filteredSpots.length]);

  // Scroll results into view when they appear
  useEffect(() => {
    if (showResults) {
      setTimeout(() => {
        // Get the search-container element (parent wrapper in index.astro)
        const searchContainer = document.querySelector('.search-container');
        if (!searchContainer) return;

        // Get the header element to calculate offset
        const header = document.querySelector('header');
        const headerHeight = header ? header.offsetHeight : 0;

        // Get the search-container's position relative to the document
        const containerRect = searchContainer.getBoundingClientRect();
        const currentScrollY = window.pageYOffset || document.documentElement.scrollTop;

        // Calculate absolute position of search-container top
        const containerTopAbsolute = containerRect.top + currentScrollY;

        // Scroll to position container below header with 16px (1rem) padding
        const padding = 16;
        const targetScrollPosition = containerTopAbsolute - headerHeight - padding;

        window.scrollTo({
          top: targetScrollPosition,
          behavior: 'smooth'
        });
      }, 300); // Wait for transition to complete (250ms) + small buffer
    }
  }, [showResults]);

  // Search by geolocation
  const handleUseLocation = async () => {
    if ('geolocation' in navigator) {
      setIsLoadingLocation(true);
      setErrorMessage('');
      setLoadingMessage('Accessing GPS...');

      setTimeout(() => {
        if (isLoadingLocation) {
          setLoadingMessage('Locating position...');
        }
      }, 1000);

      // Check if Permissions API is available and check geolocation permission state
      let permissionDenied = false;
      if ('permissions' in navigator && 'query' in navigator.permissions) {
        try {
          const result = await navigator.permissions.query({ name: 'geolocation' as PermissionName });
          if (result.state === 'denied') {
            permissionDenied = true;
            // Even if denied, we'll still try - user might have just reset permissions
            console.log('Geolocation permission previously denied, attempting anyway...');
          }
        } catch (e) {
          // Permissions API might not support geolocation query in all browsers
          console.log('Unable to query geolocation permission:', e);
        }
      }

      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords;
          setUserLocation({ lat: latitude, lon: longitude });
          setSearchContext(`Near ${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);
          setLoadingMessage('Loading fishing spots...');

          // Load spots if not already loaded
          if (allSpots.length === 0) {
            await loadSpots();
          }

          setIsLoadingLocation(false);
          setLoadingMessage('');

          // Show transition before results
          setShowTransition(true);
          setTimeout(() => {
            setShowTransition(false);
            setShowResults(true);
          }, 250);

          setSortBy('distance');
        },
        (error) => {
          setIsLoadingLocation(false);
          setLoadingMessage('');

          if (error.code === error.PERMISSION_DENIED) {
            setErrorMessage('Location access denied. To enable: Click the location icon in your browser\'s address bar, allow location access, then click "Use Current Location" again.');
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

  // Search by text query
  const handleSearchSubmit = async (e: JSX.TargetedEvent<HTMLFormElement, Event>) => {
    e.preventDefault();

    const query = searchQuery.trim();
    if (!query) return;

    setIsSearching(true);
    setShowSuggestions(false);
    setErrorMessage('');
    setLoadingMessage('Searching locations...');

    // Try to geocode the query
    const specificQuery = query + ', texas';
    const apiUrl = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(specificQuery)}&format=json&limit=1&email=${nominatimEmail}`;

    try {
      const response = await fetch(apiUrl);

      if (!response.ok) {
        throw new Error(`API response not OK: ${response.status}`);
      }

      const data = await response.json();

      if (data && data.length > 0) {
        // Geocoding succeeded - use coordinates
        const lat = parseFloat(data[0].lat);
        const lon = parseFloat(data[0].lon);
        setUserLocation({ lat, lon });
        setSearchContext(`Near ${query}`);
        setSortBy('distance');
      } else {
        // Geocoding failed - use text search
        setUserLocation(null);
        setSearchContext(`Search: "${query}"`);
        setSortBy('name');
      }

      // Load spots if not already loaded
      setLoadingMessage('Loading fishing spots...');
      if (allSpots.length === 0) {
        await loadSpots();
      }

      setIsSearching(false);
      setLoadingMessage('');
      setSearchQuery(''); // Clear search input after successful search

      // Show transition before results
      setShowTransition(true);
      setTimeout(() => {
        setShowTransition(false);
        setShowResults(true);
      }, 250);

    } catch (error) {
      console.error('Geocoding error:', error);
      setIsSearching(false);
      setLoadingMessage('');
      setErrorMessage('Connection error. Please try again.');
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
    setTimeout(() => {
      (e.target as HTMLInputElement).scrollIntoView({
        behavior: 'smooth',
        block: 'center'
      });
    }, 300);
  };

  const handleSuggestionClick = (county: string) => {
    // Navigate to county page instead of inline results
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

  const handleNewSearch = () => {
    // Trigger wipe-away animation, then return to search (no loading overlay)
    setIsTransitioning(true);

    // Clear saved search state
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem('searchWidgetState');
    }

    // Clear all loading states immediately to prevent stuck state
    setIsLoadingLocation(false);
    setIsSearching(false);
    setIsLoadingSpots(false);
    setLoadingMessage('');
    setErrorMessage('');

    setTimeout(() => {
      setShowResults(false);
      setUserLocation(null);
      setSearchContext('');
      setTypeFilters(new Set());
      setDisplayCount(20);
    }, 500); // Wait for wipe-away animation

    setTimeout(() => {
      setIsTransitioning(false);
    }, 900); // Reset transitioning state
  };

  const handleTypeFilterToggle = (type: string) => {
    const newFilters = new Set(typeFilters);
    if (newFilters.has(type)) {
      newFilters.delete(type);
    } else {
      newFilters.add(type);
    }
    setTypeFilters(newFilters);
  };

  // Close suggestions when clicking outside
  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, []);

  // Helper function to get county slug
  const getCountySlug = (countyName: string): string => {
    if (!countyName) return '';
    if (countyName.includes(',')) {
      countyName = countyName.split(',')[0].trim();
    }
    countyName = countyName.replace(/\s+County$/i, '').trim();
    return countyName.toLowerCase().replace(/\s+/g, '-');
  };

  // Format distance display
  const formatDistance = (distance?: number): string => {
    if (!distance) return '';
    if (distance < 0.1) {
      return `${(distance * 5280).toFixed(0)} ft away`;
    }
    return `${distance.toFixed(1)} mi away`;
  };

  return (
    <div class="search-widget" data-show-results={showResults} data-transitioning={isTransitioning} ref={widgetRef}>
      {/* Transition Loading Overlay */}
      {showTransition && (
        <div class="search-widget-transition">
          {isDarkMode ? (
            <div class="transition-loading-dark">
              <div class="loading-text">LOADING...</div>
              <div class="loading-bar"></div>
              <div class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          ) : (
            <div class="transition-loading-light">
              <div class="loading-text">Loading</div>
              <div class="loading-spinner"></div>
              <div class="loading-message">Finding fishing spots...</div>
            </div>
          )}
        </div>
      )}

      {!showResults ? (
        // SEARCH MODE
        <>
          <div class="location-prompt">
            <svg class="location-icon" width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            <p class="location-title">Find Fishing Spots Near You</p>
          </div>

          <div class="search-actions">
            {/* Primary action: Use Current Location */}
            <button
              type="button"
              class="btn-location-hero"
              onClick={handleUseLocation}
              disabled={isLoadingLocation}
            >
              {isLoadingLocation ? (
                <div class="location-loading">
                  <svg class="spinner" width="28" height="28" viewBox="0 0 50 50">
                    <circle cx="25" cy="25" r="20" fill="none" stroke="currentColor" stroke-width="4" stroke-dasharray="80" stroke-dashoffset="60"/>
                  </svg>
                  <span class="loading-text">{loadingMessage || 'Locating...'}</span>
                </div>
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
              <span class="divider-text">or search by location</span>
            </div>

            {/* Secondary action: Manual Search */}
            <div class="search-form-section">
              <form class="search-form" onSubmit={handleSearchSubmit}>
                <div class="input-wrapper">
                  <span class="search-prompt">›</span>
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
        </>
      ) : (
        // RESULTS MODE
        <div class="search-results" ref={searchResultsRef}>
          {/* Results Header */}
          <div class="results-header">
            <div class="results-info">
              <span class="query-prompt">›</span>
              <span class="query-text">{searchContext} ({filteredSpots.length} spot{filteredSpots.length !== 1 ? 's' : ''})</span>
            </div>
            <button class="btn-new-search" onClick={handleNewSearch}>
              ← New Search
            </button>
          </div>

          {/* Filter & Sort Controls */}
          <div class="results-controls">
            <div class="controls-row">
              <button
                class="btn-filter-toggle"
                onClick={() => setShowFilters(!showFilters)}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/>
                </svg>
                Filters {typeFilters.size > 0 && `(${typeFilters.size})`}
              </button>

              <div class="sort-control">
                <label>Sort:</label>
                <select value={sortBy} onChange={(e) => setSortBy((e.target as HTMLSelectElement).value as any)}>
                  {userLocation && <option value="distance">Distance</option>}
                  <option value="name">Name</option>
                </select>
              </div>
            </div>

            {/* Collapsible Filter Panel */}
            {showFilters && (
              <div class="filter-panel">
                <div class="filter-section-title">Spot Type</div>
                <div class="filter-checkboxes">
                  <label class="filter-checkbox">
                    <input
                      type="checkbox"
                      checked={typeFilters.has('lake')}
                      onChange={() => handleTypeFilterToggle('lake')}
                    />
                    <span class="checkbox-label">Lakes</span>
                  </label>

                  <label class="filter-checkbox">
                    <input
                      type="checkbox"
                      checked={typeFilters.has('river_access')}
                      onChange={() => handleTypeFilterToggle('river_access')}
                    />
                    <span class="checkbox-label">River Access</span>
                  </label>

                  <label class="filter-checkbox">
                    <input
                      type="checkbox"
                      checked={typeFilters.has('public_water')}
                      onChange={() => handleTypeFilterToggle('public_water')}
                    />
                    <span class="checkbox-label">Public Waters</span>
                  </label>

                  <label class="filter-checkbox highlight-no-license">
                    <input
                      type="checkbox"
                      checked={typeFilters.has('state_park')}
                      onChange={() => handleTypeFilterToggle('state_park')}
                    />
                    <span class="checkbox-label">
                      State Parks
                      <span class="no-license-badge">No License Required</span>
                    </span>
                  </label>

                  <label class="filter-checkbox">
                    <input
                      type="checkbox"
                      checked={typeFilters.has('fishing_pier')}
                      onChange={() => handleTypeFilterToggle('fishing_pier')}
                    />
                    <span class="checkbox-label">Fishing Piers</span>
                  </label>
                </div>
                {typeFilters.size > 0 && (
                  <button class="btn-clear-filters" onClick={() => setTypeFilters(new Set())}>
                    Clear All Filters
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Results Grid */}
          <div class="results-container" ref={resultsRef}>
            {isLoadingSpots ? (
              <div class="loading-state">
                <svg class="spinner" width="40" height="40" viewBox="0 0 50 50">
                  <circle cx="25" cy="25" r="20" fill="none" stroke="currentColor" stroke-width="4" stroke-dasharray="80" stroke-dashoffset="60"/>
                </svg>
                <p>Loading fishing spots...</p>
              </div>
            ) : displayedSpots.length === 0 ? (
              <div class="empty-state">
                <p>No fishing spots found.</p>
                <button onClick={handleNewSearch}>Try a different search</button>
              </div>
            ) : (
              <div class="results-grid">
                {displayedSpots.map((spot, index) => {
                  const displayName = spot.name.replace(/\s*\([a-z]+\d+\)\s*$/i, '');
                  const countySlug = getCountySlug(spot.county);
                  const amenities = spot.amenities ? (typeof spot.amenities === 'string' ? JSON.parse(spot.amenities) : spot.amenities) : {};

                  const amenityIcons: Record<string, string> = {
                    'boat_ramp': '🚤 Boat Ramp',
                    'fishing_pier': '🎣 Pier',
                    'fish_cleaning': '🔪 Cleaning',
                    'restrooms': '🚻 Restrooms',
                    'parking': '🅿️ Parking',
                  };

                  const prominentAmenities = Object.entries(amenityIcons)
                    .filter(([key]) => amenities[key] === true)
                    .map(([_, label]) => label)
                    .slice(0, 3);

                  return (
                    <a
                      key={spot.id}
                      href={`/${stateSlugLookup[spot.state]}/${countySlug}/${spot.slug}`}
                      class="spot-card"
                      data-spot-type={spot.spot_type}
                      style={`animation-delay: ${Math.min(index * 0.05, 0.5)}s`}
                    >
                      <div class="card-header">
                        <h3>{displayName}</h3>
                        {spot.distance && (
                          <div class="distance-indicator">{formatDistance(spot.distance)}</div>
                        )}
                      </div>
                      <div class="card-body">
                        {prominentAmenities.length > 0 ? (
                          <>
                            {prominentAmenities.map(amenity => (
                              <span key={amenity} class="card-meta-item">{amenity}</span>
                            ))}
                          </>
                        ) : (
                          <span class="amenity-placeholder">No amenities listed</span>
                        )}
                      </div>
                    </a>
                  );
                })}
              </div>
            )}

            {/* Load More Indicator */}
            {displayedSpots.length < filteredSpots.length && (
              <div class="load-more-indicator">
                <svg class="spinner-small" width="24" height="24" viewBox="0 0 50 50">
                  <circle cx="25" cy="25" r="20" fill="none" stroke="currentColor" stroke-width="5" stroke-dasharray="80" stroke-dashoffset="60"/>
                </svg>
                <span>Loading more...</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
