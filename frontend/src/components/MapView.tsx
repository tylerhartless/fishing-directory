import { useEffect, useRef, useState } from 'preact/hooks';
import { getIpGeolocationData } from '../lib/ipGeolocation';

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

interface MapViewProps {
  spots: Spot[];
  userLocation: { lat: number; lon: number } | null;
  isDarkMode: boolean;
  mapboxToken: string;
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

// Color mapping for spot types — matches badge colors from retro-colors.css
const SPOT_TYPE_COLORS: Record<string, { dark: string; light: string }> = {
  lake:          { dark: '#5c9dff', light: '#5a6b73' },
  river_access:  { dark: '#b88dff', light: '#6b4a9e' },
  public_water:  { dark: '#7ec97e', light: '#4a6741' },
  state_park:    { dark: '#a8d96e', light: '#7a8450' },
  fishing_pier:  { dark: '#ffb84d', light: '#d4a574' },
  boat_ramp:     { dark: '#c87854', light: '#b85c3a' },
  bank_fishing:  { dark: '#7ec97e', light: '#4a6741' },
  pier:          { dark: '#ffb84d', light: '#d4a574' },
  wade_fishing:  { dark: '#5c9dff', light: '#5a6b73' },
  kayak_launch:  { dark: '#b88dff', light: '#6b4a9e' },
};

const DEFAULT_COLOR = { dark: '#9ab087', light: '#6b6b6b' };

// Amenity display helpers
const amenityLabels: Record<string, string> = {
  'boat_ramp': 'Boat Ramp',
  'fishing_pier': 'Pier',
  'fish_cleaning': 'Cleaning',
  'restrooms': 'Restrooms',
  'parking': 'Parking',
};

function getCountySlug(countyName: string): string {
  if (!countyName) return '';
  if (countyName.includes(',')) {
    countyName = countyName.split(',')[0].trim();
  }
  countyName = countyName.replace(/\s+County$/i, '').trim();
  return countyName.toLowerCase().replace(/\s+/g, '-');
}

function formatDistance(distance?: number): string {
  if (!distance) return '';
  if (distance < 0.1) {
    return `${(distance * 5280).toFixed(0)} ft`;
  }
  return `${distance.toFixed(1)} mi`;
}

function getSpotTypeLabel(spotType: string): string {
  const labels: Record<string, string> = {
    lake: 'Lake',
    river_access: 'River Access',
    public_water: 'Public Water',
    state_park: 'State Park',
    fishing_pier: 'Fishing Pier',
    boat_ramp: 'Boat Ramp',
    bank_fishing: 'Bank Fishing',
    pier: 'Pier',
    wade_fishing: 'Wade Fishing',
    kayak_launch: 'Kayak Launch',
  };
  return labels[spotType] || spotType.replace(/_/g, ' ');
}

export default function MapView({ spots, userLocation, isDarkMode, mapboxToken }: MapViewProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const tileLayerRef = useRef<any>(null);
  const clusterGroupRef = useRef<any>(null);
  const leafletRef = useRef<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [mapReady, setMapReady] = useState(false);
  const [ipLocation, setIpLocation] = useState<{ lat: number; lon: number } | null>(null);

  // Fetch IP geolocation for initial map center
  useEffect(() => {
    if (!userLocation) {
      getIpGeolocationData().then((data) => {
        if (data && data.latitude && data.longitude) {
          setIpLocation({ lat: data.latitude, lon: data.longitude });
        }
      });
    }
  }, []);

  // Initialize the map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    let cancelled = false;

    async function initMap() {
      try {
        // Dynamic imports to avoid SSR issues — Leaflet needs window/document
        const L = (await import('leaflet')).default;

        // Import CSS - Vite/Astro will bundle these
        await import('leaflet/dist/leaflet.css');

        // Import markercluster - CJS module, Vite handles conversion
        await import('leaflet.markercluster');
        await import('leaflet.markercluster/dist/MarkerCluster.css');
        await import('leaflet.markercluster/dist/MarkerCluster.Default.css');

        if (cancelled || !mapContainerRef.current) return;

        leafletRef.current = L;

        // Determine initial center & zoom
        let center: [number, number] = [39.8, -98.5]; // Continental US fallback
        let zoom = 4;

        if (userLocation) {
          center = [userLocation.lat, userLocation.lon];
          zoom = 10;
        } else if (ipLocation) {
          center = [ipLocation.lat, ipLocation.lon];
          zoom = 7;
        }

        // Create map
        const map = L.map(mapContainerRef.current, {
          center,
          zoom,
          scrollWheelZoom: false, // Prevent mobile scroll hijacking
          zoomControl: true,
        });

        // Enable scroll zoom on focus (click/tap on the map)
        map.once('focus', () => {
          map.scrollWheelZoom.enable();
        });

        // Also enable on click for desktop
        map.once('click', () => {
          map.scrollWheelZoom.enable();
        });

        mapInstanceRef.current = map;

        // Add tile layer — CARTO free tiles (no token needed)
        const tiles = L.tileLayer(
          isDarkMode
            ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
            : 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
          {
            attribution: '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>',
            maxZoom: 19,
          }
        ).addTo(map);

        tileLayerRef.current = tiles;

        // Create cluster group
        const clusterGroup = (L as any).markerClusterGroup({
          maxClusterRadius: 50,
          spiderfyOnMaxZoom: true,
          showCoverageOnHover: false,
          zoomToBoundsOnClick: true,
          iconCreateFunction: (cluster: any) => {
            const count = cluster.getChildCount();
            let size = 'small';
            let dimension = 36;
            if (count >= 100) {
              size = 'large';
              dimension = 48;
            } else if (count >= 10) {
              size = 'medium';
              dimension = 42;
            }
            return L.divIcon({
              html: `<div class="spot-cluster spot-cluster-${size}"><span>${count}</span></div>`,
              className: 'spot-cluster-icon',
              iconSize: L.point(dimension, dimension),
            });
          },
        });

        clusterGroupRef.current = clusterGroup;
        map.addLayer(clusterGroup);

        // Don't add markers here — let the marker effect handle it
        // (spots may have updated while the async init was running)
        setMapReady(true);
        setIsLoading(false);

        // Invalidate size after render to handle container sizing
        setTimeout(() => {
          map.invalidateSize();
        }, 100);
      } catch (error) {
        console.error('Failed to initialize map:', error);
        setIsLoading(false);
      }
    }

    initMap();

    return () => {
      cancelled = true;
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [ipLocation]); // Re-init when IP location arrives (only runs once since ipLocation starts null)

  // Update tile layer when theme changes
  useEffect(() => {
    if (!mapInstanceRef.current || !tileLayerRef.current || !leafletRef.current) return;

    const L = leafletRef.current;
    const map = mapInstanceRef.current;

    // Remove old tile layer
    map.removeLayer(tileLayerRef.current);

    // Add new tile layer with correct theme — CARTO
    const tiles = L.tileLayer(
      isDarkMode
        ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
        : 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
      {
        attribution: '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>',
        maxZoom: 19,
      }
    ).addTo(map);

    tileLayerRef.current = tiles;
  }, [isDarkMode]);

  // Update markers when spots change, theme changes, or map finishes initializing
  useEffect(() => {
    if (!mapReady || !clusterGroupRef.current || !leafletRef.current) return;

    const L = leafletRef.current;
    const clusterGroup = clusterGroupRef.current;

    clusterGroup.clearLayers();
    addMarkers(L, clusterGroup, spots);
  }, [spots, isDarkMode, mapReady]);

  // Re-center map when userLocation changes
  useEffect(() => {
    if (!mapInstanceRef.current || !userLocation) return;
    mapInstanceRef.current.setView([userLocation.lat, userLocation.lon], 10, { animate: true });
  }, [userLocation]);

  function addMarkers(L: any, clusterGroup: any, spotsToAdd: Spot[]) {
    const markers: any[] = [];

    for (const spot of spotsToAdd) {
      const lat = parseFloat(spot.latitude);
      const lng = parseFloat(spot.longitude);

      if (isNaN(lat) || isNaN(lng)) continue;

      const colors = SPOT_TYPE_COLORS[spot.spot_type] || DEFAULT_COLOR;
      const color = isDarkMode ? colors.dark : colors.light;

      const marker = L.circleMarker([lat, lng], {
        radius: 7,
        fillColor: color,
        color: isDarkMode ? 'rgba(255,255,255,0.6)' : 'rgba(0,0,0,0.5)',
        weight: 1.5,
        fillOpacity: 0.85,
      });

      // Build popup content
      const displayName = spot.name.replace(/\s*\([a-z]+\d+\)\s*$/i, '');
      const countySlug = getCountySlug(spot.county);
      const stateSlug = stateSlugLookup[spot.state] || 'texas';
      const spotUrl = `/${stateSlug}/${countySlug}/${spot.slug}`;

      const amenities = spot.amenities
        ? (typeof spot.amenities === 'string' ? JSON.parse(spot.amenities) : spot.amenities)
        : {};
      const prominentAmenities = Object.entries(amenityLabels)
        .filter(([key]) => amenities[key] === true)
        .map(([_, label]) => label)
        .slice(0, 3);

      const distanceHtml = spot.distance
        ? `<div class="map-popup-distance">${formatDistance(spot.distance)} away</div>`
        : '';

      const amenitiesHtml = prominentAmenities.length > 0
        ? `<div class="map-popup-amenities">${prominentAmenities.join(' &middot; ')}</div>`
        : '';

      const typeLabel = getSpotTypeLabel(spot.spot_type);
      const typeBadgeHtml = `<span class="map-popup-type" style="background:${color}">${typeLabel}</span>`;

      const popupHtml = `
        <div class="map-popup">
          <a href="${spotUrl}" class="map-popup-name">${displayName}</a>
          ${typeBadgeHtml}
          ${distanceHtml}
          ${amenitiesHtml}
        </div>
      `;

      marker.bindPopup(popupHtml, {
        maxWidth: 250,
        minWidth: 150,
        className: 'spot-map-popup',
      });

      markers.push(marker);
    }

    clusterGroup.addLayers(markers);
  }

  return (
    <div class="map-view-container">
      {isLoading && (
        <div class="map-loading-overlay">
          <svg class="spinner" width="40" height="40" viewBox="0 0 50 50">
            <circle cx="25" cy="25" r="20" fill="none" stroke="currentColor" stroke-width="4" stroke-dasharray="80" stroke-dashoffset="60" />
          </svg>
          <p>Loading map...</p>
        </div>
      )}
      <div ref={mapContainerRef} class="map-leaflet-container" />
      {!isLoading && (
        <div class="map-scroll-hint">Click or tap the map to enable zoom</div>
      )}
    </div>
  );
}
