import { useState, useEffect, useRef } from 'preact/hooks';
import type { JSX } from 'preact';
import InFeedAd from './InFeedAd';
import MapView from './MapView';
import { ADS_ENABLED, PUBLISHER_ID, AD_FREQUENCY, AD_SLOTS } from '../lib/ads-config';

// Development-only logging
const isDev = import.meta.env.DEV;

interface SearchWidgetProps {
  nominatimEmail?: string;
  mapboxToken?: string;
  // Pre-loaded data mode props
  initialSpots?: Spot[];
  initialTypeFilter?: string;
  hideSearch?: boolean;
  hideFilters?: boolean;
  defaultCenter?: [number, number];  // [lat, lon]
  defaultZoom?: number;
  showSortToggle?: boolean;
  backButtonUrl?: string;
  backButtonText?: string;
  availableSpotTypes?: string[];      // Limit filter chips to these types
  itemMode?: 'spot' | 'county';      // Controls card rendering and map markers
}

interface Spot {
  id: number;
  slug: string;
  name: string;
  state: string;
  county: string;
  county_slug?: string;
  latitude: string | number;
  longitude: string | number;
  spot_type: string;
  water_body_name?: string;
  amenities?: any;
  distance?: number;
  count?: number;                     // County mode: number of spots in county
}

const ALL_SPOT_TYPES = ['lake', 'river_access', 'public_water', 'state_park', 'fishing_pier'] as const;

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

