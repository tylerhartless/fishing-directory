import { useEffect, useRef, useState } from 'preact/hooks';
import { getIpGeolocationData } from '../lib/ipGeolocation';

interface Spot {
  canonical_id: string;
  name: string;
  state: string;
  state_route: string;
  county: string;
  county_slug: string;
  latitude: number;
  longitude: number;
  spot_type: string;
  water_body_names?: string[];
  amenities?: Record<string, boolean>;
  distance?: number;
  count?: number;
}

interface MapViewProps {
  spots: Spot[];
  userLocation: { lat: number; lon: number } | null;
  isDarkMode: boolean;
  mapboxToken: string;
  defaultCenter?: [number, number];  // [lat, lon] for pre-loaded mode
  defaultZoom?: number;
  itemMode?: 'spot' | 'county';
}

// Color mapping for spot types — matches badge colors from retro-colors.css
// Light mode now uses the same vibrant colors as the filter chip borders for consistency
const SPOT_TYPE_COLORS: Record<string, { dark: string; light: string }> = {
  lake:            { dark: '#5c9dff', light: '#5c9dff' },
  river_access:    { dark: '#b88dff', light: '#b88dff' },
  public_water:    { dark: '#4fb8c2', light: '#4fb8c2' },
  state_park:      { dark: '#a8d96e', light: '#a8d96e' },
  community_park:  { dark: '#f08c6e', light: '#f08c6e' },
  pier:            { dark: '#ffb84d', light: '#ffb84d' },
  boat_ramp:       { dark: '#c87854', light: '#c87854' },
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
    community_park: 'Community Park',
    pier: 'Pier',
    boat_ramp: 'Boat Ramp',
  };
  return labels[spotType] || spotType.replace(/_/g, ' ');
}