export default function SearchWidget({
  nominatimEmail = 'contact@wherecanifish.com',
  mapboxToken = '',
  initialSpots,
  initialTypeFilter,
  hideSearch = false,
  hideFilters = false,
  defaultCenter,
  defaultZoom,
  showSortToggle = false,
  backButtonUrl,
  backButtonText = 'Back',
  availableSpotTypes,
  itemMode = 'spot',
}: SearchWidgetProps) {
  const isPreloadedMode = !!initialSpots && initialSpots.length > 0;
  const chipTypes = availableSpotTypes || [...ALL_SPOT_TYPES];

  // Search state
  const [isLoadingLocation, setIsLoadingLocation] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState<Array<{ name: string; county: string }>>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [loadingMessage, setLoadingMessage] = useState('');

  // Results state
  const [showResults, setShowResults] = useState(isPreloadedMode);
  const [showTransition, setShowTransition] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [allSpots, setAllSpots] = useState<Spot[]>(isPreloadedMode ? initialSpots! : []);
  const [filteredSpots, setFilteredSpots] = useState<Spot[]>([]);
  const [displayedSpots, setDisplayedSpots] = useState<Spot[]>([]);
  const [isLoadingSpots, setIsLoadingSpots] = useState(false);
  const [userLocation, setUserLocation] = useState<{ lat: number; lon: number } | null>(null);
  const [searchContext, setSearchContext] = useState<string>('');

  // Filter state
  const [typeFilters, setTypeFilters] = useState<Set<string>>(
    initialTypeFilter ? new Set([initialTypeFilter]) : new Set(chipTypes)
  );
  const [searchRadius, setSearchRadius] = useState<number>(50); // Default to 50 miles
  const [sortMode, setSortMode] = useState<'distance' | 'alphabetical'>('alphabetical');

  // View mode state (list vs map)
  const [viewMode, setViewMode] = useState<'list' | 'map'>('map');

  // Radius expansion steps for progressive loading
  const RADIUS_STEPS = [50, 100, 200, 500];

  // Infinite scroll state
  const [displayCount, setDisplayCount] = useState(20);
  const resultsRef = useRef<HTMLDivElement>(null);
  const searchResultsRef = useRef<HTMLDivElement>(null);
  const widgetRef = useRef<HTMLDivElement>(null);
  const searchRadiusRef = useRef(searchRadius);
  searchRadiusRef.current = searchRadius;

  // Cancellation refs for cleanup
  const geoCancelRef = useRef<(() => void) | null>(null);
  const fetchAbortRef = useRef<AbortController | null>(null);
  const isLoadingLocationRef = useRef(false);

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

  // Cleanup geolocation and fetch on unmount
  useEffect(() => {
    return () => {
      if (geoCancelRef.current) {
        geoCancelRef.current();
        geoCancelRef.current = null;
      }
      if (fetchAbortRef.current) {
        fetchAbortRef.current.abort();
        fetchAbortRef.current = null;
      }
    };
  }, []);

  // Restore search state from sessionStorage on mount (search mode only)
  useEffect(() => {
    if (isPreloadedMode) return;
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
          const restoredFilters = new Set<string>(state.typeFilters);
          setTypeFilters(restoredFilters.size === 0 ? new Set(ALL_SPOT_TYPES) : restoredFilters);
          setSearchRadius(state.searchRadius || 50);
          setDisplayCount(state.displayCount);
          if (state.viewMode) setViewMode(state.viewMode);
          setShowResults(true);
        } catch (error) {
          if (isDev) console.error('Failed to restore search state:', error);
          sessionStorage.removeItem('searchWidgetState');
        }
      }
    }
  }, []);

  // In pre-loaded mode, check sessionStorage for saved GPS location
  useEffect(() => {
    if (!isPreloadedMode) return;
    try {
      const savedLocation = sessionStorage.getItem('user_gps_location');
      if (savedLocation) {
        const locationData = JSON.parse(savedLocation);
        const now = Date.now();
        if (locationData.timestamp && (now - locationData.timestamp) < 60 * 60 * 1000) {
          setUserLocation({ lat: locationData.lat, lon: locationData.lon });
          setSortMode('distance');
        }
      }
    } catch (e) {
      // ignore
    }
  }, []);

  // Save search state to sessionStorage when results are shown (search mode only)
  useEffect(() => {
    if (isPreloadedMode) return;
    if (typeof window !== 'undefined' && showResults && allSpots.length > 0) {
      const state = {
        userLocation,
        searchContext,
        allSpots,
        typeFilters: Array.from(typeFilters),
        searchRadius,
        displayCount,
        viewMode,
      };
      sessionStorage.setItem('searchWidgetState', JSON.stringify(state));
    }
  }, [showResults, userLocation, searchContext, allSpots, typeFilters, searchRadius, displayCount, viewMode]);

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
    // Abort any previous in-flight request
    if (fetchAbortRef.current) {
      fetchAbortRef.current.abort();
    }
    const controller = new AbortController();
    fetchAbortRef.current = controller;

    setIsLoadingSpots(true);
    try {
      const response = await fetch(`${API_URL}/spots.php?limit=5000`, {
        signal: controller.signal,
      });
      const data = await response.json();

      if (data.success) {
        setAllSpots(data.spots);
      } else {
        setErrorMessage('Failed to load fishing spots');
      }
    } catch (error) {
      if (error instanceof DOMException && error.name === 'AbortError') {
        // Request was cancelled — not an error
        return;
      }
      if (isDev) console.error('Error loading spots:', error);
      setErrorMessage('Failed to load fishing spots. Please try again later.');
    } finally {
      setIsLoadingSpots(false);
      if (fetchAbortRef.current === controller) {
        fetchAbortRef.current = null;
      }
    }
  };

  // Filter and sort spots
  useEffect(() => {
    if (!showResults) return;

    let filtered = [...allSpots];

    // Apply type filters
    if (initialTypeFilter && hideFilters) {
      // Locked filter mode — always filter to the specified type
      filtered = filtered.filter(spot => spot.spot_type === initialTypeFilter);
    } else if (typeFilters.size > 0 && typeFilters.size < ALL_SPOT_TYPES.length) {
      filtered = filtered.filter(spot => typeFilters.has(spot.spot_type));
    }

    // Calculate distances if we have user location
    if (userLocation) {
      filtered = filtered.map(spot => ({
        ...spot,
        distance: calculateDistance(
          userLocation.lat,
          userLocation.lon,
          parseFloat(String(spot.latitude)),
          parseFloat(String(spot.longitude))
        )
      }));

      // In pre-loaded mode, skip radius filtering (all spots are already scoped)
      if (!isPreloadedMode) {
        // In map view, show all spots (clustering handles density); in list view, use progressive radius
        const effectiveRadius = viewMode === 'map' ? 500 : searchRadius;
        let spotsInRadius = filtered.filter(spot => (spot.distance || 0) <= effectiveRadius);

        // Auto-expand only if zero results found (for remote areas)
        if (spotsInRadius.length === 0) {
          for (const radius of RADIUS_STEPS) {
            if (radius <= effectiveRadius) continue;
            spotsInRadius = filtered.filter(spot => (spot.distance || 0) <= radius);
            if (spotsInRadius.length > 0) {
              setSearchRadius(radius);
              break;
            }
          }
        }

        filtered = spotsInRadius;
      }
    }

    // Sort based on sortMode (pre-loaded) or default behavior (search)
    if (isPreloadedMode) {
      if (sortMode === 'distance' && userLocation) {
        filtered.sort((a, b) => (a.distance || 0) - (b.distance || 0));
      } else {
        filtered.sort((a, b) => a.name.localeCompare(b.name));
      }
    } else {
      // Search mode: always sort by distance when user location is available
      if (userLocation) {
        filtered.sort((a, b) => (a.distance || 0) - (b.distance || 0));
      } else {
        filtered.sort((a, b) => a.name.localeCompare(b.name));
      }
    }

    setFilteredSpots(filtered);
    setDisplayedSpots(filtered.slice(0, displayCount));
  }, [allSpots, typeFilters, searchRadius, userLocation, showResults, displayCount, viewMode, sortMode]);

  // Infinite scroll handler
  const handleScroll = () => {
    if (!resultsRef.current) return;

    const { scrollTop, scrollHeight, clientHeight } = resultsRef.current;

    // Update fade classes based on scroll position
    const isScrolledFromTop = scrollTop > 10;
    const isScrolledFromBottom = scrollTop + clientHeight < scrollHeight - 10;

    if (isScrolledFromTop) {
      resultsRef.current.classList.add('scrolled-from-top');
    } else {
      resultsRef.current.classList.remove('scrolled-from-top');
    }

    if (isScrolledFromBottom) {
      resultsRef.current.classList.add('scrolled-from-bottom');
    } else {
      resultsRef.current.classList.remove('scrolled-from-bottom');
    }

    // Load more when scrolled to 150% of viewport
    if (scrollHeight - scrollTop <= clientHeight * 1.5) {
      if (displayedSpots.length < filteredSpots.length) {
        setDisplayCount(prev => prev + 20);
      } else if (userLocation) {
        // All spots in current radius shown — expand to next radius step
        const currentRadius = searchRadiusRef.current;
        const nextRadius = RADIUS_STEPS.find(r => r > currentRadius);
        if (nextRadius) {
          setSearchRadius(nextRadius);
        }
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

  // Scroll results into view when they appear (home page only)
  // Only on mobile and tablet, not on desktop (>= 1024px)
  useEffect(() => {
    if (isPreloadedMode) return; // Don't auto-scroll on directory pages
    if (showResults) {
      // Check if window width is less than desktop breakpoint (1024px)
      if (window.innerWidth >= 1024) {
        return; // Don't scroll on desktop
      }

      setTimeout(() => {
        // Get the search-container element (parent wrapper in index.astro)
        // Only scroll on home page - search-container only exists there
        const searchContainer = document.querySelector('.search-container');
        if (!searchContainer) return;

        // Get the search-container's position relative to the document
        const containerRect = searchContainer.getBoundingClientRect();
        const currentScrollY = window.pageYOffset || document.documentElement.scrollTop;

        // Calculate absolute position of search-container top
        const containerTopAbsolute = containerRect.top + currentScrollY;

        // Scroll to position the widget container with padding for balanced spacing
        const padding = 17; // Balanced padding for even gap
        const targetScrollPosition = containerTopAbsolute - padding;

        window.scrollTo({
          top: targetScrollPosition,
          behavior: 'smooth'
        });
      }, 300); // Wait for transition to complete (250ms) + small buffer
    }
  }, [showResults]);

  // Geolocation options: use WiFi/cell for speed, 10s timeout, accept cached positions up to 1 min old
  const geoOptions: PositionOptions = {
    enableHighAccuracy: false,
    timeout: 10000,
    maximumAge: 60000,
  };

  // Search by geolocation
  const handleUseLocation = async () => {
    if ('geolocation' in navigator) {
      // Cancel any previous in-flight geolocation callback
      if (geoCancelRef.current) {
        geoCancelRef.current();
      }

      let isCancelled = false;
      geoCancelRef.current = () => {
        isCancelled = true;
        isLoadingLocationRef.current = false;
        setIsLoadingLocation(false);
        setLoadingMessage('');
      };

      setIsLoadingLocation(true);
      isLoadingLocationRef.current = true;
      setErrorMessage('');
      setLoadingMessage('Accessing GPS...');

      setTimeout(() => {
        if (isLoadingLocationRef.current) {
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
            if (isDev) console.log('Geolocation permission previously denied, attempting anyway...');
          }
        } catch (e) {
          // Permissions API might not support geolocation query in all browsers
          if (isDev) console.log('Unable to query geolocation permission:', e);
        }
      }

      navigator.geolocation.getCurrentPosition(
        async (position) => {
          if (isCancelled) return;
          geoCancelRef.current = null;

          const { latitude, longitude } = position.coords;
          if (isDev) console.log('[SearchWidget] GPS success:', { latitude, longitude });
          setUserLocation({ lat: latitude, lon: longitude });
          setSearchContext(`Near ${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);
          setLoadingMessage('Loading fishing spots...');

          // Store location in sessionStorage for use on other pages (1 hour cache)
          if (typeof window !== 'undefined') {
            sessionStorage.setItem('user_gps_location', JSON.stringify({
              lat: latitude,
              lon: longitude,
              timestamp: Date.now()
            }));
          }

          // Load spots if not already loaded
          if (allSpots.length === 0) {
            if (isDev) console.log('[SearchWidget] Loading spots from API...');
            await loadSpots();
          } else {
            if (isDev) console.log('[SearchWidget] Spots already loaded:', allSpots.length);
          }

          if (isDev) console.log('[SearchWidget] allSpots count after load:', allSpots.length);

          isLoadingLocationRef.current = false;
          setIsLoadingLocation(false);
          setLoadingMessage('');

          // Show transition before results
          setShowTransition(true);
          setTimeout(() => {
            setShowTransition(false);
            setShowResults(true);
          }, 250);
        },
        (error) => {
          if (isCancelled) return;
          geoCancelRef.current = null;

          if (isDev) console.log('[SearchWidget] GPS error:', error.code, error.message);
          isLoadingLocationRef.current = false;
          setIsLoadingLocation(false);
          setLoadingMessage('');

          if (error.code === error.PERMISSION_DENIED) {
            setErrorMessage('Location access denied. To enable: Click the location icon in your browser\'s address bar, allow location access, then click "Use Current Location" again.');
          } else if (window.location.protocol === 'http:' && window.location.hostname !== 'localhost') {
            setErrorMessage('Location requires HTTPS. Please search manually or enable HTTPS.');
          } else {
            setErrorMessage('Unable to determine your location. Please try searching manually below.');
          }
        },
        geoOptions
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
      } else {
        // Geocoding failed - use text search
        setUserLocation(null);
        setSearchContext(`Search: "${query}"`);
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
      if (isDev) console.error('Geocoding error:', error);
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

  const handleSortToggle = () => {
    if (sortMode === 'alphabetical') {
      if (userLocation) {
        setSortMode('distance');
      } else if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const loc = { lat: position.coords.latitude, lon: position.coords.longitude };
            setUserLocation(loc);
            setSortMode('distance');
            sessionStorage.setItem('user_gps_location', JSON.stringify({
              ...loc, timestamp: Date.now()
            }));
          },
          () => {
            // GPS failed — stay on alphabetical
          },
          geoOptions
        );
      }
    } else {
      setSortMode('alphabetical');
    }
  };

  const handleNewSearch = () => {
    // In pre-loaded mode, navigate back
    if (isPreloadedMode && backButtonUrl) {
      window.location.href = backButtonUrl;
      return;
    }

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
      setSearchRadius(50);
      setDisplayCount(20);
      setViewMode('map');
    }, 500); // Wait for wipe-away animation

    setTimeout(() => {
      setIsTransitioning(false);
    }, 900); // Reset transitioning state
  };

  const handleTypeFilterToggle = (type: string) => {
    const isDefaultState = typeFilters.size === chipTypes.length;

    if (isDefaultState) {
      // First tap from "all active": isolate to just this one
      setTypeFilters(new Set([type]));
    } else {
      const newFilters = new Set(typeFilters);
      if (newFilters.has(type)) {
        // Deselect this chip; if it was the last one, reset to all
        newFilters.delete(type);
        if (newFilters.size === 0) {
          setTypeFilters(new Set(chipTypes));
          return;
        }
      } else {
        // Stack: add this chip to the active set
        newFilters.add(type);
      }
      setTypeFilters(newFilters);
    }
  };

  const handleClearTypeFilters = () => {
    setTypeFilters(new Set(chipTypes));
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
    <div class="search-widget" data-show-results={showResults} data-transitioning={isTransitioning} data-preloaded={isPreloadedMode} ref={widgetRef}>
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

      {!showResults && !hideSearch ? (
        // SEARCH MODE
        <>
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
                    <circle cx="12" cy="12" r="10" stroke-width="2"/>
                    <circle cx="12" cy="12" r="6" stroke-width="2"/>
                    <circle cx="12" cy="12" r="2" stroke-width="2"/>
                    <line x1="12" y1="0" x2="12" y2="5" stroke-width="2" stroke-linecap="round"/>
                    <line x1="12" y1="19" x2="12" y2="24" stroke-width="2" stroke-linecap="round"/>
                    <line x1="0" y1="12" x2="5" y2="12" stroke-width="2" stroke-linecap="round"/>
                    <line x1="19" y1="12" x2="24" y2="12" stroke-width="2" stroke-linecap="round"/>
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
              <form class="search-form" onSubmit={handleSearchSubmit}>
                <div class="input-wrapper">
                  <span class="search-prompt">›</span>
                  <input
                    type="text"
                    class="search-input"
                    placeholder="City or zip code"
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
            {isPreloadedMode && backButtonUrl ? (
              <a href={backButtonUrl} class="btn-new-search">
                ← {backButtonText}
              </a>
            ) : !isPreloadedMode ? (
              <button class="btn-new-search" onClick={handleNewSearch}>
                ← New Search
              </button>
            ) : null}

            {showSortToggle && viewMode === 'list' && (
              <button
                class="control-button"
                onClick={handleSortToggle}
              >
                <span class="control-label">Sort:</span>
                <span class="control-label">{sortMode === 'distance' ? 'Distance' : 'A-Z'}</span>
              </button>
            )}

            {mapboxToken && (
              <button
                class={`control-button ${viewMode === 'map' ? 'control-button-active' : ''}`}
                onClick={() => setViewMode(viewMode === 'list' ? 'map' : 'list')}
                aria-label={viewMode === 'list' ? 'Switch to map view' : 'Switch to list view'}
              >
                <span class="control-label">{viewMode === 'list' ? 'Map' : 'List'}</span>
              </button>
            )}
          </div>

          {/* Filter Chips */}
          {!hideFilters && <div class="filter-chips">
            {chipTypes.map(type => {
              const isActive = typeFilters.has(type);
              const labels: Record<string, string> = {
                lake: 'Lakes',
                river_access: 'Rivers',
                public_water: 'Public Waters',
                state_park: 'State Parks',
                fishing_pier: 'Piers',
              };
              return (
                <button
                  key={type}
                  class={`filter-chip ${isActive ? 'filter-chip-active' : 'filter-chip-inactive'} filter-chip-${type}`}
                  onClick={() => handleTypeFilterToggle(type)}
                  aria-pressed={isActive}
                >
                  <span class="filter-chip-label">{labels[type]}</span>
                  {type === 'state_park' && <span class="no-license-sup" title="No License Required">No License</span>}
                </button>
              );
            })}
            {typeFilters.size < chipTypes.length && (
              <button
                class="filter-chip filter-chip-clear"
                onClick={handleClearTypeFilters}
                aria-label="Clear all filters"
              >
                <span class="filter-chip-label">Clear</span>
              </button>
            )}
          </div>}

          {/* Results: List View or Map View */}
          {viewMode === 'map' && mapboxToken ? (
            <MapView
              spots={filteredSpots}
              userLocation={userLocation}
              isDarkMode={isDarkMode}
              mapboxToken={mapboxToken}
              defaultCenter={defaultCenter}
              defaultZoom={defaultZoom}
              itemMode={itemMode}
            />
          ) : (
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
                  <p>{isPreloadedMode ? 'No fishing spots found.' : 'No fishing spots found in your area yet.'}</p>
                  {!isPreloadedMode && <button onClick={handleNewSearch}>Try a different search</button>}
                  {isPreloadedMode && backButtonUrl && <a href={backButtonUrl} class="btn-new-search">← {backButtonText}</a>}
                </div>
              ) : (
                <div class="results-grid">
                  {displayedSpots.map((spot, index) => {
                    const showAd = ADS_ENABLED && index > 0 && index % AD_FREQUENCY === 0;

                    if (itemMode === 'county') {
                      // County card rendering
                      return (
                        <>
                          {showAd && (
                            <InFeedAd
                              publisherId={PUBLISHER_ID}
                              slotId={AD_SLOTS.inFeed}
                              index={index}
                            />
                          )}
                          <a
                            key={spot.id}
                            href={`/${stateSlugLookup[spot.state] || 'texas'}/${spot.slug}`}
                            class="spot-card county-card"
                            style={`animation-delay: ${Math.min(index * 0.05, 0.5)}s`}
                          >
                            <div class="card-header">
                              <h3>{spot.name} County</h3>
                              {spot.distance && (
                                <div class="distance-indicator">{formatDistance(spot.distance)}</div>
                              )}
                            </div>
                            <div class="card-body">
                              <span class="card-meta-item">{spot.count} {spot.count === 1 ? 'spot' : 'spots'}</span>
                            </div>
                          </a>
                        </>
                      );
                    }

                    // Spot card rendering
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
                      <>
                        {showAd && (
                          <InFeedAd
                            publisherId={PUBLISHER_ID}
                            slotId={AD_SLOTS.inFeed}
                            index={index}
                          />
                        )}
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
                      </>
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
          )}
        </div>
      )}
    </div>
  );
}