export default function MapView({ spots, userLocation, isDarkMode, mapboxToken, defaultCenter, defaultZoom, itemMode = 'spot' }: MapViewProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const tileLayerRef = useRef<any>(null);
  const clusterGroupRef = useRef<any>(null);
  const leafletRef = useRef<any>(null);
  const autoZoomedForLocationRef = useRef<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [mapReady, setMapReady] = useState(false);
  const [ipLocation, setIpLocation] = useState<{ lat: number; lon: number } | null>(null);

  // Fetch IP geolocation for initial map center (skip if defaultCenter provided)
  useEffect(() => {
    if (!userLocation && !defaultCenter) {
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
        } else if (defaultCenter && defaultZoom) {
          center = defaultCenter;
          zoom = defaultZoom;
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

        // Add tile layer — Mapbox raster tiles (512px for retina sharpness)
        const tiles = L.tileLayer(
          isDarkMode
            ? `https://api.mapbox.com/styles/v1/netlace/cmo22y7nx002c01qfha7d96ct/tiles/512/{z}/{x}/{y}@2x?access_token=${mapboxToken}`
            : `https://api.mapbox.com/styles/v1/netlace/cmo22v29h00gn01s49nnh6e5x/tiles/512/{z}/{x}/{y}@2x?access_token=${mapboxToken}`,
          {
            attribution: '&copy; <a href="https://www.mapbox.com/about/maps/">Mapbox</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
            tileSize: 512,
            zoomOffset: -1,
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

    // Add new tile layer with correct theme — Mapbox raster tiles
    const tiles = L.tileLayer(
      isDarkMode
        ? `https://api.mapbox.com/styles/v1/netlace/cmo22y7nx002c01qfha7d96ct/tiles/512/{z}/{x}/{y}@2x?access_token=${mapboxToken}`
        : `https://api.mapbox.com/styles/v1/netlace/cmo22v29h00gn01s49nnh6e5x/tiles/512/{z}/{x}/{y}@2x?access_token=${mapboxToken}`,
      {
        attribution: '&copy; <a href="https://www.mapbox.com/about/maps/">Mapbox</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        tileSize: 512,
        zoomOffset: -1,
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

  // Re-center map when userLocation changes, zooming to frame the nearest spots
  useEffect(() => {
    if (!mapInstanceRef.current || !userLocation || !leafletRef.current) return;
    if (spots.length === 0) return; // wait for spots to load before calculating bounds

    // Only auto-zoom once per unique user location — don't re-zoom on filter changes
    const locationKey = `${userLocation.lat},${userLocation.lon}`;
    if (autoZoomedForLocationRef.current === locationKey) return;
    autoZoomedForLocationRef.current = locationKey;

    const L = leafletRef.current;
    const map = mapInstanceRef.current;

    // Get the 3 nearest spots (spots are pre-sorted by distance from SearchWidget)
    const nearestSpots = spots
      .filter(s => !isNaN(parseFloat(String(s.latitude))) && !isNaN(parseFloat(String(s.longitude))))
      .slice(0, 3);

    if (nearestSpots.length > 0) {
      const latlngs: [number, number][] = [
        [userLocation.lat, userLocation.lon],
        ...nearestSpots.map(s => [parseFloat(String(s.latitude)), parseFloat(String(s.longitude))] as [number, number])
      ];
      const bounds = L.latLngBounds(latlngs);
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 14, animate: true });
    } else {
      // Fallback: no spots nearby, just center on user
      map.setView([userLocation.lat, userLocation.lon], 10, { animate: true });
    }
  }, [userLocation, spots]);

  // Fit bounds to all pre-loaded spots when no user location (directory pages)
  useEffect(() => {
    if (!mapInstanceRef.current || !leafletRef.current || !mapReady) return;
    if (userLocation) return; // User location takes priority (handled by above effect)
    if (!defaultCenter) return; // Not in pre-loaded mode
    if (spots.length === 0) return;

    const L = leafletRef.current;
    const map = mapInstanceRef.current;

    const validSpots = spots.filter(s => !isNaN(parseFloat(String(s.latitude))) && !isNaN(parseFloat(String(s.longitude))));
    if (validSpots.length > 0) {
      const latlngs = validSpots.map(s => [parseFloat(String(s.latitude)), parseFloat(String(s.longitude))] as [number, number]);
      const bounds = L.latLngBounds(latlngs);
      map.fitBounds(bounds, { padding: [30, 30], maxZoom: defaultZoom || 10, animate: false });
    }
  }, [spots, mapReady, defaultCenter]);

  function addMarkers(L: any, clusterGroup: any, spotsToAdd: Spot[]) {
    const markers: any[] = [];

    for (const spot of spotsToAdd) {
      const lat = Number(spot.latitude);
      const lng = Number(spot.longitude);

      if (isNaN(lat) || isNaN(lng)) continue;

      if (itemMode === 'county') {
        // County marker — neutral sage green color
        const color = isDarkMode ? '#7ec97e' : '#5a9a5a';

        const marker = L.circleMarker([lat, lng], {
          radius: 10,
          fillColor: color,
          color: isDarkMode ? 'rgba(255,255,255,0.9)' : 'rgba(0,0,0,0.7)',
          weight: 2,
          fillOpacity: 1.0,
        });

        const countyUrl = `/${spot.state_route}/${spot.county_slug}`;
        const distanceHtml = spot.distance
          ? `<div class="map-popup-distance">${formatDistance(spot.distance)} away</div>`
          : '';

        const popupHtml = `
          <div class="map-popup">
            <a href="${countyUrl}" class="map-popup-name">${spot.name} County</a>
            <span class="map-popup-type" style="background:${color}">${spot.count} ${spot.count === 1 ? 'spot' : 'spots'}</span>
            ${distanceHtml}
          </div>
        `;

        marker.bindPopup(popupHtml, {
          maxWidth: 250,
          minWidth: 150,
          className: 'spot-map-popup',
        });

        markers.push(marker);
      } else {
        // Spot marker — color-coded by type
        const colors = SPOT_TYPE_COLORS[spot.spot_type] || DEFAULT_COLOR;
        const color = isDarkMode ? colors.dark : colors.light;

        const marker = L.circleMarker([lat, lng], {
          radius: 9,
          fillColor: color,
          color: isDarkMode ? 'rgba(255,255,255,0.9)' : 'rgba(0,0,0,0.7)',
          weight: 2,
          fillOpacity: 1.0,
        });

        // Build popup content
        const displayName = spot.name;
        const spotUrl = `/${spot.state_route}/${spot.county_slug}/${spot.canonical_id}`;

        const amenities = spot.amenities ?? {};
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
    </div>
  );
}
